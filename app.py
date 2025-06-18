from flask import Flask, render_template, session, request, redirect, url_for, send_from_directory, abort, flash
from flaskext.mysql import MySQL
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import functools
import uuid
import re
import os

mysql = MySQL()

app = Flask(__name__, template_folder='templates')
app.secret_key = 'strongkey' # **IMPORTANT: Change this to a strong, unique secret key!**
mysql.init_app(app)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'attempt1' # Ensure this is your actual database name
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_HOST'] = 'localhost'


# --- File Upload Configuration ---
UPLOAD_ROOT_FOLDER = 'uploads' # Path relative to your app.py
UPLOAD_FOLDER_CLAIMS = os.path.join(UPLOAD_ROOT_FOLDER, 'claims')
UPLOAD_FOLDER_POLICY_DOCS = os.path.join(UPLOAD_ROOT_FOLDER, 'policy_docs')

os.makedirs(UPLOAD_FOLDER_CLAIMS, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_POLICY_DOCS, exist_ok=True)

app.config['UPLOAD_FOLDER_CLAIMS'] = UPLOAD_FOLDER_CLAIMS
app.config['UPLOAD_FOLDER_POLICY_DOCS'] = UPLOAD_FOLDER_POLICY_DOCS

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'} # Typically these for documents. Removed doc/docx for sensitive docs
MAX_FILE_SIZE_MB = 5 # Example: Max 5MB per file for individual files
app.config['MAX_CONTENT_LENGTH'] = 3 * MAX_FILE_SIZE_MB * 1024 * 1024 # Max total request body size for 3 files


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_dir):
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename):
        # flash(f"Invalid file type for {file.filename}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}", 'danger') # Removed
        return "INVALID_FILE_TYPE" 

    filename = secure_filename(file.filename)
    unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
    
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    return unique_filename

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    try:
        if not filename.startswith(('claims/', 'policy_docs/')):
            app.logger.warning(f"Attempted to access file outside allowed upload subdirectories: {filename}")
            abort(404)
            
        return send_from_directory(app.root_path + '/' + UPLOAD_ROOT_FOLDER, filename)
    except Exception as e:
        app.logger.error(f"Error serving uploaded file {filename}: {e}")
        abort(404)

# --- Decorators for Authentication ---

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or session.get('role') != 'admin':
            # flash('Please log in as an administrator to access this page.', 'danger') # Removed
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or session.get('role') != 'user':
            # flash('Please log in as a user to access this page.', 'danger') # Removed
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Public Landing Page ---
@app.route('/')
def index():
    return render_template('user_login.html')

# --- Admin Authentication (Separate from User Authentication) ---

