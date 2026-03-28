<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';
require 'includes/functions/platform_sync.php';

function console_log($message)
{
    echo $message . PHP_EOL;
}

function naudoc_sync_fetch_base_url()
{
    return platform_sync_internal_naudoc_base_url();
}

function naudoc_sync_public_base_url()
{
    return platform_sync_public_naudoc_base_url();
}

function naudoc_sync_username()
{
    return platform_sync_naudoc_username();
}

function naudoc_sync_password()
{
    return platform_sync_naudoc_password();
}

function naudoc_profiles_cache_path()
{
    return DIR_FS_CACHE . 'naudoc_profiles.json';
}

function bridge_base_url()
{
    return platform_sync_bridge_base_url();
}

function http_get_body($url)
{
    $auth = base64_encode(naudoc_sync_username() . ':' . naudoc_sync_password());

    $context = stream_context_create([
        'http' => [
            'method' => 'GET',
            'header' => "Authorization: Basic {$auth}\r\n" .
                "Accept: text/html,application/xhtml+xml\r\n" .
                "User-Agent: NauDocProfileSync/1.0\r\n",
            'timeout' => 15,
            'ignore_errors' => true,
        ],
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
        ],
    ]);

    $body = @file_get_contents($url, false, $context);
    if ($body === false)
    {
        throw new RuntimeException('Unable to fetch ' . $url);
    }

    $headers = $http_response_header ?? [];
    $status_code = 0;
    if (isset($headers[0]) && preg_match('#\s(\d{3})\s#', $headers[0], $matches))
    {
        $status_code = (int) $matches[1];
    }

    if ($status_code < 200 || $status_code >= 300)
    {
        throw new RuntimeException('Unexpected status ' . $status_code . ' for ' . $url);
    }

    return $body;
}

function decode_naudoc_html($body)
{
    $decoded = @iconv('windows-1251', 'UTF-8//IGNORE', $body);
    if ($decoded === false || !strlen($decoded))
    {
        return $body;
    }

    return $decoded;
}

function normalize_spaces($value)
{
    $value = html_entity_decode(strip_tags((string) $value), ENT_QUOTES, 'UTF-8');
    $value = preg_replace('/\s+/u', ' ', $value);
    return trim((string) $value);
}

function split_display_name($display_name)
{
    $parts = preg_split('/\s+/u', trim($display_name));
    $parts = array_values(array_filter($parts, 'strlen'));

    if (count($parts) >= 2)
    {
        $last_name = array_shift($parts);
        $first_name = implode(' ', $parts);
        return [$first_name, $last_name];
    }

    if (count($parts) === 1)
    {
        return [$parts[0], ''];
    }

    return ['', ''];
}

function fetch_rukovoditel_user_by_username($username)
{
    $query = db_query("select * from app_entity_1 where field_12='" . db_input($username) . "' limit 1");
    return db_fetch_array($query);
}

function fetch_unique_rukovoditel_user_by_display_name($first_name, $last_name)
{
    if (!strlen($first_name) || !strlen($last_name))
    {
        return false;
    }

    $query = db_query(
        "select * from app_entity_1 where field_7='" . db_input($first_name) . "' and field_8='" . db_input($last_name) . "' order by id limit 2"
    );

    $rows = [];
    while ($row = db_fetch_array($query))
    {
        $rows[] = $row;
    }

    return count($rows) === 1 ? $rows[0] : false;
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

function extract_member_usernames($html)
{
    $usernames = [];

    if (preg_match_all('#storage/members/([^/"\'?]+)/inFrame\?link=view#u', $html, $matches))
    {
        foreach ($matches[1] as $username)
        {
            $username = trim((string) $username);
            if (!strlen($username))
            {
                continue;
            }

            if (in_array($username, ['user_defaults', 'portal_membership'], true))
            {
                continue;
            }

            $usernames[$username] = true;
        }
    }

    return array_keys($usernames);
}

function extract_display_name($html)
{
    if (preg_match('#<title>\s*(.*?)\s*,&nbsp;#su', $html, $matches))
    {
        return normalize_spaces($matches[1]);
    }

    if (preg_match('#<a href="\./view"\s+target="workspace">(.*?)</a>#su', $html, $matches))
    {
        return normalize_spaces($matches[1]);
    }

    return '';
}

function build_profile_urls($username)
{
    $fetch_base = naudoc_sync_fetch_base_url();
    $public_base = naudoc_sync_public_base_url();

    return [
        'fetch_profile_url' => $fetch_base . '/storage/members/' . rawurlencode($username) . '/inFrame?link=view',
        'profile_url' => $public_base . '/storage/members/' . rawurlencode($username) . '/inFrame?link=view',
        'folder_url' => $public_base . '/storage/members/' . rawurlencode($username) . '/folder_contents',
    ];
}

function write_cache_file(array $payload)
{
    $path = naudoc_profiles_cache_path();
    $dir = dirname($path);

    if (!is_dir($dir))
    {
        mkdir($dir, 0775, true);
    }

    file_put_contents(
        $path,
        json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)
    );
}

