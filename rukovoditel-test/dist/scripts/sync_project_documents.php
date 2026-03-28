<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';
require 'includes/functions/platform_sync.php';

const PROJECT_ENTITY_ID = 21;
const DOC_CARD_ENTITY_ID = 25;

const PROJECT_PRIORITY_FIELD_ID = 156;
const PROJECT_STAGE_FIELD_ID = 157;
const PROJECT_NAME_FIELD_ID = 158;
const PROJECT_START_FIELD_ID = 159;
const PROJECT_DESCRIPTION_FIELD_ID = 160;
const PROJECT_TEAM_FIELD_ID = 161;
const PROJECT_MANAGER_FIELD_ID = 225;
const PROJECT_CURATOR_FIELD_ID = 226;
const PROJECT_DEPARTMENT_FIELD_ID = 227;
const PROJECT_PLAN_FINISH_FIELD_ID = 228;
const PROJECT_PROGRESS_FIELD_ID = 229;
const PROJECT_NAUDOC_LINK_FIELD_ID = 230;

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

function get_project_doc_card_link_field_id()
{
    static $field_id = null;

    if ($field_id === null)
    {
        $field_id = platform_sync_field_id_by_name(PROJECT_ENTITY_ID, 'Связанная карточка документа');
    }

    if (!(int) $field_id)
    {
        throw new RuntimeException(
            "Field 'Связанная карточка документа' was not found for projects. Run apply_process_model.sh first."
        );
    }

    return (int) $field_id;
}

function report_sync_failure($message, $context = [])
{
    $response = platform_sync_bridge_report_sync_failure(
        'projects',
        'projects',
        (string) ($context['project_id'] ?? ''),
        $message,
        $context
    );
    if (!$response['ok'])
    {
        console_log('Warning: failed to write sync failure log: ' . $response['status_code'] . ' ' . $response['body']);
    }
}

function resolve_sync_failure($project_id, $result = [])
{
    $response = platform_sync_bridge_resolve_sync_failure(
        'projects',
        'projects',
        (int) $project_id,
        $result
    );
    if (!$response['ok'])
    {
        console_log('Warning: failed to resolve sync failure log: ' . $response['status_code'] . ' ' . $response['body']);
    }
}

function create_demo_project_if_needed()
{
    $existing = platform_sync_fetch_row_by_sql("select id from app_entity_" . PROJECT_ENTITY_ID . " limit 1");
    if ($existing)
    {
        console_log('Demo seed skipped: project records already exist.');
        return;
    }

    $project_doc_card_field_id = get_project_doc_card_link_field_id();
    $priority_choice_id = platform_sync_choice_id_by_name(PROJECT_PRIORITY_FIELD_ID, 'Высокий');
    $stage_choice_id = platform_sync_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'В работе');
    $department_choice_id = platform_sync_choice_id_by_name(PROJECT_DEPARTMENT_FIELD_ID, 'ИТ и сервис');

    if (!$priority_choice_id)
    {
        $priority_choice_id = platform_sync_default_choice_id(PROJECT_PRIORITY_FIELD_ID);
    }

    if (!$stage_choice_id)
    {
        $stage_choice_id = platform_sync_default_choice_id(PROJECT_STAGE_FIELD_ID);
    }

    if (!$department_choice_id)
    {
        $department_choice_id = platform_sync_default_choice_id(PROJECT_DEPARTMENT_FIELD_ID);
    }

    $item_id = items::insert(PROJECT_ENTITY_ID, [
        'created_by' => 1,
        'parent_item_id' => 0,
        'field_' . PROJECT_PRIORITY_FIELD_ID => (string) $priority_choice_id,
        'field_' . PROJECT_STAGE_FIELD_ID => (string) $stage_choice_id,
        'field_' . PROJECT_NAME_FIELD_ID => 'Тестовый проект цифрового документооборота',
        'field_' . PROJECT_START_FIELD_ID => (string) strtotime('today'),
        'field_' . PROJECT_DESCRIPTION_FIELD_ID => '<p>Автоматически созданный тестовый проект для проверки связки проект -> карточка документа -> middleware.</p>',
        'field_' . PROJECT_TEAM_FIELD_ID => '1',
        'field_' . PROJECT_MANAGER_FIELD_ID => '1',
        'field_' . PROJECT_CURATOR_FIELD_ID => '1',
        'field_' . PROJECT_DEPARTMENT_FIELD_ID => (string) $department_choice_id,
        'field_' . PROJECT_PLAN_FINISH_FIELD_ID => (string) strtotime('+30 days'),
        'field_' . PROJECT_PROGRESS_FIELD_ID => '25',
        'field_' . PROJECT_NAUDOC_LINK_FIELD_ID => '',
        'field_' . $project_doc_card_field_id => '',
    ]);

    if (!$item_id)
    {
        throw new RuntimeException('Failed to create demo project.');
    }

    console_log('Created demo project #' . $item_id);
}

