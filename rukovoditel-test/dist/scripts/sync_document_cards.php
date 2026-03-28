<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';
require 'includes/functions/platform_sync.php';

const DOC_CARD_ENTITY_ID = 25;
const PROJECT_ENTITY_ID = 21;
const REQUEST_ENTITY_ID = 23;

const DOC_TITLE_FIELD_ID = 242;
const DOC_NAUDOC_LINK_FIELD_ID = 250;
const DOC_PROJECT_LINK_FIELD_ID = 251;
const DOC_REQUEST_LINK_FIELD_ID = 252;
const DOC_DESCRIPTION_FIELD_ID = 253;

const PROJECT_TITLE_FIELD_ID = 158;
const PROJECT_DESCRIPTION_FIELD_ID = 160;
const REQUEST_TITLE_FIELD_ID = 178;
const REQUEST_TYPE_FIELD_ID = 179;
const REQUEST_DESCRIPTION_FIELD_ID = 185;

function console_log($message)
{
    echo $message . PHP_EOL;
}

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

function report_sync_failure($doc_card_id, $message, array $context = [], $link_id = 0)
{
    $response = platform_sync_bridge_report_sync_failure(
        'document_cards',
        'document_cards',
        (string) $doc_card_id,
        $message,
        $context,
        $link_id
    );

    if (!$response['ok'])
    {
        console_log('Warning: failed to write sync failure log: ' . $response['status_code'] . ' ' . $response['body']);
    }
}

function resolve_sync_failure($doc_card_id, array $result = [], $link_id = 0)
{
    $response = platform_sync_bridge_resolve_sync_failure(
        'document_cards',
        'document_cards',
        (string) $doc_card_id,
        $result,
        $link_id
    );

    if (!$response['ok'])
    {
        console_log('Warning: failed to resolve sync failure log: ' . $response['status_code'] . ' ' . $response['body']);
    }
}

function resolve_sync_status($naudoc_url)
{
    return strlen(trim((string) $naudoc_url)) ? 'linked' : 'pending_nau_doc';
}

function find_first_linked_item($entity_id, $csv_value)
{
    $item_id = (int) platform_sync_first_csv_value($csv_value);
    if ($item_id <= 0 || !platform_sync_item_exists($entity_id, $item_id))
    {
        return [];
    }

    return db_find('app_entity_' . (int) $entity_id, $item_id) ?: [];
}

function resolve_request_type_name($request)
{
    if (!count($request))
    {
        return '';
    }

    return platform_sync_choice_name_by_id(
        REQUEST_TYPE_FIELD_ID,
        (int) ($request['field_' . REQUEST_TYPE_FIELD_ID] ?? 0)
    );
}

function ensure_document_route_for_card($doc_card, $project = [], $request = [])
{
    $doc_route_field_id = get_doc_route_field_id();
    $current_route_id = (int) ($doc_card['field_' . $doc_route_field_id] ?? 0);

    if ($current_route_id > 0)
    {
        return platform_sync_choice_name_by_id($doc_route_field_id, $current_route_id);
    }

    if (count($request))
    {
        $route_label = platform_sync_infer_request_doc_route_label(
            resolve_request_type_name($request),
            (string) ($request['field_' . REQUEST_TITLE_FIELD_ID] ?? ''),
            (string) ($request['field_' . REQUEST_DESCRIPTION_FIELD_ID] ?? '')
        );
    }
    elseif (count($project))
    {
        $route_label = platform_sync_infer_project_doc_route_label(
            (string) ($project['field_' . PROJECT_TITLE_FIELD_ID] ?? ''),
            (string) ($project['field_' . PROJECT_DESCRIPTION_FIELD_ID] ?? '')
        );
    }
    else
    {
        $route_label = platform_sync_infer_request_doc_route_label(
            '',
            (string) ($doc_card['field_' . DOC_TITLE_FIELD_ID] ?? ''),
            (string) ($doc_card['field_' . DOC_DESCRIPTION_FIELD_ID] ?? '')
        );
    }

    $route_id = platform_sync_doc_route_choice_id_by_label($doc_route_field_id, $route_label);
    if ($route_id > 0)
    {
        items::update_by_id(DOC_CARD_ENTITY_ID, (int) $doc_card['id'], [
            'field_' . $doc_route_field_id => (string) $route_id,
        ], [
            'run_email_rules' => false,
            'run_process' => false,
        ]);
    }

    $fresh_doc_card = db_find('app_entity_' . DOC_CARD_ENTITY_ID, (int) $doc_card['id']);
    return platform_sync_choice_name_by_id(
        $doc_route_field_id,
        (int) ($fresh_doc_card['field_' . $doc_route_field_id] ?? 0)
    );
}

