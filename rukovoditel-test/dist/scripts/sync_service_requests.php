<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';
require 'includes/functions/platform_sync.php';

const REQUEST_ENTITY_ID = 23;
const DOC_CARD_ENTITY_ID = 25;

const REQUEST_GROUP_FIELD_ID = 182;
const REQUEST_TYPE_FIELD_ID = 183;
const REQUEST_SUBJECT_FIELD_ID = 184;
const REQUEST_DESCRIPTION_FIELD_ID = 185;
const REQUEST_STATUS_FIELD_ID = 186;
const REQUEST_CHANNEL_FIELD_ID = 235;
const REQUEST_RESPONSIBLE_FIELD_ID = 236;
const REQUEST_DUE_DATE_FIELD_ID = 237;
const REQUEST_SERVICE_CATEGORY_FIELD_ID = 238;
const REQUEST_PROJECT_LINK_FIELD_ID = 239;
const REQUEST_DOC_CARD_LINK_FIELD_ID = 240;
const REQUEST_NAUDOC_LINK_FIELD_ID = 241;
const REQUEST_PRIORITY_FIELD_ID = 276;

const DOC_TITLE_FIELD_ID = 242;
const DOC_TYPE_FIELD_ID = 243;
const DOC_STATUS_FIELD_ID = 244;
const DOC_DATE_FIELD_ID = 246;
const DOC_OWNER_FIELD_ID = 247;
const DOC_VERSION_FIELD_ID = 249;
const DOC_NAUDOC_LINK_FIELD_ID = 250;
const DOC_PROJECT_LINK_FIELD_ID = 251;
const DOC_REQUEST_LINK_FIELD_ID = 252;
const DOC_DESCRIPTION_FIELD_ID = 253;

function get_doc_route_field_id()
{
    static $field_id = null;

    if ($field_id === null)
    {
        $field_id = platform_sync_field_id_by_name(DOC_CARD_ENTITY_ID, 'Маршрут документа');
    }

    if (!(int) $field_id)
    {
        throw new RuntimeException(
            "Field 'Маршрут документа' was not found for document cards. Run apply_process_model.sh first."
        );
    }

    return (int) $field_id;
}

function console_log($message)
{
    echo $message . PHP_EOL;
}

function report_sync_failure($message, $context = [])
{
    $response = platform_sync_bridge_report_sync_failure(
        'service_requests',
        'service_requests',
        (string) ($context['request_id'] ?? ''),
        $message,
        $context
    );
    if (!$response['ok'])
    {
        console_log('Warning: failed to write sync failure log: ' . $response['status_code'] . ' ' . $response['body']);
    }
}

function resolve_sync_failure($request_id, $result = [])
{
    $response = platform_sync_bridge_resolve_sync_failure(
        'service_requests',
        'service_requests',
        (int) $request_id,
        $result
    );
    if (!$response['ok'])
    {
        console_log('Warning: failed to resolve sync failure log: ' . $response['status_code'] . ' ' . $response['body']);
    }
}

