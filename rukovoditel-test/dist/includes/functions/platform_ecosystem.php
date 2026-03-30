<?php

if(!function_exists('platform_public_base_url'))
{
    function platform_public_base_url()
    {
        if(function_exists('platform_sync_public_base_url'))
        {
            return rtrim(platform_sync_public_base_url(), '/') . '/';
        }

        $base = trim((string) getenv('PLATFORM_PUBLIC_BASE_URL'));
        return rtrim($base ?: 'https://localhost:18443', '/') . '/';
    }
}

if(!function_exists('platform_env_truthy'))
{
    function platform_env_truthy($name, $default = false)
    {
        $value = getenv($name);

        if($value === false || $value === '')
        {
            return (bool) $default;
        }

        return in_array(strtolower(trim((string) $value)), ['1', 'true', 'yes', 'on'], true);
    }
}

if(!function_exists('platform_current_user_group_id'))
{
    function platform_current_user_group_id()
    {
        if((defined('IS_CRON') && IS_CRON) || PHP_SAPI === 'cli')
        {
            return 0;
        }

        global $app_user;

        if(!isset($app_user) || !is_array($app_user))
        {
            return 0;
        }

        return (int) ($app_user['group_id'] ?? 0);
    }
}

if(!function_exists('platform_user_has_group_access'))
{
    function platform_user_has_group_access($allowed_groups)
    {
        if((defined('IS_CRON') && IS_CRON) || PHP_SAPI === 'cli')
        {
            return true;
        }

        if(!is_array($allowed_groups) || !count($allowed_groups))
        {
            return false;
        }

        $group_id = platform_current_user_group_id();
        $normalized = array_map('intval', $allowed_groups);

        return in_array($group_id, $normalized, true);
    }
}

if(!function_exists('platform_user_can_open_naudoc'))
{
    function platform_user_can_open_naudoc()
    {
        return platform_user_has_group_access([0, 7]);
    }
}

if(!function_exists('platform_user_can_open_docspace'))
{
    function platform_user_can_open_docspace()
    {
        return platform_user_has_group_access([0, 4, 5, 7, 8]);
    }
}

if(!function_exists('platform_user_can_open_workspace'))
{
    function platform_user_can_open_workspace()
    {
        return platform_user_has_group_access([0, 4, 5, 6, 7, 8]);
    }
}

if(!function_exists('platform_user_can_open_workspace_module'))
{
    function platform_user_can_open_workspace_module($module)
    {
        $module = strtolower(trim((string) $module));

        if(!platform_user_can_open_workspace())
        {
            return false;
        }

        if($module === 'community')
        {
            return platform_workspace_module_enabled('community') && platform_user_has_group_access([0, 4, 7]);
        }

        if($module === 'calendar' || !strlen($module))
        {
            return true;
        }

        return false;
    }
}

if(!function_exists('platform_user_can_create_meeting'))
{
    function platform_user_can_create_meeting()
    {
        return platform_user_can_open_workspace_module('calendar');
    }
}

if(!function_exists('platform_service_enabled'))
{
    function platform_service_enabled($service)
    {
        $service = strtolower(trim((string) $service));
        $env_key = strtoupper(preg_replace('/[^a-z0-9]+/i', '_', $service)) . '_ENABLED';
        $default = in_array($service, ['docspace', 'workspace'], true);

        return platform_env_truthy($env_key, $default);
    }
}

if(!function_exists('platform_service_public_url'))
{
    function platform_service_public_url($service)
    {
        $service = strtolower(trim((string) $service));
        $env_key = strtoupper(preg_replace('/[^a-z0-9]+/i', '_', $service)) . '_PUBLIC_URL';
        $configured_url = trim((string) getenv($env_key));

        if(strlen($configured_url))
        {
            return rtrim($configured_url, '/') . '/';
        }

        return platform_public_base_url() . rawurlencode($service) . '/';
    }
}