@app.route('/setup-admin', methods=['GET', 'POST'])
def setup_admin():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT COUNT(*) AS count FROM admin_users")
    admin_count = cur.fetchone()['count']

    if admin_count > 0:
        # flash('Admin user already exists. Please log in.', 'info') # Removed
        cur.close()
        conn.close()
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')

        if not username or not password:
            # flash('Username and Password are required!', 'danger') # Removed
            cur.close()
            conn.close()
            return render_template('setup_admin.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters long!', 'danger') # Removed
            cur.close()
            conn.close()
            return render_template('setup_admin.html')

        hashed_password = generate_password_hash(password)

        try:
            cur.execute("INSERT INTO admin_users (username, password, email) VALUES (%s, %s, %s)",
                        (username, hashed_password, email))
            conn.commit()
            # flash('Initial admin user created successfully! Please log in.', 'success') # Removed
            return redirect(url_for('admin_login'))
        except pymysql.Error as e:
            # flash(f'Error creating admin user: {e}', 'danger') # Removed
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    return render_template('setup_admin.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'loggedin' in session and session.get('role') == 'admin':
        return redirect(url_for('dashboard'))

    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT COUNT(*) AS count FROM admin_users")
    admin_count = cur.fetchone()['count']
    if admin_count == 0:
        cur.close()
        conn.close()
        return redirect(url_for('setup_admin'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and Password are required!', 'danger') # Removed
            cur.close()
            conn.close()
            return render_template('admin_login.html')


        cur.execute("SELECT * FROM admin_users WHERE username = %s OR email = %s", (username, username))
        admin_user = cur.fetchone()

        if admin_user and check_password_hash(admin_user['password'], password):
            session['loggedin'] = True
            session['id'] = admin_user['id']
            session['username'] = admin_user['username']
            session['role'] = 'admin'
            # flash('Logged in as Admin successfully!', 'success') # Removed
            cur.close()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            # flash('Incorrect username/email or password for admin.', 'danger') # Removed
            cur.close()
            conn.close()
    
    cur.close()
    conn.close()
    return render_template('admin_login.html')

# --- User Authentication (Separate from Admin Authentication) ---

@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    conn = None
    cur = None
    form_data = {} 
    
    try:
        # Establish connection and cursor ONLY if it's a POST request (data submission)
        # or if you need to fetch data for GET request (e.g. dropdowns in register form)
        # For a simple registration form, it's usually only needed on POST.
        # However, to avoid 'conn' being None if an error occurs *before* conn = mysql.connect(),
        # it's safer to have it here if any DB operations are inside the try.
        
        # If there are no DB operations for GET (which is typical for a register form),
        # you can move conn = mysql.connect() and cur = conn.cursor()
        # inside the `if request.method == 'POST':` block.
        # But keeping it here handles cases where `existing_user` check needs it.
        conn = mysql.connect() # Establish connection here
        cur = conn.cursor(pymysql.cursors.DictCursor) # Get cursor here

        if request.method == 'POST':
            nama_nasabah = request.form['nama_nasabah']
            email_nasabah = request.form['email_nasabah']
            password = request.form['password']

            form_data = request.form.to_dict()

            if not nama_nasabah or not email_nasabah or not password:
                return render_template('user_register.html', form_data=form_data)
            if len(password) < 8:
                return render_template('user_register.html', form_data=form_data)
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email_nasabah):
                return render_template('user_register.html', form_data=form_data)

            hashed_password = generate_password_hash(password)

            cur.execute("SELECT * FROM nasabah WHERE Email_Nasabah = %s", (email_nasabah,))
            existing_user = cur.fetchone()
            if existing_user:
                return render_template('user_register.html', form_data=form_data)

            new_nasabah_id = 'N' + str(uuid.uuid4().int)[:8]

            insert_query = """
                INSERT INTO nasabah (ID_Nasabah, Nama_Nasabah, Email_Nasabah, password_hash)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(insert_query, (new_nasabah_id, nama_nasabah, email_nasabah, hashed_password))
            conn.commit()

            session['loggedin'] = True
            session['id'] = new_nasabah_id
            session['username'] = nama_nasabah
            session['role'] = 'user'
            
            # --- FIX: Changed redirect target from user_profile_setup to user_dashboard ---
            return redirect(url_for('user_login')) 

        # If GET request, render with empty form_data
        # Note: conn and cur are already initialized above for the try block.
        return render_template('user_register.html', form_data=form_data) 
    except pymysql.Error as e:
        if conn: conn.rollback()
        # If an error happens, re-render the form with existing data and an indication of error
        return render_template('user_register.html', form_data=form_data) 
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if 'loggedin' in session and session.get('role') == 'user':
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        email_or_name = request.form['email_or_name']
        password = request.form['password']

        if not email_or_name or not password:
            # flash('Email/Username and Password are required!', 'danger') # Removed
            return render_template('user_login.html')

        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute("SELECT ID_Nasabah, Nama_Nasabah, password_hash FROM nasabah WHERE Email_Nasabah = %s OR Nama_Nasabah = %s", (email_or_name, email_or_name))
        nasabah_user = cur.fetchone()

        if nasabah_user and check_password_hash(nasabah_user['password_hash'], password):
            session['loggedin'] = True
            session['id'] = nasabah_user['ID_Nasabah']
            session['username'] = nasabah_user['Nama_Nasabah']
            session['role'] = 'user'
            # flash('Logged in as User successfully!', 'success') # Removed
            cur.close()
            conn.close()
            return redirect(url_for('user_dashboard'))
        else:
            # flash('Incorrect email/name or password for user.', 'danger') # Removed
            cur.close()
            conn.close()
    
    return render_template('user_login.html')

# --- Universal Logout Route ---
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    # flash('You have been logged out.', 'info') # Removed
    return redirect(url_for('index'))


# ====================================================================================================================
# ADMIN ROUTES
# ====================================================================================================================

@app.route('/adminHome')
@admin_required
def dashboard():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT COUNT(*) AS total FROM nasabah")
    total_users = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM produk_asuransi")
    total_products = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM agen")
    total_agents = cur.fetchone()['total'] # This will be removed in a later update

    cur.execute("SELECT COUNT(*) AS total FROM data_polis")
    total_policies = cur.fetchone()['total']

    cur.close()
    conn.close()

    return render_template(
        'adminHome.html',
        total_users=total_users,
        total_products=total_products,
        total_agents=total_agents,
        total_policies=total_policies,
    )

@app.route('/adminUserManagement/',methods=['GET'])
@admin_required
def User():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM nasabah")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('adminUserManagement.html', nasabah = data)

@app.route('/adminUserManagement/add',methods=['GET','POST'])
@admin_required
def addUser():
    conn = None
    cur = None
    form_data = {} # Initialize for GET and POST errors
    try:
        conn = mysql.connect() # Establish connection here
        cur = conn.cursor(pymysql.cursors.DictCursor) # Get cursor here

        if request.method == 'POST':
            # --- Automated ID Generation Logic for ID_Nasabah ---
            new_nasabah_id = ""
            cur.execute("SELECT MAX(ID_Nasabah) AS max_id FROM nasabah")
            result = cur.fetchone()
            max_id = result['max_id']

            if max_id:
                # Assuming IDs are like N001, N002, ..., N999
                # Extract numeric part, convert to int, increment
                numeric_part = int(max_id[1:]) # Get '005' from 'N005', convert to 5
                next_number = numeric_part + 1
                # Format back to N00X, N0XX, or NXXX (assuming 3 digits after N, adjust if different)
                new_nasabah_id = 'N' + str(next_number).zfill(len(max_id) - 1) # zfill pads with leading zeros
            else:
                # If no users exist yet, start with N001
                new_nasabah_id = 'N001'
            # --- End Automated ID Generation Logic ---

            # Get data from the form, including new password
            Nama_Nasabah = request.form['Nama_Nasabah']
            Email_Nasabah = request.form['Email_Nasabah']
            password = request.form['password'] # NEW: Password input

            form_data = request.form.to_dict() # Capture for re-population

            # Validation: Check for empty fields and password length
            if not all([Nama_Nasabah, Email_Nasabah, password]): # Password is now required
                return render_template('AddUserForm.html', form_data=form_data)
            if len(password) < 8:
                # flash('Password must be at least 8 characters long!', 'danger') # Removed
                return render_template('AddUserForm.html', form_data=form_data)
            if not re.match(r'[^@]+@[^@]+\.[^@]+', Email_Nasabah):
                return render_template('AddUserForm.html', form_data=form_data)

            # Check if email already exists
            cur.execute("SELECT ID_Nasabah FROM nasabah WHERE Email_Nasabah = %s", (Email_Nasabah,))
            if cur.fetchone():
                # flash('An account with this email already exists!', 'danger') # Removed
                return render_template('AddUserForm.html', form_data=form_data)

            hashed_password = generate_password_hash(password)

            # MODIFIED INSERT QUERY: Add password_hash
            insert_query = """
                INSERT INTO nasabah (ID_Nasabah, Nama_Nasabah, Email_Nasabah, password_hash)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(insert_query, (new_nasabah_id, Nama_Nasabah, Email_Nasabah, hashed_password))
            conn.commit()
            # flash('User added successfully!', 'success') # Removed
            return redirect (url_for('User')) # Redirect to User list on success
        
        # For GET request, simply render the form
        return render_template('AddUserForm.html', form_data=form_data)
    except pymysql.Error as e:
        if conn: conn.rollback()
        # flash(f'Error adding user: {e}', 'danger') # Removed
        return render_template('AddUserForm.html', form_data=form_data) # Re-render on database error
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()

# ... (rest of your app.py imports and configurations) ...

# Locate the updateUser route:
@app.route('/adminUserManagement/update/<string:id>',methods=['GET','POST'])
@admin_required
def updateUser(id):
    conn = None
    cur = None
    try:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # MODIFIED SELECT: Only fetch required columns from nasabah table (ID, Name, Email, Password Hash)
        # Assuming you want to display current Name and Email in the form
        cur.execute("SELECT ID_Nasabah, Nama_Nasabah, Email_Nasabah FROM nasabah WHERE ID_Nasabah = %s", id)
        data = cur.fetchone() # This is the existing user data

        if not data: # User not found on GET request
            return redirect(url_for('User'))

        # Prepare form_data for rendering. For GET, it's the fetched data. For POST, it's request.form
        form_data = data 

        if request.method == 'POST':
            Nama_Nasabah = request.form['Nama_Nasabah']
            Email_Nasabah = request.form['Email_Nasabah']
            new_password = request.form.get('new_password') # Optional password field

            # Capture submitted form data into form_data for re-population if validation fails
            form_data = request.form.to_dict() 
            form_data['ID_Nasabah'] = id # Ensure ID is preserved for template if re-rendering

            # Validation: Only Name, Email are required. Password is optional.
            if not all([Nama_Nasabah, Email_Nasabah]):
                return render_template('UpdateUserForm.html', nasabah=form_data)
            
            if not re.match(r'[^@]+@[^@]+\.[^@]+', Email_Nasabah): # Basic email format validation
                return render_template('UpdateUserForm.html', nasabah=form_data)

            # Password validation (if provided)
            if new_password:
                if len(new_password) < 8:
                    return render_template('UpdateUserForm.html', nasabah=form_data)
                hashed_password = generate_password_hash(new_password)
            else:
                hashed_password = None # No password update

            # Check if email already exists for *another* user (important for uniqueness)
            cur.execute("SELECT ID_Nasabah FROM nasabah WHERE Email_Nasabah = %s AND ID_Nasabah != %s", (Email_Nasabah, id))
            if cur.fetchone():
                # flash('Email already registered by another user!', 'danger') # If flash enabled
                return render_template('UpdateUserForm.html', nasabah=form_data)


            try:
                # Build the update query dynamically based on whether password is provided
                if hashed_password:
                    update_query = """
                        UPDATE nasabah SET 
                        Nama_Nasabah = %s, Email_Nasabah = %s, password_hash = %s 
                        WHERE ID_Nasabah = %s
                    """
                    cur.execute(update_query, (Nama_Nasabah, Email_Nasabah, hashed_password, id))
                else:
                    update_query = """
                        UPDATE nasabah SET 
                        Nama_Nasabah = %s, Email_Nasabah = %s 
                        WHERE ID_Nasabah = %s
                    """
                    cur.execute(update_query, (Nama_Nasabah, Email_Nasabah, id))

                conn.commit()
                # flash('User updated successfully!', 'success') # If flash enabled
                return redirect (url_for('User')) # Redirect to User list on success
            except pymysql.Error as e:
                conn.rollback()
                # flash(f'Error updating user: {e}', 'danger') # If flash enabled
                return render_template('UpdateUserForm.html', nasabah=form_data) # Re-render on DB error
        
        # If GET request, render the form with initial fetched user data
        return render_template('UpdateUserForm.html',nasabah = form_data)
    except pymysql.Error as e:
        # Catch errors from initial DB connection or SELECT query for GET request
        # flash(f'Database error: {e}', 'danger') # If flash enabled
        if conn: conn.rollback() # Rollback if connection was active
        return redirect(url_for('User')) # Redirect to user list on severe error (e.g., user ID not found on GET)
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()

@app.route('/adminUserManagement/delete/<string:id>',methods=['GET'])
@admin_required
def deleteUser(id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute("DELETE FROM nasabah WHERE ID_Nasabah = %s", id)
        conn.commit()
        # flash('User deleted successfully!', 'success') # Removed
    except pymysql.Error as e:
        # flash(f'Error deleting user: {e}', 'danger') # Removed
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('User'))

@app.route('/adminUserManagement/policies/<string:nasabah_id>', methods=['GET'])
@admin_required
def adminUserPolicies(nasabah_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT Nama_Nasabah FROM nasabah WHERE ID_Nasabah = %s", (nasabah_id,))
    nasabah_name_data = cur.fetchone()
    if not nasabah_name_data:
        # flash('User not found!', 'danger') # Removed
        cur.close()
        conn.close()
        return redirect(url_for('User'))

    nasabah_name = nasabah_name_data['Nama_Nasabah']

    cur.execute("""
        SELECT
            dp.ID_Data_Polis,
            dp.ID_Polis,
            pa.Nama_Produk,
            dp.Nama_Data_Polis,
            dp.Hubungan_Data_Polis,
            dp.Alamat_Data_Polis,
            dp.Nomor_Telepon_Polis,
            dp.Tanggal_Polis_Dibuat,
            dp.KTP_File,
            dp.NPWP_File,
            dp.KK_File
        FROM
            data_polis dp
        JOIN
            produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
        WHERE
            dp.ID_Nasabah = %s
        ORDER BY
            dp.Tanggal_Polis_Dibuat DESC
    """, (nasabah_id,))
    user_policies = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('adminUserPolicies.html',
                           nasabah_name=nasabah_name,
                           user_policies=user_policies,
                           nasabah_id=nasabah_id)


#==================================================================================================================================
#Product Management (Admin side)
@app.route('/adminProductManagement/',methods=['GET'])
@admin_required
def Product():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM produk_asuransi")
    data2 = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('adminProductManagement.html', product_asuransi = data2)

@app.route('/adminProductManagement/add',methods=['GET','POST'])
@admin_required
def addProduct():
    conn = None
    cur = None
    form_data = {} # Initialize for GET and POST errors
    try:
        conn = mysql.connect() # Establish connection here
        cur = conn.cursor(pymysql.cursors.DictCursor) # Get cursor here

        if request.method == 'POST':
            new_product_id = ""
            cur.execute("SELECT MAX(ID_Produk) AS max_id FROM produk_asuransi")
            result = cur.fetchone()
            max_id = result['max_id']

            if max_id:
                numeric_part = int(max_id[1:])
                next_number = numeric_part + 1
                new_product_id = 'P' + str(next_number).zfill(len(max_id) - 1)
            else:
                new_product_id = 'P001'

            Nama_Produk = request.form['Nama_Produk']
            Masa_Berlaku = request.form['Masa_Berlaku']
            Nama_Jenis_Asuransi = request.form['Nama_Jenis_Asuransi']
            Premi_Bulanan = request.form['Premi_Bulanan']

            form_data = request.form.to_dict()

            if not all([Nama_Produk, Masa_Berlaku, Nama_Jenis_Asuransi, Premi_Bulanan]): # Validation
                return render_template('AddProductForm.html', form_data=form_data)

            cur.execute("""
                INSERT INTO produk_asuransi (ID_Produk, Nama_Produk, Masa_Berlaku, Nama_Jenis_Asuransi, Premi_Bulanan)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_product_id, Nama_Produk, Masa_Berlaku, Nama_Jenis_Asuransi, Premi_Bulanan))
            conn.commit()
            return redirect (url_for('Product'))
        
        return render_template('AddProductForm.html', form_data=form_data)
    except pymysql.Error as e:
        if conn: conn.rollback()
        return render_template('AddProductForm.html', form_data=form_data)
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()

@app.route('/adminProductManagement/update/<string:id>',methods=['GET','POST'])
@admin_required
def updateProduct(id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM produk_asuransi WHERE ID_Produk = %s", id)
    data3 = cur.fetchone()

    if request.method == 'POST':
        Nama_Produk = request.form['Nama_Produk']
        Masa_Berlaku = request.form['Masa_Berlaku']
        Nama_Jenis_Asuransi = request.form['Nama_Jenis_Asuransi']
        Premi_Bulanan = request.form['Premi_Bulanan']

        if not all([Nama_Produk, Masa_Berlaku, Nama_Jenis_Asuransi, Premi_Bulanan]):
            # flash('All fields are required!', 'danger') # Removed
            data_to_pass = request.form.to_dict()
            data_to_pass['ID_Data_Polis'] = id
            return render_template('UpdatePolicyForm.html', polis=data_to_pass)

        try:
            update_query = "UPDATE produk_asuransi SET Nama_Produk = %s, Masa_Berlaku = %s, Nama_Jenis_Asuransi = %s, Premi_Bulanan = %s WHERE ID_Produk = %s"
            cur.execute(update_query, (Nama_Produk, Masa_Berlaku, Nama_Jenis_Asuransi, Premi_Bulanan, id))
            conn.commit()
            # flash('Product updated successfully!', 'success') # Removed
        except pymysql.Error as e:
            # flash(f'Error updating product: {e}', 'danger') # Removed
            conn.rollback()
        finally:
            cur.close()
            conn.close()
        return redirect (url_for('Product'))
    
    cur.close()
    conn.close()
    return render_template('UpdateProductForm.html',produk_asuransi = data3)


@app.route('/adminProductManagement/delete/<string:id>',methods=['GET'])
@admin_required
def deleteProduct(id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute("DELETE FROM produk_asuransi WHERE ID_Produk = %s", id)
        conn.commit()
        # flash('Product deleted successfully!', 'success') # Removed
    except pymysql.Error as e:
        # flash(f'Error deleting product: {e}', 'danger') # Removed
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('Product'))

#==================================================================================================================================
#Policy Management
# Policy Management (MODIFIED)
@app.route('/adminPolicyManagement/',methods=['GET'])
@admin_required
def Policy():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    # MODIFIED QUERY: Include dp.Status_Polis
    cur.execute("""
        SELECT
            dp.ID_Data_Polis,
            dp.ID_Polis,
            pa.Nama_Produk,
            dp.Nama_Data_Polis,
            dp.Hubungan_Data_Polis,
            dp.Alamat_Data_Polis,
            dp.Nomor_Telepon_Polis,
            dp.ID_Nasabah,
            n.Nama_Nasabah,
            dp.Tanggal_Polis_Dibuat,
            dp.KTP_File,
            dp.NPWP_File,
            dp.KK_File,
            dp.Status_Polis
        FROM
            data_polis dp
        JOIN
            nasabah n ON dp.ID_Nasabah = n.ID_Nasabah
        JOIN
            produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
        ORDER BY
            dp.Tanggal_Polis_Dibuat DESC
    """)
    data_polis = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('adminPolicyManagement.html', data_polis = data_polis)


@app.route('/adminPolicyManagement/add',methods=['GET','POST'])
@admin_required
def addPolicy():
    conn = None
    cur = None
    form_data = {}
    try:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        if request.method == 'POST':
            # --- Automated ID_Data_Polis Generation Logic (NEW) ---
            new_data_polis_id = ""
            cur.execute("SELECT MAX(ID_Data_Polis) AS max_id FROM data_polis WHERE ID_Data_Polis LIKE 'DP%'") # Look for IDs with 'DP' prefix
            result = cur.fetchone()
            max_id_dp = result['max_id'] # Renamed to avoid conflict with product max_id if debugging

            if max_id_dp:
                # Extract numeric part, convert to int, increment
                # Assumes IDs are like DP001, DP002, etc.
                numeric_part = int(max_id_dp[2:]) # Get '005' from 'DP005', convert to 5
                next_number = numeric_part + 1
                # Format back to DP00X, DP0XX, or DPXXX (assuming 3 digits after DP, adjust if different)
                new_data_polis_id = 'DP' + str(next_number).zfill(len(max_id_dp) - 2) # zfill pads with leading zeros
            else:
                # If no policies exist yet, start with DP001
                new_data_polis_id = 'DP001'
            # --- End Automated ID_Data_Polis Generation Logic ---

            # ID_Data_Polis = request.form['ID_Data_Polis'] # REMOVED: No longer taking from form
            ID_Polis = request.form['ID_Polis']
            Nama_Data_Polis = request.form['Nama_Data_Polis']
            Hubungan_Data_Polis = request.form['Hubungan_Data_Polis']
            Alamat_Data_Polis = request.form['Alamat_Data_Polis']
            Nomor_Telepon_Polis = request.form['Nomor_Telepon_Polis']
            ID_Nasabah = request.form['ID_Nasabah'] 
            # --- NEW Policy Holder Details (from data_polis table) ---
            # These fields are also added to the DB, so they should be collected here too.
            # I will assume they are added to the AddPolicyForm.html
            NIK_Pemegang_Polis = request.form['NIK_Pemegang_Polis']
            Jenis_Kelamin_Pemegang_Polis = request.form['Jenis_Kelamin_Pemegang_Polis']
            Tempat_Lahir_Pemegang_Polis = request.form['Tempat_Lahir_Pemegang_Polis']
            Tanggal_Lahir_Pemegang_Polis = request.form['Tanggal_Lahir_Pemegang_Polis']
            # --- End NEW Policy Holder Details ---


            form_data = request.form.to_dict() # Capture for re-population

            # MODIFIED VALIDATION: Check for the NEW policy holder fields.
            # And removed ID_Data_Polis from validation as it's now auto-generated
            if not all([ID_Polis, Nama_Data_Polis, Hubungan_Data_Polis, Alamat_Data_Polis, Nomor_Telepon_Polis, ID_Nasabah,
                        NIK_Pemegang_Polis, Jenis_Kelamin_Pemegang_Polis, Tempat_Lahir_Pemegang_Polis, Tanggal_Lahir_Pemegang_Polis]):
                return render_template('AddPolicyForm.html', form_data=form_data)

            # MODIFIED INSERT QUERY: Add new policy holder fields and use generated ID
            insert_query = """
                INSERT INTO data_polis (
                    ID_Data_Polis, ID_Polis, Nama_Data_Polis, Hubungan_Data_Polis, Alamat_Data_Polis, Nomor_Telepon_Polis,
                    ID_Nasabah, Tanggal_Polis_Dibuat, Status_Polis,
                    NIK_Pemegang_Polis, Jenis_Kelamin_Pemegang_Polis, Tempat_Lahir_Pemegang_Polis, Tanggal_Lahir_Pemegang_Polis
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), 'Approved', %s, %s, %s, %s)
            """
            cur.execute(insert_query, (
                new_data_polis_id, ID_Polis, Nama_Data_Polis, Hubungan_Data_Polis, Alamat_Data_Polis, Nomor_Telepon_Polis,
                ID_Nasabah,
                NIK_Pemegang_Polis, Jenis_Kelamin_Pemegang_Polis, Tempat_Lahir_Pemegang_Polis, Tanggal_Lahir_Pemegang_Polis
            ))
            conn.commit()
            return redirect (url_for('Policy'))
        
        # For GET request, simply render the form
        return render_template('AddPolicyForm.html', form_data=form_data)
    except pymysql.Error as e:
        if conn: conn.rollback()
        return "Error adding policy." # Placeholder for database error
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()

@app.route('/adminPolicyManagement/detail/<string:policy_id>', methods=['GET', 'POST'])
@admin_required
def adminPolicyDetail(policy_id):
    conn = None # Initialize conn to None
    cur = None  # Initialize cur to None
    try:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        if request.method == 'POST':
            new_status = request.form['status_polis']
            admin_notes_policy = request.form.get('admin_notes_policy', '')

            try:
                update_query = """
                    UPDATE data_polis SET
                    Status_Polis = %s,
                    Admin_Notes = %s
                    WHERE ID_Data_Polis = %s
                """
                cur.execute(update_query, (new_status, admin_notes_policy, policy_id))
                conn.commit()
                # flash('Policy status updated successfully!', 'success') # If you put back flash
                return redirect(url_for('adminPolicyDetail', policy_id=policy_id))
            except pymysql.Error as e:
                # flash(f'Error updating policy status: {e}', 'danger') # If you put back flash
                conn.rollback()
                # Important: If POST fails, you want to fall through to GET logic
                # to re-render the page with an error message and pre-filled form.
                # So, do NOT close connection here.
        
        # This part executes for GET requests OR if a POST request failed (and didn't redirect)
        cur.execute("""
            SELECT
                dp.*,
                n.Nama_Nasabah,
                n.Email_Nasabah,
                pa.Nama_Produk
            FROM
                data_polis dp
            JOIN
                nasabah n ON dp.ID_Nasabah = n.ID_Nasabah
            JOIN
                produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
            WHERE
                dp.ID_Data_Polis = %s
        """, (policy_id,))
        policy = cur.fetchone()

        if not policy:
            # flash('Policy not found.', 'danger') # If you put back flash
            return redirect(url_for('Policy'))

        policy_statuses = ['Approved', 'Rejected', 'Active', 'Expired']

        return render_template('adminPolicyDetail.html', policy=policy, policy_statuses=policy_statuses)

    finally:
        # This finally block ensures that cur and conn are closed
        # whether the function finishes successfully, redirects, or encounters an error.
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


@app.route('/adminPolicyManagement/update/<string:id>',methods=['GET','POST'])
@admin_required
def updatePolicy(id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM data_polis WHERE ID_Data_Polis = %s", id)
    data3 = cur.fetchone()

    if request.method == 'POST':
        Nama_Data_Polis = request.form['Nama_Data_Polis']
        Hubungan_Data_Polis = request.form['Hubungan_Data_Polis']
        Alamat_Data_Polis = request.form['Alamat_Data_Polis']
        Nomor_Telepon_Polis = request.form['Nomor_Telepon_Polis']

        if not all([Nama_Data_Polis, Hubungan_Data_Polis, Alamat_Data_Polis, Nomor_Telepon_Polis]):
            # flash('All fields are required!', 'danger') # Removed
            data_to_pass = request.form.to_dict()
            data_to_pass['ID_Data_Polis'] = id
            return render_template('UpdatePolicyForm.html', polis=data_to_pass)

        try:
            update_query = "UPDATE data_polis SET Nama_Data_Polis = %s, Hubungan_Data_Polis = %s, Alamat_Data_Polis = %s, Nomor_Telepon_Polis = %s WHERE ID_Data_Polis = %s"
            cur.execute(update_query, (Nama_Data_Polis, Hubungan_Data_Polis, Alamat_Data_Polis, Nomor_Telepon_Polis, id))
            conn.commit()
            # flash('Policy updated successfully!', 'success') # Removed
        except pymysql.Error as e:
            # flash(f'Error updating policy: {e}', 'danger') # Removed
            conn.rollback()
        finally:
            cur.close()
            conn.close()
        return redirect (url_for('Policy'))
    
    cur.close()
    conn.close()
    return render_template('UpdatePolicyForm.html',polis = data3)

@app.route('/adminPolicyManagement/delete/<string:id>',methods=['GET'])
@admin_required
def deletePolicy(id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute("DELETE FROM data_polis WHERE ID_Data_Polis = %s", id)
        conn.commit()
        # flash('Policy deleted successfully!', 'success') # Removed
    except pymysql.Error as e:
        # flash(f'Error deleting policy: {e}', 'danger') # Removed
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('Policy'))

@app.route('/adminClaimManagement/', methods=['GET'])
@admin_required
def adminClaimManagement():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
        SELECT
            ka.ID_Klaim,
            ka.Jenis_Klaim,
            ka.Tanggal_Kejadian,
            ka.Status_Klaim,
            ka.Tanggal_Pengajuan,
            ka.Jumlah_Klaim,
            n.Nama_Nasabah,
            pa.Nama_Produk,
            dp.Nama_Data_Polis,
            dp.ID_Data_Polis
        FROM
            klaim_asuransi ka
        JOIN
            nasabah n ON ka.ID_Nasabah = n.ID_Nasabah
        JOIN
            data_polis dp ON ka.ID_Data_Polis = dp.ID_Data_Polis
        JOIN
            produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
        ORDER BY
            ka.Tanggal_Pengajuan DESC
    """)
    claims = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('adminClaimManagement.html', claims=claims)

@app.route('/adminClaimManagement/detail/<string:claim_id>', methods=['GET', 'POST'])
@admin_required
def adminClaimDetail(claim_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        new_status = request.form['status_klaim']
        admin_notes = request.form['catatan_admin']

        try:
            update_query = """
                UPDATE klaim_asuransi SET
                Status_Klaim = %s,
                Catatan_Admin = %s
                WHERE ID_Klaim = %s
            """
            cur.execute(update_query, (new_status, admin_notes, claim_id))
            conn.commit()
            # flash('Claim updated successfully!', 'success') # Removed
            return redirect(url_for('adminClaimDetail', claim_id=claim_id))
        except pymysql.Error as e:
            # flash(f'Error updating claim: {e}', 'danger') # Removed
            conn.rollback()
        finally:
            cur.close()
            conn.close()
            
    cur.execute("""
        SELECT
            ka.*,
            n.Nama_Nasabah,
            n.Email_Nasabah,
            pa.Nama_Produk,
            dp.Nama_Data_Polis,
            dp.ID_Data_Polis,
            dp.Tanggal_Polis_Dibuat,
            dp.KTP_File,
            dp.NPWP_File,
            dp.KK_File
        FROM
            klaim_asuransi ka
        JOIN
            nasabah n ON ka.ID_Nasabah = n.ID_Nasabah
        JOIN
            data_polis dp ON ka.ID_Data_Polis = dp.ID_Data_Polis
        JOIN
            produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
        WHERE
            ka.ID_Klaim = %s
    """, (claim_id,))
    claim = cur.fetchone()

    cur.close()
    conn.close()

    if not claim:
        # flash('Claim not found.', 'danger') # Removed
        return redirect(url_for('adminClaimManagement'))

    claim_statuses = ['Pending', 'In Review', 'Approved', 'Rejected', 'Closed']

    return render_template('adminClaimDetail.html', claim=claim, claim_statuses=claim_statuses)

@app.route('/adminClaimManagement/delete/<string:claim_id>', methods=['GET'])
@admin_required
def adminDeleteClaim(claim_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute("DELETE FROM klaim_asuransi WHERE ID_Klaim = %s", (claim_id,))
        conn.commit()
        # flash('Claim deleted successfully!', 'success') # Removed
    except pymysql.Error as e:
        # flash(f'Error deleting claim: {e}', 'danger') # Removed
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('adminClaimManagement'))



# ====================================================================================================================
# USER ROUTES
# ====================================================================================================================

@app.route('/user_dashboard')
@user_required
def user_dashboard():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    user_id = session['id']

    cur.execute("SELECT COUNT(*) AS policy_count FROM data_polis WHERE ID_Nasabah = %s", (user_id,))
    policy_count = cur.fetchone()['policy_count']

    user_policies = []
    if policy_count > 0:
        cur.execute("""
            SELECT 
                dp.ID_Data_Polis, 
                dp.Nama_Data_Polis, 
                dp.Hubungan_Data_Polis,
                pa.Nama_Produk 
            FROM 
                data_polis dp
            JOIN 
                produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
            WHERE 
                dp.ID_Nasabah = %s 
            ORDER BY 
                dp.Tanggal_Polis_Dibuat DESC 
            LIMIT 5
        """, (user_id,))
        user_policies = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('user_dashboard.html',
                             username=session['username'],
                             policy_count=policy_count,
                             user_policies=user_policies)

@app.route('/user_products')
@user_required
def user_products():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT ID_Produk, Nama_Produk, Masa_Berlaku, Nama_Jenis_Asuransi, Premi_Bulanan FROM produk_asuransi")
    products = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('user_products.html', products=products)


@app.route('/user_products/<string:product_id>')
@user_required
def user_product_detail(product_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT ID_Produk, Nama_Produk, Masa_Berlaku,  Nama_Jenis_Asuransi, Premi_Bulanan FROM produk_asuransi WHERE ID_Produk = %s", (product_id,))
    product = cur.fetchone()

    cur.close()
    conn.close()

    if not product:
        # flash('Product not found!', 'danger') # Removed
        return redirect(url_for('user_products'))

    return render_template('user_product_detail.html', product=product)

@app.route('/user_products/apply/<string:product_id>', methods=['GET', 'POST'])
@user_required
def apply_for_policy(product_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT ID_Produk, Nama_Produk, Masa_Berlaku FROM produk_asuransi WHERE ID_Produk = %s", (product_id,))
    product = cur.fetchone()

    if not product:
        # flash('Product not found for application!', 'danger') # Removed
        cur.close()
        conn.close()
        return redirect(url_for('user_products'))

    form_data = request.form.to_dict()

    if request.method == 'POST':
        nama_data_polis = request.form['nama_data_polis']
        hubungan_data_polis = request.form['hubungan_data_polis']
        alamat_data_polis = request.form['alamat_data_polis']
        nomor_telepon_polis = request.form['nomor_telepon_polis']

        ktp_file = request.files.get('ktp_file')
        npwp_file = request.files.get('npwp_file')
        kk_file = request.files.get('kk_file')

        uploaded_ktp_filename = None
        uploaded_npwp_filename = None
        uploaded_kk_filename = None

        if not all([nama_data_polis, hubungan_data_polis, alamat_data_polis, nomor_telepon_polis]):
            # flash('All contact and address fields are required for policy application!', 'danger') # Removed
            return render_template('user_policy_apply.html', product=product, form_data=form_data)
            
        ktp_res = save_uploaded_file(ktp_file, app.config['UPLOAD_FOLDER_POLICY_DOCS'])
        if ktp_res == "INVALID_FILE_TYPE": return render_template('user_policy_apply.html', product=product, form_data=form_data)
        uploaded_ktp_filename = ktp_res

        npwp_res = save_uploaded_file(npwp_file, app.config['UPLOAD_FOLDER_POLICY_DOCS'])
        if npwp_res == "INVALID_FILE_TYPE": return render_template('user_policy_apply.html', product=product, form_data=form_data)
        uploaded_npwp_filename = npwp_res

        kk_res = save_uploaded_file(kk_file, app.config['UPLOAD_FOLDER_POLICY_DOCS'])
        if kk_res == "INVALID_FILE_TYPE": return render_template('user_policy_apply.html', product=product, form_data=form_data)
        uploaded_kk_filename = kk_res


        id_nasabah = session['id']
        new_data_polis_id = 'P' + str(uuid.uuid4().int)[:8]

        try:
            insert_query = """
                INSERT INTO data_polis (
                    ID_Data_Polis, ID_Polis, Nama_Data_Polis, Hubungan_Data_Polis,
                    Alamat_Data_Polis, Nomor_Telepon_Polis, ID_Nasabah, Tanggal_Polis_Dibuat,
                    KTP_File, NPWP_File, KK_File, Status_Polis
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, 'Pending')
            """
            cur.execute(insert_query, (
                new_data_polis_id, product['ID_Produk'], nama_data_polis,
                hubungan_data_polis, alamat_data_polis, nomor_telepon_polis,
                id_nasabah,
                uploaded_ktp_filename, uploaded_npwp_filename, uploaded_kk_filename
            ))
            conn.commit()
            # flash(f'Successfully applied for "{product["Nama_Produk"]}"! Your policy ID is {new_data_polis_id}. Your application is pending approval.', 'success') # Removed
            return redirect(url_for('user_dashboard'))
        except pymysql.Error as e:
            # flash(f'Error applying for policy: {e}', 'danger') # Removed
            conn.rollback()
            if uploaded_ktp_filename and uploaded_ktp_filename != "INVALID_FILE_TYPE": os.remove(os.path.join(app.config['UPLOAD_FOLDER_POLICY_DOCS'], uploaded_ktp_filename))
            if uploaded_npwp_filename and uploaded_npwp_filename != "INVALID_FILE_TYPE": os.remove(os.path.join(app.config['UPLOAD_FOLDER_POLICY_DOCS'], uploaded_npwp_filename))
            if uploaded_kk_filename and uploaded_kk_filename != "INVALID_FILE_TYPE": os.remove(os.path.join(app.config['UPLOAD_FOLDER_POLICY_DOCS'], uploaded_kk_filename))
        finally:
            cur.close()
            conn.close()
            
    cur.close()
    conn.close()
    return render_template('user_policy_apply.html', product=product, form_data=form_data)

@app.route('/my_policies')
@user_required
def my_policies():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    user_id = session['id']

    cur.execute("""
        SELECT
            dp.ID_Data_Polis,
            dp.ID_Polis,
            dp.Nama_Data_Polis,
            dp.Hubungan_Data_Polis,
            dp.Alamat_Data_Polis,
            dp.Nomor_Telepon_Polis,
            dp.Tanggal_Polis_Dibuat,
            pa.Nama_Produk,
            pa.Masa_Berlaku,
            dp.KTP_File,
            dp.NPWP_File,
            dp.KK_File,
            dp.Status_Polis
        FROM
            data_polis dp
        JOIN
            produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
        WHERE
            dp.ID_Nasabah = %s
        ORDER BY
            dp.Tanggal_Polis_Dibuat DESC
    """, (user_id,))
    user_policies = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('my_policies.html', user_policies=user_policies)

@app.route('/my_policies/<string:policy_id>')
@user_required
def policy_detail(policy_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    user_id = session['id']

    cur.execute("""
        SELECT
            dp.*,
            pa.Nama_Produk,
            pa.Masa_Berlaku,
            n.Nama_Nasabah,
            n.Email_Nasabah
        FROM
            data_polis dp
        JOIN
            produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
        JOIN
            nasabah n ON dp.ID_Nasabah = n.ID_Nasabah
        WHERE
            dp.ID_Data_Polis = %s AND dp.ID_Nasabah = %s
    """, (policy_id, user_id,))
    policy = cur.fetchone()

    cur.close()
    conn.close()

    if not policy:
        # flash('Policy not found or you do not have permission to view it.', 'danger') # Removed
        return redirect(url_for('my_policies'))
    
    return render_template('policy_detail.html', policy=policy)

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/claim/submit', methods=['GET', 'POST'])
@user_required
def submit_claim():
    conn = None # Initialize conn to None
    cur = None  # Initialize cur to None
    user_id = session['id']

    user_policies = []
    form_data = request.form.to_dict() # Capture form data for re-population

    # Flag to indicate if there are no approved policies, for template rendering
    no_active_policies_found = False

    try:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # Fetch ONLY 'Approved' policies for the user
        cur.execute("""
            SELECT 
                dp.ID_Data_Polis, 
                pa.Nama_Produk,
                dp.Nama_Data_Polis,
                dp.Tanggal_Polis_Dibuat,
                dp.Status_Polis
            FROM 
                data_polis dp
            JOIN 
                produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
            WHERE 
                dp.ID_Nasabah = %s AND dp.Status_Polis = 'Active'
            ORDER BY
                dp.Tanggal_Polis_Dibuat DESC
        """, (user_id,))
        user_policies = cur.fetchall()

        if not user_policies:
            no_active_policies_found = True # Set flag for template

        if request.method == 'POST':
            # If no approved policies were found on GET, and user somehow submits, prevent processing
            if no_active_policies_found:
                # No redirect needed, just re-render with the message
                return render_template('submit_claim.html', user_policies=[], form_data=form_data, no_active_policies_found=True)


            id_data_polis = request.form['id_data_polis']
            jenis_klaim = request.form['jenis_klaim']
            tanggal_kejadian = request.form['tanggal_kejadian']
            lokasi_kejadian = request.form['lokasi_kejadian']
            deskripsi_kejadian = request.form['deskripsi_kejadian']
            jumlah_klaim = request.form.get('jumlah_klaim')
            
            dokumen_pendukung_filename = None # Optional new field

            # --- Critical Validation: Check selected policy's status AGAIN on POST ---
            cur.execute("SELECT Status_Polis FROM data_polis WHERE ID_Data_Polis = %s AND ID_Nasabah = %s", (id_data_polis, user_id,))
            selected_policy_status = cur.fetchone()

            if not selected_policy_status or selected_policy_status['Status_Polis'] != 'Active':
                # flash('The selected policy is not approved. You can only submit claims on approved policies.', 'danger') # Removed
                # Re-render with form data and approved policies list
                # Re-fetch approved policies in case status changed for others too
                cur.execute("""
                    SELECT 
                        dp.ID_Data_Polis, 
                        pa.Nama_Produk,
                        dp.Nama_Data_Polis,
                        dp.Tanggal_Polis_Dibuat,
                        dp.Status_Polis
                    FROM 
                        data_polis dp
                    JOIN 
                        produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
                    WHERE 
                        dp.ID_Nasabah = %s AND dp.Status_Polis = 'Approved'
                    ORDER BY
                        dp.Tanggal_Polis_Dibuat DESC
                """, (user_id,))
                user_policies_reloaded = cur.fetchall()
                # Ensure no_approved_policies_found flag is updated for the template
                no_active_policies_found = not user_policies_reloaded
                return render_template('submit_claim.html', user_policies=user_policies_reloaded, form_data=form_data, no_active_policies_found=no_active_policies_found)


            # Validation: Check all required fields (excluding description, amount, document)
            if not all([id_data_polis, jenis_klaim, tanggal_kejadian, lokasi_kejadian]):
                # flash('Please fill out all required claim details (excluding description, amount, and documents).', 'danger') # Removed
                return render_template('submit_claim.html', user_policies=user_policies, form_data=form_data, no_active_policies_found=no_active_policies_found)


            # Handle file upload (unchanged)
            if 'dokumen_pendukung' in request.files:
                file = request.files['dokumen_pendukung']
                if file.filename == '':
                    pass 
                elif file and allowed_file(file.filename):
                    original_filename = secure_filename(file.filename)
                    unique_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
                    file_path = os.path.join(app.config['UPLOAD_FOLDER_CLAIMS'], unique_filename)
                    file.save(file_path)
                    dokumen_pendukung_filename = unique_filename
                else:
                    # flash('Invalid file type for supporting documents. Allowed: png, jpg, jpeg, pdf, doc, docx.', 'danger') # Removed
                    return render_template('submit_claim.html', user_policies=user_policies, form_data=form_data, no_active_policies_found=no_active_policies_found)

            new_claim_id = 'K' + str(uuid.uuid4().int)[:8]

            insert_query = """
                INSERT INTO klaim_asuransi (
                    ID_Klaim, ID_Nasabah, ID_Data_Polis, Jenis_Klaim, Tanggal_Kejadian,
                    Lokasi_Kejadian, Deskripsi_Kejadian, Jumlah_Klaim, Dokumen_Pendukung, Tanggal_Pengajuan, Status_Klaim
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
            """
            cur.execute(insert_query, (
                new_claim_id, user_id, id_data_polis, jenis_klaim, tanggal_kejadian,
                lokasi_kejadian, deskripsi_kejadian, jumlah_klaim if jumlah_klaim else None,
                dokumen_pendukung_filename,
                'Pending'
            ))
            conn.commit()
            # flash(f'Your claim (ID: {new_claim_id}) has been submitted successfully!', 'success') # Removed
            return redirect(url_for('my_claims'))
        
    except pymysql.Error as e:
        # flash(f'Error submitting claim: {e}', 'danger') # Removed
        conn.rollback()
        if dokumen_pendukung_filename and dokumen_pendukung_filename != "INVALID_FILE_TYPE":
             os.remove(os.path.join(app.config['UPLOAD_FOLDER_CLAIMS'], dokumen_pendukung_filename))
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    
    # Final render for GET requests or failed POSTs (before redirect)
    return render_template('submit_claim.html', user_policies=user_policies, form_data=form_data, no_active_policies_found=no_active_policies_found)
@app.route('/my_claims')
@user_required
def my_claims():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    user_id = session['id']

    cur.execute("""
        SELECT
            ka.ID_Klaim,
            ka.Jenis_Klaim,
            ka.Tanggal_Kejadian,
            ka.Status_Klaim,
            ka.Tanggal_Pengajuan,
            pa.Nama_Produk,
            dp.Nama_Data_Polis
        FROM
            klaim_asuransi ka
        JOIN
            data_polis dp ON ka.ID_Data_Polis = dp.ID_Data_Polis
        JOIN
            produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
        WHERE
            ka.ID_Nasabah = %s
        ORDER BY
            ka.Tanggal_Pengajuan DESC
    """, (user_id,))
    claims = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('my_claims.html', claims=claims)

@app.route('/my_claims/<string:claim_id>')
@user_required
def claim_detail(claim_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    user_id = session['id']

    cur.execute("""
        SELECT
            ka.*,
            pa.Nama_Produk,
            dp.Nama_Data_Polis,
            dp.ID_Data_Polis,
            dp.Tanggal_Polis_Dibuat,
            ka.Dokumen_Pendukung,
            dp.KTP_File,
            dp.NPWP_File,
            dp.KK_File
        FROM
            klaim_asuransi ka
        JOIN
            data_polis dp ON ka.ID_Data_Polis = dp.ID_Data_Polis
        JOIN
            produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
        WHERE
            ka.ID_Klaim = %s AND ka.ID_Nasabah = %s
    """, (claim_id, user_id,))
    claim = cur.fetchone()

    cur.close()
    conn.close()

    if not claim:
        # flash('Claim not found or you do not have permission to view it.', 'danger') # Removed
        return redirect(url_for('my_claims'))
    
    return render_template('claim_detail.html', claim=claim)


@app.route('/claim/status')
@user_required
def check_claim_status():
    return render_template('check_claim_status.html')

@app.route('/payment/<string:policy_id>')
@user_required
def initiate_payment(policy_id):
    conn = None
    cur = None
    try:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        user_id = session['id']

        # Verify the policy exists, belongs to the user, and is APPROVED
        cur.execute("""
            SELECT ID_Data_Polis, Nama_Produk, Premi_Bulanan, Status_Polis
            FROM data_polis dp
            JOIN produk_asuransi pa ON dp.ID_Polis = pa.ID_Produk
            WHERE dp.ID_Data_Polis = %s AND dp.ID_Nasabah = %s AND dp.Status_Polis = 'Approved'
        """, (policy_id, user_id))
        policy_to_pay = cur.fetchone()

        if not policy_to_pay:
            return redirect(url_for('my_policies'))

        update_query = """
            UPDATE data_polis SET Status_Polis = 'Active' WHERE ID_Data_Polis = %s
        """
        cur.execute(update_query, (policy_id,))
        conn.commit()

        # Redirect user back to My Policies or a payment confirmation page
        return redirect(url_for('my_policies')) # Successfully initiated/completed

    except pymysql.Error as e:
        if conn: conn.rollback()
        return redirect(url_for('my_policies')) # Handle error during payment initiation
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()

# ... (rest of your app.py, including admin routes) ...

if __name__ == '__main__':
    app.run(debug=True)