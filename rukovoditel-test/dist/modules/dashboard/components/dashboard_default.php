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

if (!function_exists('platform_home_card'))
{
    function platform_home_card($title, $description, $buttons = [], $note = '')
    {
        $html = '<section class="platform-home-card">';
        $html .= '<h3>' . $title . '</h3>';
        $html .= '<p>' . $description . '</p>';

        if (count($buttons))
        {
            $html .= '<div class="platform-home-card-actions">';

            foreach ($buttons as $button)
            {
                $html .= platform_home_button(
                    $button['label'],
                    $button['url'],
                    $button['type'] ?? 'primary',
                    $button['external'] ?? false
                );
            }

            $html .= '</div>';
        }

        if (strlen($note))
        {
            $html .= '<div class="platform-home-card-note">' . $note . '</div>';
        }

        $html .= '</section>';

        return $html;
    }
}

if (!function_exists('platform_home_contour_card'))
{
    function platform_home_contour_card($title, $description, $bullets = [], $buttons = [], $variant = 'blue', $note = '')
    {
        $html = '<section class="platform-home-contour-card platform-home-contour-card-' . $variant . '">';
        $html .= '<div class="platform-home-contour-card-head">';
        $html .= '<h3>' . $title . '</h3>';
        $html .= '<p>' . $description . '</p>';
        $html .= '</div>';

        if (count($bullets))
        {
            $html .= '<ul class="platform-home-contour-points">';

            foreach ($bullets as $bullet)
            {
                $html .= '<li>' . $bullet . '</li>';
            }

            $html .= '</ul>';
        }

        if (count($buttons))
        {
            $html .= '<div class="platform-home-card-actions">';

            foreach ($buttons as $button)
            {
                $html .= platform_home_button(
                    $button['label'],
                    $button['url'],
                    $button['type'] ?? 'primary',
                    $button['external'] ?? false
                );
            }

            $html .= '</div>';
        }

        if (strlen($note))
        {
            $html .= '<div class="platform-home-contour-note">' . $note . '</div>';
        }

        $html .= '</section>';

        return $html;
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

$documents_note = 'Чтобы редактировать документ совместно, откройте карточку документа и нажмите кнопку "Открыть документ в редакторе".';
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
$onlyoffice_demo_url = '';
$onlyoffice_demo_item_url = platform_home_entity_url(25);
$naudoc_profile = platform_home_current_naudoc_profile($username);

$doc_field_id = 250;
$request_field_id = 241;
$project_field_id = 230;
$onlyoffice_field_id = (int) $onlyoffice_demo['field_id'];

$linked_docs_count = (int) platform_home_scalar_query("select count(*) from app_entity_25 where length(trim(coalesce(field_{$doc_field_id}, '')))>0");
$requests_without_doc_count = (int) platform_home_scalar_query("select count(*) from app_entity_23 where length(trim(coalesce(field_{$request_field_id}, '')))=0");
$projects_without_doc_count = (int) platform_home_scalar_query("select count(*) from app_entity_21 where length(trim(coalesce(field_{$project_field_id}, '')))=0");
$drafts_count = $onlyoffice_field_id > 0 ? (int) platform_home_scalar_query("select count(*) from app_entity_25 where length(trim(coalesce(field_{$onlyoffice_field_id}, '')))>0") : 0;

if ($onlyoffice_demo['item_id'] > 0 && $onlyoffice_demo['field_id'] > 0 && $onlyoffice_demo['file_id'] > 0)
{
    $onlyoffice_demo_item_url = url_for('items/info', 'path=25-' . $onlyoffice_demo['item_id']);
    $onlyoffice_demo_url = url_for(
        'items/onlyoffice_editor',
        'path=25-' . $onlyoffice_demo['item_id'] . '&action=open&field=' . $onlyoffice_demo['field_id'] . '&file=' . $onlyoffice_demo['file_id']
    );
}

$contour_cards = [];
$contour_cards[] = platform_home_contour_card(
    'Рабочий кабинет',
    'Ежедневная работа сотрудников и руководителей: заявки, проекты, задачи и карточки документов.',
    [
        'Заявки, задачи и проекты',
        'Карточки и база документов',
    ],
    [
        ['label' => 'Заявки', 'url' => platform_home_entity_url(23), 'type' => 'primary'],
        ['label' => 'Документы', 'url' => platform_home_entity_url(25), 'type' => 'secondary'],
    ],
    'blue',
    'Основная навигация по разделам находится слева.'
);

$contour_cards[] = platform_home_contour_card(
    'NauDoc',
    'Официальный контур для регистрации, маршрутов, версий и архива документов.',
    [
        'Регистрация и архив',
        'Версии и маршруты',
    ],
    [
        ['label' => 'Открыть NauDoc', 'url' => '/docs/', 'type' => 'primary', 'external' => true],
    ],
    'orange'
);

$onlyoffice_card_buttons = [
    ['label' => 'Открыть карточки документов', 'url' => platform_home_entity_url(25), 'type' => 'primary'],
];

if ($onlyoffice_demo['item_id'] > 0)
{
    $onlyoffice_card_buttons[] = ['label' => 'Открыть демо-документ', 'url' => $onlyoffice_demo_item_url, 'type' => 'secondary'];
}

$contour_cards[] = platform_home_contour_card(
    'Редактор документов',
    'ONLYOFFICE для совместной работы над черновиком документа в браузере.',
    [
        'Совместная работа в браузере',
        'Запуск из карточки документа',
    ],
    $onlyoffice_card_buttons,
    'dark',
    'Откройте карточку документа и нажмите кнопку редактора.'
);

$primary_cards = [];
$primary_cards[] = platform_home_card(
    'Заявки на обслуживание',
    'Оформление заявок, контроль исполнения и связь с карточкой документа.',
    [
        ['label' => 'Открыть заявки', 'url' => platform_home_entity_url(23), 'type' => 'primary'],
    ]
);

if (!$is_office)
{
    $primary_cards[] = platform_home_card(
        'Поручения и задачи',
        'Мои рабочие поручения и контроль исполнения.',
        [
            ['label' => 'Открыть задачи', 'url' => $tasks_url, 'type' => 'primary'],
        ]
    );
}

$primary_cards[] = platform_home_card(
    'Проекты',
    'Проекты, связанные документы, контроль сроков и работа по этапам.',
    [
        ['label' => 'Открыть проекты', 'url' => platform_home_entity_url(21), 'type' => 'primary'],
    ]
);

if (($is_admin || $is_manager || $is_employee) && strlen($discussions_url))
{
    $primary_cards[] = platform_home_card(
        'Рабочие обсуждения',
        'Внутренние обсуждения по рабочим вопросам внутри платформы.',
        [
            ['label' => 'Открыть обсуждения', 'url' => $discussions_url, 'type' => 'primary'],
        ]
    );
}

$primary_cards[] = platform_home_card(
    'Карточки документов',
    'Карточка документа с быстрым доступом к редактору, статусу и официальному контуру.',
    [
        ['label' => 'Открыть карточки', 'url' => platform_home_entity_url(25), 'type' => 'primary'],
        ['label' => 'Открыть NauDoc', 'url' => '/docs/', 'type' => 'secondary', 'external' => true],
    ],
    $documents_note
);

$primary_cards[] = platform_home_card(
    'База документов',
    'Реестр готовых документов, шаблонов и материалов.',
    [
        ['label' => 'Открыть базу документов', 'url' => platform_home_entity_url(26), 'type' => 'primary'],
    ]
);

$primary_cards[] = platform_home_card(
    'Обеспечение',
    'МТЗ и сопутствующие процессы обеспечения подразделений.',
    [
        ['label' => 'Открыть МТЗ', 'url' => platform_home_entity_url(27), 'type' => 'primary'],
    ]
);

$integration_profile_html = '';
if (count($naudoc_profile))
{
    $integration_profile_html = '
        <section class="platform-home-profile-card">
            <div class="platform-home-profile-heading">Связанный профиль</div>
            <div class="platform-home-profile-name">' . htmlspecialchars($naudoc_profile['display_name']) . '</div>
            <p>Текущий пользователь связан с официальным профилем в NauDoc. Можно быстро перейти в профиль и личную папку.</p>
            <div class="platform-home-card-actions">
                ' . platform_home_button('Профиль NauDoc', $naudoc_profile['profile_url'], 'primary', true) . '
                ' . platform_home_button('Личная папка', $naudoc_profile['folder_url'], 'secondary', true) . '
            </div>
        </section>
    ';
}
else
{
    $integration_profile_html = '
        <section class="platform-home-profile-card platform-home-profile-card-muted">
            <div class="platform-home-profile-heading">Связанный профиль</div>
            <div class="platform-home-profile-name">Профиль NauDoc пока не найден</div>
            <p>Рабочий кабинет открыт, но для этого пользователя еще не подтверждена связь с карточкой в NauDoc.</p>
            <div class="platform-home-card-actions">
                ' . platform_home_button('Открыть NauDoc', '/docs/', 'secondary', true) . '
            </div>
        </section>
    ';
}

$admin_system_cards = [
    platform_home_card(
        'Пользователи и роли',
        'Пользователи системы, группы доступа и роли.',
        [
            ['label' => 'Пользователи', 'url' => platform_home_entity_url(1), 'type' => 'primary'],
            ['label' => 'Группы доступа', 'url' => url_for('users_groups/users_groups'), 'type' => 'secondary'],
        ]
    ),
    platform_home_card(
        'Настройки и структура',
        'Настройки приложения, сущности, меню и конфигурация.',
        [
            ['label' => 'Настройки приложения', 'url' => url_for('configuration/application'), 'type' => 'primary'],
            ['label' => 'Сущности приложения', 'url' => url_for('entities/entities'), 'type' => 'secondary'],
        ]
    ),
    platform_home_card(
        'Логи и резервные копии',
        'Журналы, резервные копии и сопровождение платформы.',
        [
            ['label' => 'Логи', 'url' => url_for('logs/settings'), 'type' => 'primary'],
            ['label' => 'Резервные копии', 'url' => url_for('tools/db_backup'), 'type' => 'secondary'],
        ]
    ),
    platform_home_card(
        'Интеграции',
        'Рабочие внешние контуры и интеграционный слой.',
        [
            ['label' => 'NauDoc', 'url' => '/docs/', 'type' => 'primary', 'external' => true],
            ['label' => 'Bridge', 'url' => '/bridge/', 'type' => 'secondary', 'external' => true],
            ['label' => 'Карточки документов', 'url' => platform_home_entity_url(25), 'type' => 'secondary'],
        ]
    ),
];

$user_work_cards = [
    platform_home_card(
        'Заявки',
        'Сервисные обращения и рабочие запросы.',
        [
            ['label' => 'Открыть заявки', 'url' => platform_home_entity_url(23), 'type' => 'primary'],
        ]
    ),
    platform_home_card(
        'Проекты',
        'Проекты, инициативы и связанные документы.',
        [
            ['label' => 'Открыть проекты', 'url' => platform_home_entity_url(21), 'type' => 'primary'],
        ]
    ),
    platform_home_card(
        'Документы',
        'Карточки документов, черновики и переход в официальный контур.',
        [
            ['label' => 'Карточки документов', 'url' => platform_home_entity_url(25), 'type' => 'primary'],
            ['label' => 'NauDoc', 'url' => '/docs/', 'type' => 'secondary', 'external' => true],
        ],
        $documents_note
    ),
    platform_home_card(
        'База документов',
        'Шаблоны, инструкции и готовые материалы.',
        [
            ['label' => 'Открыть базу', 'url' => platform_home_entity_url(26), 'type' => 'primary'],
        ]
    ),
    platform_home_card(
        'МТЗ',
        'Материально-техническое обеспечение и связанные заявки.',
        [
            ['label' => 'Открыть МТЗ', 'url' => platform_home_entity_url(27), 'type' => 'primary'],
        ]
    ),
];

if (!$is_office)
{
    array_splice($user_work_cards, 1, 0, [
        platform_home_card(
            'Задачи',
            'Мои поручения и задачи без лишних разделов.',
            [
                ['label' => 'Открыть задачи', 'url' => $tasks_url, 'type' => 'primary'],
            ]
        ),
    ]);
}

if ($is_manager)
{
    $user_work_cards[] = platform_home_card(
        'Контроль руководителя',
        'Быстрые отчеты по проектам, согласованию и рискам по документам.',
        [
            ['label' => 'Проекты на контроле', 'url' => platform_home_named_report_url(21, 'Проекты на контроле', platform_home_entity_url(21)), 'type' => 'primary'],
            ['label' => 'Документы на согласовании', 'url' => $doc_approval_url, 'type' => 'secondary'],
        ]
    );
}

if ($is_admin)
{
    echo '
    <div class="platform-home platform-home-admin-mode">
        <section class="platform-home-hero">
            <div class="platform-home-hero-main">
                <span class="platform-home-eyebrow">Административный контур</span>
                <h1>Центр управления платформой</h1>
                <p>
                    Полный режим сопровождения платформы: рабочие разделы, настройки, логи, резервные копии и интеграции.
                </p>
                <div class="platform-home-hero-actions">
                    ' . platform_home_button('Рабочие документы', platform_home_entity_url(25), 'primary') . '
                    ' . platform_home_button('NauDoc', '/docs/', 'secondary', true) . '
                    ' . platform_home_button('Bridge', '/bridge/', 'secondary', true) . '
                </div>
            </div>
            <div class="platform-home-hero-side">
                <div class="platform-home-callout">
                    <div class="platform-home-callout-title">Что есть в админском режиме</div>
                    <ul>
                        <li>Настройки, пользователи, роли и сущности.</li>
                        <li>Логи, резервные копии и интеграционный контроль.</li>
                        <li>Полный доступ к рабочим модулям и отчетам.</li>
                    </ul>
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

        <section class="platform-home-section">
            <div class="platform-home-section-header">
                <h2>Системные разделы</h2>
                <p>Инструменты сопровождения и управления.</p>
            </div>
            <div class="platform-home-grid">
                ' . implode('', $admin_system_cards) . '
            </div>
        </section>

        <section class="platform-home-section">
            <div class="platform-home-section-header">
                <h2>Рабочий контур</h2>
                <p>Основные рабочие модули доступны и в админском режиме.</p>
            </div>
            <div class="platform-home-grid">
                ' . implode('', $primary_cards) . '
            </div>
        </section>

        <section class="platform-home-section">
            <div class="platform-home-section-header">
                <h2>Связанный профиль</h2>
                <p>Связка текущего администратора с NauDoc.</p>
            </div>
            ' . $integration_profile_html . '
        </section>
    </div>
    ';
}
else
{
    echo '
    <div class="platform-home platform-home-user-mode">
        <section class="platform-home-hero">
            <div class="platform-home-hero-main">
                <span class="platform-home-eyebrow">Пользовательский режим</span>
                <h1>Рабочий кабинет</h1>
                <p>
                    Упрощенный режим для ' . $role_label . ': только рабочие разделы, документы и нужные переходы без административного шума.
                </p>
                <div class="platform-home-hero-actions">
                    ' . platform_home_button('Заявки', platform_home_entity_url(23), 'primary') . '
                    ' . platform_home_button('Документы', platform_home_entity_url(25), 'secondary') . '
                    ' . platform_home_button('NauDoc', '/docs/', 'secondary', true) . '
                </div>
            </div>
            <div class="platform-home-hero-side">
                <div class="platform-home-callout">
                    <div class="platform-home-callout-title">Как работать</div>
                    <ul>
                        <li>Основные разделы находятся слева.</li>
                        <li>Официальный документ и архив открываются через NauDoc.</li>
                        <li>Редактирование документа запускается из карточки.</li>
                    </ul>
                </div>
            </div>
        </section>

        <section class="platform-home-section">
            <div class="platform-home-section-header">
                <h2>Рабочие разделы</h2>
                <p>Основные модули для ежедневной работы.</p>
            </div>
            <div class="platform-home-grid">
                ' . implode('', $user_work_cards) . '
            </div>
        </section>

        <section class="platform-home-section">
            <div class="platform-home-section-header">
                <h2>Основные контуры</h2>
                <p>Рабочий кабинет, официальный контур и редактор.</p>
            </div>
            <div class="platform-home-grid platform-home-grid-contours">
                ' . implode('', $contour_cards) . '
            </div>
        </section>

        <section class="platform-home-section">
            <div class="platform-home-section-header">
                <h2>Связанный профиль</h2>
                <p>Связка текущего пользователя с NauDoc.</p>
            </div>
            ' . $integration_profile_html . '
        </section>
    </div>
    ';
}
