<?php

if (!function_exists('platform_sync_fetch_row_by_sql'))
{
    function platform_sync_fetch_row_by_sql($sql)
    {
        $query = db_query($sql);
        return db_fetch_array($query);
    }
}

if (!function_exists('platform_sync_fetch_all_rows'))
{
    function platform_sync_fetch_all_rows($sql)
    {
        $rows = [];
        $query = db_query($sql);
        while ($row = db_fetch_array($query))
        {
            $rows[] = $row;
        }

        return $rows;
    }
}

if (!function_exists('platform_sync_choice_id_by_name'))
{
    function platform_sync_choice_id_by_name($field_id, $name)
    {
        $name = trim((string) $name);
        if ($name === '')
        {
            return 0;
        }

        $row = platform_sync_fetch_row_by_sql(
            "select id from app_fields_choices where fields_id='" . (int) $field_id . "' and name='" . db_input($name) . "' limit 1"
        );

        return $row ? (int) $row['id'] : 0;
    }
}

if (!function_exists('platform_sync_choice_name_by_id'))
{
    function platform_sync_choice_name_by_id($field_id, $choice_id)
    {
        if (!(int) $choice_id)
        {
            return '';
        }

        $row = platform_sync_fetch_row_by_sql(
            "select name from app_fields_choices where fields_id='" . (int) $field_id . "' and id='" . (int) $choice_id . "' limit 1"
        );

        return $row ? $row['name'] : '';
    }
}

if (!function_exists('platform_sync_default_choice_id'))
{
    function platform_sync_default_choice_id($field_id)
    {
        $row = platform_sync_fetch_row_by_sql(
            "select id from app_fields_choices where fields_id='" . (int) $field_id . "' and is_default=1 order by sort_order, id limit 1"
        );

        if ($row)
        {
            return (int) $row['id'];
        }

        $row = platform_sync_fetch_row_by_sql(
            "select id from app_fields_choices where fields_id='" . (int) $field_id . "' order by sort_order, id limit 1"
        );

        return $row ? (int) $row['id'] : 0;
    }
}

if (!function_exists('platform_sync_item_exists'))
{
    function platform_sync_item_exists($entity_id, $item_id)
    {
        $row = platform_sync_fetch_row_by_sql(
            "select id from app_entity_" . (int) $entity_id . " where id='" . (int) $item_id . "' limit 1"
        );

        return (bool) $row;
    }
}

if (!function_exists('platform_sync_normalize_csv_value'))
{
    function platform_sync_normalize_csv_value($value)
    {
        $value = trim((string) $value);
        if ($value === '')
        {
            return '';
        }

        $parts = array_filter(array_map('trim', explode(',', $value)));
        return implode(',', $parts);
    }
}

if (!function_exists('platform_sync_first_csv_value'))
{
    function platform_sync_first_csv_value($value)
    {
        $parts = array_filter(array_map('trim', explode(',', (string) $value)));
        return count($parts) ? $parts[0] : '';
    }
}

if (!function_exists('platform_sync_field_id_by_name'))
{
    function platform_sync_field_id_by_name($entity_id, $name, $field_type = '')
    {
        $sql = "select id from app_fields where entities_id='" . (int) $entity_id . "' and name='" . db_input($name) . "'";

        if (trim((string) $field_type) !== '')
        {
            $sql .= " and type='" . db_input($field_type) . "'";
        }

        $sql .= " order by id limit 1";
        $row = platform_sync_fetch_row_by_sql($sql);

        return $row ? (int) $row['id'] : 0;
    }
}

if (!function_exists('platform_sync_field_id_by_type'))
{
    function platform_sync_field_id_by_type($entity_id, $field_type)
    {
        $row = platform_sync_fetch_row_by_sql(
            "select id from app_fields where entities_id='" . (int) $entity_id . "' and type='" . db_input($field_type) . "' order by id limit 1"
        );

        return $row ? (int) $row['id'] : 0;
    }
}

