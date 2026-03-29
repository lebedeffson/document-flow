<?php

$service = $_GET['service'] ?? 'docspace';
$entity_id = (int) ($_GET['entity_id'] ?? 0);
$item_id = (int) ($_GET['item_id'] ?? 0);
$requested_module = strtolower(trim((string) ($_GET['workspace_module'] ?? '')));
$requested_room_type = strtolower(trim((string) ($_GET['room_type'] ?? '')));
$requested_intent = strtolower(trim((string) ($_GET['intent'] ?? '')));

$service_map = [
    'docspace' => [
        'title' => 'ONLYOFFICE DocSpace',
        'subtitle' => 'Встроенный collaboration-контур первой волны',
        'description' => 'DocSpace встроен в пользовательский контур как внешний слой совместной работы вокруг карточки документа, проекта, заявки и связанных материалов.',
        'points' => [
            'Первая волна использует DocSpace прежде всего для Collaboration rooms и Public rooms',
            'При необходимости можно ограниченно подключать Form filling rooms для сбора форм и ответов',
            'Открывается прямо из карточки и сохраняет привязку к рабочему контексту',
            'Если room URL подключен, сервис доступен прямо во встроенном режиме',
            'Если внешний room URL еще не задан, остается рабочая встроенная shell-страница с быстрыми действиями',
            'Основной жизненный цикл документа по-прежнему остается в Rukovoditel, ONLYOFFICE Docs и NauDoc',
        ],
        'empty_title' => 'Встроенный режим активен',
        'empty_text' => 'Внешняя комната DocSpace для этой записи пока не задана. Первая волна все равно уже дает рабочую встроенную точку входа: отсюда можно вернуться в карточку, открыть редактор ONLYOFFICE, перейти в NauDoc и подключить room URL позже без переделки пользовательского маршрута.',
        'icon' => 'fa-users',
        'accent' => 'docspace',
        'target_label' => 'Комната DocSpace',
        'model_label' => 'Модель DocSpace',
    ],
    'workspace' => [
        'title' => 'ONLYOFFICE Workspace',
        'subtitle' => 'Встроенный сервисный слой первой волны',
        'description' => 'Workspace встроен как легкий сервисный слой только для тех задач, которых действительно нет в Rukovoditel, без подмены основного пользовательского кабинета.',
        'points' => [
            'Базовый scope первой волны: Calendar',
            'Допустимое легкое расширение: Community как новости или база знаний',
            'Открывается из того же контура и не ломает основной пользовательский маршрут',
            'Если target URL подключен, сервис можно открыть и во встроенном режиме',
            'Если внешний сервис еще не задан, shell-страница остается рабочей точкой перехода и контекста',
            'Mail, CRM, Projects и Documents не входят в первую волну, чтобы не дублировать Rukovoditel и не раздувать внедрение',
            'Роли, заявки, проекты, карточки документов и согласование остаются в Rukovoditel',
        ],
        'empty_title' => 'Встроенный сервисный вход готов',
        'empty_text' => 'Внешний Workspace URL для этой записи пока не задан. При этом встроенный вход уже работает: он сохраняет контекст записи, дает быстрые переходы и позволяет позже подключить легкий service-scope первой волны без изменения пользовательского UX.',
        'icon' => 'fa-briefcase',
        'accent' => 'workspace',
        'target_label' => 'Сервис Workspace',
        'model_label' => 'Модель Workspace',
    ],
];

if(!isset($service_map[$service]))
{
    redirect_to('dashboard/page_not_found');
}

$context = $service_map[$service];
$item_url = '';
$item_title = '';
$onlyoffice_url = '';
$naudoc_url = '';
$target_url = '';
$target_source = '';
$card_shell_link_present = false;
$docspace_room_type = '';
$workspace_module = '';
$workspace_calendar_url = '';
$workspace_create_meeting_url = '';
$workspace_community_url = '';
$service_field_key = $service . '_url';
$service_public_url = platform_service_public_url($service);
$env_target_url = platform_service_target_url($service);

