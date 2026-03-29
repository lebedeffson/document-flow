<?php

define('IS_CRON', true);

chdir(dirname(__DIR__));
require 'includes/application_core.php';
require_once 'includes/classes/model/configuration.php';

function console_log($message)
{
    echo $message . PHP_EOL;
}

function fetch_row_by_sql($sql)
{
    $query = db_query($sql);
    return db_fetch_array($query);
}

function get_field_id_by_name($entity_id, $name)
{
    $row = fetch_row_by_sql(
        "select id from app_fields where entities_id='" . (int) $entity_id . "' and name='" . db_input($name) . "' limit 1"
    );

    return $row ? (int) $row['id'] : 0;
}

function get_choice_id_by_name($field_id, $name)
{
    if (!(int) $field_id)
    {
        return 0;
    }

    $row = fetch_row_by_sql(
        "select id from app_fields_choices where fields_id='" . (int) $field_id . "' and name='" . db_input($name) . "' limit 1"
    );

    return $row ? (int) $row['id'] : 0;
}

function optional_field_payload($field_id, $value)
{
    if ((int) $field_id <= 0 || $value === '' || $value === null || (int) $value <= 0)
    {
        return [];
    }

    return [
        'field_' . (int) $field_id => $value,
    ];
}

function env_truthy($value)
{
    $value = strtolower(trim((string) $value));
    return in_array($value, ['1', 'true', 'yes', 'on'], true);
}

function normalize_workspace_wave1_module($choice_name)
{
    $choice_name = trim((string) $choice_name);

    if (!strlen($choice_name))
    {
        return '';
    }

    if (strcasecmp($choice_name, 'Community') !== 0)
    {
        return $choice_name;
    }

    return env_truthy(getenv('DOCFLOW_WORKSPACE_WAVE1_ENABLE_COMMUNITY'))
        ? 'Community'
        : 'Calendar';
}

function optional_choice_payload_by_name($entity_id, $field_name, $choice_name)
{
    if (trim((string) $field_name) === 'Модуль Workspace')
    {
        $choice_name = normalize_workspace_wave1_module($choice_name);
    }

    $field_id = get_field_id_by_name($entity_id, $field_name);
    $choice_id = get_choice_id_by_name($field_id, $choice_name);

    return optional_field_payload($field_id, $choice_id);
}

function demo_timestamp($date)
{
    $timestamp = strtotime($date . ' 10:00:00');
    return $timestamp ? $timestamp : time();
}

function set_configuration_value($key, $value)
{
    configuration::set($key, $value);
    console_log("Configured {$key}");
}

function rename_field_if_exists($field_id, $name)
{
    $field = db_find('app_fields', $field_id);
    if($field)
    {
        db_perform('app_fields', ['name' => $name], 'update', "id='" . db_input($field_id) . "'");
        console_log("Updated field #{$field_id} name");
    }
}

function update_ecosystem_links($entity_id, $item_id)
{
    $docspace_field_id = platform_field_id_by_name($entity_id, 'Комната DocSpace', 'fieldtype_input_url');
    $workspace_field_id = platform_field_id_by_name($entity_id, 'Сервис Workspace', 'fieldtype_input_url');
    $sql_data = [];

    if($docspace_field_id > 0)
    {
        $sql_data['field_' . $docspace_field_id] = platform_service_enabled('docspace')
            ? platform_ecosystem_url('docspace', $entity_id, $item_id, true)
            : '';
    }

    if($workspace_field_id > 0)
    {
        $sql_data['field_' . $workspace_field_id] = platform_service_enabled('workspace')
            ? platform_ecosystem_url('workspace', $entity_id, $item_id, true)
            : '';
    }

    if(count($sql_data))
    {
        $sql_data['date_updated'] = time();
        db_perform('app_entity_' . (int) $entity_id, $sql_data, 'update', "id='" . db_input($item_id) . "'");
        console_log("Updated office ecosystem links for entity {$entity_id} item #{$item_id}");
    }
}

function apply_choice_value_to_item($entity_id, $item_id, $field_name, $choice_name)
{
    $entity_id = (int) $entity_id;
    $item_id = (int) $item_id;

    if (trim((string) $field_name) === 'Модуль Workspace')
    {
        $choice_name = normalize_workspace_wave1_module($choice_name);
    }

    $field_id = get_field_id_by_name($entity_id, $field_name);
    $choice_id = get_choice_id_by_name($field_id, $choice_name);

    if($entity_id <= 0 || $item_id <= 0 || $field_id <= 0 || $choice_id <= 0)
    {
        return;
    }

    db_perform(
        'app_entity_' . $entity_id,
        [
            'field_' . $field_id => $choice_id,
            'date_updated' => time(),
        ],
        'update',
        "id='" . db_input($item_id) . "'"
    );
}

function apply_ecosystem_model($entity_id, $item_id, $docspace_room = '', $workspace_module = '')
{
    if(strlen(trim((string) $docspace_room)))
    {
        apply_choice_value_to_item($entity_id, $item_id, 'Сценарий DocSpace', $docspace_room);
    }

    if(strlen(trim((string) $workspace_module)))
    {
        apply_choice_value_to_item($entity_id, $item_id, 'Модуль Workspace', $workspace_module);
    }
}