function sync_document_card($doc_card)
{
    $doc_card_id = (int) $doc_card['id'];
    $doc_card_url = platform_sync_item_url(DOC_CARD_ENTITY_ID, $doc_card_id);
    $doc_card_title = trim((string) ($doc_card['field_' . DOC_TITLE_FIELD_ID] ?? ''));
    $doc_card_naudoc_url = platform_sync_normalize_naudoc_url($doc_card['field_' . DOC_NAUDOC_LINK_FIELD_ID] ?? '');

    $linked_project = find_first_linked_item(PROJECT_ENTITY_ID, (string) ($doc_card['field_' . DOC_PROJECT_LINK_FIELD_ID] ?? ''));
    $linked_request = find_first_linked_item(REQUEST_ENTITY_ID, (string) ($doc_card['field_' . DOC_REQUEST_LINK_FIELD_ID] ?? ''));

    $project_id = (int) ($linked_project['id'] ?? 0);
    $request_id = (int) ($linked_request['id'] ?? 0);
    $project_url = $project_id > 0 ? platform_sync_item_url(PROJECT_ENTITY_ID, $project_id) : '';
    $request_url = $request_id > 0 ? platform_sync_item_url(REQUEST_ENTITY_ID, $request_id) : '';
    $document_route = ensure_document_route_for_card($doc_card, $linked_project, $linked_request);

    $sync_status = platform_sync_bridge_choose_sync_status(
        'document_cards',
        $doc_card_id,
        resolve_sync_status($doc_card_naudoc_url)
    );

    $source_values = [
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'doc_card_title' => $doc_card_title,
        'source_project_id' => $project_id,
        'source_project_url' => $project_url,
        'source_request_id' => $request_id,
        'source_request_url' => $request_url,
        'document_route' => $document_route,
    ];

    $metadata = platform_sync_bridge_build_metadata_from_mappings('document_cards', $source_values, [
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'source_project_id' => $project_id,
        'source_project_url' => $project_url,
        'source_request_id' => $request_id,
        'source_request_url' => $request_url,
        'document_route' => $document_route,
    ]);
    $metadata = platform_sync_bridge_attach_naudoc_projection(
        $metadata,
        platform_sync_bridge_build_naudoc_projection('document_cards', $source_values)
    );

    $link_result = platform_sync_bridge_upsert_link([
        'external_system' => 'rukovoditel',
        'external_entity' => 'document_cards',
        'external_item_id' => (string) $doc_card_id,
        'external_title' => $doc_card_title,
        'naudoc_url' => $doc_card_naudoc_url,
        'naudoc_title' => $doc_card_title,
        'sync_status' => $sync_status,
        'notes' => 'Автосвязь document card -> NauDoc bridge state (direct)',
        'metadata' => $metadata,
    ]);

    $link_id = (int) ($link_result['link']['id'] ?? 0);
    if ($link_id > 0)
    {
        $writeback_result = platform_sync_bridge_writeback_link($link_id);
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
        }
    }

    resolve_sync_failure($doc_card_id, [
        'link_id' => $link_id,
        'naudoc_url' => $doc_card_naudoc_url,
        'source_project_id' => $project_id,
        'source_request_id' => $request_id,
    ], $link_id);

    console_log(
        'Synced document card #' . $doc_card_id
        . ($doc_card_naudoc_url ? ' -> ' . $doc_card_naudoc_url : ' (pending NauDoc URL)')
    );
}

$force_all = in_array('--force-all', $argv, true);
$only_missing = in_array('--only-missing', $argv, true);

console_log('Syncing standalone document cards...');

$sql = "select * from app_entity_" . DOC_CARD_ENTITY_ID;
if ($only_missing && !$force_all)
{
    $sql .= " where trim(field_" . DOC_NAUDOC_LINK_FIELD_ID . ")=''";
}
$sql .= " order by id";

$rows = platform_sync_fetch_all_rows($sql);
foreach ($rows as $doc_card)
{
    try
    {
        sync_document_card($doc_card);
    }
    catch (Throwable $e)
    {
        $doc_card_id = (int) ($doc_card['id'] ?? 0);
        report_sync_failure($doc_card_id, $e->getMessage(), [
            'doc_card_id' => $doc_card_id,
            'doc_card_title' => (string) ($doc_card['field_' . DOC_TITLE_FIELD_ID] ?? ''),
        ]);
        console_log('Failed to sync document card #' . $doc_card_id . ': ' . $e->getMessage());
    }
}

console_log('Standalone document card sync completed. Processed: ' . count($rows));
