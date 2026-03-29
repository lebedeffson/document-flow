<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';
require_once 'includes/libs/PasswordHash.php';
require_once 'includes/functions/platform_sync.php';

function console_log($message)
{
    echo $message . PHP_EOL;
}

function env_value($key, $default = '')
{
    $value = getenv($key);

    if ($value === false)
    {
        return $default;
    }

    $value = trim((string) $value);
    return strlen($value) ? $value : $default;
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

function deactivate_user_if_exists($username)
{
    $user = fetch_user_by_username($username);
    if (!$user)
    {
        return;
    }

    db_perform('app_entity_1', ['field_5' => 0, 'date_updated' => time()], 'update', "id='" . db_input($user['id']) . "'");
    console_log("Deactivated legacy user {$username} (#{$user['id']})");
}

function update_user_password($username, $password)
{
    $user = fetch_user_by_username($username);
    if (!$user)
    {
        console_log("Skipped password rotation for {$username}: user not found");
        return;
    }

    $hasher = new PasswordHash(11, false);
    db_perform(
        'app_entity_1',
        [
            'password' => $hasher->HashPassword($password),
            'date_updated' => time(),
        ],
        'update',
        "id='" . db_input($user['id']) . "'"
    );

    console_log("Updated password for {$username} (#{$user['id']})");
}

function build_rukovoditel_display_name($user)
{
    if (!$user)
    {
        return '';
    }

    $first_name = trim((string) ($user['field_7'] ?? ''));
    $last_name = trim((string) ($user['field_8'] ?? ''));
    return trim($first_name . ' ' . $last_name);
}

function rukovoditel_role_meta($user)
{
    $group_id = (int) ($user['field_6'] ?? 0);
    $map = [
        0 => ['role_key' => 'admin', 'role_label' => 'Администратор платформы'],
        4 => ['role_key' => 'manager', 'role_label' => 'Заведующий отделением / руководитель подразделения'],
        5 => ['role_key' => 'employee', 'role_label' => 'Врач / сотрудник подразделения'],
        8 => ['role_key' => 'nurse_coordinator', 'role_label' => 'Старшая медсестра / координатор отделения'],
        6 => ['role_key' => 'requester', 'role_label' => 'Регистратура / заявитель'],
        7 => ['role_key' => 'office', 'role_label' => 'Канцелярия / делопроизводство'],
    ];

    return $map[$group_id] ?? ['role_key' => '', 'role_label' => ''];
}

function upsert_bridge_user_profile(array $payload)
{
    try
    {
        $response = platform_sync_http_json_post(platform_sync_bridge_base_url() . '/user-profiles/upsert', $payload);
        if (!$response['ok'])
        {
            throw new RuntimeException('Unexpected status ' . $response['status_code'] . ' for Bridge user profile sync: ' . $response['body']);
        }

        return true;
    }
    catch (RuntimeException $exception)
    {
        console_log('Bridge user profile sync warning: ' . $exception->getMessage());
        return false;
    }
}

function sync_bridge_local_profile($username)
{
    $user = fetch_user_by_username($username);
    if (!$user || (int) ($user['field_5'] ?? 0) !== 1)
    {
        console_log("Skipped Bridge local profile sync for {$username}: active user not found");
        return;
    }

    $role_meta = rukovoditel_role_meta($user);
    upsert_bridge_user_profile([
        'source_system' => 'rukovoditel',
        'source_username' => (string) ($user['field_12'] ?? ''),
        'source_display_name' => build_rukovoditel_display_name($user),
        'source_email' => (string) ($user['field_9'] ?? ''),
        'source_department' => '',
        'source_role_key' => $role_meta['role_key'],
        'source_role_label' => $role_meta['role_label'],
        'source_profile_url' => platform_sync_item_url(1, (int) $user['id']),
        'source_folder_url' => platform_sync_public_base_url() . '/index.php?module=items/items&path=1',
        'linked_system' => 'rukovoditel',
        'linked_user_id' => (string) $user['id'],
        'linked_username' => (string) ($user['field_12'] ?? ''),
        'linked_display_name' => build_rukovoditel_display_name($user),
        'linked_email' => (string) ($user['field_9'] ?? ''),
        'linked_department' => '',
        'linked_role_key' => $role_meta['role_key'],
        'linked_role_label' => $role_meta['role_label'],
        'sync_status' => 'matched',
        'notes' => 'Локальный профиль Rukovoditel синхронизирован из provisioning role-аккаунтов.',
        'metadata' => [
            'source' => 'provision_test_users',
            'match_method' => 'local_rukovoditel_profile',
            'is_active' => 1,
        ],
    ]);

    console_log("Synced Bridge local profile {$username}");
}

function ensure_role_user($username, $group_id, $first_name, $last_name, $email, $password, $skin = 'light')
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
        console_log("Created role user {$username} (#{$user_id})");
        return (int) $user_id;
    }

    $user_id = (int) $user['id'];
    db_perform('app_entity_1', $sql_data, 'update', "id='" . db_input($user_id) . "'");
    console_log("Updated role user {$username} (#{$user_id})");
    return $user_id;
}