if(!function_exists('platform_service_target_url'))
{
    function platform_service_target_url($service)
    {
        $service = strtolower(trim((string) $service));
        $env_key = strtoupper(preg_replace('/[^a-z0-9]+/i', '_', $service)) . '_TARGET_URL';
        $configured_url = trim((string) getenv($env_key));

        if(!strlen($configured_url))
        {
            return '';
        }

        return filter_var($configured_url, FILTER_VALIDATE_URL) ? $configured_url : '';
    }
}

if(!function_exists('platform_normalize_absolute_url'))
{
    function platform_normalize_absolute_url($value)
    {
        $value = trim((string) $value);

        if(!strlen($value))
        {
            return '';
        }

        return rtrim($value, '/');
    }
}

if(!function_exists('platform_url_with_query'))
{
    function platform_url_with_query($url, $params = [])
    {
        $url = trim((string) $url);

        if(!strlen($url) || !is_array($params) || !count($params))
        {
            return $url;
        }

        $query = http_build_query($params);

        if(!strlen($query))
        {
            return $url;
        }

        return $url . (strpos($url, '?') === false ? '?' : '&') . $query;
    }
}

if(!function_exists('platform_urls_match'))
{
    function platform_urls_match($left, $right)
    {
        $left = platform_normalize_absolute_url($left);
        $right = platform_normalize_absolute_url($right);

        return strlen($left) && strlen($right) && strcasecmp($left, $right) === 0;
    }
}

if(!function_exists('platform_field_id_by_type'))
{
    function platform_field_id_by_type($entity_id, $field_type)
    {
        if(function_exists('platform_sync_field_id_by_type'))
        {
            return platform_sync_field_id_by_type($entity_id, $field_type);
        }

        return 0;
    }
}

if(!function_exists('platform_field_id_by_name'))
{
    function platform_field_id_by_name($entity_id, $field_name, $field_type = '')
    {
        if(function_exists('platform_sync_field_id_by_name'))
        {
            return platform_sync_field_id_by_name($entity_id, $field_name, $field_type);
        }

        return 0;
    }
}

if(!function_exists('platform_choice_name_by_value'))
{
    function platform_choice_name_by_value($field_id, $value)
    {
        $field_id = (int) $field_id;
        $value = trim((string) $value);

        if($field_id <= 0 || !strlen($value))
        {
            return '';
        }

        if(ctype_digit($value))
        {
            $choice = db_fetch_array(db_query(
                "select name from app_fields_choices where fields_id='" . db_input($field_id) . "' and id='" . db_input($value) . "' limit 1"
            ));

            if($choice && isset($choice['name']))
            {
                return trim((string) $choice['name']);
            }
        }

        return $value;
    }
}

if(!function_exists('platform_item_dropdown_choice_name'))
{
    function platform_item_dropdown_choice_name($entity_id, $item, $field_name)
    {
        if(!is_array($item) || $entity_id <= 0)
        {
            return '';
        }

        $field_id = platform_field_id_by_name($entity_id, $field_name, 'fieldtype_dropdown');

        if($field_id <= 0 || !isset($item['field_' . $field_id]))
        {
            return '';
        }

        return platform_choice_name_by_value($field_id, $item['field_' . $field_id]);
    }
}

if(!function_exists('platform_docspace_room_type'))
{
    function platform_docspace_room_type($entity_id, $item)
    {
        return platform_item_dropdown_choice_name($entity_id, $item, 'Сценарий DocSpace');
    }
}

if(!function_exists('platform_workspace_module'))
{
    function platform_workspace_module($entity_id, $item)
    {
        $module = platform_item_dropdown_choice_name($entity_id, $item, 'Модуль Workspace');

        return platform_workspace_module_enabled($module) ? $module : '';
    }
}

if(!function_exists('platform_docspace_room_label'))
{
    function platform_docspace_room_label($value)
    {
        $value = strtolower(trim((string) $value));

        $labels = [
            'collaboration room' => 'Collaboration room',
            'public room' => 'Public room',
            'form filling room' => 'Form filling room',
        ];

        return $labels[$value] ?? trim((string) $value);
    }
}

