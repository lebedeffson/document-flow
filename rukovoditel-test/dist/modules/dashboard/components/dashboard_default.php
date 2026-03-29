<?php
/**
 * Этот файл является частью программы "CRM Руководитель" - конструктор CRM систем для бизнеса
 * https://www.rukovoditel.net.ru/
 * 
 * CRM Руководитель - это свободное программное обеспечение,
 * распространяемое на условиях GNU GPLv3 https://www.gnu.org/licenses/gpl-3.0.html
 * 
 * Автор и правообладатель программы: Харчишина Ольга Александровна (RU), Харчишин Сергей Васильевич (RU).
 * Государственная регистрация программы для ЭВМ: 2023664624
 * https://fips.ru/EGD/3b18c104-1db7-4f2d-83fb-2d38e1474ca3
 */
?>
<?php

app_reset_selected_items();

if (!function_exists('platform_home_entity_url'))
{
    function platform_home_entity_url($entity_id)
    {
        return url_for('items/items', 'path=' . (int)$entity_id);
    }
}

if (!function_exists('platform_home_report_url'))
{
    function platform_home_report_url($report_id)
    {
        return url_for('reports/view', 'reports_id=' . (int)$report_id);
    }
}

if (!function_exists('platform_home_named_report_url'))
{
    function platform_home_named_report_url($entity_id, $report_name, $fallback = '')
    {
        $report = db_fetch_array(db_query(
            "select id from app_reports where entities_id='" . (int)$entity_id . "' and name='" . db_input($report_name) . "' order by id limit 1"
        ));

        if ($report)
        {
            return platform_home_report_url($report['id']);
        }

        return $fallback;
    }
}

if (!function_exists('platform_home_button'))
{
    function platform_home_button($label, $url, $type = 'primary', $external = false)
    {
        $class = 'platform-home-btn platform-home-btn-' . $type;
        $target = $external ? ' target="_blank" rel="noopener"' : '';

        return '<a class="' . $class . '" href="' . htmlspecialchars($url) . '"' . $target . '>' . $label . '</a>';
    }
}

if (!function_exists('platform_home_link_item'))
{
    function platform_home_link_item($title, $description, $url, $external = false)
    {
        $target = $external ? ' target="_blank" rel="noopener"' : '';

        return '
            <a class="platform-home-link-item" href="' . htmlspecialchars($url) . '"' . $target . '>
                <span class="platform-home-link-title">' . $title . '</span>
                <span class="platform-home-link-description">' . $description . '</span>
            </a>
        ';
    }
}

if (!function_exists('platform_home_links_group'))
{
    function platform_home_links_group($items)
    {
        $html = '';

        foreach ($items as $item)
        {
            $html .= platform_home_link_item(
                $item['title'],
                $item['description'],
                $item['url'],
                $item['external'] ?? false
            );
        }

        return $html;
    }
}

if (!function_exists('platform_home_scalar_query'))
{
    function platform_home_scalar_query($sql)
    {
        $query = db_query($sql);
        if ($row = db_fetch_array($query))
        {
            return array_shift($row);
        }

        return 0;
    }
}

if (!function_exists('platform_home_status_card'))
{
    function platform_home_status_card($title, $value, $description, $url = '')
    {
        $html = '<div class="platform-home-status-card">';
        $html .= '<div class="platform-home-status-value">' . $value . '</div>';
        $html .= '<div class="platform-home-status-title">' . $title . '</div>';
        $html .= '<div class="platform-home-status-description">' . $description . '</div>';

        if (strlen($url))
        {
            $html .= '<div class="platform-home-status-link"><a href="' . htmlspecialchars($url) . '">Открыть раздел</a></div>';
        }

        $html .= '</div>';

        return $html;
    }
}

if (!function_exists('platform_home_naudoc_profiles'))
{
    function platform_home_naudoc_profiles()
    {
        $path = DIR_FS_CACHE . 'naudoc_profiles.json';
        if (!is_file($path))
        {
            return [];
        }

        $payload = json_decode(file_get_contents($path), true);
        if (!is_array($payload) || !isset($payload['profiles']) || !is_array($payload['profiles']))
        {
            return [];
        }

        return $payload['profiles'];
    }
}

