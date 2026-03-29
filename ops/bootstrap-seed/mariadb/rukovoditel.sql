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
(4,'Заведующий отделением / руководитель подразделения',0,0,'',10,'Согласование, утверждение и управленческий контроль по подразделению.'),
(5,'Врач / сотрудник подразделения',0,0,'',20,'Ежедневная работа с документами, заявками, задачами и проектами подразделения.'),
(6,'Регистратура / заявитель',0,0,'',30,'Подача обращений, регистрация входящих запросов и отслеживание собственных кейсов.'),
(7,'Канцелярия / делопроизводство',0,0,'',40,'Регистрация документов, контроль маршрутов, номенклатуры и архива.'),
(8,'Старшая медсестра / координатор отделения',0,0,'',25,'Координация документооборота отделения, контроль исполнения и сопровождение маршрутов внутри подразделения.');
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_attachments`
--

LOCK TABLES `app_attachments` WRITE;
/*!40000 ALTER TABLE `app_attachments` DISABLE KEYS */;
INSERT INTO `app_attachments` VALUES
(3,'469e7422c418c29c8a566350b7a6e7c4','1774721884_20260326_224621.png','2026-03-28','264');
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
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_configuration`
--

LOCK TABLES `app_configuration` WRITE;
/*!40000 ALTER TABLE `app_configuration` DISABLE KEYS */;
INSERT INTO `app_configuration` VALUES
(9,'CFG_APP_NAME','Единая платформа документооборота'),
(10,'CFG_APP_SHORT_NAME','Документооборот'),
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
(34,'CFG_LOGIN_PAGE_HEADING','Рабочий контур платформы документооборота'),
(35,'CFG_LOGIN_PAGE_CONTENT','Проекты, заявки, совместная работа над документами, маршруты согласования и архив в едином рабочем веб-контуре.'),
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
(46,'CFG_CUSTOM_CSS_TIME','1774347288'),
(47,'CFG_APP_SHORT_NAME_MOBILE',''),
(48,'CFG_APP_LOGO_URL',''),
(49,'CFG_APP_FAVICON',''),
(50,'CFG_APP_COPYRIGHT_NAME',''),
(51,'CFG_APP_NUMBER_FORMAT','2/./*'),
(52,'CFG_APP_FIRST_DAY_OF_WEEK','0'),
(53,'CFG_DROP_DOWN_MENU_ON_HOVER','0'),
(54,'CFG_DISABLE_CHECK_FOR_UPDATES','0');
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
(21,0,1,'Проекты и инициативы','Клинические, административные, ИТ и хозяйственные проекты учреждения.',1,10),
(22,21,1,'Поручения и задачи','Задачи и поручения внутри проектов и процессов.',1,11),
(23,0,1,'Заявки на обслуживание','Сервисные и документные заявки от сотрудников, врачей и регистратуры.',1,20),
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
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(48,27,6,'create,view_assigned,update,reports'),
(49,21,7,'view,reports'),
(50,22,7,'view,reports'),
(51,23,7,'view,reports'),
(52,24,7,''),
(53,25,7,'view,create,update,reports'),
(54,26,7,'view,create,update,reports'),
(55,27,7,'view,reports'),
(56,21,8,'view,create,update,reports'),
(57,22,8,'view,create,update,reports'),
(58,23,8,'view,create,update,reports'),
(59,24,8,'view_assigned,create,update,reports'),
(60,25,8,'view,create,update,reports'),
(61,26,8,'view,reports'),
(62,27,8,'view,create,update,reports');
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entities_menu`
--

LOCK TABLES `app_entities_menu` WRITE;
/*!40000 ALTER TABLE `app_entities_menu` DISABLE KEYS */;
INSERT INTO `app_entities_menu` VALUES
(2,0,'Работа','fa-tasks','#1f4f86','#e8f1fb','23,21,22,27','','','entity','','','',10),
(3,0,'Документы','fa-folder-open-o','#8a4b08','#fff1dd','25,26','','','entity','','','',20),
(4,0,'Контроль','fa-line-chart','#204b76','#d9e8f6','','common80,common90,common89,common81,common82','','entity','','','',30),
(5,0,'Канцелярия','fa-archive','#8a4b08','#f8e8d0','','common91','','entity','','','',40);
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_1`
--

LOCK TABLES `app_entity_1` WRITE;
/*!40000 ALTER TABLE `app_entity_1` DISABLE KEYS */;
INSERT INTO `app_entity_1` VALUES
(1,2986271,0,0,0,1774345972,1774786460,NULL,0,'$P$EDO3VHH.Lpx8VXt9joWw6h3.S8BORr.','',1,1,0,'Иван Иванович','Иванов','admin@example.local','','admin','russian.php','blue',1774786461),
(2,1509012,0,0,0,1774360158,1774786460,0,0,'$P$ExnfhxHqzro72d/kzdyCurFMvgaRBb1','',1,0,4,'Мария','Заведующая','manager.test@example.local','','manager.test','russian.php','light',1774710072),
(3,3381673,0,0,0,1774360158,1774786460,0,0,'$P$E2J5wr9WOdkkocuHWg6XwvohXMeITr1','',1,0,5,'Илья','Врач','employee.test@example.local','','employee.test','russian.php','light',1774710072),
(4,2724394,0,0,0,1774360158,1774786460,0,0,'$P$ETCJdTscq1TGDfc7DcFUoanPraRoK41','',1,0,6,'Ольга','Регистратор','requester.test@example.local','','requester.test','russian.php','light',1774710072),
(5,6253855,0,0,0,1774360158,1774786460,0,0,'$P$ETLvO09JJQsId0IKwYeMWwZt6RGpqJ1','',1,0,7,'Анна','Делопроизводитель','office.test@example.local','','office.test','russian.php','light',1774710073),
(6,1199206,0,0,0,1774564278,1774786460,0,0,'$P$E6IZqJuksQbNHs5WQKFgzpoUWU55HP/','',1,0,5,'Елена','Сотрудник','user.demo@example.local','','user.demo','russian.php','light',1774710467),
(7,2008067,0,0,0,1774681478,1774786460,0,0,'$P$ERY9LB51GJ16Avw3S2QDD270pwOl3E1','',1,0,8,'Наталья','Старшая медсестра','nurse.test@example.local','','nurse.test','russian.php','light',1774710570),
(8,2321338,0,0,0,1774715603,1774786460,0,0,'$P$EqBNgYChA6SULUFmmjUThI6dgpexA1.','',1,1,4,'Мария','Заведующая','department.head@hospital.local','','department.head','russian.php','light',1774786461),
(9,8058019,0,0,0,1774715603,1774786460,0,0,'$P$Ew/q8NpkskE4V8bSpadMwVzcxDhDgt/','',1,1,5,'Илья','Врач','clinician.primary@hospital.local','','clinician.primary','russian.php','light',1774786462),
(10,85990410,0,0,0,1774715603,1774786460,0,0,'$P$EHKNRmYnVJd/B87StBemIcvTKNjrTv/','',1,1,8,'Наталья','Старшая медсестра','nurse.coordinator@hospital.local','','nurse.coordinator','russian.php','light',1774786462),
(11,75192311,0,0,0,1774715603,1774786460,0,0,'$P$ETYDiPQgeWHK8ZDDl24ODuln7BTCtp1','',1,1,6,'Ольга','Регистратор','registry.operator@hospital.local','','registry.operator','russian.php','light',1774786462),
(12,63965912,0,0,0,1774715603,1774786460,0,0,'$P$E5a/im4qqXr4WLQ3twePsFlzPlCMUF/','',1,1,7,'Анна','Делопроизводитель','records.office@hospital.local','','records.office','russian.php','light',1774786462);
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
  `field_284` varchar(255) NOT NULL,
  `field_285` varchar(255) NOT NULL,
  `field_295` int(11) NOT NULL,
  `field_296` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_field_225` (`field_225`(128)),
  KEY `idx_field_226` (`field_226`(128)),
  KEY `idx_field_227` (`field_227`),
  KEY `idx_field_228` (`field_228`),
  KEY `idx_field_229` (`field_229`),
  KEY `idx_field_279` (`field_279`(128)),
  KEY `idx_field_280` (`field_280`),
  KEY `idx_field_295` (`field_295`),
  KEY `idx_field_296` (`field_296`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_21`
--

LOCK TABLES `app_entity_21` WRITE;
/*!40000 ALTER TABLE `app_entity_21` DISABLE KEYS */;
INSERT INTO `app_entity_21` VALUES
(1,0,0,0,1774349478,1774785745,1,0,'461','465','Внедрение единой платформы документооборота',1773990000,'<p>Пилотный проект по запуску единого контура: рабочие процессы в Rukovoditel, официальный документный контур в NauDoc, совместное редактирование в ONLYOFFICE.</p>','2,3,5','','1','1',470,1776236400,55,'https://docflow.hospital.local/docs/storage/bridge_document_cards_2','Контрольный кейс для показа заказчику: проект, документы, согласование и публикация финальной версии.','2',524,'https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=21&item_id=1','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=21&item_id=1',828,832),
(2,0,0,0,1774249200,1774680236,1,0,'462','466','Подготовка регламента согласования учебных документов',1774249200,'<p>Второй демонстрационный кейс: проект в стадии согласования, по нему еще нет опубликованной финальной версии в NauDoc.</p>','2,3','','2','2',471,1776668400,25,'https://docflow.hospital.local/docs/storage/bridge_document_cards_3','Кейс нужен для показа статусов: проект в работе, документ ожидает публикации.','3',524,'','',0,0),
(3,0,0,0,1770706800,1774785745,2,0,'463','468','Архивирование завершенных регламентов',1770706800,'<p>Завершенный демонстрационный кейс для показа жизненного цикла проекта: рабочая стадия, публикация документа, регистрация и перевод материалов в архив.</p>','2,5','','2','2',470,1773558000,100,'https://docflow.hospital.local/docs/storage/bridge_document_cards_8','Проект завершен. Документ зарегистрирован и материалы переданы в архив.','8',524,'https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=21&item_id=3','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=21&item_id=3',829,832),
(4,0,0,0,1774249200,1774785745,1,0,'462','466','Подготовка регламента согласования внутренних документов',1774249200,'<p>Второй демонстрационный кейс: проект в стадии согласования, по нему еще нет опубликованной финальной версии в NauDoc.</p>','2,3','','2','2',471,1776668400,25,'https://docflow.hospital.local/docs/storage/bridge_document_cards_12','Кейс нужен для показа статусов: проект в работе, документ ожидает публикации.','12',524,'https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=21&item_id=4','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=21&item_id=4',828,832);
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
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(10,2,279,3),
(20,4,279,12),
(25,2,280,524),
(60,4,280,524),
(61,3,280,524),
(62,1,280,524);
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_22`
--

LOCK TABLES `app_entity_22` WRITE;
/*!40000 ALTER TABLE `app_entity_22` DISABLE KEYS */;
INSERT INTO `app_entity_22` VALUES
(1,0,0,0,1774335600,1774785670,2,0,'800','Подготовить текст приказа о запуске пилота','803','809','1,2,3','<p>Подготовить финальный текст приказа, сверить состав согласующих и приложить версию для запуска маршрута.</p>','6','2',1774335600,1774681200,'','2','5',''),
(2,0,0,0,1774422000,1774600896,2,0,'799','Проверить регламент согласования учебных документов','804','810','1,2,5','<p>Нужно проверить последовательность согласования, сроки и роли участников перед публикацией регламента.</p>','4','1',1774422000,1774854000,'','2','2',''),
(3,0,0,0,1774508400,1774785670,5,0,'801','Собрать замечания канцелярии к входящему договору','805','810','4,5','<p>Канцелярия готовит замечания к карточке договора и проверяет, все ли реквизиты отражены перед передачей документа в работу.</p>','3','2',1774508400,1774767600,'','5','6','https://docflow.hospital.local/docs'),
(4,0,0,0,1774162800,1774785670,1,0,'798','Подготовить комплект закупки МФУ для канцелярии','806','809','3','<p>Комплект документов для закупки сформирован и передан дальше. Задача закрыта и используется как пример завершенного поручения.</p>','5','5',1774162800,1774335600,'','1','1','https://docflow.hospital.local/docs'),
(5,0,0,0,1774422000,1774785670,2,0,'799','Проверить регламент согласования внутренних документов','804','810','1,2,5','<p>Нужно проверить последовательность согласования, сроки и роли участников перед публикацией регламента.</p>','4','1',1774422000,1774854000,'','2','2','');
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
  `field_286` varchar(255) NOT NULL,
  `field_287` varchar(255) NOT NULL,
  `field_297` int(11) NOT NULL,
  `field_298` int(11) NOT NULL,
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
  KEY `idx_field_281` (`field_281`),
  KEY `idx_field_297` (`field_297`),
  KEY `idx_field_298` (`field_298`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_23`
--

LOCK TABLES `app_entity_23` WRITE;
/*!40000 ALTER TABLE `app_entity_23` DISABLE KEYS */;
INSERT INTO `app_entity_23` VALUES
(1,0,0,0,1774348397,1774785745,1,0,'387','385','Подготовка маршрута согласования приказа о пилоте','<p>Нужно оформить карточку документа, настроить маршрут согласования и подготовить публикацию итоговой версии в NauDoc.</p>','400','',404,'1',1774681200,410,'1','1','https://docflow.hospital.local/docs/storage/bridge_document_cards_1',394,'Карточка документа создана, маршрут согласования завершен, ссылка на итоговый документ возвращена в рабочий контур.',547,'https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=23&item_id=1','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=23&item_id=1',835,836),
(2,0,0,0,1774335600,1774680236,1,0,'389','383','Подключить шаблон служебной записки для кафедр','<p>Требуется подготовить шаблон служебной записки, дать доступ кафедрам и вывести документ в общий контур согласования.</p>','400','',406,'3',1774940400,411,'2','9','https://docflow.hospital.local/docs/storage/bridge_document_cards_9',395,'',547,'','',0,0),
(3,0,0,0,1774536023,1774785745,5,0,'5','384','Закупка принтера для регистратора канцелярии','<p>Хозяйственная заявка на закупку принтера для рабочего места регистратора. Нужна как наглядный пример не-документного сервисного запроса.</p>','400','1774536021_3.drawio.png',405,'5',1775286000,412,'','10','https://docflow.hospital.local/docs/storage/bridge_document_cards_10',395,'Подготовлено коммерческое предложение, ожидается закупка по линии обеспечения.',547,'','',0,0),
(4,0,0,0,1774422000,1774785745,5,0,'5','385','Оформить карточку входящего договора на сопровождение','<p>Кейс канцелярии: нужно зарегистрировать входящий договор, связать его с карточкой документа и вернуть ссылку на официальный контур.</p>','400','',406,'5',1774854000,410,'','6','https://docflow.hospital.local/docs/storage/bridge_document_cards_6',395,'Карточка договора открыта, регистрация проходит через канцелярский контур.',547,'https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=23&item_id=4','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=23&item_id=4',834,836),
(5,0,0,0,1774508400,1774785745,4,0,'4','383','Открыть доступ к шаблонам служебной записки','<p>Заявка от сотрудника подразделения: требуется открыть доступ к шаблонам служебных записок и инструкциям по оформлению документов.</p>','400','',407,'3',1775113200,411,'4','11','https://docflow.hospital.local/docs/storage/bridge_document_cards_11',394,'Ожидается уточнение по отделениям и перечню шаблонов.',547,'https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=23&item_id=5','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=23&item_id=5',834,837),
(6,0,0,0,1774335600,1774785745,1,0,'389','383','Подключить шаблон служебной записки для отделений','<p>Требуется подготовить шаблон служебной записки, дать доступ отделениям и вывести документ в общий контур согласования.</p>','400','',406,'3',1774940400,411,'4','13','https://docflow.hospital.local/docs/storage/bridge_document_cards_13',395,'',547,'https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=23&item_id=6','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=23&item_id=6',834,837);
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
) ENGINE=InnoDB AUTO_INCREMENT=155 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(14,3,182,389),
(15,3,235,404),
(17,3,276,393),
(18,3,238,409),
(19,3,183,383),
(29,2,240,9),
(30,3,240,10),
(31,5,240,11),
(34,6,240,13),
(43,2,186,400),
(44,2,281,547),
(146,6,186,400),
(147,6,281,547),
(148,5,186,400),
(149,5,281,547),
(150,3,186,400),
(151,3,281,547),
(152,4,281,547),
(153,1,186,400),
(154,1,281,547);
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_24`
--

LOCK TABLES `app_entity_24` WRITE;
/*!40000 ALTER TABLE `app_entity_24` DISABLE KEYS */;
INSERT INTO `app_entity_24` VALUES
(1,0,0,0,1774335600,1774785670,1,0,'Согласование шаблона приказа по пилотному запуску','<p>Обсуждение используется как демонстрация внутренней координации: комментарии руководителя, канцелярии и исполнителя по одному документу.</p>','751',''),
(2,0,0,0,1774422000,1774600896,2,0,'Замечания к регламенту согласования учебных документов','<p>Обсуждение для показа совместной проработки документа: руководитель фиксирует замечания, канцелярия уточняет регистрацию, исполнитель вносит правки.</p>','750',''),
(3,0,0,0,1774508400,1774785670,3,0,'Переход сотрудников на совместное редактирование документов','<p>Обсуждение сценария работы в ONLYOFFICE: кто редактирует черновик, как передавать итоговую версию в NauDoc и кто контролирует публикацию.</p>','751',''),
(4,0,0,0,1774422000,1774785670,2,0,'Замечания к регламенту согласования внутренних документов','<p>Обсуждение для показа совместной проработки документа: руководитель фиксирует замечания, канцелярия уточняет регистрацию, исполнитель вносит правки.</p>','750','');
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
  `field_282` text NOT NULL,
  `field_288` varchar(255) NOT NULL,
  `field_289` varchar(255) NOT NULL,
  `field_294` int(11) NOT NULL,
  `field_299` int(11) NOT NULL,
  `field_300` int(11) NOT NULL,
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
  KEY `idx_field_252` (`field_252`(128)),
  KEY `idx_field_294` (`field_294`),
  KEY `idx_field_299` (`field_299`),
  KEY `idx_field_300` (`field_300`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_25`
--

