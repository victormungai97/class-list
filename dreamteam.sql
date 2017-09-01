-- phpMyAdmin SQL Dump
-- version 4.6.5.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 01, 2017 at 02:11 PM
-- Server version: 10.1.21-MariaDB
-- PHP Version: 5.6.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dreamteam`
--

DROP DATABASE IF EXISTS `dreamteam`;
CREATE DATABASE IF NOT EXISTS `dreamteam` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `dreamteam`;
-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('587a02a3d968');

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `id` int(11) NOT NULL,
  `student` varchar(45) NOT NULL,
  `class_` int(11) NOT NULL,
  `verified` int(11) NOT NULL,
  `uploaded_photo` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `classes`
--

CREATE TABLE `classes` (
  `id` int(11) NOT NULL,
  `time_started` datetime NOT NULL,
  `duration` float NOT NULL,
  `archived` tinyint(1) NOT NULL,
  `lec_course_id` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `id` int(11) NOT NULL,
  `programme_id` varchar(8) NOT NULL,
  `name` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`id`, `programme_id`, `name`) VALUES
(101, 'F17', 'Physics A'),
(102, 'F17', 'Physics B'),
(111, 'F17', 'Applied Mathematics A'),
(112, 'F17', 'Applied Mathematics B'),
(121, 'F17', 'Pure Mathematics A'),
(122, 'F17', 'Pure Mathematics B'),
(131, 'F17', 'Computer Science I'),
(132, 'F17', 'Computer Science II'),
(141, 'F17', 'Communication Skills'),
(142, 'F17', 'Electrical Measurements'),
(151, 'F17', 'Elements Of Philosophy'),
(152, 'F17', 'The Development Process'),
(161, 'F17', 'Mechanical Workshop Technology'),
(162, 'F17', 'Electrical Workshop Technology'),
(201, 'F17', 'Physical Electronics A'),
(202, 'F17', 'Physical Electronic B'),
(221, 'F17', 'Electric Circuit Theory I  A'),
(222, 'F17', 'Electric Circuit Theory I B'),
(231, 'F17', 'Computer Science III'),
(232, 'F17', 'Computer Science IV'),
(241, 'F17', 'Engineering Drawing A'),
(242, 'F17', 'Engineering Drawing B'),
(251, 'F17', 'Thermodynamics For Electrical Engineers'),
(252, 'F17', 'Fluid Mechanics For Electrical Engineers'),
(261, 'F17', 'Mechanics Of Machines And Strengths Of Materi'),
(262, 'F17', 'Mechanics Of Machines And Strenghts Of Materi'),
(271, 'F17', 'Mathematics II A'),
(272, 'F17', 'Mathematics II B'),
(281, 'F17', 'Laboratory II A'),
(282, 'F17', 'Laboratory II B'),
(301, 'F17', 'Analogue Electronic A'),
(302, 'F17', 'Analogue Electronics B'),
(321, 'F17', 'Electrical Circuit Theory II A'),
(322, 'F17', 'Electrical Circuit Theory II B'),
(331, 'F17', 'Digital Electronics A'),
(332, 'F17', 'Digital Electronics B'),
(341, 'F17', 'Electrical Machines I A'),
(342, 'F17', 'Electrical Machines I B'),
(351, 'F17', 'Electromagnetic Fields A'),
(352, 'F17', 'Electromagnetic Fields B'),
(362, 'F17', 'Instrumentation'),
(371, 'F17', 'Mathematics III A'),
(372, 'F17', 'Mathematics III B'),
(381, 'F17', 'Laboratory III A'),
(382, 'F17', 'Laboratory III B'),
(401, 'F17', 'Electronics A'),
(402, 'F17', 'Electronics B'),
(411, 'F17', 'Control Systems A'),
(412, 'F17', 'Control System B'),
(421, 'F17', 'Telecommunications And Electroacoustics A'),
(422, 'F17', 'Telecommunications And Electroacoustics B'),
(431, 'F17', 'Electrical Power Systems I A'),
(432, 'F17', 'Electrical Power Systems I B'),
(441, 'F17', 'Electrical Machines II A'),
(442, 'F17', 'Electrical Machines Iib'),
(451, 'F17', 'Electrodynamics And Insulating Materials A'),
(452, 'F17', 'Electrodynamics And Insulating Materials B'),
(471, 'F17', 'Statistics'),
(472, 'F17', 'Numerical Methods'),
(481, 'F17', 'Laboratory IV A'),
(482, 'F17', 'Laboratory IV B'),
(501, 'F17', 'Applied Electronics A'),
(502, 'F17', 'Applied Electronics B'),
(511, 'F17', 'Control Engineering A'),
(512, 'F17', 'Control Engineering B'),
(521, 'F17', 'Telecommunications A'),
(522, 'F17', 'Telecommunications B'),
(531, 'F17', 'Electrical Power Systems II A'),
(532, 'F17', 'Electrical Power Systems II B'),
(541, 'F17', 'Power Electronics & Variable Machine Drives A'),
(542, 'F17', 'Power Electronics & Variable Machine Drives B'),
(551, 'F17', 'Microwaves And Antennas A'),
(552, 'F17', 'Microwaves And Antennas B'),
(560, 'F17', 'Engineering Project'),
(571, 'F17', 'Mathematical Methods'),
(582, 'F17', 'Management For Engineers'),
(591, 'F17', 'Laboratory V A'),
(592, 'F17', 'Laboratory V B');

-- --------------------------------------------------------

--
-- Table structure for table `days_of_the_week`
--

CREATE TABLE `days_of_the_week` (
  `id` int(11) NOT NULL,
  `name` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `days_of_the_week`
--

INSERT INTO `days_of_the_week` (`id`, `name`) VALUES
(6, 'Friday'),
(2, 'Monday'),
(7, 'Saturday'),
(1, 'Sunday'),
(5, 'Thursday'),
(3, 'Tuesday'),
(4, 'Wednesday');

-- --------------------------------------------------------

--
-- Table structure for table `lecturers`
--

CREATE TABLE `lecturers` (
  `id` int(11) NOT NULL,
  `staff_id` varchar(15) NOT NULL,
  `name` varchar(45) NOT NULL,
  `email` varchar(120) NOT NULL,
  `rank` varchar(25) DEFAULT NULL,
  `programme` varchar(60) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `is_lecturer` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `lecturers_teaching`
--

CREATE TABLE `lecturers_teaching` (
  `id` int(11) NOT NULL,
  `lecturers_id` int(11) NOT NULL,
  `courses_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `photos`
