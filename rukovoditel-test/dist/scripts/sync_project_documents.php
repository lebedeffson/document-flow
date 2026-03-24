<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';

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

function console_log($message)
{
    echo $message . PHP_EOL;
}

function fetch_row_by_sql($sql)
{
    $query = db_query($sql);
    return db_fetch_array($query);
}

function fetch_all_rows($sql)
{
    $rows = [];
    $query = db_query($sql);
    while ($row = db_fetch_array($query))
    {
        $rows[] = $row;
    }
    return $rows;
}

function get_choice_id_by_name($field_id, $name)
{
    $row = fetch_row_by_sql(
        "select id from app_fields_choices where fields_id='" . (int) $field_id . "' and name='" . db_input($name) . "' limit 1"
    );

    return $row ? (int) $row['id'] : 0;
}

function get_default_choice_id($field_id)
{
    $row = fetch_row_by_sql(
        "select id from app_fields_choices where fields_id='" . (int) $field_id . "' and is_default=1 order by sort_order, id limit 1"
    );

    if ($row)
    {
        return (int) $row['id'];
    }

    $row = fetch_row_by_sql(
        "select id from app_fields_choices where fields_id='" . (int) $field_id . "' order by sort_order, id limit 1"
    );

    return $row ? (int) $row['id'] : 0;
}

function item_exists($entity_id, $item_id)
{
    $row = fetch_row_by_sql("select id from app_entity_" . (int) $entity_id . " where id='" . (int) $item_id . "' limit 1");
    return (bool) $row;
}

function normalize_csv_value($value)
{
    $value = trim((string) $value);
    if ($value === '')
    {
        return '';
    }

    $parts = array_filter(array_map('trim', explode(',', $value)));
    return implode(',', $parts);
}

function first_csv_value($value)
{
    $parts = array_filter(array_map('trim', explode(',', (string) $value)));
    return count($parts) ? $parts[0] : '';
}

function get_field_id_by_name($entity_id, $name)
{
    $row = fetch_row_by_sql(
        "select id from app_fields where entities_id='" . (int) $entity_id . "' and name='" . db_input($name) . "' limit 1"
    );

    return $row ? (int) $row['id'] : 0;
}

function get_project_doc_card_link_field_id()
{
    static $field_id = null;

    if ($field_id === null)
    {
        $field_id = get_field_id_by_name(PROJECT_ENTITY_ID, 'Связанная карточка документа');
    }

    if (!(int) $field_id)
    {
        throw new RuntimeException(
            "Field 'Связанная карточка документа' was not found for projects. Run apply_process_model.sh first."
        );
    }

    return (int) $field_id;
}

function public_base_url()
{
    return rtrim(getenv('RUKOVODITEL_PUBLIC_URL') ?: 'http://localhost:18081', '/');
}

function public_naudoc_base_url()
{
    return rtrim(getenv('NAUDOC_PUBLIC_URL') ?: 'https://localhost:18443/docs', '/');
}

