<?php

// define database connection
$db_host = getenv('RUKOVODITEL_DB_HOST') ?: 'rukovoditel_db';
$db_port = getenv('RUKOVODITEL_DB_PORT') ?: '3306';
$db_name = getenv('RUKOVODITEL_DB_NAME') ?: 'rukovoditel';
$db_user = getenv('RUKOVODITEL_DB_USER') ?: 'rukovoditel';
$db_password = getenv('RUKOVODITEL_DB_PASSWORD') ?: 'rukovoditel';

define('DB_SERVER', $db_host . ':' . $db_port); // eg, localhost - should not be empty for productive servers
define('DB_SERVER_USERNAME', $db_user);
define('DB_SERVER_PASSWORD', $db_password);
define('DB_SERVER_PORT', $db_port);
define('DB_DATABASE', $db_name);
