-- MySQL dump 10.13  Distrib 5.7.19, for Linux (x86_64)
--
-- Host: localhost    Database: dreamteam
-- ------------------------------------------------------
-- Server version	5.7.19-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `dreamteam`
--

/*!40000 DROP DATABASE IF EXISTS `dreamteam`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `dreamteam` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `dreamteam`;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('f775a2b938a4');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendance` (
  `id` int(11) NOT NULL,
  `student` varchar(45) NOT NULL,
  `class_` int(11) NOT NULL,
  `verified` int(11) DEFAULT NULL,
  `uploaded_photo` varchar(100) NOT NULL,
  `course` varchar(80) DEFAULT NULL,
  `time_started` datetime NOT NULL,
  PRIMARY KEY (`id`,`student`,`class_`,`uploaded_photo`),
  KEY `class_` (`class_`),
  KEY `student` (`student`),
  KEY `uploaded_photo` (`uploaded_photo`),
  KEY `ix_attendance_verified` (`verified`),
  KEY `ix_attendance_time_started` (`time_started`),
  KEY `course` (`course`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`class_`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`student`) REFERENCES `students` (`reg_num`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `attendance_ibfk_3` FOREIGN KEY (`uploaded_photo`) REFERENCES `photos` (`address`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `attendance_ibfk_4` FOREIGN KEY (`verified`) REFERENCES `verification_statuses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `attendance_ibfk_5` FOREIGN KEY (`course`) REFERENCES `courses` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time_started` datetime NOT NULL,
  `duration` float NOT NULL,
  `archived` tinyint(1) NOT NULL,
  `lec_course_id` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_classes_lec_course_id` (`lec_course_id`),
  KEY `ix_classes_time_started` (`time_started`),
  CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`lec_course_id`) REFERENCES `lecturers_teaching` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classes`
--

LOCK TABLES `classes` WRITE;
/*!40000 ALTER TABLE `classes` DISABLE KEYS */;
/*!40000 ALTER TABLE `classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `programme_id` varchar(8) NOT NULL,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_courses_programme_id` (`programme_id`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`programme_id`) REFERENCES `programmes` (`program_id`)
) ENGINE=InnoDB AUTO_INCREMENT=593 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (101,'F17','Physics A'),(102,'F17','Physics B'),(111,'F17','Applied Mathematics A'),(112,'F17','Applied Mathematics B'),(121,'F17','Pure Mathematics A'),(122,'F17','Pure Mathematics B'),(131,'F17','Computer Science I'),(132,'F17','Computer Science II'),(141,'F17','Communication Skills'),(142,'F17','Electrical Measurements'),(151,'F17','Elements Of Philosophy'),(152,'F17','The Development Process'),(161,'F17','Mechanical Workshop Technology'),(162,'F17','Electrical Workshop Technology'),(201,'F17','Physical Electronics A'),(202,'F17','Physical Electronic B'),(221,'F17','Electric Circuit Theory I  A'),(222,'F17','Electric Circuit Theory I B'),(231,'F17','Computer Science III'),(232,'F17','Computer Science IV'),(241,'F17','Engineering Drawing A'),(242,'F17','Engineering Drawing B'),(251,'F17','Thermodynamics For Electrical Engineers'),(252,'F17','Fluid Mechanics For Electrical Engineers'),(261,'F17','Mechanics Of Machines And Strengths Of Materials A'),(262,'F17','Mechanics Of Machines And Strengths Of Materials B'),(271,'F17','Mathematics II A'),(272,'F17','Mathematics II B'),(281,'F17','Laboratory II A'),(282,'F17','Laboratory II B'),(301,'F17','Analogue Electronic A'),(302,'F17','Analogue Electronics B'),(321,'F17','Electrical Circuit Theory II A'),(322,'F17','Electrical Circuit Theory II B'),(331,'F17','Digital Electronics A'),(332,'F17','Digital Electronics B'),(341,'F17','Electrical Machines I A'),(342,'F17','Electrical Machines I B'),(351,'F17','Electromagnetic Fields A'),(352,'F17','Electromagnetic Fields B'),(362,'F17','Instrumentation'),(371,'F17','Mathematics III A'),(372,'F17','Mathematics III B'),(381,'F17','Laboratory III A'),(382,'F17','Laboratory III B'),(401,'F17','Electronics A'),(402,'F17','Electronics B'),(411,'F17','Control Systems A'),(412,'F17','Control System B'),(421,'F17','Telecommunications And Electroacoustics A'),(422,'F17','Telecommunications And Electroacoustics B'),(431,'F17','Electrical Power Systems I A'),(432,'F17','Electrical Power Systems I B'),(441,'F17','Electrical Machines II A'),(442,'F17','Electrical Machines Iib'),(451,'F17','Electrodynamics And Insulating Materials A'),(452,'F17','Electrodynamics And Insulating Materials B'),(471,'F17','Statistics'),(472,'F17','Numerical Methods'),(481,'F17','Laboratory IV A'),(482,'F17','Laboratory IV B'),(501,'F17','Applied Electronics A'),(502,'F17','Applied Electronics B'),(511,'F17','Control Engineering A'),(512,'F17','Control Engineering B'),(521,'F17','Telecommunications A'),(522,'F17','Telecommunications B'),(531,'F17','Electrical Power Systems II A'),(532,'F17','Electrical Power Systems II B'),(541,'F17','Power Electronics & Variable Machine Drives A'),(542,'F17','Power Electronics & Variable Machine Drives B'),(551,'F17','Microwaves And Antennas A'),(552,'F17','Microwaves And Antennas B'),(560,'F17','Engineering Project'),(571,'F17','Mathematical Methods'),(582,'F17','Management For Engineers'),(591,'F17','Laboratory V A'),(592,'F17','Laboratory V B');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `days_of_the_week`
--

DROP TABLE IF EXISTS `days_of_the_week`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `days_of_the_week` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `days_of_the_week`
--

LOCK TABLES `days_of_the_week` WRITE;
/*!40000 ALTER TABLE `days_of_the_week` DISABLE KEYS */;
INSERT INTO `days_of_the_week` VALUES (6,'Friday'),(2,'Monday'),(7,'Saturday'),(1,'Sunday'),(5,'Thursday'),(3,'Tuesday'),(4,'Wednesday');
/*!40000 ALTER TABLE `days_of_the_week` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `extras`
--

DROP TABLE IF EXISTS `extras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `extras` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` varchar(120) DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `LAC` float DEFAULT NULL,
  `CID` float DEFAULT NULL,
  `altitude` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `extras`
--

LOCK TABLES `extras` WRITE;
/*!40000 ALTER TABLE `extras` DISABLE KEYS */;
/*!40000 ALTER TABLE `extras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecturers`
--

DROP TABLE IF EXISTS `lecturers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lecturers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `staff_id` varchar(15) NOT NULL,
  `name` varchar(45) NOT NULL,
  `email` varchar(120) NOT NULL,
  `rank` varchar(25) DEFAULT NULL,
  `programme` varchar(80) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `is_lecturer` tinyint(1) DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `staff_id` (`staff_id`),
  KEY `programme` (`programme`),
  KEY `user` (`user`),
  CONSTRAINT `lecturers_ibfk_1` FOREIGN KEY (`programme`) REFERENCES `programmes` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `lecturers_ibfk_2` FOREIGN KEY (`user`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecturers`
--

LOCK TABLES `lecturers` WRITE;
/*!40000 ALTER TABLE `lecturers` DISABLE KEYS */;
/*!40000 ALTER TABLE `lecturers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecturers_teaching`
--

DROP TABLE IF EXISTS `lecturers_teaching`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lecturers_teaching` (
  `id` int(11) NOT NULL,
  `lecturers_id` int(11) NOT NULL,
  `courses_id` int(11) NOT NULL,
  `programme` varchar(8) NOT NULL,
  PRIMARY KEY (`id`,`lecturers_id`,`courses_id`),
  KEY `ix_lecturers_teaching_courses_id` (`courses_id`),
  KEY `ix_lecturers_teaching_lecturers_id` (`lecturers_id`),
  KEY `programme` (`programme`),
  CONSTRAINT `lecturers_teaching_ibfk_1` FOREIGN KEY (`courses_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `lecturers_teaching_ibfk_2` FOREIGN KEY (`lecturers_id`) REFERENCES `lecturers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `lecturers_teaching_ibfk_3` FOREIGN KEY (`programme`) REFERENCES `programmes` (`program_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecturers_teaching`
--

LOCK TABLES `lecturers_teaching` WRITE;
/*!40000 ALTER TABLE `lecturers_teaching` DISABLE KEYS */;
/*!40000 ALTER TABLE `lecturers_teaching` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photos`
--

DROP TABLE IF EXISTS `photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` varchar(45) NOT NULL,
  `address` varchar(100) NOT NULL,
  `learning` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address` (`address`),
  KEY `ix_photos_student_id` (`student_id`),
  CONSTRAINT `photos_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`reg_num`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos`
--

LOCK TABLES `photos` WRITE;
/*!40000 ALTER TABLE `photos` DISABLE KEYS */;
/*!40000 ALTER TABLE `photos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `programmes`
--

DROP TABLE IF EXISTS `programmes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `programmes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `program_id` varchar(8) NOT NULL,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `program_id` (`program_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `programmes`
--

LOCK TABLES `programmes` WRITE;
/*!40000 ALTER TABLE `programmes` DISABLE KEYS */;
INSERT INTO `programmes` VALUES (1,'F17','B.sc. (Electrical And Electronic Engineering)');
/*!40000 ALTER TABLE `programmes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_courses`
--

DROP TABLE IF EXISTS `student_courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_courses` (
  `id` int(11) NOT NULL,
  `student_id` varchar(45) NOT NULL,
  `courses_id` int(11) NOT NULL,
  `programme` varchar(8) NOT NULL,
  PRIMARY KEY (`id`,`student_id`,`courses_id`),
  KEY `ix_student_courses_courses_id` (`courses_id`),
  KEY `ix_student_courses_student_id` (`student_id`),
  KEY `programme` (`programme`),
  CONSTRAINT `student_courses_ibfk_1` FOREIGN KEY (`courses_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `student_courses_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`reg_num`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `student_courses_ibfk_3` FOREIGN KEY (`programme`) REFERENCES `programmes` (`program_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_courses`
--

LOCK TABLES `student_courses` WRITE;
/*!40000 ALTER TABLE `student_courses` DISABLE KEYS */;
/*!40000 ALTER TABLE `student_courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `students` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reg_num` varchar(45) DEFAULT NULL,
  `name` varchar(60) NOT NULL,
  `year_of_study` int(11) NOT NULL,
  `programme` varchar(80) NOT NULL,
  `class_rep` tinyint(1) NOT NULL,
  `is_student` tinyint(1) DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  `email` varchar(120) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `ix_students_reg_num` (`reg_num`),
  KEY `ix_students_class_rep` (`class_rep`),
  KEY `ix_students_name` (`name`),
  KEY `ix_students_year_of_study` (`year_of_study`),
  KEY `students_ibfk_1` (`programme`),
  KEY `user` (`user`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`programme`) REFERENCES `programmes` (`name`),
  CONSTRAINT `students_ibfk_2` FOREIGN KEY (`user`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suggestions`
--

DROP TABLE IF EXISTS `suggestions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `suggestions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(20) NOT NULL,
  `message` varchar(2000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suggestions`
--

LOCK TABLES `suggestions` WRITE;
/*!40000 ALTER TABLE `suggestions` DISABLE KEYS */;
/*!40000 ALTER TABLE `suggestions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `verification_statuses`
--

DROP TABLE IF EXISTS `verification_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `verification_statuses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(40) NOT NULL,
  `error_message` varchar(140) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `verification_statuses`
--

LOCK TABLES `verification_statuses` WRITE;
/*!40000 ALTER TABLE `verification_statuses` DISABLE KEYS */;
/*!40000 ALTER TABLE `verification_statuses` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-10-19  1:25:18