function normalize_naudoc_url($url)
{
    $url = trim((string) $url);
    if ($url === '')
    {
        return '';
    }

    $public_base = public_naudoc_base_url();
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

function bridge_base_url()
{
    return rtrim(getenv('BRIDGE_BASE_URL') ?: 'http://host.docker.internal:18082', '/');
}

function item_url($entity_id, $item_id)
{
    return public_base_url() . '/index.php?module=items/info&path=' . (int) $entity_id . '-' . (int) $item_id;
}

function http_json_request($method, $url, $payload)
{
    $content = json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    $context = stream_context_create([
        'http' => [
            'method' => strtoupper($method),
            'header' => "Content-Type: application/json\r\nAccept: application/json\r\n",
            'content' => $content,
            'ignore_errors' => true,
            'timeout' => 10,
        ],
    ]);

    $response_body = @file_get_contents($url, false, $context);
    $headers = $http_response_header ?? [];
    $status_code = 0;
    if (isset($headers[0]) and preg_match('#\s(\d{3})\s#', $headers[0], $matches))
    {
        $status_code = (int) $matches[1];
    }

    return [
        'status_code' => $status_code,
        'body' => $response_body === false ? '' : $response_body,
        'ok' => $status_code >= 200 && $status_code < 300,
    ];
}

function http_json_get($url)
{
    $context = stream_context_create([
        'http' => [
            'method' => 'GET',
            'header' => "Accept: application/json\r\n",
            'ignore_errors' => true,
            'timeout' => 10,
        ],
    ]);

    $response_body = @file_get_contents($url, false, $context);
    $headers = $http_response_header ?? [];
    $status_code = 0;
    if (isset($headers[0]) and preg_match('#\s(\d{3})\s#', $headers[0], $matches))
    {
        $status_code = (int) $matches[1];
    }

    return [
        'status_code' => $status_code,
        'body' => $response_body === false ? '' : $response_body,
        'ok' => $status_code >= 200 && $status_code < 300,
    ];
}

function lookup_bridge_link($external_entity, $external_item_id)
{
    $response = http_json_get(
        bridge_base_url() . '/links/lookup?' . http_build_query([
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

function choose_bridge_sync_status($external_entity, $external_item_id, $default_sync_status)
{
    $existing = lookup_bridge_link($external_entity, $external_item_id);
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

function upsert_bridge_link($payload)
{
    $response = http_json_request('POST', bridge_base_url() . '/links/upsert', $payload);
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

function create_demo_project_if_needed()
{
    $existing = fetch_row_by_sql("select id from app_entity_" . PROJECT_ENTITY_ID . " limit 1");
    if ($existing)
    {
        console_log('Demo seed skipped: project records already exist.');
        return;
    }

    $project_doc_card_field_id = get_project_doc_card_link_field_id();
    $priority_choice_id = get_choice_id_by_name(PROJECT_PRIORITY_FIELD_ID, 'Высокий');
    $stage_choice_id = get_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'В работе');
    $department_choice_id = get_choice_id_by_name(PROJECT_DEPARTMENT_FIELD_ID, 'ИТ и сервис');

    if (!$priority_choice_id)
    {
        $priority_choice_id = get_default_choice_id(PROJECT_PRIORITY_FIELD_ID);
    }

    if (!$stage_choice_id)
    {
        $stage_choice_id = get_default_choice_id(PROJECT_STAGE_FIELD_ID);
    }

    if (!$department_choice_id)
    {
        $department_choice_id = get_default_choice_id(PROJECT_DEPARTMENT_FIELD_ID);
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
    $preferred = get_choice_id_by_name(DOC_TYPE_FIELD_ID, 'Регламент');
    if ($preferred)
    {
        return $preferred;
    }

    $fallback = get_choice_id_by_name(DOC_TYPE_FIELD_ID, 'Иное');
    if ($fallback)
    {
        return $fallback;
    }

    return get_default_choice_id(DOC_TYPE_FIELD_ID);
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
    $project_url = item_url(PROJECT_ENTITY_ID, $project_id);
    $project_naudoc_url = normalize_naudoc_url($project['field_' . PROJECT_NAUDOC_LINK_FIELD_ID]);
    $owner_id = first_csv_value($project['field_' . PROJECT_MANAGER_FIELD_ID]) ?:
        first_csv_value($project['field_' . PROJECT_CURATOR_FIELD_ID]) ?:
        (string) $project['created_by'];
    $doc_card_id = (int) $project['field_' . $project_doc_card_field_id];

    $doc_status_id = get_choice_id_by_name(DOC_STATUS_FIELD_ID, 'Черновик');
    $doc_type_id = resolve_project_doc_type_choice();

    if (!$doc_card_id || !item_exists(DOC_CARD_ENTITY_ID, $doc_card_id))
    {
        $doc_card_id = items::insert(DOC_CARD_ENTITY_ID, [
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
        ]);

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

    if ($doc_updates)
    {
        items::update_by_id(DOC_CARD_ENTITY_ID, $doc_card_id, $doc_updates, [
            'run_email_rules' => false,
            'run_process' => false,
        ]);
        $doc_card = db_find('app_entity_' . DOC_CARD_ENTITY_ID, $doc_card_id);
    }

    $doc_card_url = item_url(DOC_CARD_ENTITY_ID, $doc_card_id);
    $doc_card_title = trim((string) $doc_card['field_' . DOC_TITLE_FIELD_ID]);
    $doc_card_naudoc_url = normalize_naudoc_url($doc_card['field_' . DOC_NAUDOC_LINK_FIELD_ID]);

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

    $sync_status = choose_bridge_sync_status(
        'projects',
        $project_id,
        resolve_sync_status($project_naudoc_url ?: $doc_card_naudoc_url)
    );
    $doc_card_sync_status = choose_bridge_sync_status(
        'document_cards',
        $doc_card_id,
        resolve_sync_status($doc_card_naudoc_url)
    );

    upsert_bridge_link([
        'external_system' => 'rukovoditel',
        'external_entity' => 'projects',
        'external_item_id' => (string) $project_id,
        'external_title' => $project_title,
        'naudoc_url' => $project_naudoc_url ?: $doc_card_naudoc_url,
        'naudoc_title' => $doc_card_title,
        'sync_status' => $sync_status,
        'notes' => 'Автосвязь project -> document card',
        'metadata' => [
            'project_id' => $project_id,
            'project_url' => $project_url,
            'doc_card_id' => $doc_card_id,
            'doc_card_url' => $doc_card_url,
            'manager_user_id' => $owner_id,
        ],
    ]);

    upsert_bridge_link([
        'external_system' => 'rukovoditel',
        'external_entity' => 'document_cards',
        'external_item_id' => (string) $doc_card_id,
        'external_title' => $doc_card_title,
        'naudoc_url' => $doc_card_naudoc_url,
        'naudoc_title' => $doc_card_title,
        'sync_status' => $doc_card_sync_status,
        'notes' => 'Автосвязь document card -> NauDoc bridge state (project)',
        'metadata' => [
            'doc_card_id' => $doc_card_id,
            'doc_card_url' => $doc_card_url,
            'source_project_id' => $project_id,
            'source_project_url' => $project_url,
        ],
    ]);

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
        return fetch_all_rows(
            "select * from app_entity_" . PROJECT_ENTITY_ID . " where id='" . (int) $project_id . "' order by id"
        );
    }

    $active_stage_ids = array_filter([
        get_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'Инициирование'),
        get_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'В работе'),
        get_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'На согласовании'),
        get_choice_id_by_name(PROJECT_STAGE_FIELD_ID, 'На паузе'),
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

    return fetch_all_rows(
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
foreach ($projects as $project)
{
    $result = ensure_doc_card_for_project($project);
    $synced++;
    console_log(
        'Synced project #' . $result['project_id'] .
        ' -> doc card #' . $result['doc_card_id'] .
        ' [' . $result['sync_status'] . ']'
    );
}

console_log('Project sync complete. Total processed: ' . $synced);
