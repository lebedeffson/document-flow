<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';

function console_log($message)
{
    echo $message . PHP_EOL;
}

function fetch_row_by_sql($sql)
{
    $query = db_query($sql);
    return db_fetch_array($query);
}

function entity_has_records($entity_id)
{
    $row = fetch_row_by_sql("select count(*) as total from app_entity_" . (int) $entity_id);
    return (int) $row['total'] > 0;
}

function ensure_entities_group($name, $sort_order)
{
    $group = fetch_row_by_sql("select * from app_entities_groups where name='" . db_input($name) . "' limit 1");

    if (!$group)
    {
        db_perform('app_entities_groups', [
            'name' => $name,
            'sort_order' => $sort_order,
        ]);

        $group_id = db_insert_id();
        console_log("Created entity group: {$name}");
    }
    else
    {
        $group_id = (int) $group['id'];
        db_perform('app_entities_groups', [
            'name' => $name,
            'sort_order' => $sort_order,
        ], 'update', "id='" . db_input($group_id) . "'");
    }

    return $group_id;
}

function ensure_entity_record($id, $parent_id, $group_id, $name, $sort_order, $display_in_menu, $notes)
{
    $exists = fetch_row_by_sql("select * from app_entities where id='" . (int) $id . "' limit 1");
    $table_exists = fetch_row_by_sql("show tables like 'app_entity_" . (int) $id . "'");

    if (!$exists)
    {
        db_query(
            "insert into app_entities (id,parent_id,group_id,name,notes,display_in_menu,sort_order) values (" .
            (int) $id . "," .
            (int) $parent_id . "," .
            (int) $group_id . ",'" .
            db_input($name) . "','" .
            db_input($notes) . "'," .
            (int) $display_in_menu . "," .
            (int) $sort_order . ")"
        );

        entities::prepare_tables($id);

        $tab_id = ensure_form_tab($id, 'Информация', 0, ['Информация']);
        entities::insert_reserved_fields($id, $tab_id);

        console_log("Created entity: {$name} (#{$id})");
    }
    else
    {
        db_perform('app_entities', [
            'parent_id' => $parent_id,
            'group_id' => $group_id,
            'name' => $name,
            'notes' => $notes,
            'display_in_menu' => $display_in_menu,
            'sort_order' => $sort_order,
        ], 'update', "id='" . db_input($id) . "'");
    }

    if ($exists && !$table_exists)
    {
        entities::prepare_tables($id);
    }
}

function ensure_default_report($entity_id)
{
    $report = fetch_row_by_sql("select * from app_reports where entities_id='" . (int) $entity_id . "' and reports_type='default' limit 1");

    if (!$report)
    {
        db_query(
            "insert into app_reports set " .
            "parent_id=0," .
            "entities_id=" . (int) $entity_id . "," .
            "created_by=0," .
            "reports_type='default'," .
            "name=''," .
            "description=''," .
            "menu_icon=''," .
            "icon_color=''," .
            "bg_color=''," .
            "in_menu=0," .
            "in_dashboard=0," .
            "in_dashboard_counter=0," .
            "in_dashboard_icon=0," .
            "in_dashboard_counter_color=''," .
            "in_dashboard_counter_bg_color=''," .
            "in_dashboard_counter_fields=''," .
            "dashboard_counter_hide_count=0," .
            "dashboard_counter_hide_zero_count=0," .
            "dashboard_counter_sum_by_field=0," .
            "in_header=0," .
            "in_header_autoupdate=0," .
            "dashboard_sort_order=NULL," .
            "header_sort_order=0," .
            "dashboard_counter_sort_order=0," .
            "listing_order_fields=''," .
            "users_groups=''," .
            "assigned_to=''," .
            "displays_assigned_only=0," .
            "parent_entity_id=0," .
            "parent_item_id=0," .
            "fields_in_listing=''," .
            "rows_per_page=0," .
            "notification_days=''," .
            "notification_time=''," .
            "listing_type=''," .
            "listing_col_width=''"
        );
    }
}

function ensure_entity_cfg_set($entity_id, $cfg)
{
    foreach ($cfg as $name => $value)
    {
        entities::set_cfg($name, $value, $entity_id);
    }
}

function ensure_form_tab($entity_id, $name, $sort_order, $legacy_names = [])
{
    $names = array_unique(array_merge([$name], $legacy_names));
    $names_sql = [];
    foreach ($names as $item)
    {
        $names_sql[] = "'" . db_input($item) . "'";
    }

    $tab = fetch_row_by_sql(
        "select * from app_forms_tabs where entities_id='" . (int) $entity_id . "' and name in (" . implode(',', $names_sql) . ") order by id limit 1"
    );

    if (!$tab)
    {
        db_perform('app_forms_tabs', [
            'entities_id' => $entity_id,
            'parent_id' => 0,
            'is_folder' => 0,
            'name' => $name,
            'icon' => '',
            'icon_color' => '',
            'description' => '',
            'sort_order' => $sort_order,
        ]);

        $tab_id = db_insert_id();
    }
    else
    {
        $tab_id = (int) $tab['id'];
        db_perform('app_forms_tabs', [
            'name' => $name,
            'sort_order' => $sort_order,
            'parent_id' => 0,
            'is_folder' => 0,
            'icon' => '',
            'icon_color' => '',
            'description' => '',
        ], 'update', "id='" . db_input($tab_id) . "'");
    }

    return $tab_id;
}

function get_reserved_field($entity_id, $type)
{
    return fetch_row_by_sql(
        "select * from app_fields where entities_id='" . (int) $entity_id . "' and type='" . db_input($type) . "' limit 1"
    );
}

function ensure_reserved_field($entity_id, $type, $updates)
{
    $field = get_reserved_field($entity_id, $type);

    if (!$field)
    {
        db_perform('app_fields', array_merge([
            'entities_id' => $entity_id,
            'forms_tabs_id' => $updates['forms_tabs_id'],
            'comments_forms_tabs_id' => 0,
            'forms_rows_position' => '',
            'type' => $type,
            'name' => '',
            'short_name' => '',
            'is_heading' => 0,
            'tooltip' => '',
            'tooltip_display_as' => '',
            'tooltip_in_item_page' => 0,
            'tooltip_item_page' => '',
            'notes' => '',
            'is_required' => 0,
            'required_message' => '',
            'configuration' => '',
            'sort_order' => 0,
            'listing_status' => 1,
            'listing_sort_order' => 0,
            'comments_status' => 0,
            'comments_sort_order' => 0,
        ], $updates));

        $field_id = db_insert_id();
    }
    else
    {
        $field_id = (int) $field['id'];
        db_perform('app_fields', $updates, 'update', "id='" . db_input($field_id) . "'");
    }

    return $field_id;
}

function find_custom_field($entity_id, $name, $legacy_names = [])
{
    $names = array_unique(array_merge([$name], $legacy_names));
    $names_sql = [];
    foreach ($names as $item)
    {
        $names_sql[] = "'" . db_input($item) . "'";
    }

    return fetch_row_by_sql(
        "select * from app_fields where entities_id='" . (int) $entity_id . "' and name in (" . implode(',', $names_sql) . ") order by id limit 1"
    );
}

function ensure_custom_field($entity_id, $name, $type, $forms_tabs_id, $params = [], $legacy_names = [])
{
    $field = find_custom_field($entity_id, $name, $legacy_names);

    $data = array_merge([
        'entities_id' => $entity_id,
        'forms_tabs_id' => $forms_tabs_id,
        'comments_forms_tabs_id' => 0,
        'forms_rows_position' => '',
        'type' => $type,
        'name' => $name,
        'short_name' => '',
        'is_heading' => 0,
        'tooltip' => '',
        'tooltip_display_as' => '',
        'tooltip_in_item_page' => 0,
        'tooltip_item_page' => '',
        'notes' => '',
        'is_required' => 0,
        'required_message' => '',
        'configuration' => '',
        'sort_order' => 0,
        'listing_status' => 0,
        'listing_sort_order' => 0,
        'comments_status' => 0,
        'comments_sort_order' => 0,
    ], $params);

    if (!$field)
    {
        db_perform('app_fields', $data);
        $field_id = db_insert_id();
        entities::prepare_field($entity_id, $field_id, $type);
    }
    else
    {
        $field_id = (int) $field['id'];
        db_perform('app_fields', $data, 'update', "id='" . db_input($field_id) . "'");
    }

    return $field_id;
}

function sync_field_choices($entity_id, $field_id, $choices)
{
    $has_data = entity_has_records($entity_id);
    $existing = [];

    $query = db_query("select * from app_fields_choices where fields_id='" . (int) $field_id . "' order by sort_order, id");
    while ($row = db_fetch_array($query))
    {
        $existing[$row['name']] = $row;
    }

    if (!$has_data)
    {
        db_query("delete from app_fields_choices where fields_id='" . (int) $field_id . "'");
        $existing = [];
    }

    db_query("update app_fields_choices set is_default=0 where fields_id='" . (int) $field_id . "'");

    $sort_order = 1;
    foreach ($choices as $choice)
    {
        $data = [
            'fields_id' => $field_id,
            'parent_id' => $choice['parent_id'] ?? 0,
            'is_active' => $choice['is_active'] ?? 1,
            'name' => $choice['name'],
            'icon' => $choice['icon'] ?? '',
            'is_default' => $choice['is_default'] ?? 0,
            'bg_color' => $choice['bg_color'] ?? '',
            'sort_order' => $choice['sort_order'] ?? $sort_order,
            'users' => $choice['users'] ?? '',
            'value' => $choice['value'] ?? '',
            'filename' => $choice['filename'] ?? '',
        ];

        if (isset($existing[$choice['name']]))
        {
            db_perform('app_fields_choices', $data, 'update', "id='" . db_input($existing[$choice['name']]['id']) . "'");
        }
        else
        {
            db_perform('app_fields_choices', $data);
        }

        $sort_order++;
    }
}

