<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';
require 'includes/functions/platform_sync.php';

const PROJECT_ENTITY_ID = 21;
const REQUEST_ENTITY_ID = 23;
const DOC_CARD_ENTITY_ID = 25;

const PROJECT_NAUDOC_LINK_FIELD_ID = 230;
const REQUEST_STATUS_FIELD_ID = 186;
const REQUEST_DOC_CARD_LINK_FIELD_ID = 240;
const REQUEST_NAUDOC_LINK_FIELD_ID = 241;

const DOC_STATUS_FIELD_ID = 244;
const DOC_NAUDOC_LINK_FIELD_ID = 250;
const DOC_REQUEST_LINK_FIELD_ID = 252;

function console_log($message)
{
    echo $message . PHP_EOL;
}

function get_project_doc_card_link_field_id()
{
    static $field_id = null;

    if ($field_id === null)
    {
        $field_id = platform_sync_field_id_by_name(PROJECT_ENTITY_ID, 'Связанная карточка документа');
    }

    return (int) $field_id;
}

function get_project_doc_sync_status_field_id()
{
    static $field_id = null;

    if ($field_id === null)
    {
        $field_id = platform_sync_field_id_by_name(PROJECT_ENTITY_ID, 'Статус документа / интеграции');
    }

    return (int) $field_id;
}

function get_request_doc_sync_status_field_id()
{
    static $field_id = null;

    if ($field_id === null)
    {
        $field_id = platform_sync_field_id_by_name(REQUEST_ENTITY_ID, 'Статус документа / интеграции');
    }

    return (int) $field_id;
}

function report_sync_failure($link, $message)
{
    $response = platform_sync_bridge_report_sync_failure(
        'pull_bridge',
        trim((string) ($link['external_entity'] ?? '')),
        trim((string) ($link['external_item_id'] ?? '')),
        $message,
        [
            'link_id' => (int) ($link['id'] ?? 0),
            'sync_status' => trim((string) ($link['sync_status'] ?? '')),
            'naudoc_url' => trim((string) ($link['naudoc_url'] ?? '')),
        ],
        (int) ($link['id'] ?? 0)
    );
    if (!$response['ok'])
    {
        console_log('Warning: failed to write pull failure log: ' . $response['status_code'] . ' ' . $response['body']);
    }
}

function resolve_sync_failure($link, $result = [])
{
    $response = platform_sync_bridge_resolve_sync_failure(
        'pull_bridge',
        trim((string) ($link['external_entity'] ?? '')),
        trim((string) ($link['external_item_id'] ?? '')),
        $result,
        (int) ($link['id'] ?? 0)
    );
    if (!$response['ok'])
    {
        console_log('Warning: failed to resolve pull failure log: ' . $response['status_code'] . ' ' . $response['body']);
    }
}

function fetch_bridge_links($external_entity, $item_id = 0)
{
    $query = [
        'external_system' => 'rukovoditel',
        'external_entity' => $external_entity,
    ];

    if ($item_id > 0)
    {
        $query['external_item_id'] = (string) $item_id;
    }

    return platform_sync_http_json_get_decoded(platform_sync_bridge_base_url() . '/links?' . http_build_query($query));
}

function map_doc_status_name($sync_status)
{
    $mapping = platform_sync_bridge_find_status_mapping($sync_status);
    if ($mapping && trim((string) ($mapping['doc_status_name'] ?? '')) !== '')
    {
        return trim((string) $mapping['doc_status_name']);
    }

    $status = platform_sync_lower_text($sync_status);
    if ($status === '' || $status === 'pending_nau_doc')
    {
        return '';
    }
    if (strpos($status, 'чернов') !== false || strpos($status, 'draft') !== false)
    {
        return 'Черновик';
    }
    if (strpos($status, 'архив') !== false || strpos($status, 'archive') !== false)
    {
        return 'Архивирован';
    }
    if (strpos($status, 'ознаком') !== false || strpos($status, 'familiar') !== false)
    {
        return 'На ознакомлении';
    }
    if (strpos($status, 'подпис') !== false || strpos($status, 'sign') !== false)
    {
        return 'Подписан';
    }
    if (strpos($status, 'утверж') !== false || strpos($status, 'approve') !== false)
    {
        return 'На утверждении';
    }
    if (
        $status === 'linked' ||
        strpos($status, 'соглас') !== false ||
        strpos($status, 'review') !== false ||
        strpos($status, 'register') !== false
    )
    {
        return 'На согласовании';
    }

    return '';
}