function upsert_bridge_user_profile(array $payload)
{
    try
    {
        $response = platform_sync_http_json_post(bridge_base_url() . '/user-profiles/upsert', $payload);
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

$members_html = decode_naudoc_html(http_get_body(naudoc_sync_fetch_base_url() . '/storage/members/'));
$usernames = extract_member_usernames($members_html);

$summary = [
    'synced_at' => date('c'),
    'base_url' => naudoc_sync_public_base_url(),
    'profiles' => [],
];

$matched = 0;
$needs_review = 0;
$seen = 0;

console_log('Syncing NauDoc member profiles...');

foreach ($usernames as $username)
{
    $seen++;
    $urls = build_profile_urls($username);
    $profile_html = decode_naudoc_html(http_get_body($urls['fetch_profile_url']));
    $display_name = extract_display_name($profile_html);

    list($first_name, $last_name) = split_display_name($display_name);
    $user = fetch_rukovoditel_user_by_username($username);
    $suggested_user = (!$user) ? fetch_unique_rukovoditel_user_by_display_name($first_name, $last_name) : false;
    $role_meta = $user ? rukovoditel_role_meta($user) : ['role_key' => '', 'role_label' => ''];
    $suggested_role_meta = $suggested_user ? rukovoditel_role_meta($suggested_user) : ['role_key' => '', 'role_label' => ''];

    $sync_status = 'unmatched';
    $notes = 'Профиль найден в NauDoc, но пока не сопоставлен с пользователем Rukovoditel.';
    $match_method = 'none';

    if ($user)
    {
        $sync_status = 'matched';
        $notes = 'Профиль автоматически сопоставлен по username.';
        $match_method = 'username_exact';
    }
    elseif ($suggested_user)
    {
        $sync_status = 'needs_review';
        $notes = 'Найдена вероятная связка по отображаемому имени. Нужна проверка администратора.';
        $match_method = 'display_name_suggestion';
        $needs_review++;
    }

    $summary['profiles'][$username] = [
        'username' => $username,
        'display_name' => $display_name,
        'profile_url' => $urls['profile_url'],
        'folder_url' => $urls['folder_url'],
        'matched_rukovoditel_user_id' => $user ? (int) $user['id'] : 0,
        'suggested_rukovoditel_user_id' => $suggested_user ? (int) $suggested_user['id'] : 0,
        'sync_status' => $sync_status,
    ];

    if ($user)
    {
        $matched++;
        $update_data = [
            'date_updated' => time(),
        ];

        if (strlen($first_name))
        {
            $update_data['field_7'] = $first_name;
        }

        if (strlen($last_name))
        {
            $update_data['field_8'] = $last_name;
        }

        db_perform('app_entity_1', $update_data, 'update', "id='" . db_input($user['id']) . "'");
        console_log('Matched NauDoc user ' . $username . ' -> Rukovoditel #' . $user['id'] . ' [' . $display_name . ']');
    }
    else
    {
        if ($suggested_user)
        {
            console_log('Found NauDoc user ' . $username . ' with suggested Rukovoditel match #' . $suggested_user['id'] . ' [' . build_rukovoditel_display_name($suggested_user) . ']');
        }
        else
        {
            console_log('Found NauDoc user ' . $username . ' without Rukovoditel match');
        }
    }

    upsert_bridge_user_profile([
        'source_system' => 'naudoc',
        'source_username' => $username,
        'source_display_name' => $display_name,
        'source_email' => '',
        'source_department' => '',
        'source_role_key' => '',
        'source_role_label' => '',
        'source_profile_url' => $urls['profile_url'],
        'source_folder_url' => $urls['folder_url'],
        'linked_system' => $user ? 'rukovoditel' : '',
        'linked_user_id' => $user ? (string) $user['id'] : '',
        'linked_username' => $user ? (string) $user['field_12'] : '',
        'linked_display_name' => build_rukovoditel_display_name($user),
        'linked_email' => $user ? (string) ($user['field_9'] ?? '') : '',
        'linked_department' => '',
        'linked_role_key' => $role_meta['role_key'],
        'linked_role_label' => $role_meta['role_label'],
        'sync_status' => $sync_status,
        'notes' => $notes,
        'metadata' => [
            'source' => 'sync_naudoc_profiles',
            'display_name' => $display_name,
            'matched_rukovoditel_user_id' => $user ? (int) $user['id'] : 0,
            'match_method' => $match_method,
            'suggested_user_id' => $suggested_user ? (int) $suggested_user['id'] : 0,
            'suggested_username' => $suggested_user ? (string) ($suggested_user['field_12'] ?? '') : '',
            'suggested_display_name' => $suggested_user ? build_rukovoditel_display_name($suggested_user) : '',
            'suggested_email' => $suggested_user ? (string) ($suggested_user['field_9'] ?? '') : '',
            'suggested_department' => '',
            'suggested_role_key' => $suggested_role_meta['role_key'],
            'suggested_role_label' => $suggested_role_meta['role_label'],
        ],
    ]);
}

ksort($summary['profiles']);
write_cache_file($summary);

console_log('');
console_log('NauDoc profile sync summary:');
console_log('  scanned: ' . $seen);
console_log('  matched: ' . $matched);
console_log('  needs_review: ' . $needs_review);
console_log('  cache: ' . naudoc_profiles_cache_path());