function ensure_access_schema($entity_id, $group_id, $schema)
{
    $record = fetch_row_by_sql(
        "select * from app_entities_access where entities_id='" . (int) $entity_id . "' and access_groups_id='" . (int) $group_id . "' limit 1"
    );

    if (!$record)
    {
        db_perform('app_entities_access', [
            'entities_id' => $entity_id,
            'access_groups_id' => $group_id,
            'access_schema' => $schema,
        ]);
    }
    else
    {
        db_perform('app_entities_access', [
            'access_schema' => $schema,
        ], 'update', "id='" . db_input($record['id']) . "'");
    }
}

function ensure_access_group($name, $sort_order, $preferred_id = null, $notes = '')
{
    $group = fetch_row_by_sql("select * from app_access_groups where name='" . db_input($name) . "' limit 1");

    if (!$group && $preferred_id)
    {
        $group = fetch_row_by_sql("select * from app_access_groups where id='" . (int) $preferred_id . "' limit 1");
    }

    $data = [
        'name' => $name,
        'is_default' => 0,
        'is_ldap_default' => 0,
        'ldap_filter' => '',
        'sort_order' => $sort_order,
        'notes' => $notes,
    ];

    if (!$group)
    {
        if ($preferred_id)
        {
            $data['id'] = (int) $preferred_id;
        }

        db_perform('app_access_groups', $data);
        $group_id = $preferred_id ?: db_insert_id();
        console_log("Ensured access group: {$name} (#{$group_id})");
        return (int) $group_id;
    }

    $group_id = (int) $group['id'];
    db_perform('app_access_groups', $data, 'update', "id='" . db_input($group_id) . "'");
    return $group_id;
}

function ensure_common_report($entity_id, $name, $params = [])
{
    $report = fetch_row_by_sql(
        "select * from app_reports where entities_id='" . (int) $entity_id . "' and reports_type='common' and name='" . db_input($name) . "' limit 1"
    );

    $default_report = fetch_row_by_sql(
        "select * from app_reports where entities_id='" . (int) $entity_id . "' and reports_type='default' limit 1"
    );

    $data = array_merge([
        'parent_id' => 0,
        'entities_id' => $entity_id,
        'created_by' => 0,
        'reports_type' => 'common',
        'name' => $name,
        'description' => '',
        'menu_icon' => '',
        'icon_color' => '',
        'bg_color' => '',
        'in_menu' => 0,
        'in_dashboard' => 1,
        'in_dashboard_counter' => 1,
        'in_dashboard_icon' => 0,
        'in_dashboard_counter_color' => '#1f4f86',
        'in_dashboard_counter_bg_color' => '#f3d7ad',
        'in_dashboard_counter_fields' => '',
        'dashboard_counter_hide_count' => 0,
        'dashboard_counter_hide_zero_count' => 0,
        'dashboard_counter_sum_by_field' => 0,
        'in_header' => 0,
        'in_header_autoupdate' => 0,
        'dashboard_sort_order' => 0,
        'header_sort_order' => 0,
        'dashboard_counter_sort_order' => 0,
        'listing_order_fields' => ($default_report ? $default_report['listing_order_fields'] : ''),
        'users_groups' => '',
        'assigned_to' => '',
        'displays_assigned_only' => 0,
        'parent_entity_id' => 0,
        'parent_item_id' => 0,
        'fields_in_listing' => '',
        'rows_per_page' => 0,
        'notification_days' => '',
        'notification_time' => '',
        'listing_type' => '',
        'listing_col_width' => '',
    ], $params);

    if (!$report)
    {
        db_perform('app_reports', $data);
        return db_insert_id();
    }

    db_perform('app_reports', $data, 'update', "id='" . db_input($report['id']) . "'");
    return (int) $report['id'];
}

function sync_report_filters($report_id, $filters)
{
    db_query("delete from app_reports_filters where reports_id='" . (int) $report_id . "'");

    foreach ($filters as $filter)
    {
        $values = $filter['values'];
        if (is_array($values))
        {
            $values = implode(',', array_filter($values));
        }

        db_perform('app_reports_filters', [
            'reports_id' => $report_id,
            'fields_id' => $filter['fields_id'],
            'filters_values' => (string) $values,
            'filters_condition' => $filter['filters_condition'] ?? 'include',
            'is_active' => $filter['is_active'] ?? 1,
        ]);
    }
}

function get_choice_id_by_name($field_id, $name)
{
    $choice = fetch_row_by_sql(
        "select id from app_fields_choices where fields_id='" . (int) $field_id . "' and name='" . db_input($name) . "' limit 1"
    );

    return $choice ? (int) $choice['id'] : 0;
}

function sync_fields_access($entity_id, $group_id, $rules)
{
    $allowed_schemas = ['view', 'view_inform', 'hide'];
    $managed_fields = array_filter(array_map('intval', array_keys($rules)));

    if (!count($managed_fields))
    {
        return;
    }

    db_query(
        "delete from app_fields_access where entities_id='" . (int) $entity_id . "' and access_groups_id='" . (int) $group_id . "' and fields_id in (" . implode(',', $managed_fields) . ")"
    );

    foreach ($rules as $field_id => $schema)
    {
        if (!in_array($schema, $allowed_schemas, true))
        {
            continue;
        }

        db_perform('app_fields_access', [
            'entities_id' => $entity_id,
            'access_groups_id' => $group_id,
            'fields_id' => (int) $field_id,
            'access_schema' => $schema,
        ]);
    }
}

function ensure_entities_menu_item($name, $params = [])
{
    $parent_id = (int) ($params['parent_id'] ?? 0);
    $menu = fetch_row_by_sql(
        "select * from app_entities_menu where name='" . db_input($name) . "' and parent_id='" . $parent_id . "' limit 1"
    );

    $data = array_merge([
        'parent_id' => $parent_id,
        'name' => $name,
        'icon' => '',
        'icon_color' => '',
        'bg_color' => '',
        'entities_list' => '',
        'reports_list' => '',
        'pages_list' => '',
        'sort_order' => 0,
        'type' => 'entity',
        'url' => '',
        'users_groups' => '',
        'assigned_to' => '',
    ], $params);

    foreach (['entities_list', 'reports_list', 'pages_list', 'users_groups', 'assigned_to'] as $list_key)
    {
        if (isset($data[$list_key]) && is_array($data[$list_key]))
        {
            $data[$list_key] = implode(',', array_filter(array_map('strval', $data[$list_key]), 'strlen'));
        }
    }

    if (!$menu)
    {
        db_perform('app_entities_menu', $data);
        return (int) db_insert_id();
    }

    db_perform('app_entities_menu', $data, 'update', "id='" . db_input($menu['id']) . "'");
    return (int) $menu['id'];
}

function config_json($data)
{
    return json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}

function onlyoffice_public_js_api_url()
{
    return getenv('ONLYOFFICE_PUBLIC_JS_API_URL') ?: 'https://localhost:18443/office/web-apps/apps/api/documents/api.js';
}

function onlyoffice_jwt_secret()
{
    return getenv('ONLYOFFICE_JWT_SECRET') ?: 'onlyoffice_dev_secret';
}

console_log('Provisioning process model for Rukovoditel...');

$manager_group_id = ensure_access_group('Руководитель / преподаватель', 10, 4, 'Согласование, утверждение и управленческий контроль.');
$employee_group_id = ensure_access_group('Исполнитель / сотрудник', 20, 5, 'Ежедневная работа с проектами, задачами, заявками и карточками.');
$requester_group_id = ensure_access_group('Заявитель / пользователь', 30, 6, 'Подача заявок и отслеживание собственных обращений.');
$office_group_id = ensure_access_group('Канцелярия / делопроизводитель', 40, 7, 'Регистрация документов, контроль маршрутов и сопровождение архива.');

$operations_group_id = ensure_entities_group('Операционная работа', 10);
$documents_group_id = ensure_entities_group('Документы', 20);
$supply_group_id = ensure_entities_group('Обеспечение', 30);

ensure_entity_record(21, 0, $operations_group_id, 'Проекты и инициативы', 10, 1, 'Учебные, методические, организационные и сервисные проекты.');
ensure_entity_record(22, 21, $operations_group_id, 'Поручения и задачи', 11, 1, 'Задачи и поручения внутри проектов и процессов.');
ensure_entity_record(23, 0, $operations_group_id, 'Заявки на обслуживание', 20, 1, 'Сервисные заявки от сотрудников и преподавателей.');
ensure_entity_record(24, 21, $operations_group_id, 'Рабочие обсуждения', 30, 0, 'Обсуждения и договоренности по проектам.');
ensure_entity_record(25, 0, $documents_group_id, 'Карточки документов', 30, 1, 'Операционный слой карточек документов с ссылками на NauDoc.');
ensure_entity_record(26, 0, $documents_group_id, 'База документов', 40, 1, 'База регламентов, шаблонов и материалов.');
ensure_entity_record(27, 0, $supply_group_id, 'Заявки на МТЗ', 50, 1, 'Заявки на материально-техническое обеспечение.');

foreach ([21, 22, 23, 24, 25, 26, 27] as $entity_id)
{
    ensure_default_report($entity_id);
}

ensure_entity_cfg_set(21, [
    'menu_title' => 'Проекты и инициативы',
    'listing_heading' => 'Проекты и инициативы',
    'window_heading' => 'Карточка проекта',
    'insert_button' => 'Создать проект',
    'use_comments' => '1',
    'email_subject_new_item' => 'Новый проект:',
    'email_subject_new_comment' => 'Новый комментарий к проекту:',
]);

ensure_entity_cfg_set(22, [
    'menu_title' => 'Поручения и задачи',
    'listing_heading' => 'Поручения и задачи',
    'window_heading' => 'Карточка задачи',
    'insert_button' => 'Добавить задачу',
    'use_comments' => '1',
    'email_subject_new_item' => 'Новая задача:',
    'email_subject_new_comment' => 'Новый комментарий к задаче:',
]);

ensure_entity_cfg_set(23, [
    'menu_title' => 'Заявки на обслуживание',
    'listing_heading' => 'Заявки на обслуживание',
    'window_heading' => 'Карточка заявки',
    'insert_button' => 'Создать заявку',
    'use_comments' => '1',
    'email_subject_new_item' => 'Новая заявка:',
    'email_subject_new_comment' => 'Новый комментарий к заявке:',
]);

