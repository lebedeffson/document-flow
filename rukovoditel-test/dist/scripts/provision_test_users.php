<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';
require_once 'includes/libs/PasswordHash.php';

function console_log($message)
{
    echo $message . PHP_EOL;
}

function fetch_user_by_username($username)
{
    $query = db_query("select * from app_entity_1 where field_12='" . db_input($username) . "' limit 1");
    return db_fetch_array($query);
}

function update_user_profile($username, array $data)
{
    $user = fetch_user_by_username($username);
    if (!$user)
    {
        console_log("Skipped profile sync for {$username}: user not found");
        return 0;
    }

    db_perform('app_entity_1', $data, 'update', "id='" . db_input($user['id']) . "'");
    console_log("Updated profile {$username} (#{$user['id']})");
    return (int) $user['id'];
}

function ensure_test_user($username, $group_id, $first_name, $last_name, $email, $password, $skin = 'light')
{
    $language = defined('CFG_APP_LANGUAGE') ? CFG_APP_LANGUAGE : '';
    $hasher = new PasswordHash(11, false);
    $user = fetch_user_by_username($username);

    $sql_data = [
        'field_5' => 1,
        'field_6' => (int) $group_id,
        'field_7' => $first_name,
        'field_8' => $last_name,
        'field_9' => $email,
        'field_12' => $username,
        'field_13' => $language,
        'field_14' => $skin,
        'password' => $hasher->HashPassword($password),
        'is_email_verified' => 1,
        'date_updated' => time(),
    ];

    if (!$user)
    {
        $sql_data['date_added'] = time();
        $sql_data['created_by'] = 0;
        $sql_data['parent_item_id'] = 0;
        $sql_data['multiple_access_groups'] = '';

        db_perform('app_entity_1', $sql_data);
        $user_id = db_insert_id();
        console_log("Created test user {$username} (#{$user_id})");
        return (int) $user_id;
    }

    $user_id = (int) $user['id'];
    db_perform('app_entity_1', $sql_data, 'update', "id='" . db_input($user_id) . "'");
    console_log("Updated test user {$username} (#{$user_id})");
    return $user_id;
}

update_user_profile('admin', [
    'field_7' => 'Иван Иванович',
    'field_8' => 'Иванов',
    'field_9' => 'admin@example.local',
    'date_updated' => time(),
]);

$password = 'rolepass123';
$users = [
    [
        'username' => 'manager.test',
        'group_id' => 4,
        'first_name' => 'Мария',
        'last_name' => 'Заведующая',
        'email' => 'manager.test@example.local',
    ],
    [
        'username' => 'employee.test',
        'group_id' => 5,
        'first_name' => 'Илья',
        'last_name' => 'Врач',
        'email' => 'employee.test@example.local',
    ],
    [
        'username' => 'user.demo',
        'group_id' => 5,
        'first_name' => 'Елена',
        'last_name' => 'Сотрудник',
        'email' => 'user.demo@example.local',
    ],
    [
        'username' => 'requester.test',
        'group_id' => 6,
        'first_name' => 'Ольга',
        'last_name' => 'Регистратор',
        'email' => 'requester.test@example.local',
    ],
    [
        'username' => 'office.test',
        'group_id' => 7,
        'first_name' => 'Анна',
        'last_name' => 'Делопроизводитель',
        'email' => 'office.test@example.local',
    ],
];

foreach ($users as $user)
{
    ensure_test_user(
        $user['username'],
        $user['group_id'],
        $user['first_name'],
        $user['last_name'],
        $user['email'],
        $password
    );
}

console_log('');
console_log('Provisioned role test users:');
console_log('  admin / admin123  -> Иванов Иван Иванович');
console_log('  manager.test / rolepass123');
console_log('  employee.test / rolepass123');
console_log('  user.demo / rolepass123');
console_log('  requester.test / rolepass123');
console_log('  office.test / rolepass123');