function map_request_status_name($sync_status)
{
    $mapping = platform_sync_bridge_find_status_mapping($sync_status);
    if ($mapping && trim((string) ($mapping['request_status_name'] ?? '')) !== '')
    {
        return trim((string) $mapping['request_status_name']);
    }

    $status = platform_sync_lower_text($sync_status);
    if ($status === '' || $status === 'pending_nau_doc')
    {
        return '';
    }
    if (strpos($status, 'чернов') !== false || strpos($status, 'draft') !== false)
    {
        return 'Новая';
    }
    if (strpos($status, 'отклон') !== false || strpos($status, 'reject') !== false)
    {
        return 'Отклонена';
    }
    if (strpos($status, 'ожидает') !== false || strpos($status, 'waiting') !== false)
    {
        return 'Ожидает заявителя';
    }
    if (strpos($status, 'архив') !== false || strpos($status, 'archive') !== false || strpos($status, 'подпис') !== false || strpos($status, 'sign') !== false)
    {
        return 'Выполнена';
    }
    if (
        $status === 'linked' ||
        strpos($status, 'соглас') !== false ||
        strpos($status, 'review') !== false ||
        strpos($status, 'approve') !== false ||
        strpos($status, 'register') !== false
    )
    {
        return 'На согласовании';
    }

    return '';
}

function map_doc_sync_status_name($sync_status, $naudoc_url)
{
    $mapping = platform_sync_bridge_find_status_mapping($sync_status);
    if ($mapping)
    {
        $mapped_status = trim((string) ($mapping['integration_status_name'] ?? ''));
        if ($mapped_status === 'Ошибка синхронизации')
        {
            return $mapped_status;
        }
    }

    $status = platform_sync_lower_text($sync_status);
    $has_url = trim((string) $naudoc_url) !== '';

    if ($status === '' || $status === 'pending_nau_doc' || !$has_url)
    {
        return 'Ожидает документ';
    }

    if ($mapping && trim((string) ($mapping['integration_status_name'] ?? '')) !== '')
    {
        return trim((string) $mapping['integration_status_name']);
    }

    if (strpos($status, 'архив') !== false || strpos($status, 'archive') !== false)
    {
        return 'Архивирован';
    }
    if (strpos($status, 'ознаком') !== false || strpos($status, 'familiar') !== false)
    {
        return 'На ознакомлении';
    }
    if (strpos($status, 'подпис') !== false || strpos($status, 'sign') !== false)
    {
        return 'Подписан';
    }
    if (strpos($status, 'утверж') !== false || strpos($status, 'approve') !== false)
    {
        return 'На утверждении';
    }
    if (strpos($status, 'соглас') !== false || strpos($status, 'review') !== false || strpos($status, 'register') !== false)
    {
        return 'На согласовании';
    }
    if (strpos($status, 'чернов') !== false || strpos($status, 'draft') !== false)
    {
        return 'Черновик';
    }

    return 'Связано';
}

function update_item($entity_id, $item_id, $updates)
{
    if (!count($updates))
    {
        return false;
    }

    items::update_by_id($entity_id, $item_id, $updates, [
        'run_email_rules' => false,
        'run_process' => false,
    ]);

    return true;
}

