<?php

$service = $_GET['service'] ?? 'docspace';
$entity_id = (int) ($_GET['entity_id'] ?? 0);
$item_id = (int) ($_GET['item_id'] ?? 0);

$service_map = [
    'docspace' => [
        'title' => 'ONLYOFFICE DocSpace',
        'subtitle' => 'Сервис пока не развернут в этом стенде',
        'description' => 'В текущем контуре встроен только редактор ONLYOFFICE Docs. DocSpace вынесен в следующий этап и пока не поднят как отдельный сервис.',
        'points' => [
            'Планируется как внешний контур для комнат и совместной работы',
            'В этом стенде отдельный сервис DocSpace еще не поднят',
            'Для работы с документом используйте карточку документа и встроенный редактор',
        ],
        'icon' => 'fa-users',
        'accent' => 'docspace',
    ],
    'workspace' => [
        'title' => 'ONLYOFFICE Workspace',
        'subtitle' => 'Сервис пока не развернут в этом стенде',
        'description' => 'В текущем контуре Workspace не поднят как отдельный сервис. Рабочий контур платформы сейчас строится вокруг Rukovoditel, NauDoc и встроенного редактора ONLYOFFICE Docs.',
        'points' => [
            'Планируется как отдельный корпоративный сервисный слой',
            'В этом стенде отдельный сервис Workspace еще не поднят',
            'Для работы с документом используйте карточку документа и встроенный редактор',
        ],
        'icon' => 'fa-briefcase',
        'accent' => 'workspace',
    ],
];

if(!isset($service_map[$service]))
{
    redirect_to('dashboard/page_not_found');
}

$context = $service_map[$service];
$item_url = '';
$item_title = '';

if($entity_id > 0 && $item_id > 0)
{
    $item_url = url_for('items/info', 'path=' . $entity_id . '-' . $item_id);
    $title_field_id = platform_field_id_by_type($entity_id, 'fieldtype_input');

    if($title_field_id > 0)
    {
        $item_row = db_fetch_array(db_query("select field_" . $title_field_id . " as item_title from app_entity_" . (int) $entity_id . " where id='" . (int) $item_id . "' limit 1"));
        $item_title = trim($item_row['item_title'] ?? '');
    }
}
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
            <h3>Для чего используется</h3>
            <ul class="ecosystem-page-points">
                <?php foreach($context['points'] as $point): ?>
                    <li><?php echo $point ?></li>
                <?php endforeach ?>
            </ul>
        </section>

        <section class="ecosystem-page-card">
            <h3>Текущее состояние</h3>
            <p>
                Отдельный сервис сейчас не развернут. В текущем стенде реально встроен только редактор ONLYOFFICE Docs,
                который открывается из карточки документа. Для официального контура используется NauDoc.
            </p>

            <?php if(strlen($item_url)): ?>
                <div class="ecosystem-page-context">
                    <div class="ecosystem-page-context-label">Текущий контекст</div>
                    <div class="ecosystem-page-context-title">
                        <?php echo strlen($item_title) ? htmlspecialchars($item_title) : ('Запись #' . $item_id) ?>
                    </div>
                    <div class="ecosystem-page-actions">
                        <?php echo link_to('<i class="fa fa-arrow-left"></i> Вернуться в карточку', $item_url, ['class' => 'btn btn-default']) ?>
                    </div>
                </div>
            <?php else: ?>
                <div class="ecosystem-page-actions">
                    <?php echo link_to('<i class="fa fa-home"></i> Вернуться на главную', url_for('dashboard/dashboard'), ['class' => 'btn btn-default']) ?>
                </div>
            <?php endif ?>
        </section>
    </div>
</div>
