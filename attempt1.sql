-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 18, 2025 at 04:44 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `attempt1`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin_users`
--

CREATE TABLE `admin_users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin_users`
--

INSERT INTO `admin_users` (`id`, `username`, `password`, `email`, `created_at`) VALUES
(6, 'Owen', 'scrypt:32768:8:1$xaKtiWVMVElQObdK$14362dae94d7b3a1370d39e5a47a5416ffb1f541a6764429e6083f6c530ea841712a49a8a4b43efdd59ac4874cbe7664e0f892e5c2090b7907f2387c68c4f789', 'owen@gmail.com', '2025-06-09 04:53:10');

-- --------------------------------------------------------

--
-- Table structure for table `agen`
--

CREATE TABLE `agen` (
  `ID_Agen` varchar(55) NOT NULL,
  `Nama_Agen` varchar(55) DEFAULT NULL,
  `Kontak_Agen` varchar(55) DEFAULT NULL,
  `Email_Agen` varchar(55) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `agen`
--

INSERT INTO `agen` (`ID_Agen`, `Nama_Agen`, `Kontak_Agen`, `Email_Agen`) VALUES
('A001', 'Ahmad Hidayat', '34567890', 'ahmad.hidayat@gmail.com'),
('A002', 'Dian', '081264567870', 'dian.purnama@gmail.com'),
('A003', 'Sarah Mentari', '081363677875', 'sarah.mentari@gmail.com'),
('A004', 'Axel Agustiana', '081265667875', 'axel.agustiana@gmail.com'),
('A005', 'Azrul Nauval Zulaeha', '081363417873', 'azrul.nauva.zulaeha@gmail.com'),
('A006', 'Achmad Lalo', '0812835547690', 'achmad.lalo@gmail.com'),
('A007', 'Yuda Octaviana', '081365673870', 'yuda.octaviana@gmail.com'),
('A008', 'Fajri Usmani', '081233673875', 'fajri.usmani@gmail.com'),
('A009', 'Reny Parhorasan', '081284567697', 'reny.parhorasan@gmail.com'),
('A010', 'Tessa Prasetyo', '081363637871', 'tessa.prasetyo@gmail.com');

-- --------------------------------------------------------

--
-- Table structure for table `data_polis`
--

CREATE TABLE `data_polis` (
  `ID_Data_Polis` varchar(55) NOT NULL,
  `ID_Polis` varchar(55) DEFAULT NULL,
  `Nama_Data_Polis` varchar(55) DEFAULT NULL,
  `Hubungan_Data_Polis` varchar(55) DEFAULT NULL,
  `Alamat_Data_Polis` varchar(255) DEFAULT NULL,
  `Nomor_Telepon_Polis` varchar(55) DEFAULT NULL,
  `ID_Nasabah` varchar(255) DEFAULT NULL,
  `Tanggal_Polis_Dibuat` date DEFAULT NULL,
  `KTP_File` varchar(255) DEFAULT NULL,
  `NPWP_File` varchar(255) DEFAULT NULL,
  `KK_File` varchar(255) DEFAULT NULL,
  `Status_Polis` varchar(50) DEFAULT NULL,
  `Admin_Notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `data_polis`
--

