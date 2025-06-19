-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 18, 2025 at 08:57 PM
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
-- Database: `healthcheck`
--

-- --------------------------------------------------------

--
-- Table structure for table `doctors`
--

CREATE TABLE `doctors` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `specialization` varchar(100) NOT NULL,
  `experience` int(11) DEFAULT NULL,
  `contact` varchar(15) NOT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `added_on` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `doctors`
--

INSERT INTO `doctors` (`id`, `name`, `specialization`, `experience`, `contact`, `photo_path`, `added_on`) VALUES
(1, 'Rohit Singh', 'Cardiologist', 5, '7485691235', 'static/Doctors_Photo\\Rohit.jpg', '2025-05-22 07:28:49'),
(2, 'Dr. Aditya Verma', 'Cardiologist', 7, '9876543023', 'static/Doctors_Photo\\Aditya.jpg', '2025-05-22 15:13:31'),
(3, 'Dr. Aniruddha Mandal', 'Cardiologist', 5, '7689450231', 'static/Doctors_Photo\\Anuradha.jpg', '2025-05-22 15:21:06'),
(4, 'Dr. Anil Mishra', 'Cardiologist', 4, '6789340256', 'static/Doctors_Photo\\Anil.jpg', '2025-05-22 15:21:53'),
(5, 'Dr. Anoop Misra', 'Diabetologist', 6, '7803267891', 'static/Doctors_Photo\\dhiman.jpg', '2025-05-22 15:23:21'),
(6, 'Dr. Sudipta Dutta', 'Diabetologist', 5, '9905674321', 'static/Doctors_Photo\\a_1.jpg', '2025-05-22 15:46:15'),
(8, 'Dr. Rajendiran N', 'Diabetologist', 10, '7804563218', 'static/Doctors_Photo\\a_15.webp', '2025-05-22 15:49:21'),
(9, 'Dr. Debasish Saha', 'Diabetologist', 6, '9256731804', 'static/Doctors_Photo\\a_11.jpg', '2025-05-22 15:50:27'),
(10, 'Dr. Bhawna Siroh', 'Oncologist (Breast)', 8, '8567094327', 'static/Doctors_Photo\\a_2.jpg', '2025-05-22 15:51:55'),
(11, 'Dr. Meenu Walia', 'Oncologist (Breast)', 6, '9769036216', 'static/Doctors_Photo\\a_3.jpg', '2025-05-22 15:53:14'),
(12, 'Dr. Rajesh Mistry', 'Oncologist (Breast)', 7, '7435690821', 'static/Doctors_Photo\\a_10.jpg', '2025-05-22 16:00:24'),
(13, 'Dr. Kapil Kumar', 'Oncologist (Breast)', 8, '9945678234', 'static/Doctors_Photo\\a_6.jpg', '2025-05-22 16:01:54'),
(14, 'Dr. Mohit Bhatt', 'Neurologist (Parkinson)', 7, '8045678234', 'static/Doctors_Photo\\a_21.jpg', '2025-05-22 16:08:21'),
(15, 'Dr. Geetha Lakshmipathy', 'Neurologist (Parkinson)', 8, '7569083451', 'static/Doctors_Photo\\a_8.jpg', '2025-05-22 16:08:57'),
(16, 'Dr. Abhishek Srivastava', 'Neurologist (Parkinson)', 12, '9706542987', 'static/Doctors_Photo\\a_4.jpg', '2025-05-22 16:13:37'),
(17, 'Dr. Dhanaraj M', 'Neurologist (Parkinson)', 7, '9167283405', 'static/Doctors_Photo\\a_23.jpg', '2025-05-22 16:14:43'),
(18, 'Dr. Govardhan Gupta', 'Nephrologist', 17, '8859043261', 'static/Doctors_Photo\\Govardhan_gupta.jpeg', '2025-05-22 16:18:39'),
(19, 'Dr Sanjay Maitra', 'Nephrologist', 30, '9768043571', 'static/Doctors_Photo\\Dr.-Sanjay-Maitra.webp', '2025-05-22 16:20:07'),
(20, 'Dr. Avinandan Banerjee', 'Nephrologist', 8, '8906578421', 'static/Doctors_Photo\\a_5.jpg', '2025-05-22 16:22:54'),
(21, 'Dr. Anirban Chatterjee', 'Gastroenterologist', 37, '7756342109', 'static/Doctors_Photo\\anirban.webp', '2025-05-22 16:25:35'),
(22, 'Dr. Partha Pratim Biswas', 'Gastroenterologist', 36, '7906584213', 'static/Doctors_Photo\\partha.webp', '2025-05-22 16:26:14'),
(23, 'Dr. Sanjay Dey Bakshi', 'Gastroenterologist', 33, '9807653421', 'static/Doctors_Photo\\Sanjay_dey_Bakshi.webp', '2025-05-22 16:29:35'),
(24, 'Dr. Pritha Nayyar', 'Pulmonologist', 9, '8320176583', 'static/Doctors_Photo\\a_13.jpg', '2025-05-22 16:30:53'),
(25, 'Dr. Nevin Kishore', 'Pulmonologist', 20, '7789045623', 'static/Doctors_Photo\\Dr_Nevin_Kishore_0_c780fd6914.jpeg', '2025-05-22 16:31:50'),
(26, 'Dr Rakesh Bilagi', 'Pulmonologist', 6, '7890345621', 'static/Doctors_Photo\\a_20.jpg', '2025-05-22 16:34:46'),
(27, 'Dr. Aabha Nagra', 'Hepatologist', 15, '8907541278', 'static/Doctors_Photo\\a_18.jpg', '2025-05-22 16:36:55'),
(28, 'Dr. Sitha Siramolpiwat', 'Hepatologist', 12, '8907423671', 'static/Doctors_Photo\\a_16.jpg', '2025-05-22 16:38:01'),
(29, 'Dr. Gaurav Gupta', 'Hepatologist', 9, '6789034512', 'static/Doctors_Photo\\a_12.jpg', '2025-05-22 16:38:45'),
(30, 'Dr. Sujoy Saha', 'Gastroenterologist', 12, '7745091208', 'static/Doctors_Photo\\a_24.jpeg', '2025-05-23 15:35:25'),
(31, 'Dr. Saubhika Ghosh', 'Hepatologist', 9, '7589032415', 'static/Doctors_Photo\\a_17.jpg', '2025-05-23 15:37:18'),
(32, 'Dr. Arup Ratan Dutta', 'Nephrologist', 18, '8904367812', 'static/Doctors_Photo\\a_25.jpg', '2025-05-23 15:39:05'),
(33, 'Dr. Akshit Gupta', 'Pulmonologist', 15, '8023451709', 'static/Doctors_Photo\\a_14.jpg', '2025-05-23 15:40:45'),
(34, 'Dr. Archita Bandyopadhyay', 'Infectious Disease Specialist', 7, '6790345271', 'static/Doctors_Photo\\a_7.jpg', '2025-05-23 15:42:37'),
(35, 'Dr. Khairul Basar', 'Infectious Disease Specialist', 20, '7789403218', 'static/Doctors_Photo\\a_26.jpg', '2025-05-23 15:46:36'),
(37, 'Dr. Neha Gupta', 'Infectious Disease Specialist', 10, '7768905412', 'static/Doctors_Photo\\dr-neha-gupta-2987.png', '2025-05-23 15:51:47'),
(38, 'Dr. Subhashree Samantaray', 'Infectious Disease Specialist', 14, '7590432709', 'static/Doctors_Photo\\a_27.jpeg', '2025-05-23 15:54:20');

