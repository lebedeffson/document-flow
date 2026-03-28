<?php

$service = $_GET['service'] ?? 'docspace';
$entity_id = (int) ($_GET['entity_id'] ?? 0);
$item_id = (int) ($_GET['item_id'] ?? 0);

$service_map = [
    'docspace' => [
        'title' => 'ONLYOFFICE DocSpace',
        'subtitle' => 'Встроенный collaboration-контур первой волны',
        'description' => 'DocSpace встроен в пользовательский контур как точка групповой работы вокруг карточки документа, проекта, заявки и связанных материалов.',
        'points' => [
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
    ],
    'workspace' => [
        'title' => 'ONLYOFFICE Workspace',
        'subtitle' => 'Встроенный сервисный слой первой волны',
        'description' => 'Workspace встроен как дополнительный сервисный слой для тех задач, которых действительно нет в Rukovoditel, без подмены основного пользовательского кабинета.',
        'points' => [
            'Открывается из того же контура и не ломает основной пользовательский маршрут',
            'Если target URL подключен, сервис можно открыть и во встроенном режиме',
            'Если внешний сервис еще не задан, shell-страница остается рабочей точкой перехода и контекста',
            'Роли, заявки, проекты, карточки документов и согласование остаются в Rukovoditel',
        ],
        'empty_title' => 'Встроенный сервисный вход готов',
        'empty_text' => 'Внешний Workspace URL для этой записи пока не задан. При этом встроенный вход уже работает: он сохраняет контекст записи, дает быстрые переходы и позволяет подключить внешний сервис позже без изменения пользовательского UX.',
        'icon' => 'fa-briefcase',
        'accent' => 'workspace',
        'target_label' => 'Сервис Workspace',
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