--

CREATE TABLE `photos` (
  `id` int(11) NOT NULL,
  `student_id` varchar(45) NOT NULL,
  `address` varchar(100) NOT NULL,
  `learning` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `programmes`
--

CREATE TABLE `programmes` (
  `id` int(11) NOT NULL,
  `program_id` varchar(8) NOT NULL,
  `name` varchar(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `programmes`
--

INSERT INTO `programmes` (`id`, `program_id`, `name`) VALUES
(1, 'F17', 'B.sc. (Electrical And Electronic Engineering)');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `reg_num` varchar(45) DEFAULT NULL,
  `name` varchar(60) NOT NULL,
  `year_of_study` int(11) NOT NULL,
  `programme` varchar(60) NOT NULL,
  `class_rep` tinyint(1) NOT NULL,
  `is_student` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `verification_statuses`
--

CREATE TABLE `verification_statuses` (
  `id` int(11) NOT NULL,
  `description` varchar(40) NOT NULL,
  `error_message` varchar(140) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`id`,`student`,`class_`,`uploaded_photo`),
  ADD KEY `class_` (`class_`),
  ADD KEY `student` (`student`),
  ADD KEY `uploaded_photo` (`uploaded_photo`),
  ADD KEY `ix_attendance_verified` (`verified`);

--
-- Indexes for table `classes`
--
ALTER TABLE `classes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_classes_lec_course_id` (`lec_course_id`),
  ADD KEY `ix_classes_time_started` (`time_started`);

--
-- Indexes for table `courses`
--
ALTER TABLE `courses`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `ix_courses_programme_id` (`programme_id`);

--
-- Indexes for table `days_of_the_week`
--
ALTER TABLE `days_of_the_week`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `lecturers`
--
ALTER TABLE `lecturers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `staff_id` (`staff_id`),
  ADD KEY `programme` (`programme`);

--
-- Indexes for table `lecturers_teaching`
--
ALTER TABLE `lecturers_teaching`
  ADD PRIMARY KEY (`id`,`lecturers_id`,`courses_id`),
  ADD KEY `ix_lecturers_teaching_courses_id` (`courses_id`),
  ADD KEY `ix_lecturers_teaching_lecturers_id` (`lecturers_id`);

--
-- Indexes for table `photos`
--
ALTER TABLE `photos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `address` (`address`),
  ADD KEY `ix_photos_student_id` (`student_id`);

--
-- Indexes for table `programmes`
--
ALTER TABLE `programmes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD UNIQUE KEY `program_id` (`program_id`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_students_reg_num` (`reg_num`),
  ADD KEY `ix_students_class_rep` (`class_rep`),
  ADD KEY `ix_students_name` (`name`),
  ADD KEY `ix_students_year_of_study` (`year_of_study`),
  ADD KEY `students_ibfk_1` (`programme`);

--
-- Indexes for table `verification_statuses`
--
ALTER TABLE `verification_statuses`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `classes`
--
ALTER TABLE `classes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `courses`
--
ALTER TABLE `courses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=593;
--
-- AUTO_INCREMENT for table `days_of_the_week`
--
ALTER TABLE `days_of_the_week`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
--
-- AUTO_INCREMENT for table `lecturers`
--
ALTER TABLE `lecturers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT for table `photos`
--
ALTER TABLE `photos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `programmes`
--
ALTER TABLE `programmes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT for table `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `verification_statuses`
--
ALTER TABLE `verification_statuses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`class_`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`student`) REFERENCES `students` (`reg_num`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `attendance_ibfk_3` FOREIGN KEY (`uploaded_photo`) REFERENCES `photos` (`address`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `attendance_ibfk_4` FOREIGN KEY (`verified`) REFERENCES `verification_statuses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `classes`
--
ALTER TABLE `classes`
  ADD CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`lec_course_id`) REFERENCES `lecturers_teaching` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `courses`
--
ALTER TABLE `courses`
  ADD CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`programme_id`) REFERENCES `programmes` (`program_id`);

--
-- Constraints for table `lecturers`
--
ALTER TABLE `lecturers`
  ADD CONSTRAINT `lecturers_ibfk_1` FOREIGN KEY (`programme`) REFERENCES `programmes` (`name`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `lecturers_teaching`
--
ALTER TABLE `lecturers_teaching`
  ADD CONSTRAINT `lecturers_teaching_ibfk_1` FOREIGN KEY (`courses_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `lecturers_teaching_ibfk_2` FOREIGN KEY (`lecturers_id`) REFERENCES `lecturers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `photos`
--
ALTER TABLE `photos`
  ADD CONSTRAINT `photos_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`reg_num`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `students`
--
ALTER TABLE `students`
  ADD CONSTRAINT `students_ibfk_1` FOREIGN KEY (`programme`) REFERENCES `programmes` (`name`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
