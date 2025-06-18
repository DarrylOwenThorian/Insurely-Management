Insurely is a insurance management platform that is designed to help agents and users to manage their insurances. This platform provides several useful features on managing owned insurance, claiming requests, and for agents to manage users. With this, we hope that insurance managing process such as adding more products, requesting claims, and user account management will be improved.

The application have 3 expected users:
Users, acts as the customer,  named as "nasabah" on the database.
Agents, acts as the manager, named as "admin_users" on the database.
Master, acts as the owner, is you.

before running the application, these libraries should be installed on the computer first :
pymysql library - pip install PyMySQL
Flask - pip install flask
Flaskext - pip install Flask-MySQL
bcrpt - pip install flask-bcrypt

As for the mySQL file, it is in the directory named as 'attempt1' for use, its named such because i expected to do way more attempts on the database, feel free to rename it as you wanted. Before running the app make sure to import the mySQL file into any database tools and to change the configuration in 'app.py' according to the name that was used.

Keep in mind there is some redundant data in the current database that is has not been dropped, such as "agen" that is supposed to be used as the Agent data, yet it uses admin_users instead, please ignore them.