function create_demo_request_if_needed()
{
    $existing = platform_sync_fetch_row_by_sql("select id from app_entity_" . REQUEST_ENTITY_ID . " limit 1");
    if ($existing)
    {
        console_log('Demo seed skipped: service request records already exist.');
        return;
    }

    $group_choice_id = platform_sync_default_choice_id(REQUEST_GROUP_FIELD_ID);
    $type_choice_id = platform_sync_choice_id_by_name(REQUEST_TYPE_FIELD_ID, 'Документооборот');
    $status_choice_id = platform_sync_choice_id_by_name(REQUEST_STATUS_FIELD_ID, 'Новая');
    $channel_choice_id = platform_sync_choice_id_by_name(REQUEST_CHANNEL_FIELD_ID, 'Веб-форма');
    $service_choice_id = platform_sync_choice_id_by_name(REQUEST_SERVICE_CATEGORY_FIELD_ID, 'Документы');
    $priority_choice_id = platform_sync_choice_id_by_name(REQUEST_PRIORITY_FIELD_ID, 'Высокий');

    $item_id = items::insert(REQUEST_ENTITY_ID, [
        'created_by' => 1,
        'parent_item_id' => 0,
        'field_' . REQUEST_GROUP_FIELD_ID => (string) $group_choice_id,
        'field_' . REQUEST_TYPE_FIELD_ID => (string) $type_choice_id,
        'field_' . REQUEST_SUBJECT_FIELD_ID => 'Тестовая заявка на подготовку документа',
        'field_' . REQUEST_DESCRIPTION_FIELD_ID => '<p>Автоматически созданная тестовая заявка для проверки связки Rukovoditel -> карточка документа -> middleware.</p>',
        'field_' . REQUEST_STATUS_FIELD_ID => (string) $status_choice_id,
        'field_' . REQUEST_CHANNEL_FIELD_ID => (string) $channel_choice_id,
        'field_' . REQUEST_RESPONSIBLE_FIELD_ID => '1',
        'field_' . REQUEST_DUE_DATE_FIELD_ID => (string) strtotime('+5 days'),
        'field_' . REQUEST_SERVICE_CATEGORY_FIELD_ID => (string) $service_choice_id,
        'field_' . REQUEST_PROJECT_LINK_FIELD_ID => '',
        'field_' . REQUEST_DOC_CARD_LINK_FIELD_ID => '',
        'field_' . REQUEST_NAUDOC_LINK_FIELD_ID => '',
        'field_' . REQUEST_PRIORITY_FIELD_ID => (string) $priority_choice_id,
    ]);

    if (!$item_id)
    {
        throw new RuntimeException('Failed to create demo service request.');
    }

    console_log('Created demo service request #' . $item_id);
}

function resolve_doc_type_choice($request_type_name)
{
    if ($request_type_name === 'Документооборот')
    {
        $preferred = platform_sync_choice_id_by_name(DOC_TYPE_FIELD_ID, 'Служебная записка');
        if ($preferred)
        {
            return $preferred;
        }
    }

    $fallback = platform_sync_choice_id_by_name(DOC_TYPE_FIELD_ID, 'Иное');
    if ($fallback)
    {
        return $fallback;
    }

    return platform_sync_default_choice_id(DOC_TYPE_FIELD_ID);
}

function resolve_sync_status($naudoc_url)
{
    return strlen(trim((string) $naudoc_url)) ? 'linked' : 'pending_nau_doc';
}