if (!function_exists('platform_home_current_naudoc_profile'))
{
    function platform_home_current_naudoc_profile($username)
    {
        $profiles = platform_home_naudoc_profiles();
        if (!$username || !isset($profiles[$username]) || !is_array($profiles[$username]))
        {
            return [];
        }

        return $profiles[$username];
    }
}

$group_id = (int)$app_user['group_id'];
$user_name = trim($app_user['name']);
$username = trim($app_user['username'] ?? '');

$is_admin = ($group_id === 0);
$is_manager = ($is_admin || $group_id === 4);
$is_employee = ($group_id === 5);
$is_requester = ($group_id === 6);
$is_office = ($group_id === 7);

$role_label = 'сотрудника';
if ($is_manager)
{
    $role_label = 'руководителя';
}
elseif ($is_office)
{
    $role_label = 'канцелярии';
}
elseif ($is_requester)
{
    $role_label = 'заявителя';
}

$documents_note = 'Чтобы начать работу, откройте карточку документа и используйте кнопки "Создать пустой документ", "Создать пустую таблицу" или "Открыть документ в редакторе".';
$tasks_url = platform_home_named_report_url(22, 'Мои задачи в работе', platform_home_entity_url(21));
$discussions_url = platform_home_named_report_url(24, 'Рабочие обсуждения', '');
$onlyoffice_demo = platform_first_onlyoffice_demo(25);
$linked_requests_url = ($is_admin || $is_manager)
    ? platform_home_named_report_url(23, 'Заявки без финального документа', platform_home_entity_url(23))
    : platform_home_entity_url(23);
$linked_projects_url = ($is_admin || $is_manager)
    ? platform_home_named_report_url(21, 'Проекты с риском по документам', platform_home_entity_url(21))
    : platform_home_entity_url(21);
$doc_approval_url = ($is_admin || $is_manager)
    ? platform_home_named_report_url(25, 'Документы на согласовании', platform_home_entity_url(25))
    : platform_home_entity_url(25);
$onlyoffice_demo_item_url = platform_home_entity_url(25);
$onlyoffice_demo_editor_url = '';
$docspace_entry_url = platform_service_entry_url('docspace');
$workspace_entry_url = platform_service_entry_url('workspace');
$workspace_calendar_url = platform_service_module_entry_url('workspace', 'calendar');
$workspace_create_meeting_url = platform_workspace_create_meeting_url();
$workspace_community_url = platform_service_module_entry_url('workspace', 'community');
$naudoc_profile = platform_home_current_naudoc_profile($username);

$doc_field_id = 250;
$request_field_id = 241;
$project_field_id = 230;
$onlyoffice_field_id = (int) $onlyoffice_demo['field_id'];

$linked_docs_count = (int) platform_home_scalar_query("select count(*) from app_entity_25 where length(trim(coalesce(field_{$doc_field_id}, '')))>0");
$requests_without_doc_count = (int) platform_home_scalar_query("select count(*) from app_entity_23 where length(trim(coalesce(field_{$request_field_id}, '')))=0");
$projects_without_doc_count = (int) platform_home_scalar_query("select count(*) from app_entity_21 where length(trim(coalesce(field_{$project_field_id}, '')))=0");
$drafts_count = $onlyoffice_field_id > 0 ? (int) platform_home_scalar_query("select count(*) from app_entity_25 where length(trim(coalesce(field_{$onlyoffice_field_id}, '')))>0") : 0;

if ($onlyoffice_demo['item_id'] > 0)
{
    $onlyoffice_demo_item_url = url_for('items/info', 'path=25-' . $onlyoffice_demo['item_id']);
    if (platform_service_enabled('docspace'))
    {
        $docspace_entry_url = platform_service_entry_url('docspace', 25, $onlyoffice_demo['item_id']);
    }
    if (platform_service_enabled('workspace'))
    {
        $workspace_entry_url = platform_service_entry_url('workspace', 25, $onlyoffice_demo['item_id']);
        $workspace_calendar_url = platform_service_module_entry_url('workspace', 'calendar', 25, $onlyoffice_demo['item_id']);
        $workspace_create_meeting_url = platform_workspace_create_meeting_url(25, $onlyoffice_demo['item_id']);
        $workspace_community_url = platform_service_module_entry_url('workspace', 'community', 25, $onlyoffice_demo['item_id']);
    }

    if ((int) $onlyoffice_demo['field_id'] > 0 && (int) $onlyoffice_demo['file_id'] > 0)
    {
        $onlyoffice_demo_editor_url = url_for(
            'items/onlyoffice_editor',
            'path=25-' . $onlyoffice_demo['item_id'] . '&action=open&field=' . (int) $onlyoffice_demo['field_id'] . '&file=' . (int) $onlyoffice_demo['file_id']
        );
    }
}