LOCK TABLES `app_entity_25` WRITE;
/*!40000 ALTER TABLE `app_entity_25` DISABLE KEYS */;
INSERT INTO `app_entity_25` VALUES
(1,0,0,0,1774348397,1774786476,1,0,'Служебная записка о запуске пилотного контура',419,425,'СЗ-2026-001',1774076400,'1',1798700400,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_1','1','1','<p>Документ оформлен по заявке на запуск пилотного контура и используется как основной демонстрационный кейс канцелярского маршрута.</p>','','11,10,6','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=1','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=1',819,838,841),
(2,0,0,0,1774349478,1774786476,1,0,'Документ проекта: Внедрение единой платформы документооборота',421,427,'РГ-2026-004',1774162800,'1',1805698800,'1.1','https://docflow.hospital.local/docs/storage/bridge_document_cards_2','1','','<p>Карточка проектного документа используется для показа связки проект -> документ -> NauDoc и совместной работы над черновиком.</p>','','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=2','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=2',819,838,842),
(3,0,0,0,1774535702,1774690778,1,0,'Документ проекта: Подготовка регламента согласования учебных документов',421,425,'',1774535702,'2',0,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_3','2','','<p>Карточка создана автоматически из проекта #2.</p><p>Второй демонстрационный кейс: проект в стадии согласования, по нему еще нет опубликованной финальной версии в NauDoc.</p>','','','','',819,0,0),
(5,0,0,0,1774422000,1774785745,2,0,'Приказ о запуске пилотного контура',417,425,'ПР-2026-015',1774422000,'1',1798700400,'0.9','https://docflow.hospital.local/docs/storage/bridge_document_cards_5','1','','<p>Пример документа в статусе согласования. Используется для демонстрации маршрута согласования и отчета по документам, ожидающим решения.</p>','','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=5','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=5',820,838,841),
(6,0,0,0,1774422000,1774785745,5,0,'Входящий договор на сопровождение платформы',418,425,'ДГ-2026-021',1774422000,'5',1805958000,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_6','','4','<p>Пример зарегистрированного документа канцелярии. Нужен для показа регистрационного контура и работы со входящими договорами.</p>','','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=6','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=6',823,839,842),
(8,0,0,0,1773558000,1774785745,2,0,'Документ проекта: Архивирование завершенных регламентов',421,425,'АР-2026-003',1773558000,'2',1836716400,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_8','3','','<p>Пример архивного документа. Используется для показа полного цикла: создание, регистрация, завершение и перевод в архив.</p>','','','','',825,0,0),
(9,0,0,0,1774566993,1774690717,1,0,'Подключить шаблон служебной записки для кафедр',423,425,'',1774566993,'3',0,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_9','2','2','<p>Карточка создана автоматически из заявки #2.</p><p>Требуется подготовить шаблон служебной записки, дать доступ кафедрам и вывести документ в общий контур согласования.</p>','','','','',821,0,0),
(10,0,0,0,1774566993,1774690717,5,0,'Закупка принтера для регистратора канцелярии',423,425,'',1774566993,'5',0,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_10','','3','<p>Карточка создана автоматически из заявки #3.</p><p>Хозяйственная заявка на закупку принтера для рабочего места регистратора. Нужна как наглядный пример не-документного сервисного запроса.</p>','','','','',823,0,0),
(11,0,0,0,1774566993,1774690717,4,0,'Открыть доступ к шаблонам служебной записки',423,425,'',1774566993,'3',0,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_11','4','5','<p>Карточка создана автоматически из заявки #5.</p><p>Заявка от преподавателя: требуется открыть доступ к шаблонам служебных записок и инструкциям по оформлению документов.</p>','','','','',821,0,0),
(12,0,0,0,1774608827,1774690779,1,0,'Документ проекта: Подготовка регламента согласования внутренних документов',421,425,'',1774608827,'2',0,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_12','4','','<p>Карточка создана автоматически из проекта #4.</p><p>Второй демонстрационный кейс: проект в стадии согласования, по нему еще нет опубликованной финальной версии в NauDoc.</p>','','','','',819,0,0),
(13,0,0,0,1774608827,1774690717,1,0,'Подключить шаблон служебной записки для отделений',423,425,'',1774608827,'3',0,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_13','4','6','<p>Карточка создана автоматически из заявки #6.</p><p>Требуется подготовить шаблон служебной записки, дать доступ отделениям и вывести документ в общий контур согласования.</p>','','','','',821,0,0),
(14,0,0,0,1774335600,1774785745,3,0,'Рабочий документ отделения: Иван Иванов',419,425,'РД-2026-014',1774335600,'1',1798700400,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_14','','','<p>Простой рабочий документ для контрольного пользовательского сценария: открыть карточку, найти документ, запустить ONLYOFFICE, внести правку и проверить публикацию в NauDoc.</p><p>Исполнитель: Иван Иванов.</p>','','2','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=14','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=14',819,838,841),
(15,0,0,0,1774422000,1774785745,3,0,'Направление пациента: Иван Иванов',419,425,'НП-2026-021',1774422000,'1',1798700400,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_15','','','<p>Простой hospital-кейс: направление пациента оформляется в рабочем контуре, редактируется в ONLYOFFICE и получает официальный объект в NauDoc.</p><p>Пациент: Иван Иванов.</p>','','3','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=15','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=15',822,840,841),
(16,0,0,0,1774422000,1774785745,7,0,'Медицинская запись отделения: Иван Иванов',421,425,'МЗ-2026-009',1774422000,'1',1798700400,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_16','','','<p>Простой клинический документ для теста hospital-маршрута: подготовка внутренней медицинской записи отделения, совместная правка и публикация в официальный контур.</p><p>Ответственный сотрудник: Иван Иванов.</p>','','4','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=16','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=16',821,838,841),
(17,0,0,0,1774508400,1774785745,2,0,'Внутренний приказ отделения: график обходов',421,425,'ПР-2026-018',1774508400,'1',1798700400,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_17','','','<p>Внутренний приказ подразделения для теста сценария согласования и ознакомления персонала. Используется как простой понятный кейс для заведующего и сотрудников.</p>','','5','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=17','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=17',820,839,841),
(18,0,0,0,1774594800,1774785745,2,0,'Таблица дежурств отделения: апрель 2026',421,425,'ТА-2026-022',1774594800,'1',1798700400,'1.0','https://docflow.hospital.local/docs/storage/bridge_document_cards_18','','','<p>Контрольная таблица отделения для проверки ONLYOFFICE Spreadsheet Editor: открыть карточку, запустить таблицу, изменить значение, сохранить и убедиться, что совместная работа не ломается.</p><p>Сценарий удобен для заведующего и старшей медсестры.</p>','','7','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=25&item_id=18','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=25&item_id=18',820,838,841);
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
) ENGINE=InnoDB AUTO_INCREMENT=4337 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(17,3,243,421),
(19,3,247,2),
(20,3,251,2),
(58,4,244,425),
(66,8,247,2),
(67,8,244,425),
(81,9,243,423),
(83,9,247,3),
(84,9,251,2),
(85,9,252,2),
(86,10,243,423),
(88,10,247,5),
(89,10,252,3),
(90,11,243,423),
(92,11,247,3),
(94,11,252,5),
(98,11,251,4),
(99,12,243,421),
(101,12,247,2),
(102,12,251,4),
(104,13,243,423),
(106,13,247,3),
(107,13,251,4),
(108,13,252,6),
(113,12,244,425),
(114,3,244,425),
(116,13,244,425),
(117,11,244,425),
(118,10,244,425),
(119,9,244,425),
(823,9,294,821),
(824,10,294,823),
(825,11,294,821),
(826,13,294,821),
(831,3,294,819),
(832,8,294,825),
(833,12,294,819),
(4283,1,251,1),
(4286,6,244,425),
(4287,18,244,425),
(4288,17,244,425),
(4289,16,244,425),
(4290,15,244,425),
(4291,14,244,425),
(4334,2,244,427),
(4336,1,244,425);
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
  `field_290` varchar(255) NOT NULL,
  `field_291` varchar(255) NOT NULL,
  `field_301` int(11) NOT NULL,
  `field_302` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_field_256` (`field_256`),
  KEY `idx_field_257` (`field_257`),
  KEY `idx_field_259` (`field_259`(128)),
  KEY `idx_field_260` (`field_260`),
  KEY `idx_field_262` (`field_262`(128)),
  KEY `idx_field_301` (`field_301`),
  KEY `idx_field_302` (`field_302`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_26`
--

LOCK TABLES `app_entity_26` WRITE;
/*!40000 ALTER TABLE `app_entity_26` DISABLE KEYS */;
INSERT INTO `app_entity_26` VALUES
(1,0,0,0,1774365718,1774785670,1,0,'Регламент совместной работы с документами',755,758,'1.1','5',1788246000,'https://docflow.hospital.local/docs','','<p>Нормативный материал для пользователей платформы: сценарий подготовки документа, согласование, публикация и архив.</p>','1774365715_3.3.1-тд.docx','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=26&item_id=1','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=26&item_id=1',844,847),
(2,0,0,0,1774335600,1774600896,5,0,'Шаблон служебной записки для кафедр',754,758,'2.0','5',1790838000,'https://localhost:18443/docs','шаблон,кафедра,служебная записка','<p>Готовый шаблон, который преподаватели и сотрудники используют для подготовки служебных записок внутри платформы.</p>','','','',0,0),
(3,0,0,0,1774335600,1774785670,2,0,'Инструкция для руководителя по согласованию документов',755,758,'1.3','2',1794726000,'https://docflow.hospital.local/docs','руководитель,согласование,инструкция','<p>Краткая инструкция для руководителей: как открыть документ, согласовать версию, оставить замечания и контролировать публикацию.</p>','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=26&item_id=3','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=26&item_id=3',844,847),
(4,0,0,0,1774422000,1774785670,1,0,'Матрица ролей и маршрутов документов',756,759,'0.8','1',1786777200,'https://docflow.hospital.local/docs','роли,маршруты,документооборот','<p>Рабочий методический материал с ролями, маршрутами согласования и зонами ответственности по документам.</p>','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=26&item_id=4','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=26&item_id=4',844,847),
(5,0,0,0,1774335600,1774785670,5,0,'Шаблон служебной записки для отделений',754,758,'2.0','5',1790838000,'https://docflow.hospital.local/docs','шаблон,отделение,служебная записка','<p>Готовый шаблон, который врачи и сотрудники используют для подготовки служебных записок внутри платформы.</p>','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=26&item_id=5','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=26&item_id=5',844,847),
(6,0,0,0,1774335600,1774785670,3,0,'Простой шаблон документа: Иван Иванов',754,758,'1.0','3',1798700400,'https://docflow.hospital.local/docs','тест,иван иванов,простой шаблон','<p>Обычный рабочий шаблон для быстрой подготовки документа. Можно открыть, скопировать как основу, заполнить данными пациента или подразделения и передать в согласование.</p><p>Пример исполнителя: Иван Иванов.</p>','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=26&item_id=6','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=26&item_id=6',844,847),
(7,0,0,0,1774422000,1774785670,3,0,'Шаблон направления пациента',754,758,'1.0','3',1798700400,'https://docflow.hospital.local/docs','пациент,направление,врач','<p>Простой шаблон направления пациента для hospital pilot. Используется как основа для теста сценария врача: заполнить, согласовать и передать в официальный контур.</p>','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=26&item_id=7','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=26&item_id=7',845,847),
(8,0,0,0,1774422000,1774785670,7,0,'Шаблон медицинской записи отделения',754,758,'1.0','3',1798700400,'https://docflow.hospital.local/docs','медицинская запись,отделение,врач','<p>Шаблон внутренней медицинской записи отделения. Подходит для быстрого теста ввода данных, редактирования и хранения медицинской служебной документации.</p>','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=26&item_id=8','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=26&item_id=8',843,847),
(9,0,0,0,1774508400,1774785670,2,0,'Шаблон внутреннего приказа отделения',756,759,'1.0','2',1798700400,'https://docflow.hospital.local/docs','приказ,отделение,руководитель','<p>Шаблон внутреннего приказа подразделения. Используется для теста маршрута руководителя: подготовить документ, утвердить и довести до сотрудников.</p>','','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=26&item_id=9','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=26&item_id=9',844,847);
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_26_values`
--

LOCK TABLES `app_entity_26_values` WRITE;
/*!40000 ALTER TABLE `app_entity_26_values` DISABLE KEYS */;
INSERT INTO `app_entity_26_values` VALUES
(1,1,257,758),
(2,1,256,754),
(3,1,262,783);
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
  `field_292` varchar(255) NOT NULL,
  `field_293` varchar(255) NOT NULL,
  `field_303` int(11) NOT NULL,
  `field_304` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_parent_item_id` (`parent_item_id`),
  KEY `idx_created_by` (`created_by`),
  KEY `idx_field_266` (`field_266`),
  KEY `idx_field_268` (`field_268`),
  KEY `idx_field_269` (`field_269`),
  KEY `idx_field_270` (`field_270`(128)),
  KEY `idx_field_271` (`field_271`),
  KEY `idx_field_272` (`field_272`(128)),
  KEY `idx_field_303` (`field_303`),
  KEY `idx_field_304` (`field_304`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_entity_27`
--

LOCK TABLES `app_entity_27` WRITE;
/*!40000 ALTER TABLE `app_entity_27` DISABLE KEYS */;
INSERT INTO `app_entity_27` VALUES
(1,0,0,0,1774162800,1774785670,1,0,'Оснащение канцелярии МФУ и расходными материалами',761,'2',774,779,'5',1775372400,'1','https://docflow.hospital.local/docs','<p>Контрольный кейс по обеспечению: заявка связана с проектом внедрения и показывает отдельный процесс МТЗ.</p>','','767','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=27&item_id=1','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=27&item_id=1',849,851),
(2,0,0,0,1774249200,1774785670,5,0,'Сканер для оцифровки входящих документов',762,'1',775,780,'5',1775631600,'4','https://docflow.hospital.local/docs','<p>Пример заказа оборудования: позиция согласована и уже заказана, чтобы показывать разные статусы обеспечения.</p>','','5','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=27&item_id=2','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=27&item_id=2',849,851),
(3,0,0,0,1774335600,1774785670,2,0,'Лицензии ONLYOFFICE для совместного редактирования',765,'30',774,778,'2',1775977200,'1','https://docflow.hospital.local/docs','<p>Пример заявки на программное обеспечение. Используется для показа сценария закупки лицензий и связи с проектом цифровизации.</p>','','2','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=docspace&entity_id=27&item_id=3','https://docflow.hospital.local/index.php?module=dashboard/ecosystem&service=workspace&entity_id=27&item_id=3',848,851);
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
) ENGINE=InnoDB AUTO_INCREMENT=305 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(182,23,28,0,'','fieldtype_grouped_users','Инициатор / подразделение','',0,'','',0,'','',1,'','',0,1,4,1,1),
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
(226,21,25,0,'','fieldtype_users','Заведующий / куратор подразделения','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',2,1,7,1,4),
(227,21,24,0,'','fieldtype_dropdown','Подразделение / отделение','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',3,1,5,0,0),
(228,21,33,0,'','fieldtype_input_date','Плановая дата завершения','',0,'','',0,'','',0,'','',0,1,9,1,5),
(229,21,33,0,'','fieldtype_progress','Прогресс','',0,'','',0,'','',0,'','{\"step\":\"5\",\"display_progress_bar\":\"1\",\"bar_color\":\"#214f8b\"}',1,1,10,1,6),
(230,21,33,0,'','fieldtype_input_url','Ссылка на NauDoc','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть документ\"}',2,0,0,0,0),
(231,21,33,0,'','fieldtype_textarea','Комментарий руководителя','',0,'','',0,'','',0,'','',9,0,0,0,0),
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
(245,25,30,0,'','fieldtype_input','Регистрационный номер','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',2,1,6,0,0),
(246,25,30,0,'','fieldtype_input_date','Дата документа','',0,'','',0,'','',0,'','',3,1,7,0,0),
(247,25,30,0,'','fieldtype_users','Ответственный','',0,'','',0,'','',0,'','{\"display_as\":\"dropdown\",\"allow_search\":\"1\"}',4,1,8,0,0),
(248,25,35,0,'','fieldtype_input_date','Срок действия','',0,'','',0,'','',0,'','',1,1,8,0,0),
(249,25,35,0,'','fieldtype_input','Версия','',0,'','',0,'','',0,'','{\"width\":\"input-medium\"}',2,0,0,0,0),
(250,25,35,0,'','fieldtype_input_url','Ссылка на NauDoc','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть документ\"}',3,0,0,0,0),
(251,25,35,0,'','fieldtype_entity','Связанный проект','',0,'','',0,'','',0,'','{\"entity_id\":21,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',8,1,11,0,0),
(252,25,35,0,'','fieldtype_entity','Связанная заявка','',0,'','',0,'','',0,'','{\"entity_id\":23,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',9,1,12,0,0),
(253,25,30,0,'','fieldtype_textarea_wysiwyg','Описание','',0,'','',0,'','',0,'','{\"allow_search\":\"1\"}',5,0,0,0,0),
(254,25,30,0,'','fieldtype_attachments','Вложения','',0,'','',0,'','',0,'','',7,0,0,0,0),
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
(277,23,34,0,'','fieldtype_textarea','Результат исполнения','',0,'','',0,'','',0,'','',12,0,0,0,0),
(278,27,32,0,'','fieldtype_grouped_users','Инициатор / группа','',0,'','',0,'','',1,'','',0,1,6,0,0),
(279,21,33,0,'','fieldtype_entity','Связанная карточка документа','',0,'','',0,'','',0,'','{\"entity_id\":25,\"display_as\":\"dropdown\",\"width\":\"input-large\",\"allow_search\":\"1\",\"display_as_link\":\"1\"}',7,1,13,0,0),
(280,21,33,0,'','fieldtype_dropdown','Статус документа / интеграции','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',8,1,14,0,0),
(281,23,34,0,'','fieldtype_dropdown','Статус документа / интеграции','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',11,1,12,0,0),
(282,25,30,0,'','fieldtype_onlyoffice','Совместное редактирование','',0,'','',0,'','',0,'','{\"url_to_js_api\":\"https://docflow.hospital.local/office/web-apps/apps/api/documents/api.js\",\"secret_key\":\"de7f1362c0711d000b0cd0365a6684ca3115428602519889ef653f0a97f9fc31\",\"allow_edit\":\"users_edit_access\",\"lang\":\"ru\",\"location\":\"ru\",\"region\":\"ru-RU\",\"allow_change_file_name\":\"1\",\"upload_limit\":\"1\",\"upload_size_limit\":\"64\",\"allowed_extensions\":[\".docx\",\".xlsx\",\".pptx\",\".odt\",\".ods\",\".odp\",\".txt\"],\"display_date_added\":\"1\"}',6,0,0,0,0),
(284,21,33,0,'','fieldtype_input_url','Комната DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть комнату\"}',3,0,0,0,0),
(285,21,33,0,'','fieldtype_input_url','Сервис Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть сервис\"}',5,0,0,0,0),
(286,23,34,0,'','fieldtype_input_url','Комната DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть комнату\"}',7,0,0,0,0),
(287,23,34,0,'','fieldtype_input_url','Сервис Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть сервис\"}',9,0,0,0,0),
(288,25,35,0,'','fieldtype_input_url','Комната DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть комнату\"}',4,0,0,0,0),
(289,25,35,0,'','fieldtype_input_url','Сервис Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть сервис\"}',6,0,0,0,0),
(290,26,36,0,'','fieldtype_input_url','Комната DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть комнату\"}',5,0,0,0,0),
(291,26,36,0,'','fieldtype_input_url','Сервис Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть сервис\"}',7,0,0,0,0),
(292,27,37,0,'','fieldtype_input_url','Комната DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть комнату\"}',5,0,0,0,0),
(293,27,37,0,'','fieldtype_input_url','Сервис Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-xlarge\",\"target\":\"_blank\",\"preview_text\":\"Открыть сервис\"}',7,0,0,0,0),
(294,25,35,0,'','fieldtype_dropdown','Маршрут документа','',0,'','',0,'','',1,'','{\"width\":\"input-large\"}',1,1,5,0,0),
(295,21,33,0,'','fieldtype_dropdown','Сценарий DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',4,0,0,0,0),
(296,21,33,0,'','fieldtype_dropdown','Модуль Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',6,0,0,0,0),
(297,23,34,0,'','fieldtype_dropdown','Сценарий DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',8,0,0,0,0),
(298,23,34,0,'','fieldtype_dropdown','Модуль Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',10,0,0,0,0),
(299,25,35,0,'','fieldtype_dropdown','Сценарий DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',5,0,0,0,0),
(300,25,35,0,'','fieldtype_dropdown','Модуль Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',7,0,0,0,0),
(301,26,36,0,'','fieldtype_dropdown','Сценарий DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',6,0,0,0,0),
(302,26,36,0,'','fieldtype_dropdown','Модуль Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',8,0,0,0,0),
(303,27,37,0,'','fieldtype_dropdown','Сценарий DocSpace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',6,0,0,0,0),
(304,27,37,0,'','fieldtype_dropdown','Модуль Workspace','',0,'','',0,'','',0,'','{\"width\":\"input-large\"}',8,0,0,0,0);
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
) ENGINE=InnoDB AUTO_INCREMENT=562 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_fields_access`
--

LOCK TABLES `app_fields_access` WRITE;
/*!40000 ALTER TABLE `app_fields_access` DISABLE KEYS */;
INSERT INTO `app_fields_access` VALUES
(488,5,21,231,'view_inform'),
(489,8,21,231,'view_inform'),
(490,6,23,186,'view_inform'),
(491,6,23,236,'view_inform'),
(492,6,23,237,'view_inform'),
(493,6,23,238,'view_inform'),
(494,6,23,239,'view_inform'),
(495,6,23,240,'view_inform'),
(496,6,23,241,'view_inform'),
(497,6,23,281,'view_inform'),
(498,6,23,277,'view_inform'),
(499,6,25,244,'view_inform'),
(500,6,25,245,'view_inform'),
(501,6,25,249,'view_inform'),
(502,6,25,250,'view_inform'),
(503,4,21,284,'hide'),
(504,4,21,285,'hide'),
(505,4,23,286,'hide'),
(506,4,23,287,'hide'),
(507,4,25,288,'hide'),
(508,4,25,289,'hide'),
(509,4,26,290,'hide'),
(510,4,26,291,'hide'),
(511,4,27,292,'hide'),
(512,4,27,293,'hide'),
(513,5,21,284,'hide'),
(514,5,21,285,'hide'),
(515,5,23,286,'hide'),
(516,5,23,287,'hide'),
(517,5,25,288,'hide'),
(518,5,25,289,'hide'),
(519,5,26,290,'hide'),
(520,5,26,291,'hide'),
(521,5,27,292,'hide'),
(522,5,27,293,'hide'),
(523,8,21,284,'hide'),
(524,8,21,285,'hide'),
(525,8,23,286,'hide'),
(526,8,23,287,'hide'),
(527,8,25,288,'hide'),
(528,8,25,289,'hide'),
(529,8,26,290,'hide'),
(530,8,26,291,'hide'),
(531,8,27,292,'hide'),
(532,8,27,293,'hide'),
(533,6,21,284,'hide'),
(534,6,21,285,'hide'),
(535,6,23,286,'hide'),
(536,6,23,287,'hide'),
(537,6,25,288,'hide'),
(538,6,25,289,'hide'),
(539,6,26,290,'hide'),
(540,6,26,291,'hide'),
(541,6,27,292,'hide'),
(542,6,27,293,'hide'),
(543,7,21,284,'hide'),
(544,7,21,285,'hide'),
(545,7,23,286,'hide'),
(546,7,23,287,'hide'),
(547,7,25,288,'hide'),
(548,7,25,289,'hide'),
(549,7,26,290,'hide'),
(550,7,26,291,'hide'),
(551,7,27,292,'hide'),
(552,7,27,293,'hide'),
(553,7,21,160,'hide'),
(554,7,21,161,'hide'),
(555,7,21,231,'hide'),
(556,7,22,173,'hide'),
(557,7,22,174,'hide'),
(558,7,23,235,'hide'),
(559,7,23,238,'hide'),
(560,7,23,277,'hide'),
(561,7,27,274,'hide');
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
) ENGINE=InnoDB AUTO_INCREMENT=853 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_fields_choices`
--

LOCK TABLES `app_fields_choices` WRITE;
/*!40000 ALTER TABLE `app_fields_choices` DISABLE KEYS */;
INSERT INTO `app_fields_choices` VALUES
(382,0,183,1,'Техническая поддержка','',0,'#bde0fe',1,'','',''),
(383,0,183,1,'Медицинская документация','',1,'#bde0fe',1,'','',''),
(384,0,183,1,'Хозяйственный запрос','',0,'#ffe5b4',3,'','',''),
(385,0,183,1,'Документооборот','',0,'#ffd6a5',4,'','',''),
(386,0,183,1,'Доступ / учетная запись','',0,'#d8f3dc',5,'','',''),
(387,0,182,1,'Администрация','',1,'#d8e2dc',1,'1','',''),
(388,0,182,1,'Поликлиника','',0,'#bee1e6',2,'1','',''),
(389,0,182,1,'Стационар','',0,'#cdb4db',3,'1','',''),
(390,0,182,1,'Приемное отделение','',0,'#ffc8dd',4,'1','',''),
(391,0,182,1,'ИТ и хозслужба','',0,'#bde0fe',5,'1','',''),
(392,0,182,1,'Хозяйственная служба / снабжение','',0,'#ffe5b4',6,'1','',''),
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
(409,0,238,1,'ИТ и доступ','',0,'',3,'','',''),
(410,0,238,1,'Документы и регистрация','',1,'',1,'','',''),
(411,0,238,1,'Медицинские процессы','',0,'',2,'','',''),
(412,0,238,1,'АХО / МТЗ','',0,'',4,'','',''),
(413,0,238,1,'Административное обслуживание','',0,'',5,'','',''),
(417,0,243,1,'Приказ','',0,'#cce3de',6,'','',''),
(418,0,243,1,'Договор','',0,'#cdb4db',7,'','',''),
(419,0,243,1,'Служебная записка','',0,'#ffd6a5',5,'','',''),
(420,0,243,1,'Заявление','',0,'#ffddd2',10,'','',''),
(421,0,243,1,'Регламент','',0,'#ffcad4',9,'','',''),
(422,0,243,1,'Акт','',0,'#ffe5b4',8,'','',''),
(423,0,243,1,'Иное','',0,'#adb5bd',11,'','',''),
(424,0,244,1,'Черновик','',1,'#dee2e6',1,'','',''),
(425,0,244,1,'На согласовании','',0,'#ffd166',2,'','',''),
(426,0,244,1,'На утверждении','',0,'#ffddd2',3,'','',''),
(427,0,244,1,'Подписан','',0,'#95d5b2',4,'','',''),
(428,0,244,1,'На ознакомлении','',0,'#bde0fe',5,'','',''),
(429,0,244,1,'Архивирован','',0,'#adb5bd',8,'','',''),
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
(471,0,227,1,'Поликлиника','',0,'#bee1e6',2,'','',''),
(472,0,227,1,'Стационар','',0,'#cdb4db',3,'','',''),
(473,0,227,1,'Приемное отделение','',0,'#ffc8dd',4,'','',''),
(474,0,227,1,'ИТ и хозслужба','',0,'#bde0fe',5,'','',''),
(475,0,227,1,'Хозяйственная служба / снабжение','',0,'#ffe5b4',6,'','',''),
(523,0,280,1,'Ожидает документ','',1,'#dee2e6',1,'','',''),
(524,0,280,1,'Связано','',0,'#bde0fe',2,'','',''),
(525,0,280,1,'Черновик','',0,'#c9d6ea',3,'','',''),
(526,0,280,1,'На согласовании','',0,'#ffd166',4,'','',''),
(527,0,280,1,'На утверждении','',0,'#ffddd2',5,'','',''),
(528,0,280,1,'Подписан','',0,'#95d5b2',6,'','',''),
(529,0,280,1,'На ознакомлении','',0,'#bde0fe',7,'','',''),
(530,0,280,1,'Архивирован','',0,'#adb5bd',9,'','',''),
(531,0,280,1,'Ошибка синхронизации','',0,'#d90429',10,'','',''),
(546,0,281,1,'Ожидает документ','',1,'#dee2e6',1,'','',''),
(547,0,281,1,'Связано','',0,'#bde0fe',2,'','',''),
(548,0,281,1,'Черновик','',0,'#c9d6ea',3,'','',''),
(549,0,281,1,'На согласовании','',0,'#ffd166',4,'','',''),
(550,0,281,1,'На утверждении','',0,'#ffddd2',5,'','',''),
(551,0,281,1,'Подписан','',0,'#95d5b2',6,'','',''),
(552,0,281,1,'На ознакомлении','',0,'#bde0fe',7,'','',''),
(553,0,281,1,'Архивирован','',0,'#adb5bd',9,'','',''),
(554,0,281,1,'Ошибка синхронизации','',0,'#d90429',10,'','',''),
(635,0,280,1,'Зарегистрирован','',0,'#cce3de',8,'','',''),
(650,0,281,1,'Зарегистрирован','',0,'#cce3de',8,'','',''),
(654,0,243,1,'Входящий документ','',0,'#d8f3dc',1,'','',''),
(655,0,243,1,'Исходящий документ','',0,'#bde0fe',2,'','',''),
(656,0,243,1,'Внутренний документ','',1,'#e9ecef',3,'','',''),
(657,0,244,1,'На регистрации','',0,'#f8edeb',6,'','',''),
(658,0,244,1,'Зарегистрирован','',0,'#cce3de',7,'','',''),
(750,0,193,1,'Открыто','',1,'#bde0fe',1,'','',''),
(751,0,193,1,'В работе','',0,'#ffd166',2,'','',''),
(752,0,193,1,'Закрыто','',0,'#95d5b2',3,'','',''),
(753,0,256,1,'Регламент','',0,'#cdb4db',1,'','',''),
(754,0,256,1,'Шаблон','',0,'#bde0fe',2,'','',''),
(755,0,256,1,'Инструкция','',0,'#ffd6a5',3,'','',''),
(756,0,256,1,'Методический материал','',0,'#d8f3dc',4,'','',''),
(757,0,256,1,'Архивный материал','',0,'#dee2e6',5,'','',''),
(758,0,257,1,'Действует','',1,'#95d5b2',1,'','',''),
(759,0,257,1,'На пересмотре','',0,'#ffd166',2,'','',''),
(760,0,257,1,'Архив','',0,'#adb5bd',3,'','',''),
(761,0,266,1,'Канцелярия','',1,'#ffe5b4',1,'','',''),
(762,0,266,1,'Компьютерная техника','',0,'#bde0fe',2,'','',''),
(763,0,266,1,'Мебель','',0,'#d8f3dc',3,'','',''),
(764,0,266,1,'Расходные материалы','',0,'#ffd6a5',4,'','',''),
(765,0,266,1,'Программное обеспечение','',0,'#cdb4db',5,'','',''),
(766,0,266,1,'Иное','',0,'#dee2e6',6,'','',''),
(767,0,278,1,'Администрация','',1,'#d8e2dc',1,'1','',''),
(768,0,278,1,'Поликлиника','',0,'#bee1e6',2,'1','',''),
(769,0,278,1,'Стационар','',0,'#cdb4db',3,'1','',''),
(770,0,278,1,'Приемное отделение','',0,'#ffc8dd',4,'1','',''),
(771,0,278,1,'ИТ и хозслужба','',0,'#bde0fe',5,'1','',''),
(772,0,278,1,'Хозяйственная служба / снабжение','',0,'#ffe5b4',6,'1','',''),
(773,0,268,1,'Критичный','',0,'#d90429',1,'','',''),
(774,0,268,1,'Высокий','',0,'#f77f00',2,'','',''),
(775,0,268,1,'Средний','',1,'#fcbf49',3,'','',''),
(776,0,268,1,'Низкий','',0,'#3a86ff',4,'','',''),
(777,0,269,1,'Новая','',1,'#dee2e6',1,'','',''),
(778,0,269,1,'На согласовании','',0,'#ffd166',2,'','',''),
(779,0,269,1,'В закупке','',0,'#bde0fe',3,'','',''),
(780,0,269,1,'Заказано','',0,'#ffddd2',4,'','',''),
(781,0,269,1,'Получено','',0,'#95d5b2',5,'','',''),
(782,0,269,1,'Отклонена','',0,'#adb5bd',6,'','',''),
(783,0,262,1,'1','',NULL,'',NULL,'','',''),
(798,0,167,1,'Поручение','',1,'#d8f3dc',1,'','',''),
(799,0,167,1,'Согласование','',0,'#ffd166',2,'','',''),
(800,0,167,1,'Подготовка документа','',0,'#bde0fe',3,'','',''),
(801,0,167,1,'Контроль исполнения','',0,'#f8edeb',4,'','',''),
(802,0,169,1,'Новая','',1,'#dee2e6',1,'','',''),
(803,0,169,1,'В работе','',0,'#8ecae6',2,'','',''),
(804,0,169,1,'На согласовании','',0,'#ffd166',3,'','',''),
(805,0,169,1,'На проверке','',0,'#ffddd2',4,'','',''),
(806,0,169,1,'Выполнена','',0,'#95d5b2',5,'','',''),
(807,0,169,1,'Отменена','',0,'#adb5bd',6,'','',''),
(808,0,170,1,'Критичный','',0,'#d90429',1,'','',''),
(809,0,170,1,'Высокий','',0,'#f77f00',2,'','',''),
(810,0,170,1,'Средний','',1,'#fcbf49',3,'','',''),
(811,0,170,1,'Низкий','',0,'#3a86ff',4,'','',''),
(812,0,227,1,'Регистратура','',0,'#d8f3dc',7,'','',''),
(813,0,227,1,'Канцелярия','',0,'#f8edeb',8,'','',''),
(814,0,183,1,'Кадровый вопрос','',0,'#f8edeb',6,'','',''),
(815,0,182,1,'Регистратура','',0,'#d8f3dc',7,'1','',''),
(816,0,182,1,'Канцелярия','',0,'#f8edeb',8,'1','',''),
(817,0,243,1,'Медицинский документ','',0,'#f8edeb',4,'','',''),
(818,0,294,1,'Входящая регистрация','',0,'#d8f3dc',1,'','',''),
(819,0,294,1,'Исходящее письмо / согласование','',0,'#bde0fe',2,'','',''),
(820,0,294,1,'Внутренний приказ / распоряжение','',1,'#e9ecef',3,'','',''),
(821,0,294,1,'Медицинская документация отделения','',0,'#f8edeb',4,'','',''),
(822,0,294,1,'Пациент / направление / выписка','',0,'#ffd6a5',5,'','',''),
(823,0,294,1,'Договор / закупка / МТЗ','',0,'#cdb4db',6,'','',''),
(824,0,294,1,'Ознакомление персонала','',0,'#cce3de',7,'','',''),
(825,0,294,1,'Архив / закрытие','',0,'#adb5bd',8,'','',''),
(826,0,278,1,'Регистратура','',0,'#d8f3dc',7,'1','',''),
(827,0,278,1,'Канцелярия','',0,'#f8edeb',8,'1','',''),
(828,0,295,1,'Collaboration room','',1,'#bde0fe',1,'','',''),
(829,0,295,1,'Public room','',0,'#d8f3dc',2,'','',''),
(830,0,295,1,'Form filling room','',0,'#ffe5b4',3,'','',''),
(831,0,296,1,'Calendar','',1,'#cdb4db',1,'','',''),
(832,0,296,1,'Community','',0,'#bee1e6',2,'','',''),
(833,0,297,1,'Collaboration room','',0,'#bde0fe',1,'','',''),
(834,0,297,1,'Public room','',0,'#d8f3dc',2,'','',''),
(835,0,297,1,'Form filling room','',1,'#ffe5b4',3,'','',''),
(836,0,298,1,'Calendar','',1,'#cdb4db',1,'','',''),
(837,0,298,1,'Community','',0,'#bee1e6',2,'','',''),
(838,0,299,1,'Collaboration room','',1,'#bde0fe',1,'','',''),
(839,0,299,1,'Public room','',0,'#d8f3dc',2,'','',''),
(840,0,299,1,'Form filling room','',0,'#ffe5b4',3,'','',''),
(841,0,300,1,'Calendar','',1,'#cdb4db',1,'','',''),
(842,0,300,1,'Community','',0,'#bee1e6',2,'','',''),
(843,0,301,1,'Collaboration room','',0,'#bde0fe',1,'','',''),
(844,0,301,1,'Public room','',1,'#d8f3dc',2,'','',''),
(845,0,301,1,'Form filling room','',0,'#ffe5b4',3,'','',''),
(846,0,302,1,'Calendar','',0,'#cdb4db',1,'','',''),
(847,0,302,1,'Community','',1,'#bee1e6',2,'','',''),
(848,0,303,1,'Collaboration room','',0,'#bde0fe',1,'','',''),
(849,0,303,1,'Public room','',1,'#d8f3dc',2,'','',''),
(850,0,303,1,'Form filling room','',0,'#ffe5b4',3,'','',''),
(851,0,304,1,'Calendar','',1,'#cdb4db',1,'','',''),
(852,0,304,1,'Community','',0,'#bee1e6',2,'','','');
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(5,27,'common_report_filters_panel_82',1,1,'horizontal','',0,0),
(6,23,'common_report_filters_panel_89',1,1,'horizontal','',0,0),
(7,21,'common_report_filters_panel_90',1,1,'horizontal','',0,0),
(8,25,'common_report_filters_panel_91',1,1,'horizontal','',0,0),
(9,24,'common_report_filters_panel_307',1,1,'horizontal','',0,0);
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
(25,21,0,0,'Ответственные и роли','','','',1),
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_onlyoffice_files`
--

LOCK TABLES `app_onlyoffice_files` WRITE;
/*!40000 ALTER TABLE `app_onlyoffice_files` DISABLE KEYS */;
INSERT INTO `app_onlyoffice_files` VALUES
(1,25,282,'','pilot-onlyoffice.docx',0,'25/2026/03/28/1','docflow.hospital.local-1-1774710075','',1774365174,1),
(2,25,282,'','ivan-ivanov-test.docx',0,'25/2026/03/29/2','docflow.hospital.local-2-1774786438','E8oob9oTZNV1',1774705489,1),
(3,25,282,'','patient-route-ivan-ivanov.docx',0,'25/2026/03/29/3','docflow.hospital.local-3-1774785667','',1774706097,1),
(4,25,282,'','clinical-note-ivan-ivanov.docx',0,'25/2026/03/29/4','docflow.hospital.local-4-1774785667','',1774706097,1),
(5,25,282,'','internal-order-rounds.docx',0,'25/2026/03/29/5','docflow.hospital.local-5-1774785667','',1774706098,1),
(6,25,282,'','hospital-reference-document.docx',0,'25/2026/03/28/6','rukovoditel-6-1774727468','',1774715640,1),
(7,25,282,'','duty-schedule-april-2026.xlsx',0,'25/2026/03/29/7','docflow.hospital.local-7-1774786439','O4RgVWoSwYT8',1774721059,1),
(10,25,282,'','blank-spreadsheet-20260328-214529.xlsx',0,'25/2026/03/28/10','docflow.hospital.local-10-1774723529','',1774723529,1),
(11,25,282,'','blank-document-20260328-214707.docx',0,'25/2026/03/28/11','rukovoditel-11-1774726347','',1774723627,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_portlets`
--

LOCK TABLES `app_portlets` WRITE;
/*!40000 ALTER TABLE `app_portlets` DISABLE KEYS */;
INSERT INTO `app_portlets` VALUES
(1,'filters_preview_74',1,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=859 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(78,0,22,0,'common','Мои задачи в работе','Задачи и поручения, которые требуют моего внимания прямо сейчас.','fa fa-check-square-o','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,10,0,10,'','0,4,5,8,6','',1,0,0,'',0,'','','',''),
(79,0,23,0,'common','Мои заявки','Собственные заявки и обращения, которые еще находятся в работе.','fa fa-life-ring','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,20,0,20,'','0,4,5,8,6','',1,0,0,'',0,'','','',''),
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
(90,0,21,0,'common','Проекты с риском по документам','Проекты, где документ еще не завершен или интеграция требует внимания.','fa fa-warning','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,35,0,35,'','0,4','',0,0,0,'',0,'','','',''),
(91,0,25,0,'common','Документы канцелярии','Документы, которые требуют регистрации, контроля завершения или передачи в архив.','fa fa-archive','','',0,1,1,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,45,0,45,'','0,7','',0,0,0,'',0,'','','',''),
(92,93,22,0,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(93,0,21,0,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(94,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(95,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(96,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(97,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(98,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(99,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(100,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(101,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(102,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(103,0,1,1,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(104,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(105,0,26,1,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(106,107,22,2,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(107,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(108,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(109,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(110,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(111,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(112,0,23,2,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(113,0,21,2,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(114,0,27,2,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(115,0,25,2,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(116,0,26,2,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(117,118,22,3,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(118,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(119,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(120,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(121,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(122,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(123,0,23,3,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(124,0,21,3,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(125,0,27,3,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(126,0,25,3,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(127,0,26,3,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(128,129,22,4,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(129,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(130,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(131,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(132,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(133,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(134,0,23,4,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(135,0,21,4,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(136,0,27,4,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(137,0,25,4,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(138,0,26,4,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(139,140,22,5,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(140,0,21,5,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(141,0,23,5,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(142,0,21,5,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(143,0,27,5,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(144,0,25,5,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(145,0,26,5,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(146,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(147,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(148,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(149,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(150,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(151,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(152,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(153,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(154,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(155,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(156,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(157,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(158,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(159,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(160,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(161,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(162,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(163,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(164,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(165,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(166,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(167,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(168,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(169,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(170,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(171,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(172,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(173,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(174,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(175,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(176,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(177,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(178,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(179,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(180,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(181,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(182,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(183,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(184,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(185,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(186,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(187,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(188,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(189,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(190,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(191,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(192,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(193,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(194,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(195,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(196,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(197,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(198,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(199,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(200,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(201,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(202,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(203,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(204,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(205,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(206,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(207,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(208,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(209,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(210,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(211,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(212,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(213,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(214,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(215,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(216,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(217,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(218,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(219,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(220,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(221,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(222,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(223,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(224,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(225,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(226,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(227,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(228,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(229,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(230,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(231,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(232,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(233,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(234,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(235,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(236,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(237,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(238,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(239,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(240,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(241,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(242,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(243,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(244,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(245,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(246,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(247,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(248,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(249,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(250,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(251,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(252,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(253,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(254,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(255,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(256,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(257,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(258,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(259,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(260,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(261,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(262,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(263,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(264,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(265,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(266,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(267,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(268,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(269,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(270,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(271,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(272,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(273,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(274,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(275,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(276,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(277,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(278,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(279,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(280,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(281,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(282,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(283,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(284,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(285,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(286,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(287,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(288,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(289,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(290,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(291,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(292,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(293,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(294,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(295,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(296,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(297,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(298,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(299,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(300,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(301,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(302,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(303,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(304,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(305,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(306,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(307,0,24,0,'common','Рабочие обсуждения','Внутренние обсуждения и договоренности по рабочим вопросам.','fa fa-comments-o','','',0,0,0,0,'#1f4f86','#f3d7ad','',0,0,0,0,0,0,0,0,'','0,4,5,8','',0,0,0,'',0,'','','',''),
(308,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(309,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(310,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(311,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(312,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(313,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(314,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(315,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(316,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(317,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(318,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(319,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(320,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(321,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(322,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(323,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(324,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(325,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(326,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(327,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(328,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(329,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(330,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(331,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(332,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(333,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(334,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(335,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(336,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(337,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(338,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(339,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(340,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(341,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(342,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(343,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(344,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(345,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(346,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(347,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(348,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(349,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(350,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(351,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(352,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(353,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(354,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(355,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(356,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(357,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(358,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(359,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(360,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(361,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(362,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(363,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(364,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(365,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(366,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(367,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(368,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(369,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(370,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(371,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(372,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(373,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(374,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(375,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(376,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(377,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(378,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(379,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(380,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(381,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(382,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(383,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(384,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(385,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(386,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(387,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(388,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(389,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(390,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(391,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(392,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(393,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(394,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(395,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(396,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(397,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(398,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(399,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(400,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(401,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(402,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(403,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(404,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(405,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(406,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(407,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(408,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(409,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(410,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(411,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(412,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(413,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(414,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(415,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(416,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(417,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(418,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(419,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(420,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(421,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(422,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(423,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(424,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(425,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(426,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(427,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(428,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(429,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(430,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(431,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(432,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(433,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(434,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(435,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(436,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(437,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(438,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(439,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(440,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(441,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(442,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(443,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(444,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(445,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(446,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(447,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(448,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(449,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(450,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(451,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(452,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(453,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(454,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(455,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(456,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(457,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(458,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(459,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(460,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(461,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(462,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(463,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(464,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(465,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(466,467,22,6,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(467,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(468,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(469,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(470,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(471,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(472,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(473,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(474,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(475,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(476,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(477,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(478,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(479,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(480,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(481,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(482,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(483,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(484,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(485,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(486,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(487,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(488,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(489,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(490,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(491,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(492,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(493,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(494,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(495,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(496,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(497,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(498,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(499,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(500,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(501,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(502,0,23,6,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(503,0,21,6,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(504,0,27,6,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(505,0,25,6,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(506,0,26,6,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(507,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(508,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(509,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(510,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(511,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(512,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(513,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(514,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(515,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(516,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(517,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(518,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(519,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(520,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(521,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(522,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(523,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(524,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(525,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(526,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(527,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(528,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(529,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(530,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(531,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(532,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(533,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(534,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(535,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(536,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(537,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(538,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(539,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(540,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(541,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(542,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(543,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(544,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(545,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(546,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(547,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(548,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(549,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(550,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(551,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(552,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(553,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(554,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(555,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(556,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(557,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(558,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(559,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(560,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(561,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(562,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(563,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(564,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(565,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(566,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(567,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(568,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(569,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(570,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(571,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(572,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(573,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(574,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(575,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(576,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(577,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(578,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(579,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(580,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(581,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(582,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(583,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(584,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(585,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(586,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(587,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(588,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(589,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(590,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(591,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(592,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(593,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(594,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(595,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(596,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(597,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(598,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(599,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(600,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(601,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(602,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(603,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(604,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(605,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(606,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(607,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(608,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(609,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(610,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(611,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(612,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(613,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(614,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(615,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(616,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(617,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(618,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(619,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(620,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(621,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(622,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(623,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(624,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(625,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(626,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(627,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(628,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(629,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(630,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(631,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(632,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(633,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(634,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(635,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(636,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(637,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(638,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(639,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(640,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(641,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(642,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(643,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(644,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(645,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(646,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(647,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(648,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(649,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(650,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(651,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(652,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(653,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(654,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(655,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(656,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(657,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(658,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(659,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(660,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(661,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(662,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(663,664,22,7,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(664,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(665,0,23,7,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(666,0,21,7,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(667,0,25,7,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(668,0,26,7,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(669,0,27,7,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(670,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(671,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(672,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(673,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(674,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(675,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(676,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(677,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(678,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(679,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(680,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(681,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(682,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(683,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(684,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(685,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(686,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(687,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(688,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(689,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(690,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(691,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(692,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(693,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(694,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(695,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(696,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(697,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(698,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(699,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(700,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(701,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(702,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(703,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(704,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(705,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(706,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(707,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(708,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(709,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(710,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(711,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(712,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(713,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(714,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(715,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(716,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(717,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(718,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(719,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(720,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(721,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(722,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(723,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(724,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(725,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(726,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(727,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(728,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(729,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(730,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(731,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(732,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(733,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(734,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(735,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(736,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(737,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(738,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(739,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(740,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(741,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(742,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(743,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(744,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(745,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(746,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(747,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(748,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(749,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(750,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(751,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(752,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(753,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(754,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(755,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(756,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(757,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(758,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(759,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(760,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(761,0,21,2,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(762,0,21,3,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(763,0,21,6,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(764,0,21,4,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(765,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(766,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(767,0,21,7,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(768,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(769,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(770,771,22,8,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(771,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(772,0,23,8,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(773,0,21,8,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(774,0,27,8,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(775,0,25,8,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(776,0,26,8,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(777,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(778,779,22,9,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(779,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(780,0,23,9,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(781,0,21,9,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(782,0,27,9,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(783,0,25,9,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(784,0,26,9,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(785,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(786,787,22,11,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(787,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(788,0,23,11,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(789,0,21,11,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(790,0,27,11,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(791,0,25,11,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(792,0,26,11,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(793,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(794,795,22,12,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(795,0,21,12,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(796,0,23,12,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(797,0,21,12,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(798,0,27,12,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(799,0,25,12,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(800,0,26,12,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(801,802,22,10,'entity_menu','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(802,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(803,0,23,10,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(804,0,21,10,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(805,0,27,10,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(806,0,25,10,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(807,0,26,10,'entity','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(808,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(809,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(810,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(811,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(812,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(813,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(814,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(815,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(816,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(817,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(818,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(819,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(820,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(821,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(822,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(823,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(824,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(825,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(826,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(827,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(828,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(829,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(830,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(831,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(832,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(833,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(834,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(835,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(836,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(837,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(838,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(839,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(840,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(841,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(842,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(843,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(844,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(845,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(846,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(847,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(848,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(849,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(850,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(851,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(852,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(853,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(854,0,21,1,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(855,0,21,8,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(856,0,21,9,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(857,0,21,11,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','',''),
(858,0,21,10,'parent','','','','','',0,0,0,0,'','','',0,0,0,0,0,NULL,0,0,'','','',0,0,0,'',0,'','','','');
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
) ENGINE=InnoDB AUTO_INCREMENT=248 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(118,92,169,'46,47,48','include',1),
(127,106,169,'46,47,48','include',1),
(128,112,186,'60,61,62','include',1),
(129,113,157,'37,38,39','include',1),
(130,117,169,'46,47,48','include',1),
(131,123,186,'60,61,62','include',1),
(132,124,157,'37,38,39','include',1),
(133,128,169,'46,47,48','include',1),
(134,134,186,'60,61,62','include',1),
(135,135,157,'37,38,39','include',1),
(136,139,169,'46,47,48','include',1),
(137,141,186,'60,61,62','include',1),
(138,142,157,'37,38,39','include',1),
(179,466,169,'46,47,48','include',1),
(180,502,186,'60,61,62','include',1),
(181,503,157,'37,38,39','include',1),
(222,663,169,'46,47,48','include',1),
(223,665,186,'60,61,62','include',1),
(224,666,157,'37,38,39','include',1),
(225,770,169,'46,47,48','include',1),
(226,772,186,'60,61,62','include',1),
(227,773,157,'37,38,39','include',1),
(228,778,169,'46,47,48','include',1),
(229,780,186,'60,61,62','include',1),
(230,781,157,'37,38,39','include',1),
(231,786,169,'46,47,48','include',1),
(232,788,186,'60,61,62','include',1),
(233,789,157,'37,38,39','include',1),
(234,794,169,'46,47,48','include',1),
(235,796,186,'60,61,62','include',1),
(236,797,157,'37,38,39','include',1),
(237,801,169,'46,47,48','include',1),
(238,803,186,'60,61,62','include',1),
(239,804,157,'37,38,39','include',1),
(240,78,169,'802,803,804,805','include',1),
(241,79,186,'397,398,399,400,401','include',1),
(242,89,281,'546,547,548,549,550,552,554','include',1),
(243,80,157,'464,465,466,467','include',1),
(244,90,280,'523,524,525,526,527,529,531','include',1),
(245,81,244,'425,426,428,657','include',1),
(246,82,269,'778,779,780','include',1),
(247,91,244,'427,428,657,658','include',1);
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
('0462a1069407aad4f3f9fbcabe8cae75',1774785068,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"v0e4A2pDzP\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('085b5807b852db49ea3f05066888a9e1',1774787902,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"mqPQIh1S8e\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"11\";'),
('08e90af506f50ea845f8bb7a4c3ba146',1774785468,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"HaDmpHW7RP\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('13cb51d91aaecb62bc47a80b4a699302',1774785468,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"SRH7frCQAV\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('1542b14f10e152bc3085cc4e8ee97d6e',1774787819,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"H9xicw5uK9\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('15bd1cc485e20c02b41d4eb7dd5d7d96',1774787879,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"oPT7Cy11q1\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}'),
('1753cf13dd9ee04d6d6a0ad087af2828',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"BEUjwuwCK7\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('19aee8b1903d33e164d2d2b29db74824',1774787819,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"CnhAjjGAZQ\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('1f4934f85c379678680109e8eb862320',1774787879,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"4NVx1K3wqv\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}'),
('20c004ec6b7f7f9c8c9cb769efa0b685',1774785895,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"a5yIa9JUWB\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('225af30d2834f11638ce58d487fc0309',1774785458,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"yO7b8B2XAD\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:1:{s:10:\"is_checked\";b:1;}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:5:\"3.6.4\";app_selected_items|a:1:{i:91;a:0:{}}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";holidays_filter|s:4:\"2026\";entities_filter|i:0;'),
('28a8363215a93a9b9b8fbbf12a330558',1774787879,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"239tzGTupY\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('2ad8e7ab78ac6ec8b3035b582c825cd2',1774785468,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"S79ffUJuX3\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('2d9adebdb1631ee0e9493bdf71bd6b9e',1774787902,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"OHCEn7FQDJ\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"8\";'),
('31f9bc4a235813c2768f6f00fa5d56dd',1774787819,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"FDiu4xHxWW\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('33b581a2bb779f37c2e1cd2b4aa9e837',1774787902,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"vssG16XP7x\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"12\";'),
('379f79d34921daf240887faa8d583bc4',1774787879,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"pu8MYAEGGh\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('38f9a6ad2d6044b9c09837d50e7f86d3',1774787014,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"NmrkfBPMFG\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('3e188f97a07145b4e8e4f6dc5be5cf71',1774785895,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"R4K5qByATq\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('3f2984f02c834aa7e6197a42785a13fa',1774787820,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"8p7f4ZEamE\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('402ecabdfbf82f629c5d9cb65280dcd7',1774785409,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"t4GI1GFZU6\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('410b18cef5b0d7292d34265e79514f8e',1774787903,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"Jw8DYgMAXK\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('41320fc649f4726158b2ca2e3736bf9a',1774785409,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"XuFhJ0F2Wk\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('43951b7fc237c58e4d2df95e5a195a44',1774785895,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"O2Bt27zP3Z\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('45dacc9add0232220d449c2543cf2b04',1774787036,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"BtO5JAoNaE\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('4abd9d6271759b539b0b9ad0363ac65b',1774787879,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"0icHcdMkW8\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('4cbbafac5bf5d712cad0a5810f8cf837',1774787903,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"KrP5obfwrw\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('4e16a15f3b3aec4e6c5eaf4cf6399818',1774787819,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"CqUySTJMRV\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('53b58803223839e553f9a7b8bf4d85be',1774785468,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"qFdOQiiMez\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('54d6773f6dcddf833c81c509e655923d',1774787660,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"sMr0No5UcV\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('55afd66ea83ea2c4e8fa0b09accff9fd',1774785895,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"1YPNqo2Mi1\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('5b4cc1a2ad3d815154c6e7b7829d0b6c',1774787900,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"RcspaqZcWg\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('5bd5bc206ff42c57d4e67e9878e5aee5',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"kfGprtv7J7\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}'),
('5cbd3550fcdcc4ac066addaaedda2e0d',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"az4ZI7zkYa\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('609e32a5e773942835ef2e6c7e49f268',1774785409,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"TzmtaGG7yN\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('61efb051902626b90b63567902d18e94',1774785480,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"3sCQ2YeBxB\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('645f33de3d0fd8a29a5f24ea77b975ea',1774787902,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"YOrOdpavnV\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('648e906fe12b2a68683485e0d067ed76',1774787879,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"uospyv0iiO\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('670c28a923182d22a5d8631146a656eb',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"j0yvqOwvcR\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('6df8fe7c30513af57d983476de251ac4',1774785895,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"Ppysww8zSW\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('722093845104dc72e393c1d1d3623528',1774785009,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"T9Jq5Y8Z47\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('754313012b9e15d24595baf6a938ba23',1774787652,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"d26hgNbZJF\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('768439a62de1b609be91a58f73a21a4f',1774787652,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"XBnnD9szYP\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('7b716ea89c00743a300a477e7e38aa73',1774785008,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"RuoE5JJFy2\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('7d53bab02969df947628b3ed22e8e25b',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"zNQbASab5C\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('7e69f5fdebe68c7c0af51553f2bcdf22',1774785106,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"DYkjdiQA5b\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('826163ca454a9946ed20d1bcf282db93',1774785895,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"jDxikmbHmX\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('84b942a6c42db18ceda9eaa14c820eaa',1774785051,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"avbxZ2fpPj\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('8530bb80ce66a712d75bc17abdbed0e6',1774787639,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"YGmeKGEcx5\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('863a157c0f6050abde032e8dbb16a16e',1774787819,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"bhTQ6W8tBE\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('870db6b0042e1448e48f2ea6d5dd8f38',1774785180,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"5qavaPGWVX\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('8b6bd1018f6235696310c120ba710f98',1774787441,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"6RCPjvyEzE\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('8d760981704c88d49a7c00da6900ddf9',1774787795,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"Ab7NXx8Hhh\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('9126678957a196d03702f274ed1b6006',1774787125,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"tfq4Z78Of3\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('9bde36796d7ee52836921b46bc061722',1774785468,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"M1VRe1KoBZ\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('9c259dc3af137c591c557144b9257327',1774785352,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"t13jyibcWm\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('9eb07355d6741a528eb061cc284d61ec',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"h8VtIFwPDV\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('9f00d6c78306bce54535059f86ce926e',1774787749,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"5BwQuDmaNC\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('a063df56076cd0303ddca7d6a95929bb',1774787723,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"HEbKzhxDgc\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('a1b5265928d68b10da04f9fb80d142f3',1774787899,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"pZu0GAYwNr\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('a3edbb8d8a8797368866ba45080b4f4d',1774785078,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"jRrFP1QtOs\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('a663a45c661d978391354342108ecc94',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"0y9CCnIqcj\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('a8bc4760d2123aaa78000dbeeec9540d',1774787901,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"OqaeD6tKki\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";entities_filter|i:0;'),
('ab31162b88098a762cc22ed08dfe679f',1774785257,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"B4xjrNVKV9\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('ac19430d13fde2ac65a3560f1af80e1b',1774787900,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"xFbCe0tGRp\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('b1b02cb35da0869a300fe870aecb6380',1774787819,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"YE2661I6RM\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('b42bb8b7fadecfa1e3dde7cb79e73835',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"ZMN8eOFUE2\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('b8ad6fa4f7d40a4004816be7f77a8799',1774787879,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"7dX9UIT57k\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}'),
('b956e7254d6ff19b6501fd371c4a225d',1774787660,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"FNPcjZ3pbp\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('bcc569f6356285b8f7b869a80042e86c',1774787652,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"I1Hp4kRV7Q\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('c230d135b47a1503db73481368838acd',1774787660,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"YhdzrAOvYp\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:2:\"10\";'),
('ce9e5acd12b5153825dec947e2ed6f05',1774785409,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"3H0CeqoNjT\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('d331cf982f1f7c569d29a4a800e8a469',1774787699,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"6TXC3xt8ho\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('d7c587125a571061b9d802a91180cfb0',1774785093,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"RBRmwQkSiw\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('e4aa5bb1ed4e98659e4b6e7a5c3406c0',1774785480,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"b3tz5Sx5JR\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('e6a64f9718d81ccc7aa44e43c7a19dca',1774785468,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"m6o0OdeJ8T\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"9\";'),
('e7626f2f1b2d052d2194cbcc2e9e4435',1774785943,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"gENSym8fOH\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:1:{s:10:\"is_checked\";b:1;}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:5:\"3.6.4\";app_selected_items|a:1:{i:91;a:0:{}}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";holidays_filter|s:4:\"2026\";entities_filter|i:0;'),
('eb830397129dde9be7f5d6760c36ddd1',1774785068,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"5ZfawT0oiH\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('f3f78d00a42bd077bac9a34e53fdbe0b',1774787061,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|N;app_send_to|N;app_session_token|s:10:\"ewapMncFf9\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;'),
('f82b380f27ec65f802cbf5d3de0c5d62',1774787878,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"E50gMAvI9W\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";'),
('f8c06e8b848ee7ec45abf4a55c4ad2ae',1774785008,'uploadify_attachments|a:0:{}uploadify_attachments_queue|a:0:{}alerts|O:6:\"alerts\":1:{s:8:\"messages\";a:0:{}}app_send_to|N;app_session_token|s:10:\"P6I1w4gP8I\";app_current_users_filter|a:0:{}app_previously_logged_user|i:0;two_step_verification_info|a:0:{}app_email_verification_code|s:0:\"\";app_force_print_template|N;app_current_version|s:0:\"\";app_selected_items|a:0:{}listing_page_keeper|a:0:{}user_roles_dropdown_change_holder|a:0:{}app_subentity_form_items|a:0:{}app_subentity_form_items_deleted|a:0:{}app_logged_users_id|s:1:\"1\";');
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_configuration`
--

LOCK TABLES `app_users_configuration` WRITE;
/*!40000 ALTER TABLE `app_users_configuration` DISABLE KEYS */;
INSERT INTO `app_users_configuration` VALUES
(1,1,'sidebar-status','');
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
) ENGINE=InnoDB AUTO_INCREMENT=1452 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
(13,1,'admin','172.19.0.1',1,1774348420),
(14,1,'admin','172.19.0.1',1,1774358351),
(15,1,'admin','172.19.0.1',1,1774358351),
(16,1,'admin','172.19.0.1',1,1774358598),
(17,1,'admin','172.19.0.1',1,1774359002),
(18,1,'admin','172.19.0.1',1,1774359013),
(19,1,'admin','172.19.0.1',1,1774359985),
(20,1,'admin','172.19.0.1',1,1774360165),
(21,2,'manager.test','172.19.0.1',1,1774360165),
(22,3,'employee.test','172.19.0.1',1,1774360166),
(23,4,'requester.test','172.19.0.1',1,1774360166),
(24,5,'office.test','172.19.0.1',1,1774360166),
(25,1,'admin','172.19.0.1',1,1774360399),
(26,2,'manager.test','172.19.0.1',1,1774360399),
(27,3,'employee.test','172.19.0.1',1,1774360400),
(28,4,'requester.test','172.19.0.1',1,1774360400),
(29,5,'office.test','172.19.0.1',1,1774360400),
(30,1,'admin','172.19.0.1',1,1774360417),
(31,2,'manager.test','172.19.0.1',1,1774360417),
(32,3,'employee.test','172.19.0.1',1,1774360418),
(33,4,'requester.test','172.19.0.1',1,1774360418),
(34,5,'office.test','172.19.0.1',1,1774360418),
(35,1,'admin','172.19.0.1',1,1774360435),
(36,2,'manager.test','172.19.0.1',1,1774360436),
(37,3,'employee.test','172.19.0.1',1,1774360436),
(38,4,'requester.test','172.19.0.1',1,1774360437),
(39,5,'office.test','172.19.0.1',1,1774360437),
(40,1,'admin','172.19.0.1',1,1774361002),
(41,1,'admin','172.19.0.1',1,1774361003),
(42,2,'manager.test','172.19.0.1',1,1774361004),
(43,3,'employee.test','172.19.0.1',1,1774361004),
(44,4,'requester.test','172.19.0.1',1,1774361004),
(45,5,'office.test','172.19.0.1',1,1774361004),
(46,1,'admin','172.19.0.1',1,1774361569),
(47,1,'admin','172.19.0.1',1,1774361570),
(48,2,'manager.test','172.19.0.1',1,1774361571),
(49,3,'employee.test','172.19.0.1',1,1774361571),
(50,4,'requester.test','172.19.0.1',1,1774361572),
(51,5,'office.test','172.19.0.1',1,1774361572),
(52,1,'admin','172.19.0.1',1,1774362191),
(53,1,'admin','172.19.0.1',1,1774362416),
(54,1,'admin','172.19.0.1',1,1774362423),
(55,2,'manager.test','172.19.0.1',1,1774362423),
(56,3,'employee.test','172.19.0.1',1,1774362424),
(57,4,'requester.test','172.19.0.1',1,1774362424),
(58,5,'office.test','172.19.0.1',1,1774362424),
(59,1,'admin','172.19.0.1',1,1774365043),
(60,1,'admin','172.19.0.1',1,1774365228),
(61,1,'admin','172.19.0.1',1,1774365228),
(62,1,'admin','172.19.0.1',1,1774365236),
(63,1,'admin','172.19.0.1',1,1774365266),
(64,1,'admin','172.19.0.1',1,1774365280),
(65,1,'admin','172.19.0.1',1,1774365280),
(66,1,'admin','172.19.0.1',1,1774365366),
(67,1,'admin','172.19.0.1',1,1774365418),
(68,1,'admin','172.19.0.1',1,1774365510),
(69,1,'admin','172.19.0.1',1,1774365510),
(70,1,'admin','172.19.0.1',1,1774365510),
(71,1,'admin','172.19.0.1',1,1774365564),
(72,1,'admin','172.19.0.1',1,1774365564),
(73,1,'admin','172.19.0.1',1,1774365564),
(74,1,'admin','172.19.0.1',1,1774365564),
(75,1,'admin','172.19.0.1',1,1774365796),
(76,1,'admin','172.19.0.1',1,1774535160),
(77,1,'admin','172.19.0.1',1,1774535160),
(78,1,'admin','172.19.0.1',1,1774535160),
(79,1,'admin','172.19.0.1',1,1774535180),
(80,1,'admin','172.19.0.1',1,1774535732),
(81,1,'admin','172.19.0.1',1,1774535733),
(82,1,'admin','172.19.0.1',1,1774535733),
(83,1,'admin','172.19.0.1',1,1774535733),
(84,0,'admin','172.19.0.1',0,1774535944),
(85,1,'admin','172.19.0.1',1,1774535953),
(86,1,'admin','172.19.0.1',1,1774536822),
(87,1,'admin','172.19.0.1',1,1774536823),
(88,1,'admin','172.19.0.1',1,1774536823),
(89,1,'admin','172.19.0.1',1,1774536963),
(90,1,'admin','172.19.0.1',1,1774537457),
(91,1,'admin','172.19.0.1',1,1774537457),
(92,1,'admin','172.19.0.1',1,1774537469),
(93,1,'admin','172.19.0.1',1,1774537705),
(94,1,'admin','172.19.0.1',1,1774538787),
(95,1,'admin','172.19.0.1',1,1774539113),
(96,2,'manager.test','172.19.0.1',1,1774539136),
(97,1,'admin','172.19.0.1',1,1774539136),
(98,3,'employee.test','172.19.0.1',1,1774539136),
(99,5,'office.test','172.19.0.1',1,1774539136),
(100,1,'admin','172.19.0.1',1,1774539136),
(101,1,'admin','172.19.0.1',1,1774539150),
(102,1,'admin','172.19.0.1',1,1774539158),
(103,1,'admin','172.19.0.1',1,1774539435),
(104,1,'admin','172.19.0.1',1,1774539522),
(105,1,'admin','172.19.0.1',1,1774539522),
(106,1,'admin','172.19.0.1',1,1774539833),
(107,1,'admin','172.19.0.1',1,1774539976),
(108,1,'admin','172.19.0.1',1,1774539987),
(109,1,'admin','172.19.0.1',1,1774540559),
(110,1,'admin','172.19.0.1',1,1774541011),
(111,1,'admin','172.19.0.1',1,1774541462),
(112,2,'manager.test','172.19.0.1',1,1774541462),
(113,3,'employee.test','172.19.0.1',1,1774541463),
(114,4,'requester.test','172.19.0.1',1,1774541463),
(115,5,'office.test','172.19.0.1',1,1774541463),
(116,3,'employee.test','172.19.0.1',1,1774541605),
(117,1,'admin','172.19.0.1',1,1774541605),
(118,1,'admin','172.19.0.1',1,1774541799),
(119,1,'admin','172.19.0.1',1,1774541799),
(120,1,'admin','172.19.0.1',1,1774541799),
(121,1,'admin','172.19.0.1',1,1774541800),
(122,1,'admin','172.19.0.1',1,1774541804),
(123,2,'manager.test','172.19.0.1',1,1774541804),
(124,3,'employee.test','172.19.0.1',1,1774541805),
(125,4,'requester.test','172.19.0.1',1,1774541805),
(126,5,'office.test','172.19.0.1',1,1774541805),
(127,1,'admin','172.19.0.1',1,1774541846),
(128,1,'admin','172.19.0.1',1,1774541849),
(129,2,'manager.test','172.19.0.1',1,1774541850),
(130,3,'employee.test','172.19.0.1',1,1774541850),
(131,4,'requester.test','172.19.0.1',1,1774541850),
(132,5,'office.test','172.19.0.1',1,1774541850),
(133,1,'admin','172.19.0.1',1,1774542061),
(134,1,'admin','172.19.0.1',1,1774542061),
(135,1,'admin','172.19.0.1',1,1774542061),
(136,1,'admin','172.19.0.1',1,1774542135),
(137,1,'admin','172.19.0.1',1,1774542135),
(138,1,'admin','172.19.0.1',1,1774542135),
(139,1,'admin','172.19.0.1',1,1774542135),
(140,1,'admin','172.19.0.1',1,1774542136),
(141,2,'manager.test','172.19.0.1',1,1774542136),
(142,3,'employee.test','172.19.0.1',1,1774542137),
(143,4,'requester.test','172.19.0.1',1,1774542137),
(144,5,'office.test','172.19.0.1',1,1774542137),
(145,1,'admin','172.19.0.1',1,1774542414),
(146,1,'admin','172.19.0.1',1,1774542415),
(147,1,'admin','172.19.0.1',1,1774542416),
(148,2,'manager.test','172.19.0.1',1,1774542416),
(149,3,'employee.test','172.19.0.1',1,1774542416),
(150,4,'requester.test','172.19.0.1',1,1774542417),
(151,5,'office.test','172.19.0.1',1,1774542417),
(152,1,'admin','172.19.0.1',1,1774542749),
(153,1,'admin','172.19.0.1',1,1774542749),
(154,2,'manager.test','172.19.0.1',1,1774542749),
(155,3,'employee.test','172.19.0.1',1,1774542750),
(156,4,'requester.test','172.19.0.1',1,1774542750),
(157,5,'office.test','172.19.0.1',1,1774542750),
(158,1,'admin','172.19.0.1',1,1774542989),
(159,1,'admin','172.19.0.1',1,1774542989),
(160,1,'admin','172.19.0.1',1,1774542989),
(161,1,'admin','172.19.0.1',1,1774543221),
(162,1,'admin','172.19.0.1',1,1774543222),
(163,2,'manager.test','172.19.0.1',1,1774543222),
(164,3,'employee.test','172.19.0.1',1,1774543223),
(165,4,'requester.test','172.19.0.1',1,1774543223),
(166,5,'office.test','172.19.0.1',1,1774543223),
(167,1,'admin','172.19.0.1',1,1774543224),
(168,1,'admin','172.19.0.1',1,1774543224),
(169,1,'admin','172.19.0.1',1,1774543224),
(170,1,'admin','172.19.0.1',1,1774543415),
(171,1,'admin','172.19.0.1',1,1774543543),
(172,1,'admin','172.19.0.1',1,1774543543),
(173,1,'admin','172.19.0.1',1,1774543544),
(174,1,'admin','172.19.0.1',1,1774543544),
(175,1,'admin','172.19.0.1',1,1774543544),
(176,1,'admin','172.19.0.1',1,1774543738),
(177,1,'admin','172.19.0.1',1,1774543739),
(178,2,'manager.test','172.19.0.1',1,1774543739),
(179,3,'employee.test','172.19.0.1',1,1774543740),
(180,4,'requester.test','172.19.0.1',1,1774543740),
(181,5,'office.test','172.19.0.1',1,1774543740),
(182,1,'admin','172.19.0.1',1,1774543741),
(183,1,'admin','172.19.0.1',1,1774543741),
(184,1,'admin','172.19.0.1',1,1774543741),
(185,1,'admin','172.19.0.1',1,1774543919),
(186,1,'admin','172.19.0.1',1,1774544009),
(187,1,'admin','172.19.0.1',1,1774544034),
(188,1,'admin','172.19.0.1',1,1774544078),
(189,1,'admin','172.19.0.1',1,1774544129),
(190,1,'admin','172.19.0.1',1,1774544130),
(191,1,'admin','172.19.0.1',1,1774544240),
(192,1,'admin','172.19.0.1',1,1774544241),
(193,2,'manager.test','172.19.0.1',1,1774544242),
(194,3,'employee.test','172.19.0.1',1,1774544242),
(195,4,'requester.test','172.19.0.1',1,1774544242),
(196,5,'office.test','172.19.0.1',1,1774544242),
(197,1,'admin','172.19.0.1',1,1774544243),
(198,1,'admin','172.19.0.1',1,1774544243),
(199,1,'admin','172.19.0.1',1,1774544243),
(200,1,'admin','172.19.0.1',1,1774544244),
(201,1,'admin','172.19.0.1',1,1774544291),
(202,1,'admin','172.19.0.1',1,1774544374),
(203,1,'admin','172.19.0.1',1,1774544537),
(204,1,'admin','172.19.0.1',1,1774544538),
(205,1,'admin','172.19.0.1',1,1774544538),
(206,2,'manager.test','172.19.0.1',1,1774544539),
(207,3,'employee.test','172.19.0.1',1,1774544539),
(208,4,'requester.test','172.19.0.1',1,1774544539),
(209,5,'office.test','172.19.0.1',1,1774544539),
(210,1,'admin','172.19.0.1',1,1774544540),
(211,1,'admin','172.19.0.1',1,1774544540),
(212,1,'admin','172.19.0.1',1,1774544541),
(213,1,'admin','172.19.0.1',1,1774544541),
(214,1,'admin','172.19.0.1',1,1774544550),
(215,1,'admin','172.19.0.1',1,1774544797),
(216,1,'admin','172.19.0.1',1,1774544798),
(217,1,'admin','172.19.0.1',1,1774544798),
(218,2,'manager.test','172.19.0.1',1,1774544798),
(219,3,'employee.test','172.19.0.1',1,1774544799),
(220,4,'requester.test','172.19.0.1',1,1774544799),
(221,5,'office.test','172.19.0.1',1,1774544799),
(222,1,'admin','172.19.0.1',1,1774544800),
(223,1,'admin','172.19.0.1',1,1774544800),
(224,1,'admin','172.19.0.1',1,1774544800),
(225,1,'admin','172.19.0.1',1,1774544801),
(226,1,'admin','172.19.0.1',1,1774544810),
(227,1,'admin','172.19.0.1',1,1774544848),
(228,1,'admin','172.19.0.1',1,1774544911),
(229,1,'admin','172.19.0.1',1,1774545102),
(230,1,'admin','172.19.0.1',1,1774545122),
(231,1,'admin','172.19.0.1',1,1774545123),
(232,1,'admin','172.19.0.1',1,1774545123),
(233,1,'admin','172.19.0.1',1,1774545123),
(234,2,'manager.test','172.19.0.1',1,1774545124),
(235,3,'employee.test','172.19.0.1',1,1774545124),
(236,4,'requester.test','172.19.0.1',1,1774545124),
(237,5,'office.test','172.19.0.1',1,1774545124),
(238,1,'admin','172.19.0.1',1,1774545125),
(239,1,'admin','172.19.0.1',1,1774545125),
(240,1,'admin','172.19.0.1',1,1774545126),
(241,1,'admin','172.19.0.1',1,1774545126),
(242,1,'admin','172.19.0.1',1,1774545135),
(243,1,'admin','172.19.0.1',1,1774545145),
(244,1,'admin','172.19.0.1',1,1774545332),
(245,1,'admin','172.19.0.1',1,1774545369),
(246,1,'admin','172.19.0.1',1,1774545393),
(247,1,'admin','172.19.0.1',1,1774545416),
(248,1,'admin','172.19.0.1',1,1774545462),
(249,1,'admin','172.19.0.1',1,1774545476),
(250,1,'admin','172.19.0.1',1,1774545477),
(251,2,'manager.test','172.19.0.1',1,1774545477),
(252,3,'employee.test','172.19.0.1',1,1774545477),
(253,4,'requester.test','172.19.0.1',1,1774545477),
(254,5,'office.test','172.19.0.1',1,1774545478),
(255,1,'admin','172.19.0.1',1,1774545479),
(256,1,'admin','172.19.0.1',1,1774545479),
(257,1,'admin','172.19.0.1',1,1774545479),
(258,1,'admin','172.19.0.1',1,1774545479),
(259,1,'admin','172.19.0.1',1,1774545488),
(260,1,'admin','172.19.0.1',1,1774545498),
(261,1,'admin','172.19.0.1',1,1774545906),
(262,1,'admin','172.19.0.1',1,1774545907),
(263,2,'manager.test','172.19.0.1',1,1774545908),
(264,3,'employee.test','172.19.0.1',1,1774545908),
(265,4,'requester.test','172.19.0.1',1,1774545908),
(266,5,'office.test','172.19.0.1',1,1774545908),
(267,1,'admin','172.19.0.1',1,1774545909),
(268,1,'admin','172.19.0.1',1,1774545909),
(269,1,'admin','172.19.0.1',1,1774545910),
(270,1,'admin','172.19.0.1',1,1774545910),
(271,1,'admin','172.19.0.1',1,1774545919),
(272,1,'admin','172.19.0.1',1,1774545928),
(273,1,'admin','172.19.0.1',1,1774559098),
(274,1,'admin','172.19.0.1',1,1774559099),
(275,2,'manager.test','172.19.0.1',1,1774559100),
(276,3,'employee.test','172.19.0.1',1,1774559100),
(277,4,'requester.test','172.19.0.1',1,1774559100),
(278,5,'office.test','172.19.0.1',1,1774559100),
(279,1,'admin','172.19.0.1',1,1774559101),
(280,1,'admin','172.19.0.1',1,1774559101),
(281,1,'admin','172.19.0.1',1,1774559102),
(282,1,'admin','172.19.0.1',1,1774559102),
(283,1,'admin','172.19.0.1',1,1774559111),
(284,1,'admin','172.19.0.1',1,1774559121),
(285,1,'admin','172.19.0.1',1,1774559476),
(286,1,'admin','172.19.0.1',1,1774559477),
(287,2,'manager.test','172.19.0.1',1,1774559477),
(288,3,'employee.test','172.19.0.1',1,1774559477),
(289,4,'requester.test','172.19.0.1',1,1774559478),
(290,5,'office.test','172.19.0.1',1,1774559478),
(291,1,'admin','172.19.0.1',1,1774559501),
(292,1,'admin','172.19.0.1',1,1774559503),
(293,2,'manager.test','172.19.0.1',1,1774559503),
(294,3,'employee.test','172.19.0.1',1,1774559503),
(295,4,'requester.test','172.19.0.1',1,1774559503),
(296,5,'office.test','172.19.0.1',1,1774559503),
(297,1,'admin','172.19.0.1',1,1774559515),
(298,1,'admin','172.19.0.1',1,1774559516),
(299,2,'manager.test','172.19.0.1',1,1774559516),
(300,3,'employee.test','172.19.0.1',1,1774559516),
(301,4,'requester.test','172.19.0.1',1,1774559517),
(302,5,'office.test','172.19.0.1',1,1774559517),
(303,1,'admin','172.19.0.1',1,1774559518),
(304,1,'admin','172.19.0.1',1,1774559518),
(305,1,'admin','172.19.0.1',1,1774559518),
(306,1,'admin','172.19.0.1',1,1774559519),
(307,1,'admin','172.19.0.1',1,1774559528),
(308,1,'admin','172.19.0.1',1,1774559537),
(309,1,'admin','172.19.0.1',1,1774559576),
(310,1,'admin','172.19.0.1',1,1774562613),
(311,1,'admin','172.19.0.1',1,1774562614),
(312,2,'manager.test','172.19.0.1',1,1774562614),
(313,3,'employee.test','172.19.0.1',1,1774562615),
(314,4,'requester.test','172.19.0.1',1,1774562615),
(315,5,'office.test','172.19.0.1',1,1774562615),
(316,1,'admin','172.19.0.1',1,1774562616),
(317,1,'admin','172.19.0.1',1,1774562616),
(318,1,'admin','172.19.0.1',1,1774562616),
(319,1,'admin','172.19.0.1',1,1774562617),
(320,1,'admin','172.19.0.1',1,1774562626),
(321,1,'admin','172.19.0.1',1,1774562635),
(322,1,'admin','172.19.0.1',1,1774562688),
(323,1,'admin','172.19.0.1',1,1774562719),
(324,1,'admin','172.19.0.1',1,1774562999),
(325,1,'admin','172.19.0.1',1,1774562999),
(326,1,'admin','172.19.0.1',1,1774563000),
(327,2,'manager.test','172.19.0.1',1,1774563001),
(328,3,'employee.test','172.19.0.1',1,1774563001),
(329,4,'requester.test','172.19.0.1',1,1774563001),
(330,5,'office.test','172.19.0.1',1,1774563001),
(331,1,'admin','172.19.0.1',1,1774563002),
(332,1,'admin','172.19.0.1',1,1774563003),
(333,1,'admin','172.19.0.1',1,1774563003),
(334,1,'admin','172.19.0.1',1,1774563003),
(335,1,'admin','172.19.0.1',1,1774563003),
(336,1,'admin','172.19.0.1',1,1774563012),
(337,1,'admin','172.19.0.1',1,1774563022),
(338,1,'admin','172.19.0.1',1,1774563051),
(339,1,'admin','172.19.0.1',1,1774563183),
(340,1,'admin','172.19.0.1',1,1774563184),
(341,2,'manager.test','172.19.0.1',1,1774563184),
(342,1,'admin','172.19.0.1',1,1774563185),
(343,3,'employee.test','172.19.0.1',1,1774563185),
(344,4,'requester.test','172.19.0.1',1,1774563185),
(345,5,'office.test','172.19.0.1',1,1774563185),
(346,1,'admin','172.19.0.1',1,1774563672),
(347,1,'admin','172.19.0.1',1,1774563702),
(348,1,'admin','172.19.0.1',1,1774563796),
(349,1,'admin','172.19.0.1',1,1774563796),
(350,1,'admin','172.19.0.1',1,1774563822),
(351,1,'admin','172.19.0.1',1,1774563822),
(352,1,'admin','172.19.0.1',1,1774563823),
(353,2,'manager.test','172.19.0.1',1,1774563824),
(354,3,'employee.test','172.19.0.1',1,1774563824),
(355,4,'requester.test','172.19.0.1',1,1774563824),
(356,5,'office.test','172.19.0.1',1,1774563824),
(357,1,'admin','172.19.0.1',1,1774563825),
(358,1,'admin','172.19.0.1',1,1774563826),
(359,1,'admin','172.19.0.1',1,1774563826),
(360,1,'admin','172.19.0.1',1,1774563826),
(361,1,'admin','172.19.0.1',1,1774563827),
(362,1,'admin','172.19.0.1',1,1774563836),
(363,1,'admin','172.19.0.1',1,1774563845),
(364,1,'admin','172.19.0.1',1,1774563896),
(365,1,'admin','172.19.0.1',1,1774563956),
(366,1,'admin','172.19.0.1',1,1774563957),
(367,2,'manager.test','172.19.0.1',1,1774563958),
(368,3,'employee.test','172.19.0.1',1,1774563958),
(369,4,'requester.test','172.19.0.1',1,1774563958),
(370,5,'office.test','172.19.0.1',1,1774563958),
(371,1,'admin','172.19.0.1',1,1774563959),
(372,1,'admin','172.19.0.1',1,1774563960),
(373,1,'admin','172.19.0.1',1,1774563960),
(374,1,'admin','172.19.0.1',1,1774563960),
(375,1,'admin','172.19.0.1',1,1774563961),
(376,1,'admin','172.19.0.1',1,1774563970),
(377,1,'admin','172.19.0.1',1,1774563979),
(378,1,'admin','172.19.0.1',1,1774564278),
(379,6,'user.demo','172.19.0.1',1,1774564278),
(380,1,'admin','172.19.0.1',1,1774564286),
(381,1,'admin','172.19.0.1',1,1774564287),
(382,2,'manager.test','172.19.0.1',1,1774564288),
(383,3,'employee.test','172.19.0.1',1,1774564288),
(384,4,'requester.test','172.19.0.1',1,1774564288),
(385,5,'office.test','172.19.0.1',1,1774564288),
(386,1,'admin','172.19.0.1',1,1774564289),
(387,1,'admin','172.19.0.1',1,1774564289),
(388,1,'admin','172.19.0.1',1,1774564290),
(389,1,'admin','172.19.0.1',1,1774564290),
(390,1,'admin','172.19.0.1',1,1774564290),
(391,1,'admin','172.19.0.1',1,1774564300),
(392,1,'admin','172.19.0.1',1,1774564309),
(393,1,'admin','172.19.0.1',1,1774564386),
(394,1,'admin','172.19.0.1',1,1774564387),
(395,2,'manager.test','172.19.0.1',1,1774564387),
(396,1,'admin','172.19.0.1',1,1774564387),
(397,3,'employee.test','172.19.0.1',1,1774564387),
(398,4,'requester.test','172.19.0.1',1,1774564388),
(399,5,'office.test','172.19.0.1',1,1774564388),
(400,1,'admin','172.19.0.1',1,1774564463),
(401,1,'admin','172.19.0.1',1,1774564464),
(402,2,'manager.test','172.19.0.1',1,1774564465),
(403,3,'employee.test','172.19.0.1',1,1774564465),
(404,4,'requester.test','172.19.0.1',1,1774564465),
(405,5,'office.test','172.19.0.1',1,1774564465),
(406,1,'admin','172.19.0.1',1,1774564466),
(407,1,'admin','172.19.0.1',1,1774564467),
(408,1,'admin','172.19.0.1',1,1774564467),
(409,1,'admin','172.19.0.1',1,1774564467),
(410,1,'admin','172.19.0.1',1,1774564467),
(411,1,'admin','172.19.0.1',1,1774564477),
(412,1,'admin','172.19.0.1',1,1774564486),
(413,1,'admin','172.19.0.1',1,1774564643),
(414,1,'admin','172.19.0.1',1,1774564644),
(415,2,'manager.test','172.19.0.1',1,1774564645),
(416,3,'employee.test','172.19.0.1',1,1774564645),
(417,4,'requester.test','172.19.0.1',1,1774564645),
(418,5,'office.test','172.19.0.1',1,1774564645),
(419,1,'admin','172.19.0.1',1,1774564646),
(420,1,'admin','172.19.0.1',1,1774564647),
(421,1,'admin','172.19.0.1',1,1774564647),
(422,1,'admin','172.19.0.1',1,1774564647),
(423,1,'admin','172.19.0.1',1,1774564647),
(424,1,'admin','172.19.0.1',1,1774564656),
(425,1,'admin','172.19.0.1',1,1774564666),
(426,1,'admin','172.19.0.1',1,1774565005),
(427,1,'admin','172.19.0.1',1,1774565006),
(428,2,'manager.test','172.19.0.1',1,1774565007),
(429,3,'employee.test','172.19.0.1',1,1774565007),
(430,4,'requester.test','172.19.0.1',1,1774565007),
(431,5,'office.test','172.19.0.1',1,1774565007),
(432,1,'admin','172.19.0.1',1,1774565008),
(433,1,'admin','172.19.0.1',1,1774565009),
(434,1,'admin','172.19.0.1',1,1774565009),
(435,1,'admin','172.19.0.1',1,1774565009),
(436,1,'admin','172.19.0.1',1,1774565009),
(437,1,'admin','172.19.0.1',1,1774565018),
(438,1,'admin','172.19.0.1',1,1774565028),
(439,1,'admin','172.19.0.1',1,1774565273),
(440,1,'admin','172.19.0.1',1,1774565274),
(441,2,'manager.test','172.19.0.1',1,1774565274),
(442,3,'employee.test','172.19.0.1',1,1774565275),
(443,4,'requester.test','172.19.0.1',1,1774565275),
(444,5,'office.test','172.19.0.1',1,1774565275),
(445,1,'admin','172.19.0.1',1,1774565276),
(446,1,'admin','172.19.0.1',1,1774565276),
(447,1,'admin','172.19.0.1',1,1774565276),
(448,1,'admin','172.19.0.1',1,1774565277),
(449,1,'admin','172.19.0.1',1,1774565277),
(450,1,'admin','172.19.0.1',1,1774565286),
(451,1,'admin','172.19.0.1',1,1774565295),
(452,1,'admin','172.19.0.1',1,1774565605),
(453,1,'admin','172.19.0.1',1,1774565661),
(454,1,'admin','172.19.0.1',1,1774565663),
(455,2,'manager.test','172.19.0.1',1,1774565663),
(456,3,'employee.test','172.19.0.1',1,1774565663),
(457,6,'user.demo','172.19.0.1',1,1774565664),
(458,4,'requester.test','172.19.0.1',1,1774565664),
(459,5,'office.test','172.19.0.1',1,1774565664),
(460,1,'admin','172.19.0.1',1,1774565665),
(461,1,'admin','172.19.0.1',1,1774565665),
(462,1,'admin','172.19.0.1',1,1774565665),
(463,1,'admin','172.19.0.1',1,1774565666),
(464,1,'admin','172.19.0.1',1,1774565666),
(465,1,'admin','172.19.0.1',1,1774565675),
(466,1,'admin','172.19.0.1',1,1774565684),
(467,1,'admin','172.19.0.1',1,1774565861),
(468,1,'admin','172.19.0.1',1,1774565915),
(469,1,'admin','172.19.0.1',1,1774565952),
(470,1,'admin','172.19.0.1',1,1774566014),
(471,6,'user.demo','172.19.0.1',1,1774566020),
(472,6,'user.demo','172.19.0.1',1,1774566090),
(473,6,'user.demo','172.19.0.1',1,1774566121),
(474,6,'user.demo','172.19.0.1',1,1774566208),
(475,6,'user.demo','172.19.0.1',1,1774566227),
(476,1,'admin','172.19.0.1',1,1774566255),
(477,1,'admin','172.19.0.1',1,1774566308),
(478,1,'admin','172.19.0.1',1,1774566309),
(479,2,'manager.test','172.19.0.1',1,1774566309),
(480,3,'employee.test','172.19.0.1',1,1774566310),
(481,6,'user.demo','172.19.0.1',1,1774566310),
(482,4,'requester.test','172.19.0.1',1,1774566310),
(483,5,'office.test','172.19.0.1',1,1774566310),
(484,1,'admin','172.19.0.1',1,1774566311),
(485,1,'admin','172.19.0.1',1,1774566312),
(486,1,'admin','172.19.0.1',1,1774566312),
(487,1,'admin','172.19.0.1',1,1774566312),
(488,1,'admin','172.19.0.1',1,1774566313),
(489,1,'admin','172.19.0.1',1,1774566322),
(490,1,'admin','172.19.0.1',1,1774566331),
(491,1,'admin','172.19.0.1',1,1774566994),
(492,1,'admin','172.19.0.1',1,1774566995),
(493,2,'manager.test','172.19.0.1',1,1774566996),
(494,3,'employee.test','172.19.0.1',1,1774566996),
(495,6,'user.demo','172.19.0.1',1,1774566996),
(496,4,'requester.test','172.19.0.1',1,1774566996),
(497,5,'office.test','172.19.0.1',1,1774566996),
(498,1,'admin','172.19.0.1',1,1774566997),
(499,1,'admin','172.19.0.1',1,1774566997),
(500,1,'admin','172.19.0.1',1,1774566998),
(501,1,'admin','172.19.0.1',1,1774566998),
(502,1,'admin','172.19.0.1',1,1774566998),
(503,1,'admin','172.19.0.1',1,1774567007),
(504,1,'admin','172.19.0.1',1,1774567016),
(505,1,'admin','172.19.0.1',1,1774567094),
(506,1,'admin','172.19.0.1',1,1774598310),
(507,1,'admin','172.19.0.1',1,1774598313),
(508,2,'manager.test','172.19.0.1',1,1774598315),
(509,3,'employee.test','172.19.0.1',1,1774598315),
(510,6,'user.demo','172.19.0.1',1,1774598316),
(511,4,'requester.test','172.19.0.1',1,1774598317),
(512,5,'office.test','172.19.0.1',1,1774598317),
(513,1,'admin','172.19.0.1',1,1774598319),
(514,1,'admin','172.19.0.1',1,1774598321),
(515,1,'admin','172.19.0.1',1,1774598321),
(516,1,'admin','172.19.0.1',1,1774598321),
(517,1,'admin','172.19.0.1',1,1774599218),
(518,1,'admin','172.19.0.1',1,1774599219),
(519,1,'admin','172.19.0.1',1,1774599306),
(520,1,'admin','172.19.0.1',1,1774599310),
(521,2,'manager.test','172.19.0.1',1,1774599311),
(522,3,'employee.test','172.19.0.1',1,1774599312),
(523,6,'user.demo','172.19.0.1',1,1774599313),
(524,4,'requester.test','172.19.0.1',1,1774599313),
(525,5,'office.test','172.19.0.1',1,1774599314),
(526,1,'admin','172.19.0.1',1,1774599316),
(527,1,'admin','172.19.0.1',1,1774599318),
(528,1,'admin','172.19.0.1',1,1774599318),
(529,1,'admin','172.19.0.1',1,1774599318),
(530,1,'admin','172.19.0.1',1,1774599322),
(531,1,'admin','172.19.0.1',1,1774599336),
(532,1,'admin','172.19.0.1',1,1774599415),
(533,1,'admin','172.19.0.1',1,1774599494),
(534,6,'user.demo','172.19.0.1',1,1774599500),
(535,1,'admin','172.19.0.1',1,1774600134),
(536,6,'user.demo','172.19.0.1',1,1774600139),
(537,1,'admin','172.19.0.1',1,1774600201),
(538,6,'user.demo','172.19.0.1',1,1774600206),
(539,1,'admin','172.19.0.1',1,1774600228),
(540,1,'admin','172.19.0.1',1,1774600230),
(541,2,'manager.test','172.19.0.1',1,1774600230),
(542,3,'employee.test','172.19.0.1',1,1774600230),
(543,6,'user.demo','172.19.0.1',1,1774600231),
(544,4,'requester.test','172.19.0.1',1,1774600231),
(545,5,'office.test','172.19.0.1',1,1774600231),
(546,1,'admin','172.19.0.1',1,1774600232),
(547,1,'admin','172.19.0.1',1,1774600233),
(548,1,'admin','172.19.0.1',1,1774600233),
(549,1,'admin','172.19.0.1',1,1774600233),
(550,1,'admin','172.19.0.1',1,1774600235),
(551,1,'admin','172.19.0.1',1,1774600245),
(552,1,'admin','172.19.0.1',1,1774600297),
(553,1,'admin','172.19.0.1',1,1774601104),
(554,1,'admin','172.19.0.1',1,1774601105),
(555,1,'admin','172.19.0.1',1,1774601106),
(556,2,'manager.test','172.19.0.1',1,1774601106),
(557,3,'employee.test','172.19.0.1',1,1774601107),
(558,6,'user.demo','172.19.0.1',1,1774601107),
(559,4,'requester.test','172.19.0.1',1,1774601107),
(560,5,'office.test','172.19.0.1',1,1774601107),
(561,1,'admin','172.19.0.1',1,1774601108),
(562,1,'admin','172.19.0.1',1,1774601109),
(563,1,'admin','172.19.0.1',1,1774601109),
(564,1,'admin','172.19.0.1',1,1774601109),
(565,1,'admin','172.19.0.1',1,1774601111),
(566,1,'admin','172.19.0.1',1,1774601122),
(567,1,'admin','172.19.0.1',1,1774601172),
(568,1,'admin','172.19.0.1',1,1774601181),
(569,1,'admin','172.19.0.1',1,1774601303),
(570,1,'admin','172.19.0.1',1,1774601365),
(571,1,'admin','172.19.0.1',1,1774601410),
(572,6,'user.demo','172.19.0.1',1,1774601419),
(573,6,'user.demo','172.19.0.1',1,1774601522),
(574,1,'admin','172.19.0.1',1,1774601584),
(575,6,'user.demo','172.19.0.1',1,1774601591),
(576,6,'user.demo','172.19.0.1',1,1774601687),
(577,1,'admin','172.19.0.1',1,1774602015),
(578,1,'admin','172.19.0.1',1,1774602234),
(579,6,'user.demo','172.19.0.1',1,1774602242),
(580,6,'user.demo','172.19.0.1',1,1774602338),
(581,1,'admin','172.19.0.1',1,1774602603),
(582,1,'admin','172.19.0.1',1,1774602604),
(583,2,'manager.test','172.19.0.1',1,1774602605),
(584,3,'employee.test','172.19.0.1',1,1774602605),
(585,6,'user.demo','172.19.0.1',1,1774602605),
(586,4,'requester.test','172.19.0.1',1,1774602606),
(587,5,'office.test','172.19.0.1',1,1774602606),
(588,1,'admin','172.19.0.1',1,1774602607),
(589,1,'admin','172.19.0.1',1,1774602607),
(590,1,'admin','172.19.0.1',1,1774602607),
(591,1,'admin','172.19.0.1',1,1774602607),
(592,1,'admin','172.19.0.1',1,1774602609),
(593,1,'admin','172.19.0.1',1,1774602620),
(594,1,'admin','172.19.0.1',1,1774602670),
(595,1,'admin','172.19.0.1',1,1774602678),
(596,1,'admin','172.19.0.1',1,1774602897),
(597,6,'user.demo','172.19.0.1',1,1774602905),
(598,6,'user.demo','172.19.0.1',1,1774603000),
(599,1,'admin','172.19.0.1',1,1774603259),
(600,6,'user.demo','172.19.0.1',1,1774603267),
(601,1,'admin','172.19.0.1',1,1774603841),
(602,1,'admin','172.19.0.1',1,1774603842),
(603,1,'admin','172.19.0.1',1,1774603842),
(604,2,'manager.test','172.19.0.1',1,1774603843),
(605,3,'employee.test','172.19.0.1',1,1774603843),
(606,6,'user.demo','172.19.0.1',1,1774603843),
(607,4,'requester.test','172.19.0.1',1,1774603844),
(608,5,'office.test','172.19.0.1',1,1774603844),
(609,1,'admin','172.19.0.1',1,1774603845),
(610,1,'admin','172.19.0.1',1,1774603845),
(611,1,'admin','172.19.0.1',1,1774603845),
(612,1,'admin','172.19.0.1',1,1774603846),
(613,1,'admin','172.19.0.1',1,1774603847),
(614,6,'user.demo','172.19.0.1',1,1774603850),
(615,1,'admin','172.19.0.1',1,1774603858),
(616,1,'admin','172.19.0.1',1,1774603908),
(617,1,'admin','172.19.0.1',1,1774603917),
(618,1,'admin','172.19.0.1',1,1774603933),
(619,1,'admin','172.19.0.1',1,1774604136),
(620,6,'user.demo','172.19.0.1',1,1774604143),
(621,6,'user.demo','172.19.0.1',1,1774604239),
(622,1,'admin','172.19.0.1',1,1774605385),
(623,1,'admin','172.19.0.1',1,1774605387),
(624,2,'manager.test','172.19.0.1',1,1774605387),
(625,3,'employee.test','172.19.0.1',1,1774605388),
(626,6,'user.demo','172.19.0.1',1,1774605388),
(627,4,'requester.test','172.19.0.1',1,1774605388),
(628,5,'office.test','172.19.0.1',1,1774605388),
(629,1,'admin','172.19.0.1',1,1774605389),
(630,1,'admin','172.19.0.1',1,1774605390),
(631,1,'admin','172.19.0.1',1,1774605390),
(632,1,'admin','172.19.0.1',1,1774605390),
(633,1,'admin','172.19.0.1',1,1774605392),
(634,1,'admin','172.19.0.1',1,1774605403),
(635,1,'admin','172.19.0.1',1,1774605454),
(636,1,'admin','172.19.0.1',1,1774605462),
(637,1,'admin','172.19.0.1',1,1774605681),
(638,6,'user.demo','172.19.0.1',1,1774605689),
(639,6,'user.demo','172.19.0.1',1,1774605784),
(640,1,'admin','172.19.0.1',1,1774606609),
(641,1,'admin','172.19.0.1',1,1774606610),
(642,2,'manager.test','172.19.0.1',1,1774606611),
(643,3,'employee.test','172.19.0.1',1,1774606611),
(644,6,'user.demo','172.19.0.1',1,1774606611),
(645,4,'requester.test','172.19.0.1',1,1774606612),
(646,5,'office.test','172.19.0.1',1,1774606612),
(647,1,'admin','172.19.0.1',1,1774606613),
(648,1,'admin','172.19.0.1',1,1774606613),
(649,1,'admin','172.19.0.1',1,1774606613),
(650,1,'admin','172.19.0.1',1,1774606614),
(651,1,'admin','172.19.0.1',1,1774606616),
(652,1,'admin','172.19.0.1',1,1774606626),
(653,1,'admin','172.19.0.1',1,1774606679),
(654,1,'admin','172.19.0.1',1,1774606687),
(655,1,'admin','172.19.0.1',1,1774606906),
(656,6,'user.demo','172.19.0.1',1,1774606914),
(657,6,'user.demo','172.19.0.1',1,1774607010),
(658,1,'admin','172.19.0.1',1,1774609604),
(659,1,'admin','172.19.0.1',1,1774609606),
(660,2,'manager.test','172.19.0.1',1,1774609606),
(661,3,'employee.test','172.19.0.1',1,1774609606),
(662,6,'user.demo','172.19.0.1',1,1774609607),
(663,4,'requester.test','172.19.0.1',1,1774609607),
(664,5,'office.test','172.19.0.1',1,1774609607),
(665,1,'admin','172.19.0.1',1,1774609608),
(666,1,'admin','172.19.0.1',1,1774609609),
(667,1,'admin','172.19.0.1',1,1774609609),
(668,1,'admin','172.19.0.1',1,1774609609),
(669,1,'admin','172.19.0.1',1,1774609611),
(670,1,'admin','172.19.0.1',1,1774609621),
(671,1,'admin','172.19.0.1',1,1774609672),
(672,1,'admin','172.19.0.1',1,1774609680),
(673,1,'admin','172.19.0.1',1,1774618150),
(674,1,'admin','172.19.0.1',1,1774618153),
(675,2,'manager.test','172.19.0.1',1,1774618153),
(676,3,'employee.test','172.19.0.1',1,1774618154),
(677,6,'user.demo','172.19.0.1',1,1774618154),
(678,4,'requester.test','172.19.0.1',1,1774618154),
(679,5,'office.test','172.19.0.1',1,1774618155),
(680,1,'admin','172.19.0.1',1,1774618156),
(681,1,'admin','172.19.0.1',1,1774618157),
(682,1,'admin','172.19.0.1',1,1774618157),
(683,1,'admin','172.19.0.1',1,1774618157),
(684,1,'admin','172.19.0.1',1,1774618160),
(685,1,'admin','172.19.0.1',1,1774618173),
(686,1,'admin','172.19.0.1',1,1774618188),
(687,1,'admin','172.19.0.1',1,1774618188),
(688,1,'admin','172.19.0.1',1,1774618188),
(689,1,'admin','172.19.0.1',1,1774618189),
(690,1,'admin','172.19.0.1',1,1774618189),
(691,1,'admin','172.19.0.1',1,1774618232),
(692,1,'admin','172.19.0.1',1,1774618240),
(693,1,'admin','172.19.0.1',1,1774618460),
(694,6,'user.demo','172.19.0.1',1,1774618467),
(695,6,'user.demo','172.19.0.1',1,1774618563),
(696,1,'admin','172.19.0.1',1,1774619403),
(697,1,'admin','172.19.0.1',1,1774619403),
(698,1,'admin','172.19.0.1',1,1774619403),
(699,1,'admin','172.19.0.1',1,1774619403),
(700,1,'admin','172.19.0.1',1,1774619404),
(701,1,'admin','172.19.0.1',1,1774620072),
(702,1,'admin','172.19.0.1',1,1774620073),
(703,1,'admin','172.19.0.1',1,1774620073),
(704,1,'admin','172.19.0.1',1,1774620073),
(705,1,'admin','172.19.0.1',1,1774620074),
(706,1,'admin','172.19.0.1',1,1774620118),
(707,1,'admin','172.19.0.1',1,1774620121),
(708,2,'manager.test','172.19.0.1',1,1774620121),
(709,3,'employee.test','172.19.0.1',1,1774620122),
(710,6,'user.demo','172.19.0.1',1,1774620122),
(711,4,'requester.test','172.19.0.1',1,1774620122),
(712,5,'office.test','172.19.0.1',1,1774620123),
(713,1,'admin','172.19.0.1',1,1774620124),
(714,1,'admin','172.19.0.1',1,1774620125),
(715,1,'admin','172.19.0.1',1,1774620125),
(716,1,'admin','172.19.0.1',1,1774620125),
(717,1,'admin','172.19.0.1',1,1774620128),
(718,1,'admin','172.19.0.1',1,1774620141),
(719,1,'admin','172.19.0.1',1,1774620199),
(720,1,'admin','172.19.0.1',1,1774620208),
(721,1,'admin','172.19.0.1',1,1774620428),
(722,6,'user.demo','172.19.0.1',1,1774620436),
(723,6,'user.demo','172.19.0.1',1,1774620532),
(724,1,'admin','172.19.0.1',1,1774627480),
(725,1,'admin','172.19.0.1',1,1774627480),
(726,1,'admin','172.19.0.1',1,1774627480),
(727,1,'admin','172.19.0.1',1,1774627481),
(728,1,'admin','172.19.0.1',1,1774628582),
(729,1,'admin','172.19.0.1',1,1774628582),
(730,1,'admin','172.19.0.1',1,1774628582),
(731,1,'admin','172.19.0.1',1,1774628583),
(732,1,'admin','172.19.0.1',1,1774628844),
(733,1,'admin','172.19.0.1',1,1774628845),
(734,2,'manager.test','172.19.0.1',1,1774628846),
(735,3,'employee.test','172.19.0.1',1,1774628846),
(736,6,'user.demo','172.19.0.1',1,1774628846),
(737,4,'requester.test','172.19.0.1',1,1774628846),
(738,5,'office.test','172.19.0.1',1,1774628847),
(739,1,'admin','172.19.0.1',1,1774628847),
(740,1,'admin','172.19.0.1',1,1774628848),
(741,1,'admin','172.19.0.1',1,1774628848),
(742,1,'admin','172.19.0.1',1,1774628848),
(743,1,'admin','172.19.0.1',1,1774628850),
(744,1,'admin','172.19.0.1',1,1774628860),
(745,1,'admin','172.19.0.1',1,1774628909),
(746,1,'admin','172.19.0.1',1,1774628917),
(747,1,'admin','172.19.0.1',1,1774629136),
(748,6,'user.demo','172.19.0.1',1,1774629144),
(749,6,'user.demo','172.19.0.1',1,1774629239),
(750,1,'admin','172.19.0.1',1,1774630935),
(751,1,'admin','172.19.0.1',1,1774630937),
(752,2,'manager.test','172.19.0.1',1,1774630937),
(753,3,'employee.test','172.19.0.1',1,1774630938),
(754,6,'user.demo','172.19.0.1',1,1774630938),
(755,4,'requester.test','172.19.0.1',1,1774630938),
(756,5,'office.test','172.19.0.1',1,1774630938),
(757,1,'admin','172.19.0.1',1,1774630939),
(758,1,'admin','172.19.0.1',1,1774630939),
(759,1,'admin','172.19.0.1',1,1774630939),
(760,1,'admin','172.19.0.1',1,1774630940),
(761,1,'admin','172.19.0.1',1,1774630941),
(762,1,'admin','172.19.0.1',1,1774630952),
(763,1,'admin','172.19.0.1',1,1774631000),
(764,1,'admin','172.19.0.1',1,1774631008),
(765,1,'admin','172.19.0.1',1,1774631227),
(766,6,'user.demo','172.19.0.1',1,1774631235),
(767,6,'user.demo','172.19.0.1',1,1774631330),
(768,1,'admin','172.19.0.1',1,1774632167),
(769,1,'admin','172.19.0.1',1,1774632225),
(770,1,'admin','172.19.0.1',1,1774632240),
(771,1,'admin','172.19.0.1',1,1774632302),
(772,1,'admin','172.19.0.1',1,1774632392),
(773,1,'admin','172.19.0.1',1,1774632392),
(774,1,'admin','172.19.0.1',1,1774632392),
(775,1,'admin','172.19.0.1',1,1774632393),
(776,1,'admin','172.19.0.1',1,1774633982),
(777,1,'admin','172.19.0.1',1,1774637219),
(778,1,'admin','172.19.0.1',1,1774642130),
(779,1,'admin','172.19.0.1',1,1774642196),
(780,1,'admin','172.19.0.1',1,1774642197),
(781,1,'admin','172.19.0.1',1,1774642207),
(782,1,'admin','172.19.0.1',1,1774642257),
(783,1,'admin','172.19.0.1',1,1774642386),
(784,1,'admin','172.19.0.1',1,1774642387),
(785,1,'admin','172.19.0.1',1,1774642389),
(786,2,'manager.test','172.19.0.1',1,1774642389),
(787,3,'employee.test','172.19.0.1',1,1774642389),
(788,6,'user.demo','172.19.0.1',1,1774642389),
(789,4,'requester.test','172.19.0.1',1,1774642390),
(790,5,'office.test','172.19.0.1',1,1774642390),
(791,1,'admin','172.19.0.1',1,1774642390),
(792,1,'admin','172.19.0.1',1,1774642391),
(793,1,'admin','172.19.0.1',1,1774642391),
(794,1,'admin','172.19.0.1',1,1774642408),
(795,1,'admin','172.19.0.1',1,1774642408),
(796,1,'admin','172.19.0.1',1,1774642431),
(797,1,'admin','172.19.0.1',1,1774642446),
(798,1,'admin','172.19.0.1',1,1774642490),
(799,1,'admin','172.19.0.1',1,1774642490),
(800,1,'admin','172.19.0.1',1,1774642490),
(801,1,'admin','172.19.0.1',1,1774642490),
(802,1,'admin','172.19.0.1',1,1774642492),
(803,2,'manager.test','172.19.0.1',1,1774642492),
(804,3,'employee.test','172.19.0.1',1,1774642492),
(805,6,'user.demo','172.19.0.1',1,1774642492),
(806,4,'requester.test','172.19.0.1',1,1774642493),
(807,5,'office.test','172.19.0.1',1,1774642493),
(808,1,'admin','172.19.0.1',1,1774642494),
(809,1,'admin','172.19.0.1',1,1774642494),
(810,1,'admin','172.19.0.1',1,1774642494),
(811,1,'admin','172.19.0.1',1,1774642494),
(812,1,'admin','172.19.0.1',1,1774642496),
(813,1,'admin','172.19.0.1',1,1774642506),
(814,1,'admin','172.19.0.1',1,1774642555),
(815,1,'admin','172.19.0.1',1,1774642563),
(816,1,'admin','172.19.0.1',1,1774642782),
(817,6,'user.demo','172.19.0.1',1,1774642789),
(818,6,'user.demo','172.19.0.1',1,1774642885),
(819,1,'admin','172.19.0.1',1,1774643352),
(820,1,'admin','172.19.0.1',1,1774643571),
(821,6,'user.demo','172.19.0.1',1,1774643579),
(822,6,'user.demo','172.19.0.1',1,1774643674),
(823,1,'admin','172.19.0.1',1,1774644572),
(824,1,'admin','172.19.0.1',1,1774644573),
(825,1,'admin','172.19.0.1',1,1774644573),
(826,1,'admin','172.19.0.1',1,1774644574),
(827,1,'admin','172.19.0.1',1,1774644574),
(828,1,'admin','172.19.0.1',1,1774644574),
(829,1,'admin','172.19.0.1',1,1774644575),
(830,2,'manager.test','172.19.0.1',1,1774644575),
(831,3,'employee.test','172.19.0.1',1,1774644575),
(832,6,'user.demo','172.19.0.1',1,1774644576),
(833,4,'requester.test','172.19.0.1',1,1774644576),
(834,5,'office.test','172.19.0.1',1,1774644576),
(835,1,'admin','172.19.0.1',1,1774644577),
(836,1,'admin','172.19.0.1',1,1774644577),
(837,1,'admin','172.19.0.1',1,1774644577),
(838,1,'admin','172.19.0.1',1,1774644577),
(839,1,'admin','172.19.0.1',1,1774644579),
(840,1,'admin','172.19.0.1',1,1774644581),
(841,1,'admin','172.19.0.1',1,1774644589),
(842,1,'admin','172.19.0.1',1,1774644638),
(843,1,'admin','172.19.0.1',1,1774644646),
(844,1,'admin','172.19.0.1',1,1774644800),
(845,6,'user.demo','172.19.0.1',1,1774644807),
(846,1,'admin','172.19.0.1',1,1774644865),
(847,6,'user.demo','172.19.0.1',1,1774644872),
(848,6,'user.demo','172.19.0.1',1,1774644903),
(849,6,'user.demo','172.19.0.1',1,1774644968),
(850,1,'admin','172.19.0.1',1,1774646247),
(851,1,'admin','172.19.0.1',1,1774646285),
(852,1,'admin','172.19.0.1',1,1774646287),
(853,2,'manager.test','172.19.0.1',1,1774646287),
(854,3,'employee.test','172.19.0.1',1,1774646287),
(855,6,'user.demo','172.19.0.1',1,1774646288),
(856,4,'requester.test','172.19.0.1',1,1774646288),
(857,5,'office.test','172.19.0.1',1,1774646288),
(858,1,'admin','172.19.0.1',1,1774646289),
(859,1,'admin','172.19.0.1',1,1774646289),
(860,1,'admin','172.19.0.1',1,1774646289),
(861,1,'admin','172.19.0.1',1,1774646290),
(862,1,'admin','172.19.0.1',1,1774646291),
(863,1,'admin','172.19.0.1',1,1774646301),
(864,1,'admin','172.19.0.1',1,1774646350),
(865,1,'admin','172.19.0.1',1,1774646358),
(866,1,'admin','172.19.0.1',1,1774646577),
(867,6,'user.demo','172.19.0.1',1,1774646585),
(868,6,'user.demo','172.19.0.1',1,1774646680),
(869,1,'admin','172.19.0.1',1,1774646991),
(870,1,'admin','172.19.0.1',1,1774646991),
(871,1,'admin','172.19.0.1',1,1774646993),
(872,1,'admin','172.19.0.1',1,1774647210),
(873,6,'user.demo','172.19.0.1',1,1774647218),
(874,6,'user.demo','172.19.0.1',1,1774647313),
(875,1,'admin','172.19.0.1',1,1774648000),
(876,1,'admin','172.19.0.1',1,1774648014),
(877,1,'admin','172.19.0.1',1,1774648015),
(878,1,'admin','172.19.0.1',1,1774648016),
(879,2,'manager.test','172.19.0.1',1,1774648017),
(880,3,'employee.test','172.19.0.1',1,1774648017),
(881,6,'user.demo','172.19.0.1',1,1774648017),
(882,4,'requester.test','172.19.0.1',1,1774648017),
(883,5,'office.test','172.19.0.1',1,1774648018),
(884,1,'admin','172.19.0.1',1,1774648018),
(885,1,'admin','172.19.0.1',1,1774648019),
(886,1,'admin','172.19.0.1',1,1774648019),
(887,1,'admin','172.19.0.1',1,1774648019),
(888,1,'admin','172.19.0.1',1,1774648021),
(889,1,'admin','172.19.0.1',1,1774648031),
(890,1,'admin','172.19.0.1',1,1774648079),
(891,1,'admin','172.19.0.1',1,1774648087),
(892,1,'admin','172.19.0.1',1,1774648306),
(893,6,'user.demo','172.19.0.1',1,1774648313),
(894,6,'user.demo','172.19.0.1',1,1774648409),
(895,1,'admin','172.19.0.1',1,1774678564),
(896,1,'admin','172.19.0.1',1,1774678574),
(897,1,'admin','172.19.0.1',1,1774678577),
(898,2,'manager.test','172.19.0.1',1,1774678577),
(899,3,'employee.test','172.19.0.1',1,1774678577),
(900,6,'user.demo','172.19.0.1',1,1774678578),
(901,4,'requester.test','172.19.0.1',1,1774678578),
(902,5,'office.test','172.19.0.1',1,1774678578),
(903,1,'admin','172.19.0.1',1,1774678579),
(904,1,'admin','172.19.0.1',1,1774678580),
(905,1,'admin','172.19.0.1',1,1774678580),
(906,1,'admin','172.19.0.1',1,1774678580),
(907,1,'admin','172.19.0.1',1,1774678582),
(908,1,'admin','172.19.0.1',1,1774678593),
(909,1,'admin','172.19.0.1',1,1774678654),
(910,1,'admin','172.19.0.1',1,1774678662),
(911,1,'admin','172.19.0.1',1,1774678881),
(912,6,'user.demo','172.19.0.1',1,1774678888),
(913,6,'user.demo','172.19.0.1',1,1774678984),
(914,1,'admin','172.19.0.1',1,1774680386),
(915,1,'admin','172.19.0.1',1,1774680386),
(916,1,'admin','172.19.0.1',1,1774680386),
(917,1,'admin','172.19.0.1',1,1774680387),
(918,1,'admin','172.19.0.1',1,1774680390),
(919,1,'admin','172.19.0.1',1,1774680394),
(920,2,'manager.test','172.19.0.1',1,1774680395),
(921,3,'employee.test','172.19.0.1',1,1774680395),
(922,6,'user.demo','172.19.0.1',1,1774680395),
(923,4,'requester.test','172.19.0.1',1,1774680395),
(924,5,'office.test','172.19.0.1',1,1774680396),
(925,1,'admin','172.19.0.1',1,1774680397),
(926,1,'admin','172.19.0.1',1,1774680397),
(927,1,'admin','172.19.0.1',1,1774680397),
(928,1,'admin','172.19.0.1',1,1774680398),
(929,1,'admin','172.19.0.1',1,1774680399),
(930,1,'admin','172.19.0.1',1,1774680410),
(931,1,'admin','172.19.0.1',1,1774680469),
(932,1,'admin','172.19.0.1',1,1774680477),
(933,1,'admin','172.19.0.1',1,1774680696),
(934,6,'user.demo','172.19.0.1',1,1774680704),
(935,6,'user.demo','172.19.0.1',1,1774680800),
(936,1,'admin','172.19.0.1',1,1774681553),
(937,1,'admin','172.19.0.1',1,1774681554),
(938,1,'admin','172.19.0.1',1,1774681773),
(939,6,'user.demo','172.19.0.1',1,1774681781),
(940,6,'user.demo','172.19.0.1',1,1774681877),
(941,7,'nurse.test','172.19.0.1',1,1774681884),
(942,7,'nurse.test','172.19.0.1',1,1774681980),
(943,1,'admin','172.19.0.1',1,1774682282),
(944,1,'admin','172.19.0.1',1,1774682501),
(945,6,'user.demo','172.19.0.1',1,1774682508),
(946,6,'user.demo','172.19.0.1',1,1774682604),
(947,7,'nurse.test','172.19.0.1',1,1774682612),
(948,7,'nurse.test','172.19.0.1',1,1774682708),
(949,1,'admin','172.19.0.1',1,1774682964),
(950,1,'admin','172.19.0.1',1,1774683296),
(951,1,'admin','172.19.0.1',1,1774683515),
(952,6,'user.demo','172.19.0.1',1,1774683523),
(953,6,'user.demo','172.19.0.1',1,1774683620),
(954,7,'nurse.test','172.19.0.1',1,1774683627),
(955,7,'nurse.test','172.19.0.1',1,1774683724),
(956,1,'admin','172.19.0.1',1,1774684344),
(957,1,'admin','172.19.0.1',1,1774684344),
(958,1,'admin','172.19.0.1',1,1774684344),
(959,1,'admin','172.19.0.1',1,1774684344),
(960,1,'admin','172.19.0.1',1,1774684708),
(961,1,'admin','172.19.0.1',1,1774684708),
(962,1,'admin','172.19.0.1',1,1774684708),
(963,1,'admin','172.19.0.1',1,1774684709),
(964,1,'admin','172.19.0.1',1,1774684747),
(965,1,'admin','172.19.0.1',1,1774685143),
(966,1,'admin','172.19.0.1',1,1774685148),
(967,2,'manager.test','172.19.0.1',1,1774685149),
(968,3,'employee.test','172.19.0.1',1,1774685149),
(969,6,'user.demo','172.19.0.1',1,1774685149),
(970,4,'requester.test','172.19.0.1',1,1774685149),
(971,5,'office.test','172.19.0.1',1,1774685150),
(972,1,'admin','172.19.0.1',1,1774685151),
(973,1,'admin','172.19.0.1',1,1774685152),
(974,1,'admin','172.19.0.1',1,1774685152),
(975,1,'admin','172.19.0.1',1,1774685153),
(976,1,'admin','172.19.0.1',1,1774685157),
(977,1,'admin','172.19.0.1',1,1774685170),
(978,1,'admin','172.19.0.1',1,1774685230),
(979,1,'admin','172.19.0.1',1,1774685239),
(980,1,'admin','172.19.0.1',1,1774685459),
(981,6,'user.demo','172.19.0.1',1,1774685467),
(982,6,'user.demo','172.19.0.1',1,1774685564),
(983,7,'nurse.test','172.19.0.1',1,1774685572),
(984,7,'nurse.test','172.19.0.1',1,1774685668),
(985,1,'admin','172.19.0.1',1,1774687191),
(986,1,'admin','172.19.0.1',1,1774687196),
(987,1,'admin','172.19.0.1',1,1774687200),
(988,2,'manager.test','172.19.0.1',1,1774687200),
(989,3,'employee.test','172.19.0.1',1,1774687200),
(990,6,'user.demo','172.19.0.1',1,1774687201),
(991,4,'requester.test','172.19.0.1',1,1774687201),
(992,5,'office.test','172.19.0.1',1,1774687201),
(993,1,'admin','172.19.0.1',1,1774687202),
(994,1,'admin','172.19.0.1',1,1774687202),
(995,1,'admin','172.19.0.1',1,1774687203),
(996,1,'admin','172.19.0.1',1,1774687203),
(997,1,'admin','172.19.0.1',1,1774687205),
(998,1,'admin','172.19.0.1',1,1774687215),
(999,1,'admin','172.19.0.1',1,1774687264),
(1000,1,'admin','172.19.0.1',1,1774687272),
(1001,1,'admin','172.19.0.1',1,1774687491),
(1002,6,'user.demo','172.19.0.1',1,1774687499),
(1003,6,'user.demo','172.19.0.1',1,1774687595),
(1004,7,'nurse.test','172.19.0.1',1,1774687602),
(1005,7,'nurse.test','172.19.0.1',1,1774687698),
(1006,1,'admin','172.19.0.1',1,1774688956),
(1007,1,'admin','172.19.0.1',1,1774688956),
(1008,1,'admin','172.19.0.1',1,1774688956),
(1009,1,'admin','172.19.0.1',1,1774688956),
(1010,1,'admin','172.19.0.1',1,1774688963),
(1011,1,'admin','172.19.0.1',1,1774688967),
(1012,2,'manager.test','172.19.0.1',1,1774688967),
(1013,3,'employee.test','172.19.0.1',1,1774688967),
(1014,6,'user.demo','172.19.0.1',1,1774688968),
(1015,4,'requester.test','172.19.0.1',1,1774688968),
(1016,5,'office.test','172.19.0.1',1,1774688968),
(1017,1,'admin','172.19.0.1',1,1774688969),
(1018,1,'admin','172.19.0.1',1,1774688969),
(1019,1,'admin','172.19.0.1',1,1774688969),
(1020,1,'admin','172.19.0.1',1,1774688970),
(1021,1,'admin','172.19.0.1',1,1774688972),
(1022,1,'admin','172.19.0.1',1,1774688982),
(1023,1,'admin','172.19.0.1',1,1774689031),
(1024,1,'admin','172.19.0.1',1,1774689040),
(1025,1,'admin','172.19.0.1',1,1774689258),
(1026,6,'user.demo','172.19.0.1',1,1774689266),
(1027,6,'user.demo','172.19.0.1',1,1774689362),
(1028,7,'nurse.test','172.19.0.1',1,1774689369),
(1029,7,'nurse.test','172.19.0.1',1,1774689465),
(1030,1,'admin','172.19.0.1',1,1774690832),
(1031,1,'admin','172.19.0.1',1,1774690835),
(1032,2,'manager.test','172.19.0.1',1,1774690836),
(1033,3,'employee.test','172.19.0.1',1,1774690836),
(1034,6,'user.demo','172.19.0.1',1,1774690836),
(1035,4,'requester.test','172.19.0.1',1,1774690836),
(1036,5,'office.test','172.19.0.1',1,1774690836),
(1037,1,'admin','172.19.0.1',1,1774690838),
(1038,1,'admin','172.19.0.1',1,1774690839),
(1039,1,'admin','172.19.0.1',1,1774690839),
(1040,1,'admin','172.19.0.1',1,1774690839),
(1041,1,'admin','172.19.0.1',1,1774690841),
(1042,1,'admin','172.19.0.1',1,1774690851),
(1043,1,'admin','172.19.0.1',1,1774690898),
(1044,1,'admin','172.19.0.1',1,1774690906),
(1045,1,'admin','172.19.0.1',1,1774691125),
(1046,6,'user.demo','172.19.0.1',1,1774691132),
(1047,6,'user.demo','172.19.0.1',1,1774691228),
(1048,7,'nurse.test','172.19.0.1',1,1774691235),
(1049,7,'nurse.test','172.19.0.1',1,1774691331),
(1050,6,'user.demo','172.19.0.1',1,1774691752),
(1051,6,'user.demo','172.19.0.1',1,1774691772),
(1052,6,'user.demo','172.19.0.1',1,1774691829),
(1053,6,'user.demo','172.19.0.1',1,1774691855),
(1054,6,'user.demo','172.19.0.1',1,1774691903),
(1055,1,'admin','172.19.0.1',1,1774692092),
(1056,1,'admin','172.19.0.1',1,1774692093),
(1057,6,'user.demo','172.19.0.1',1,1774692213),
(1058,1,'admin','172.19.0.1',1,1774692312),
(1059,6,'user.demo','172.19.0.1',1,1774692319),
(1060,6,'user.demo','172.19.0.1',1,1774692415),
(1061,7,'nurse.test','172.19.0.1',1,1774692422),
(1062,7,'nurse.test','172.19.0.1',1,1774692518),
(1063,1,'admin','172.19.0.1',1,1774692725),
(1064,1,'admin','172.19.0.1',1,1774692726),
(1065,1,'admin','172.19.0.1',1,1774692729),
(1066,2,'manager.test','172.19.0.1',1,1774692730),
(1067,3,'employee.test','172.19.0.1',1,1774692730),
(1068,6,'user.demo','172.19.0.1',1,1774692730),
(1069,4,'requester.test','172.19.0.1',1,1774692730),
(1070,5,'office.test','172.19.0.1',1,1774692731),
(1071,1,'admin','172.19.0.1',1,1774692732),
(1072,1,'admin','172.19.0.1',1,1774692733),
(1073,1,'admin','172.19.0.1',1,1774692733),
(1074,1,'admin','172.19.0.1',1,1774692733),
(1075,1,'admin','172.19.0.1',1,1774692735),
(1076,1,'admin','172.19.0.1',1,1774692745),
(1077,1,'admin','172.19.0.1',1,1774692793),
(1078,1,'admin','172.19.0.1',1,1774692801),
(1079,1,'admin','172.19.0.1',1,1774692866),
(1080,1,'admin','172.19.0.1',1,1774692866),
(1081,1,'admin','172.19.0.1',1,1774692866),
(1082,1,'admin','172.19.0.1',1,1774693019),
(1083,6,'user.demo','172.19.0.1',1,1774693027),
(1084,6,'user.demo','172.19.0.1',1,1774693122),
(1085,7,'nurse.test','172.19.0.1',1,1774693130),
(1086,7,'nurse.test','172.19.0.1',1,1774693225),
(1087,1,'admin','172.19.0.1',1,1774702843),
(1088,1,'admin','172.19.0.1',1,1774702857),
(1089,1,'admin','172.19.0.1',1,1774702931),
(1090,1,'admin','172.19.0.1',1,1774702934),
(1091,2,'manager.test','172.19.0.1',1,1774702935),
(1092,3,'employee.test','172.19.0.1',1,1774702935),
(1093,6,'user.demo','172.19.0.1',1,1774702935),
(1094,4,'requester.test','172.19.0.1',1,1774702935),
(1095,5,'office.test','172.19.0.1',1,1774702935),
(1096,1,'admin','172.19.0.1',1,1774702937),
(1097,1,'admin','172.19.0.1',1,1774702938),
(1098,1,'admin','172.19.0.1',1,1774702938),
(1099,1,'admin','172.19.0.1',1,1774702938),
(1100,1,'admin','172.19.0.1',1,1774702940),
(1101,1,'admin','172.19.0.1',1,1774702951),
(1102,1,'admin','172.19.0.1',1,1774702999),
(1103,1,'admin','172.19.0.1',1,1774703007),
(1104,1,'admin','172.19.0.1',1,1774703225),
(1105,6,'user.demo','172.19.0.1',1,1774703233),
(1106,6,'user.demo','172.19.0.1',1,1774703328),
(1107,7,'nurse.test','172.19.0.1',1,1774703336),
(1108,7,'nurse.test','172.19.0.1',1,1774703431),
(1109,1,'admin','172.19.0.1',1,1774703946),
(1110,1,'admin','172.19.0.1',1,1774703949),
(1111,2,'manager.test','172.19.0.1',1,1774703949),
(1112,3,'employee.test','172.19.0.1',1,1774703950),
(1113,6,'user.demo','172.19.0.1',1,1774703950),
(1114,4,'requester.test','172.19.0.1',1,1774703950),
(1115,5,'office.test','172.19.0.1',1,1774703950),
(1116,1,'admin','172.19.0.1',1,1774703952),
(1117,1,'admin','172.19.0.1',1,1774703952),
(1118,1,'admin','172.19.0.1',1,1774703952),
(1119,1,'admin','172.19.0.1',1,1774703953),
(1120,1,'admin','172.19.0.1',1,1774703954),
(1121,1,'admin','172.19.0.1',1,1774703964),
(1122,1,'admin','172.19.0.1',1,1774704012),
(1123,1,'admin','172.19.0.1',1,1774704020),
(1124,1,'admin','172.19.0.1',1,1774704238),
(1125,6,'user.demo','172.19.0.1',1,1774704246),
(1126,6,'user.demo','172.19.0.1',1,1774704341),
(1127,7,'nurse.test','172.19.0.1',1,1774704349),
(1128,7,'nurse.test','172.19.0.1',1,1774704445),
(1129,1,'admin','172.19.0.1',1,1774705501),
(1130,1,'admin','172.19.0.1',1,1774705501),
(1131,1,'admin','172.19.0.1',1,1774705501),
(1132,1,'admin','172.19.0.1',1,1774705502),
(1133,6,'user.demo','172.19.0.1',1,1774705538),
(1134,1,'admin','172.19.0.1',1,1774706120),
(1135,1,'admin','172.19.0.1',1,1774706139),
(1136,1,'admin','172.19.0.1',1,1774706139),
(1137,1,'admin','172.19.0.1',1,1774706139),
(1138,1,'admin','172.19.0.1',1,1774706139),
(1139,1,'admin','172.19.0.1',1,1774706139),
(1140,1,'admin','172.19.0.1',1,1774706140),
(1141,1,'admin','172.19.0.1',1,1774706140),
(1142,1,'admin','172.19.0.1',1,1774706140),
(1143,1,'admin','172.19.0.1',1,1774706140),
(1144,1,'admin','172.19.0.1',1,1774706141),
(1145,1,'admin','172.19.0.1',1,1774706141),
(1146,1,'admin','172.19.0.1',1,1774706141),
(1147,1,'admin','172.19.0.1',1,1774706155),
(1148,6,'user.demo','172.19.0.1',1,1774706156),
(1149,1,'admin','172.19.0.1',1,1774706157),
(1150,6,'user.demo','172.19.0.1',1,1774706165),
(1151,6,'user.demo','172.19.0.1',1,1774706175),
(1152,6,'user.demo','172.19.0.1',1,1774706185),
(1153,6,'user.demo','172.19.0.1',1,1774706227),
(1154,1,'admin','172.19.0.1',1,1774706373),
(1155,6,'user.demo','172.19.0.1',1,1774706381),
(1156,6,'user.demo','172.19.0.1',1,1774706477),
(1157,7,'nurse.test','172.19.0.1',1,1774706484),
(1158,7,'nurse.test','172.19.0.1',1,1774706580),
(1159,1,'admin','172.19.0.1',1,1774706844),
(1160,1,'admin','172.19.0.1',1,1774706844),
(1161,1,'admin','172.19.0.1',1,1774706844),
(1162,1,'admin','172.19.0.1',1,1774706844),
(1163,1,'admin','172.19.0.1',1,1774706844),
(1164,1,'admin','172.19.0.1',1,1774706854),
(1165,1,'admin','172.19.0.1',1,1774706857),
(1166,2,'manager.test','172.19.0.1',1,1774706858),
(1167,3,'employee.test','172.19.0.1',1,1774706858),
(1168,6,'user.demo','172.19.0.1',1,1774706858),
(1169,4,'requester.test','172.19.0.1',1,1774706858),
(1170,5,'office.test','172.19.0.1',1,1774706858),
(1171,1,'admin','172.19.0.1',1,1774706860),
(1172,1,'admin','172.19.0.1',1,1774706861),
(1173,1,'admin','172.19.0.1',1,1774706861),
(1174,1,'admin','172.19.0.1',1,1774706861),
(1175,1,'admin','172.19.0.1',1,1774706863),
(1176,1,'admin','172.19.0.1',1,1774706873),
(1177,1,'admin','172.19.0.1',1,1774706921),
(1178,1,'admin','172.19.0.1',1,1774706929),
(1179,1,'admin','172.19.0.1',1,1774707148),
(1180,6,'user.demo','172.19.0.1',1,1774707155),
(1181,6,'user.demo','172.19.0.1',1,1774707251),
(1182,7,'nurse.test','172.19.0.1',1,1774707259),
(1183,7,'nurse.test','172.19.0.1',1,1774707354),
(1184,1,'admin','172.19.0.1',1,1774707650),
(1185,1,'admin','172.19.0.1',1,1774707651),
(1186,1,'admin','172.19.0.1',1,1774707651),
(1187,1,'admin','172.19.0.1',1,1774707651),
(1188,6,'user.demo','172.19.0.1',1,1774707652),
(1189,1,'admin','172.19.0.1',1,1774707653),
(1190,1,'admin','172.19.0.1',1,1774707865),
(1191,1,'admin','172.19.0.1',1,1774707942),
(1192,1,'admin','172.19.0.1',1,1774708099),
(1193,1,'admin','172.19.0.1',1,1774708100),
(1194,2,'manager.test','172.19.0.1',1,1774708101),
(1195,3,'employee.test','172.19.0.1',1,1774708101),
(1196,6,'user.demo','172.19.0.1',1,1774708101),
(1197,4,'requester.test','172.19.0.1',1,1774708101),
(1198,5,'office.test','172.19.0.1',1,1774708101),
(1199,6,'user.demo','172.19.0.1',1,1774708133),
(1200,7,'nurse.test','172.19.0.1',1,1774708140),
(1201,4,'requester.test','172.19.0.1',1,1774708145),
(1202,5,'office.test','172.19.0.1',1,1774708149),
(1203,2,'manager.test','172.19.0.1',1,1774708152),
(1204,6,'user.demo','172.19.0.1',1,1774708183),
(1205,7,'nurse.test','172.19.0.1',1,1774708190),
(1206,4,'requester.test','172.19.0.1',1,1774708195),
(1207,5,'office.test','172.19.0.1',1,1774708198),
(1208,2,'manager.test','172.19.0.1',1,1774708202),
(1209,1,'admin','172.19.0.1',1,1774708318),
(1210,6,'user.demo','172.19.0.1',1,1774708325),
(1211,6,'user.demo','172.19.0.1',1,1774708421),
(1212,7,'nurse.test','172.19.0.1',1,1774708428),
(1213,7,'nurse.test','172.19.0.1',1,1774708524),
(1214,1,'admin','172.19.0.1',1,1774709942),
(1215,1,'admin','172.19.0.1',1,1774709942),
(1216,1,'admin','172.19.0.1',1,1774710021),
(1217,1,'admin','172.19.0.1',1,1774710022),
(1218,1,'admin','172.19.0.1',1,1774710022),
(1219,1,'admin','172.19.0.1',1,1774710022),
(1220,1,'admin','172.19.0.1',1,1774710023),
(1221,2,'manager.test','172.19.0.1',1,1774710023),
(1222,3,'employee.test','172.19.0.1',1,1774710024),
(1223,6,'user.demo','172.19.0.1',1,1774710024),
(1224,4,'requester.test','172.19.0.1',1,1774710024),
(1225,5,'office.test','172.19.0.1',1,1774710024),
(1226,7,'nurse.test','172.19.0.1',1,1774710024),
(1227,1,'admin','172.19.0.1',1,1774710068),
(1228,1,'admin','172.19.0.1',1,1774710072),
(1229,2,'manager.test','172.19.0.1',1,1774710072),
(1230,3,'employee.test','172.19.0.1',1,1774710072),
(1231,6,'user.demo','172.19.0.1',1,1774710072),
(1232,4,'requester.test','172.19.0.1',1,1774710072),
(1233,5,'office.test','172.19.0.1',1,1774710073),
(1234,7,'nurse.test','172.19.0.1',1,1774710073),
(1235,1,'admin','172.19.0.1',1,1774710075),
(1236,1,'admin','172.19.0.1',1,1774710075),
(1237,1,'admin','172.19.0.1',1,1774710075),
(1238,1,'admin','172.19.0.1',1,1774710076),
(1239,1,'admin','172.19.0.1',1,1774710078),
(1240,1,'admin','172.19.0.1',1,1774710088),
(1241,1,'admin','172.19.0.1',1,1774710137),
(1242,1,'admin','172.19.0.1',1,1774710145),
(1243,1,'admin','172.19.0.1',1,1774710364),
(1244,6,'user.demo','172.19.0.1',1,1774710371),
(1245,6,'user.demo','172.19.0.1',1,1774710467),
(1246,7,'nurse.test','172.19.0.1',1,1774710474),
(1247,7,'nurse.test','172.19.0.1',1,1774710570),
(1248,1,'admin','172.19.0.1',1,1774715640),
(1249,1,'admin','172.19.0.1',1,1774715641),
(1250,1,'admin','172.19.0.1',1,1774715641),
(1251,1,'admin','172.19.0.1',1,1774715641),
(1252,0,'admin','172.19.0.1',0,1774715946),
(1253,1,'admin','172.19.0.1',1,1774715987),
(1254,1,'admin','172.19.0.1',1,1774716004),
(1255,1,'admin','172.19.0.1',1,1774716005),
(1256,1,'admin','172.19.0.1',1,1774716005),
(1257,8,'department.head','172.19.0.1',1,1774716005),
(1258,9,'clinician.primary','172.19.0.1',1,1774716005),
(1259,11,'registry.operator','172.19.0.1',1,1774716005),
(1260,12,'records.office','172.19.0.1',1,1774716005),
(1261,10,'nurse.coordinator','172.19.0.1',1,1774716006),
(1262,1,'admin','172.19.0.1',1,1774719264),
(1263,1,'admin','172.19.0.1',1,1774719326),
(1264,1,'admin','172.19.0.1',1,1774719342),
(1265,1,'admin','172.19.0.1',1,1774719342),
(1266,8,'department.head','172.19.0.1',1,1774719343),
(1267,9,'clinician.primary','172.19.0.1',1,1774719343),
(1268,11,'registry.operator','172.19.0.1',1,1774719343),
(1269,12,'records.office','172.19.0.1',1,1774719343),
(1270,10,'nurse.coordinator','172.19.0.1',1,1774719344),
(1271,1,'admin','172.19.0.1',1,1774719912),
(1272,1,'admin','172.19.0.1',1,1774719924),
(1273,8,'department.head','172.19.0.1',1,1774719924),
(1274,9,'clinician.primary','172.19.0.1',1,1774719925),
(1275,11,'registry.operator','172.19.0.1',1,1774719925),
(1276,12,'records.office','172.19.0.1',1,1774719925),
(1277,10,'nurse.coordinator','172.19.0.1',1,1774719925),
(1278,1,'admin','172.19.0.1',1,1774720332),
(1279,8,'department.head','172.19.0.1',1,1774720333),
(1280,9,'clinician.primary','172.19.0.1',1,1774720333),
(1281,11,'registry.operator','172.19.0.1',1,1774720333),
(1282,12,'records.office','172.19.0.1',1,1774720333),
(1283,10,'nurse.coordinator','172.19.0.1',1,1774720333),
(1284,1,'admin','172.19.0.1',1,1774721133),
(1285,1,'admin','172.19.0.1',1,1774721133),
(1286,1,'admin','172.19.0.1',1,1774721134),
(1287,1,'admin','172.19.0.1',1,1774721134),
(1288,1,'admin','172.19.0.1',1,1774721134),
(1289,1,'admin','172.19.0.1',1,1774721134),
(1290,9,'clinician.primary','172.19.0.1',1,1774721153),
(1291,8,'department.head','172.19.0.1',1,1774721168),
(1292,1,'admin','172.19.0.1',1,1774721256),
(1293,8,'department.head','172.19.0.1',1,1774721256),
(1294,9,'clinician.primary','172.19.0.1',1,1774721257),
(1295,11,'registry.operator','172.19.0.1',1,1774721257),
(1296,12,'records.office','172.19.0.1',1,1774721257),
(1297,10,'nurse.coordinator','172.19.0.1',1,1774721257),
(1298,0,'admin','172.19.0.1',0,1774721375),
(1299,0,'admin','172.19.0.1',0,1774721381),
(1300,1,'admin','172.19.0.1',1,1774721430),
(1301,9,'clinician.primary','172.19.0.1',1,1774722381),
(1302,8,'department.head','172.19.0.1',1,1774722389),
(1303,9,'clinician.primary','172.19.0.1',1,1774722418),
(1304,8,'department.head','172.19.0.1',1,1774722426),
(1305,9,'clinician.primary','172.19.0.1',1,1774722442),
(1306,8,'department.head','172.19.0.1',1,1774722450),
(1307,9,'clinician.primary','172.19.0.1',1,1774722468),
(1308,8,'department.head','172.19.0.1',1,1774722476),
(1309,9,'clinician.primary','172.19.0.1',1,1774723061),
(1310,8,'department.head','172.19.0.1',1,1774723069),
(1311,9,'clinician.primary','172.19.0.1',1,1774723115),
(1312,8,'department.head','172.19.0.1',1,1774723123),
(1313,9,'clinician.primary','172.19.0.1',1,1774723205),
(1314,8,'department.head','172.19.0.1',1,1774723213),
(1315,9,'clinician.primary','172.19.0.1',1,1774723246),
(1316,8,'department.head','172.19.0.1',1,1774723253),
(1317,9,'clinician.primary','172.19.0.1',1,1774723293),
(1318,8,'department.head','172.19.0.1',1,1774723302),
(1319,9,'clinician.primary','172.19.0.1',1,1774723382),
(1320,8,'department.head','172.19.0.1',1,1774723390),
(1321,1,'admin','172.19.0.1',1,1774723428),
(1322,1,'admin','172.19.0.1',1,1774723428),
(1323,1,'admin','172.19.0.1',1,1774723428),
(1324,1,'admin','172.19.0.1',1,1774723429),
(1325,1,'admin','172.19.0.1',1,1774723429),
(1326,1,'admin','172.19.0.1',1,1774723429),
(1327,1,'admin','172.19.0.1',1,1774723429),
(1328,1,'admin','172.19.0.1',1,1774723562),
(1329,9,'clinician.primary','172.19.0.1',1,1774724092),
(1330,9,'clinician.primary','172.19.0.1',1,1774724123),
(1331,9,'clinician.primary','172.19.0.1',1,1774724156),
(1332,9,'clinician.primary','172.19.0.1',1,1774724217),
(1333,9,'clinician.primary','172.19.0.1',1,1774724261),
(1334,9,'clinician.primary','172.19.0.1',1,1774724339),
(1335,9,'clinician.primary','172.19.0.1',1,1774724429),
(1336,9,'clinician.primary','172.19.0.1',1,1774724486),
(1337,9,'clinician.primary','172.19.0.1',1,1774724523),
(1338,9,'clinician.primary','172.19.0.1',1,1774724564),
(1339,9,'clinician.primary','172.19.0.1',1,1774724809),
(1340,1,'admin','172.19.0.1',1,1774724881),
(1341,1,'admin','172.19.0.1',1,1774724881),
(1342,1,'admin','172.19.0.1',1,1774724881),
(1343,1,'admin','172.19.0.1',1,1774724882),
(1344,1,'admin','172.19.0.1',1,1774724882),
(1345,1,'admin','172.19.0.1',1,1774724882),
(1346,8,'department.head','172.19.0.1',1,1774724981),
(1347,8,'department.head','172.19.0.1',1,1774725029),
(1348,8,'department.head','172.19.0.1',1,1774725030),
(1349,8,'department.head','172.19.0.1',1,1774725071),
(1350,8,'department.head','172.19.0.1',1,1774725109),
(1351,1,'admin','172.19.0.1',1,1774725184),
(1352,1,'admin','172.19.0.1',1,1774725184),
(1353,1,'admin','172.19.0.1',1,1774725184),
(1354,1,'admin','172.19.0.1',1,1774725185),
(1355,1,'admin','172.19.0.1',1,1774725185),
(1356,1,'admin','172.19.0.1',1,1774725185),
(1357,1,'admin','172.19.0.1',1,1774725634),
(1358,8,'department.head','172.19.0.1',1,1774725635),
(1359,9,'clinician.primary','172.19.0.1',1,1774725635),
(1360,11,'registry.operator','172.19.0.1',1,1774725635),
(1361,12,'records.office','172.19.0.1',1,1774725635),
(1362,10,'nurse.coordinator','172.19.0.1',1,1774725635),
(1363,1,'admin','172.19.0.1',1,1774725681),
(1364,1,'admin','172.19.0.1',1,1774725681),
(1365,1,'admin','172.19.0.1',1,1774725681),
(1366,1,'admin','172.19.0.1',1,1774725681),
(1367,1,'admin','172.19.0.1',1,1774725682),
(1368,1,'admin','172.19.0.1',1,1774725682),
(1369,1,'admin','172.19.0.1',1,1774725682),
(1370,1,'admin','172.19.0.1',1,1774725701),
(1371,1,'admin','172.19.0.1',1,1774726307),
(1372,1,'admin','172.19.0.1',1,1774726324),
(1373,1,'admin','172.19.0.1',1,1774726328),
(1374,8,'department.head','172.19.0.1',1,1774726328),
(1375,9,'clinician.primary','172.19.0.1',1,1774726328),
(1376,11,'registry.operator','172.19.0.1',1,1774726328),
(1377,12,'records.office','172.19.0.1',1,1774726329),
(1378,10,'nurse.coordinator','172.19.0.1',1,1774726329),
(1379,1,'admin','172.19.0.1',1,1774726331),
(1380,1,'admin','172.19.0.1',1,1774726331),
(1381,1,'admin','172.19.0.1',1,1774726331),
(1382,1,'admin','172.19.0.1',1,1774726332),
(1383,1,'admin','172.19.0.1',1,1774726332),
(1384,1,'admin','172.19.0.1',1,1774726332),
(1385,1,'admin','172.19.0.1',1,1774726332),
(1386,1,'admin','172.19.0.1',1,1774726334),
(1387,1,'admin','172.19.0.1',1,1774726345),
(1388,1,'admin','172.19.0.1',1,1774726394),
(1389,1,'admin','172.19.0.1',1,1774726402),
(1390,1,'admin','172.19.0.1',1,1774726621),
(1391,9,'clinician.primary','172.19.0.1',1,1774726629),
(1392,9,'clinician.primary','172.19.0.1',1,1774726725),
(1393,10,'nurse.coordinator','172.19.0.1',1,1774726732),
(1394,10,'nurse.coordinator','172.19.0.1',1,1774726828),
(1395,1,'admin','172.19.0.1',1,1774733347),
(1396,1,'admin','172.19.0.1',1,1774733349),
(1397,8,'department.head','172.19.0.1',1,1774733349),
(1398,9,'clinician.primary','172.19.0.1',1,1774733349),
(1399,11,'registry.operator','172.19.0.1',1,1774733349),
(1400,12,'records.office','172.19.0.1',1,1774733350),
(1401,10,'nurse.coordinator','172.19.0.1',1,1774733350),
(1402,1,'admin','172.23.0.1',1,1774775580),
(1403,1,'admin','172.23.0.1',1,1774775594),
(1404,1,'admin','172.23.0.1',1,1774783568),
(1405,9,'clinician.primary','172.23.0.1',1,1774783568),
(1406,10,'nurse.coordinator','172.23.0.1',1,1774783568),
(1407,1,'admin','172.23.0.1',1,1774783611),
(1408,1,'admin','172.23.0.1',1,1774783628),
(1409,1,'admin','172.23.0.1',1,1774783817),
(1410,1,'admin','172.23.0.1',1,1774783912),
(1411,1,'admin','172.23.0.1',1,1774783969),
(1412,1,'admin','172.23.0.1',1,1774783969),
(1413,9,'clinician.primary','172.23.0.1',1,1774783969),
(1414,10,'nurse.coordinator','172.23.0.1',1,1774783969),
(1415,1,'admin','172.23.0.1',1,1774783971),
(1416,1,'admin','172.23.0.1',1,1774784028),
(1417,9,'clinician.primary','172.23.0.1',1,1774784028),
(1418,10,'nurse.coordinator','172.23.0.1',1,1774784028),
(1419,9,'clinician.primary','172.23.0.1',1,1774784040),
(1420,10,'nurse.coordinator','172.23.0.1',1,1774784040),
(1421,1,'admin','172.23.0.1',1,1774784455),
(1422,1,'admin','172.23.0.1',1,1774784455),
(1423,9,'clinician.primary','172.23.0.1',1,1774784455),
(1424,9,'clinician.primary','172.23.0.1',1,1774784455),
(1425,9,'clinician.primary','172.23.0.1',1,1774784455),
(1426,10,'nurse.coordinator','172.23.0.1',1,1774784455),
(1427,1,'admin','172.23.0.1',1,1774784457),
(1428,1,'admin','172.23.0.1',1,1774786220),
(1429,9,'clinician.primary','172.23.0.1',1,1774786220),
(1430,10,'nurse.coordinator','172.23.0.1',1,1774786220),
(1431,1,'admin','172.23.0.1',1,1774786283),
(1432,1,'admin','172.23.0.1',1,1774786309),
(1433,1,'admin','172.23.0.1',1,1774786379),
(1434,1,'admin','172.23.0.1',1,1774786379),
(1435,9,'clinician.primary','172.23.0.1',1,1774786379),
(1436,10,'nurse.coordinator','172.23.0.1',1,1774786379),
(1437,1,'admin','172.23.0.1',1,1774786438),
(1438,9,'clinician.primary','172.23.0.1',1,1774786438),
(1439,10,'nurse.coordinator','172.23.0.1',1,1774786438),
(1440,1,'admin','172.23.0.1',1,1774786438),
(1441,1,'admin','172.23.0.1',1,1774786438),
(1442,1,'admin','172.23.0.1',1,1774786439),
(1443,1,'admin','172.23.0.1',1,1774786439),
(1444,1,'admin','172.23.0.1',1,1774786439),
(1445,1,'admin','172.23.0.1',1,1774786439),
(1446,1,'admin','172.23.0.1',1,1774786461),
(1447,8,'department.head','172.23.0.1',1,1774786461),
(1448,9,'clinician.primary','172.23.0.1',1,1774786462),
(1449,11,'registry.operator','172.23.0.1',1,1774786462),
(1450,12,'records.office','172.23.0.1',1,1774786462),
(1451,10,'nurse.coordinator','172.23.0.1',1,1774786462);
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_users_notifications`
--

LOCK TABLES `app_users_notifications` WRITE;
/*!40000 ALTER TABLE `app_users_notifications` DISABLE KEYS */;
INSERT INTO `app_users_notifications` VALUES
(1,0,26,1,'Новый материал базы документов: 1','new_item',1774365718,1),
(2,0,23,3,'Новая заявка: покупка принтера','new_item',1774536023,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_who_is_online`
--

LOCK TABLES `app_who_is_online` WRITE;
/*!40000 ALTER TABLE `app_who_is_online` DISABLE KEYS */;
INSERT INTO `app_who_is_online` VALUES
(1,1,1774786461),
(2,2,1774710072),
(3,3,1774710072),
(4,4,1774710073),
(5,5,1774710073),
(6,6,1774710467),
(7,7,1774710570),
(8,8,1774786461),
(9,9,1774786462),
(10,11,1774786462),
(11,12,1774786462),
(12,10,1774786462);
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

-- Dump completed on 2026-03-29 12:15:36