if($entity_id > 0 && $item_id > 0)
{
    $item_query = db_query("select * from app_entity_" . (int) $entity_id . " where id='" . (int) $item_id . "' limit 1");

    if($item = db_fetch_array($item_query))
    {
        $ecosystem_links = platform_item_ecosystem_links($entity_id, $item);
        $item_url = $ecosystem_links['item_url'] ?? '';
        $item_title = trim((string) ($ecosystem_links['item_title'] ?? ''));
        $onlyoffice_url = trim((string) ($ecosystem_links['onlyoffice_url'] ?? ''));
        $naudoc_url = trim((string) ($ecosystem_links['naudoc_url'] ?? ''));
        $item_target_url = trim((string) ($ecosystem_links[$service_field_key] ?? ''));
        $docspace_room_type = trim((string) ($ecosystem_links['docspace_room_label'] ?? ''));
        $workspace_module = trim((string) ($ecosystem_links['workspace_module_label'] ?? ''));
        $workspace_calendar_url = trim((string) ($ecosystem_links['workspace_calendar_url'] ?? ''));
        $workspace_create_meeting_url = trim((string) ($ecosystem_links['workspace_create_meeting_url'] ?? ''));
        $workspace_community_url = trim((string) ($ecosystem_links['workspace_community_url'] ?? ''));

        if(filter_var($item_target_url, FILTER_VALIDATE_URL))
        {
            if(platform_service_is_shell_url($service, $item_target_url, $entity_id, $item_id))
            {
                $card_shell_link_present = true;
            }
            else
            {
                $target_url = $item_target_url;
                $target_source = 'URL из карточки';
            }
        }
    }
}

if(!strlen($item_title) && $item_id > 0)
{
    $item_title = 'Запись #' . $item_id;
}

if(!strlen($target_url) && strlen($env_target_url))
{
    $target_url = $env_target_url;
    $target_source = 'URL из .env';
}

if($service === 'docspace' && !strlen($docspace_room_type) && strlen($requested_room_type))
{
    $docspace_room_type = platform_docspace_room_label($requested_room_type);
}

if($service === 'workspace' && !strlen($workspace_module) && strlen($requested_module))
{
    $workspace_module = platform_workspace_module_label($requested_module);
}

if($service === 'workspace' && !strlen($workspace_calendar_url))
{
    $workspace_calendar_url = platform_service_module_entry_url('workspace', 'calendar', $entity_id, $item_id);
}

if($service === 'workspace' && !strlen($workspace_community_url))
{
    $workspace_community_url = platform_service_module_entry_url('workspace', 'community', $entity_id, $item_id);
}

if($service === 'workspace' && !strlen($workspace_create_meeting_url))
{
    $workspace_create_meeting_url = platform_workspace_create_meeting_url($entity_id, $item_id);
}

if($service === 'docspace' && strlen($docspace_room_type))
{
    if(strcasecmp($docspace_room_type, 'Public room') === 0)
    {
        $context['subtitle'] = 'Public room первой волны';
        $context['description'] = 'DocSpace используется как безопасный внешний контур публикации и выдачи пакетов документов без подмены основного рабочего кабинета.';
        $context['points'] = [
            'Public room подходит для выдачи пакета документов внешним участникам по ссылке',
            'Комната сохраняет привязку к карточке или проекту и не ломает основной маршрут пользователя',
            'Рабочий черновик и согласование по-прежнему живут в Rukovoditel, ONLYOFFICE Docs и NauDoc',
            'При необходимости права, срок действия ссылки и пароль можно настраивать уже на стороне DocSpace',
        ];
    }
    elseif(strcasecmp($docspace_room_type, 'Form filling room') === 0)
    {
        $context['subtitle'] = 'Form filling room первой волны';
        $context['description'] = 'DocSpace используется как контур сбора форм и ответов вокруг рабочей записи без отдельного пользовательского кабинета.';
        $context['points'] = [
            'Form filling room нужен для раздачи и сбора форм без пересылки файлов вручную',
            'Контекст записи сохраняется, а сам пользовательский маршрут остается единым',
            'Основной документный цикл по-прежнему остается в Rukovoditel, ONLYOFFICE Docs и NauDoc',
            'После подключения внешней комнаты URL можно закрепить прямо на карточке и использовать без переделки UX',
        ];
    }
}