$admin_work_links = [
    ['title' => 'Заявки на обслуживание', 'description' => 'Рабочие обращения и сервисные запросы.', 'url' => platform_home_entity_url(23)],
    ['title' => 'Проекты и инициативы', 'description' => 'Проекты, этапы и связанные документы.', 'url' => platform_home_entity_url(21)],
    ['title' => 'Поручения и задачи', 'description' => 'Рабочие задачи через отчетный контур.', 'url' => $tasks_url],
    ['title' => 'Рабочие обсуждения', 'description' => 'Обсуждения в контексте проектов.', 'url' => strlen($discussions_url) ? $discussions_url : platform_home_entity_url(21)],
    ['title' => 'Карточки документов', 'description' => 'Основная точка работы с документом.', 'url' => platform_home_entity_url(25)],
    ['title' => 'База документов', 'description' => 'Шаблоны, инструкции и материалы.', 'url' => platform_home_entity_url(26)],
    ['title' => 'МТЗ', 'description' => 'Материально-техническое обеспечение.', 'url' => platform_home_entity_url(27)],
];

$admin_system_links = [
    ['title' => 'Пользователи', 'description' => 'Список сотрудников, учетные записи и профили.', 'url' => platform_home_entity_url(1)],
    ['title' => 'Создать пользователя', 'description' => 'Быстро завести нового сотрудника без поиска по техразделам.', 'url' => url_for('items/form', 'path=1')],
    ['title' => 'Группы и права', 'description' => 'Группы доступа, роли и схема прав.', 'url' => url_for('users_groups/users_groups')],
    ['title' => 'Настройки приложения', 'description' => 'Общая конфигурация платформы.', 'url' => url_for('configuration/application')],
    ['title' => 'Сущности приложения', 'description' => 'Структура модулей и форм.', 'url' => url_for('entities/entities')],
    ['title' => 'Логи', 'description' => 'HTTP, PHP, MySQL и почта.', 'url' => url_for('logs/settings')],
    ['title' => 'Резервные копии', 'description' => 'Ручные и автоматические бэкапы.', 'url' => url_for('tools/db_backup')],
    ['title' => 'NauDoc', 'description' => 'Официальный документный контур.', 'url' => '/docs/', 'external' => true],
    ['title' => 'Bridge', 'description' => 'Интеграционный слой и контроль связей.', 'url' => '/bridge/', 'external' => true],
];

if (strlen($docspace_entry_url))
{
    $admin_system_links[] = ['title' => 'DocSpace', 'description' => 'Встроенный collaboration-контур первой волны.', 'url' => $docspace_entry_url];
}

if (strlen($workspace_entry_url))
{
    $admin_system_links[] = ['title' => 'Workspace', 'description' => 'Встроенный сервисный слой первой волны.', 'url' => $workspace_entry_url];
}

if (strlen($workspace_calendar_url))
{
    $admin_system_links[] = ['title' => 'Встречи Workspace', 'description' => 'Календарь и встречи доступны всем пользователям первой волны.', 'url' => $workspace_calendar_url];
}

if (strlen($workspace_create_meeting_url))
{
    $admin_system_links[] = ['title' => 'Создать встречу', 'description' => 'Быстрый вход в сценарий создания календарной встречи.', 'url' => $workspace_create_meeting_url];
}

if (strlen($workspace_community_url))
{
    $admin_system_links[] = ['title' => 'Workspace Community', 'description' => 'Легкие новости и база знаний без запуска тяжелых модулей.', 'url' => $workspace_community_url];
}

$user_work_links = [
    ['title' => 'Заявки', 'description' => 'Создание и сопровождение обращений.', 'url' => platform_home_entity_url(23)],
];

if (!$is_office)
{
    $user_work_links[] = ['title' => 'Задачи', 'description' => 'Мои поручения и рабочие задачи.', 'url' => $tasks_url];
}