if (!function_exists('platform_sync_public_base_url'))
{
    function platform_sync_public_base_url()
    {
        $candidates = [
            getenv('PLATFORM_PUBLIC_BASE_URL'),
            getenv('DOCFLOW_PUBLIC_BASE'),
            getenv('RUKOVODITEL_PUBLIC_URL'),
            'https://localhost:18443',
        ];

        foreach ($candidates as $candidate)
        {
            $candidate = trim((string) $candidate);
            if ($candidate !== '')
            {
                return rtrim($candidate, '/');
            }
        }

        return 'https://localhost:18443';
    }
}

if (!function_exists('platform_sync_public_naudoc_base_url'))
{
    function platform_sync_public_naudoc_base_url()
    {
        $candidates = [
            getenv('NAUDOC_PUBLIC_URL'),
            getenv('DOCFLOW_DOCS_BASE'),
            platform_sync_public_base_url() . '/docs',
            'https://localhost:18443/docs',
        ];

        foreach ($candidates as $candidate)
        {
            $candidate = trim((string) $candidate);
            if ($candidate !== '')
            {
                return rtrim($candidate, '/');
            }
        }

        return 'https://localhost:18443/docs';
    }
}

if (!function_exists('platform_sync_internal_naudoc_base_url'))
{
    function platform_sync_internal_naudoc_base_url()
    {
        $candidates = [
            getenv('NAUDOC_SYNC_BASE_URL'),
            getenv('NAUDOC_BASE_URL'),
            'http://host.docker.internal:18080/docs',
        ];

        foreach ($candidates as $candidate)
        {
            $candidate = trim((string) $candidate);
            if ($candidate !== '')
            {
                return rtrim($candidate, '/');
            }
        }

        return 'http://host.docker.internal:18080/docs';
    }
}

if (!function_exists('platform_sync_naudoc_username'))
{
    function platform_sync_naudoc_username()
    {
        return trim((string) (getenv('NAUDOC_USERNAME') ?: 'admin'));
    }
}

if (!function_exists('platform_sync_naudoc_password'))
{
    function platform_sync_naudoc_password()
    {
        return (string) (getenv('NAUDOC_PASSWORD') ?: 'admin');
    }
}

if (!function_exists('platform_sync_normalize_naudoc_url'))
{
    function platform_sync_normalize_naudoc_url($url)
    {
        $url = trim((string) $url);
        if ($url === '')
        {
            return '';
        }

        $public_base = platform_sync_public_naudoc_base_url();
        $known_bases = array_filter(array_unique([
            rtrim($public_base, '/'),
            'http://localhost:18080/docs',
            'http://host.docker.internal:18080/docs',
            'https://localhost:18443/docs',
        ]));

        foreach ($known_bases as $base)
        {
            $base = rtrim($base, '/');
            if (strpos($url, $base) === 0)
            {
                return $public_base . substr($url, strlen($base));
            }
        }

        return $url;
    }
}

if (!function_exists('platform_sync_bridge_base_url'))
{
    function platform_sync_bridge_base_url()
    {
        return rtrim(getenv('BRIDGE_BASE_URL') ?: 'http://host.docker.internal:18082', '/');
    }
}

if (!function_exists('platform_sync_item_url'))
{
    function platform_sync_item_url($entity_id, $item_id)
    {
        return platform_sync_public_base_url() . '/index.php?module=items/info&path=' . (int) $entity_id . '-' . (int) $item_id;
    }
}

if (!function_exists('platform_sync_lower_text'))
{
    function platform_sync_lower_text($value)
    {
        $value = trim((string) $value);
        if ($value === '')
        {
            return '';
        }

        if (function_exists('mb_strtolower'))
        {
            return mb_strtolower($value, 'UTF-8');
        }

        return strtolower($value);
    }
}

if (!function_exists('platform_sync_http_request'))
{
    function platform_sync_http_request($method, $url, array $headers = [], $content = null)
    {
        $header_text = '';
        if (count($headers))
        {
            $header_text = implode("\r\n", $headers) . "\r\n";
        }

        $options = [
            'method' => strtoupper($method),
            'header' => $header_text,
            'ignore_errors' => true,
            'timeout' => 10,
        ];

        if ($content !== null)
        {
            $options['content'] = $content;
        }

        $context = stream_context_create(['http' => $options]);
        $response_body = @file_get_contents($url, false, $context);
        $response_headers = $http_response_header ?? [];
        $status_code = 0;

        if (isset($response_headers[0]) && preg_match('#\s(\d{3})\s#', $response_headers[0], $matches))
        {
            $status_code = (int) $matches[1];
        }

        return [
            'status_code' => $status_code,
            'body' => $response_body === false ? '' : $response_body,
            'ok' => $status_code >= 200 && $status_code < 300,
        ];
    }
}

