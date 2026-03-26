<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';

function console_log($message)
{
    echo $message . PHP_EOL;
}

function naudoc_sync_fetch_base_url()
{
    $value = getenv('NAUDOC_SYNC_BASE_URL');
    if (!$value)
    {
        $value = getenv('NAUDOC_BASE_URL');
    }

    if (!$value)
    {
        $value = 'http://host.docker.internal:18080/docs';
    }

    return rtrim($value, '/');
}

function naudoc_sync_public_base_url()
{
    $value = getenv('NAUDOC_PUBLIC_URL');
    if (!$value)
    {
        $value = 'https://localhost:18443/docs';
    }

    return rtrim($value, '/');
}

function naudoc_sync_username()
{
    return getenv('NAUDOC_USERNAME') ?: 'admin';
}

function naudoc_sync_password()
{
    return getenv('NAUDOC_PASSWORD') ?: 'admin';
}

function naudoc_profiles_cache_path()
{
    return DIR_FS_CACHE . 'naudoc_profiles.json';
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

$members_html = decode_naudoc_html(http_get_body(naudoc_sync_fetch_base_url() . '/storage/members/'));
$usernames = extract_member_usernames($members_html);

$summary = [
    'synced_at' => date('c'),
    'base_url' => naudoc_sync_public_base_url(),
    'profiles' => [],
];

$matched = 0;
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

    $summary['profiles'][$username] = [
        'username' => $username,
        'display_name' => $display_name,
        'profile_url' => $urls['profile_url'],
        'folder_url' => $urls['folder_url'],
        'matched_rukovoditel_user_id' => $user ? (int) $user['id'] : 0,
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
        console_log('Found NauDoc user ' . $username . ' without Rukovoditel match');
    }
}

ksort($summary['profiles']);
write_cache_file($summary);

console_log('');
console_log('NauDoc profile sync summary:');
console_log('  scanned: ' . $seen);
console_log('  matched: ' . $matched);
console_log('  cache: ' . naudoc_profiles_cache_path());