if(!function_exists('platform_docspace_room_key'))
{
    function platform_docspace_room_key($value)
    {
        $value = strtolower(trim((string) $value));

        $keys = [
            'collaboration room' => 'collaboration_room',
            'public room' => 'public_room',
            'form filling room' => 'form_filling_room',
        ];

        return $keys[$value] ?? preg_replace('/[^a-z0-9]+/i', '_', $value);
    }
}

if(!function_exists('platform_workspace_module_label'))
{
    function platform_workspace_module_label($value)
    {
        $value = strtolower(trim((string) $value));

        $labels = [
            'calendar' => 'Calendar',
            'community' => 'Community',
        ];

        if(isset($labels[$value]) && !platform_workspace_module_enabled($value))
        {
            return '';
        }

        return $labels[$value] ?? trim((string) $value);
    }
}

if(!function_exists('platform_workspace_module_key'))
{
    function platform_workspace_module_key($value)
    {
        $value = strtolower(trim((string) $value));

        $keys = [
            'calendar' => 'calendar',
            'community' => 'community',
        ];

        return $keys[$value] ?? preg_replace('/[^a-z0-9]+/i', '_', $value);
    }
}

if(!function_exists('platform_workspace_module_enabled'))
{
    function platform_workspace_module_enabled($module)
    {
        $module = strtolower(trim((string) $module));

        if(!strlen($module))
        {
            return false;
        }

        if($module === 'calendar')
        {
            return true;
        }

        if($module === 'community')
        {
            return platform_env_truthy('DOCFLOW_WORKSPACE_WAVE1_ENABLE_COMMUNITY', false);
        }

        return false;
    }
}

if(!function_exists('platform_item_title'))
{
    function platform_item_title($entity_id, $item)
    {
        $title_field_id = platform_field_id_by_type($entity_id, 'fieldtype_input');

        if($title_field_id > 0 && is_array($item) && isset($item['field_' . $title_field_id]))
        {
            return trim((string) $item['field_' . $title_field_id]);
        }

        return '';
    }
}

if(!function_exists('platform_item_url'))
{
    function platform_item_url($entity_id, $item_id)
    {
        if($entity_id <= 0 || $item_id <= 0 || !function_exists('url_for'))
        {
            return '';
        }

        return url_for('items/info', 'path=' . (int) $entity_id . '-' . (int) $item_id);
    }
}

if(!function_exists('platform_first_onlyoffice_demo'))
{
    function platform_onlyoffice_field_id($entity_id)
    {
        $preferred_names = ['Совместное редактирование', 'Рабочий черновик'];

        foreach($preferred_names as $field_name)
        {
            $field_id = platform_field_id_by_name($entity_id, $field_name, 'fieldtype_onlyoffice');

            if($field_id > 0)
            {
                return $field_id;
            }
        }

        return platform_field_id_by_type($entity_id, 'fieldtype_onlyoffice');
    }
}

if(!function_exists('platform_first_onlyoffice_demo'))
{
    function platform_first_onlyoffice_demo($entity_id = 25)
    {
        $field_id = platform_onlyoffice_field_id($entity_id);

        if($field_id <= 0)
        {
            return ['item_id' => 0, 'field_id' => 0, 'file_id' => 0];
        }

        $item_query = db_query(
            "select id, field_" . (int) $field_id . " as file_ids from app_entity_" . (int) $entity_id .
            " where length(field_" . (int) $field_id . ")>0 order by id limit 1"
        );

        if(!$item = db_fetch_array($item_query))
        {
            return ['item_id' => 0, 'field_id' => $field_id, 'file_id' => 0];
        }

        $file_ids = array_filter(array_map('trim', explode(',', $item['file_ids'])));

        return [
            'item_id' => (int) $item['id'],
            'field_id' => (int) $field_id,
            'file_id' => count($file_ids) ? (int) $file_ids[0] : 0,
        ];
    }
}