if (!function_exists('platform_sync_http_json_request'))
{
    function platform_sync_http_json_request($method, $url, $payload)
    {
        $content = json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

        return platform_sync_http_request(
            $method,
            $url,
            ['Content-Type: application/json', 'Accept: application/json'],
            $content
        );
    }
}

if (!function_exists('platform_sync_http_json_post'))
{
    function platform_sync_http_json_post($url, $payload)
    {
        return platform_sync_http_json_request('POST', $url, $payload);
    }
}

if (!function_exists('platform_sync_http_json_get'))
{
    function platform_sync_http_json_get($url)
    {
        return platform_sync_http_request('GET', $url, ['Accept: application/json']);
    }
}

if (!function_exists('platform_sync_http_json_get_decoded'))
{
    function platform_sync_http_json_get_decoded($url)
    {
        $response = platform_sync_http_json_get($url);
        if (!$response['ok'])
        {
            throw new RuntimeException('HTTP GET failed with status ' . $response['status_code'] . ': ' . ($response['body'] ?: ''));
        }

        $decoded = json_decode($response['body'], true);
        if (!is_array($decoded))
        {
            throw new RuntimeException('HTTP response is not valid JSON: ' . $response['body']);
        }

        return $decoded;
    }
}

if (!function_exists('platform_sync_bridge_lookup_link'))
{
    function platform_sync_bridge_lookup_link($external_entity, $external_item_id)
    {
        $response = platform_sync_http_json_get(
            platform_sync_bridge_base_url() . '/links/lookup?' . http_build_query([
                'external_system' => 'rukovoditel',
                'external_entity' => $external_entity,
                'external_item_id' => (string) $external_item_id,
            ])
        );

        if (!$response['ok'])
        {
            return null;
        }

        $decoded = json_decode($response['body'], true);
        return is_array($decoded) ? $decoded : null;
    }
}

if (!function_exists('platform_sync_bridge_choose_sync_status'))
{
    function platform_sync_bridge_choose_sync_status($external_entity, $external_item_id, $default_sync_status)
    {
        $existing = platform_sync_bridge_lookup_link($external_entity, $external_item_id);
        if (!$existing)
        {
            return $default_sync_status;
        }

        $existing_status = trim((string) ($existing['sync_status'] ?? ''));
        if ($existing_status === '')
        {
            return $default_sync_status;
        }

        if ($default_sync_status === 'linked' && $existing_status !== 'pending_nau_doc')
        {
            return $existing_status;
        }

        if ($default_sync_status === 'pending_nau_doc' && !in_array($existing_status, ['linked', 'pending_nau_doc'], true))
        {
            return $existing_status;
        }

        return $default_sync_status;
    }
}

if (!function_exists('platform_sync_bridge_fetch_field_mappings'))
{
    function platform_sync_bridge_fetch_field_mappings($source_entity, $target_system = 'bridge', $target_entity = 'metadata', $throw_on_error = false)
    {
        static $cache = [];

        $source_entity = trim((string) $source_entity);
        if ($source_entity === '')
        {
            return [];
        }

        $target_system = trim((string) $target_system);
        $cache_key = $source_entity . '|' . $target_system . '|' . (($target_entity === null) ? '*' : trim((string) $target_entity)) . '|' . ($throw_on_error ? 'throw' : 'soft');
        if (isset($cache[$cache_key]))
        {
            return $cache[$cache_key];
        }

        $query = [
            'source_system' => 'rukovoditel',
            'source_entity' => $source_entity,
            'target_system' => $target_system,
            'direction' => 'push',
            'active' => 1,
        ];
        if ($target_entity !== null)
        {
            $query['target_entity'] = trim((string) $target_entity);
        }

        $url = platform_sync_bridge_base_url() . '/field-mappings?' . http_build_query($query);

        try
        {
            if ($throw_on_error)
            {
                $rows = platform_sync_http_json_get_decoded($url);
            }
            else
            {
                $response = platform_sync_http_json_get($url);
                $rows = $response['ok'] ? json_decode($response['body'], true) : [];
            }
        }
        catch (Throwable $e)
        {
            $rows = [];
            if ($throw_on_error)
            {
                throw $e;
            }
        }

        $cache[$cache_key] = is_array($rows) ? $rows : [];
        return $cache[$cache_key];
    }
}