function ensure_doc_card_for_request($request)
{
    $request_id = (int) $request['id'];
    $request_title = trim((string) $request['field_' . REQUEST_SUBJECT_FIELD_ID]);
    $request_type_name = platform_sync_choice_name_by_id(REQUEST_TYPE_FIELD_ID, (int) $request['field_' . REQUEST_TYPE_FIELD_ID]);
    $request_url = platform_sync_item_url(REQUEST_ENTITY_ID, $request_id);
    $project_link = platform_sync_normalize_csv_value($request['field_' . REQUEST_PROJECT_LINK_FIELD_ID]);
    $request_naudoc_url = platform_sync_normalize_naudoc_url($request['field_' . REQUEST_NAUDOC_LINK_FIELD_ID]);
    $owner_id = platform_sync_first_csv_value($request['field_' . REQUEST_RESPONSIBLE_FIELD_ID]) ?: (string) $request['created_by'];
    $doc_card_id = (int) $request['field_' . REQUEST_DOC_CARD_LINK_FIELD_ID];

    $doc_status_id = platform_sync_choice_id_by_name(DOC_STATUS_FIELD_ID, 'Черновик');
    $doc_type_id = resolve_doc_type_choice($request_type_name);
    $doc_route_field_id = get_doc_route_field_id();
    $inferred_doc_route_label = platform_sync_infer_request_doc_route_label(
        $request_type_name,
        $request_title,
        (string) $request['field_' . REQUEST_DESCRIPTION_FIELD_ID]
    );
    $inferred_doc_route_id = platform_sync_doc_route_choice_id_by_label(
        $doc_route_field_id,
        $inferred_doc_route_label
    );

    if (!$doc_card_id || !platform_sync_item_exists(DOC_CARD_ENTITY_ID, $doc_card_id))
    {
        $insert_data = [
            'created_by' => (int) $request['created_by'],
            'parent_item_id' => 0,
            'field_' . DOC_TITLE_FIELD_ID => $request_title,
            'field_' . DOC_TYPE_FIELD_ID => (string) $doc_type_id,
            'field_' . DOC_STATUS_FIELD_ID => (string) $doc_status_id,
            'field_' . DOC_DATE_FIELD_ID => (string) time(),
            'field_' . DOC_OWNER_FIELD_ID => (string) $owner_id,
            'field_' . DOC_VERSION_FIELD_ID => '1.0',
            'field_' . DOC_NAUDOC_LINK_FIELD_ID => $request_naudoc_url,
            'field_' . DOC_PROJECT_LINK_FIELD_ID => $project_link,
            'field_' . DOC_REQUEST_LINK_FIELD_ID => (string) $request_id,
            'field_' . DOC_DESCRIPTION_FIELD_ID => '<p>Карточка создана автоматически из заявки #' . $request_id . '.</p>' . ($request['field_' . REQUEST_DESCRIPTION_FIELD_ID] ?: ''),
        ];

        if ($inferred_doc_route_id > 0)
        {
            $insert_data['field_' . $doc_route_field_id] = (string) $inferred_doc_route_id;
        }

        $doc_card_id = items::insert(DOC_CARD_ENTITY_ID, $insert_data);

        if (!$doc_card_id)
        {
            throw new RuntimeException('Failed to create document card for request #' . $request_id);
        }

        items::update_by_id(REQUEST_ENTITY_ID, $request_id, [
            'field_' . REQUEST_DOC_CARD_LINK_FIELD_ID => (string) $doc_card_id,
        ], [
            'run_email_rules' => false,
            'run_process' => false,
        ]);

        console_log('Created document card #' . $doc_card_id . ' for request #' . $request_id);
    }

    $doc_card = db_find('app_entity_' . DOC_CARD_ENTITY_ID, $doc_card_id);
    $doc_updates = [];
    if ((string) $doc_card['field_' . DOC_REQUEST_LINK_FIELD_ID] !== (string) $request_id)
    {
        $doc_updates['field_' . DOC_REQUEST_LINK_FIELD_ID] = (string) $request_id;
    }
    if ($project_link && (string) $doc_card['field_' . DOC_PROJECT_LINK_FIELD_ID] !== $project_link)
    {
        $doc_updates['field_' . DOC_PROJECT_LINK_FIELD_ID] = $project_link;
    }
    if ($request_naudoc_url && (string) $doc_card['field_' . DOC_NAUDOC_LINK_FIELD_ID] !== $request_naudoc_url)
    {
        $doc_updates['field_' . DOC_NAUDOC_LINK_FIELD_ID] = $request_naudoc_url;
    }
    if ($owner_id && (string) $doc_card['field_' . DOC_OWNER_FIELD_ID] !== (string) $owner_id)
    {
        $doc_updates['field_' . DOC_OWNER_FIELD_ID] = (string) $owner_id;
    }
    if (
        $inferred_doc_route_id > 0 &&
        (int) ($doc_card['field_' . $doc_route_field_id] ?? 0) <= 0
    )
    {
        $doc_updates['field_' . $doc_route_field_id] = (string) $inferred_doc_route_id;
    }
    if ($doc_updates)
    {
        items::update_by_id(DOC_CARD_ENTITY_ID, $doc_card_id, $doc_updates, [
            'run_email_rules' => false,
            'run_process' => false,
        ]);
        $doc_card = db_find('app_entity_' . DOC_CARD_ENTITY_ID, $doc_card_id);
    }

    $doc_card_url = platform_sync_item_url(DOC_CARD_ENTITY_ID, $doc_card_id);
    $doc_card_title = trim((string) $doc_card['field_' . DOC_TITLE_FIELD_ID]);
    $doc_card_naudoc_url = platform_sync_normalize_naudoc_url($doc_card['field_' . DOC_NAUDOC_LINK_FIELD_ID]);
    $doc_route_name = platform_sync_choice_name_by_id(
        $doc_route_field_id,
        (int) ($doc_card['field_' . $doc_route_field_id] ?? 0)
    );
    if (!$request_naudoc_url && $doc_card_naudoc_url)
    {
        items::update_by_id(REQUEST_ENTITY_ID, $request_id, [
            'field_' . REQUEST_NAUDOC_LINK_FIELD_ID => $doc_card_naudoc_url,
        ], [
            'run_email_rules' => false,
            'run_process' => false,
        ]);
        $request_naudoc_url = $doc_card_naudoc_url;
    }

    $sync_status = platform_sync_bridge_choose_sync_status(
        'service_requests',
        $request_id,
        resolve_sync_status($request_naudoc_url ?: $doc_card_naudoc_url)
    );
    $doc_card_sync_status = platform_sync_bridge_choose_sync_status(
        'document_cards',
        $doc_card_id,
        resolve_sync_status($doc_card_naudoc_url)
    );

    $request_source_values = [
        'request_id' => $request_id,
        'request_url' => $request_url,
        'request_title' => $request_title,
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'doc_card_title' => $doc_card_title,
        'responsible_user_id' => $owner_id,
        'document_route' => $doc_route_name,
    ];
    $request_metadata = platform_sync_bridge_build_metadata_from_mappings('service_requests', $request_source_values, [
        'request_id' => $request_id,
        'request_url' => $request_url,
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'responsible_user_id' => $owner_id,
        'document_route' => $doc_route_name,
    ]);
    $request_metadata = platform_sync_bridge_attach_naudoc_projection(
        $request_metadata,
        platform_sync_bridge_build_naudoc_projection('service_requests', $request_source_values)
    );

    $request_link_payload = [
        'external_system' => 'rukovoditel',
        'external_entity' => 'service_requests',
        'external_item_id' => (string) $request_id,
        'external_title' => $request_title,
        'naudoc_url' => $request_naudoc_url ?: $doc_card_naudoc_url,
        'naudoc_title' => $doc_card_title,
        'sync_status' => $sync_status,
        'notes' => 'Автосвязь service request -> document card',
        'metadata' => $request_metadata,
    ];
    platform_sync_bridge_upsert_link($request_link_payload);

    $doc_card_source_values = [
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'doc_card_title' => $doc_card_title,
        'source_request_id' => $request_id,
        'source_request_url' => $request_url,
        'document_route' => $doc_route_name,
    ];
    $doc_card_metadata = platform_sync_bridge_build_metadata_from_mappings('document_cards', $doc_card_source_values, [
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'source_request_id' => $request_id,
        'source_request_url' => $request_url,
        'document_route' => $doc_route_name,
    ]);
    $doc_card_metadata = platform_sync_bridge_attach_naudoc_projection(
        $doc_card_metadata,
        platform_sync_bridge_build_naudoc_projection('document_cards', $doc_card_source_values)
    );

    $doc_card_link_result = platform_sync_bridge_upsert_link([
        'external_system' => 'rukovoditel',
        'external_entity' => 'document_cards',
        'external_item_id' => (string) $doc_card_id,
        'external_title' => $doc_card_title,
        'naudoc_url' => $doc_card_naudoc_url,
        'naudoc_title' => $doc_card_title,
        'sync_status' => $doc_card_sync_status,
        'notes' => 'Автосвязь document card -> NauDoc bridge state',
        'metadata' => $doc_card_metadata,
    ]);

    $doc_card_link_id = (int) ($doc_card_link_result['link']['id'] ?? 0);
    if ($doc_card_link_id)
    {
        $writeback_result = platform_sync_bridge_writeback_link($doc_card_link_id);
        $written_naudoc_url = platform_sync_normalize_naudoc_url($writeback_result['link']['naudoc_url'] ?? '');

        if ($written_naudoc_url && $written_naudoc_url !== $doc_card_naudoc_url)
        {
            items::update_by_id(DOC_CARD_ENTITY_ID, $doc_card_id, [
                'field_' . DOC_NAUDOC_LINK_FIELD_ID => $written_naudoc_url,
            ], [
                'run_email_rules' => false,
                'run_process' => false,
            ]);
            $doc_card_naudoc_url = $written_naudoc_url;
            $doc_card_sync_status = resolve_sync_status($doc_card_naudoc_url);
        }

        if ($written_naudoc_url && $written_naudoc_url !== $request_naudoc_url)
        {
            items::update_by_id(REQUEST_ENTITY_ID, $request_id, [
                'field_' . REQUEST_NAUDOC_LINK_FIELD_ID => $written_naudoc_url,
            ], [
                'run_email_rules' => false,
                'run_process' => false,
            ]);
            $request_naudoc_url = $written_naudoc_url;
            $sync_status = resolve_sync_status($request_naudoc_url);

            $request_link_payload['naudoc_url'] = $request_naudoc_url;
            $request_link_payload['sync_status'] = $sync_status;
            platform_sync_bridge_upsert_link($request_link_payload);
        }
    }

    return [
        'request_id' => $request_id,
        'doc_card_id' => $doc_card_id,
        'request_url' => $request_url,
        'doc_card_url' => $doc_card_url,
        'sync_status' => $sync_status,
    ];
}