INSERT INTO `data_polis` (`ID_Data_Polis`, `ID_Polis`, `Nama_Data_Polis`, `Hubungan_Data_Polis`, `Alamat_Data_Polis`, `Nomor_Telepon_Polis`, `ID_Nasabah`, `Tanggal_Polis_Dibuat`, `KTP_File`, `NPWP_File`, `KK_File`, `Status_Polis`, `Admin_Notes`) VALUES
('DP021', 'POL021', 'Bima Surya', 'Istri', 'Jl. Mayjen Sungkono No.12, Surabaya', '081123435480', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP022', 'POL022', 'Putrima Al-fathan', 'Pemilik', 'Jl. Malioboro No.78, Yogyakarta', '082234567891', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP023', 'POL023', 'Putrima Al-fathan', 'Pemilik', 'Jl. Malioboro No.78, Yogyakarta', '082234567891', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP024', 'POL024', 'Putra Kusnanto', 'Anak', 'Jl. Pemuda No.34, Semarang', '081364567802', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP025', 'POL025', 'Monica Syahputra', 'Pemilik', 'Jl. Semeru No.56, Malang', '084456789013', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP026', 'POL026', 'Linda Wati', 'Pemilik', 'Jl. Semeru No.56, Malang', '084456789013', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP027', 'POL027', 'Farrel Dwitama', 'Suami', 'Jl. Rasuna Said No.89, Jakarta', '081356789124', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP028', 'POL028', 'Putri Kemala', 'Istri', 'Jl. Pasteur No.23, Bandung', '081367895235', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP029', 'POL029', 'Oscar Pratama', 'Pemilik', 'Jl. HR Muhammad No.45, Surabaya', '087789012346', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP030', 'POL030', 'Oscar Pratama', 'Pemilik', 'Jl. HR Muhammad No.45, Surabaya', '087789012346', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP031', 'POL031', 'Renita Juwita', 'Pemilik', 'Jl. Kaliurang No.67, Yogyakarta', '088890123457', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP032', 'POL032', 'Putri Maharani', 'Pemilik', 'Jl. Kaliurang No.67, Yogyakarta', '088890123457', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP033', 'POL033', 'Mochammad Septian', 'Suami', 'Jl. Pahlawan No.90, Semarang', '081201234558', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP034', 'POL034', 'Nella Kinandatsani', 'Pemilik', 'Jl. Soekarno Hatta No.12, Malang', '081234567892', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('DP035', 'POL035', 'Nella Kinandatsani', 'Pemilik', 'Jl. Soekarno Hatta No.12, Malang', '081234567892', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('P10243285', 'P002', 'Vincent', 'Pemilik', 'jakarta', '08123456789', 'N89020818', '2025-06-09', 'b431f817-679d-4eef-8dcc-be9b761a14ae.jpg', '526038f4-e746-46bf-99fb-efd313e65432.jpg', '1f51d4f2-6f60-47a5-919c-8fa37aede034.jpg', 'Active', 'alasan'),
('P16289587', 'P001', 'Niko', 'Pemilik', 'Jakarta', '08123456768', 'N13824151', '2025-06-09', 'c270267d-b796-4f3f-bdbe-206dc0a6aa3f.jpg', '5dc17310-51ff-41b4-b53b-f2546fa15986.jpg', '6e7c9f15-5ee4-40cd-b4f6-04f8a3f24e4c.jpg', 'Active', 'approv'),
('P17023510', 'P001', 'rahel', 'Pemilik', 'jakarta', '08123456789', 'N28443800', '2025-06-09', NULL, NULL, NULL, NULL, NULL),
('P19482027', 'P002', 'rahel', 'Pemilik', 'Jakarta', '08123456789', 'N29084254', '2025-06-18', '187e2c59-771f-49d8-be53-2c18da12fc09.jpg', 'b15f7ff5-cd32-46eb-9643-76e86f97f464.jpg', '328ba61c-6b19-4461-b081-dc2962eb90de.jpg', 'Active', 'saya terima'),
('P32940557', 'P001', 'Owen', 'Pemilik', 'Jakarta', '08123456789', 'N001', '2025-06-09', '8e96cfa2-fe91-4d94-a491-40229490a108.jpg', '7e6e8d59-0ffd-43c9-8c7b-1a9d2378ac93.jpg', '9f42ea74-6f83-4442-9c03-2a333a2c6284.jpg', 'Pending', NULL),
('P58150938', 'P002', 'Owen', 'Pemilik', 'Jakarta', '08123456789', 'N001', '2025-06-18', '206705eb-9ab2-4ba2-bb1d-e497511b044c.jpg', 'c5b47287-1c4c-4708-9ac4-4ea9484febb3.jpg', '8d95b24a-73b9-4a40-ba88-6ac61142e954.jpg', 'Active', 'None');

-- --------------------------------------------------------

--
-- Table structure for table `klaim_asuransi`
--

CREATE TABLE `klaim_asuransi` (
  `ID_Klaim` varchar(20) NOT NULL,
  `ID_Nasabah` varchar(20) NOT NULL,
  `ID_Data_Polis` varchar(20) NOT NULL,
  `Jenis_Klaim` varchar(50) DEFAULT NULL,
  `Tanggal_Kejadian` date DEFAULT NULL,
  `Lokasi_Kejadian` varchar(255) DEFAULT NULL,
  `Deskripsi_Kejadian` text DEFAULT NULL,
  `Jumlah_Klaim` decimal(15,2) DEFAULT NULL,
  `Dokumen_Pendukung` text DEFAULT NULL,
  `Status_Klaim` varchar(50) DEFAULT 'Pending',
  `Tanggal_Pengajuan` datetime DEFAULT current_timestamp(),
  `Catatan_Admin` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `klaim_asuransi`
--

INSERT INTO `klaim_asuransi` (`ID_Klaim`, `ID_Nasabah`, `ID_Data_Polis`, `Jenis_Klaim`, `Tanggal_Kejadian`, `Lokasi_Kejadian`, `Deskripsi_Kejadian`, `Jumlah_Klaim`, `Dokumen_Pendukung`, `Status_Klaim`, `Tanggal_Pengajuan`, `Catatan_Admin`) VALUES
('K18247111', 'N13824151', 'P16289587', 'Medis', '2025-06-09', 'Jakarta', 'contoh', 1000000.00, NULL, 'Approved', '2025-06-09 16:13:27', 'diterima'),
('K24624053', 'N89020818', 'P10243285', 'Medical', '2025-06-09', 'Jakarta', 'deskripsi', 1000000.00, NULL, 'Pending', '2025-06-09 20:18:49', NULL),
('K26005892', 'N001', 'P58150938', 'Medis', '2025-06-18', 'Jakarta', 'Tabrakan di Jalan', 1000000.00, NULL, 'Pending', '2025-06-18 18:19:47', NULL),
('K31790778', 'N29084254', 'P19482027', 'Medical', '2025-06-18', 'Jakarta', 'Jatuh', 1000000.00, '3e5e9f9f-eca4-48a7-88df-b665a9be22bc.jpg', 'Approved', '2025-06-18 20:15:19', 'diterima');

-- --------------------------------------------------------

--
-- Table structure for table `nasabah`
--

CREATE TABLE `nasabah` (
  `ID_Nasabah` varchar(55) NOT NULL,
  `NIK_Nasabah` varchar(55) DEFAULT NULL,
  `Nama_Nasabah` varchar(255) DEFAULT NULL,
  `Jenis_Kelamin_Nasabah` varchar(55) DEFAULT NULL,
  `Tempat_Lahir_Nasabah` varchar(55) DEFAULT NULL,
  `Tanggal_Lahir_Nasabah` date DEFAULT NULL,
  `Alamat_Nasabah` varchar(255) DEFAULT NULL,
  `No_Telepon_Nasabah` varchar(55) DEFAULT NULL,
  `Email_Nasabah` varchar(55) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `nasabah`
--

INSERT INTO `nasabah` (`ID_Nasabah`, `NIK_Nasabah`, `Nama_Nasabah`, `Jenis_Kelamin_Nasabah`, `Tempat_Lahir_Nasabah`, `Tanggal_Lahir_Nasabah`, `Alamat_Nasabah`, `No_Telepon_Nasabah`, `Email_Nasabah`, `password_hash`) VALUES
('N001', NULL, 'owin', NULL, NULL, NULL, NULL, NULL, 'owen@gmail.com', 'scrypt:32768:8:1$Gv0HXcqHYpg4sRJt$7efde7ce716e7fe6b9f1ed0ebad82f4b5a35a7b5f708bb845f08a32ed62684c08b1e9dd70da9ec7f17600fec57c89e7373b51dfa06673d631015cbd57fdbe956'),
('N13824151', NULL, 'Niko', NULL, NULL, NULL, NULL, NULL, 'niko@gmail.com', 'scrypt:32768:8:1$dHI2fQUjnkDGD5fG$81826dbae07909d915813bfde45b1ea9a8aa51028f92ca7813f60459ee3287b33a5fe1aa93ee6e80e305a06b6c7ad5cb89df1caf36b2e974efb33ab92898f4a7'),
('N13824152', NULL, 'owinn', NULL, NULL, NULL, NULL, NULL, 'owinna@gmail.com', 'scrypt:32768:8:1$ZHrrzFu0Ub8fjLQV$76e586fe82785233046a3adb4f99743bd8ad5ba73782f129d32c4b3944df8d87353fbb1fa8d207378ce6251a40bd5d28dbdc8ce111ba91c7389b259fe5d3a2e7'),
('N29084254', NULL, 'rahel', NULL, NULL, NULL, NULL, NULL, 'rahel@gmail.com', 'scrypt:32768:8:1$mGl8NqzUrR12UBwa$cb849a7e93a7d8b2fc2360b615435809d5e9d6fe941f2feed21a26b45edbe9b5d1c82357709053fbc1a784eba4475fb614290bead1e2ce39c78e6ae5c135e163'),
('N89020818', NULL, 'Vincent', NULL, NULL, NULL, NULL, NULL, 'vincent@gmail.com', 'scrypt:32768:8:1$PcKf8gj5AglaWGm3$5008fb7308ef865ad173cea72ea75eaccdde62bd004fde4889820651630aaf1736f942dcd07b902062ed76af56b01da032d661fae5d3c0237128b4ee721c11d2');

-- --------------------------------------------------------

--
-- Table structure for table `polis`
--

CREATE TABLE `polis` (
  `ID_Polis` varchar(55) NOT NULL,
  `ID_Nasabah` varchar(55) DEFAULT NULL,
  `ID_Produk` varchar(55) DEFAULT NULL,
  `ID_Agen` varchar(55) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `produk_asuransi`
--

CREATE TABLE `produk_asuransi` (
  `ID_Produk` varchar(55) NOT NULL,
  `Nama_Produk` varchar(55) DEFAULT NULL,
  `Masa_Berlaku` varchar(55) DEFAULT NULL,
  `Nama_Jenis_Asuransi` varchar(100) DEFAULT NULL,
  `Premi_Bulanan` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `produk_asuransi`
--

INSERT INTO `produk_asuransi` (`ID_Produk`, `Nama_Produk`, `Masa_Berlaku`, `Nama_Jenis_Asuransi`, `Premi_Bulanan`) VALUES
('P002', 'Sehat Sejahtera', '4 Tahun', 'Kesehatan Keluarga', 200000),
('P003', 'Pendidikan Plus', '4 Tahun', 'Pendidikan Anak', 180000),
('P004', 'Kendaraan Aman', '4 Tahun', 'Kendaraan Bermotor', 170000),
('P005', 'Properti Aman', '4 Tahun', 'Properti & Rumah', 160000),
('P006', 'Proteksi Elektronik', '4 Tahun', 'Elektronik', 100000);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin_users`
--
ALTER TABLE `admin_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `agen`
--
ALTER TABLE `agen`
  ADD PRIMARY KEY (`ID_Agen`);

--
-- Indexes for table `data_polis`
--
ALTER TABLE `data_polis`
  ADD PRIMARY KEY (`ID_Data_Polis`),
  ADD KEY `fk_data_polis_polis` (`ID_Polis`);

--
-- Indexes for table `klaim_asuransi`
--
ALTER TABLE `klaim_asuransi`
  ADD PRIMARY KEY (`ID_Klaim`),
  ADD KEY `ID_Nasabah` (`ID_Nasabah`),
  ADD KEY `ID_Data_Polis` (`ID_Data_Polis`);

--
-- Indexes for table `nasabah`
--
ALTER TABLE `nasabah`
  ADD PRIMARY KEY (`ID_Nasabah`);

--
-- Indexes for table `polis`
--
ALTER TABLE `polis`
  ADD PRIMARY KEY (`ID_Polis`),
  ADD KEY `ID_Produk` (`ID_Produk`),
  ADD KEY `ID_Agen` (`ID_Agen`),
  ADD KEY `fk_polis_nasabah` (`ID_Nasabah`);

--
-- Indexes for table `produk_asuransi`
--
ALTER TABLE `produk_asuransi`
  ADD PRIMARY KEY (`ID_Produk`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin_users`
--
ALTER TABLE `admin_users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `klaim_asuransi`
--
ALTER TABLE `klaim_asuransi`
  ADD CONSTRAINT `klaim_asuransi_ibfk_1` FOREIGN KEY (`ID_Nasabah`) REFERENCES `nasabah` (`ID_Nasabah`),
  ADD CONSTRAINT `klaim_asuransi_ibfk_2` FOREIGN KEY (`ID_Data_Polis`) REFERENCES `data_polis` (`ID_Data_Polis`);

--
-- Constraints for table `polis`
--
ALTER TABLE `polis`
  ADD CONSTRAINT `fk_polis_nasabah` FOREIGN KEY (`ID_Nasabah`) REFERENCES `nasabah` (`ID_Nasabah`) ON DELETE CASCADE,
  ADD CONSTRAINT `polis_ibfk_2` FOREIGN KEY (`ID_Produk`) REFERENCES `produk_asuransi` (`ID_Produk`),
  ADD CONSTRAINT `polis_ibfk_3` FOREIGN KEY (`ID_Agen`) REFERENCES `agen` (`ID_Agen`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