function find_item_by_titles($entity_id, $field_id, array $titles)
{
    $titles = array_values(array_unique(array_filter(array_map('trim', $titles))));
    if (!count($titles))
    {
        return false;
    }

    $titles_sql = [];
    foreach ($titles as $title)
    {
        $titles_sql[] = "'" . db_input($title) . "'";
    }

    return fetch_row_by_sql(
        "select * from app_entity_" . (int) $entity_id .
        " where field_" . (int) $field_id . " in (" . implode(',', $titles_sql) . ") order by id limit 1"
    );
}

function ensure_demo_item($entity_id, $title_field_id, $target_title, array $data, array $legacy_titles = [])
{
    $item = find_item_by_titles($entity_id, $title_field_id, array_merge([$target_title], $legacy_titles));
    $sql_data = array_merge([
        'parent_id' => 0,
        'parent_item_id' => 0,
        'linked_id' => 0,
        'sort_order' => 0,
        'created_by' => 1,
        'date_added' => time(),
        'date_updated' => time(),
    ], $data);

    $sql_data['field_' . (int) $title_field_id] = $target_title;

    if (!$item)
    {
        db_perform('app_entity_' . (int) $entity_id, $sql_data);
        $item_id = db_insert_id();
        console_log("Created baseline item {$target_title} (#{$item_id}) in entity {$entity_id}");
        return (int) $item_id;
    }

    $item_id = (int) $item['id'];
    unset($sql_data['date_added']);
    db_perform('app_entity_' . (int) $entity_id, $sql_data, 'update', "id='" . db_input($item_id) . "'");
    console_log("Updated baseline item {$target_title} (#{$item_id}) in entity {$entity_id}");
    return $item_id;
}

set_configuration_value('CFG_APP_NAME', 'Единая платформа документооборота');
set_configuration_value('CFG_APP_SHORT_NAME', 'Документооборот');
set_configuration_value('CFG_LOGIN_PAGE_HEADING', 'Рабочий контур платформы документооборота');
set_configuration_value(
    'CFG_LOGIN_PAGE_CONTENT',
    'Проекты, заявки, совместная работа над документами, маршруты согласования и архив в едином рабочем веб-контуре.'
);

rename_field_if_exists(282, 'Совместное редактирование');

$naudoc_public_url = getenv('NAUDOC_PUBLIC_URL') ?: 'https://localhost:18443/docs';

$doc_route_field_id = get_field_id_by_name(25, 'Маршрут документа');
$route_internal_order_id = get_choice_id_by_name($doc_route_field_id, 'Внутренний приказ / распоряжение');
$route_outgoing_approval_id = get_choice_id_by_name($doc_route_field_id, 'Исходящее письмо / согласование');
$route_contract_id = get_choice_id_by_name($doc_route_field_id, 'Договор / закупка / МТЗ');
$route_clinical_document_id = get_choice_id_by_name($doc_route_field_id, 'Медицинская документация отделения');
$route_patient_route_id = get_choice_id_by_name($doc_route_field_id, 'Пациент / направление / выписка');