function parse_cli_options()
{
    global $argv;

    $options = [
        'request_id' => 0,
        'seed_demo' => false,
        'force_all' => false,
    ];

    foreach ($argv as $arg)
    {
        if (strpos($arg, '--request-id=') === 0)
        {
            $options['request_id'] = (int) substr($arg, strlen('--request-id='));
        }
        elseif ($arg === '--seed-demo')
        {
            $options['seed_demo'] = true;
        }
        elseif ($arg === '--force-all')
        {
            $options['force_all'] = true;
        }
    }

    return $options;
}

function fetch_requests_to_sync($request_id, $force_all)
{
    if ($request_id > 0)
    {
        return platform_sync_fetch_all_rows(
            "select * from app_entity_" . REQUEST_ENTITY_ID . " where id='" . (int) $request_id . "' order by id"
        );
    }

    $docflow_type_id = platform_sync_choice_id_by_name(REQUEST_TYPE_FIELD_ID, 'Документооборот');
    $where = [];
    if ($force_all)
    {
        $where[] = '1=1';
    }
    else
    {
        if ($docflow_type_id > 0)
        {
            $where[] = "field_" . REQUEST_TYPE_FIELD_ID . "='" . (int) $docflow_type_id . "'";
        }
        $where[] = "length(field_" . REQUEST_DOC_CARD_LINK_FIELD_ID . ")>0";
        $where[] = "length(field_" . REQUEST_NAUDOC_LINK_FIELD_ID . ")>0";
    }

    return platform_sync_fetch_all_rows(
        "select * from app_entity_" . REQUEST_ENTITY_ID . " where " . implode(' or ', $where) . " order by id"
    );
}