if(!function_exists('platform_item_onlyoffice_url'))
{
    function platform_item_onlyoffice_url($entity_id, $item)
    {
        if(!is_array($item) || !isset($item['id']) || $entity_id <= 0)
        {
            return '';
        }

        $field_id = platform_onlyoffice_field_id($entity_id);

        if($field_id <= 0 || !isset($item['field_' . $field_id]))
        {
            return '';
        }

        $file_ids = array_filter(array_map('trim', explode(',', (string) $item['field_' . $field_id])));
        $file_id = count($file_ids) ? (int) $file_ids[0] : 0;

        if($file_id <= 0 || !function_exists('url_for'))
        {
            return '';
        }

        return url_for(
            'items/onlyoffice_editor',
            'path=' . (int) $entity_id . '-' . (int) $item['id'] . '&action=open&field=' . (int) $field_id . '&file=' . $file_id
        );
    }
}

if(!function_exists('platform_item_onlyoffice_create_url'))
{
    function platform_item_onlyoffice_create_url($entity_id, $item, $file_type = 'docx')
    {
        if(!is_array($item) || !isset($item['id']) || $entity_id <= 0 || !function_exists('url_for'))
        {
            return '';
        }

        $file_type = strtolower(trim((string) $file_type));
        if(!in_array($file_type, ['docx', 'xlsx'], true))
        {
            return '';
        }

        $field_id = platform_onlyoffice_field_id($entity_id);

        if($field_id <= 0)
        {
            return '';
        }

        return url_for(
            'items/onlyoffice',
            'path=' . (int) $entity_id . '-' . (int) $item['id'] .
            '&action=create_blank&field_id=' . (int) $field_id .
            '&file_type=' . rawurlencode($file_type) .
            '&redirect=editor'
        );
    }
}

if(!function_exists('platform_item_naudoc_url'))
{
    function platform_item_naudoc_url($entity_id, $item)
    {
        if(!is_array($item) || $entity_id <= 0)
        {
            return '';
        }

        $field_id = platform_field_id_by_name($entity_id, 'Ссылка на NauDoc', 'fieldtype_input_url');

        if($field_id <= 0 || !isset($item['field_' . $field_id]))
        {
            return '';
        }

        return trim((string) $item['field_' . $field_id]);
    }
}

if(!function_exists('platform_ecosystem_url'))
{
    function platform_ecosystem_url($service, $entity_id = 0, $item_id = 0, $absolute = false, $extra_params = [])
    {
        $params = ['service' => $service];

        if($entity_id > 0 && $item_id > 0)
        {
            $params['entity_id'] = (int) $entity_id;
            $params['item_id'] = (int) $item_id;
        }

        if(is_array($extra_params))
        {
            foreach($extra_params as $key => $value)
            {
                if($value === '' || $value === null)
                {
                    continue;
                }

                $params[$key] = $value;
            }
        }

        $query = http_build_query($params);

        if(!$absolute && function_exists('url_for'))
        {
            return url_for('dashboard/ecosystem', $query);
        }

        return platform_public_base_url() . 'index.php?module=dashboard/ecosystem&' . $query;
    }
}

if(!function_exists('platform_service_entry_url'))
{
    function platform_service_entry_url($service, $entity_id = 0, $item_id = 0, $extra_params = [])
    {
        if(!platform_service_enabled($service))
        {
            return '';
        }

        $service = strtolower(trim((string) $service));

        if($service === 'docspace' && !platform_user_can_open_docspace())
        {
            return '';
        }

        if($service === 'workspace' && !platform_user_can_open_workspace())
        {
            return '';
        }

        if(strlen(platform_service_target_url($service)))
        {
            $params = [];

            if($entity_id > 0 && $item_id > 0)
            {
                $params['entity_id'] = (int) $entity_id;
                $params['item_id'] = (int) $item_id;
            }

            if(is_array($extra_params))
            {
                foreach($extra_params as $key => $value)
                {
                    if($value === '' || $value === null)
                    {
                        continue;
                    }

                    $params[$key] = $value;
                }
            }

            return platform_url_with_query(platform_service_public_url($service), $params);
        }

        return platform_ecosystem_url($service, $entity_id, $item_id, false, $extra_params);
    }
}