function sync_doc_card_record($doc_card_id, $naudoc_url, $sync_status, $request_id = 0)
{
    if (!$doc_card_id || !platform_sync_item_exists(DOC_CARD_ENTITY_ID, $doc_card_id))
    {
        return false;
    }

    $doc_card = db_find('app_entity_' . DOC_CARD_ENTITY_ID, $doc_card_id);
    $updates = [];

    if ($naudoc_url !== '' && (string) $doc_card['field_' . DOC_NAUDOC_LINK_FIELD_ID] !== $naudoc_url)
    {
        $updates['field_' . DOC_NAUDOC_LINK_FIELD_ID] = $naudoc_url;
    }

    if ($request_id > 0 && (string) $doc_card['field_' . DOC_REQUEST_LINK_FIELD_ID] !== (string) $request_id)
    {
        $updates['field_' . DOC_REQUEST_LINK_FIELD_ID] = (string) $request_id;
    }

    $doc_status_name = map_doc_status_name($sync_status);
    $doc_status_id = platform_sync_choice_id_by_name(DOC_STATUS_FIELD_ID, $doc_status_name);
    if ($doc_status_id > 0 && (int) $doc_card['field_' . DOC_STATUS_FIELD_ID] !== $doc_status_id)
    {
        $updates['field_' . DOC_STATUS_FIELD_ID] = (string) $doc_status_id;
    }

    return update_item(DOC_CARD_ENTITY_ID, $doc_card_id, $updates);
}

function sync_doc_card_link($link)
{
    $doc_card_id = (int) $link['external_item_id'];
    if (!$doc_card_id || !platform_sync_item_exists(DOC_CARD_ENTITY_ID, $doc_card_id))
    {
        console_log('Skipped document card link #' . ($link['id'] ?? '?') . ': target card not found.');
        return false;
    }

    $metadata = isset($link['metadata']) && is_array($link['metadata']) ? $link['metadata'] : [];
    $request_id = (int) platform_sync_bridge_metadata_value($metadata, 'document_cards', 'source_request_id');
    $updated = sync_doc_card_record(
        $doc_card_id,
        trim((string) ($link['naudoc_url'] ?? '')),
        trim((string) ($link['sync_status'] ?? '')),
        $request_id
    );

    console_log(
        'Document card #' . $doc_card_id .
        ($updated ? ' updated from bridge.' : ' already актуальна.')
    );

    return $updated;
}

function sync_request_link($link)
{
    $request_id = (int) $link['external_item_id'];
    if (!$request_id || !platform_sync_item_exists(REQUEST_ENTITY_ID, $request_id))
    {
        console_log('Skipped request link #' . ($link['id'] ?? '?') . ': target request not found.');
        return false;
    }

    $request = db_find('app_entity_' . REQUEST_ENTITY_ID, $request_id);
    $metadata = isset($link['metadata']) && is_array($link['metadata']) ? $link['metadata'] : [];
    $naudoc_url = platform_sync_normalize_naudoc_url($link['naudoc_url'] ?? '');
    $doc_card_id = (int) platform_sync_bridge_metadata_value($metadata, 'service_requests', 'doc_card_id');
    $request_doc_sync_status_field_id = get_request_doc_sync_status_field_id();

    $updates = [];
    if ($naudoc_url !== '' && (string) $request['field_' . REQUEST_NAUDOC_LINK_FIELD_ID] !== $naudoc_url)
    {
        $updates['field_' . REQUEST_NAUDOC_LINK_FIELD_ID] = $naudoc_url;
    }

    if ($doc_card_id > 0 && platform_sync_item_exists(DOC_CARD_ENTITY_ID, $doc_card_id) && (string) $request['field_' . REQUEST_DOC_CARD_LINK_FIELD_ID] !== (string) $doc_card_id)
    {
        $updates['field_' . REQUEST_DOC_CARD_LINK_FIELD_ID] = (string) $doc_card_id;
    }

    $request_status_name = map_request_status_name($link['sync_status'] ?? '');
    $request_status_id = platform_sync_choice_id_by_name(REQUEST_STATUS_FIELD_ID, $request_status_name);
    if ($request_status_id > 0 && (int) $request['field_' . REQUEST_STATUS_FIELD_ID] !== $request_status_id)
    {
        $updates['field_' . REQUEST_STATUS_FIELD_ID] = (string) $request_status_id;
    }

    $doc_sync_status_name = map_doc_sync_status_name($link['sync_status'] ?? '', $naudoc_url);
    $doc_sync_status_id = $request_doc_sync_status_field_id > 0
        ? platform_sync_choice_id_by_name($request_doc_sync_status_field_id, $doc_sync_status_name)
        : 0;
    if (
        $request_doc_sync_status_field_id > 0 &&
        $doc_sync_status_id > 0 &&
        (int) $request['field_' . $request_doc_sync_status_field_id] !== $doc_sync_status_id
    )
    {
        $updates['field_' . $request_doc_sync_status_field_id] = (string) $doc_sync_status_id;
    }

    $request_updated = update_item(REQUEST_ENTITY_ID, $request_id, $updates);
    $doc_card_updated = false;

    if ($doc_card_id > 0)
    {
        $doc_card_updated = sync_doc_card_record(
            $doc_card_id,
            $naudoc_url,
            trim((string) ($link['sync_status'] ?? '')),
            $request_id
        );
    }

    console_log(
        'Request #' . $request_id .
        (($request_updated || $doc_card_updated) ? ' updated from bridge.' : ' already актуальна.')
    );

    return $request_updated || $doc_card_updated;
}