console_log('Syncing service requests with document cards and middleware...');

$options = parse_cli_options();
if ($options['seed_demo'])
{
    create_demo_request_if_needed();
}

$requests = fetch_requests_to_sync($options['request_id'], $options['force_all']);
if (!count($requests))
{
    console_log('No service requests matched sync criteria.');
    exit(0);
}

$synced = 0;
$failed = 0;
foreach ($requests as $request)
{
    try
    {
        $result = ensure_doc_card_for_request($request);
        resolve_sync_failure($result['request_id'], [
            'doc_card_id' => $result['doc_card_id'],
            'sync_status' => $result['sync_status'],
        ]);

        $synced++;
        console_log(
            'Synced request #' . $result['request_id'] .
            ' -> doc card #' . $result['doc_card_id'] .
            ' [' . $result['sync_status'] . ']'
        );
    }
    catch (Throwable $e)
    {
        $failed++;
        $request_id = (int) $request['id'];
        report_sync_failure($e->getMessage(), [
            'request_id' => $request_id,
            'request_title' => trim((string) $request['field_' . REQUEST_SUBJECT_FIELD_ID]),
            'doc_card_id' => (int) $request['field_' . REQUEST_DOC_CARD_LINK_FIELD_ID],
            'project_link' => platform_sync_normalize_csv_value($request['field_' . REQUEST_PROJECT_LINK_FIELD_ID]),
        ]);
        console_log('Failed sync request #' . $request_id . ': ' . $e->getMessage());
    }
}

console_log('Sync complete. Successful: ' . $synced . ', failed: ' . $failed);