if(!function_exists('platform_service_module_target_url'))
{
    function platform_service_module_target_url($service, $module)
    {
        $service = strtolower(trim((string) $service));
        $module = strtolower(trim((string) $module));

        if(!strlen($service) || !strlen($module))
        {
            return '';
        }

        if($service === 'workspace' && !platform_workspace_module_enabled($module))
        {
            return '';
        }

        $env_key = strtoupper(preg_replace('/[^a-z0-9]+/i', '_', $service . '_' . $module)) . '_TARGET_URL';
        $configured_url = trim((string) getenv($env_key));

        if(!strlen($configured_url))
        {
            return '';
        }

        return filter_var($configured_url, FILTER_VALIDATE_URL) ? $configured_url : '';
    }
}

if(!function_exists('platform_service_module_entry_url'))
{
    function platform_service_module_entry_url($service, $module, $entity_id = 0, $item_id = 0)
    {
        if(!platform_service_enabled($service))
        {
            return '';
        }

        $service = strtolower(trim((string) $service));
        $module = strtolower(trim((string) $module));
        $extra_params = ['workspace_module' => $module];

        if($service === 'docspace')
        {
            $extra_params = ['room_type' => $module];
        }

        if($service === 'docspace' && !platform_user_can_open_docspace())
        {
            return '';
        }

        if($service === 'workspace' && !platform_workspace_module_enabled($module))
        {
            return '';
        }

        if($service === 'workspace' && !platform_user_can_open_workspace_module($module))
        {
            return '';
        }

        $module_target = platform_service_module_target_url($service, $module);

        if(strlen($module_target))
        {
            return $module_target;
        }

        if(strlen(platform_service_target_url($service)))
        {
            return platform_service_entry_url($service, $entity_id, $item_id, $extra_params);
        }

        return platform_ecosystem_url($service, $entity_id, $item_id, false, $extra_params);
    }
}

if(!function_exists('platform_workspace_create_meeting_url'))
{
    function platform_workspace_create_meeting_url($entity_id = 0, $item_id = 0)
    {
        if(!platform_service_enabled('workspace') || !platform_user_can_create_meeting())
        {
            return '';
        }

        $extra_params = [
            'workspace_module' => 'calendar',
            'intent' => 'create_meeting',
        ];

        $calendar_target = platform_service_module_target_url('workspace', 'calendar');

        if(strlen($calendar_target))
        {
            return platform_url_with_query($calendar_target, ['intent' => 'create_meeting']);
        }

        if(strlen(platform_service_target_url('workspace')))
        {
            return platform_service_entry_url('workspace', $entity_id, $item_id, $extra_params);
        }

        return platform_ecosystem_url('workspace', $entity_id, $item_id, false, $extra_params);
    }
}

if(!function_exists('platform_service_is_shell_url'))
{
    function platform_service_is_shell_url($service, $url, $entity_id = 0, $item_id = 0)
    {
        $url = trim((string) $url);

        if(!filter_var($url, FILTER_VALIDATE_URL))
        {
            return false;
        }

        return platform_urls_match($url, platform_service_public_url($service))
            || platform_urls_match($url, platform_ecosystem_url($service, $entity_id, $item_id, true));
    }
}