function sync_project_link($link)
{
    $project_id = (int) $link['external_item_id'];
    if (!$project_id || !platform_sync_item_exists(PROJECT_ENTITY_ID, $project_id))
    {
        console_log('Skipped project link #' . ($link['id'] ?? '?') . ': target project not found.');
        return false;
    }

    $project = db_find('app_entity_' . PROJECT_ENTITY_ID, $project_id);
    $metadata = isset($link['metadata']) && is_array($link['metadata']) ? $link['metadata'] : [];
    $naudoc_url = platform_sync_normalize_naudoc_url($link['naudoc_url'] ?? '');
    $doc_card_id = (int) platform_sync_bridge_metadata_value($metadata, 'projects', 'doc_card_id');
    $project_doc_card_field_id = get_project_doc_card_link_field_id();
    $project_doc_sync_status_field_id = get_project_doc_sync_status_field_id();

    $updates = [];
    if ($naudoc_url !== '' && (string) $project['field_' . PROJECT_NAUDOC_LINK_FIELD_ID] !== $naudoc_url)
    {
        $updates['field_' . PROJECT_NAUDOC_LINK_FIELD_ID] = $naudoc_url;
    }

    if (
        $project_doc_card_field_id > 0 &&
        $doc_card_id > 0 &&
        platform_sync_item_exists(DOC_CARD_ENTITY_ID, $doc_card_id) &&
        (string) $project['field_' . $project_doc_card_field_id] !== (string) $doc_card_id
    )
    {
        $updates['field_' . $project_doc_card_field_id] = (string) $doc_card_id;
    }

    $doc_sync_status_name = map_doc_sync_status_name($link['sync_status'] ?? '', $naudoc_url);
    $doc_sync_status_id = $project_doc_sync_status_field_id > 0
        ? platform_sync_choice_id_by_name($project_doc_sync_status_field_id, $doc_sync_status_name)
        : 0;
    if (
        $project_doc_sync_status_field_id > 0 &&
        $doc_sync_status_id > 0 &&
        (int) $project['field_' . $project_doc_sync_status_field_id] !== $doc_sync_status_id
    )
    {
        $updates['field_' . $project_doc_sync_status_field_id] = (string) $doc_sync_status_id;
    }

    $project_updated = update_item(PROJECT_ENTITY_ID, $project_id, $updates);
    $doc_card_updated = false;

    if ($doc_card_id > 0)
    {
        $doc_card_updated = sync_doc_card_record(
            $doc_card_id,
            $naudoc_url,
            trim((string) ($link['sync_status'] ?? '')),
            0
        );
    }

    console_log(
        'Project #' . $project_id .
        (($project_updated || $doc_card_updated) ? ' updated from bridge.' : ' already актуален.')
    );

    return $project_updated || $doc_card_updated;
}