-- --------------------------------------------------------

--
-- Table structure for table `health_reports`
--

CREATE TABLE `health_reports` (
  `id` int(11) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `height` float DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `category` enum('BMI','BMR') DEFAULT NULL,
  `result_value` float DEFAULT NULL,
  `pdf_path` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `health_reports`
--

INSERT INTO `health_reports` (`id`, `username`, `height`, `weight`, `category`, `result_value`, `pdf_path`, `created_at`) VALUES
(1, 'Sumanta ', 125, 180, 'BMR', 2476.25, 'static/pdfs\\Sumanta__BMR_20250603123129.pdf', '2025-06-03 12:31:29');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `gender` enum('Male','Female','Other') NOT NULL,
  `password` varchar(255) NOT NULL,
  `profile_pic` varchar(255) DEFAULT 'default.png',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(20) DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `phone`, `gender`, `password`, `profile_pic`, `created_at`, `status`) VALUES
(1, 'Indrajit Mondal', 'indra@gmail.com', '7685844606', 'Male', 'scrypt:32768:8:1$ij5qp34SQhpKPnKt$6ce83cb8e506cf6ce5b0702cbd29bfa48c0a4024f530924e00373366fd6fc410b6d2c171331fc4d9e94b9a7ad6879518cce7fda305ee1993968870f9374c433b', 'Indrajit_Mondal.jpg', '2025-03-27 13:11:59', 'active'),
(2, 'Sumanta ', 'spaul938286@gmail.com', '9382868676', 'Male', 'scrypt:32768:8:1$VXBKTvGyZSBIj1k0$3c07828c0a46da4ed4f39fa5adf1a2c6928dee5a93504deb052ba749c65d31ddebd765b0c234ab3aca2fd11757c021e4b3990c1187442e86485c094adddbee9b', 'default.png', '2025-04-05 18:50:26', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `user_activity`
--

CREATE TABLE `user_activity` (
  `id` int(11) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `disease_name` varchar(100) DEFAULT NULL,
  `prediction_result` text DEFAULT NULL,
  `pdf_report` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_activity`
--

INSERT INTO `user_activity` (`id`, `username`, `disease_name`, `prediction_result`, `pdf_report`, `created_at`) VALUES
(5, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250505130020.pdf', '2025-05-05 07:30:20'),
(6, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250505130146.pdf', '2025-05-05 07:31:47'),
(7, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250505130309.pdf', '2025-05-05 07:33:09'),
(8, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250505130310.pdf', '2025-05-05 07:33:10'),
(9, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250505131306.pdf', '2025-05-05 07:43:06'),
(10, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250510222652.pdf', '2025-05-10 16:56:52'),
(11, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250512225423.pdf', '2025-05-12 17:24:23'),
(12, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250512232014.pdf', '2025-05-12 17:50:14'),
(13, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250512232201.pdf', '2025-05-12 17:52:01'),
(14, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250512232202.pdf', '2025-05-12 17:52:02'),
(15, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250512232246.pdf', '2025-05-12 17:52:46'),
(16, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250512232247.pdf', '2025-05-12 17:52:47'),
(17, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250512232250.pdf', '2025-05-12 17:52:50'),
(18, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513115303.pdf', '2025-05-13 06:23:03'),
(19, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513115738.pdf', '2025-05-13 06:27:38'),
(20, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513135207.pdf', '2025-05-13 08:22:07'),
(21, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513140625.pdf', '2025-05-13 08:36:25'),
(22, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513140948.pdf', '2025-05-13 08:39:48'),
(23, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513140948.pdf', '2025-05-13 08:39:48'),
(24, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513140948.pdf', '2025-05-13 08:39:48'),
(25, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513140951.pdf', '2025-05-13 08:39:51'),
(26, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513141104.pdf', '2025-05-13 08:41:04'),
(27, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513141602.pdf', '2025-05-13 08:46:02'),
(28, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513141740.pdf', '2025-05-13 08:47:41'),
(29, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513142503.pdf', '2025-05-13 08:55:03'),
(30, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513170238.pdf', '2025-05-13 11:32:38'),
(31, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513171916.pdf', '2025-05-13 11:49:16'),
(32, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513172007.pdf', '2025-05-13 11:50:07'),
(33, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513172343.pdf', '2025-05-13 11:53:43'),
(34, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513173123.pdf', '2025-05-13 12:01:23'),
(35, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513173200.pdf', '2025-05-13 12:02:00'),
(36, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513173248.pdf', '2025-05-13 12:02:48'),
(37, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513173335.pdf', '2025-05-13 12:03:35'),
(38, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513173412.pdf', '2025-05-13 12:04:12'),
(39, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250513194926.pdf', '2025-05-13 14:19:26'),
(40, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513212918.pdf', '2025-05-13 15:59:18'),
(41, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250513213658.pdf', '2025-05-13 16:06:58'),
(42, 'Sumanta ', 'Parkinson', 'Parkinson\'s Detected', 'static/reports\\Sumanta _parkinson_report_20250515122203.pdf', '2025-05-15 06:52:03'),
(43, 'Sumanta ', 'Parkinson', 'Parkinson\'s Detected', 'static/reports\\Sumanta _parkinson_report_20250515122347.pdf', '2025-05-15 06:53:47'),
(44, 'Sumanta ', 'Parkinson', 'Parkinson\'s Detected', 'static/reports\\Sumanta _parkinson_report_20250515122613.pdf', '2025-05-15 06:56:13'),
(45, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250517212747.pdf', '2025-05-17 15:57:47'),
(46, 'Sumanta ', 'Kidney', 'The prediction indicates a positive case of chronic kidney disease.', 'static/reports\\Sumanta _kidney_report_20250517212838.pdf', '2025-05-17 15:58:38'),
(47, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Glioma', 'static/reports\\Sumanta _brain_tumor_report_20250603122919.pdf', '2025-06-03 06:59:19'),
(48, 'Sumanta ', 'Diabetes', 'Diabetes Detected (Positive)', 'static/reports\\Sumanta _diabetes_report_20250607230534.pdf', '2025-06-07 17:35:34'),
(49, 'Sumanta ', 'Heart Disease', 'No Heart Disease (Negative)', 'static/reports\\Sumanta _heart_disease_report_20250608161815.pdf', '2025-06-08 10:48:15'),
(50, 'Sumanta ', 'fatty_Liver', 'The prediction indicates a Severe illness.', 'static/reports\\Sumanta _fatty_liver_report_20250608162007.pdf', '2025-06-08 10:50:07'),
(51, 'Sumanta ', 'Kidney', 'The prediction indicates a positive case of chronic kidney disease.', 'static/reports\\Sumanta _kidney_report_20250608162226.pdf', '2025-06-08 10:52:26'),
(52, 'Sumanta ', 'Parkinson', 'Error: could not convert string to float: \'\'', 'static/reports\\Sumanta _parkinson_report_20250608162328.pdf', '2025-06-08 10:53:28'),
(53, 'Sumanta ', 'Parkinson', 'Error: could not convert string to float: \'\'', 'static/reports\\Sumanta _parkinson_report_20250608162328.pdf', '2025-06-08 10:53:28'),
(54, 'Sumanta ', 'Parkinson', 'Error: X has 8 features, but RandomForestClassifier is expecting 132 features as input.', 'static/reports\\Sumanta _parkinson_report_20250608162337.pdf', '2025-06-08 10:53:37'),
(55, 'Sumanta ', 'Parkinson', 'Error: X has 8 features, but RandomForestClassifier is expecting 132 features as input.', 'static/reports\\Sumanta _parkinson_report_20250608162402.pdf', '2025-06-08 10:54:02'),
(56, 'Sumanta ', 'Parkinson', 'Error: X has 8 features, but RandomForestClassifier is expecting 132 features as input.', 'static/reports\\Sumanta _parkinson_report_20250608162403.pdf', '2025-06-08 10:54:03'),
(57, 'Sumanta ', 'Parkinson', 'Error: X has 8 features, but RandomForestClassifier is expecting 132 features as input.', 'static/reports\\Sumanta _parkinson_report_20250608162409.pdf', '2025-06-08 10:54:09'),
(58, 'Sumanta ', 'Parkinson', 'Error: X has 8 features, but RandomForestClassifier is expecting 132 features as input.', 'static/reports\\Sumanta _parkinson_report_20250608162414.pdf', '2025-06-08 10:54:14'),
(59, 'Sumanta ', 'Parkinson', 'Error: X has 8 features, but RandomForestClassifier is expecting 132 features as input.', 'static/reports\\Sumanta _parkinson_report_20250608162424.pdf', '2025-06-08 10:54:24'),
(60, 'Sumanta ', 'Parkinson', 'Error: X has 8 features, but RandomForestClassifier is expecting 132 features as input.', 'static/reports\\Sumanta _parkinson_report_20250608162429.pdf', '2025-06-08 10:54:29'),
(61, 'Sumanta ', 'Parkinson', 'Error: X has 8 features, but RandomForestClassifier is expecting 132 features as input.', 'static/reports\\Sumanta _parkinson_report_20250608162440.pdf', '2025-06-08 10:54:40'),
(62, 'Sumanta ', 'Liver', 'The prediction indicates a positive case of liver disease.', 'static/reports\\Sumanta _liver_report_20250608162630.pdf', '2025-06-08 10:56:30'),
(63, 'Sumanta ', 'Breast Cancer', 'The Breast Cancer is Benign', 'static/reports\\Sumanta _breast_cancer_report_20250608163509.pdf', '2025-06-08 11:05:09'),
(64, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Glioma', 'static/reports\\Sumanta _brain_tumor_report_20250608164018.pdf', '2025-06-08 11:10:18'),
(65, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Glioma', 'static/reports\\Sumanta _brain_tumor_report_20250608164413.pdf', '2025-06-08 11:14:13'),
(66, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Glioma', 'static/reports\\Sumanta _brain_tumor_report_20250608164537.pdf', '2025-06-08 11:15:37'),
(67, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Glioma', 'static/reports\\Sumanta _brain_tumor_report_20250608164605.pdf', '2025-06-08 11:16:05'),
(68, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Glioma', 'static/reports\\Sumanta _brain_tumor_report_20250608165016.pdf', '2025-06-08 11:20:16'),
(69, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Pituitary', 'static/reports\\Sumanta _brain_tumor_report_20250608165812.pdf', '2025-06-08 11:28:12'),
(70, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Pituitary', 'static/reports\\Sumanta _brain_tumor_report_20250608165835.pdf', '2025-06-08 11:28:35'),
(71, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Pituitary', 'static/reports\\Sumanta _brain_tumor_report_20250608165854.pdf', '2025-06-08 11:28:54'),
(72, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Pituitary', 'static/reports\\Sumanta _brain_tumor_report_20250608165918.pdf', '2025-06-08 11:29:18'),
(73, 'Sumanta ', 'Brain Tumor', 'No Tumor Detected', 'static/reports\\Sumanta _brain_tumor_report_20250608170205.pdf', '2025-06-08 11:32:05'),
(74, 'Sumanta ', 'Brain Tumor', 'No Tumor Detected', 'static/reports\\Sumanta _brain_tumor_report_20250608170401.pdf', '2025-06-08 11:34:01'),
(75, 'Sumanta ', 'Brain Tumor', 'No Tumor Detected', 'static/reports\\Sumanta _brain_tumor_report_20250608170558.pdf', '2025-06-08 11:35:58'),
(76, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Meningioma', 'static/reports\\Sumanta _brain_tumor_report_20250608170606.pdf', '2025-06-08 11:36:06'),
(77, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Meningioma', 'static/reports\\Sumanta _brain_tumor_report_20250608170654.pdf', '2025-06-08 11:36:54'),
(78, 'Sumanta ', 'Kidney', 'The prediction indicates a positive case of chronic kidney disease.', 'static/reports\\Sumanta _kidney_report_20250608173614.pdf', '2025-06-08 12:06:14'),
(79, 'Sumanta ', 'Kidney', 'The prediction indicates a positive case of chronic kidney disease.', 'static/reports\\Sumanta _kidney_report_20250608173918.pdf', '2025-06-08 12:09:18'),
(80, 'Sumanta ', 'Kidney', 'The prediction indicates a positive case of chronic kidney disease.', 'static/reports\\Sumanta _kidney_report_20250608173922.pdf', '2025-06-08 12:09:22'),
(81, 'Sumanta ', 'Kidney', 'The prediction indicates a positive case of chronic kidney disease.', 'static/reports\\Sumanta _kidney_report_20250608173925.pdf', '2025-06-08 12:09:25'),
(82, 'Sumanta ', 'Kidney', 'You are predicted safe from Chronic Kidney disease (Negative)', 'static/reports\\Sumanta _kidney_report_20250608173933.pdf', '2025-06-08 12:09:33'),
(83, 'Sumanta ', 'Heart Disease', 'Heart Disease Detected (Positive)', 'static/reports\\Sumanta _heart_disease_report_20250608174022.pdf', '2025-06-08 12:10:22'),
(84, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Meningioma', 'static/reports\\Sumanta _brain_tumor_report_20250608174346.pdf', '2025-06-08 12:13:46'),
(85, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Meningioma', 'static/reports\\Sumanta _brain_tumor_report_20250608174440.pdf', '2025-06-08 12:14:40'),
(86, 'Sumanta ', 'Kidney', 'The prediction indicates a positive case of chronic kidney disease.', 'static/reports\\Sumanta _kidney_report_20250608174855.pdf', '2025-06-08 12:18:55'),
(87, 'Sumanta ', 'Kidney', 'The prediction indicates a positive case of chronic kidney disease.', 'static/reports\\Sumanta _kidney_report_20250608175244.pdf', '2025-06-08 12:22:44'),
(88, 'Sumanta ', 'Brain Tumor', 'Tumor Detected: Glioma', 'static/reports\\Sumanta _brain_tumor_report_20250612105020.pdf', '2025-06-12 05:20:20'),
(89, 'Sumanta ', 'Liver', 'The prediction indicates a positive case of liver disease.', 'static/reports\\Sumanta _liver_report_20250612165000.pdf', '2025-06-12 11:20:00');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `doctors`
--
ALTER TABLE `doctors`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `health_reports`
--
ALTER TABLE `health_reports`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `user_activity`
--
ALTER TABLE `user_activity`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `doctors`
--
ALTER TABLE `doctors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `health_reports`
--
ALTER TABLE `health_reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user_activity`
--
ALTER TABLE `user_activity`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=90;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