if (!function_exists('platform_sync_bridge_build_mapped_values'))
{
    function platform_sync_bridge_build_mapped_values($source_entity, array $source_values, $target_system = 'bridge', $target_entity = 'metadata')
    {
        $mappings = platform_sync_bridge_fetch_field_mappings($source_entity, $target_system, $target_entity);
        if (!count($mappings))
        {
            return [];
        }

        $mapped = [];
        foreach ($mappings as $mapping)
        {
            $source_key = trim((string) ($mapping['source_field_key'] ?? ''));
            $target_key = trim((string) ($mapping['target_field_key'] ?? ''));

            if ($source_key === '' || $target_key === '' || !array_key_exists($source_key, $source_values))
            {
                continue;
            }

            $value = $source_values[$source_key];
            if ($value === '' || $value === null)
            {
                continue;
            }

            $mapped[$target_key] = $value;
        }

        return $mapped;
    }
}

if (!function_exists('platform_sync_bridge_build_metadata_from_mappings'))
{
    function platform_sync_bridge_build_metadata_from_mappings($source_entity, array $source_values, array $fallback_metadata)
    {
        $metadata = platform_sync_bridge_build_mapped_values($source_entity, $source_values, 'bridge', 'metadata');
        return count($metadata) ? $metadata : $fallback_metadata;
    }
}

if (!function_exists('platform_sync_bridge_build_naudoc_projection'))
{
    function platform_sync_bridge_build_naudoc_projection($source_entity, array $source_values)
    {
        $mappings = platform_sync_bridge_fetch_field_mappings($source_entity, 'naudoc', null);
        if (!count($mappings))
        {
            return [];
        }

        $projection = [];
        foreach ($mappings as $mapping)
        {
            $source_key = trim((string) ($mapping['source_field_key'] ?? ''));
            $target_entity = trim((string) ($mapping['target_entity'] ?? 'document'));
            $target_key = trim((string) ($mapping['target_field_key'] ?? ''));

            if ($source_key === '' || $target_key === '' || $target_entity === '' || !array_key_exists($source_key, $source_values))
            {
                continue;
            }

            $value = $source_values[$source_key];
            if ($value === '' || $value === null)
            {
                continue;
            }

            if (!isset($projection[$target_entity]) || !is_array($projection[$target_entity]))
            {
                $projection[$target_entity] = [];
            }

            $projection[$target_entity][$target_key] = $value;
        }

        return $projection;
    }
}

if (!function_exists('platform_sync_bridge_attach_naudoc_projection'))
{
    function platform_sync_bridge_attach_naudoc_projection(array $metadata, array $projection)
    {
        if (count($projection))
        {
            $metadata['naudoc_projection'] = $projection;
        }

        return $metadata;
    }
}

if (!function_exists('platform_sync_bridge_upsert_link'))
{
    function platform_sync_bridge_upsert_link($payload)
    {
        $response = platform_sync_http_json_request('POST', platform_sync_bridge_base_url() . '/links/upsert', $payload);
        if (!$response['ok'])
        {
            throw new RuntimeException(
                'Bridge upsert failed with status ' . $response['status_code'] . ': ' . $response['body']
            );
        }

        $decoded = json_decode($response['body'], true);
        if (!is_array($decoded))
        {
            throw new RuntimeException('Bridge response is not valid JSON: ' . $response['body']);
        }

        return $decoded;
    }
}

if (!function_exists('platform_sync_bridge_report_sync_failure'))
{
    function platform_sync_bridge_report_sync_failure($job_name, $external_entity, $external_item_id, $message, array $context = [], $link_id = 0)
    {
        $payload = [
            'source' => 'rukovoditel_sync',
            'job_name' => $job_name,
            'external_system' => 'rukovoditel',
            'external_entity' => $external_entity,
            'external_item_id' => (string) $external_item_id,
            'link_id' => (int) $link_id,
            'message' => $message,
            'context' => $context,
        ];

        return platform_sync_http_json_post(platform_sync_bridge_base_url() . '/sync-failures', $payload);
    }
}