if(!function_exists('platform_document_route_specs'))
{
    function platform_document_route_specs()
    {
        return [
            'Входящая регистрация' => [
                'wave_label' => 'Боевой маршрут первой волны',
                'summary' => 'Канцелярский маршрут для входящих документов и первичного учета.',
                'creator_roles' => 'Канцелярия или регистратура',
                'approval_roles' => 'Формальное согласование не требуется',
                'registration_roles' => 'Канцелярия',
                'draft_system' => 'Rukovoditel + ONLYOFFICE Docs',
                'official_system' => 'NauDoc',
                'status_flow' => 'Черновик -> На регистрации -> Зарегистрирован -> На ознакомлении -> Архивирован',
            ],
            'Внутренний приказ / распоряжение' => [
                'wave_label' => 'Боевой маршрут первой волны',
                'summary' => 'Внутренний приказ подразделения с согласованием, утверждением и ознакомлением.',
                'creator_roles' => 'Заведующий отделением или уполномоченный сотрудник',
                'approval_roles' => 'Заведующий отделением / руководитель подразделения',
                'registration_roles' => 'Канцелярия при обязательной регистрации',
                'draft_system' => 'Rukovoditel + ONLYOFFICE Docs',
                'official_system' => 'NauDoc',
                'status_flow' => 'Черновик -> На согласовании -> На утверждении -> Подписан -> На ознакомлении -> Архивирован',
            ],
            'Пациент / направление / выписка' => [
                'wave_label' => 'Боевой маршрут первой волны',
                'summary' => 'Пациентский документ с участием врача, координатора отделения и регистрационного контура.',
                'creator_roles' => 'Врач или старшая медсестра / координатор',
                'approval_roles' => 'Заведующий отделением',
                'registration_roles' => 'Регистратура и канцелярия',
                'draft_system' => 'Rukovoditel + ONLYOFFICE Docs',
                'official_system' => 'NauDoc',
                'status_flow' => 'Черновик -> На согласовании -> На утверждении -> Подписан -> На регистрации -> Зарегистрирован -> Архивирован',
            ],
            'Медицинская документация отделения' => [
                'wave_label' => 'Боевой маршрут первой волны',
                'summary' => 'Клинический документ отделения с рабочим черновиком в контуре подразделения и официальным статусом в NauDoc.',
                'creator_roles' => 'Врач или старшая медсестра / координатор',
                'approval_roles' => 'Заведующий отделением',
                'registration_roles' => 'Канцелярия при обязательной регистрации',
                'draft_system' => 'Rukovoditel + ONLYOFFICE Docs',
                'official_system' => 'NauDoc',
                'status_flow' => 'Черновик -> На согласовании -> На утверждении -> Подписан -> На регистрации -> Зарегистрирован -> Архивирован',
            ],
        ];
    }
}

if(!function_exists('platform_document_route_spec'))
{
    function platform_document_route_spec($route_label)
    {
        $route_label = trim((string) $route_label);
        $specs = platform_document_route_specs();

        return $specs[$route_label] ?? [];
    }
}

if(!function_exists('platform_document_route_summary'))
{
    function platform_document_route_summary($entity_id, $item)
    {
        if((int) $entity_id !== 25 || !is_array($item))
        {
            return [];
        }

        $route_label = platform_item_dropdown_choice_name($entity_id, $item, 'Маршрут документа');
        if(!strlen($route_label))
        {
            return [];
        }

        $spec = platform_document_route_spec($route_label);
        if(!count($spec))
        {
            return [];
        }

        return array_merge([
            'route_label' => $route_label,
            'status_label' => platform_item_dropdown_choice_name($entity_id, $item, 'Статус документа'),
            'registration_number' => trim((string) ($item['field_' . platform_field_id_by_name($entity_id, 'Регистрационный номер', 'fieldtype_input')] ?? '')),
        ], $spec);
    }
}

