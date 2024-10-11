-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 10, 2024 at 05:16 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `filterlab`
--

-- --------------------------------------------------------

--
-- Table structure for table `object`
--

CREATE TABLE `filters` (
  `file_id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `filter_path` varchar(255) DEFAULT NULL,
  `text` varchar(255) DEFAULT NULL,
  `object_path` varchar(255) DEFAULT NULL,
  `bg_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `object`
--

INSERT INTO `filters` (`file_id`, `name`, `filter_path`, `text`, `object_path`, `bg_path`) VALUES
(1, 'filter1', 'static/img/filter1.png', 'filter1', NULL, 'static/img/bg1.webp'),
(2, 'filter2', 'static/img/filter2.png', 'filter2', NULL, 'static/img/bg1.webp'),
(3, 'filter3', 'static/img/filter3.png', 'filter3', NULL, 'static/img/bg1.webp'),
(4, 'filter4', 'static/img/filter4.png', 'filter4', NULL, 'static/img/bg1.webp'),
(5, 'filter5', 'static/img/filter6.png', 'filter5', NULL, 'static/img/bg1.webp'),
(6, 'filter6', 'static/img/filter7.png', 'filter6', NULL, 'static/img/bg1.webp');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `object`
--
ALTER TABLE `filters`
  ADD PRIMARY KEY (`file_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `object`
--
ALTER TABLE `filters`
  MODIFY `file_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
