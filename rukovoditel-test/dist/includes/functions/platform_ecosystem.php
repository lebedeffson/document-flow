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
    function platform_ecosystem_url($service, $entity_id = 0, $item_id = 0, $absolute = false)
    {
        $params = 'service=' . rawurlencode($service);

        if($entity_id > 0 && $item_id > 0)
        {
            $params .= '&entity_id=' . (int) $entity_id . '&item_id=' . (int) $item_id;
        }

        if(!$absolute && function_exists('url_for'))
        {
            return url_for('dashboard/ecosystem', $params);
        }

        return platform_public_base_url() . 'index.php?module=dashboard/ecosystem&' . $params;
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
            'naudoc_url' => platform_item_naudoc_url($entity_id, $item),
            'docspace_url' => $docspace_url,
            'workspace_url' => $workspace_url,
            'docspace_entry_url' => '',
            'workspace_entry_url' => '',
        ];

        if(platform_service_enabled('docspace'))
        {
            $links['docspace_entry_url'] = platform_ecosystem_url('docspace', $entity_id, $item_id);
        }

        if(platform_service_enabled('workspace'))
        {
            $links['workspace_entry_url'] = platform_ecosystem_url('workspace', $entity_id, $item_id);
        }

        return $links;
    }
}