$user_work_links[] = ['title' => 'Проекты', 'description' => 'Проекты, этапы и связанный контур.', 'url' => platform_home_entity_url(21)];
$user_work_links[] = ['title' => 'Карточки документов', 'description' => 'Работа с документом и переход в редактор.', 'url' => platform_home_entity_url(25)];
$user_work_links[] = ['title' => 'База документов', 'description' => 'Шаблоны, инструкции и регламенты.', 'url' => platform_home_entity_url(26)];
$user_work_links[] = ['title' => 'МТЗ', 'description' => 'Заявки на обеспечение и снабжение.', 'url' => platform_home_entity_url(27)];

if ($is_manager)
{
    $user_work_links[] = ['title' => 'Контроль руководителя', 'description' => 'Ключевые отчеты по контролю и согласованию.', 'url' => platform_home_named_report_url(21, 'Проекты на контроле', platform_home_entity_url(21))];
}

$user_document_links = [
    ['title' => 'NauDoc', 'description' => 'Регистрация, архив и официальный документ.', 'url' => '/docs/', 'external' => true],
    ['title' => 'Карточки документов', 'description' => 'Рабочая карточка и запуск редактора.', 'url' => platform_home_entity_url(25)],
];

if (strlen($docspace_entry_url))
{
    $user_document_links[] = ['title' => 'DocSpace', 'description' => 'Встроенный collaboration-контур вокруг карточки документа.', 'url' => $docspace_entry_url];
}

if (strlen($workspace_entry_url))
{
    $user_document_links[] = ['title' => 'Workspace', 'description' => 'Встроенный сервисный слой для сопутствующей работы.', 'url' => $workspace_entry_url];
}

if (strlen($workspace_calendar_url))
{
    $user_document_links[] = ['title' => 'Встречи Workspace', 'description' => 'Календарь и встречи доступны всем пользователям.', 'url' => $workspace_calendar_url];
}

if (strlen($workspace_create_meeting_url))
{
    $user_document_links[] = ['title' => 'Создать встречу', 'description' => 'Быстрый переход к созданию календарной встречи.', 'url' => $workspace_create_meeting_url];
}

if (strlen($workspace_community_url))
{
    $user_document_links[] = ['title' => 'Workspace Community', 'description' => 'Новости и база знаний первой волны.', 'url' => $workspace_community_url];
}

if ($onlyoffice_demo['item_id'] > 0)
{
    $user_document_links[] = ['title' => 'ONLYOFFICE', 'description' => 'Открыть рабочий документ через карточку.', 'url' => $onlyoffice_demo_item_url];
}