if(!function_exists('platform_item_ecosystem_links'))
{
    function platform_item_ecosystem_links($entity_id, $item)
    {
        $item_id = 0;
        if(is_array($item) && isset($item['id']))
        {
            $item_id = (int) $item['id'];
        }

        $docspace_field_id = platform_field_id_by_name($entity_id, 'Комната DocSpace', 'fieldtype_input_url');
        $workspace_field_id = platform_field_id_by_name($entity_id, 'Сервис Workspace', 'fieldtype_input_url');

        $docspace_url = '';
        $workspace_url = '';
        $docspace_room_type = platform_docspace_room_type($entity_id, $item);
        $workspace_module = platform_workspace_module($entity_id, $item);
        $docspace_room_key = platform_docspace_room_key($docspace_room_type);
        $workspace_module_key = platform_workspace_module_key($workspace_module);

        if($docspace_field_id > 0 && is_array($item) && isset($item['field_' . $docspace_field_id]))
        {
            $docspace_url = trim((string) $item['field_' . $docspace_field_id]);
        }

        if($workspace_field_id > 0 && is_array($item) && isset($item['field_' . $workspace_field_id]))
        {
            $workspace_url = trim((string) $item['field_' . $workspace_field_id]);
        }

        $links = [
            'item_title' => platform_item_title($entity_id, $item),
            'item_url' => platform_item_url($entity_id, $item_id),
            'onlyoffice_url' => platform_item_onlyoffice_url($entity_id, $item),
            'onlyoffice_create_doc_url' => platform_item_onlyoffice_create_url($entity_id, $item, 'docx'),
            'onlyoffice_create_sheet_url' => platform_item_onlyoffice_create_url($entity_id, $item, 'xlsx'),
            'naudoc_url' => platform_user_can_open_naudoc() ? platform_item_naudoc_url($entity_id, $item) : '',
            'docspace_url' => $docspace_url,
            'workspace_url' => $workspace_url,
            'docspace_room_type' => $docspace_room_type,
            'docspace_room_key' => $docspace_room_key,
            'docspace_room_label' => platform_docspace_room_label($docspace_room_type),
            'workspace_module' => $workspace_module,
            'workspace_module_key' => $workspace_module_key,
            'workspace_module_label' => platform_workspace_module_label($workspace_module),
            'docspace_entry_url' => '',
            'workspace_entry_url' => '',
            'workspace_calendar_url' => platform_service_module_entry_url('workspace', 'calendar', $entity_id, $item_id),
            'workspace_create_meeting_url' => platform_workspace_create_meeting_url($entity_id, $item_id),
            'workspace_community_url' => platform_service_module_entry_url('workspace', 'community', $entity_id, $item_id),
        ];

        if(platform_service_enabled('docspace'))
        {
            if(filter_var($docspace_url, FILTER_VALIDATE_URL) && !platform_service_is_shell_url('docspace', $docspace_url, $entity_id, $item_id))
            {
                $links['docspace_entry_url'] = $docspace_url;
            }
            elseif(strlen($docspace_room_key))
            {
                $links['docspace_entry_url'] = platform_service_module_entry_url('docspace', $docspace_room_key, $entity_id, $item_id);
            }
            else
            {
                $links['docspace_entry_url'] = platform_service_entry_url('docspace', $entity_id, $item_id);
            }
        }

        if(platform_service_enabled('workspace'))
        {
            if(filter_var($workspace_url, FILTER_VALIDATE_URL) && !platform_service_is_shell_url('workspace', $workspace_url, $entity_id, $item_id))
            {
                $links['workspace_entry_url'] = $workspace_url;

                if(strcasecmp($links['workspace_module_label'], 'Calendar') === 0)
                {
                    $links['workspace_calendar_url'] = $workspace_url;
                }
                elseif(strcasecmp($links['workspace_module_label'], 'Community') === 0)
                {
                    $links['workspace_community_url'] = $workspace_url;
                }
            }
            elseif(strlen($workspace_module_key))
            {
                $links['workspace_entry_url'] = platform_service_module_entry_url('workspace', $workspace_module_key, $entity_id, $item_id);
            }
            else
            {
                $links['workspace_entry_url'] = platform_service_entry_url('workspace', $entity_id, $item_id);
            }
        }

        return $links;
    }
}
