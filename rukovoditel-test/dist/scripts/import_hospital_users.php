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

function rukovoditel_role_meta_by_group($group_id)
{
    $map = [
        0 => ['role_key' => 'admin', 'role_label' => 'Администратор платформы'],
        4 => ['role_key' => 'manager', 'role_label' => 'Заведующий отделением / руководитель подразделения'],
        5 => ['role_key' => 'employee', 'role_label' => 'Врач / сотрудник подразделения'],
        8 => ['role_key' => 'nurse_coordinator', 'role_label' => 'Старшая медсестра / координатор отделения'],
        6 => ['role_key' => 'requester', 'role_label' => 'Регистратура / заявитель'],
        7 => ['role_key' => 'office', 'role_label' => 'Канцелярия / делопроизводство'],
    ];

    return $map[(int) $group_id] ?? ['role_key' => '', 'role_label' => ''];
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

function sync_bridge_local_profile($username, $department = '', $notes = '', $source = 'hospital_csv_import')
{
    $user = fetch_user_by_username($username);
    if (!$user)
    {
        console_log("Skipped Bridge local profile sync for {$username}: user not found");
        return;
    }

    $is_active = (int) ($user['field_5'] ?? 0) === 1;
    $role_meta = rukovoditel_role_meta_by_group((int) ($user['field_6'] ?? 0));
    upsert_bridge_user_profile([
        'source_system' => 'rukovoditel',
        'source_username' => (string) ($user['field_12'] ?? ''),
        'source_display_name' => build_rukovoditel_display_name($user),
        'source_email' => (string) ($user['field_9'] ?? ''),
        'source_department' => (string) $department,
        'source_role_key' => $role_meta['role_key'],
        'source_role_label' => $role_meta['role_label'],
        'source_profile_url' => platform_sync_item_url(1, (int) $user['id']),
        'source_folder_url' => platform_sync_public_base_url() . '/index.php?module=items/items&path=1',
        'linked_system' => 'rukovoditel',
        'linked_user_id' => (string) $user['id'],
        'linked_username' => (string) ($user['field_12'] ?? ''),
        'linked_display_name' => build_rukovoditel_display_name($user),
        'linked_email' => (string) ($user['field_9'] ?? ''),
        'linked_department' => (string) $department,
        'linked_role_key' => $role_meta['role_key'],
        'linked_role_label' => $role_meta['role_label'],
        'sync_status' => 'matched',
        'notes' => trim('Локальный профиль Rukovoditel синхронизирован из согласованного CSV-списка. ' . $notes),
        'metadata' => [
            'source' => $source,
            'match_method' => 'local_rukovoditel_profile',
            'is_active' => $is_active ? 1 : 0,
        ],
    ]);

    console_log("Synced Bridge local profile {$username}");
}

function csv_headers($handle)
{
    $headers = fgetcsv($handle);
    if (!is_array($headers))
    {
        return [];
    }

    if (isset($headers[0]))
    {
        $headers[0] = preg_replace('/^\xEF\xBB\xBF/', '', (string) $headers[0]);
    }

    return array_map(static function ($value)
    {
        return trim((string) $value);
    }, $headers);
}

function text_lower($value)
{
    $value = (string) $value;

    if (function_exists('mb_strtolower'))
    {
        return mb_strtolower($value);
    }

    return strtolower($value);
}

function text_contains($haystack, $needle)
{
    if (!strlen((string) $needle))
    {
        return false;
    }

    if (function_exists('mb_strpos'))
    {
        return mb_strpos((string) $haystack, (string) $needle) !== false;
    }

    return strpos((string) $haystack, (string) $needle) !== false;
}

function normalize_bool($value, $default = true)
{
    $value = trim((string) $value);

    if (!strlen($value))
    {
        return (bool) $default;
    }

    return in_array(text_lower($value), ['1', 'true', 'yes', 'y', 'on', 'да'], true);
}

function detect_group_id(array $row)
{
    if (isset($row['group_id']) && strlen(trim((string) $row['group_id'])) && is_numeric($row['group_id']))
    {
        return (int) $row['group_id'];
    }

    $label = text_lower(trim((string) ($row['group_name'] ?? $row['role_label'] ?? '')));
    $map = [
        0 => ['admin', 'администратор'],
        4 => ['завед', 'руковод', 'manager', 'head'],
        5 => ['врач', 'doctor', 'clinician', 'employee', 'сотрудник'],
        6 => ['регистрат', 'requester', 'registry', 'заявител'],
        7 => ['канцел', 'office', 'records'],
        8 => ['медсестр', 'nurse', 'координатор'],
    ];

    foreach ($map as $group_id => $needles)
    {
        foreach ($needles as $needle)
        {
            if (text_contains($label, $needle))
            {
                return (int) $group_id;
            }
        }
    }

    return 0;
}

function build_name_parts(array $row)
{
    $first_name = trim((string) ($row['first_name'] ?? ''));
    $last_name = trim((string) ($row['last_name'] ?? ''));

    if (strlen($first_name) || strlen($last_name))
    {
        return [
            'first_name' => $first_name,
            'last_name' => $last_name,
        ];
    }

    return [
        'first_name' => trim((string) ($row['full_name'] ?? '')),
        'last_name' => '',
    ];
}

function upsert_hospital_user(array $row, $default_role_password, $update_passwords)
{
    $username = trim((string) ($row['username'] ?? ''));
    $group_id = detect_group_id($row);
    $is_active = normalize_bool($row['is_active'] ?? '1', true);
    $name_parts = build_name_parts($row);
    $email = trim((string) ($row['email'] ?? ''));
    $language = defined('CFG_APP_LANGUAGE') ? CFG_APP_LANGUAGE : '';
    $password = trim((string) ($row['password'] ?? ''));
    $department = trim((string) ($row['department'] ?? ''));
    $notes = trim((string) ($row['notes'] ?? ''));

    if (!strlen($username))
    {
        throw new InvalidArgumentException('username is required');
    }

    if (!in_array($group_id, [0, 4, 5, 6, 7, 8], true))
    {
        throw new InvalidArgumentException('group_id is invalid for ' . $username);
    }

    $user = fetch_user_by_username($username);
    $hasher = new PasswordHash(11, false);
    $sql_data = [
        'field_5' => $is_active ? 1 : 0,
        'field_6' => $group_id,
        'field_7' => $name_parts['first_name'],
        'field_8' => $name_parts['last_name'],
        'field_9' => $email,
        'field_12' => $username,
        'field_13' => $language,
        'field_14' => 'light',
        'is_email_verified' => 1,
        'date_updated' => time(),
    ];

    $should_update_password = false;
    if (!$user)
    {
        $should_update_password = true;
    }
    elseif (strlen($password) || $update_passwords)
    {
        $should_update_password = true;
    }

    if ($should_update_password)
    {
        if (!strlen($password))
        {
            $password = $group_id === 0
                ? env_value('DOCFLOW_ADMIN_PASSWORD', 'admin123')
                : env_value('DOCFLOW_HOSPITAL_USER_DEFAULT_PASSWORD', $default_role_password);
        }

        $sql_data['password'] = $hasher->HashPassword($password);
    }

    if (!$user)
    {
        $sql_data['date_added'] = time();
        $sql_data['created_by'] = 0;
        $sql_data['parent_item_id'] = 0;
        $sql_data['multiple_access_groups'] = '';
        db_perform('app_entity_1', $sql_data);
        $user_id = db_insert_id();
        console_log("Created hospital user {$username} (#{$user_id})");
    }
    else
    {
        $user_id = (int) $user['id'];
        db_perform('app_entity_1', $sql_data, 'update', "id='" . db_input($user_id) . "'");
        console_log("Updated hospital user {$username} (#{$user_id})");
    }

    sync_bridge_local_profile($username, $department, $notes);

    return [
        'username' => $username,
        'group_id' => $group_id,
        'is_active' => $is_active ? 1 : 0,
        'department' => $department,
    ];
}

$args = $argv;
array_shift($args);

$csv_path = '';
$update_passwords = false;

foreach ($args as $arg)
{
    if ($arg === '--update-passwords')
    {
        $update_passwords = true;
        continue;
    }

    if (!strlen($csv_path))
    {
        $csv_path = $arg;
    }
}

if (!strlen($csv_path))
{
    fwrite(STDERR, "Usage: php scripts/import_hospital_users.php /path/to/users.csv [--update-passwords]" . PHP_EOL);
    exit(1);
}

if (!is_file($csv_path))
{
    fwrite(STDERR, "CSV file not found: {$csv_path}" . PHP_EOL);
    exit(1);
}

$default_role_password = env_value('DOCFLOW_HOSPITAL_USER_DEFAULT_PASSWORD', env_value('DOCFLOW_ROLE_DEFAULT_PASSWORD', 'rolepass123'));
$handle = fopen($csv_path, 'r');
if (!$handle)
{
    fwrite(STDERR, "Unable to open CSV file: {$csv_path}" . PHP_EOL);
    exit(1);
}

$headers = csv_headers($handle);
if (!count($headers))
{
    fclose($handle);
    fwrite(STDERR, "CSV file is empty: {$csv_path}" . PHP_EOL);
    exit(1);
}

$imported = 0;
$failures = 0;

while (($row = fgetcsv($handle)) !== false)
{
    if (!count($row) || (count($row) === 1 && !strlen(trim((string) $row[0]))))
    {
        continue;
    }

    $assoc = [];
    foreach ($headers as $index => $header)
    {
        $assoc[$header] = trim((string) ($row[$index] ?? ''));
    }

    try
    {
        upsert_hospital_user($assoc, $default_role_password, $update_passwords);
        $imported++;
    }
    catch (InvalidArgumentException $exception)
    {
        $failures++;
        console_log('Skipped row: ' . $exception->getMessage());
    }
}

fclose($handle);

console_log('');
console_log("Imported hospital users: {$imported}");
console_log("Skipped rows: {$failures}");

exit($failures > 0 ? 1 : 0);