if ($is_admin)
{
    echo '
    <div class="platform-home platform-home-admin-mode">
        <section class="platform-home-hero platform-home-hero-compact">
            <div class="platform-home-hero-main">
                <span class="platform-home-eyebrow">Административный контур</span>
                <h1>Центр управления платформой</h1>
                <p>
                    Полный режим сопровождения: рабочие модули, документы, пользователи, настройки и контроль интеграций.
                </p>
                <div class="platform-home-hero-actions">
                    ' . platform_home_button('Рабочие документы', platform_home_entity_url(25), 'primary') . '
                    ' . platform_home_button('Создать пользователя', url_for('items/form', 'path=1'), 'secondary') . '
                    ' . (strlen($docspace_entry_url) ? platform_home_button('DocSpace', $docspace_entry_url, 'secondary') : '') . '
                    ' . (strlen($workspace_entry_url) ? platform_home_button('Workspace', $workspace_entry_url, 'secondary') : '') . '
                    ' . (strlen($workspace_calendar_url) ? platform_home_button('Встречи', $workspace_calendar_url, 'secondary') : '') . '
                    ' . (strlen($workspace_create_meeting_url) ? platform_home_button('Создать встречу', $workspace_create_meeting_url, 'secondary') : '') . '
                    ' . platform_home_button('NauDoc', '/docs/', 'secondary', true) . '
                    ' . platform_home_button('Bridge', '/bridge/', 'secondary', true) . '
                </div>
            </div>
        </section>

        <section class="platform-home-section">
            <div class="platform-home-section-header">
                <h2>Состояние контура</h2>
                <p>Ключевые показатели интеграции и состояния платформы.</p>
            </div>
            <div class="platform-home-status-grid">
                ' . platform_home_status_card('Документы с NauDoc', $linked_docs_count, 'Карточки, у которых уже есть официальный URL.', platform_home_entity_url(25)) . '
                ' . platform_home_status_card('Заявки без финального документа', $requests_without_doc_count, 'Записи, которым еще нужен официальный документ.', $linked_requests_url) . '
                ' . platform_home_status_card('Проекты без финального документа', $projects_without_doc_count, 'Проекты, которые еще не закрыты официальным документом.', $linked_projects_url) . '
                ' . platform_home_status_card('Черновики в редакторе', $drafts_count, 'Документы, доступные для совместного редактирования.', $doc_approval_url) . '
            </div>
        </section>

        <section class="platform-home-section platform-home-section-split">
            <div class="platform-home-panel">
                <div class="platform-home-section-header">
                    <h2>Рабочие разделы</h2>
                    <p>Основные модули платформы для ежедневной работы и контроля.</p>
                </div>
                <div class="platform-home-links">
                    ' . platform_home_links_group($admin_work_links) . '
                </div>
            </div>
            <div class="platform-home-panel">
                <div class="platform-home-section-header">
                    <h2>Сопровождение и интеграции</h2>
                    <p>Системные инструменты, администрирование и внешние контуры.</p>
                </div>
                <div class="platform-home-links">
                    ' . platform_home_links_group($admin_system_links) . '
                </div>
            </div>
        </section>
    </div>
    ';
}
else
{
    $document_panel_note = $documents_note;

    if (count($naudoc_profile))
    {
    $user_document_links[] = ['title' => 'Профиль в NauDoc', 'description' => 'Связанный официальный профиль пользователя.', 'url' => $naudoc_profile['profile_url'], 'external' => true];
        $document_panel_note = 'Связанный профиль: ' . htmlspecialchars($naudoc_profile['display_name']) . '. ' . $documents_note;
    }

    if (strlen($onlyoffice_demo_editor_url))
    {
        $user_document_links[] = ['title' => 'ONLYOFFICE', 'description' => 'Сразу открыть редактор на рабочем документе.', 'url' => $onlyoffice_demo_editor_url, 'external' => true];
    }

    echo '
    <div class="platform-home platform-home-user-mode">
        <section class="platform-home-hero platform-home-hero-compact">
            <div class="platform-home-hero-main">
                <span class="platform-home-eyebrow">Пользовательский режим</span>
                <h1>Рабочий кабинет</h1>
                <p>
                    Упрощенный режим для ' . $role_label . ': основные разделы слева, документы через карточку, официальный контур через NauDoc.
                </p>
                <div class="platform-home-hero-actions">
                    ' . platform_home_button('Заявки', platform_home_entity_url(23), 'primary') . '
                    ' . platform_home_button('Документы', platform_home_entity_url(25), 'secondary') . '
                    ' . (strlen($onlyoffice_demo_editor_url) ? platform_home_button('ONLYOFFICE', $onlyoffice_demo_editor_url, 'secondary', true) : '') . '
                    ' . (strlen($docspace_entry_url) ? platform_home_button('DocSpace', $docspace_entry_url, 'secondary') : '') . '
                    ' . (strlen($workspace_entry_url) ? platform_home_button('Workspace', $workspace_entry_url, 'secondary') : '') . '
                    ' . (strlen($workspace_calendar_url) ? platform_home_button('Встречи', $workspace_calendar_url, 'secondary') : '') . '
                    ' . (strlen($workspace_create_meeting_url) ? platform_home_button('Создать встречу', $workspace_create_meeting_url, 'secondary') : '') . '
                    ' . platform_home_button('NauDoc', '/docs/', 'secondary', true) . '
                </div>
            </div>
        </section>

        <section class="platform-home-section platform-home-section-split">
            <div class="platform-home-panel">
                <div class="platform-home-section-header">
                    <h2>Рабочие разделы</h2>
                    <p>Короткие переходы в основные модули без лишних экранов.</p>
                </div>
                <div class="platform-home-links">
                    ' . platform_home_links_group($user_work_links) . '
                </div>
            </div>
            <div class="platform-home-panel">
                <div class="platform-home-section-header">
                    <h2>Документы и согласование</h2>
                    <p>Рабочая карточка, редактор и официальный контур документа.</p>
                </div>
                <div class="platform-home-links">
                    ' . platform_home_links_group($user_document_links) . '
                </div>
                <div class="platform-home-inline-note">' . $document_panel_note . ' Найти документ можно через поиск в списке карточек, а загрузить файл — через кнопку создания карточки и поле "Вложения".</div>
            </div>
        </section>
    </div>
    ';
}
