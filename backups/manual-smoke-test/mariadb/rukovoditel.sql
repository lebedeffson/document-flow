/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.16-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: rukovoditel
-- ------------------------------------------------------
-- Server version	10.11.16-MariaDB-ubu2204

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `app_access_groups`
--

DROP TABLE IF EXISTS `app_access_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_access_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `is_default` tinyint(1) DEFAULT NULL,
  `is_ldap_default` tinyint(1) DEFAULT NULL,
  `ldap_filter` text NOT NULL,
  `sort_order` int(11) NOT NULL,
  `notes` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_access_groups`
--

LOCK TABLES `app_access_groups` WRITE;
/*!40000 ALTER TABLE `app_access_groups` DISABLE KEYS */;
INSERT INTO `app_access_groups` VALUES
(4,'Руководитель / преподаватель',1,0,'',2,''),
(5,'Исполнитель / сотрудник',0,0,'',1,''),
(6,'Заявитель / пользователь',0,0,'',0,'');
/*!40000 ALTER TABLE `app_access_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_access_rules`
--

DROP TABLE IF EXISTS `app_access_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_access_rules` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entities_id` int(10) unsigned NOT NULL,
  `fields_id` int(10) unsigned NOT NULL,
  `choices` text NOT NULL,
  `users_groups` text NOT NULL,
  `access_schema` text NOT NULL,
  `fields_view_only_access` text NOT NULL,
  `comments_access_schema` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_fields_id` (`fields_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_access_rules`
--

LOCK TABLES `app_access_rules` WRITE;
/*!40000 ALTER TABLE `app_access_rules` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_access_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_access_rules_fields`
--

DROP TABLE IF EXISTS `app_access_rules_fields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_access_rules_fields` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entities_id` int(10) unsigned NOT NULL,
  `fields_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_fields_id` (`fields_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_access_rules_fields`
--

LOCK TABLES `app_access_rules_fields` WRITE;
/*!40000 ALTER TABLE `app_access_rules_fields` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_access_rules_fields` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_approved_items`
--

DROP TABLE IF EXISTS `app_approved_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_approved_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `items_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `users_id` int(11) NOT NULL,
  `signature` longtext NOT NULL,
  `date_added` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_users_id` (`users_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_approved_items`
--

LOCK TABLES `app_approved_items` WRITE;
/*!40000 ALTER TABLE `app_approved_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_approved_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_attachments`
--

DROP TABLE IF EXISTS `app_attachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_attachments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `form_token` varchar(64) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `date_added` date NOT NULL,
  `container` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_attachments`
--

LOCK TABLES `app_attachments` WRITE;
/*!40000 ALTER TABLE `app_attachments` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_attachments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_backups`
--

DROP TABLE IF EXISTS `app_backups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_backups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `users_id` int(11) NOT NULL,
  `is_auto` tinyint(1) NOT NULL,
  `description` text NOT NULL,
  `filename` varchar(64) NOT NULL,
  `date_added` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_backups`
--

LOCK TABLES `app_backups` WRITE;
/*!40000 ALTER TABLE `app_backups` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_backups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_blocked_forms`
--

DROP TABLE IF EXISTS `app_blocked_forms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_blocked_forms` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entity_id` int(10) unsigned NOT NULL,
  `item_id` int(10) unsigned NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `date` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entity_id` (`entity_id`),
  KEY `idx_item_id` (`item_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_blocked_forms`
--

LOCK TABLES `app_blocked_forms` WRITE;
/*!40000 ALTER TABLE `app_blocked_forms` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_blocked_forms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_comments`
--

DROP TABLE IF EXISTS `app_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `items_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `description` text NOT NULL,
  `attachments` text NOT NULL,
  `date_added` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_entities_items` (`entities_id`,`items_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_comments`
--

LOCK TABLES `app_comments` WRITE;
/*!40000 ALTER TABLE `app_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_comments_access`
--

DROP TABLE IF EXISTS `app_comments_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_comments_access` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `access_groups_id` int(11) NOT NULL,
  `access_schema` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_access_groups_id` (`access_groups_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_comments_access`
--

LOCK TABLES `app_comments_access` WRITE;
/*!40000 ALTER TABLE `app_comments_access` DISABLE KEYS */;
INSERT INTO `app_comments_access` VALUES
(4,21,6,'view,create'),
(5,21,5,'view,create'),
(6,21,4,'view,create,update,delete'),
(7,22,5,'view,create'),
(8,22,4,'view,create,update,delete'),
(9,23,6,'view,create'),
(10,23,4,'view,create,update,delete'),
(11,24,5,'view,create'),
(12,24,4,'view,create,update,delete');
/*!40000 ALTER TABLE `app_comments_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_comments_forms_tabs`
--

DROP TABLE IF EXISTS `app_comments_forms_tabs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_comments_forms_tabs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_comments_forms_tabs`
--

LOCK TABLES `app_comments_forms_tabs` WRITE;
/*!40000 ALTER TABLE `app_comments_forms_tabs` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_comments_forms_tabs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_comments_history`
--

DROP TABLE IF EXISTS `app_comments_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_comments_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comments_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `fields_value` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_comments_id` (`comments_id`),
  KEY `idx_fields_id` (`fields_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_comments_history`
--

LOCK TABLES `app_comments_history` WRITE;
/*!40000 ALTER TABLE `app_comments_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_comments_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_composite_unique_fields`
--

DROP TABLE IF EXISTS `app_composite_unique_fields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_composite_unique_fields` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entities_id` int(10) unsigned NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_unique_for_parent` tinyint(1) NOT NULL,
  `field_1` int(10) unsigned NOT NULL,
  `field_2` int(10) unsigned NOT NULL,
  `message` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_composite_unique_fields`
--

LOCK TABLES `app_composite_unique_fields` WRITE;
/*!40000 ALTER TABLE `app_composite_unique_fields` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_composite_unique_fields` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_configuration`
--

DROP TABLE IF EXISTS `app_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_configuration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `configuration_name` varchar(255) NOT NULL,
  `configuration_value` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_configuration`
--

LOCK TABLES `app_configuration` WRITE;
/*!40000 ALTER TABLE `app_configuration` DISABLE KEYS */;
INSERT INTO `app_configuration` VALUES
(9,'CFG_APP_NAME','Rukovoditel + NauDoc Test'),
(10,'CFG_APP_SHORT_NAME','RN Test'),
(11,'CFG_APP_LOGO',''),
(12,'CFG_EMAIL_USE_NOTIFICATION','1'),
(13,'CFG_EMAIL_SUBJECT_LABEL',''),
(14,'CFG_EMAIL_AMOUNT_PREVIOUS_COMMENTS','2'),
(15,'CFG_EMAIL_COPY_SENDER','0'),
(16,'CFG_EMAIL_SEND_FROM_SINGLE','0'),
(17,'CFG_EMAIL_ADDRESS_FROM','noreply@example.local'),
(18,'CFG_EMAIL_NAME_FROM','NauBridge'),
(19,'CFG_EMAIL_USE_SMTP','0'),
(20,'CFG_EMAIL_SMTP_SERVER',''),
(21,'CFG_EMAIL_SMTP_PORT',''),
(22,'CFG_EMAIL_SMTP_ENCRYPTION',''),
(23,'CFG_EMAIL_SMTP_LOGIN',''),
(24,'CFG_EMAIL_SMTP_PASSWORD',''),
(25,'CFG_LDAP_USE','0'),
(26,'CFG_LDAP_SERVER_NAME',''),
(27,'CFG_LDAP_SERVER_PORT',''),
(28,'CFG_LDAP_BASE_DN',''),
(29,'CFG_LDAP_UID',''),
(30,'CFG_LDAP_USER',''),
(31,'CFG_LDAP_EMAIL_ATTRIBUTE',''),
(32,'CFG_LDAP_USER_DN',''),
(33,'CFG_LDAP_PASSWORD',''),
(34,'CFG_LOGIN_PAGE_HEADING',''),
(35,'CFG_LOGIN_PAGE_CONTENT',''),
(36,'CFG_APP_TIMEZONE','Europe/Moscow'),
(37,'CFG_APP_DATE_FORMAT','m/d/Y'),
(38,'CFG_APP_DATETIME_FORMAT','m/d/Y H:i'),
(39,'CFG_APP_ROWS_PER_PAGE','10'),
(40,'CFG_REGISTRATION_EMAIL_SUBJECT',''),
(41,'CFG_REGISTRATION_EMAIL_BODY',''),
(42,'CFG_PASSWORD_MIN_LENGTH','5'),
(43,'CFG_APP_LANGUAGE','russian.php'),
(44,'CFG_APP_SKIN','light'),
(45,'CFG_PUBLIC_USER_PROFILE_FIELDS',''),
(46,'CFG_CUSTOM_CSS_TIME','1774347288');
/*!40000 ALTER TABLE `app_configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_custom_php`
--

DROP TABLE IF EXISTS `app_custom_php`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_custom_php` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_folder` tinyint(1) NOT NULL,
  `name` varchar(255) NOT NULL,
  `code` longtext NOT NULL,
  `notes` text NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_custom_php`
--

LOCK TABLES `app_custom_php` WRITE;
/*!40000 ALTER TABLE `app_custom_php` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_custom_php` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_dashboard_pages`
--

DROP TABLE IF EXISTS `app_dashboard_pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_dashboard_pages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_by` int(11) NOT NULL,
  `sections_id` int(11) NOT NULL,
  `type` varchar(16) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `name` varchar(255) NOT NULL,
  `icon` varchar(64) NOT NULL,
  `description` text NOT NULL,
  `color` varchar(16) NOT NULL,
  `users_fields` text NOT NULL,
  `users_groups` text NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_sections_id` (`sections_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_dashboard_pages`
--

LOCK TABLES `app_dashboard_pages` WRITE;
/*!40000 ALTER TABLE `app_dashboard_pages` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_dashboard_pages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_dashboard_pages_sections`
--

DROP TABLE IF EXISTS `app_dashboard_pages_sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_dashboard_pages_sections` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `grid` tinyint(1) NOT NULL,
  `sort_order` smallint(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_dashboard_pages_sections`
--

LOCK TABLES `app_dashboard_pages_sections` WRITE;
/*!40000 ALTER TABLE `app_dashboard_pages_sections` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_dashboard_pages_sections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_emails_on_schedule`
--

DROP TABLE IF EXISTS `app_emails_on_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_emails_on_schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_added` bigint(20) unsigned NOT NULL,
  `email_to` varchar(255) NOT NULL,
  `email_to_name` varchar(255) NOT NULL,
  `email_subject` varchar(255) NOT NULL,
  `email_body` text NOT NULL,
  `email_from` varchar(255) NOT NULL,
  `email_from_name` varchar(255) NOT NULL,
  `email_attachments` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_emails_on_schedule`
--

LOCK TABLES `app_emails_on_schedule` WRITE;
/*!40000 ALTER TABLE `app_emails_on_schedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_emails_on_schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entities`
--

DROP TABLE IF EXISTS `app_entities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `notes` text NOT NULL,
  `display_in_menu` tinyint(1) DEFAULT 0,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_group_id` (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entities`
--

LOCK TABLES `app_entities` WRITE;
/*!40000 ALTER TABLE `app_entities` DISABLE KEYS */;
INSERT INTO `app_entities` VALUES
(1,0,0,'Пользователи','',0,10),
(21,0,1,'Проекты и инициативы','Учебные, методические, организационные и сервисные проекты.',1,10),
(22,21,1,'Поручения и задачи','Задачи и поручения внутри проектов и процессов.',1,11),
(23,0,1,'Заявки на обслуживание','Сервисные заявки от сотрудников и преподавателей.',1,20),
(24,21,1,'Рабочие обсуждения','Обсуждения и договоренности по проектам.',0,30),
(25,0,2,'Карточки документов','Операционный слой карточек документов с ссылками на NauDoc.',1,30),
(26,0,2,'База документов','База регламентов, шаблонов и материалов.',1,40),
(27,0,3,'Заявки на МТЗ','Заявки на материально-техническое обеспечение.',1,50);
/*!40000 ALTER TABLE `app_entities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entities_access`
--

DROP TABLE IF EXISTS `app_entities_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entities_access` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `access_groups_id` int(11) NOT NULL,
  `access_schema` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_access_groups_id` (`access_groups_id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entities_access`
--

LOCK TABLES `app_entities_access` WRITE;
/*!40000 ALTER TABLE `app_entities_access` DISABLE KEYS */;
INSERT INTO `app_entities_access` VALUES
(28,21,6,'view_assigned'),
(29,21,5,'view,create,update,reports'),
(30,21,4,'view,create,update,delete,reports'),
(31,22,6,'view_assigned,update'),
(32,22,5,'view,create,update,reports'),
(33,22,4,'view,create,update,delete,reports'),
(34,23,6,'view_assigned,create,update,reports'),
(35,23,5,'view,create,update,reports'),
(36,23,4,'view,create,update,delete,reports'),
(37,24,6,''),
(38,24,5,'view_assigned,create,update,delete,reports'),
(39,24,4,'view,create,update,delete,reports'),
(40,25,4,'view,create,update,delete,reports'),
(41,25,5,'view,create,update,reports'),
(42,25,6,'view_assigned,create'),
(43,26,4,'view,create,update,delete,reports'),
(44,26,5,'view,create,update,reports'),
(45,26,6,'view,reports'),
(46,27,4,'view,create,update,delete,reports'),
(47,27,5,'view,create,update,reports'),
(48,27,6,'create,view_assigned,update,reports');
/*!40000 ALTER TABLE `app_entities_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entities_configuration`
--

DROP TABLE IF EXISTS `app_entities_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entities_configuration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `configuration_name` varchar(255) NOT NULL,
  `configuration_value` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entities_configuration`
--

LOCK TABLES `app_entities_configuration` WRITE;
/*!40000 ALTER TABLE `app_entities_configuration` DISABLE KEYS */;
INSERT INTO `app_entities_configuration` VALUES
(11,1,'menu_title','Пользователи'),
(12,1,'listing_heading','Пользователи'),
(13,1,'window_heading','Информация о пользователе'),
(14,1,'insert_button','Добавить пользователя'),
(15,1,'use_comments','0'),
(25,21,'menu_title','Проекты и инициативы'),
(26,21,'listing_heading','Проекты и инициативы'),
(27,21,'window_heading','Карточка проекта'),
(28,21,'insert_button','Создать проект'),
(29,21,'email_subject_new_item','Новый проект:'),
(30,21,'use_comments','1'),
(31,21,'email_subject_new_comment','Новый комментарий к проекту:'),
(32,22,'menu_title','Поручения и задачи'),
(33,22,'listing_heading','Поручения и задачи'),
(34,22,'window_heading','Карточка задачи'),
(35,22,'insert_button','Добавить задачу'),
(36,22,'email_subject_new_item','Новая задача:'),
(37,22,'use_comments','1'),
(38,22,'email_subject_new_comment','Новый комментарий к задаче:'),
(39,23,'menu_title','Заявки на обслуживание'),
(40,23,'listing_heading','Заявки на обслуживание'),
(41,23,'window_heading','Карточка заявки'),
(42,23,'insert_button','Создать заявку'),
(43,23,'email_subject_new_item','Новая заявка:'),
(44,23,'use_comments','1'),
(45,23,'email_subject_new_comment','Новый комментарий к заявке:'),
(46,24,'menu_title','Рабочие обсуждения'),
(47,24,'listing_heading','Рабочие обсуждения'),
(48,24,'window_heading','Карточка обсуждения'),
(49,24,'insert_button','Добавить обсуждение'),
(50,24,'email_subject_new_item','Новое обсуждение:'),
(51,24,'use_comments','1'),
(52,24,'email_subject_new_comment','Новый комментарий к обсуждению:'),
(53,21,'use_editor_in_comments','0'),
(54,22,'use_editor_in_comments','0'),
(55,23,'use_editor_in_comments','0'),
(56,24,'use_editor_in_comments','0'),
(57,25,'menu_title','Карточки документов'),
(58,25,'listing_heading','Карточки документов'),
(59,25,'window_heading','Карточка документа'),
(60,25,'insert_button','Создать карточку документа'),
(61,25,'use_comments','1'),
(62,25,'email_subject_new_item','Новый документ:'),
(63,25,'email_subject_new_comment','Новый комментарий к документу:'),
(64,26,'menu_title','База документов'),
(65,26,'listing_heading','База документов'),
(66,26,'window_heading','Карточка документа базы'),
(67,26,'insert_button','Добавить документ'),
(68,26,'use_comments','1'),
(69,26,'email_subject_new_item','Новый материал базы документов:'),
(70,26,'email_subject_new_comment','Новый комментарий к документу базы:'),
(71,27,'menu_title','Заявки на МТЗ'),
(72,27,'listing_heading','Заявки на МТЗ'),
(73,27,'window_heading','Карточка заявки МТЗ'),
(74,27,'insert_button','Создать заявку МТЗ'),
(75,27,'use_comments','1'),
(76,27,'email_subject_new_item','Новая заявка на МТЗ:'),
(77,27,'email_subject_new_comment','Новый комментарий к заявке МТЗ:');
/*!40000 ALTER TABLE `app_entities_configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entities_groups`
--

DROP TABLE IF EXISTS `app_entities_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entities_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `sort_order` smallint(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entities_groups`
--

LOCK TABLES `app_entities_groups` WRITE;
/*!40000 ALTER TABLE `app_entities_groups` DISABLE KEYS */;
INSERT INTO `app_entities_groups` VALUES
(1,'Операционная работа',10),
(2,'Документы',20),
(3,'Обеспечение',30);
/*!40000 ALTER TABLE `app_entities_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entities_menu`
--

DROP TABLE IF EXISTS `app_entities_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entities_menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `icon` varchar(64) NOT NULL,
  `icon_color` varchar(7) NOT NULL,
  `bg_color` varchar(7) NOT NULL,
  `entities_list` text NOT NULL,
  `reports_list` text NOT NULL,
  `pages_list` text NOT NULL,
  `type` varchar(16) DEFAULT 'entity',
  `url` varchar(255) NOT NULL,
  `users_groups` text NOT NULL,
  `assigned_to` text NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entities_menu`
--

LOCK TABLES `app_entities_menu` WRITE;
/*!40000 ALTER TABLE `app_entities_menu` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entities_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_1`
--

DROP TABLE IF EXISTS `app_entity_1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `client_id` bigint(20) unsigned NOT NULL,
  `parent_id` int(11) NOT NULL DEFAULT 0,
  `parent_item_id` int(11) NOT NULL DEFAULT 0,
  `linked_id` int(11) NOT NULL DEFAULT 0,
  `date_added` bigint(20) NOT NULL DEFAULT 0,
  `date_updated` bigint(20) NOT NULL DEFAULT 0,
  `created_by` int(11) DEFAULT NULL,
  `sort_order` int(11) NOT NULL DEFAULT 0,
  `password` varchar(255) NOT NULL,
  `multiple_access_groups` varchar(64) NOT NULL,
  `is_email_verified` tinyint(1) NOT NULL DEFAULT 1,
  `field_5` tinyint(1) NOT NULL,
  `field_6` int(11) NOT NULL,
  `field_7` varchar(255) NOT NULL,
  `field_8` varchar(255) NOT NULL,
  `field_9` varchar(255) NOT NULL,
  `field_10` varchar(255) NOT NULL,
  `field_12` varchar(255) NOT NULL,
  `field_13` varchar(64) NOT NULL,
  `field_14` varchar(64) NOT NULL,
  `field_201` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_client_id` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_1`
--

LOCK TABLES `app_entity_1` WRITE;
/*!40000 ALTER TABLE `app_entity_1` DISABLE KEYS */;
INSERT INTO `app_entity_1` VALUES
(1,2986271,0,0,0,1774345972,0,NULL,0,'$P$EML8ArLkG/J2tOgXP/hY4y3Nno.mSY.','',1,1,0,'Admin','Bridge','admin@example.local','','admin','russian.php','blue',1774348420);
/*!40000 ALTER TABLE `app_entity_1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_1_values`
--

DROP TABLE IF EXISTS `app_entity_1_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_1_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `items_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `value` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_items_fields_id` (`items_id`,`fields_id`),
  KEY `idx_value_id` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_1_values`
--

LOCK TABLES `app_entity_1_values` WRITE;
/*!40000 ALTER TABLE `app_entity_1_values` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_1_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_21`
--

DROP TABLE IF EXISTS `app_entity_21`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_21` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT 0,
  `parent_item_id` int(11) DEFAULT 0,
  `linked_id` int(11) DEFAULT 0,
  `date_added` bigint(20) NOT NULL DEFAULT 0,
  `date_updated` bigint(20) NOT NULL DEFAULT 0,
  `created_by` int(11) DEFAULT NULL,
  `sort_order` int(11) DEFAULT 0,
  `field_156` text NOT NULL,
  `field_157` text NOT NULL,
  `field_158` text NOT NULL,
  `field_159` bigint(20) NOT NULL DEFAULT 0,
  `field_160` text NOT NULL,
  `field_161` text NOT NULL,
  `field_162` text NOT NULL,
  `field_225` text NOT NULL,
  `field_226` text NOT NULL,
  `field_227` int(11) NOT NULL,
  `field_228` bigint(11) NOT NULL,
  `field_229` int(11) NOT NULL,
  `field_230` varchar(255) NOT NULL,
  `field_231` text NOT NULL,
  `field_279` text NOT NULL,
  `field_280` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_field_225` (`field_225`(128)),
  KEY `idx_field_226` (`field_226`(128)),
  KEY `idx_field_227` (`field_227`),
  KEY `idx_field_228` (`field_228`),
  KEY `idx_field_229` (`field_229`),
  KEY `idx_field_279` (`field_279`(128)),
  KEY `idx_field_280` (`field_280`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_21`
--

LOCK TABLES `app_entity_21` WRITE;
/*!40000 ALTER TABLE `app_entity_21` DISABLE KEYS */;
INSERT INTO `app_entity_21` VALUES
(1,0,0,0,1774349478,1774349936,1,0,'461','465','Тестовый проект цифрового документооборота',1774299600,'<p>Автоматически созданный тестовый проект для проверки связки проект -> карточка документа -> middleware.</p>','1','','1','1',474,1776941478,25,'http://localhost:18080/docs','','2',528);
/*!40000 ALTER TABLE `app_entity_21` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_21_values`
--

DROP TABLE IF EXISTS `app_entity_21_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_21_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `items_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `value` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_items_fields_id` (`items_id`,`fields_id`),
  KEY `idx_value_id` (`value`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_21_values`
--

LOCK TABLES `app_entity_21_values` WRITE;
/*!40000 ALTER TABLE `app_entity_21_values` DISABLE KEYS */;
INSERT INTO `app_entity_21_values` VALUES
(1,1,156,461),
(2,1,157,465),
(3,1,161,1),
(4,1,225,1),
(5,1,226,1),
(6,1,227,474),
(7,1,279,2),
(9,1,280,528);
/*!40000 ALTER TABLE `app_entity_21_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_22`
--

DROP TABLE IF EXISTS `app_entity_22`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_22` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT 0,
  `parent_item_id` int(11) DEFAULT 0,
  `linked_id` int(11) DEFAULT 0,
  `date_added` bigint(20) NOT NULL DEFAULT 0,
  `date_updated` bigint(20) NOT NULL DEFAULT 0,
  `created_by` int(11) DEFAULT NULL,
  `sort_order` int(11) DEFAULT 0,
  `field_167` text NOT NULL,
  `field_168` text NOT NULL,
  `field_169` text NOT NULL,
  `field_170` text NOT NULL,
  `field_171` text NOT NULL,
  `field_172` text NOT NULL,
  `field_173` varchar(64) NOT NULL,
  `field_174` varchar(64) NOT NULL,
  `field_175` bigint(20) NOT NULL DEFAULT 0,
  `field_176` bigint(20) NOT NULL DEFAULT 0,
  `field_177` text NOT NULL,
  `field_232` text NOT NULL,
  `field_233` text NOT NULL,
  `field_234` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_field_232` (`field_232`(128)),
  KEY `idx_field_233` (`field_233`(128))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_22`
--

LOCK TABLES `app_entity_22` WRITE;
/*!40000 ALTER TABLE `app_entity_22` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_22` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_22_values`
--

DROP TABLE IF EXISTS `app_entity_22_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_22_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `items_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `value` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_items_fields_id` (`items_id`,`fields_id`),
  KEY `idx_value_id` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_22_values`
--

LOCK TABLES `app_entity_22_values` WRITE;
/*!40000 ALTER TABLE `app_entity_22_values` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_22_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_23`
--

DROP TABLE IF EXISTS `app_entity_23`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_23` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT 0,
  `parent_item_id` int(11) DEFAULT 0,
  `linked_id` int(11) DEFAULT 0,
  `date_added` bigint(20) NOT NULL DEFAULT 0,
  `date_updated` bigint(20) NOT NULL DEFAULT 0,
  `created_by` int(11) DEFAULT NULL,
  `sort_order` int(11) DEFAULT 0,
  `field_182` text NOT NULL,
  `field_183` text NOT NULL,
  `field_184` text NOT NULL,
  `field_185` text NOT NULL,
  `field_186` text NOT NULL,
  `field_194` text NOT NULL,
  `field_235` int(11) NOT NULL,
  `field_236` text NOT NULL,
  `field_237` bigint(11) NOT NULL,
  `field_238` int(11) NOT NULL,
  `field_239` text NOT NULL,
  `field_240` text NOT NULL,
  `field_241` varchar(255) NOT NULL,
  `field_276` int(11) NOT NULL,
  `field_277` text NOT NULL,
  `field_281` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_field_235` (`field_235`),
  KEY `idx_field_236` (`field_236`(128)),
  KEY `idx_field_237` (`field_237`),
  KEY `idx_field_238` (`field_238`),
  KEY `idx_field_239` (`field_239`(128)),
  KEY `idx_field_240` (`field_240`(128)),
  KEY `idx_field_276` (`field_276`),
  KEY `idx_field_281` (`field_281`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_23`
--

LOCK TABLES `app_entity_23` WRITE;
/*!40000 ALTER TABLE `app_entity_23` DISABLE KEYS */;
INSERT INTO `app_entity_23` VALUES
(1,0,0,0,1774348397,1774349936,1,0,'387','385','Тестовая заявка на подготовку документа','<p>Автоматически созданная тестовая заявка для проверки связки Rukovoditel -> карточка документа -> middleware.</p>','402','',404,'1',1774780397,410,'','1','http://localhost:18080/docs',394,'',551);
/*!40000 ALTER TABLE `app_entity_23` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_23_values`
--

DROP TABLE IF EXISTS `app_entity_23_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_23_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `items_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `value` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_items_fields_id` (`items_id`,`fields_id`),
  KEY `idx_value_id` (`value`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_23_values`
--

LOCK TABLES `app_entity_23_values` WRITE;
/*!40000 ALTER TABLE `app_entity_23_values` DISABLE KEYS */;
INSERT INTO `app_entity_23_values` VALUES
(1,1,182,387),
(2,1,183,385),
(4,1,235,404),
(5,1,236,1),
(6,1,238,410),
(7,1,276,394),
(8,1,240,1),
(12,1,186,402),
(13,1,281,551);
/*!40000 ALTER TABLE `app_entity_23_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_24`
--

DROP TABLE IF EXISTS `app_entity_24`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_24` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT 0,
  `parent_item_id` int(11) DEFAULT 0,
  `linked_id` int(11) DEFAULT 0,
  `date_added` bigint(20) NOT NULL DEFAULT 0,
  `date_updated` bigint(20) NOT NULL DEFAULT 0,
  `created_by` int(11) DEFAULT NULL,
  `sort_order` int(11) DEFAULT 0,
  `field_191` text NOT NULL,
  `field_192` text NOT NULL,
  `field_193` text NOT NULL,
  `field_195` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_24`
--

LOCK TABLES `app_entity_24` WRITE;
/*!40000 ALTER TABLE `app_entity_24` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_24` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_24_values`
--

DROP TABLE IF EXISTS `app_entity_24_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_24_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `items_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `value` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_items_fields_id` (`items_id`,`fields_id`),
  KEY `idx_value_id` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_24_values`
--

LOCK TABLES `app_entity_24_values` WRITE;
/*!40000 ALTER TABLE `app_entity_24_values` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_24_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_25`
--

DROP TABLE IF EXISTS `app_entity_25`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_25` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) unsigned DEFAULT 0,
  `parent_item_id` int(11) unsigned DEFAULT 0,
  `linked_id` int(11) unsigned DEFAULT 0,
  `date_added` bigint(11) DEFAULT 0,
  `date_updated` bigint(11) DEFAULT 0,
  `created_by` int(11) unsigned DEFAULT NULL,
  `sort_order` int(11) DEFAULT 0,
  `field_242` varchar(255) NOT NULL,
  `field_243` int(11) NOT NULL,
  `field_244` int(11) NOT NULL,
  `field_245` varchar(255) NOT NULL,
  `field_246` bigint(11) NOT NULL,
  `field_247` text NOT NULL,
  `field_248` bigint(11) NOT NULL,
  `field_249` varchar(255) NOT NULL,
  `field_250` varchar(255) NOT NULL,
  `field_251` text NOT NULL,
  `field_252` text NOT NULL,
  `field_253` text NOT NULL,
  `field_254` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_field_243` (`field_243`),
  KEY `idx_field_244` (`field_244`),
  KEY `idx_field_246` (`field_246`),
  KEY `idx_field_247` (`field_247`(128)),
  KEY `idx_field_248` (`field_248`),
  KEY `idx_field_251` (`field_251`(128)),
  KEY `idx_field_252` (`field_252`(128))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_25`
--

LOCK TABLES `app_entity_25` WRITE;
/*!40000 ALTER TABLE `app_entity_25` DISABLE KEYS */;
INSERT INTO `app_entity_25` VALUES
(1,0,0,0,1774348397,1774349936,1,0,'Тестовая заявка на подготовку документа',419,427,'',1774348397,'1',0,'1.0','http://localhost:18080/docs','','1','<p>Карточка создана автоматически из заявки #1.</p><p>Автоматически созданная тестовая заявка для проверки связки Rukovoditel -> карточка документа -> middleware.</p>',''),
(2,0,0,0,1774349478,1774349936,1,0,'Документ проекта: Тестовый проект цифрового документооборота',421,427,'',1774349478,'1',0,'1.0','http://localhost:18080/docs','1','','<p>Карточка создана автоматически из проекта #1.</p><p>Автоматически созданный тестовый проект для проверки связки проект -> карточка документа -> middleware.</p>','');
/*!40000 ALTER TABLE `app_entity_25` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_25_values`
--

DROP TABLE IF EXISTS `app_entity_25_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_25_values` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `items_id` int(11) unsigned NOT NULL,
  `fields_id` int(11) unsigned NOT NULL,
  `value` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_items_fields_id` (`items_id`,`fields_id`),
  KEY `idx_value_id` (`value`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_25_values`
--

LOCK TABLES `app_entity_25_values` WRITE;
/*!40000 ALTER TABLE `app_entity_25_values` DISABLE KEYS */;
INSERT INTO `app_entity_25_values` VALUES
(1,1,243,419),
(3,1,247,1),
(4,1,252,1),
(6,2,243,421),
(8,2,247,1),
(9,2,251,1),
(14,2,244,427),
(15,1,244,427);
/*!40000 ALTER TABLE `app_entity_25_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_26`
--

DROP TABLE IF EXISTS `app_entity_26`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_26` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) unsigned DEFAULT 0,
  `parent_item_id` int(11) unsigned DEFAULT 0,
  `linked_id` int(11) unsigned DEFAULT 0,
  `date_added` bigint(11) DEFAULT 0,
  `date_updated` bigint(11) DEFAULT 0,
  `created_by` int(11) unsigned DEFAULT NULL,
  `sort_order` int(11) DEFAULT 0,
  `field_255` varchar(255) NOT NULL,
  `field_256` int(11) NOT NULL,
  `field_257` int(11) NOT NULL,
  `field_258` varchar(255) NOT NULL,
  `field_259` text NOT NULL,
  `field_260` bigint(11) NOT NULL,
  `field_261` varchar(255) NOT NULL,
  `field_262` text NOT NULL,
  `field_263` text NOT NULL,
  `field_264` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_field_256` (`field_256`),
  KEY `idx_field_257` (`field_257`),
  KEY `idx_field_259` (`field_259`(128)),
  KEY `idx_field_260` (`field_260`),
  KEY `idx_field_262` (`field_262`(128))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_26`
--

LOCK TABLES `app_entity_26` WRITE;
/*!40000 ALTER TABLE `app_entity_26` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_26` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_26_values`
--

DROP TABLE IF EXISTS `app_entity_26_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_26_values` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `items_id` int(11) unsigned NOT NULL,
  `fields_id` int(11) unsigned NOT NULL,
  `value` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_items_fields_id` (`items_id`,`fields_id`),
  KEY `idx_value_id` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_26_values`
--

LOCK TABLES `app_entity_26_values` WRITE;
/*!40000 ALTER TABLE `app_entity_26_values` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_26_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_27`
--

DROP TABLE IF EXISTS `app_entity_27`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_27` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) unsigned DEFAULT 0,
  `parent_item_id` int(11) unsigned DEFAULT 0,
  `linked_id` int(11) unsigned DEFAULT 0,
  `date_added` bigint(11) DEFAULT 0,
  `date_updated` bigint(11) DEFAULT 0,
  `created_by` int(11) unsigned DEFAULT NULL,
  `sort_order` int(11) DEFAULT 0,
  `field_265` varchar(255) NOT NULL,
  `field_266` int(11) NOT NULL,
  `field_267` varchar(64) NOT NULL,
  `field_268` int(11) NOT NULL,
  `field_269` int(11) NOT NULL,
  `field_270` text NOT NULL,
  `field_271` bigint(11) NOT NULL,
  `field_272` text NOT NULL,
  `field_273` varchar(255) NOT NULL,
  `field_274` text NOT NULL,
  `field_275` text NOT NULL,
  `field_278` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_field_266` (`field_266`),
  KEY `idx_field_268` (`field_268`),
  KEY `idx_field_269` (`field_269`),
  KEY `idx_field_270` (`field_270`(128)),
  KEY `idx_field_271` (`field_271`),
  KEY `idx_field_272` (`field_272`(128))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_27`
--

LOCK TABLES `app_entity_27` WRITE;
/*!40000 ALTER TABLE `app_entity_27` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_27` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_entity_27_values`
--

DROP TABLE IF EXISTS `app_entity_27_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_entity_27_values` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `items_id` int(11) unsigned NOT NULL,
  `fields_id` int(11) unsigned NOT NULL,
  `value` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_items_fields_id` (`items_id`,`fields_id`),
  KEY `idx_value_id` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_27_values`
--

LOCK TABLES `app_entity_27_values` WRITE;
/*!40000 ALTER TABLE `app_entity_27_values` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_entity_27_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_favorites`
--

DROP TABLE IF EXISTS `app_favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_favorites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `users_id` int(11) NOT NULL,
  `entities_id` int(11) NOT NULL,
  `items_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_items_Id` (`items_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_favorites`
--

LOCK TABLES `app_favorites` WRITE;
/*!40000 ALTER TABLE `app_favorites` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_fields`
--

DROP TABLE IF EXISTS `app_fields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_fields` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `forms_tabs_id` int(11) NOT NULL,
  `comments_forms_tabs_id` int(11) NOT NULL DEFAULT 0,
  `forms_rows_position` varchar(255) NOT NULL,
  `type` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `short_name` varchar(64) NOT NULL,
  `is_heading` tinyint(1) DEFAULT 0,
  `tooltip` text NOT NULL,
  `tooltip_display_as` varchar(16) NOT NULL,
  `tooltip_in_item_page` tinyint(1) NOT NULL DEFAULT 0,
  `tooltip_item_page` text NOT NULL,
  `notes` text NOT NULL,
  `is_required` tinyint(1) DEFAULT 0,
  `required_message` text NOT NULL,
  `configuration` text NOT NULL,
  `sort_order` int(11) DEFAULT 0,
  `listing_status` tinyint(4) NOT NULL DEFAULT 0,
  `listing_sort_order` int(11) NOT NULL DEFAULT 0,
  `comments_status` tinyint(1) NOT NULL DEFAULT 0,
  `comments_sort_order` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_form_tabs_id` (`forms_tabs_id`),
  KEY `idx_comments_forms_tabs_id` (`comments_forms_tabs_id`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=282 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_fields`
--

LOCK TABLES `app_fields` WRITE;
/*!40000 ALTER TABLE `app_fields` DISABLE KEYS */;
INSERT INTO `app_fields` VALUES
(1,1,1,0,'','fieldtype_action','','',NULL,'','',0,'','',NULL,'','',NULL,1,0,0,0),
(2,1,1,0,'','fieldtype_id','','',NULL,'','',0,'','',NULL,'','',NULL,1,1,0,0),
(3,1,1,0,'','fieldtype_date_added','','',NULL,'','',0,'','',NULL,'','',NULL,0,0,0,0),
(4,1,1,0,'','fieldtype_created_by','','',NULL,'','',0,'','',NULL,'','',NULL,0,0,0,0),
(5,1,1,0,'','fieldtype_user_status','','',NULL,'','',0,'','',NULL,'','',0,1,7,0,0),
(6,1,1,0,'','fieldtype_user_accessgroups','','',NULL,'','',0,'','',NULL,'','',1,1,2,0,0),
(7,1,1,0,'','fieldtype_user_firstname','','',NULL,'','',0,'','',NULL,'','{\"allow_search\":\"1\"}',3,1,4,0,0),
(8,1,1,0,'','fieldtype_user_lastname','','',NULL,'','',0,'','',NULL,'','{\"allow_search\":\"1\"}',4,1,5,0,0),
(9,1,1,0,'','fieldtype_user_email','','',NULL,'','',0,'','',NULL,'','{\"allow_search\":\"1\"}',6,1,6,0,0),
(10,1,1,0,'','fieldtype_user_photo','','',NULL,'','',0,'','',NULL,'','',5,0,0,0,0),
(12,1,1,0,'','fieldtype_user_username','','',1,'','',0,'','',NULL,'','{\"allow_search\":\"1\"}',2,1,3,0,0),
(13,1,1,0,'','fieldtype_user_language','','',0,'','',0,'','',0,'','',7,0,0,0,0),
(14,1,1,0,'','fieldtype_user_skin','','',0,'','',0,'','',0,'','',0,0,0,0,0),
(152,21,24,0,'','fieldtype_action','','',0,'','',0,'','',0,'','',0,1,0,0,0),
(153,21,24,0,'','fieldtype_id','','',0,'','',0,'','',0,'','',0,1,1,0,0),
(154,21,24,0,'','fieldtype_date_added','','',0,'','',0,'','',0,'','',0,1,11,0,0),
(155,21,24,0,'','fieldtype_created_by','','',0,'','',0,'','',0,'','',0,1,12,0,0),
(156,21,24,0,'','fieldtype_dropdown','Приоритет','',0,'','',0,'','',1,'','{\"width\":\"input-medium\"}',0,1,2,1,1),
(157,21,24,0,'','fieldtype_dropdown','Этап','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',1,1,4,1,2),
(158,21,24,0,'','fieldtype_input','Название проекта','',1,'','',0,'','',1,'','{\"allow_search\":\"1\",\"width\":\"input-xlarge\"}',2,1,3,0,0),
(159,21,24,0,'','fieldtype_input_date','Дата старта','',0,'','',0,'','',0,'','',3,1,8,0,0),
(160,21,24,0,'','fieldtype_textarea_wysiwyg','Описание','',0,'','',0,'','',0,'','{\"allow_search\":\"1\"}',4,0,0,0,0),
(161,21,25,0,'','fieldtype_users','Команда','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown_muliple\",\"allow_search\":\"1\"}',0,0,0,0,0),
(162,21,24,0,'','fieldtype_attachments','Вложения','',0,'','',0,'','',0,'','',5,0,0,0,0),
(163,22,26,0,'','fieldtype_action','','',0,'','',0,'','',0,'','',0,1,0,0,0),
(164,22,26,0,'','fieldtype_id','','',0,'','',0,'','',0,'','',0,1,1,0,0),
(165,22,26,0,'','fieldtype_date_added','','',0,'','',0,'','',0,'','',0,1,10,0,0),
(166,22,26,0,'','fieldtype_created_by','','',0,'','',0,'','',0,'','',0,1,11,0,0),
(167,22,26,0,'','fieldtype_dropdown','Тип задачи','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',1,1,3,0,0),
(168,22,26,0,'','fieldtype_input','Название задачи','',1,'','',0,'','',1,'','{\"allow_search\":\"1\",\"width\":\"input-xlarge\"}',2,1,4,0,0),
(169,22,26,0,'','fieldtype_dropdown','Статус','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',3,1,5,1,2),
(170,22,26,0,'','fieldtype_dropdown','Приоритет','',0,'','',0,'','',1,'','{\"width\":\"input-medium\"}',4,1,2,1,1),
(171,22,26,0,'','fieldtype_users','Исполнители','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown_muliple\",\"allow_search\":\"1\"}',5,1,6,0,0),
(172,22,26,0,'','fieldtype_textarea_wysiwyg','Описание','',0,'','',0,'','',0,'','{\"allow_search\":\"1\"}',6,0,0,0,0),
(173,22,27,0,'','fieldtype_input_numeric','Плановые часы','',0,'','',0,'','',0,'','{\"width\":\"input-small\",\"number_format\":\"2/./*\"}',1,1,7,0,0),
(174,22,27,0,'','fieldtype_input_numeric_comments','Факт часов','',0,'','',0,'','',0,'','{\"width\":\"input-small\",\"number_format\":\"2/./*\"}',2,1,8,1,3),
(175,22,27,0,'','fieldtype_input_date','Дата начала','',0,'','',0,'','',0,'','',3,0,0,0,0),
(176,22,27,0,'','fieldtype_input_date','Срок исполнения','',0,'','',0,'','',0,'','',4,1,9,1,4),
(177,22,26,0,'','fieldtype_attachments','Вложения','',0,'','',0,'','',0,'','',7,0,0,0,0),
(178,23,28,0,'','fieldtype_action','','',0,'','',0,'','',0,'','',0,1,0,0,0),
(179,23,28,0,'','fieldtype_id','','',0,'','',0,'','',0,'','',0,1,1,0,0),
(180,23,28,0,'','fieldtype_date_added','','',0,'','',0,'','',0,'','',0,1,8,0,0),
(181,23,28,0,'','fieldtype_created_by','','',0,'','',0,'','',0,'','',0,1,9,0,0),
(182,23,28,0,'','fieldtype_grouped_users','Заявитель / группа','',0,'','',0,'','',1,'','',0,1,4,1,1),
(183,23,28,0,'','fieldtype_dropdown','Тип заявки','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',3,1,2,1,2),
(184,23,28,0,'','fieldtype_input','Тема заявки','',1,'','',0,'','',1,'','{\"allow_search\":\"1\",\"width\":\"input-xlarge\"}',4,1,3,0,0),
(185,23,28,0,'','fieldtype_textarea_wysiwyg','Описание','',0,'','',0,'','',0,'','{\"allow_search\":\"1\"}',5,0,0,0,0),
(186,23,28,0,'','fieldtype_dropdown','Статус','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',1,1,5,1,3),
(187,24,29,0,'','fieldtype_action','','',0,'','',0,'','',0,'','',0,1,0,0,0),
(188,24,29,0,'','fieldtype_id','','',0,'','',0,'','',0,'','',0,1,1,0,0),
(189,24,29,0,'','fieldtype_date_added','','',0,'','',0,'','',0,'','',0,1,4,0,0),
(190,24,29,0,'','fieldtype_created_by','','',0,'','',0,'','',0,'','',0,1,5,0,0),
(191,24,29,0,'','fieldtype_input','Тема обсуждения','',1,'','',0,'','',1,'','{\"allow_search\":\"1\",\"width\":\"input-xlarge\"}',1,1,3,0,0),
(192,24,29,0,'','fieldtype_textarea_wysiwyg','Описание','',0,'','',0,'','',0,'','{\"allow_search\":\"1\"}',2,0,0,0,0),
(193,24,29,0,'','fieldtype_dropdown','Статус','',0,'','',0,'','',0,'','{\"width\":\"input-medium\"}',0,1,2,1,0),
(194,23,28,0,'','fieldtype_attachments','Вложения','',0,'','',0,'','',0,'','',6,0,0,0,0),
(195,24,29,0,'','fieldtype_attachments','Вложения','',0,'','',0,'','',0,'','',3,0,0,0,0),
(196,1,1,0,'','fieldtype_parent_item_id','','',NULL,'','',0,'','',NULL,'','',NULL,1,100,0,0),
(197,21,24,0,'','fieldtype_parent_item_id','','',NULL,'','',0,'','',NULL,'','',NULL,0,100,0,0),
(198,22,26,0,'','fieldtype_parent_item_id','','',NULL,'','',0,'','',NULL,'','',NULL,0,100,0,0),
(199,23,28,0,'','fieldtype_parent_item_id','','',NULL,'','',0,'','',NULL,'','',NULL,0,100,0,0),
(200,24,29,0,'','fieldtype_parent_item_id','','',NULL,'','',0,'','',NULL,'','',NULL,0,100,0,0),
(201,1,1,0,'','fieldtype_user_last_login_date','','',0,'','',0,'','',0,'','',0,0,0,0,0),
(202,1,1,0,'','fieldtype_date_updated','','',0,'','',0,'','',0,'','',3,0,0,0,0),
(203,21,24,0,'','fieldtype_date_updated','','',0,'','',0,'','',0,'','',3,0,0,0,0),
(204,22,26,0,'','fieldtype_date_updated','','',0,'','',0,'','',0,'','',3,0,0,0,0),
(205,23,28,0,'','fieldtype_date_updated','','',0,'','',0,'','',0,'','',3,0,0,0,0),
(206,24,29,0,'','fieldtype_date_updated','','',0,'','',0,'','',0,'','',3,0,0,0,0),
(207,25,30,0,'','fieldtype_action','','',0,'','',0,'','',0,'','',0,1,0,0,0),
(208,25,30,0,'','fieldtype_id','','',0,'','',0,'','',0,'','',1,1,1,0,0),
(209,25,30,0,'','fieldtype_date_added','','',0,'','',0,'','',0,'','',2,1,9,0,0),
(210,25,30,0,'','fieldtype_date_updated','','',0,'','',0,'','',0,'','',3,0,0,0,0),
(211,25,30,0,'','fieldtype_created_by','','',0,'','',0,'','',0,'','',4,1,10,0,0),
(212,25,30,0,'','fieldtype_parent_item_id','','',0,'','',0,'','',0,'','',5,0,100,0,0),
(213,26,31,0,'','fieldtype_action','','',0,'','',0,'','',0,'','',0,1,0,0,0),
(214,26,31,0,'','fieldtype_id','','',0,'','',0,'','',0,'','',1,1,1,0,0),
(215,26,31,0,'','fieldtype_date_added','','',0,'','',0,'','',0,'','',2,1,8,0,0),
(216,26,31,0,'','fieldtype_date_updated','','',0,'','',0,'','',0,'','',3,0,0,0,0),
(217,26,31,0,'','fieldtype_created_by','','',0,'','',0,'','',0,'','',4,1,9,0,0),
(218,26,31,0,'','fieldtype_parent_item_id','','',0,'','',0,'','',0,'','',5,0,100,0,0),
(219,27,32,0,'','fieldtype_action','','',0,'','',0,'','',0,'','',0,1,0,0,0),
(220,27,32,0,'','fieldtype_id','','',0,'','',0,'','',0,'','',1,1,1,0,0),
(221,27,32,0,'','fieldtype_date_added','','',0,'','',0,'','',0,'','',2,1,7,0,0),
(222,27,32,0,'','fieldtype_date_updated','','',0,'','',0,'','',0,'','',3,0,0,0,0),
(223,27,32,0,'','fieldtype_created_by','','',0,'','',0,'','',0,'','',4,1,8,0,0),
(224,27,32,0,'','fieldtype_parent_item_id','','',0,'','',0,'','',0,'','',5,0,100,0,0),
(225,21,25,0,'','fieldtype_users','Руководитель проекта','',0,'','',0,'','',1,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',1,1,6,1,3),
(226,21,25,0,'','fieldtype_users','Куратор / преподаватель','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',2,1,7,1,4),
(227,21,24,0,'','fieldtype_dropdown','Подразделение / направление','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',3,1,5,0,0),
(228,21,33,0,'','fieldtype_input_date','Плановая дата завершения','',0,'','',0,'','',0,'','',0,1,9,1,5),
(229,21,33,0,'','fieldtype_progress','Прогресс','',0,'','',0,'','',0,'','{\"step\":\"5\",\"display_progress_bar\":\"1\",\"bar_color\":\"#214f8b\"}',1,1,10,1,6),
(230,21,33,0,'','fieldtype_input_url','Ссылка на NauDoc','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть документ\"}',2,0,0,0,0),
(231,21,33,0,'','fieldtype_textarea','Комментарий руководителя','',0,'','',0,'','',0,'','',5,0,0,0,0),
(232,22,26,0,'','fieldtype_users','Постановщик','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',6,0,0,0,0),
(233,22,27,0,'','fieldtype_entity','Связанная карточка документа','',0,'','',0,'','',0,'','{\"entity_id\":25,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',5,0,0,0,0),
(234,22,27,0,'','fieldtype_input_url','Ссылка на NauDoc','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть документ\"}',6,0,0,0,0),
(235,23,34,0,'','fieldtype_dropdown','Канал поступления','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',0,1,6,0,0),
(236,23,34,0,'','fieldtype_users','Ответственный','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',1,1,7,1,4),
(237,23,34,0,'','fieldtype_input_date','Срок исполнения','',0,'','',0,'','',0,'','',2,1,10,1,5),
(238,23,34,0,'','fieldtype_dropdown','Категория услуги','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',3,1,11,0,0),
(239,23,34,0,'','fieldtype_entity','Связанный проект','',0,'','',0,'','',0,'','{\"entity_id\":21,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',4,1,8,0,0),
(240,23,34,0,'','fieldtype_entity','Связанная карточка документа','',0,'','',0,'','',0,'','{\"entity_id\":25,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',5,1,9,0,0),
(241,23,34,0,'','fieldtype_input_url','Ссылка на NauDoc','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть документ\"}',6,0,0,0,0),
(242,25,30,0,'','fieldtype_input','Наименование документа','',1,'','',0,'','',1,'','{\"allow_search\":\"1\",\"width\":\"input-xlarge\"}',0,1,3,0,0),
(243,25,30,0,'','fieldtype_dropdown','Тип документа','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',1,1,2,1,0),
(244,25,35,0,'','fieldtype_dropdown','Статус документа','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',0,1,4,1,0),
(245,25,30,0,'','fieldtype_input','Регистрационный номер','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',2,1,5,0,0),
(246,25,30,0,'','fieldtype_input_date','Дата документа','',0,'','',0,'','',0,'','',3,1,6,0,0),
(247,25,30,0,'','fieldtype_users','Ответственный','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',4,1,7,0,0),
(248,25,35,0,'','fieldtype_input_date','Срок действия','',0,'','',0,'','',0,'','',1,1,8,0,0),
(249,25,35,0,'','fieldtype_input','Версия','',0,'','',0,'','',0,'','{\"width\":\"input-medium\"}',2,0,0,0,0),
(250,25,35,0,'','fieldtype_input_url','Ссылка на NauDoc','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть документ\"}',3,0,0,0,0),
(251,25,35,0,'','fieldtype_entity','Связанный проект','',0,'','',0,'','',0,'','{\"entity_id\":21,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',4,1,11,0,0),
(252,25,35,0,'','fieldtype_entity','Связанная заявка','',0,'','',0,'','',0,'','{\"entity_id\":23,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',5,1,12,0,0),
(253,25,30,0,'','fieldtype_textarea_wysiwyg','Описание','',0,'','',0,'','',0,'','{\"allow_search\":\"1\"}',5,0,0,0,0),
(254,25,30,0,'','fieldtype_attachments','Вложения','',0,'','',0,'','',0,'','',6,0,0,0,0),
(255,26,31,0,'','fieldtype_input','Название материала','',1,'','',0,'','',1,'','{\"allow_search\":\"1\",\"width\":\"input-xlarge\"}',0,1,3,0,0),
(256,26,31,0,'','fieldtype_dropdown','Категория','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',1,1,2,0,0),
(257,26,36,0,'','fieldtype_dropdown','Статус актуальности','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',0,1,4,1,0),
(258,26,36,0,'','fieldtype_input','Версия','',0,'','',0,'','',0,'','{\"width\":\"input-medium\"}',1,1,5,0,0),
(259,26,36,0,'','fieldtype_users','Ответственный','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',2,1,6,0,0),
(260,26,36,0,'','fieldtype_input_date','Следующий пересмотр','',0,'','',0,'','',0,'','',3,1,7,0,0),
(261,26,36,0,'','fieldtype_input_url','Ссылка на NauDoc','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть документ\"}',4,0,0,0,0),
(262,26,31,0,'','fieldtype_tags','Теги','',0,'','',0,'','',0,'','',2,0,0,0,0),
(263,26,31,0,'','fieldtype_textarea_wysiwyg','Краткое описание','',0,'','',0,'','',0,'','{\"allow_search\":\"1\"}',3,0,0,0,0),
(264,26,31,0,'','fieldtype_attachments','Вложения','',0,'','',0,'','',0,'','',4,0,0,0,0),
(265,27,32,0,'','fieldtype_input','Наименование потребности','',1,'','',0,'','',1,'','{\"allow_search\":\"1\",\"width\":\"input-xlarge\"}',1,1,3,0,0),
(266,27,32,0,'','fieldtype_dropdown','Категория МТЗ','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',2,1,2,0,0),
(267,27,32,0,'','fieldtype_input_numeric','Количество','',0,'','',0,'','',1,'','{\"width\":\"input-small\",\"number_format\":\"0/./*\"}',3,1,4,0,0),
(268,27,32,0,'','fieldtype_dropdown','Приоритет','',0,'','',0,'','',1,'','{\"width\":\"input-medium\"}',4,1,5,0,0),
(269,27,37,0,'','fieldtype_dropdown','Статус','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',0,1,6,1,0),
(270,27,37,0,'','fieldtype_users','Ответственный','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',1,1,7,0,0),
(271,27,37,0,'','fieldtype_input_date','Плановая дата поставки','',0,'','',0,'','',0,'','',2,1,9,0,0),
(272,27,37,0,'','fieldtype_entity','Связанный проект','',0,'','',0,'','',0,'','{\"entity_id\":21,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',3,1,8,0,0),
(273,27,37,0,'','fieldtype_input_url','Ссылка на NauDoc','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть документ\"}',4,0,0,0,0),
(274,27,32,0,'','fieldtype_textarea_wysiwyg','Обоснование','',0,'','',0,'','',0,'','{\"allow_search\":\"1\"}',5,0,0,0,0),
(275,27,32,0,'','fieldtype_attachments','Вложения','',0,'','',0,'','',0,'','',6,0,0,0,0),
(276,23,28,0,'','fieldtype_dropdown','Приоритет','',0,'','',0,'','',1,'','{\"width\":\"input-medium\"}',2,1,6,1,4),
(277,23,34,0,'','fieldtype_textarea','Результат исполнения','',0,'','',0,'','',0,'','',8,0,0,0,0),
(278,27,32,0,'','fieldtype_grouped_users','Инициатор / группа','',0,'','',0,'','',1,'','',0,1,6,0,0),
(279,21,33,0,'','fieldtype_entity','Связанная карточка документа','',0,'','',0,'','',0,'','{\"entity_id\":25,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',3,1,13,0,0),
(280,21,33,0,'','fieldtype_dropdown','Статус документа / интеграции','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',4,1,14,0,0),
(281,23,34,0,'','fieldtype_dropdown','Статус документа / интеграции','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',7,1,12,0,0);
/*!40000 ALTER TABLE `app_fields` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_fields_access`
--

DROP TABLE IF EXISTS `app_fields_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_fields_access` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `access_groups_id` int(11) NOT NULL,
  `entities_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `access_schema` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_access_groups_id` (`access_groups_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_fields_access`
--

LOCK TABLES `app_fields_access` WRITE;
/*!40000 ALTER TABLE `app_fields_access` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_fields_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_fields_choices`
--

DROP TABLE IF EXISTS `app_fields_choices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_fields_choices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL DEFAULT 0,
  `fields_id` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `name` varchar(255) NOT NULL,
  `icon` varchar(64) NOT NULL DEFAULT '',
  `is_default` tinyint(1) DEFAULT NULL,
  `bg_color` varchar(16) NOT NULL,
  `sort_order` int(11) DEFAULT NULL,
  `users` text NOT NULL,
  `value` varchar(64) NOT NULL,
  `filename` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB AUTO_INCREMENT=635 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_fields_choices`
--

LOCK TABLES `app_fields_choices` WRITE;
/*!40000 ALTER TABLE `app_fields_choices` DISABLE KEYS */;
INSERT INTO `app_fields_choices` VALUES
(382,0,183,1,'Техническая поддержка','',1,'#bde0fe',1,'','',''),
(383,0,183,1,'Методический вопрос','',0,'#cdb4db',2,'','',''),
(384,0,183,1,'Хозяйственный запрос','',0,'#ffe5b4',3,'','',''),
(385,0,183,1,'Документооборот','',0,'#ffd6a5',4,'','',''),
(386,0,183,1,'Доступ / учетная запись','',0,'#d8f3dc',5,'','',''),
(387,0,182,1,'Администрация','',1,'#d8e2dc',1,'1','',''),
(388,0,182,1,'Учебный отдел','',0,'#bee1e6',2,'1','',''),
(389,0,182,1,'Кафедра / преподаватели','',0,'#cdb4db',3,'1','',''),
(390,0,182,1,'Методический отдел','',0,'#ffc8dd',4,'1','',''),
(391,0,182,1,'ИТ и сервис','',0,'#bde0fe',5,'1','',''),
(392,0,182,1,'АХО / снабжение','',0,'#ffe5b4',6,'1','',''),
(393,0,276,1,'Критичный','',0,'#d90429',1,'','',''),
(394,0,276,1,'Высокий','',0,'#f77f00',2,'','',''),
(395,0,276,1,'Средний','',1,'#fcbf49',3,'','',''),
(396,0,276,1,'Низкий','',0,'#3a86ff',4,'','',''),
(397,0,186,1,'Новая','',1,'#dee2e6',1,'','',''),
(398,0,186,1,'Принята','',0,'#bde0fe',2,'','',''),
(399,0,186,1,'В работе','',0,'#8ecae6',3,'','',''),
(400,0,186,1,'На согласовании','',0,'#ffd166',4,'','',''),
(401,0,186,1,'Ожидает заявителя','',0,'#ffddd2',5,'','',''),
(402,0,186,1,'Выполнена','',0,'#95d5b2',6,'','',''),
(403,0,186,1,'Отклонена','',0,'#adb5bd',7,'','',''),
(404,0,235,1,'Веб-форма','',1,'',1,'','',''),
(405,0,235,1,'Телефон','',0,'',2,'','',''),
(406,0,235,1,'Почта','',0,'',3,'','',''),
(407,0,235,1,'Мессенджер','',0,'',4,'','',''),
(408,0,235,1,'Лично','',0,'',5,'','',''),
(409,0,238,1,'ИТ','',1,'',1,'','',''),
(410,0,238,1,'Документы','',0,'',2,'','',''),
(411,0,238,1,'Учебный процесс','',0,'',3,'','',''),
(412,0,238,1,'АХО / МТЗ','',0,'',4,'','',''),
(413,0,238,1,'Административное обслуживание','',0,'',5,'','',''),
(417,0,243,1,'Приказ','',0,'#d8f3dc',1,'','',''),
(418,0,243,1,'Договор','',0,'#bde0fe',2,'','',''),
(419,0,243,1,'Служебная записка','',0,'#ffd6a5',3,'','',''),
(420,0,243,1,'Заявление','',0,'#ffddd2',4,'','',''),
(421,0,243,1,'Регламент','',0,'#cdb4db',5,'','',''),
(422,0,243,1,'Акт','',0,'#ffe5b4',6,'','',''),
(423,0,243,1,'Иное','',1,'#e9ecef',7,'','',''),
(424,0,244,1,'Черновик','',1,'#dee2e6',1,'','',''),
(425,0,244,1,'На согласовании','',0,'#ffd166',2,'','',''),
(426,0,244,1,'На утверждении','',0,'#ffddd2',3,'','',''),
(427,0,244,1,'Подписан','',0,'#95d5b2',4,'','',''),
(428,0,244,1,'На ознакомлении','',0,'#bde0fe',5,'','',''),
(429,0,244,1,'Архивирован','',0,'#adb5bd',6,'','',''),
(460,0,156,1,'Критичный','',0,'#d90429',1,'','',''),
(461,0,156,1,'Высокий','',0,'#f77f00',2,'','',''),
(462,0,156,1,'Средний','',1,'#fcbf49',3,'','',''),
(463,0,156,1,'Низкий','',0,'#3a86ff',4,'','',''),
(464,0,157,1,'Инициирование','',1,'#c9d6ea',1,'','',''),
(465,0,157,1,'В работе','',0,'#8ecae6',2,'','',''),
(466,0,157,1,'На согласовании','',0,'#ffd166',3,'','',''),
(467,0,157,1,'На паузе','',0,'#adb5bd',4,'','',''),
(468,0,157,1,'Завершен','',0,'#95d5b2',5,'','',''),
(469,0,157,1,'В архиве','',0,'#ced4da',6,'','',''),
(470,0,227,1,'Администрация','',0,'#d8e2dc',1,'','',''),
(471,0,227,1,'Учебный отдел','',0,'#bee1e6',2,'','',''),
(472,0,227,1,'Кафедра / преподаватели','',0,'#cdb4db',3,'','',''),
(473,0,227,1,'Методический отдел','',0,'#ffc8dd',4,'','',''),
(474,0,227,1,'ИТ и сервис','',0,'#bde0fe',5,'','',''),
(475,0,227,1,'АХО / снабжение','',0,'#ffe5b4',6,'','',''),
(523,0,280,1,'Ожидает документ','',1,'#dee2e6',1,'','',''),
(524,0,280,1,'Связано','',0,'#bde0fe',2,'','',''),
(525,0,280,1,'Черновик','',0,'#c9d6ea',3,'','',''),
(526,0,280,1,'На согласовании','',0,'#ffd166',4,'','',''),
(527,0,280,1,'На утверждении','',0,'#ffddd2',5,'','',''),
(528,0,280,1,'Подписан','',0,'#95d5b2',6,'','',''),
(529,0,280,1,'На ознакомлении','',0,'#bde0fe',7,'','',''),
(530,0,280,1,'Архивирован','',0,'#adb5bd',8,'','',''),
(531,0,280,1,'Ошибка синхронизации','',0,'#d90429',9,'','',''),
(546,0,281,1,'Ожидает документ','',1,'#dee2e6',1,'','',''),
(547,0,281,1,'Связано','',0,'#bde0fe',2,'','',''),
(548,0,281,1,'Черновик','',0,'#c9d6ea',3,'','',''),
(549,0,281,1,'На согласовании','',0,'#ffd166',4,'','',''),
(550,0,281,1,'На утверждении','',0,'#ffddd2',5,'','',''),
(551,0,281,1,'Подписан','',0,'#95d5b2',6,'','',''),
(552,0,281,1,'На ознакомлении','',0,'#bde0fe',7,'','',''),
(553,0,281,1,'Архивирован','',0,'#adb5bd',8,'','',''),
(554,0,281,1,'Ошибка синхронизации','',0,'#d90429',9,'','',''),
(588,0,167,1,'Поручение','',1,'#d8f3dc',1,'','',''),
(589,0,167,1,'Согласование','',0,'#ffd166',2,'','',''),
(590,0,167,1,'Подготовка документа','',0,'#bde0fe',3,'','',''),
(591,0,167,1,'Контроль исполнения','',0,'#f8edeb',4,'','',''),
(592,0,169,1,'Новая','',1,'#dee2e6',1,'','',''),
(593,0,169,1,'В работе','',0,'#8ecae6',2,'','',''),
(594,0,169,1,'На согласовании','',0,'#ffd166',3,'','',''),
(595,0,169,1,'На проверке','',0,'#ffddd2',4,'','',''),
(596,0,169,1,'Выполнена','',0,'#95d5b2',5,'','',''),
(597,0,169,1,'Отменена','',0,'#adb5bd',6,'','',''),
(598,0,170,1,'Критичный','',0,'#d90429',1,'','',''),
(599,0,170,1,'Высокий','',0,'#f77f00',2,'','',''),
(600,0,170,1,'Средний','',1,'#fcbf49',3,'','',''),
(601,0,170,1,'Низкий','',0,'#3a86ff',4,'','',''),
(602,0,193,1,'Открыто','',1,'#bde0fe',1,'','',''),
(603,0,193,1,'В работе','',0,'#ffd166',2,'','',''),
(604,0,193,1,'Закрыто','',0,'#95d5b2',3,'','',''),
(605,0,256,1,'Регламент','',0,'#cdb4db',1,'','',''),
(606,0,256,1,'Шаблон','',0,'#bde0fe',2,'','',''),
(607,0,256,1,'Инструкция','',0,'#ffd6a5',3,'','',''),
(608,0,256,1,'Методический материал','',0,'#d8f3dc',4,'','',''),
(609,0,256,1,'Архивный материал','',0,'#dee2e6',5,'','',''),
(610,0,257,1,'Действует','',1,'#95d5b2',1,'','',''),
(611,0,257,1,'На пересмотре','',0,'#ffd166',2,'','',''),
(612,0,257,1,'Архив','',0,'#adb5bd',3,'','',''),
(613,0,266,1,'Канцелярия','',1,'#ffe5b4',1,'','',''),
(614,0,266,1,'Компьютерная техника','',0,'#bde0fe',2,'','',''),
(615,0,266,1,'Мебель','',0,'#d8f3dc',3,'','',''),
(616,0,266,1,'Расходные материалы','',0,'#ffd6a5',4,'','',''),
(617,0,266,1,'Программное обеспечение','',0,'#cdb4db',5,'','',''),
(618,0,266,1,'Иное','',0,'#dee2e6',6,'','',''),
(619,0,278,1,'Администрация','',1,'#d8e2dc',1,'1','',''),
(620,0,278,1,'Учебный отдел','',0,'#bee1e6',2,'1','',''),
(621,0,278,1,'Кафедра / преподаватели','',0,'#cdb4db',3,'1','',''),
(622,0,278,1,'Методический отдел','',0,'#ffc8dd',4,'1','',''),
(623,0,278,1,'ИТ и сервис','',0,'#bde0fe',5,'1','',''),
(624,0,278,1,'АХО / снабжение','',0,'#ffe5b4',6,'1','',''),
(625,0,268,1,'Критичный','',0,'#d90429',1,'','',''),
(626,0,268,1,'Высокий','',0,'#f77f00',2,'','',''),
(627,0,268,1,'Средний','',1,'#fcbf49',3,'','',''),
(628,0,268,1,'Низкий','',0,'#3a86ff',4,'','',''),
(629,0,269,1,'Новая','',1,'#dee2e6',1,'','',''),
(630,0,269,1,'На согласовании','',0,'#ffd166',2,'','',''),
(631,0,269,1,'В закупке','',0,'#bde0fe',3,'','',''),
(632,0,269,1,'Заказано','',0,'#ffddd2',4,'','',''),
(633,0,269,1,'Получено','',0,'#95d5b2',5,'','',''),
(634,0,269,1,'Отклонена','',0,'#adb5bd',6,'','','');
/*!40000 ALTER TABLE `app_fields_choices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_file_storage`
--

DROP TABLE IF EXISTS `app_file_storage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_file_storage` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entity_id` int(10) unsigned NOT NULL,
  `field_id` int(10) unsigned NOT NULL,
  `form_token` varchar(64) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `size` int(10) unsigned NOT NULL,
  `sort_order` int(11) NOT NULL,
  `folder` varchar(255) NOT NULL,
  `filekey` varchar(255) NOT NULL,
  `date_added` bigint(20) unsigned NOT NULL,
  `created_by` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entity_id` (`entity_id`),
  KEY `idx_field_id` (`field_id`),
  KEY `idx_form_token` (`form_token`),
  KEY `idx_filename` (`filename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_file_storage`
--

LOCK TABLES `app_file_storage` WRITE;
/*!40000 ALTER TABLE `app_file_storage` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_file_storage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_filters_panels`
--

DROP TABLE IF EXISTS `app_filters_panels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_filters_panels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `type` varchar(64) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_active_filters` tinyint(1) NOT NULL,
  `position` varchar(16) NOT NULL,
  `users_groups` text NOT NULL,
  `width` tinyint(1) NOT NULL,
  `sort_order` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_filters_panels`
--

LOCK TABLES `app_filters_panels` WRITE;
/*!40000 ALTER TABLE `app_filters_panels` DISABLE KEYS */;
INSERT INTO `app_filters_panels` VALUES
(1,22,'common_report_filters_panel_78',1,1,'horizontal','',0,0),
(2,23,'common_report_filters_panel_79',1,1,'horizontal','',0,0),
(3,21,'common_report_filters_panel_80',1,1,'horizontal','',0,0),
(4,25,'common_report_filters_panel_81',1,1,'horizontal','',0,0),
(5,27,'common_report_filters_panel_82',1,1,'horizontal','',0,0);
/*!40000 ALTER TABLE `app_filters_panels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_filters_panels_fields`
--

DROP TABLE IF EXISTS `app_filters_panels_fields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_filters_panels_fields` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `panels_id` int(11) NOT NULL,
  `entities_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `title` varchar(64) NOT NULL,
  `width` varchar(16) NOT NULL,
  `height` varchar(16) NOT NULL,
  `display_type` varchar(32) NOT NULL,
  `search_type_match` tinyint(1) NOT NULL,
  `exclude_values` text NOT NULL,
  `exclude_values_not_in_listing` tinyint(1) NOT NULL DEFAULT 0,
  `sort_order` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_panels_id` (`panels_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_filters_panels_fields`
--

LOCK TABLES `app_filters_panels_fields` WRITE;
/*!40000 ALTER TABLE `app_filters_panels_fields` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_filters_panels_fields` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_forms_fields_rules`
--

DROP TABLE IF EXISTS `app_forms_fields_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_forms_fields_rules` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entities_id` int(10) unsigned NOT NULL,
  `fields_id` int(10) unsigned NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `choices` text NOT NULL,
  `visible_fields` text NOT NULL,
  `hidden_fields` text NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_fields_id` (`fields_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_forms_fields_rules`
--

LOCK TABLES `app_forms_fields_rules` WRITE;
/*!40000 ALTER TABLE `app_forms_fields_rules` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_forms_fields_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_forms_rows`
--

DROP TABLE IF EXISTS `app_forms_rows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_forms_rows` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `forms_tabs_id` int(11) NOT NULL,
  `columns` tinyint(4) NOT NULL,
  `column1_width` tinyint(4) NOT NULL,
  `column2_width` tinyint(4) NOT NULL,
  `column3_width` tinyint(4) NOT NULL,
  `column4_width` tinyint(4) NOT NULL,
  `column5_width` tinyint(4) NOT NULL,
  `column6_width` tinyint(4) NOT NULL,
  `field_name_new_row` tinyint(1) NOT NULL,
  `sort_order` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `entities_id` (`entities_id`),
  KEY `forms_tabs_id` (`forms_tabs_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_forms_rows`
--

LOCK TABLES `app_forms_rows` WRITE;
/*!40000 ALTER TABLE `app_forms_rows` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_forms_rows` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_forms_tabs`
--

DROP TABLE IF EXISTS `app_forms_tabs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_forms_tabs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `parent_id` int(11) NOT NULL DEFAULT 0,
  `is_folder` tinyint(1) NOT NULL DEFAULT 0,
  `name` varchar(64) NOT NULL,
  `icon` varchar(64) NOT NULL,
  `icon_color` varchar(7) NOT NULL,
  `description` text NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_forms_tabs`
--

LOCK TABLES `app_forms_tabs` WRITE;
/*!40000 ALTER TABLE `app_forms_tabs` DISABLE KEYS */;
INSERT INTO `app_forms_tabs` VALUES
(1,1,0,0,'Информация','','','',0),
(24,21,0,0,'Основное','','','',0),
(25,21,0,0,'Команда и роли','','','',1),
(26,22,0,0,'Основное','','','',0),
(27,22,0,0,'Сроки и трудозатраты','','','',1),
(28,23,0,0,'Регистрация','','','',0),
(29,24,0,0,'Основное','','','',0),
(30,25,0,0,'Карточка','','','',0),
(31,26,0,0,'Документ','','','',0),
(32,27,0,0,'Заявка','','','',0),
(33,21,0,0,'Контроль','','','',2),
(34,23,0,0,'Исполнение','','','',1),
(35,25,0,0,'Согласование и архив','','','',1),
(36,26,0,0,'Актуализация','','','',1),
(37,27,0,0,'Исполнение','','','',1);
/*!40000 ALTER TABLE `app_forms_tabs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_global_lists`
--

DROP TABLE IF EXISTS `app_global_lists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_global_lists` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `notes` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_global_lists`
--

LOCK TABLES `app_global_lists` WRITE;
/*!40000 ALTER TABLE `app_global_lists` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_global_lists` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_global_lists_choices`
--

DROP TABLE IF EXISTS `app_global_lists_choices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_global_lists_choices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL DEFAULT 0,
  `lists_id` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `name` varchar(255) NOT NULL,
  `icon` varchar(64) NOT NULL DEFAULT '',
  `is_default` tinyint(1) DEFAULT NULL,
  `bg_color` varchar(16) NOT NULL,
  `value` varchar(64) NOT NULL,
  `sort_order` int(11) DEFAULT NULL,
  `users` text NOT NULL,
  `notes` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_lists_id` (`lists_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_global_lists_choices`
--

LOCK TABLES `app_global_lists_choices` WRITE;
/*!40000 ALTER TABLE `app_global_lists_choices` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_global_lists_choices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_global_vars`
--

DROP TABLE IF EXISTS `app_global_vars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_global_vars` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `is_folder` tinyint(1) NOT NULL,
  `name` varchar(64) NOT NULL,
  `value` varchar(255) NOT NULL,
  `notes` text NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_global_vars`
--

LOCK TABLES `app_global_vars` WRITE;
/*!40000 ALTER TABLE `app_global_vars` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_global_vars` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_help_pages`
--

DROP TABLE IF EXISTS `app_help_pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_help_pages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `type` varchar(16) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `name` varchar(255) NOT NULL,
  `icon` varchar(64) NOT NULL,
  `start_date` int(11) NOT NULL,
  `end_date` int(11) NOT NULL,
  `description` text NOT NULL,
  `color` varchar(16) NOT NULL,
  `position` varchar(16) NOT NULL,
  `users_groups` text NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_help_pages`
--

LOCK TABLES `app_help_pages` WRITE;
/*!40000 ALTER TABLE `app_help_pages` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_help_pages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_holidays`
--

DROP TABLE IF EXISTS `app_holidays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_holidays` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_holidays`
--

LOCK TABLES `app_holidays` WRITE;
/*!40000 ALTER TABLE `app_holidays` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_holidays` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_image_map_labels`
--

DROP TABLE IF EXISTS `app_image_map_labels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_image_map_labels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) NOT NULL,
  `choices_id` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_map_id` (`map_id`),
  KEY `idx_choices_id` (`choices_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_image_map_labels`
--

LOCK TABLES `app_image_map_labels` WRITE;
/*!40000 ALTER TABLE `app_image_map_labels` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_image_map_labels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_image_map_markers`
--

DROP TABLE IF EXISTS `app_image_map_markers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_image_map_markers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `items_id` int(11) NOT NULL,
  `map_id` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_map_id` (`map_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_image_map_markers`
--

LOCK TABLES `app_image_map_markers` WRITE;
/*!40000 ALTER TABLE `app_image_map_markers` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_image_map_markers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_image_map_markers_nested`
--

DROP TABLE IF EXISTS `app_image_map_markers_nested`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_image_map_markers_nested` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `items_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_image_map_markers_nested`
--

LOCK TABLES `app_image_map_markers_nested` WRITE;
/*!40000 ALTER TABLE `app_image_map_markers_nested` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_image_map_markers_nested` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_items_export_templates`
--

DROP TABLE IF EXISTS `app_items_export_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_items_export_templates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `users_id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `templates_fields` text NOT NULL,
  `is_default` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `cidx` (`entities_id`,`users_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_items_export_templates`
--

LOCK TABLES `app_items_export_templates` WRITE;
/*!40000 ALTER TABLE `app_items_export_templates` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_items_export_templates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_last_user_action`
--

DROP TABLE IF EXISTS `app_last_user_action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_last_user_action` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `users_id` int(10) unsigned NOT NULL,
  `date` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_last_user_action`
--

LOCK TABLES `app_last_user_action` WRITE;
/*!40000 ALTER TABLE `app_last_user_action` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_last_user_action` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_listing_highlight_rules`
--

DROP TABLE IF EXISTS `app_listing_highlight_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_listing_highlight_rules` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entities_id` int(10) unsigned NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `fields_id` int(10) unsigned NOT NULL,
  `fields_values` text NOT NULL,
  `bg_color` varchar(7) NOT NULL,
  `users_groups` text NOT NULL DEFAULT '',
  `sort_order` int(11) NOT NULL,
  `notes` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `entities_id` (`entities_id`),
  KEY `fields_id` (`fields_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_listing_highlight_rules`
--

LOCK TABLES `app_listing_highlight_rules` WRITE;
/*!40000 ALTER TABLE `app_listing_highlight_rules` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_listing_highlight_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_listing_sections`
--

DROP TABLE IF EXISTS `app_listing_sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_listing_sections` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `listing_types_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `fields` text NOT NULL,
  `display_as` varchar(16) NOT NULL,
  `display_field_names` tinyint(1) NOT NULL,
  `text_align` varchar(16) NOT NULL,
  `width` varchar(16) NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_listing_types_id` (`listing_types_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_listing_sections`
--

LOCK TABLES `app_listing_sections` WRITE;
/*!40000 ALTER TABLE `app_listing_sections` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_listing_sections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_listing_types`
--

DROP TABLE IF EXISTS `app_listing_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_listing_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `type` varchar(16) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_default` tinyint(4) NOT NULL,
  `width` smallint(6) NOT NULL,
  `settings` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_listing_types`
--

LOCK TABLES `app_listing_types` WRITE;
/*!40000 ALTER TABLE `app_listing_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_listing_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_login_attempt`
--

DROP TABLE IF EXISTS `app_login_attempt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_login_attempt` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_ip` varchar(64) NOT NULL,
  `count_attempt` smallint(5) unsigned NOT NULL,
  `is_banned` tinyint(1) NOT NULL DEFAULT 0,
  `date_banned` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_ip` (`user_ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_login_attempt`
--

LOCK TABLES `app_login_attempt` WRITE;
/*!40000 ALTER TABLE `app_login_attempt` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_login_attempt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_logs`
--

DROP TABLE IF EXISTS `app_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_logs` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `users_id` int(11) unsigned NOT NULL,
  `ip_address` varchar(64) NOT NULL,
  `log_type` varchar(16) NOT NULL,
  `date_added` int(11) NOT NULL,
  `http_url` varchar(255) NOT NULL,
  `is_ajax` tinyint(1) NOT NULL,
  `description` text NOT NULL,
  `seconds` decimal(11,4) NOT NULL,
  `errno` int(10) unsigned NOT NULL,
  `filename` varchar(255) NOT NULL,
  `linenum` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`),
  KEY `idx_date_added` (`date_added`),
  KEY `idx_ip_address` (`ip_address`),
  KEY `idx_log_type` (`log_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_logs`
--

LOCK TABLES `app_logs` WRITE;
/*!40000 ALTER TABLE `app_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_mind_map`
--

DROP TABLE IF EXISTS `app_mind_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_mind_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `items_id` int(11) DEFAULT NULL,
  `fields_id` int(11) DEFAULT NULL,
  `reports_id` int(11) DEFAULT NULL,
  `mm_id` varchar(64) NOT NULL,
  `mm_parent_id` varchar(64) NOT NULL,
  `mm_text` varchar(255) NOT NULL,
  `mm_layout` varchar(16) NOT NULL,
  `mm_shape` varchar(16) NOT NULL,
  `mm_side` varchar(16) NOT NULL,
  `mm_color` varchar(16) NOT NULL,
  `mm_icon` varchar(32) NOT NULL,
  `mm_collapsed` varchar(1) NOT NULL,
  `mm_value` varchar(64) NOT NULL,
  `mm_items_id` int(11) DEFAULT 0,
  `parent_entity_item_id` int(11) NOT NULL DEFAULT 0,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_reports_id` (`reports_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_mind_map`
--

LOCK TABLES `app_mind_map` WRITE;
/*!40000 ALTER TABLE `app_mind_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_mind_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_nested_entities_menu`
--

DROP TABLE IF EXISTS `app_nested_entities_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_nested_entities_menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `is_active` tinyint(4) NOT NULL,
  `name` varchar(64) NOT NULL,
  `entities` varchar(255) NOT NULL,
  `icon` varchar(64) NOT NULL,
  `icon_color` varchar(10) NOT NULL,
  `sort_order` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_nested_entities_menu`
--

LOCK TABLES `app_nested_entities_menu` WRITE;
/*!40000 ALTER TABLE `app_nested_entities_menu` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_nested_entities_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_onlyoffice_files`
--

DROP TABLE IF EXISTS `app_onlyoffice_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_onlyoffice_files` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entity_id` int(10) unsigned NOT NULL,
  `field_id` int(10) unsigned NOT NULL,
  `form_token` varchar(64) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `sort_order` int(11) NOT NULL,
  `folder` varchar(255) NOT NULL,
  `filekey` varchar(255) NOT NULL,
  `download_token` varchar(32) NOT NULL COMMENT 'For public download',
  `date_added` bigint(20) unsigned NOT NULL,
  `created_by` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entity_id` (`entity_id`),
  KEY `idx_field_id` (`field_id`),
  KEY `idx_form_token` (`form_token`),
  KEY `idx_filename` (`filename`),
  KEY `idx_download_token` (`download_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_onlyoffice_files`
--

LOCK TABLES `app_onlyoffice_files` WRITE;
/*!40000 ALTER TABLE `app_onlyoffice_files` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_onlyoffice_files` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_portlets`
--

DROP TABLE IF EXISTS `app_portlets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_portlets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `users_id` int(11) NOT NULL,
  `is_collapsed` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`,`users_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_portlets`
--

LOCK TABLES `app_portlets` WRITE;
/*!40000 ALTER TABLE `app_portlets` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_portlets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_records_visibility_rules`
--

DROP TABLE IF EXISTS `app_records_visibility_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_records_visibility_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `users_groups` text NOT NULL,
  `merged_fields` text NOT NULL,
  `merged_fields_empty_values` text NOT NULL,
  `notes` text NOT NULL,
  `mysql_query` text NOT NULL,
  `php_code` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_records_visibility_rules`
--

LOCK TABLES `app_records_visibility_rules` WRITE;
/*!40000 ALTER TABLE `app_records_visibility_rules` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_records_visibility_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_reports`
--

DROP TABLE IF EXISTS `app_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_reports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL DEFAULT 0,
  `entities_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `reports_type` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `description` text NOT NULL,
  `menu_icon` varchar(64) NOT NULL,
  `icon_color` varchar(7) NOT NULL,
  `bg_color` varchar(7) NOT NULL,
  `in_menu` tinyint(1) NOT NULL DEFAULT 0,
  `in_dashboard` tinyint(4) NOT NULL DEFAULT 0,
  `in_dashboard_counter` tinyint(1) NOT NULL DEFAULT 0,
  `in_dashboard_icon` tinyint(1) NOT NULL,
  `in_dashboard_counter_color` varchar(16) NOT NULL,
  `in_dashboard_counter_bg_color` varchar(16) NOT NULL,
  `in_dashboard_counter_fields` varchar(255) NOT NULL,
  `dashboard_counter_hide_count` tinyint(1) NOT NULL DEFAULT 0,
  `dashboard_counter_hide_zero_count` tinyint(1) NOT NULL,
  `dashboard_counter_sum_by_field` int(11) NOT NULL,
  `in_header` tinyint(1) NOT NULL DEFAULT 0,
  `in_header_autoupdate` tinyint(1) NOT NULL,
  `dashboard_sort_order` int(11) DEFAULT NULL,
  `header_sort_order` int(11) NOT NULL DEFAULT 0,
  `dashboard_counter_sort_order` int(11) NOT NULL DEFAULT 0,
  `listing_order_fields` text NOT NULL,
  `users_groups` text NOT NULL,
  `assigned_to` text NOT NULL,
  `displays_assigned_only` tinyint(1) NOT NULL DEFAULT 0,
  `parent_entity_id` int(11) NOT NULL DEFAULT 0,
  `parent_item_id` int(11) NOT NULL DEFAULT 0,
  `fields_in_listing` text NOT NULL,
  `rows_per_page` int(11) NOT NULL DEFAULT 0,
  `notification_days` varchar(32) NOT NULL,
  `notification_time` varchar(255) NOT NULL,
  `listing_type` varchar(16) NOT NULL,
  `listing_col_width` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_entity_id` (`parent_entity_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_reports_type` (`reports_type`),
  KEY `idx_in_dashboard` (`in_dashboard`),
  KEY `idx_in_dashboard_counter` (`in_dashboard_counter`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_reports`
--

LOCK TABLES `app_reports` WRITE;
/*!40000 ALTER TABLE `app_reports` DISABLE KEYS */;
INSERT INTO `app_reports` VALUES
(59,0,21,0,'default','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(61,0,22,0,'default','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(63,0,23,0,'default','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(68,0,24,0,'default','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(69,0,25,0,'default','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(70,0,26,0,'default','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(71,0,27,0,'default','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(72,73,22,1,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(73,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(74,0,25,1,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(75,0,21,1,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(76,0,27,1,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(77,0,23,1,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(78,0,22,0,'common','Мои задачи в работе','Задачи и поручения, которые требуют моего внимания прямо сейчас.','fa fa-check-square-o','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,10,0,10,'','0,4,5,6','',1,0,0,'',0,'','','',''),
(79,0,23,0,'common','Мои заявки','Собственные заявки и обращения, которые еще находятся в работе.','fa fa-life-ring','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,20,0,20,'','0,4,5,6','',1,0,0,'',0,'','','',''),
(80,0,21,0,'common','Проекты на контроле','Активные проекты, по которым руководителю важно видеть текущий этап и сроки.','fa fa-briefcase','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,30,0,30,'','0,4','',0,0,0,'',0,'','','',''),
(81,0,25,0,'common','Документы на согласовании','Документы, которые находятся на согласовании, утверждении или ознакомлении.','fa fa-files-o','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,40,0,40,'','0,4','',0,0,0,'',0,'','','',''),
(82,0,27,0,'common','Заявки МТЗ в работе','Заявки на обеспечение, которые требуют согласования или контроля закупки.','fa fa-cubes','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,50,0,50,'','0,4','',0,0,0,'',0,'','','',''),
(83,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(84,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(85,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(86,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(87,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(88,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(89,0,23,0,'common','Заявки без финального документа','Заявки, по которым документ еще не завершен или есть риск по интеграции.','fa fa-exclamation-circle','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,25,0,25,'','0,4','',0,0,0,'',0,'','','',''),
(90,0,21,0,'common','Проекты с риском по документам','Проекты, где документ еще не завершен или интеграция требует внимания.','fa fa-warning','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,35,0,35,'','0,4','',0,0,0,'',0,'','','','');
/*!40000 ALTER TABLE `app_reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_reports_filters`
--

DROP TABLE IF EXISTS `app_reports_filters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_reports_filters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reports_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `filters_values` text NOT NULL,
  `filters_condition` varchar(64) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `idx_reports_id` (`reports_id`),
  KEY `idx_fields_id` (`fields_id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_reports_filters`
--

LOCK TABLES `app_reports_filters` WRITE;
/*!40000 ALTER TABLE `app_reports_filters` DISABLE KEYS */;
INSERT INTO `app_reports_filters` VALUES
(68,59,157,'37,38,39','include',1),
(70,61,169,'46,47,48','include',1),
(72,63,186,'60,61,62','include',1),
(75,72,169,'46,47,48','include',1),
(76,75,157,'37,38,39','include',1),
(77,77,186,'60,61,62','include',1),
(103,78,169,'592,593,594,595','include',1),
(104,79,186,'397,398,399,400,401','include',1),
(105,89,281,'546,547,548,549,550,552,554','include',1),
(106,80,157,'464,465,466,467','include',1),
(107,90,280,'523,524,525,526,527,529,531','include',1),
(108,81,244,'425,426,428','include',1),
(109,82,269,'630,631,632','include',1);
/*!40000 ALTER TABLE `app_reports_filters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_reports_filters_templates`
--

DROP TABLE IF EXISTS `app_reports_filters_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_reports_filters_templates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fields_id` int(11) NOT NULL,
  `users_id` int(11) NOT NULL,
  `filters_values` text NOT NULL,
  `filters_condition` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cidx` (`fields_id`,`users_id`),
  KEY `idx_fields_id` (`fields_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_reports_filters_templates`
--

LOCK TABLES `app_reports_filters_templates` WRITE;
/*!40000 ALTER TABLE `app_reports_filters_templates` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_reports_filters_templates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_reports_groups`
--

DROP TABLE IF EXISTS `app_reports_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_reports_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `menu_icon` varchar(64) NOT NULL,
  `icon_color` varchar(7) NOT NULL,
  `bg_color` varchar(7) NOT NULL,
  `in_menu` tinyint(1) NOT NULL,
  `in_dashboard` tinyint(1) NOT NULL,
  `sort_order` smallint(6) NOT NULL,
  `counters_list` text NOT NULL,
  `reports_list` text NOT NULL,
  `created_by` int(11) NOT NULL,
  `is_common` tinyint(1) NOT NULL DEFAULT 0,
  `users_groups` text NOT NULL,
  `assigned_to` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_reports_groups`
--

LOCK TABLES `app_reports_groups` WRITE;
/*!40000 ALTER TABLE `app_reports_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_reports_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_reports_sections`
--

DROP TABLE IF EXISTS `app_reports_sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_reports_sections` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_by` int(11) NOT NULL,
  `count_columns` tinyint(1) NOT NULL DEFAULT 2,
  `reports_groups_id` int(11) NOT NULL,
  `report_left` varchar(64) NOT NULL,
  `report_right` varchar(64) NOT NULL,
  `sort_order` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_reports_groups_id` (`reports_groups_id`),
  KEY `idx_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_reports_sections`
--

LOCK TABLES `app_reports_sections` WRITE;
/*!40000 ALTER TABLE `app_reports_sections` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_reports_sections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_sessions`
--

DROP TABLE IF EXISTS `app_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_sessions` (
  `sesskey` varchar(32) NOT NULL,
  `expiry` bigint(20) unsigned NOT NULL,
  `value` longtext DEFAULT NULL,
  PRIMARY KEY (`sesskey`),
  KEY `idx_expiry` (`expiry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_sessions`
--

LOCK TABLES `app_sessions` WRITE;
/*!40000 ALTER TABLE `app_sessions` DISABLE KEYS */;
INSERT INTO `app_sessions` VALUES
('079385aa5a6611767980b9ed24f2cc79',1774348624,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"AnF0rkQ49W\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('281cc7e4d23f6fc5eeef8bf4bb3394b0',1774347638,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"OF6HO0nWvq\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('29fa8354ad5042661b149ee05f38494f',1774349860,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"E3smHA3JEq\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('2a92029ac2bb7d8e3d8515fd2cdd13c0',1774349832,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"7v76iAZwDf\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('2bb69ababbe71cc7b24e24624ca006d1',1774347638,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"GKnODpPmri\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('2ca446bba971ae56ba492d81f7505af1',1774348750,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"ZBimeti1SN\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}'),
('2e88134f296ad232f781464e4c0a8e7f',1774348633,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"3rOkskoMOZ\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}'),
('36a571d5ee573af669214b4cb2a32cce',1774350253,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"P8MIdW03bI\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('38d5cacfb8160b402a98b5169c93cf39',1774350216,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"27mij12VWg\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('483a4251d8d00a87e50b9951d20ac201',1774347638,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"SnnHnjjI9O\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('583e3e25df1e080a28d9d9b22602c200',1774347421,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"AM0CWtNMxz\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('5ccb024f6ed844500e78c6f884569990',1774348757,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"UqmkQSPDVQ\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('6e8e64755c0741ba93560ccf5ab8d496',1774347421,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"p5HVV5dkYh\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('70ae16e2f5903e69d33ad812b897df7f',1774348750,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"126JC8VbQA\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('7af63b705fb65aaa78d48f9c45b61e24',1774350216,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"ZOxuJWGcjg\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('807d7a7c0a4a40e17a0ecef65e59fe94',1774352837,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"OIQApYteeK\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('84fda7f16c3f19811122f94924a8f7b5',1774350253,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"z8T11Jtxxs\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('8a983507c71e7776698c2cdb7fea8530',1774348461,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"P7IzIWJ10V\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('8bdcf1b99489d5f569e65f3cbf237940',1774350520,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"TJwhqa4qak\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('9197ca7e9d0ac8634f4eb44db55b80d9',1774348650,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"OeQr3wUnTf\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}'),
('9c16e2d28269898645ed8d779c0875da',1774348800,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"M0mhRYsmxx\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('a6892c37f9431b918c60d2bca1aa86f6',1774349860,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"7qqKbn1ruX\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('abb01ebbcdfbcf1a6171fbc53cf22bc3',1774347617,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"q1OUk2UsGT\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('af750f8b6264afb3e5aeb3852ebcb961',1774347638,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"DYxHsO4EU5\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('b46e14e3bf6ec9502590bf9a113f2a61',1774347610,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"bnKRDoDfHp\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('b67f162a2fd5ece17a1a720a9e9ad8a8',1774350246,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"deNV0aCo8z\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('ba8bdfe04e6978e3eea01e7c17388846',1774352837,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"0bdMOzzX0f\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('d64f79a14ae88a546454b2f9bfd02582',1774349848,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"VEOfxc3vgM\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('db0b67978928b717727c5cf108ae7ff3',1774350291,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"sOnYtQ8G3N\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('e6e3c246fe337b91090fc84ea011b968',1774349331,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"w50J27mXcI\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('f0cac749bc5cd8fa427fdf2d16652bf1',1774348800,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"0ffF3DWJbp\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}');
/*!40000 ALTER TABLE `app_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_user_filters_values`
--

DROP TABLE IF EXISTS `app_user_filters_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_user_filters_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filters_id` int(11) NOT NULL,
  `reports_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `filters_values` text NOT NULL,
  `filters_condition` varchar(64) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `idx_filters_id` (`filters_id`),
  KEY `idx_reports_id` (`reports_id`),
  KEY `idx_fields_id` (`fields_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_user_filters_values`
--

LOCK TABLES `app_user_filters_values` WRITE;
/*!40000 ALTER TABLE `app_user_filters_values` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_user_filters_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_user_roles`
--

DROP TABLE IF EXISTS `app_user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_user_roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entities_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `sort_order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_user_roles`
--

LOCK TABLES `app_user_roles` WRITE;
/*!40000 ALTER TABLE `app_user_roles` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_user_roles_access`
--

DROP TABLE IF EXISTS `app_user_roles_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_user_roles_access` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_roles_id` int(11) NOT NULL,
  `fields_id` int(11) NOT NULL,
  `entities_id` int(11) NOT NULL,
  `access_schema` varchar(255) NOT NULL,
  `comments_access` varchar(64) NOT NULL,
  `fields_access` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_fields_id` (`fields_id`),
  KEY `idx_user_roles_id` (`user_roles_id`),
  KEY `entities_id` (`entities_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_user_roles_access`
--

LOCK TABLES `app_user_roles_access` WRITE;
/*!40000 ALTER TABLE `app_user_roles_access` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_user_roles_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_user_roles_to_items`
--

DROP TABLE IF EXISTS `app_user_roles_to_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_user_roles_to_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fields_id` int(11) NOT NULL,
  `entities_id` int(11) NOT NULL,
  `items_id` int(11) NOT NULL,
  `users_id` int(11) NOT NULL,
  `roles_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_roles_id` (`roles_id`),
  KEY `idx_users_id` (`users_id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_fields_id` (`fields_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_user_roles_to_items`
--

LOCK TABLES `app_user_roles_to_items` WRITE;
/*!40000 ALTER TABLE `app_user_roles_to_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_user_roles_to_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_users_alerts`
--

DROP TABLE IF EXISTS `app_users_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_users_alerts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_active` tinyint(1) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `type` varchar(16) NOT NULL,
  `location` varchar(16) NOT NULL,
  `start_date` bigint(20) unsigned NOT NULL,
  `end_date` bigint(20) unsigned NOT NULL,
  `assigned_to` text NOT NULL,
  `users_groups` text NOT NULL,
  `created_by` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_alerts`
--

LOCK TABLES `app_users_alerts` WRITE;
/*!40000 ALTER TABLE `app_users_alerts` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_users_alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_users_alerts_viewed`
--

DROP TABLE IF EXISTS `app_users_alerts_viewed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_users_alerts_viewed` (
  `users_id` int(11) NOT NULL,
  `alerts_id` int(11) NOT NULL,
  KEY `idx_ueser_alerts` (`users_id`,`alerts_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_alerts_viewed`
--

LOCK TABLES `app_users_alerts_viewed` WRITE;
/*!40000 ALTER TABLE `app_users_alerts_viewed` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_users_alerts_viewed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_users_configuration`
--

DROP TABLE IF EXISTS `app_users_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_users_configuration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `users_id` int(11) NOT NULL,
  `configuration_name` varchar(255) NOT NULL,
  `configuration_value` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_configuration`
--

LOCK TABLES `app_users_configuration` WRITE;
/*!40000 ALTER TABLE `app_users_configuration` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_users_configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_users_filters`
--

DROP TABLE IF EXISTS `app_users_filters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_users_filters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reports_id` int(11) NOT NULL,
  `users_id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `fields_in_listing` text NOT NULL,
  `listing_order_fields` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_reports_id` (`reports_id`),
  KEY `idx_users_id` (`users_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_filters`
--

LOCK TABLES `app_users_filters` WRITE;
/*!40000 ALTER TABLE `app_users_filters` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_users_filters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_users_login_log`
--

DROP TABLE IF EXISTS `app_users_login_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_users_login_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `users_id` int(11) DEFAULT NULL,
  `username` varchar(255) NOT NULL,
  `identifier` varchar(255) NOT NULL,
  `is_success` tinyint(1) NOT NULL,
  `date_added` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_login_log`
--

LOCK TABLES `app_users_login_log` WRITE;
/*!40000 ALTER TABLE `app_users_login_log` DISABLE KEYS */;
INSERT INTO `app_users_login_log` VALUES
(6,1,'admin','172.19.0.1',1,1774346995),
(7,1,'admin','172.19.0.1',1,1774347310),
(8,1,'admin','172.19.0.1',1,1774347317),
(9,1,'admin','172.19.0.1',1,1774347360),
(10,1,'admin','172.19.0.1',1,1774347891),
(11,1,'admin','172.19.0.1',1,1774348408),
(12,1,'admin','172.19.0.1',1,1774348420),
(13,1,'admin','172.19.0.1',1,1774348420);
/*!40000 ALTER TABLE `app_users_login_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_users_notifications`
--

DROP TABLE IF EXISTS `app_users_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_users_notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `users_id` int(11) NOT NULL,
  `entities_id` int(11) NOT NULL,
  `items_id` int(11) NOT NULL,
  `name` text NOT NULL,
  `type` varchar(16) NOT NULL,
  `date_added` bigint(20) unsigned NOT NULL,
  `created_by` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`),
  KEY `idx_entities_id` (`entities_id`),
  KEY `idx_items_id` (`items_id`),
  KEY `idx_uei` (`users_id`,`entities_id`) USING BTREE,
  KEY `idx_created_by` (`created_by`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_notifications`
--

LOCK TABLES `app_users_notifications` WRITE;
/*!40000 ALTER TABLE `app_users_notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_users_notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_users_search_settings`
--

DROP TABLE IF EXISTS `app_users_search_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_users_search_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `users_id` int(11) NOT NULL,
  `reports_id` int(11) NOT NULL,
  `configuration_name` varchar(255) NOT NULL,
  `configuration_value` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`),
  KEY `idx_users_reports_id` (`users_id`,`reports_id`),
  KEY `idx_reports_id` (`reports_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_search_settings`
--

LOCK TABLES `app_users_search_settings` WRITE;
/*!40000 ALTER TABLE `app_users_search_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_users_search_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_who_is_online`
--

DROP TABLE IF EXISTS `app_who_is_online`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_who_is_online` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `users_id` int(11) NOT NULL,
  `date_updated` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_users_id` (`users_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_who_is_online`
--

LOCK TABLES `app_who_is_online` WRITE;
/*!40000 ALTER TABLE `app_who_is_online` DISABLE KEYS */;
INSERT INTO `app_who_is_online` VALUES
(1,1,1774348420);
/*!40000 ALTER TABLE `app_who_is_online` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'rukovoditel'
--

--
-- Dumping routines for database 'rukovoditel'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-24 11:23:17