if (!function_exists('platform_sync_bridge_resolve_sync_failure'))
{
    function platform_sync_bridge_resolve_sync_failure($job_name, $external_entity, $external_item_id, array $result = [], $link_id = 0)
    {
        $payload = [
            'source' => 'rukovoditel_sync',
            'job_name' => $job_name,
            'external_system' => 'rukovoditel',
            'external_entity' => $external_entity,
            'external_item_id' => (string) $external_item_id,
            'link_id' => (int) $link_id,
            'result' => $result,
        ];

        return platform_sync_http_json_post(platform_sync_bridge_base_url() . '/sync-failures/resolve', $payload);
    }
}

if (!function_exists('platform_sync_bridge_fetch_status_mappings'))
{
    function platform_sync_bridge_fetch_status_mappings($throw_on_error = false)
    {
        static $cache = [];
        $cache_key = $throw_on_error ? 'throw' : 'soft';

        if (isset($cache[$cache_key]))
        {
            return $cache[$cache_key];
        }

        $url = platform_sync_bridge_base_url() . '/status-mappings?active=1';

        try
        {
            if ($throw_on_error)
            {
                $rows = platform_sync_http_json_get_decoded($url);
            }
            else
            {
                $response = platform_sync_http_json_get($url);
                $rows = $response['ok'] ? json_decode($response['body'], true) : [];
            }
        }
        catch (Throwable $e)
        {
            $rows = [];
            if ($throw_on_error)
            {
                throw $e;
            }
        }

        $cache[$cache_key] = is_array($rows) ? $rows : [];
        return $cache[$cache_key];
    }
}

if (!function_exists('platform_sync_bridge_metadata_key'))
{
    function platform_sync_bridge_metadata_key($source_entity, $logical_source_key, $default_key = '')
    {
        $default_key = trim((string) $default_key) !== '' ? trim((string) $default_key) : trim((string) $logical_source_key);

        foreach (platform_sync_bridge_fetch_field_mappings($source_entity, 'bridge', 'metadata', false) as $mapping)
        {
            if (trim((string) ($mapping['source_field_key'] ?? '')) !== trim((string) $logical_source_key))
            {
                continue;
            }

            $target_key = trim((string) ($mapping['target_field_key'] ?? ''));
            if ($target_key !== '')
            {
                return $target_key;
            }
        }

        return $default_key;
    }
}

if (!function_exists('platform_sync_bridge_metadata_value'))
{
    function platform_sync_bridge_metadata_value($metadata, $source_entity, $logical_source_key, $default_key = '')
    {
        if (!is_array($metadata))
        {
            return null;
        }

        $resolved_key = platform_sync_bridge_metadata_key($source_entity, $logical_source_key, $default_key);
        if (array_key_exists($resolved_key, $metadata))
        {
            return $metadata[$resolved_key];
        }

        $fallback_key = trim((string) $default_key) !== '' ? trim((string) $default_key) : trim((string) $logical_source_key);
        if (array_key_exists($fallback_key, $metadata))
        {
            return $metadata[$fallback_key];
        }

        return null;
    }
}

if (!function_exists('platform_sync_bridge_find_status_mapping'))
{
    function platform_sync_bridge_find_status_mapping($sync_status)
    {
        $status = platform_sync_lower_text($sync_status);
        if ($status === '')
        {
            return null;
        }

        foreach (platform_sync_bridge_fetch_status_mappings(false) as $mapping)
        {
            $match_type = platform_sync_lower_text($mapping['match_type'] ?? 'contains');
            $match_value = platform_sync_lower_text($mapping['match_value'] ?? '');
            if ($match_value === '')
            {
                continue;
            }

            if ($match_type === 'exact' && $status === $match_value)
            {
                return $mapping;
            }

            if ($match_type === 'prefix' && strpos($status, $match_value) === 0)
            {
                return $mapping;
            }

            if ($match_type === 'contains' && strpos($status, $match_value) !== false)
            {
                return $mapping;
            }
        }

        return null;
    }
}