function parse_cli_options()
{
    global $argv;

    $options = [
        'project_id' => 0,
        'request_id' => 0,
        'doc_card_id' => 0,
        'only_linked' => false,
    ];

    foreach ($argv as $arg)
    {
        if (strpos($arg, '--request-id=') === 0)
        {
            $options['request_id'] = (int) substr($arg, strlen('--request-id='));
        }
        elseif (strpos($arg, '--project-id=') === 0)
        {
            $options['project_id'] = (int) substr($arg, strlen('--project-id='));
        }
        elseif (strpos($arg, '--doc-card-id=') === 0)
        {
            $options['doc_card_id'] = (int) substr($arg, strlen('--doc-card-id='));
        }
        elseif ($arg === '--only-linked')
        {
            $options['only_linked'] = true;
        }
    }

    return $options;
}

function should_process_link($link, $only_linked)
{
    if (!$only_linked)
    {
        return true;
    }

    return trim((string) ($link['naudoc_url'] ?? '')) !== '';
}

console_log('Pulling bridge updates into Rukovoditel...');

$options = parse_cli_options();

$has_specific_filter = $options['project_id'] > 0 || $options['request_id'] > 0 || $options['doc_card_id'] > 0;

$project_links = ($options['project_id'] > 0 || !$has_specific_filter)
    ? fetch_bridge_links('projects', $options['project_id'])
    : [];
$doc_links = ($options['doc_card_id'] > 0 || !$has_specific_filter)
    ? fetch_bridge_links('document_cards', $options['doc_card_id'])
    : [];
$request_links = ($options['request_id'] > 0 || !$has_specific_filter)
    ? fetch_bridge_links('service_requests', $options['request_id'])
    : [];

$processed = 0;
$updated = 0;
$failed = 0;

foreach ($project_links as $link)
{
    if (!should_process_link($link, $options['only_linked']))
    {
        continue;
    }

    try
    {
        $processed++;
        $changed = sync_project_link($link);
        resolve_sync_failure($link, ['updated' => $changed]);
        if ($changed)
        {
            $updated++;
        }
    }
    catch (Throwable $e)
    {
        $failed++;
        report_sync_failure($link, $e->getMessage());
        console_log('Failed pull for project #' . (int) $link['external_item_id'] . ': ' . $e->getMessage());
    }
}

foreach ($doc_links as $link)
{
    if (!should_process_link($link, $options['only_linked']))
    {
        continue;
    }

    try
    {
        $processed++;
        $changed = sync_doc_card_link($link);
        resolve_sync_failure($link, ['updated' => $changed]);
        if ($changed)
        {
            $updated++;
        }
    }
    catch (Throwable $e)
    {
        $failed++;
        report_sync_failure($link, $e->getMessage());
        console_log('Failed pull for document card #' . (int) $link['external_item_id'] . ': ' . $e->getMessage());
    }
}

foreach ($request_links as $link)
{
    if (!should_process_link($link, $options['only_linked']))
    {
        continue;
    }

    try
    {
        $processed++;
        $changed = sync_request_link($link);
        resolve_sync_failure($link, ['updated' => $changed]);
        if ($changed)
        {
            $updated++;
        }
    }
    catch (Throwable $e)
    {
        $failed++;
        report_sync_failure($link, $e->getMessage());
        console_log('Failed pull for request #' . (int) $link['external_item_id'] . ': ' . $e->getMessage());
    }
}

console_log('Bridge pull complete. Processed: ' . $processed . ', updated: ' . $updated . ', failed: ' . $failed);