if($service === 'workspace' && strlen($workspace_module))
{
    if(strcasecmp($workspace_module, 'Calendar') === 0)
    {
        $context['subtitle'] = 'Calendar и встречи первой волны';
        $context['description'] = 'Workspace используется как легкий календарный слой: встречи, общие календари, слоты согласований и напоминания без переноса бизнес-процессов из Rukovoditel.';
        $context['points'] = [
            'Встречи и календарные события доступны всем пользователям, а не только администратору',
            'Календарь открывается из того же контура и не подменяет основной рабочий кабинет',
            'Если direct URL календаря не задан, shell-экран все равно сохраняет единый маршрут и контекст',
            'Mail, CRM, Projects и Documents не входят в первую волну и не дублируют Rukovoditel',
        ];
        $context['empty_title'] = 'Календарь и встречи готовы';
        $context['empty_text'] = 'Календарный контур Workspace уже встроен в первую волну. Даже если прямой URL календаря еще не закреплен, пользователи уже могут идти по единой точке входа и дальше открывать сервис без разрыва маршрута.';
    }
    elseif(strcasecmp($workspace_module, 'Community') === 0)
    {
        $context['subtitle'] = 'Community первой волны';
        $context['description'] = 'Workspace используется как легкий слой новостей и базы знаний без подмены основного рабочего кабинета и без запуска тяжелых модулей.';
        $context['points'] = [
            'Community подходит для новостей, объявлений и wiki-страниц первой волны',
            'Пользовательский маршрут остается единым: рабочая логика и документы живут в Rukovoditel',
            'Если direct URL Community не задан, shell-экран сохраняет точку входа и контекст записи',
            'Mail, CRM, Projects и Documents не входят в первую волну и не увеличивают объем внедрения',
        ];
        $context['empty_title'] = 'Community-контур готов';
        $context['empty_text'] = 'Легкий контур новостей и базы знаний уже встроен в первую волну. Даже без прямого Community URL единая точка входа сохраняется и может быть расширена позже без переделки UX.';
    }
}

if($service === 'workspace' && $requested_intent === 'create_meeting')
{
    $context['subtitle'] = 'Создание встречи';
    $context['description'] = 'Этот маршрут ведет прямо в сценарий календарной встречи: открыть календарь, выбрать слот, создать событие и вернуть участников к рабочей записи без разрыва пользовательского пути.';
    $context['points'] = [
        'Встреча создается из того же рабочего контура и доступна обычным пользователям, а не только администратору',
        'Базовый путь первой волны: Calendar -> новый слот -> описание встречи -> участники',
        'Рабочий контекст записи сохраняется, поэтому встречу можно связать с проектом, заявкой или карточкой документа',
        'Если внешний Workspace еще не подключен, shell-экран все равно оставляет понятную точку входа и не ломает UX',
    ];
    $context['empty_title'] = 'Маршрут создания встречи готов';
    $context['empty_text'] = 'Внешний календарный target пока не задан, но точка входа к созданию встречи уже закреплена. После подключения live Workspace этот же маршрут будет вести прямо в календарный сценарий без изменения пользовательских кнопок.';
}

$is_embedded_mode = strlen($target_url) > 0;
$status_label = $is_embedded_mode ? 'Встроенное подключение активно' : 'Рабочий shell первой волны';
$status_copy = $is_embedded_mode
    ? ('Сервис подключен и может открываться прямо внутри платформы. Источник: ' . $target_source . '.')
    : ($card_shell_link_present
        ? 'Для этой записи уже закреплена единая встроенная ссылка первой волны. Пользовательский маршрут остается стабильным: ссылка сохранена в карточке, а внешний target можно подключить позже через .env или прямой URL записи.'
        : $context['empty_text']);
