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
        $sql_data['field_' . $docspace_field_id] = '';
    }

    if($workspace_field_id > 0)
    {
        $sql_data['field_' . $workspace_field_id] = '';
    }

    if(count($sql_data))
    {
        $sql_data['date_updated'] = time();
        db_perform('app_entity_' . (int) $entity_id, $sql_data, 'update', "id='" . db_input($item_id) . "'");
        console_log("Reset optional ecosystem links for entity {$entity_id} item #{$item_id}");
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
        console_log("Created demo item {$target_title} (#{$item_id}) in entity {$entity_id}");
        return (int) $item_id;
    }

    $item_id = (int) $item['id'];
    unset($sql_data['date_added']);
    db_perform('app_entity_' . (int) $entity_id, $sql_data, 'update', "id='" . db_input($item_id) . "'");
    console_log("Updated demo item {$target_title} (#{$item_id}) in entity {$entity_id}");
    return $item_id;
}

set_configuration_value('CFG_APP_NAME', 'Единая платформа документооборота');
set_configuration_value('CFG_APP_SHORT_NAME', 'Документооборот');
set_configuration_value('CFG_LOGIN_PAGE_HEADING', 'Демонстрационный контур платформы документооборота');
set_configuration_value(
    'CFG_LOGIN_PAGE_CONTENT',
    'Проекты, заявки, совместная работа над документами, маршруты согласования и архив в едином веб-контуре.'
);

rename_field_if_exists(282, 'Совместное редактирование');

$naudoc_public_url = getenv('NAUDOC_PUBLIC_URL') ?: 'https://localhost:18443/docs';

$doc_route_field_id = get_field_id_by_name(25, 'Маршрут документа');
$route_internal_order_id = get_choice_id_by_name($doc_route_field_id, 'Внутренний приказ');
$route_outgoing_approval_id = get_choice_id_by_name($doc_route_field_id, 'Исходящее согласование');
$route_contract_id = get_choice_id_by_name($doc_route_field_id, 'Договор и закупка');

$project_primary_id = ensure_demo_item(
    21,
    158,
    'Внедрение единой платформы документооборота',
    [
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
    ],
    ['Тестовый проект цифрового документооборота']
);

$request_primary_id = ensure_demo_item(
    23,
    184,
    'Подготовка маршрута согласования приказа о пилоте',
    [
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
    ],
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
    ], optional_field_payload($doc_route_field_id, $route_outgoing_approval_id)),
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
    ], optional_field_payload($doc_route_field_id, $route_outgoing_approval_id)),
    ['Документ проекта: Тестовый проект цифрового документооборота']
);

db_perform('app_entity_21', ['field_279' => (string) $doc_project_id], 'update', "id='" . db_input($project_primary_id) . "'");
db_perform('app_entity_23', ['field_240' => (string) $doc_request_id], 'update', "id='" . db_input($request_primary_id) . "'");

foreach([
    [21, $project_primary_id],
    [23, $request_primary_id],
    [25, $doc_request_id],
    [25, $doc_project_id],
] as $ecosystem_item)
{
    update_ecosystem_links($ecosystem_item[0], $ecosystem_item[1]);
}

$project_secondary_id = ensure_demo_item(
    21,
    158,
    'Подготовка регламента согласования внутренних документов',
    [
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
    ]
);

$project_archive_id = ensure_demo_item(
    21,
    158,
    'Архивирование завершенных регламентов',
    [
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
    ]
);

$request_secondary_id = ensure_demo_item(
    23,
    184,
    'Подключить шаблон служебной записки для отделений',
    [
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
    ]
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
    [
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
    ]
);

$request_access_id = ensure_demo_item(
    23,
    184,
    'Открыть доступ к шаблонам служебной записки',
    [
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
    ]
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
    ], optional_field_payload($doc_route_field_id, $route_internal_order_id))
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
    ], optional_field_payload($doc_route_field_id, $route_contract_id))
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
    [
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
        'field_274' => '<p>Демонстрационный кейс по обеспечению: заявка связана с проектом внедрения и показывает отдельный процесс МТЗ.</p>',
        'field_278' => 767,
    ]
);

$mts_scanner_id = ensure_demo_item(
    27,
    265,
    'Сканер для оцифровки входящих документов',
    [
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
    ]
);

$mts_license_id = ensure_demo_item(
    27,
    265,
    'Лицензии ONLYOFFICE для совместного редактирования',
    [
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
    ]
);

$doc_base_template_id = ensure_demo_item(
    26,
    255,
    'Шаблон служебной записки для отделений',
    [
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
    ]
);

$doc_base_manager_guide_id = ensure_demo_item(
    26,
    255,
    'Инструкция для руководителя по согласованию документов',
    [
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
    ]
);

$doc_base_matrix_id = ensure_demo_item(
    26,
    255,
    'Матрица ролей и маршрутов документов',
    [
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
    ]
);

$doc_base_regulation_id = ensure_demo_item(
    26,
    255,
    'Регламент совместной работы с документами',
    [
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
    ],
    ['1']
);

foreach([
    [27, $mts_primary_id],
    [27, $mts_scanner_id],
    [27, $mts_license_id],
    [26, $doc_base_template_id],
    [26, $doc_base_manager_guide_id],
    [26, $doc_base_matrix_id],
    [26, $doc_base_regulation_id],
] as $ecosystem_item)
{
    update_ecosystem_links($ecosystem_item[0], $ecosystem_item[1]);
}

console_log('');
console_log('Customer demo data prepared.');
console_log('Primary project ID: ' . $project_primary_id);
console_log('Primary request ID: ' . $request_primary_id);
console_log('Request document ID: ' . $doc_request_id);
console_log('Project document ID: ' . $doc_project_id);
console_log('Secondary project ID: ' . $project_secondary_id);
console_log('Secondary request ID: ' . $request_secondary_id);
console_log('Archive project ID: ' . $project_archive_id);
console_log('Approval document ID: ' . $doc_approval_id);
console_log('Contract request ID: ' . $request_contract_id);
console_log('Contract document ID: ' . $doc_contract_id);