function resolve_project_doc_type_choice()
{
    $preferred = platform_sync_choice_id_by_name(DOC_TYPE_FIELD_ID, 'Регламент');
    if ($preferred)
    {
        return $preferred;
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

function ensure_doc_card_for_project($project)
{
    $project_doc_card_field_id = get_project_doc_card_link_field_id();
    $project_id = (int) $project['id'];
    $project_title = trim((string) $project['field_' . PROJECT_NAME_FIELD_ID]);
    $project_doc_title = 'Документ проекта: ' . $project_title;
    $project_url = platform_sync_item_url(PROJECT_ENTITY_ID, $project_id);
    $project_naudoc_url = platform_sync_normalize_naudoc_url($project['field_' . PROJECT_NAUDOC_LINK_FIELD_ID]);
    $owner_id = platform_sync_first_csv_value($project['field_' . PROJECT_MANAGER_FIELD_ID]) ?:
        platform_sync_first_csv_value($project['field_' . PROJECT_CURATOR_FIELD_ID]) ?:
        (string) $project['created_by'];
    $doc_card_id = (int) $project['field_' . $project_doc_card_field_id];

    $doc_status_id = platform_sync_choice_id_by_name(DOC_STATUS_FIELD_ID, 'Черновик');
    $doc_type_id = resolve_project_doc_type_choice();
    $doc_route_field_id = get_doc_route_field_id();
    $inferred_doc_route_label = platform_sync_infer_project_doc_route_label(
        $project_title,
        (string) $project['field_' . PROJECT_DESCRIPTION_FIELD_ID]
    );
    $inferred_doc_route_id = platform_sync_doc_route_choice_id_by_label(
        $doc_route_field_id,
        $inferred_doc_route_label
    );

    if (!$doc_card_id || !platform_sync_item_exists(DOC_CARD_ENTITY_ID, $doc_card_id))
    {
        $insert_data = [
            'created_by' => (int) $project['created_by'],
            'parent_item_id' => 0,
            'field_' . DOC_TITLE_FIELD_ID => $project_doc_title,
            'field_' . DOC_TYPE_FIELD_ID => (string) $doc_type_id,
            'field_' . DOC_STATUS_FIELD_ID => (string) $doc_status_id,
            'field_' . DOC_DATE_FIELD_ID => (string) time(),
            'field_' . DOC_OWNER_FIELD_ID => (string) $owner_id,
            'field_' . DOC_VERSION_FIELD_ID => '1.0',
            'field_' . DOC_NAUDOC_LINK_FIELD_ID => $project_naudoc_url,
            'field_' . DOC_PROJECT_LINK_FIELD_ID => (string) $project_id,
            'field_' . DOC_REQUEST_LINK_FIELD_ID => '',
            'field_' . DOC_DESCRIPTION_FIELD_ID => '<p>Карточка создана автоматически из проекта #' . $project_id . '.</p>' . ($project['field_' . PROJECT_DESCRIPTION_FIELD_ID] ?: ''),
        ];

        if ($inferred_doc_route_id > 0)
        {
            $insert_data['field_' . $doc_route_field_id] = (string) $inferred_doc_route_id;
        }

        $doc_card_id = items::insert(DOC_CARD_ENTITY_ID, $insert_data);

        if (!$doc_card_id)
        {
            throw new RuntimeException('Failed to create document card for project #' . $project_id);
        }

        items::update_by_id(PROJECT_ENTITY_ID, $project_id, [
            'field_' . $project_doc_card_field_id => (string) $doc_card_id,
        ], [
            'run_email_rules' => false,
            'run_process' => false,
        ]);

        console_log('Created document card #' . $doc_card_id . ' for project #' . $project_id);
    }

    $doc_card = db_find('app_entity_' . DOC_CARD_ENTITY_ID, $doc_card_id);
    $doc_updates = [];

    if ((string) $doc_card['field_' . DOC_PROJECT_LINK_FIELD_ID] !== (string) $project_id)
    {
        $doc_updates['field_' . DOC_PROJECT_LINK_FIELD_ID] = (string) $project_id;
    }

    if ((string) $doc_card['field_' . DOC_TITLE_FIELD_ID] !== $project_doc_title)
    {
        $doc_updates['field_' . DOC_TITLE_FIELD_ID] = $project_doc_title;
    }

    if ($project_naudoc_url && (string) $doc_card['field_' . DOC_NAUDOC_LINK_FIELD_ID] !== $project_naudoc_url)
    {
        $doc_updates['field_' . DOC_NAUDOC_LINK_FIELD_ID] = $project_naudoc_url;
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
    if (!$project_naudoc_url && $doc_card_naudoc_url)
    {
        items::update_by_id(PROJECT_ENTITY_ID, $project_id, [
            'field_' . PROJECT_NAUDOC_LINK_FIELD_ID => $doc_card_naudoc_url,
        ], [
            'run_email_rules' => false,
            'run_process' => false,
        ]);
        $project_naudoc_url = $doc_card_naudoc_url;
    }

    $sync_status = platform_sync_bridge_choose_sync_status(
        'projects',
        $project_id,
        resolve_sync_status($project_naudoc_url ?: $doc_card_naudoc_url)
    );
    $doc_card_sync_status = platform_sync_bridge_choose_sync_status(
        'document_cards',
        $doc_card_id,
        resolve_sync_status($doc_card_naudoc_url)
    );

    $project_source_values = [
        'project_id' => $project_id,
        'project_url' => $project_url,
        'project_title' => $project_title,
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'doc_card_title' => $doc_card_title,
        'manager_user_id' => $owner_id,
        'document_route' => $doc_route_name,
    ];
    $project_metadata = platform_sync_bridge_build_metadata_from_mappings('projects', $project_source_values, [
        'project_id' => $project_id,
        'project_url' => $project_url,
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'manager_user_id' => $owner_id,
        'document_route' => $doc_route_name,
    ]);
    $project_metadata = platform_sync_bridge_attach_naudoc_projection(
        $project_metadata,
        platform_sync_bridge_build_naudoc_projection('projects', $project_source_values)
    );

    $project_link_payload = [
        'external_system' => 'rukovoditel',
        'external_entity' => 'projects',
        'external_item_id' => (string) $project_id,
        'external_title' => $project_title,
        'naudoc_url' => $project_naudoc_url ?: $doc_card_naudoc_url,
        'naudoc_title' => $doc_card_title,
        'sync_status' => $sync_status,
        'notes' => 'Автосвязь project -> document card',
        'metadata' => $project_metadata,
    ];
    platform_sync_bridge_upsert_link($project_link_payload);

    $doc_card_source_values = [
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'doc_card_title' => $doc_card_title,
        'source_project_id' => $project_id,
        'source_project_url' => $project_url,
        'document_route' => $doc_route_name,
    ];
    $doc_card_metadata = platform_sync_bridge_build_metadata_from_mappings('document_cards', $doc_card_source_values, [
        'doc_card_id' => $doc_card_id,
        'doc_card_url' => $doc_card_url,
        'source_project_id' => $project_id,
        'source_project_url' => $project_url,
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
        'notes' => 'Автосвязь document card -> NauDoc bridge state (project)',
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

        if ($written_naudoc_url && $written_naudoc_url !== $project_naudoc_url)
        {
            items::update_by_id(PROJECT_ENTITY_ID, $project_id, [
                'field_' . PROJECT_NAUDOC_LINK_FIELD_ID => $written_naudoc_url,
            ], [
                'run_email_rules' => false,
                'run_process' => false,
            ]);
            $project_naudoc_url = $written_naudoc_url;
            $sync_status = resolve_sync_status($project_naudoc_url);

            $project_link_payload['naudoc_url'] = $project_naudoc_url;
            $project_link_payload['sync_status'] = $sync_status;
            platform_sync_bridge_upsert_link($project_link_payload);
        }
    }

    return [
        'project_id' => $project_id,
        'doc_card_id' => $doc_card_id,
        'project_url' => $project_url,
        'doc_card_url' => $doc_card_url,
        'sync_status' => $sync_status,
    ];
}

function parse_cli_options()
{
    global $argv;

    $options = [
        'project_id' => 0,
        'seed_demo' => false,
        'force_all' => false,
    ];

    foreach ($argv as $arg)
    {
        if (strpos($arg, '--project-id=') === 0)
        {
            $options['project_id'] = (int) substr($arg, strlen('--project-id='));
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

function fetch_projects_to_sync($project_id, $force_all)
{
    $project_doc_card_field_id = get_project_doc_card_link_field_id();

    if ($project_id > 0)
    {
        return platform_sync_fetch_all_rows(
            "select * from app_entity_" . PROJECT_ENTITY_ID . " where id='" . (int) $project_id . "' order by id"
        );
    }

    $active_stage_ids = array_filter([
        platform_sync_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'Инициирование'),
        platform_sync_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'В работе'),
        platform_sync_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'На согласовании'),
        platform_sync_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'На паузе'),
    ]);

    $where = [];
    if ($force_all)
    {
        $where[] = '1=1';
    }
    else
    {
        if (count($active_stage_ids))
        {
            $where[] = "field_" . PROJECT_STAGE_FIELD_ID . " in (" . implode(',', array_map('intval', $active_stage_ids)) . ")";
        }
        $where[] = "length(field_" . $project_doc_card_field_id . ")>0";
        $where[] = "length(field_" . PROJECT_NAUDOC_LINK_FIELD_ID . ")>0";
    }

    return platform_sync_fetch_all_rows(
        "select * from app_entity_" . PROJECT_ENTITY_ID . " where " . implode(' or ', $where) . " order by id"
    );
}

console_log('Syncing projects with document cards and middleware...');

$options = parse_cli_options();
if ($options['seed_demo'])
{
    create_demo_project_if_needed();
}

$projects = fetch_projects_to_sync($options['project_id'], $options['force_all']);
if (!count($projects))
{
    console_log('No projects matched sync criteria.');
    exit(0);
}

$synced = 0;
$failed = 0;
foreach ($projects as $project)
{
    try
    {
        $result = ensure_doc_card_for_project($project);
        resolve_sync_failure($result['project_id'], [
            'doc_card_id' => $result['doc_card_id'],
            'sync_status' => $result['sync_status'],
        ]);

        $synced++;
        console_log(
            'Synced project #' . $result['project_id'] .
            ' -> doc card #' . $result['doc_card_id'] .
            ' [' . $result['sync_status'] . ']'
        );
    }
    catch (Throwable $e)
    {
        $failed++;
        $project_id = (int) $project['id'];
        report_sync_failure($e->getMessage(), [
            'project_id' => $project_id,
            'project_title' => trim((string) $project['field_' . PROJECT_NAME_FIELD_ID]),
            'doc_card_id' => (int) $project['field_' . get_project_doc_card_link_field_id()],
        ]);
        console_log('Failed sync project #' . $project_id . ': ' . $e->getMessage());
    }
}

console_log('Project sync complete. Successful: ' . $synced . ', failed: ' . $failed);