?>
<div class="ecosystem-page ecosystem-page-<?php echo $context['accent'] ?>">
    <div class="ecosystem-page-head">
        <div class="ecosystem-page-icon"><i class="fa <?php echo $context['icon'] ?>"></i></div>
        <div class="ecosystem-page-copy">
            <div class="ecosystem-page-eyebrow"><?php echo $context['subtitle'] ?></div>
            <h1><?php echo $context['title'] ?></h1>
            <p><?php echo $context['description'] ?></p>
        </div>
    </div>

    <div class="ecosystem-page-body">
        <section class="ecosystem-page-card">
            <h3>Как это работает в первой волне</h3>
            <ul class="ecosystem-page-points">
                <?php foreach($context['points'] as $point): ?>
                    <li><?php echo $point ?></li>
                <?php endforeach ?>
            </ul>
        </section>

        <section class="ecosystem-page-card">
            <h3><?php echo $context['empty_title'] ?></h3>
            <div class="ecosystem-page-status-badge"><?php echo $status_label ?></div>
            <p><?php echo $status_copy ?></p>

            <div class="ecosystem-page-service-meta">
                <div>
                    <span class="ecosystem-page-context-label">Единая точка входа</span>
                    <div class="ecosystem-page-meta-value"><?php echo htmlspecialchars($service_public_url) ?></div>
                </div>

                <?php if($is_embedded_mode): ?>
                    <div>
                        <span class="ecosystem-page-context-label"><?php echo $context['target_label'] ?></span>
                        <div class="ecosystem-page-meta-value"><?php echo htmlspecialchars($target_url) ?></div>
                    </div>
                <?php endif ?>

                <?php if($service === 'docspace' && strlen($docspace_room_type)): ?>
                    <div>
                        <span class="ecosystem-page-context-label"><?php echo $context['model_label'] ?></span>
                        <div class="ecosystem-page-meta-value"><?php echo htmlspecialchars($docspace_room_type) ?></div>
                    </div>
                <?php endif ?>

                <?php if($service === 'workspace' && strlen($workspace_module)): ?>
                    <div>
                        <span class="ecosystem-page-context-label"><?php echo $context['model_label'] ?></span>
                        <div class="ecosystem-page-meta-value"><?php echo htmlspecialchars($workspace_module) ?></div>
                    </div>
                <?php endif ?>
            </div>

            <?php if(strlen($item_url)): ?>
                <div class="ecosystem-page-context">
                    <div class="ecosystem-page-context-label">Текущий контекст</div>
                    <div class="ecosystem-page-context-title">
                        <?php echo strlen($item_title) ? htmlspecialchars($item_title) : ('Запись #' . $item_id) ?>
                    </div>
                </div>
            <?php endif ?>

            <div class="ecosystem-page-actions">
                <?php if(strlen($item_url)): ?>
                    <?php echo link_to('<i class="fa fa-arrow-left"></i> Вернуться в карточку', $item_url, ['class' => 'btn btn-default']) ?>
                <?php else: ?>
                    <?php echo link_to('<i class="fa fa-home"></i> Вернуться на главную', url_for('dashboard/dashboard'), ['class' => 'btn btn-default']) ?>
                <?php endif ?>

                <?php if(strlen($onlyoffice_url)): ?>
                    <?php echo link_to('<i class="fa fa-pencil-square-o"></i> Открыть ONLYOFFICE', $onlyoffice_url, ['class' => 'btn btn-info', 'target' => '_blank']) ?>
                <?php endif ?>

                <?php if(strlen($naudoc_url)): ?>
                    <?php echo link_to('<i class="fa fa-folder-open-o"></i> Открыть NauDoc', $naudoc_url, ['class' => 'btn btn-default', 'target' => '_blank']) ?>
                <?php elseif($service === 'workspace'): ?>
                    <?php echo link_to('<i class="fa fa-archive"></i> Открыть общий NauDoc', '/docs/', ['class' => 'btn btn-default', 'target' => '_blank']) ?>
                <?php endif ?>

                <?php if($service === 'workspace' && strlen($workspace_calendar_url)): ?>
                    <?php echo link_to('<i class="fa fa-calendar"></i> Календарь и встречи', $workspace_calendar_url, ['class' => 'btn btn-default']) ?>
                <?php endif ?>

                <?php if($service === 'workspace' && strlen($workspace_create_meeting_url)): ?>
                    <?php echo link_to('<i class="fa fa-calendar-plus-o"></i> Создать встречу', $workspace_create_meeting_url, ['class' => 'btn btn-info']) ?>
                <?php endif ?>

                <?php if($service === 'workspace' && strlen($workspace_community_url) && strcasecmp($workspace_module, 'Community') === 0): ?>
                    <?php echo link_to('<i class="fa fa-book"></i> Открыть Community', $workspace_community_url, ['class' => 'btn btn-default']) ?>
                <?php endif ?>

                <?php if($is_embedded_mode): ?>
                    <?php echo link_to('<i class="fa fa-external-link"></i> Открыть сервис отдельно', $target_url, ['class' => 'btn btn-default', 'target' => '_blank']) ?>
                <?php endif ?>
            </div>
        </section>
    </div>

    <?php if($is_embedded_mode): ?>
        <section class="ecosystem-page-card ecosystem-page-embed-card">
            <div class="ecosystem-page-embed-head">
                <div>
                    <h3>Встроенный режим</h3>
                    <p>Если внешний сервис разрешает встраивание, он открывается прямо внутри платформы без разрыва контекста.</p>
                </div>
                <div class="ecosystem-page-status-badge">iframe mode</div>
            </div>
            <div class="ecosystem-page-embed-shell">
                <iframe
                    class="ecosystem-page-embed-frame"
                    src="<?php echo htmlspecialchars($target_url) ?>"
                    loading="lazy"
                    referrerpolicy="strict-origin-when-cross-origin"
                    title="<?php echo htmlspecialchars($context['title']) ?>"
                ></iframe>
            </div>
            <div class="ecosystem-page-inline-note">
                Если провайдер сервиса запрещает iframe, используйте кнопку "Открыть сервис отдельно". Точка входа и пользовательский маршрут при этом остаются едиными.
            </div>
        </section>
    <?php endif ?>
</div>