ensure_entity_cfg_set(24, [
    'menu_title' => 'Рабочие обсуждения',
    'listing_heading' => 'Рабочие обсуждения',
    'window_heading' => 'Карточка обсуждения',
    'insert_button' => 'Добавить обсуждение',
    'use_comments' => '1',
    'email_subject_new_item' => 'Новое обсуждение:',
    'email_subject_new_comment' => 'Новый комментарий к обсуждению:',
]);

ensure_entity_cfg_set(25, [
    'menu_title' => 'Карточки документов',
    'listing_heading' => 'Карточки документов',
    'window_heading' => 'Карточка документа',
    'insert_button' => 'Создать карточку документа',
    'use_comments' => '1',
    'email_subject_new_item' => 'Новый документ:',
    'email_subject_new_comment' => 'Новый комментарий к документу:',
]);

ensure_entity_cfg_set(26, [
    'menu_title' => 'База документов',
    'listing_heading' => 'База документов',
    'window_heading' => 'Карточка документа базы',
    'insert_button' => 'Добавить документ',
    'use_comments' => '1',
    'email_subject_new_item' => 'Новый материал базы документов:',
    'email_subject_new_comment' => 'Новый комментарий к документу базы:',
]);

ensure_entity_cfg_set(27, [
    'menu_title' => 'Заявки на МТЗ',
    'listing_heading' => 'Заявки на МТЗ',
    'window_heading' => 'Карточка заявки МТЗ',
    'insert_button' => 'Создать заявку МТЗ',
    'use_comments' => '1',
    'email_subject_new_item' => 'Новая заявка на МТЗ:',
    'email_subject_new_comment' => 'Новый комментарий к заявке МТЗ:',
]);

$project_main_tab = ensure_form_tab(21, 'Основное', 0, ['Информация']);
$project_team_tab = ensure_form_tab(21, 'Команда и роли', 1, ['Команда']);
$project_control_tab = ensure_form_tab(21, 'Контроль', 2);

$task_main_tab = ensure_form_tab(22, 'Основное', 0, ['Информация']);
$task_control_tab = ensure_form_tab(22, 'Сроки и трудозатраты', 1, ['Время']);

$request_main_tab = ensure_form_tab(23, 'Регистрация', 0, ['Информация']);
$request_execution_tab = ensure_form_tab(23, 'Исполнение', 1);

$discussion_main_tab = ensure_form_tab(24, 'Основное', 0, ['Информация']);

$doc_card_tab = ensure_form_tab(25, 'Карточка', 0, ['Информация']);
$doc_flow_tab = ensure_form_tab(25, 'Согласование и архив', 1);

$doc_base_tab = ensure_form_tab(26, 'Документ', 0, ['Информация']);
$doc_base_review_tab = ensure_form_tab(26, 'Актуализация', 1);

$mts_tab = ensure_form_tab(27, 'Заявка', 0, ['Информация']);
$mts_supply_tab = ensure_form_tab(27, 'Исполнение', 1);

ensure_reserved_field(21, 'fieldtype_action', ['forms_tabs_id' => $project_main_tab, 'listing_status' => 1, 'listing_sort_order' => 0]);
ensure_reserved_field(21, 'fieldtype_id', ['forms_tabs_id' => $project_main_tab, 'listing_status' => 1, 'listing_sort_order' => 1]);
ensure_reserved_field(21, 'fieldtype_date_added', ['forms_tabs_id' => $project_main_tab, 'listing_status' => 1, 'listing_sort_order' => 11]);
ensure_reserved_field(21, 'fieldtype_created_by', ['forms_tabs_id' => $project_main_tab, 'listing_status' => 1, 'listing_sort_order' => 12]);
ensure_reserved_field(21, 'fieldtype_parent_item_id', ['forms_tabs_id' => $project_main_tab, 'listing_status' => 0, 'listing_sort_order' => 100]);
ensure_reserved_field(21, 'fieldtype_date_updated', ['forms_tabs_id' => $project_main_tab, 'listing_status' => 0, 'listing_sort_order' => 0]);