$project_primary_id = ensure_demo_item(
    21,
    158,
    'Внедрение единой платформы документооборота',
    array_merge([
        'date_added' => demo_timestamp('2026-03-20'),
        'date_updated' => time(),
        'field_156' => 461,
        'field_157' => 465,
        'field_159' => demo_timestamp('2026-03-20'),
        'field_160' => '<p>Пилотный проект по запуску единого контура: рабочие процессы в Rukovoditel, официальный документный контур в NauDoc, совместное редактирование в ONLYOFFICE.</p>',
        'field_161' => '2,3,5',
        'field_225' => '1',
        'field_226' => '1',
        'field_227' => 470,
        'field_228' => demo_timestamp('2026-04-15'),
        'field_229' => 55,
        'field_230' => $naudoc_public_url,
        'field_231' => 'Контрольный кейс для показа заказчику: проект, документы, согласование и публикация финальной версии.',
        'field_280' => 528,
    ], optional_choice_payload_by_name(21, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(21, 'Модуль Workspace', 'Community')),
    ['Тестовый проект цифрового документооборота']
);

$request_primary_id = ensure_demo_item(
    23,
    184,
    'Подготовка маршрута согласования приказа о пилоте',
    array_merge([
        'date_added' => demo_timestamp('2026-03-21'),
        'date_updated' => time(),
        'field_182' => 387,
        'field_183' => 385,
        'field_185' => '<p>Нужно оформить карточку документа, настроить маршрут согласования и подготовить публикацию итоговой версии в NauDoc.</p>',
        'field_186' => 402,
        'field_235' => 404,
        'field_236' => '1',
        'field_237' => demo_timestamp('2026-03-28'),
        'field_238' => 410,
        'field_239' => (string) $project_primary_id,
        'field_241' => $naudoc_public_url,
        'field_276' => 394,
        'field_277' => 'Карточка документа создана, маршрут согласования завершен, ссылка на итоговый документ возвращена в рабочий контур.',
        'field_281' => 551,
    ], optional_choice_payload_by_name(23, 'Сценарий DocSpace', 'Form filling room'),
       optional_choice_payload_by_name(23, 'Модуль Workspace', 'Calendar')),
    ['Тестовая заявка на подготовку документа']
);

$doc_request_id = ensure_demo_item(
    25,
    242,
    'Служебная записка о запуске пилотного контура',
    array_merge([
        'date_added' => demo_timestamp('2026-03-21'),
        'date_updated' => time(),
        'field_243' => 419,
        'field_244' => 427,
        'field_245' => 'СЗ-2026-001',
        'field_246' => demo_timestamp('2026-03-21'),
        'field_247' => '1',
        'field_248' => demo_timestamp('2026-12-31'),
        'field_249' => '1.0',
        'field_250' => $naudoc_public_url,
        'field_251' => '',
        'field_252' => (string) $request_primary_id,
        'field_253' => '<p>Документ оформлен по заявке на запуск пилотного контура и используется как основной демонстрационный кейс канцелярского маршрута.</p>',
    ], optional_field_payload($doc_route_field_id, $route_outgoing_approval_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Calendar')),
    ['Тестовая заявка на подготовку документа']
);

$doc_project_id = ensure_demo_item(
    25,
    242,
    'Документ проекта: Внедрение единой платформы документооборота',
    array_merge([
        'date_added' => demo_timestamp('2026-03-22'),
        'date_updated' => time(),
        'field_243' => 421,
        'field_244' => 427,
        'field_245' => 'РГ-2026-004',
        'field_246' => demo_timestamp('2026-03-22'),
        'field_247' => '1',
        'field_248' => demo_timestamp('2027-03-22'),
        'field_249' => '1.1',
        'field_250' => $naudoc_public_url,
        'field_251' => (string) $project_primary_id,
        'field_252' => '',
        'field_253' => '<p>Карточка проектного документа используется для показа связки проект -> документ -> NauDoc и совместной работы над черновиком.</p>',
    ], optional_field_payload($doc_route_field_id, $route_outgoing_approval_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Community')),
    ['Документ проекта: Тестовый проект цифрового документооборота']
);

$doc_simple_test_id = ensure_demo_item(
    25,
    242,
    'Рабочий документ отделения: Иван Иванов',
    array_merge([
        'created_by' => 3,
        'date_added' => demo_timestamp('2026-03-24'),
        'date_updated' => time(),
        'field_243' => 419,
        'field_244' => 427,
        'field_245' => 'РД-2026-014',
        'field_246' => demo_timestamp('2026-03-24'),
        'field_247' => '1',
        'field_248' => demo_timestamp('2026-12-31'),
        'field_249' => '1.0',
        'field_250' => $naudoc_public_url,
        'field_251' => '',
        'field_252' => '',
        'field_253' => '<p>Простой рабочий документ для контрольного пользовательского сценария: открыть карточку, найти документ, запустить ONLYOFFICE, внести правку и проверить публикацию в NauDoc.</p><p>Исполнитель: Иван Иванов.</p>',
    ], optional_field_payload($doc_route_field_id, $route_outgoing_approval_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Calendar')),
    ['Тестовый документ Иван Иванов', 'Тестовый документ: Иван Иванов']
);

$doc_patient_route_id = ensure_demo_item(
    25,
    242,
    'Направление пациента: Иван Иванов',
    array_merge([
        'created_by' => 3,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_243' => 419,
        'field_244' => 427,
        'field_245' => 'НП-2026-021',
        'field_246' => demo_timestamp('2026-03-25'),
        'field_247' => '1',
        'field_248' => demo_timestamp('2026-12-31'),
        'field_249' => '1.0',
        'field_250' => $naudoc_public_url,
        'field_251' => '',
        'field_252' => '',
        'field_253' => '<p>Простой hospital-кейс: направление пациента оформляется в рабочем контуре, редактируется в ONLYOFFICE и получает официальный объект в NauDoc.</p><p>Пациент: Иван Иванов.</p>',
    ], optional_field_payload($doc_route_field_id, $route_patient_route_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Form filling room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Calendar')),
    ['Направление пациента Иван Иванов']
);

$doc_clinical_note_id = ensure_demo_item(
    25,
    242,
    'Медицинская запись отделения: Иван Иванов',
    array_merge([
        'created_by' => 7,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_243' => 421,
        'field_244' => 427,
        'field_245' => 'МЗ-2026-009',
        'field_246' => demo_timestamp('2026-03-25'),
        'field_247' => '1',
        'field_248' => demo_timestamp('2026-12-31'),
        'field_249' => '1.0',
        'field_250' => $naudoc_public_url,
        'field_251' => '',
        'field_252' => '',
        'field_253' => '<p>Простой клинический документ для теста hospital-маршрута: подготовка внутренней медицинской записи отделения, совместная правка и публикация в официальный контур.</p><p>Ответственный сотрудник: Иван Иванов.</p>',
    ], optional_field_payload($doc_route_field_id, $route_clinical_document_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Calendar')),
    ['Медицинская запись Иван Иванов']
);

$doc_internal_order_simple_id = ensure_demo_item(
    25,
    242,
    'Внутренний приказ отделения: график обходов',
    array_merge([
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-26'),
        'date_updated' => time(),
        'field_243' => 421,
        'field_244' => 427,
        'field_245' => 'ПР-2026-018',
        'field_246' => demo_timestamp('2026-03-26'),
        'field_247' => '1',
        'field_248' => demo_timestamp('2026-12-31'),
        'field_249' => '1.0',
        'field_250' => $naudoc_public_url,
        'field_251' => '',
        'field_252' => '',
        'field_253' => '<p>Внутренний приказ подразделения для теста сценария согласования и ознакомления персонала. Используется как простой понятный кейс для заведующего и сотрудников.</p>',
    ], optional_field_payload($doc_route_field_id, $route_internal_order_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Calendar')),
    ['Внутренний приказ отделения график обходов']
);

$doc_duty_schedule_id = ensure_demo_item(
    25,
    242,
    'Таблица дежурств отделения: апрель 2026',
    array_merge([
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-27'),
        'date_updated' => time(),
        'field_243' => 421,
        'field_244' => 427,
        'field_245' => 'ТА-2026-022',
        'field_246' => demo_timestamp('2026-03-27'),
        'field_247' => '1',
        'field_248' => demo_timestamp('2026-12-31'),
        'field_249' => '1.0',
        'field_250' => $naudoc_public_url,
        'field_251' => '',
        'field_252' => '',
        'field_253' => '<p>Контрольная таблица отделения для проверки ONLYOFFICE Spreadsheet Editor: открыть карточку, запустить таблицу, изменить значение, сохранить и убедиться, что совместная работа не ломается.</p><p>Сценарий удобен для заведующего и старшей медсестры.</p>',
    ], optional_field_payload($doc_route_field_id, $route_internal_order_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Calendar')),
    ['Таблица дежурств отделения', 'График дежурств отделения']
);

db_perform('app_entity_21', ['field_279' => (string) $doc_project_id], 'update', "id='" . db_input($project_primary_id) . "'");
db_perform('app_entity_23', ['field_240' => (string) $doc_request_id], 'update', "id='" . db_input($request_primary_id) . "'");

foreach([
    [21, $project_primary_id],
    [23, $request_primary_id],
    [25, $doc_request_id],
    [25, $doc_project_id],
    [25, $doc_simple_test_id],
    [25, $doc_patient_route_id],
    [25, $doc_clinical_note_id],
    [25, $doc_internal_order_simple_id],
    [25, $doc_duty_schedule_id],
] as $ecosystem_item)
{
    update_ecosystem_links($ecosystem_item[0], $ecosystem_item[1]);
}

$project_secondary_id = ensure_demo_item(
    21,
    158,
    'Подготовка регламента согласования внутренних документов',
    array_merge([
        'date_added' => demo_timestamp('2026-03-23'),
        'date_updated' => time(),
        'field_156' => 462,
        'field_157' => 466,
        'field_159' => demo_timestamp('2026-03-23'),
        'field_160' => '<p>Второй демонстрационный кейс: проект в стадии согласования, по нему еще нет опубликованной финальной версии в NauDoc.</p>',
        'field_161' => '2,3',
        'field_225' => '2',
        'field_226' => '2',
        'field_227' => 471,
        'field_228' => demo_timestamp('2026-04-20'),
        'field_229' => 25,
        'field_230' => '',
        'field_231' => 'Кейс нужен для показа статусов: проект в работе, документ ожидает публикации.',
        'field_280' => 523,
    ], optional_choice_payload_by_name(21, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(21, 'Модуль Workspace', 'Community'))
);

$project_archive_id = ensure_demo_item(
    21,
    158,
    'Архивирование завершенных регламентов',
    array_merge([
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-02-10'),
        'date_updated' => time(),
        'field_156' => 463,
        'field_157' => 468,
        'field_159' => demo_timestamp('2026-02-10'),
        'field_160' => '<p>Завершенный демонстрационный кейс для показа жизненного цикла проекта: рабочая стадия, публикация документа, регистрация и перевод материалов в архив.</p>',
        'field_161' => '2,5',
        'field_225' => '2',
        'field_226' => '2',
        'field_227' => 470,
        'field_228' => demo_timestamp('2026-03-15'),
        'field_229' => 100,
        'field_230' => $naudoc_public_url,
        'field_231' => 'Проект завершен. Документ зарегистрирован и материалы переданы в архив.',
        'field_280' => 635,
    ], optional_choice_payload_by_name(21, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(21, 'Модуль Workspace', 'Community'))
);

$request_secondary_id = ensure_demo_item(
    23,
    184,
    'Подключить шаблон служебной записки для отделений',
    array_merge([
        'date_added' => demo_timestamp('2026-03-24'),
        'date_updated' => time(),
        'field_182' => 389,
        'field_183' => 383,
        'field_185' => '<p>Требуется подготовить шаблон служебной записки, дать доступ отделениям и вывести документ в общий контур согласования.</p>',
        'field_186' => 399,
        'field_235' => 406,
        'field_236' => '3',
        'field_237' => demo_timestamp('2026-03-31'),
        'field_238' => 411,
        'field_239' => (string) $project_secondary_id,
        'field_241' => '',
        'field_276' => 395,
        'field_277' => '',
        'field_281' => 546,
    ], optional_choice_payload_by_name(23, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(23, 'Модуль Workspace', 'Community'))
);

ensure_demo_item(
    23,
    184,
    'Закупка принтера для регистратора канцелярии',
    [
        'created_by' => 5,
        'date_added' => demo_timestamp('2026-03-23'),
        'date_updated' => time(),
        'field_182' => '5',
        'field_183' => 384,
        'field_185' => '<p>Хозяйственная заявка на закупку принтера для рабочего места регистратора. Нужна как наглядный пример не-документного сервисного запроса.</p>',
        'field_186' => 399,
        'field_235' => 405,
        'field_236' => '5',
        'field_237' => demo_timestamp('2026-04-04'),
        'field_238' => 412,
        'field_239' => '',
        'field_241' => '',
        'field_276' => 395,
        'field_277' => 'Подготовлено коммерческое предложение, ожидается закупка по линии обеспечения.',
        'field_281' => 546,
    ],
    ['покупка принтера']
);

$request_contract_id = ensure_demo_item(
    23,
    184,
    'Оформить карточку входящего договора на сопровождение',
    array_merge([
        'created_by' => 5,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_182' => '5',
        'field_183' => 385,
        'field_185' => '<p>Кейс канцелярии: нужно зарегистрировать входящий договор, связать его с карточкой документа и вернуть ссылку на официальный контур.</p>',
        'field_186' => 400,
        'field_235' => 406,
        'field_236' => '5',
        'field_237' => demo_timestamp('2026-03-30'),
        'field_238' => 410,
        'field_239' => '',
        'field_241' => $naudoc_public_url,
        'field_276' => 395,
        'field_277' => 'Карточка договора открыта, регистрация проходит через канцелярский контур.',
        'field_281' => 650,
    ], optional_choice_payload_by_name(23, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(23, 'Модуль Workspace', 'Calendar'))
);

$request_access_id = ensure_demo_item(
    23,
    184,
    'Открыть доступ к шаблонам служебной записки',
    array_merge([
        'created_by' => 4,
        'date_added' => demo_timestamp('2026-03-26'),
        'date_updated' => time(),
        'field_182' => '4',
        'field_183' => 383,
        'field_185' => '<p>Заявка от сотрудника подразделения: требуется открыть доступ к шаблонам служебных записок и инструкциям по оформлению документов.</p>',
        'field_186' => 401,
        'field_235' => 407,
        'field_236' => '3',
        'field_237' => demo_timestamp('2026-04-02'),
        'field_238' => 411,
        'field_239' => (string) $project_secondary_id,
        'field_241' => '',
        'field_276' => 394,
        'field_277' => 'Ожидается уточнение по отделениям и перечню шаблонов.',
        'field_281' => 546,
    ], optional_choice_payload_by_name(23, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(23, 'Модуль Workspace', 'Community'))
);

ensure_demo_item(
    24,
    191,
    'Согласование шаблона приказа по пилотному запуску',
    [
        'date_added' => demo_timestamp('2026-03-24'),
        'date_updated' => time(),
        'field_192' => '<p>Обсуждение используется как демонстрация внутренней координации: комментарии руководителя, канцелярии и исполнителя по одному документу.</p>',
        'field_193' => 751,
    ]
);

ensure_demo_item(
    24,
    191,
    'Замечания к регламенту согласования внутренних документов',
    [
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_192' => '<p>Обсуждение для показа совместной проработки документа: руководитель фиксирует замечания, канцелярия уточняет регистрацию, исполнитель вносит правки.</p>',
        'field_193' => 750,
    ]
);

ensure_demo_item(
    24,
    191,
    'Переход сотрудников на совместное редактирование документов',
    [
        'created_by' => 3,
        'date_added' => demo_timestamp('2026-03-26'),
        'date_updated' => time(),
        'field_192' => '<p>Обсуждение сценария работы в ONLYOFFICE: кто редактирует черновик, как передавать итоговую версию в NauDoc и кто контролирует публикацию.</p>',
        'field_193' => 751,
    ]
);

$doc_approval_id = ensure_demo_item(
    25,
    242,
    'Приказ о запуске пилотного контура',
    array_merge([
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_243' => 417,
        'field_244' => 425,
        'field_245' => 'ПР-2026-015',
        'field_246' => demo_timestamp('2026-03-25'),
        'field_247' => '1',
        'field_248' => demo_timestamp('2026-12-31'),
        'field_249' => '0.9',
        'field_250' => '',
        'field_251' => (string) $project_primary_id,
        'field_252' => '',
        'field_253' => '<p>Пример документа в статусе согласования. Используется для демонстрации маршрута согласования и отчета по документам, ожидающим решения.</p>',
    ], optional_field_payload($doc_route_field_id, $route_internal_order_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Calendar'))
);

$doc_contract_id = ensure_demo_item(
    25,
    242,
    'Входящий договор на сопровождение платформы',
    array_merge([
        'created_by' => 5,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_243' => 418,
        'field_244' => 658,
        'field_245' => 'ДГ-2026-021',
        'field_246' => demo_timestamp('2026-03-25'),
        'field_247' => '5',
        'field_248' => demo_timestamp('2027-03-25'),
        'field_249' => '1.0',
        'field_250' => $naudoc_public_url,
        'field_251' => '',
        'field_252' => (string) $request_contract_id,
        'field_253' => '<p>Пример зарегистрированного документа канцелярии. Нужен для показа регистрационного контура и работы со входящими договорами.</p>',
    ], optional_field_payload($doc_route_field_id, $route_contract_id),
       optional_choice_payload_by_name(25, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(25, 'Модуль Workspace', 'Community'))
);

db_perform('app_entity_23', ['field_240' => (string) $doc_contract_id], 'update', "id='" . db_input($request_contract_id) . "'");

foreach([
    [21, $project_secondary_id],
    [21, $project_archive_id],
    [23, $request_secondary_id],
    [23, $request_contract_id],
    [23, $request_access_id],
    [25, $doc_approval_id],
    [25, $doc_contract_id],
] as $ecosystem_item)
{
    update_ecosystem_links($ecosystem_item[0], $ecosystem_item[1]);
}

ensure_demo_item(
    22,
    168,
    'Подготовить текст приказа о запуске пилота',
    [
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-24'),
        'date_updated' => time(),
        'field_167' => 800,
        'field_169' => 803,
        'field_170' => 809,
        'field_171' => '1,2,3',
        'field_172' => '<p>Подготовить финальный текст приказа, сверить состав согласующих и приложить версию для запуска маршрута.</p>',
        'field_173' => '6',
        'field_174' => '2',
        'field_175' => demo_timestamp('2026-03-24'),
        'field_176' => demo_timestamp('2026-03-28'),
        'field_232' => '2',
        'field_233' => (string) $doc_approval_id,
        'field_234' => '',
    ]
);

ensure_demo_item(
    22,
    168,
    'Проверить регламент согласования внутренних документов',
    [
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_167' => 799,
        'field_169' => 804,
        'field_170' => 810,
        'field_171' => '1,2,5',
        'field_172' => '<p>Нужно проверить последовательность согласования, сроки и роли участников перед публикацией регламента.</p>',
        'field_173' => '4',
        'field_174' => '1',
        'field_175' => demo_timestamp('2026-03-25'),
        'field_176' => demo_timestamp('2026-03-30'),
        'field_232' => '2',
        'field_233' => (string) $doc_project_id,
        'field_234' => '',
    ]
);

ensure_demo_item(
    22,
    168,
    'Собрать замечания канцелярии к входящему договору',
    [
        'created_by' => 5,
        'date_added' => demo_timestamp('2026-03-26'),
        'date_updated' => time(),
        'field_167' => 801,
        'field_169' => 805,
        'field_170' => 810,
        'field_171' => '4,5',
        'field_172' => '<p>Канцелярия готовит замечания к карточке договора и проверяет, все ли реквизиты отражены перед передачей документа в работу.</p>',
        'field_173' => '3',
        'field_174' => '2',
        'field_175' => demo_timestamp('2026-03-26'),
        'field_176' => demo_timestamp('2026-03-29'),
        'field_232' => '5',
        'field_233' => (string) $doc_contract_id,
        'field_234' => $naudoc_public_url,
    ]
);

ensure_demo_item(
    22,
    168,
    'Подготовить комплект закупки МФУ для канцелярии',
    [
        'created_by' => 1,
        'date_added' => demo_timestamp('2026-03-22'),
        'date_updated' => time(),
        'field_167' => 798,
        'field_169' => 806,
        'field_170' => 809,
        'field_171' => '3',
        'field_172' => '<p>Комплект документов для закупки сформирован и передан дальше. Задача закрыта и используется как пример завершенного поручения.</p>',
        'field_173' => '5',
        'field_174' => '5',
        'field_175' => demo_timestamp('2026-03-22'),
        'field_176' => demo_timestamp('2026-03-24'),
        'field_232' => '1',
        'field_233' => (string) $doc_request_id,
        'field_234' => $naudoc_public_url,
    ]
);

$mts_primary_id = ensure_demo_item(
    27,
    265,
    'Оснащение канцелярии МФУ и расходными материалами',
    array_merge([
        'date_added' => demo_timestamp('2026-03-22'),
        'date_updated' => time(),
        'field_266' => 761,
        'field_267' => '2',
        'field_268' => 774,
        'field_269' => 779,
        'field_270' => '5',
        'field_271' => demo_timestamp('2026-04-05'),
        'field_272' => (string) $project_primary_id,
        'field_273' => $naudoc_public_url,
        'field_274' => '<p>Контрольный кейс по обеспечению: заявка связана с проектом внедрения и показывает отдельный процесс МТЗ.</p>',
        'field_278' => 767,
    ], optional_choice_payload_by_name(27, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(27, 'Модуль Workspace', 'Calendar'))
);

$mts_scanner_id = ensure_demo_item(
    27,
    265,
    'Сканер для оцифровки входящих документов',
    array_merge([
        'created_by' => 5,
        'date_added' => demo_timestamp('2026-03-23'),
        'date_updated' => time(),
        'field_266' => 762,
        'field_267' => '1',
        'field_268' => 775,
        'field_269' => 780,
        'field_270' => '5',
        'field_271' => demo_timestamp('2026-04-08'),
        'field_272' => (string) $project_secondary_id,
        'field_273' => $naudoc_public_url,
        'field_274' => '<p>Пример заказа оборудования: позиция согласована и уже заказана, чтобы показывать разные статусы обеспечения.</p>',
        'field_278' => '5',
    ], optional_choice_payload_by_name(27, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(27, 'Модуль Workspace', 'Calendar'))
);

$mts_license_id = ensure_demo_item(
    27,
    265,
    'Лицензии ONLYOFFICE для совместного редактирования',
    array_merge([
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-24'),
        'date_updated' => time(),
        'field_266' => 765,
        'field_267' => '30',
        'field_268' => 774,
        'field_269' => 778,
        'field_270' => '2',
        'field_271' => demo_timestamp('2026-04-12'),
        'field_272' => (string) $project_primary_id,
        'field_273' => $naudoc_public_url,
        'field_274' => '<p>Пример заявки на программное обеспечение. Используется для показа сценария закупки лицензий и связи с проектом цифровизации.</p>',
        'field_278' => '2',
    ], optional_choice_payload_by_name(27, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(27, 'Модуль Workspace', 'Calendar'))
);

$doc_base_template_id = ensure_demo_item(
    26,
    255,
    'Шаблон служебной записки для отделений',
    array_merge([
        'created_by' => 5,
        'date_added' => demo_timestamp('2026-03-24'),
        'date_updated' => time(),
        'field_256' => 754,
        'field_257' => 758,
        'field_258' => '2.0',
        'field_259' => '5',
        'field_260' => demo_timestamp('2026-10-01'),
        'field_261' => $naudoc_public_url,
        'field_262' => 'шаблон,отделение,служебная записка',
        'field_263' => '<p>Готовый шаблон, который врачи и сотрудники используют для подготовки служебных записок внутри платформы.</p>',
    ], optional_choice_payload_by_name(26, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(26, 'Модуль Workspace', 'Community'))
);

$doc_base_simple_template_id = ensure_demo_item(
    26,
    255,
    'Простой шаблон документа: Иван Иванов',
    array_merge([
        'created_by' => 3,
        'date_added' => demo_timestamp('2026-03-24'),
        'date_updated' => time(),
        'field_256' => 754,
        'field_257' => 758,
        'field_258' => '1.0',
        'field_259' => '3',
        'field_260' => demo_timestamp('2026-12-31'),
        'field_261' => $naudoc_public_url,
        'field_262' => 'тест,иван иванов,простой шаблон',
        'field_263' => '<p>Обычный рабочий шаблон для быстрой подготовки документа. Можно открыть, скопировать как основу, заполнить данными пациента или подразделения и передать в согласование.</p><p>Пример исполнителя: Иван Иванов.</p>',
    ], optional_choice_payload_by_name(26, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(26, 'Модуль Workspace', 'Community')),
    ['Простой тестовый шаблон Иван Иванов']
);

$doc_base_patient_template_id = ensure_demo_item(
    26,
    255,
    'Шаблон направления пациента',
    array_merge([
        'created_by' => 3,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_256' => 754,
        'field_257' => 758,
        'field_258' => '1.0',
        'field_259' => '3',
        'field_260' => demo_timestamp('2026-12-31'),
        'field_261' => $naudoc_public_url,
        'field_262' => 'пациент,направление,врач',
        'field_263' => '<p>Простой шаблон направления пациента для hospital pilot. Используется как основа для теста сценария врача: заполнить, согласовать и передать в официальный контур.</p>',
    ], optional_choice_payload_by_name(26, 'Сценарий DocSpace', 'Form filling room'),
       optional_choice_payload_by_name(26, 'Модуль Workspace', 'Community')),
    ['Шаблон направления пациента Иван Иванов']
);

$doc_base_clinical_template_id = ensure_demo_item(
    26,
    255,
    'Шаблон медицинской записи отделения',
    array_merge([
        'created_by' => 7,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_256' => 754,
        'field_257' => 758,
        'field_258' => '1.0',
        'field_259' => '3',
        'field_260' => demo_timestamp('2026-12-31'),
        'field_261' => $naudoc_public_url,
        'field_262' => 'медицинская запись,отделение,врач',
        'field_263' => '<p>Шаблон внутренней медицинской записи отделения. Подходит для быстрого теста ввода данных, редактирования и хранения медицинской служебной документации.</p>',
    ], optional_choice_payload_by_name(26, 'Сценарий DocSpace', 'Collaboration room'),
       optional_choice_payload_by_name(26, 'Модуль Workspace', 'Community')),
    ['Шаблон медицинской записи']
);

$doc_base_internal_order_template_id = ensure_demo_item(
    26,
    255,
    'Шаблон внутреннего приказа отделения',
    array_merge([
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-26'),
        'date_updated' => time(),
        'field_256' => 756,
        'field_257' => 759,
        'field_258' => '1.0',
        'field_259' => '2',
        'field_260' => demo_timestamp('2026-12-31'),
        'field_261' => $naudoc_public_url,
        'field_262' => 'приказ,отделение,руководитель',
        'field_263' => '<p>Шаблон внутреннего приказа подразделения. Используется для теста маршрута руководителя: подготовить документ, утвердить и довести до сотрудников.</p>',
    ], optional_choice_payload_by_name(26, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(26, 'Модуль Workspace', 'Community')),
    ['Шаблон приказа отделения']
);

$doc_base_manager_guide_id = ensure_demo_item(
    26,
    255,
    'Инструкция для руководителя по согласованию документов',
    array_merge([
        'created_by' => 2,
        'date_added' => demo_timestamp('2026-03-24'),
        'date_updated' => time(),
        'field_256' => 755,
        'field_257' => 758,
        'field_258' => '1.3',
        'field_259' => '2',
        'field_260' => demo_timestamp('2026-11-15'),
        'field_261' => $naudoc_public_url,
        'field_262' => 'руководитель,согласование,инструкция',
        'field_263' => '<p>Краткая инструкция для руководителей: как открыть документ, согласовать версию, оставить замечания и контролировать публикацию.</p>',
    ], optional_choice_payload_by_name(26, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(26, 'Модуль Workspace', 'Community'))
);

$doc_base_matrix_id = ensure_demo_item(
    26,
    255,
    'Матрица ролей и маршрутов документов',
    array_merge([
        'created_by' => 1,
        'date_added' => demo_timestamp('2026-03-25'),
        'date_updated' => time(),
        'field_256' => 756,
        'field_257' => 759,
        'field_258' => '0.8',
        'field_259' => '1',
        'field_260' => demo_timestamp('2026-08-15'),
        'field_261' => $naudoc_public_url,
        'field_262' => 'роли,маршруты,документооборот',
        'field_263' => '<p>Рабочий методический материал с ролями, маршрутами согласования и зонами ответственности по документам.</p>',
    ], optional_choice_payload_by_name(26, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(26, 'Модуль Workspace', 'Community'))
);

$doc_base_regulation_id = ensure_demo_item(
    26,
    255,
    'Регламент совместной работы с документами',
    array_merge([
        'date_added' => demo_timestamp('2026-03-22'),
        'date_updated' => time(),
        'field_256' => 755,
        'field_257' => 758,
        'field_258' => '1.1',
        'field_259' => '5',
        'field_260' => demo_timestamp('2026-09-01'),
        'field_261' => $naudoc_public_url,
        'field_262' => '',
        'field_263' => '<p>Нормативный материал для пользователей платформы: сценарий подготовки документа, согласование, публикация и архив.</p>',
    ], optional_choice_payload_by_name(26, 'Сценарий DocSpace', 'Public room'),
       optional_choice_payload_by_name(26, 'Модуль Workspace', 'Community')),
    ['1']
);

foreach([
    [27, $mts_primary_id],
    [27, $mts_scanner_id],
    [27, $mts_license_id],
    [26, $doc_base_template_id],
    [26, $doc_base_simple_template_id],
    [26, $doc_base_patient_template_id],
    [26, $doc_base_clinical_template_id],
    [26, $doc_base_internal_order_template_id],
    [26, $doc_base_manager_guide_id],
    [26, $doc_base_matrix_id],
    [26, $doc_base_regulation_id],
    [25, $doc_simple_test_id],
    [25, $doc_patient_route_id],
    [25, $doc_clinical_note_id],
    [25, $doc_internal_order_simple_id],
] as $ecosystem_item)
{
    update_ecosystem_links($ecosystem_item[0], $ecosystem_item[1]);
}

foreach([
    [21, $project_primary_id, 'Collaboration room', 'Community'],
    [21, $project_secondary_id, 'Collaboration room', 'Community'],
    [21, $project_archive_id, 'Public room', 'Community'],
    [23, $request_primary_id, 'Form filling room', 'Calendar'],
    [23, $request_secondary_id, 'Public room', 'Community'],
    [23, $request_contract_id, 'Public room', 'Calendar'],
    [23, $request_access_id, 'Public room', 'Community'],
    [25, $doc_request_id, 'Collaboration room', 'Calendar'],
    [25, $doc_project_id, 'Collaboration room', 'Community'],
    [25, $doc_simple_test_id, 'Collaboration room', 'Calendar'],
    [25, $doc_patient_route_id, 'Form filling room', 'Calendar'],
    [25, $doc_clinical_note_id, 'Collaboration room', 'Calendar'],
    [25, $doc_internal_order_simple_id, 'Public room', 'Calendar'],
    [25, $doc_duty_schedule_id, 'Collaboration room', 'Calendar'],
    [25, $doc_approval_id, 'Collaboration room', 'Calendar'],
    [25, $doc_contract_id, 'Public room', 'Community'],
    [26, $doc_base_template_id, 'Public room', 'Community'],
    [26, $doc_base_simple_template_id, 'Public room', 'Community'],
    [26, $doc_base_patient_template_id, 'Form filling room', 'Community'],
    [26, $doc_base_clinical_template_id, 'Collaboration room', 'Community'],
    [26, $doc_base_internal_order_template_id, 'Public room', 'Community'],
    [26, $doc_base_manager_guide_id, 'Public room', 'Community'],
    [26, $doc_base_matrix_id, 'Public room', 'Community'],
    [26, $doc_base_regulation_id, 'Public room', 'Community'],
    [27, $mts_primary_id, 'Public room', 'Calendar'],
    [27, $mts_scanner_id, 'Public room', 'Calendar'],
    [27, $mts_license_id, 'Collaboration room', 'Calendar'],
] as $ecosystem_model)
{
    apply_ecosystem_model($ecosystem_model[0], $ecosystem_model[1], $ecosystem_model[2], $ecosystem_model[3]);
}

console_log('');
console_log('Hospital baseline data prepared.');
console_log('Primary project ID: ' . $project_primary_id);
console_log('Primary request ID: ' . $request_primary_id);
console_log('Request document ID: ' . $doc_request_id);
console_log('Project document ID: ' . $doc_project_id);
console_log('Simple test document ID: ' . $doc_simple_test_id);
console_log('Patient route document ID: ' . $doc_patient_route_id);
console_log('Clinical note document ID: ' . $doc_clinical_note_id);
console_log('Internal order test document ID: ' . $doc_internal_order_simple_id);
console_log('Secondary project ID: ' . $project_secondary_id);
console_log('Secondary request ID: ' . $request_secondary_id);
console_log('Archive project ID: ' . $project_archive_id);
console_log('Approval document ID: ' . $doc_approval_id);
console_log('Contract request ID: ' . $request_contract_id);
console_log('Contract document ID: ' . $doc_contract_id);
console_log('Simple template ID: ' . $doc_base_simple_template_id);
console_log('Patient template ID: ' . $doc_base_patient_template_id);
console_log('Clinical template ID: ' . $doc_base_clinical_template_id);
console_log('Internal order template ID: ' . $doc_base_internal_order_template_id);