update_user_profile('admin', [
    'field_7' => 'Иван Иванович',
    'field_8' => 'Иванов',
    'field_9' => 'admin@example.local',
    'date_updated' => time(),
]);

$admin_password = env_value('DOCFLOW_ADMIN_PASSWORD', 'admin123');
$password = env_value('DOCFLOW_ROLE_DEFAULT_PASSWORD', 'rolepass123');
update_user_password('admin', $admin_password);

$users = [
    [
        'username' => env_value('DOCFLOW_MANAGER_USERNAME', 'department.head'),
        'group_id' => 4,
        'first_name' => 'Мария',
        'last_name' => 'Заведующая',
        'email' => 'department.head@hospital.local',
        'legacy_usernames' => ['manager.test', 'department.head'],
    ],
    [
        'username' => env_value('DOCFLOW_EMPLOYEE_USERNAME', 'clinician.primary'),
        'group_id' => 5,
        'first_name' => 'Илья',
        'last_name' => 'Врач',
        'email' => 'clinician.primary@hospital.local',
        'legacy_usernames' => ['employee.test', 'user.demo', 'clinician.primary'],
    ],
    [
        'username' => env_value('DOCFLOW_NURSE_USERNAME', 'nurse.coordinator'),
        'group_id' => 8,
        'first_name' => 'Наталья',
        'last_name' => 'Старшая медсестра',
        'email' => 'nurse.coordinator@hospital.local',
        'legacy_usernames' => ['nurse.test', 'nurse.coordinator'],
    ],
    [
        'username' => env_value('DOCFLOW_REQUESTER_USERNAME', 'registry.operator'),
        'group_id' => 6,
        'first_name' => 'Ольга',
        'last_name' => 'Регистратор',
        'email' => 'registry.operator@hospital.local',
        'legacy_usernames' => ['requester.test', 'registry.operator'],
    ],
    [
        'username' => env_value('DOCFLOW_OFFICE_USERNAME', 'records.office'),
        'group_id' => 7,
        'first_name' => 'Анна',
        'last_name' => 'Делопроизводитель',
        'email' => 'records.office@hospital.local',
        'legacy_usernames' => ['office.test', 'records.office'],
    ],
];

foreach ($users as $user)
{
    ensure_role_user(
        $user['username'],
        $user['group_id'],
        $user['first_name'],
        $user['last_name'],
        $user['email'],
        $password
    );
}

$legacy_usernames = ['user.demo'];
foreach ($users as $user)
{
    foreach (($user['legacy_usernames'] ?? []) as $legacy_username)
    {
        if ($legacy_username !== $user['username'])
        {
            $legacy_usernames[] = $legacy_username;
        }
    }
}

foreach (array_unique($legacy_usernames) as $legacy_username)
{
    deactivate_user_if_exists($legacy_username);
}

sync_bridge_local_profile('admin');
foreach ($users as $user)
{
    sync_bridge_local_profile($user['username']);
}

console_log('');
console_log('Provisioned role users:');
console_log('  admin / password from DOCFLOW_ADMIN_PASSWORD (' . strlen($admin_password) . ' chars) -> Иванов Иван Иванович');
foreach ($users as $user)
{
    console_log('  ' . $user['username'] . ' / password from DOCFLOW_ROLE_DEFAULT_PASSWORD');
}