$project_priority_id = ensure_custom_field(21, 'Приоритет', 'fieldtype_dropdown', $project_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-medium']),
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 2,
    'comments_status' => 1,
    'comments_sort_order' => 1,
]);
$project_stage_id = ensure_custom_field(21, 'Этап', 'fieldtype_dropdown', $project_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 4,
    'comments_status' => 1,
    'comments_sort_order' => 2,
], ['Статус']);
$project_name_id = ensure_custom_field(21, 'Название проекта', 'fieldtype_input', $project_main_tab, [
    'is_required' => 1,
    'is_heading' => 1,
    'configuration' => config_json(['allow_search' => '1', 'width' => 'input-xlarge']),
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 3,
], ['Название']);
$project_start_id = ensure_custom_field(21, 'Дата старта', 'fieldtype_input_date', $project_main_tab, [
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 8,
], ['Дата начала проекта']);
$project_description_id = ensure_custom_field(21, 'Описание', 'fieldtype_textarea_wysiwyg', $project_main_tab, [
    'configuration' => config_json(['allow_search' => '1']),
    'sort_order' => 4,
], ['Описание']);
$project_team_id = ensure_custom_field(21, 'Команда', 'fieldtype_users', $project_team_tab, [
    'configuration' => config_json(['display_as' => 'dropdown_muliple', 'allow_search' => '1']),
    'sort_order' => 0,
], ['Команда']);
$project_attachments_id = ensure_custom_field(21, 'Вложения', 'fieldtype_attachments', $project_main_tab, [
    'sort_order' => 5,
], ['Вложения']);
$project_manager_id = ensure_custom_field(21, 'Руководитель проекта', 'fieldtype_users', $project_team_tab, [
    'is_required' => 1,
    'configuration' => config_json(['display_as' => 'dropdown', 'allow_search' => '1']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 6,
    'comments_status' => 1,
    'comments_sort_order' => 3,
]);
$project_curator_id = ensure_custom_field(21, 'Куратор / преподаватель', 'fieldtype_users', $project_team_tab, [
    'configuration' => config_json(['display_as' => 'dropdown', 'allow_search' => '1']),
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 7,
    'comments_status' => 1,
    'comments_sort_order' => 4,
]);
$project_department_id = ensure_custom_field(21, 'Подразделение / направление', 'fieldtype_dropdown', $project_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 5,
]);
$project_plan_finish_id = ensure_custom_field(21, 'Плановая дата завершения', 'fieldtype_input_date', $project_control_tab, [
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 9,
    'comments_status' => 1,
    'comments_sort_order' => 5,
]);
$project_progress_id = ensure_custom_field(21, 'Прогресс', 'fieldtype_progress', $project_control_tab, [
    'configuration' => config_json(['step' => '5', 'display_progress_bar' => '1', 'bar_color' => '#214f8b']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 10,
    'comments_status' => 1,
    'comments_sort_order' => 6,
]);
$project_nau_link_id = ensure_custom_field(21, 'Ссылка на NauDoc', 'fieldtype_input_url', $project_control_tab, [
    'configuration' => config_json(['width' => 'input-xlarge', 'target' => '_blank', 'preview_text' => 'Открыть документ']),
    'sort_order' => 2,
]);
$project_doc_card_link_id = ensure_custom_field(21, 'Связанная карточка документа', 'fieldtype_entity', $project_control_tab, [
    'configuration' => config_json(['entity_id' => 25, 'display_as' => 'dropdown', 'width' => 'input-large', 'allow_search' => '1', 'display_as_link' => '1']),
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 13,
]);
$project_doc_sync_status_id = ensure_custom_field(21, 'Статус документа / интеграции', 'fieldtype_dropdown', $project_control_tab, [
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 4,
    'listing_status' => 1,
    'listing_sort_order' => 14,
]);
$project_manager_note_id = ensure_custom_field(21, 'Комментарий руководителя', 'fieldtype_textarea', $project_control_tab, [
    'sort_order' => 5,
]);

sync_field_choices(21, $project_priority_id, [
    ['name' => 'Критичный', 'sort_order' => 1, 'bg_color' => '#d90429'],
    ['name' => 'Высокий', 'sort_order' => 2, 'bg_color' => '#f77f00'],
    ['name' => 'Средний', 'sort_order' => 3, 'bg_color' => '#fcbf49', 'is_default' => 1],
    ['name' => 'Низкий', 'sort_order' => 4, 'bg_color' => '#3a86ff'],
]);
sync_field_choices(21, $project_stage_id, [
    ['name' => 'Инициирование', 'sort_order' => 1, 'bg_color' => '#c9d6ea', 'is_default' => 1],
    ['name' => 'В работе', 'sort_order' => 2, 'bg_color' => '#8ecae6'],
    ['name' => 'На согласовании', 'sort_order' => 3, 'bg_color' => '#ffd166'],
    ['name' => 'На паузе', 'sort_order' => 4, 'bg_color' => '#adb5bd'],
    ['name' => 'Завершен', 'sort_order' => 5, 'bg_color' => '#95d5b2'],
    ['name' => 'В архиве', 'sort_order' => 6, 'bg_color' => '#ced4da'],
]);
sync_field_choices(21, $project_department_id, [
    ['name' => 'Администрация', 'sort_order' => 1, 'bg_color' => '#d8e2dc'],
    ['name' => 'Учебный отдел', 'sort_order' => 2, 'bg_color' => '#bee1e6'],
    ['name' => 'Кафедра / преподаватели', 'sort_order' => 3, 'bg_color' => '#cdb4db'],
    ['name' => 'Методический отдел', 'sort_order' => 4, 'bg_color' => '#ffc8dd'],
    ['name' => 'ИТ и сервис', 'sort_order' => 5, 'bg_color' => '#bde0fe'],
    ['name' => 'АХО / снабжение', 'sort_order' => 6, 'bg_color' => '#ffe5b4'],
]);
sync_field_choices(21, $project_doc_sync_status_id, [
    ['name' => 'Ожидает документ', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#dee2e6'],
    ['name' => 'Связано', 'sort_order' => 2, 'bg_color' => '#bde0fe'],
    ['name' => 'Черновик', 'sort_order' => 3, 'bg_color' => '#c9d6ea'],
    ['name' => 'На согласовании', 'sort_order' => 4, 'bg_color' => '#ffd166'],
    ['name' => 'На утверждении', 'sort_order' => 5, 'bg_color' => '#ffddd2'],
    ['name' => 'Подписан', 'sort_order' => 6, 'bg_color' => '#95d5b2'],
    ['name' => 'На ознакомлении', 'sort_order' => 7, 'bg_color' => '#bde0fe'],
    ['name' => 'Зарегистрирован', 'sort_order' => 8, 'bg_color' => '#cce3de'],
    ['name' => 'Архивирован', 'sort_order' => 9, 'bg_color' => '#adb5bd'],
    ['name' => 'Ошибка синхронизации', 'sort_order' => 10, 'bg_color' => '#d90429'],
]);

ensure_reserved_field(22, 'fieldtype_action', ['forms_tabs_id' => $task_main_tab, 'listing_status' => 1, 'listing_sort_order' => 0]);
ensure_reserved_field(22, 'fieldtype_id', ['forms_tabs_id' => $task_main_tab, 'listing_status' => 1, 'listing_sort_order' => 1]);
ensure_reserved_field(22, 'fieldtype_date_added', ['forms_tabs_id' => $task_main_tab, 'listing_status' => 1, 'listing_sort_order' => 10]);
ensure_reserved_field(22, 'fieldtype_created_by', ['forms_tabs_id' => $task_main_tab, 'listing_status' => 1, 'listing_sort_order' => 11]);
ensure_reserved_field(22, 'fieldtype_parent_item_id', ['forms_tabs_id' => $task_main_tab, 'listing_status' => 0, 'listing_sort_order' => 100]);
ensure_reserved_field(22, 'fieldtype_date_updated', ['forms_tabs_id' => $task_main_tab, 'listing_status' => 0, 'listing_sort_order' => 0]);

$task_type_id = ensure_custom_field(22, 'Тип задачи', 'fieldtype_dropdown', $task_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 3,
], ['Тип']);
$task_name_id = ensure_custom_field(22, 'Название задачи', 'fieldtype_input', $task_main_tab, [
    'is_required' => 1,
    'is_heading' => 1,
    'configuration' => config_json(['allow_search' => '1', 'width' => 'input-xlarge']),
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 4,
], ['Название']);
$task_status_id = ensure_custom_field(22, 'Статус', 'fieldtype_dropdown', $task_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 5,
    'comments_status' => 1,
    'comments_sort_order' => 2,
], ['Статус']);
$task_priority_id = ensure_custom_field(22, 'Приоритет', 'fieldtype_dropdown', $task_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-medium']),
    'sort_order' => 4,
    'listing_status' => 1,
    'listing_sort_order' => 2,
    'comments_status' => 1,
    'comments_sort_order' => 1,
], ['Приоритет']);
$task_assignee_id = ensure_custom_field(22, 'Исполнители', 'fieldtype_users', $task_main_tab, [
    'configuration' => config_json(['display_as' => 'dropdown_muliple', 'allow_search' => '1']),
    'sort_order' => 5,
    'listing_status' => 1,
    'listing_sort_order' => 6,
], ['Назначен на']);
$task_description_id = ensure_custom_field(22, 'Описание', 'fieldtype_textarea_wysiwyg', $task_main_tab, [
    'configuration' => config_json(['allow_search' => '1']),
    'sort_order' => 6,
], ['Описание']);
$task_plan_hours_id = ensure_custom_field(22, 'Плановые часы', 'fieldtype_input_numeric', $task_control_tab, [
    'configuration' => config_json(['width' => 'input-small', 'number_format' => '2/./*']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 7,
], ['Расчетное время']);
$task_fact_hours_id = ensure_custom_field(22, 'Факт часов', 'fieldtype_input_numeric_comments', $task_control_tab, [
    'configuration' => config_json(['width' => 'input-small', 'number_format' => '2/./*']),
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 8,
    'comments_status' => 1,
    'comments_sort_order' => 3,
], ['Затрачено времени']);
$task_start_date_id = ensure_custom_field(22, 'Дата начала', 'fieldtype_input_date', $task_control_tab, [
    'sort_order' => 3,
], ['Дата начала']);
$task_due_date_id = ensure_custom_field(22, 'Срок исполнения', 'fieldtype_input_date', $task_control_tab, [
    'sort_order' => 4,
    'listing_status' => 1,
    'listing_sort_order' => 9,
    'comments_status' => 1,
    'comments_sort_order' => 4,
], ['Дата окончания']);
$task_attachments_id = ensure_custom_field(22, 'Вложения', 'fieldtype_attachments', $task_main_tab, [
    'sort_order' => 7,
], ['Вложения']);
$task_requester_id = ensure_custom_field(22, 'Постановщик', 'fieldtype_users', $task_main_tab, [
    'configuration' => config_json(['display_as' => 'dropdown', 'allow_search' => '1']),
    'sort_order' => 6,
]);
$task_doc_link_id = ensure_custom_field(22, 'Связанная карточка документа', 'fieldtype_entity', $task_control_tab, [
    'configuration' => config_json(['entity_id' => 25, 'display_as' => 'dropdown', 'width' => 'input-large', 'allow_search' => '1', 'display_as_link' => '1']),
    'sort_order' => 5,
]);
$task_nau_link_id = ensure_custom_field(22, 'Ссылка на NauDoc', 'fieldtype_input_url', $task_control_tab, [
    'configuration' => config_json(['width' => 'input-xlarge', 'target' => '_blank', 'preview_text' => 'Открыть документ']),
    'sort_order' => 6,
]);

sync_field_choices(22, $task_type_id, [
    ['name' => 'Поручение', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#d8f3dc'],
    ['name' => 'Согласование', 'sort_order' => 2, 'bg_color' => '#ffd166'],
    ['name' => 'Подготовка документа', 'sort_order' => 3, 'bg_color' => '#bde0fe'],
    ['name' => 'Контроль исполнения', 'sort_order' => 4, 'bg_color' => '#f8edeb'],
]);
sync_field_choices(22, $task_status_id, [
    ['name' => 'Новая', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#dee2e6'],
    ['name' => 'В работе', 'sort_order' => 2, 'bg_color' => '#8ecae6'],
    ['name' => 'На согласовании', 'sort_order' => 3, 'bg_color' => '#ffd166'],
    ['name' => 'На проверке', 'sort_order' => 4, 'bg_color' => '#ffddd2'],
    ['name' => 'Выполнена', 'sort_order' => 5, 'bg_color' => '#95d5b2'],
    ['name' => 'Отменена', 'sort_order' => 6, 'bg_color' => '#adb5bd'],
]);
sync_field_choices(22, $task_priority_id, [
    ['name' => 'Критичный', 'sort_order' => 1, 'bg_color' => '#d90429'],
    ['name' => 'Высокий', 'sort_order' => 2, 'bg_color' => '#f77f00'],
    ['name' => 'Средний', 'sort_order' => 3, 'bg_color' => '#fcbf49', 'is_default' => 1],
    ['name' => 'Низкий', 'sort_order' => 4, 'bg_color' => '#3a86ff'],
]);

ensure_reserved_field(23, 'fieldtype_action', ['forms_tabs_id' => $request_main_tab, 'listing_status' => 1, 'listing_sort_order' => 0]);
ensure_reserved_field(23, 'fieldtype_id', ['forms_tabs_id' => $request_main_tab, 'listing_status' => 1, 'listing_sort_order' => 1]);
ensure_reserved_field(23, 'fieldtype_date_added', ['forms_tabs_id' => $request_main_tab, 'listing_status' => 1, 'listing_sort_order' => 8]);
ensure_reserved_field(23, 'fieldtype_created_by', ['forms_tabs_id' => $request_main_tab, 'listing_status' => 1, 'listing_sort_order' => 9]);
ensure_reserved_field(23, 'fieldtype_parent_item_id', ['forms_tabs_id' => $request_main_tab, 'listing_status' => 0, 'listing_sort_order' => 100]);
ensure_reserved_field(23, 'fieldtype_date_updated', ['forms_tabs_id' => $request_main_tab, 'listing_status' => 0, 'listing_sort_order' => 0]);

$request_group_id = ensure_custom_field(23, 'Заявитель / группа', 'fieldtype_grouped_users', $request_main_tab, [
    'is_required' => 1,
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 4,
    'comments_status' => 1,
    'comments_sort_order' => 1,
], ['Отдел']);
$request_type_id = ensure_custom_field(23, 'Тип заявки', 'fieldtype_dropdown', $request_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 2,
    'comments_status' => 1,
    'comments_sort_order' => 2,
], ['Тип']);
$request_priority_id = ensure_custom_field(23, 'Приоритет', 'fieldtype_dropdown', $request_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-medium']),
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 6,
    'comments_status' => 1,
    'comments_sort_order' => 4,
], ['Приоритет']);
$request_subject_id = ensure_custom_field(23, 'Тема заявки', 'fieldtype_input', $request_main_tab, [
    'is_required' => 1,
    'is_heading' => 1,
    'configuration' => config_json(['allow_search' => '1', 'width' => 'input-xlarge']),
    'sort_order' => 4,
    'listing_status' => 1,
    'listing_sort_order' => 3,
], ['Тема']);
$request_description_id = ensure_custom_field(23, 'Описание', 'fieldtype_textarea_wysiwyg', $request_main_tab, [
    'configuration' => config_json(['allow_search' => '1']),
    'sort_order' => 5,
], ['Описание']);
$request_status_id = ensure_custom_field(23, 'Статус', 'fieldtype_dropdown', $request_main_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 5,
    'comments_status' => 1,
    'comments_sort_order' => 3,
], ['Статус']);
$request_attachments_id = ensure_custom_field(23, 'Вложения', 'fieldtype_attachments', $request_main_tab, [
    'sort_order' => 6,
], ['Вложения']);
$request_channel_id = ensure_custom_field(23, 'Канал поступления', 'fieldtype_dropdown', $request_execution_tab, [
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 6,
]);
$request_responsible_id = ensure_custom_field(23, 'Ответственный', 'fieldtype_users', $request_execution_tab, [
    'configuration' => config_json(['display_as' => 'dropdown', 'allow_search' => '1']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 7,
    'comments_status' => 1,
    'comments_sort_order' => 4,
]);
$request_due_date_id = ensure_custom_field(23, 'Срок исполнения', 'fieldtype_input_date', $request_execution_tab, [
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 10,
    'comments_status' => 1,
    'comments_sort_order' => 5,
]);
$request_service_category_id = ensure_custom_field(23, 'Категория услуги', 'fieldtype_dropdown', $request_execution_tab, [
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 11,
]);
$request_project_link_id = ensure_custom_field(23, 'Связанный проект', 'fieldtype_entity', $request_execution_tab, [
    'configuration' => config_json(['entity_id' => 21, 'display_as' => 'dropdown', 'width' => 'input-large', 'allow_search' => '1', 'display_as_link' => '1']),
    'sort_order' => 4,
    'listing_status' => 1,
    'listing_sort_order' => 8,
]);
$request_doc_link_id = ensure_custom_field(23, 'Связанная карточка документа', 'fieldtype_entity', $request_execution_tab, [
    'configuration' => config_json(['entity_id' => 25, 'display_as' => 'dropdown', 'width' => 'input-large', 'allow_search' => '1', 'display_as_link' => '1']),
    'sort_order' => 5,
    'listing_status' => 1,
    'listing_sort_order' => 9,
]);
$request_nau_link_id = ensure_custom_field(23, 'Ссылка на NauDoc', 'fieldtype_input_url', $request_execution_tab, [
    'configuration' => config_json(['width' => 'input-xlarge', 'target' => '_blank', 'preview_text' => 'Открыть документ']),
    'sort_order' => 6,
]);
$request_doc_sync_status_id = ensure_custom_field(23, 'Статус документа / интеграции', 'fieldtype_dropdown', $request_execution_tab, [
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 7,
    'listing_status' => 1,
    'listing_sort_order' => 12,
]);
$request_resolution_id = ensure_custom_field(23, 'Результат исполнения', 'fieldtype_textarea', $request_execution_tab, [
    'sort_order' => 8,
], ['Решение']);

sync_field_choices(23, $request_type_id, [
    ['name' => 'Техническая поддержка', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#bde0fe'],
    ['name' => 'Методический вопрос', 'sort_order' => 2, 'bg_color' => '#cdb4db'],
    ['name' => 'Хозяйственный запрос', 'sort_order' => 3, 'bg_color' => '#ffe5b4'],
    ['name' => 'Документооборот', 'sort_order' => 4, 'bg_color' => '#ffd6a5'],
    ['name' => 'Доступ / учетная запись', 'sort_order' => 5, 'bg_color' => '#d8f3dc'],
]);
sync_field_choices(23, $request_group_id, [
    ['name' => 'Администрация', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#d8e2dc', 'users' => '1'],
    ['name' => 'Учебный отдел', 'sort_order' => 2, 'bg_color' => '#bee1e6', 'users' => '1'],
    ['name' => 'Кафедра / преподаватели', 'sort_order' => 3, 'bg_color' => '#cdb4db', 'users' => '1'],
    ['name' => 'Методический отдел', 'sort_order' => 4, 'bg_color' => '#ffc8dd', 'users' => '1'],
    ['name' => 'ИТ и сервис', 'sort_order' => 5, 'bg_color' => '#bde0fe', 'users' => '1'],
    ['name' => 'АХО / снабжение', 'sort_order' => 6, 'bg_color' => '#ffe5b4', 'users' => '1'],
]);
sync_field_choices(23, $request_priority_id, [
    ['name' => 'Критичный', 'sort_order' => 1, 'bg_color' => '#d90429'],
    ['name' => 'Высокий', 'sort_order' => 2, 'bg_color' => '#f77f00'],
    ['name' => 'Средний', 'sort_order' => 3, 'bg_color' => '#fcbf49', 'is_default' => 1],
    ['name' => 'Низкий', 'sort_order' => 4, 'bg_color' => '#3a86ff'],
]);
sync_field_choices(23, $request_status_id, [
    ['name' => 'Новая', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#dee2e6'],
    ['name' => 'Принята', 'sort_order' => 2, 'bg_color' => '#bde0fe'],
    ['name' => 'В работе', 'sort_order' => 3, 'bg_color' => '#8ecae6'],
    ['name' => 'На согласовании', 'sort_order' => 4, 'bg_color' => '#ffd166'],
    ['name' => 'Ожидает заявителя', 'sort_order' => 5, 'bg_color' => '#ffddd2'],
    ['name' => 'Выполнена', 'sort_order' => 6, 'bg_color' => '#95d5b2'],
    ['name' => 'Отклонена', 'sort_order' => 7, 'bg_color' => '#adb5bd'],
]);
sync_field_choices(23, $request_channel_id, [
    ['name' => 'Веб-форма', 'sort_order' => 1, 'is_default' => 1],
    ['name' => 'Телефон', 'sort_order' => 2],
    ['name' => 'Почта', 'sort_order' => 3],
    ['name' => 'Мессенджер', 'sort_order' => 4],
    ['name' => 'Лично', 'sort_order' => 5],
]);
sync_field_choices(23, $request_service_category_id, [
    ['name' => 'ИТ', 'sort_order' => 1, 'is_default' => 1],
    ['name' => 'Документы', 'sort_order' => 2],
    ['name' => 'Учебный процесс', 'sort_order' => 3],
    ['name' => 'АХО / МТЗ', 'sort_order' => 4],
    ['name' => 'Административное обслуживание', 'sort_order' => 5],
]);
sync_field_choices(23, $request_doc_sync_status_id, [
    ['name' => 'Ожидает документ', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#dee2e6'],
    ['name' => 'Связано', 'sort_order' => 2, 'bg_color' => '#bde0fe'],
    ['name' => 'Черновик', 'sort_order' => 3, 'bg_color' => '#c9d6ea'],
    ['name' => 'На согласовании', 'sort_order' => 4, 'bg_color' => '#ffd166'],
    ['name' => 'На утверждении', 'sort_order' => 5, 'bg_color' => '#ffddd2'],
    ['name' => 'Подписан', 'sort_order' => 6, 'bg_color' => '#95d5b2'],
    ['name' => 'На ознакомлении', 'sort_order' => 7, 'bg_color' => '#bde0fe'],
    ['name' => 'Зарегистрирован', 'sort_order' => 8, 'bg_color' => '#cce3de'],
    ['name' => 'Архивирован', 'sort_order' => 9, 'bg_color' => '#adb5bd'],
    ['name' => 'Ошибка синхронизации', 'sort_order' => 10, 'bg_color' => '#d90429'],
]);

ensure_reserved_field(24, 'fieldtype_action', ['forms_tabs_id' => $discussion_main_tab, 'listing_status' => 1, 'listing_sort_order' => 0]);
ensure_reserved_field(24, 'fieldtype_id', ['forms_tabs_id' => $discussion_main_tab, 'listing_status' => 1, 'listing_sort_order' => 1]);
ensure_reserved_field(24, 'fieldtype_date_added', ['forms_tabs_id' => $discussion_main_tab, 'listing_status' => 1, 'listing_sort_order' => 4]);
ensure_reserved_field(24, 'fieldtype_created_by', ['forms_tabs_id' => $discussion_main_tab, 'listing_status' => 1, 'listing_sort_order' => 5]);
ensure_reserved_field(24, 'fieldtype_parent_item_id', ['forms_tabs_id' => $discussion_main_tab, 'listing_status' => 0, 'listing_sort_order' => 100]);
ensure_reserved_field(24, 'fieldtype_date_updated', ['forms_tabs_id' => $discussion_main_tab, 'listing_status' => 0, 'listing_sort_order' => 0]);

$discussion_status_id = ensure_custom_field(24, 'Статус', 'fieldtype_dropdown', $discussion_main_tab, [
    'configuration' => config_json(['width' => 'input-medium']),
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 2,
    'comments_status' => 1,
], ['Статус']);
$discussion_title_id = ensure_custom_field(24, 'Тема обсуждения', 'fieldtype_input', $discussion_main_tab, [
    'is_required' => 1,
    'is_heading' => 1,
    'configuration' => config_json(['allow_search' => '1', 'width' => 'input-xlarge']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 3,
], ['Название']);
$discussion_description_id = ensure_custom_field(24, 'Описание', 'fieldtype_textarea_wysiwyg', $discussion_main_tab, [
    'configuration' => config_json(['allow_search' => '1']),
    'sort_order' => 2,
], ['Описание']);
$discussion_attachments_id = ensure_custom_field(24, 'Вложения', 'fieldtype_attachments', $discussion_main_tab, [
    'sort_order' => 3,
], ['Вложения']);

sync_field_choices(24, $discussion_status_id, [
    ['name' => 'Открыто', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#bde0fe'],
    ['name' => 'В работе', 'sort_order' => 2, 'bg_color' => '#ffd166'],
    ['name' => 'Закрыто', 'sort_order' => 3, 'bg_color' => '#95d5b2'],
]);

ensure_reserved_field(25, 'fieldtype_action', ['forms_tabs_id' => $doc_card_tab, 'listing_status' => 1, 'listing_sort_order' => 0]);
ensure_reserved_field(25, 'fieldtype_id', ['forms_tabs_id' => $doc_card_tab, 'listing_status' => 1, 'listing_sort_order' => 1]);
ensure_reserved_field(25, 'fieldtype_date_added', ['forms_tabs_id' => $doc_card_tab, 'listing_status' => 1, 'listing_sort_order' => 9]);
ensure_reserved_field(25, 'fieldtype_created_by', ['forms_tabs_id' => $doc_card_tab, 'listing_status' => 1, 'listing_sort_order' => 10]);
ensure_reserved_field(25, 'fieldtype_parent_item_id', ['forms_tabs_id' => $doc_card_tab, 'listing_status' => 0, 'listing_sort_order' => 100]);
ensure_reserved_field(25, 'fieldtype_date_updated', ['forms_tabs_id' => $doc_card_tab, 'listing_status' => 0, 'listing_sort_order' => 0]);

$doc_title_id = ensure_custom_field(25, 'Наименование документа', 'fieldtype_input', $doc_card_tab, [
    'is_required' => 1,
    'is_heading' => 1,
    'configuration' => config_json(['allow_search' => '1', 'width' => 'input-xlarge']),
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 3,
]);
$doc_type_id = ensure_custom_field(25, 'Тип документа', 'fieldtype_dropdown', $doc_card_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 2,
    'comments_status' => 1,
], []);
$doc_status_id = ensure_custom_field(25, 'Статус документа', 'fieldtype_dropdown', $doc_flow_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 4,
    'comments_status' => 1,
], []);
$doc_reg_number_id = ensure_custom_field(25, 'Регистрационный номер', 'fieldtype_input', $doc_card_tab, [
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 5,
]);
$doc_date_id = ensure_custom_field(25, 'Дата документа', 'fieldtype_input_date', $doc_card_tab, [
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 6,
]);
$doc_owner_id = ensure_custom_field(25, 'Ответственный', 'fieldtype_users', $doc_card_tab, [
    'configuration' => config_json(['display_as' => 'dropdown', 'allow_search' => '1']),
    'sort_order' => 4,
    'listing_status' => 1,
    'listing_sort_order' => 7,
]);
$doc_expire_id = ensure_custom_field(25, 'Срок действия', 'fieldtype_input_date', $doc_flow_tab, [
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 8,
]);
$doc_version_id = ensure_custom_field(25, 'Версия', 'fieldtype_input', $doc_flow_tab, [
    'configuration' => config_json(['width' => 'input-medium']),
    'sort_order' => 2,
]);
$doc_draft_id = ensure_custom_field(25, 'Рабочий черновик', 'fieldtype_onlyoffice', $doc_card_tab, [
    'configuration' => config_json([
        'url_to_js_api' => onlyoffice_public_js_api_url(),
        'secret_key' => onlyoffice_jwt_secret(),
        'allow_edit' => 'users_edit_access',
        'lang' => 'ru',
        'location' => 'ru',
        'region' => 'ru-RU',
        'allow_change_file_name' => '1',
        'upload_limit' => '1',
        'upload_size_limit' => '64',
        'allowed_extensions' => ['.docx', '.xlsx', '.pptx', '.odt', '.ods', '.odp', '.txt'],
        'display_date_added' => '1',
    ]),
    'sort_order' => 6,
]);
$doc_nau_link_id = ensure_custom_field(25, 'Ссылка на NauDoc', 'fieldtype_input_url', $doc_flow_tab, [
    'configuration' => config_json(['width' => 'input-xlarge', 'target' => '_blank', 'preview_text' => 'Открыть документ']),
    'sort_order' => 3,
]);
$doc_project_link_id = ensure_custom_field(25, 'Связанный проект', 'fieldtype_entity', $doc_flow_tab, [
    'configuration' => config_json(['entity_id' => 21, 'display_as' => 'dropdown', 'width' => 'input-large', 'allow_search' => '1', 'display_as_link' => '1']),
    'sort_order' => 4,
    'listing_status' => 1,
    'listing_sort_order' => 11,
]);
$doc_request_link_id = ensure_custom_field(25, 'Связанная заявка', 'fieldtype_entity', $doc_flow_tab, [
    'configuration' => config_json(['entity_id' => 23, 'display_as' => 'dropdown', 'width' => 'input-large', 'allow_search' => '1', 'display_as_link' => '1']),
    'sort_order' => 5,
    'listing_status' => 1,
    'listing_sort_order' => 12,
]);
$doc_description_id = ensure_custom_field(25, 'Описание', 'fieldtype_textarea_wysiwyg', $doc_card_tab, [
    'configuration' => config_json(['allow_search' => '1']),
    'sort_order' => 5,
]);
$doc_attachments_id = ensure_custom_field(25, 'Вложения', 'fieldtype_attachments', $doc_card_tab, [
    'sort_order' => 7,
]);

sync_field_choices(25, $doc_type_id, [
    ['name' => 'Входящий документ', 'sort_order' => 1, 'bg_color' => '#d8f3dc'],
    ['name' => 'Исходящий документ', 'sort_order' => 2, 'bg_color' => '#bde0fe'],
    ['name' => 'Внутренний документ', 'sort_order' => 3, 'is_default' => 1, 'bg_color' => '#e9ecef'],
    ['name' => 'Служебная записка', 'sort_order' => 4, 'bg_color' => '#ffd6a5'],
    ['name' => 'Приказ', 'sort_order' => 5, 'bg_color' => '#cce3de'],
    ['name' => 'Договор', 'sort_order' => 6, 'bg_color' => '#cdb4db'],
    ['name' => 'Акт', 'sort_order' => 7, 'bg_color' => '#ffe5b4'],
    ['name' => 'Регламент', 'sort_order' => 8, 'bg_color' => '#ffcad4'],
    ['name' => 'Заявление', 'sort_order' => 9, 'bg_color' => '#ffddd2'],
    ['name' => 'Иное', 'sort_order' => 10, 'bg_color' => '#adb5bd'],
]);
sync_field_choices(25, $doc_status_id, [
    ['name' => 'Черновик', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#dee2e6'],
    ['name' => 'На согласовании', 'sort_order' => 2, 'bg_color' => '#ffd166'],
    ['name' => 'На утверждении', 'sort_order' => 3, 'bg_color' => '#ffddd2'],
    ['name' => 'Подписан', 'sort_order' => 4, 'bg_color' => '#95d5b2'],
    ['name' => 'На ознакомлении', 'sort_order' => 5, 'bg_color' => '#bde0fe'],
    ['name' => 'На регистрации', 'sort_order' => 6, 'bg_color' => '#f8edeb'],
    ['name' => 'Зарегистрирован', 'sort_order' => 7, 'bg_color' => '#cce3de'],
    ['name' => 'Архивирован', 'sort_order' => 8, 'bg_color' => '#adb5bd'],
]);

ensure_reserved_field(26, 'fieldtype_action', ['forms_tabs_id' => $doc_base_tab, 'listing_status' => 1, 'listing_sort_order' => 0]);
ensure_reserved_field(26, 'fieldtype_id', ['forms_tabs_id' => $doc_base_tab, 'listing_status' => 1, 'listing_sort_order' => 1]);
ensure_reserved_field(26, 'fieldtype_date_added', ['forms_tabs_id' => $doc_base_tab, 'listing_status' => 1, 'listing_sort_order' => 8]);
ensure_reserved_field(26, 'fieldtype_created_by', ['forms_tabs_id' => $doc_base_tab, 'listing_status' => 1, 'listing_sort_order' => 9]);
ensure_reserved_field(26, 'fieldtype_parent_item_id', ['forms_tabs_id' => $doc_base_tab, 'listing_status' => 0, 'listing_sort_order' => 100]);
ensure_reserved_field(26, 'fieldtype_date_updated', ['forms_tabs_id' => $doc_base_tab, 'listing_status' => 0, 'listing_sort_order' => 0]);

$doc_base_title_id = ensure_custom_field(26, 'Название материала', 'fieldtype_input', $doc_base_tab, [
    'is_required' => 1,
    'is_heading' => 1,
    'configuration' => config_json(['allow_search' => '1', 'width' => 'input-xlarge']),
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 3,
]);
$doc_base_category_id = ensure_custom_field(26, 'Категория', 'fieldtype_dropdown', $doc_base_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 2,
], []);
$doc_base_status_id = ensure_custom_field(26, 'Статус актуальности', 'fieldtype_dropdown', $doc_base_review_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 4,
    'comments_status' => 1,
], []);
$doc_base_version_id = ensure_custom_field(26, 'Версия', 'fieldtype_input', $doc_base_review_tab, [
    'configuration' => config_json(['width' => 'input-medium']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 5,
]);
$doc_base_owner_id = ensure_custom_field(26, 'Ответственный', 'fieldtype_users', $doc_base_review_tab, [
    'configuration' => config_json(['display_as' => 'dropdown', 'allow_search' => '1']),
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 6,
]);
$doc_base_next_review_id = ensure_custom_field(26, 'Следующий пересмотр', 'fieldtype_input_date', $doc_base_review_tab, [
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 7,
]);
$doc_base_nau_link_id = ensure_custom_field(26, 'Ссылка на NauDoc', 'fieldtype_input_url', $doc_base_review_tab, [
    'configuration' => config_json(['width' => 'input-xlarge', 'target' => '_blank', 'preview_text' => 'Открыть документ']),
    'sort_order' => 4,
]);
$doc_base_tags_id = ensure_custom_field(26, 'Теги', 'fieldtype_tags', $doc_base_tab, [
    'sort_order' => 2,
]);
$doc_base_description_id = ensure_custom_field(26, 'Краткое описание', 'fieldtype_textarea_wysiwyg', $doc_base_tab, [
    'configuration' => config_json(['allow_search' => '1']),
    'sort_order' => 3,
]);
$doc_base_attachments_id = ensure_custom_field(26, 'Вложения', 'fieldtype_attachments', $doc_base_tab, [
    'sort_order' => 4,
]);

sync_field_choices(26, $doc_base_category_id, [
    ['name' => 'Регламент', 'sort_order' => 1, 'bg_color' => '#cdb4db'],
    ['name' => 'Шаблон', 'sort_order' => 2, 'bg_color' => '#bde0fe'],
    ['name' => 'Инструкция', 'sort_order' => 3, 'bg_color' => '#ffd6a5'],
    ['name' => 'Методический материал', 'sort_order' => 4, 'bg_color' => '#d8f3dc'],
    ['name' => 'Архивный материал', 'sort_order' => 5, 'bg_color' => '#dee2e6'],
]);
sync_field_choices(26, $doc_base_status_id, [
    ['name' => 'Действует', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#95d5b2'],
    ['name' => 'На пересмотре', 'sort_order' => 2, 'bg_color' => '#ffd166'],
    ['name' => 'Архив', 'sort_order' => 3, 'bg_color' => '#adb5bd'],
]);

ensure_reserved_field(27, 'fieldtype_action', ['forms_tabs_id' => $mts_tab, 'listing_status' => 1, 'listing_sort_order' => 0]);
ensure_reserved_field(27, 'fieldtype_id', ['forms_tabs_id' => $mts_tab, 'listing_status' => 1, 'listing_sort_order' => 1]);
ensure_reserved_field(27, 'fieldtype_date_added', ['forms_tabs_id' => $mts_tab, 'listing_status' => 1, 'listing_sort_order' => 7]);
ensure_reserved_field(27, 'fieldtype_created_by', ['forms_tabs_id' => $mts_tab, 'listing_status' => 1, 'listing_sort_order' => 8]);
ensure_reserved_field(27, 'fieldtype_parent_item_id', ['forms_tabs_id' => $mts_tab, 'listing_status' => 0, 'listing_sort_order' => 100]);
ensure_reserved_field(27, 'fieldtype_date_updated', ['forms_tabs_id' => $mts_tab, 'listing_status' => 0, 'listing_sort_order' => 0]);

$mts_name_id = ensure_custom_field(27, 'Наименование потребности', 'fieldtype_input', $mts_tab, [
    'is_required' => 1,
    'is_heading' => 1,
    'configuration' => config_json(['allow_search' => '1', 'width' => 'input-xlarge']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 3,
]);
$mts_requester_id = ensure_custom_field(27, 'Инициатор / группа', 'fieldtype_grouped_users', $mts_tab, [
    'is_required' => 1,
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 6,
], ['Заявитель / группа']);
$mts_category_id = ensure_custom_field(27, 'Категория МТЗ', 'fieldtype_dropdown', $mts_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 2,
]);
$mts_quantity_id = ensure_custom_field(27, 'Количество', 'fieldtype_input_numeric', $mts_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-small', 'number_format' => '0/./*']),
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 4,
]);
$mts_priority_id = ensure_custom_field(27, 'Приоритет', 'fieldtype_dropdown', $mts_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-medium']),
    'sort_order' => 4,
    'listing_status' => 1,
    'listing_sort_order' => 5,
]);
$mts_status_id = ensure_custom_field(27, 'Статус', 'fieldtype_dropdown', $mts_supply_tab, [
    'is_required' => 1,
    'configuration' => config_json(['width' => 'input-large']),
    'sort_order' => 0,
    'listing_status' => 1,
    'listing_sort_order' => 6,
    'comments_status' => 1,
], []);
$mts_owner_id = ensure_custom_field(27, 'Ответственный', 'fieldtype_users', $mts_supply_tab, [
    'configuration' => config_json(['display_as' => 'dropdown', 'allow_search' => '1']),
    'sort_order' => 1,
    'listing_status' => 1,
    'listing_sort_order' => 7,
]);
$mts_delivery_id = ensure_custom_field(27, 'Плановая дата поставки', 'fieldtype_input_date', $mts_supply_tab, [
    'sort_order' => 2,
    'listing_status' => 1,
    'listing_sort_order' => 9,
]);
$mts_project_id = ensure_custom_field(27, 'Связанный проект', 'fieldtype_entity', $mts_supply_tab, [
    'configuration' => config_json(['entity_id' => 21, 'display_as' => 'dropdown', 'width' => 'input-large', 'allow_search' => '1', 'display_as_link' => '1']),
    'sort_order' => 3,
    'listing_status' => 1,
    'listing_sort_order' => 8,
]);
$mts_nau_link_id = ensure_custom_field(27, 'Ссылка на NauDoc', 'fieldtype_input_url', $mts_supply_tab, [
    'configuration' => config_json(['width' => 'input-xlarge', 'target' => '_blank', 'preview_text' => 'Открыть документ']),
    'sort_order' => 4,
]);
$mts_reason_id = ensure_custom_field(27, 'Обоснование', 'fieldtype_textarea_wysiwyg', $mts_tab, [
    'configuration' => config_json(['allow_search' => '1']),
    'sort_order' => 5,
]);
$mts_attachments_id = ensure_custom_field(27, 'Вложения', 'fieldtype_attachments', $mts_tab, [
    'sort_order' => 6,
]);

sync_field_choices(27, $mts_category_id, [
    ['name' => 'Канцелярия', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#ffe5b4'],
    ['name' => 'Компьютерная техника', 'sort_order' => 2, 'bg_color' => '#bde0fe'],
    ['name' => 'Мебель', 'sort_order' => 3, 'bg_color' => '#d8f3dc'],
    ['name' => 'Расходные материалы', 'sort_order' => 4, 'bg_color' => '#ffd6a5'],
    ['name' => 'Программное обеспечение', 'sort_order' => 5, 'bg_color' => '#cdb4db'],
    ['name' => 'Иное', 'sort_order' => 6, 'bg_color' => '#dee2e6'],
]);
sync_field_choices(27, $mts_requester_id, [
    ['name' => 'Администрация', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#d8e2dc', 'users' => '1'],
    ['name' => 'Учебный отдел', 'sort_order' => 2, 'bg_color' => '#bee1e6', 'users' => '1'],
    ['name' => 'Кафедра / преподаватели', 'sort_order' => 3, 'bg_color' => '#cdb4db', 'users' => '1'],
    ['name' => 'Методический отдел', 'sort_order' => 4, 'bg_color' => '#ffc8dd', 'users' => '1'],
    ['name' => 'ИТ и сервис', 'sort_order' => 5, 'bg_color' => '#bde0fe', 'users' => '1'],
    ['name' => 'АХО / снабжение', 'sort_order' => 6, 'bg_color' => '#ffe5b4', 'users' => '1'],
]);
sync_field_choices(27, $mts_priority_id, [
    ['name' => 'Критичный', 'sort_order' => 1, 'bg_color' => '#d90429'],
    ['name' => 'Высокий', 'sort_order' => 2, 'bg_color' => '#f77f00'],
    ['name' => 'Средний', 'sort_order' => 3, 'bg_color' => '#fcbf49', 'is_default' => 1],
    ['name' => 'Низкий', 'sort_order' => 4, 'bg_color' => '#3a86ff'],
]);
sync_field_choices(27, $mts_status_id, [
    ['name' => 'Новая', 'sort_order' => 1, 'is_default' => 1, 'bg_color' => '#dee2e6'],
    ['name' => 'На согласовании', 'sort_order' => 2, 'bg_color' => '#ffd166'],
    ['name' => 'В закупке', 'sort_order' => 3, 'bg_color' => '#bde0fe'],
    ['name' => 'Заказано', 'sort_order' => 4, 'bg_color' => '#ffddd2'],
    ['name' => 'Получено', 'sort_order' => 5, 'bg_color' => '#95d5b2'],
    ['name' => 'Отклонена', 'sort_order' => 6, 'bg_color' => '#adb5bd'],
]);

$access_map = [
    21 => [$manager_group_id => 'view,create,update,delete,reports', $employee_group_id => 'view,create,update,reports', $requester_group_id => 'view_assigned', $office_group_id => 'view,reports'],
    22 => [$manager_group_id => 'view,create,update,delete,reports', $employee_group_id => 'view,create,update,reports', $requester_group_id => 'view_assigned,update', $office_group_id => 'view,reports'],
    23 => [$manager_group_id => 'view,create,update,delete,reports', $employee_group_id => 'view,create,update,reports', $requester_group_id => 'view_assigned,create,update,reports', $office_group_id => 'view,reports'],
    24 => [$manager_group_id => 'view,create,update,delete,reports', $employee_group_id => 'view_assigned,create,update,delete,reports', $requester_group_id => '', $office_group_id => ''],
    25 => [$manager_group_id => 'view,create,update,delete,reports', $employee_group_id => 'view,create,update,reports', $requester_group_id => 'view_assigned,create', $office_group_id => 'view,create,update,reports'],
    26 => [$manager_group_id => 'view,create,update,delete,reports', $employee_group_id => 'view,create,update,reports', $requester_group_id => 'view,reports', $office_group_id => 'view,create,update,reports'],
    27 => [$manager_group_id => 'view,create,update,delete,reports', $employee_group_id => 'view,create,update,reports', $requester_group_id => 'create,view_assigned,update,reports', $office_group_id => 'view,reports'],
];

foreach ($access_map as $entity_id => $groups)
{
    foreach ($groups as $group_id => $schema)
    {
        ensure_access_schema($entity_id, $group_id, $schema);
    }
}

$project_active_choices = array_filter([
    get_choice_id_by_name($project_stage_id, 'Инициирование'),
    get_choice_id_by_name($project_stage_id, 'В работе'),
    get_choice_id_by_name($project_stage_id, 'На согласовании'),
    get_choice_id_by_name($project_stage_id, 'На паузе'),
]);
$task_active_choices = array_filter([
    get_choice_id_by_name($task_status_id, 'Новая'),
    get_choice_id_by_name($task_status_id, 'В работе'),
    get_choice_id_by_name($task_status_id, 'На согласовании'),
    get_choice_id_by_name($task_status_id, 'На проверке'),
]);
$request_active_choices = array_filter([
    get_choice_id_by_name($request_status_id, 'Новая'),
    get_choice_id_by_name($request_status_id, 'Принята'),
    get_choice_id_by_name($request_status_id, 'В работе'),
    get_choice_id_by_name($request_status_id, 'На согласовании'),
    get_choice_id_by_name($request_status_id, 'Ожидает заявителя'),
]);
$doc_active_choices = array_filter([
    get_choice_id_by_name($doc_status_id, 'На согласовании'),
    get_choice_id_by_name($doc_status_id, 'На утверждении'),
    get_choice_id_by_name($doc_status_id, 'На ознакомлении'),
    get_choice_id_by_name($doc_status_id, 'На регистрации'),
]);
$mts_active_choices = array_filter([
    get_choice_id_by_name($mts_status_id, 'На согласовании'),
    get_choice_id_by_name($mts_status_id, 'В закупке'),
    get_choice_id_by_name($mts_status_id, 'Заказано'),
]);
$project_doc_attention_choices = array_filter([
    get_choice_id_by_name($project_doc_sync_status_id, 'Ожидает документ'),
    get_choice_id_by_name($project_doc_sync_status_id, 'Связано'),
    get_choice_id_by_name($project_doc_sync_status_id, 'Черновик'),
    get_choice_id_by_name($project_doc_sync_status_id, 'На согласовании'),
    get_choice_id_by_name($project_doc_sync_status_id, 'На утверждении'),
    get_choice_id_by_name($project_doc_sync_status_id, 'На ознакомлении'),
    get_choice_id_by_name($project_doc_sync_status_id, 'Ошибка синхронизации'),
]);
$request_doc_attention_choices = array_filter([
    get_choice_id_by_name($request_doc_sync_status_id, 'Ожидает документ'),
    get_choice_id_by_name($request_doc_sync_status_id, 'Связано'),
    get_choice_id_by_name($request_doc_sync_status_id, 'Черновик'),
    get_choice_id_by_name($request_doc_sync_status_id, 'На согласовании'),
    get_choice_id_by_name($request_doc_sync_status_id, 'На утверждении'),
    get_choice_id_by_name($request_doc_sync_status_id, 'На ознакомлении'),
    get_choice_id_by_name($request_doc_sync_status_id, 'Ошибка синхронизации'),
]);

$employee_tasks_report = ensure_common_report(22, 'Мои задачи в работе', [
    'description' => 'Задачи и поручения, которые требуют моего внимания прямо сейчас.',
    'users_groups' => '0,' . $manager_group_id . ',' . $employee_group_id . ',' . $requester_group_id,
    'in_dashboard' => 1,
    'in_dashboard_counter' => 1,
    'dashboard_sort_order' => 10,
    'dashboard_counter_sort_order' => 10,
    'menu_icon' => 'fa fa-check-square-o',
    'displays_assigned_only' => 1,
]);
sync_report_filters($employee_tasks_report, [
    ['fields_id' => $task_status_id, 'values' => $task_active_choices],
]);

$employee_requests_report = ensure_common_report(23, 'Мои заявки', [
    'description' => 'Собственные заявки и обращения, которые еще находятся в работе.',
    'users_groups' => '0,' . $manager_group_id . ',' . $employee_group_id . ',' . $requester_group_id,
    'in_dashboard' => 1,
    'in_dashboard_counter' => 1,
    'dashboard_sort_order' => 20,
    'dashboard_counter_sort_order' => 20,
    'menu_icon' => 'fa fa-life-ring',
    'displays_assigned_only' => 1,
]);
sync_report_filters($employee_requests_report, [
    ['fields_id' => $request_status_id, 'values' => $request_active_choices],
]);

$requests_doc_attention_report = ensure_common_report(23, 'Заявки без финального документа', [
    'description' => 'Заявки, по которым документ еще не завершен или есть риск по интеграции.',
    'users_groups' => '0,' . $manager_group_id,
    'in_dashboard' => 1,
    'in_dashboard_counter' => 1,
    'dashboard_sort_order' => 25,
    'dashboard_counter_sort_order' => 25,
    'menu_icon' => 'fa fa-exclamation-circle',
    'displays_assigned_only' => 0,
]);
sync_report_filters($requests_doc_attention_report, [
    ['fields_id' => $request_doc_sync_status_id, 'values' => $request_doc_attention_choices],
]);

$manager_projects_report = ensure_common_report(21, 'Проекты на контроле', [
    'description' => 'Активные проекты, по которым руководителю важно видеть текущий этап и сроки.',
    'users_groups' => '0,' . $manager_group_id,
    'in_dashboard' => 1,
    'in_dashboard_counter' => 1,
    'dashboard_sort_order' => 30,
    'dashboard_counter_sort_order' => 30,
    'menu_icon' => 'fa fa-briefcase',
    'displays_assigned_only' => 0,
]);
sync_report_filters($manager_projects_report, [
    ['fields_id' => $project_stage_id, 'values' => $project_active_choices],
]);

$manager_project_docs_report = ensure_common_report(21, 'Проекты с риском по документам', [
    'description' => 'Проекты, где документ еще не завершен или интеграция требует внимания.',
    'users_groups' => '0,' . $manager_group_id,
    'in_dashboard' => 1,
    'in_dashboard_counter' => 1,
    'dashboard_sort_order' => 35,
    'dashboard_counter_sort_order' => 35,
    'menu_icon' => 'fa fa-warning',
    'displays_assigned_only' => 0,
]);
sync_report_filters($manager_project_docs_report, [
    ['fields_id' => $project_doc_sync_status_id, 'values' => $project_doc_attention_choices],
]);

$manager_documents_report = ensure_common_report(25, 'Документы на согласовании', [
    'description' => 'Документы, которые находятся на согласовании, утверждении или ознакомлении.',
    'users_groups' => '0,' . $manager_group_id,
    'in_dashboard' => 1,
    'in_dashboard_counter' => 1,
    'dashboard_sort_order' => 40,
    'dashboard_counter_sort_order' => 40,
    'menu_icon' => 'fa fa-files-o',
    'displays_assigned_only' => 0,
]);
sync_report_filters($manager_documents_report, [
    ['fields_id' => $doc_status_id, 'values' => $doc_active_choices],
]);

$manager_mts_report = ensure_common_report(27, 'Заявки МТЗ в работе', [
    'description' => 'Заявки на обеспечение, которые требуют согласования или контроля закупки.',
    'users_groups' => '0,' . $manager_group_id,
    'in_dashboard' => 1,
    'in_dashboard_counter' => 1,
    'dashboard_sort_order' => 50,
    'dashboard_counter_sort_order' => 50,
    'menu_icon' => 'fa fa-cubes',
    'displays_assigned_only' => 0,
]);
sync_report_filters($manager_mts_report, [
    ['fields_id' => $mts_status_id, 'values' => $mts_active_choices],
]);

$office_documents_report = ensure_common_report(25, 'Документы канцелярии', [
    'description' => 'Документы, которые требуют регистрации, контроля завершения или передачи в архив.',
    'users_groups' => '0,' . $office_group_id,
    'in_dashboard' => 1,
    'in_dashboard_counter' => 1,
    'dashboard_sort_order' => 45,
    'dashboard_counter_sort_order' => 45,
    'menu_icon' => 'fa fa-archive',
    'displays_assigned_only' => 0,
]);
sync_report_filters($office_documents_report, [
    ['fields_id' => $doc_status_id, 'values' => array_filter([
        get_choice_id_by_name($doc_status_id, 'Подписан'),
        get_choice_id_by_name($doc_status_id, 'На ознакомлении'),
        get_choice_id_by_name($doc_status_id, 'На регистрации'),
        get_choice_id_by_name($doc_status_id, 'Зарегистрирован'),
    ])],
]);

// Role-based UX: keep daily forms focused while preserving the shared data model.
sync_fields_access(21, $employee_group_id, [
    $project_manager_note_id => 'view_inform',
]);
sync_fields_access(23, $requester_group_id, [
    $request_status_id => 'view_inform',
    $request_responsible_id => 'view_inform',
    $request_due_date_id => 'view_inform',
    $request_service_category_id => 'view_inform',
    $request_project_link_id => 'view_inform',
    $request_doc_link_id => 'view_inform',
    $request_nau_link_id => 'view_inform',
    $request_doc_sync_status_id => 'view_inform',
    $request_resolution_id => 'view_inform',
]);
sync_fields_access(25, $requester_group_id, [
    $doc_status_id => 'view_inform',
    $doc_reg_number_id => 'view_inform',
    $doc_version_id => 'view_inform',
    $doc_nau_link_id => 'view_inform',
]);
sync_fields_access(21, $office_group_id, [
    $project_description_id => 'hide',
    $project_team_id => 'hide',
    $project_manager_note_id => 'hide',
]);
sync_fields_access(22, $office_group_id, [
    $task_plan_hours_id => 'hide',
    $task_fact_hours_id => 'hide',
]);
sync_fields_access(23, $office_group_id, [
    $request_channel_id => 'hide',
    $request_service_category_id => 'hide',
    $request_resolution_id => 'hide',
]);
sync_fields_access(27, $office_group_id, [
    $mts_reason_id => 'hide',
]);

ensure_entities_menu_item('Мое рабочее место', [
    'icon' => 'fa-home',
    'icon_color' => '#1f4f86',
    'bg_color' => '#dbe8f7',
    'reports_list' => [
        'common' . $employee_tasks_report,
        'common' . $employee_requests_report,
    ],
    'sort_order' => 5,
]);
ensure_entities_menu_item('Операционная работа', [
    'icon' => 'fa-tasks',
    'icon_color' => '#1f4f86',
    'bg_color' => '#e8f1fb',
    'entities_list' => [23, 21, 22, 27],
    'sort_order' => 10,
]);
ensure_entities_menu_item('Документы', [
    'icon' => 'fa-folder-open-o',
    'icon_color' => '#8a4b08',
    'bg_color' => '#fff1dd',
    'entities_list' => [25, 26],
    'sort_order' => 20,
]);
ensure_entities_menu_item('Контроль руководителя', [
    'icon' => 'fa-line-chart',
    'icon_color' => '#204b76',
    'bg_color' => '#d9e8f6',
    'reports_list' => [
        'common' . $manager_projects_report,
        'common' . $manager_project_docs_report,
        'common' . $requests_doc_attention_report,
        'common' . $manager_documents_report,
        'common' . $manager_mts_report,
    ],
    'sort_order' => 30,
]);
ensure_entities_menu_item('Канцелярия', [
    'icon' => 'fa-archive',
    'icon_color' => '#8a4b08',
    'bg_color' => '#f8e8d0',
    'reports_list' => [
        'common' . $office_documents_report,
    ],
    'sort_order' => 40,
]);

console_log('Process model provisioned successfully.');
