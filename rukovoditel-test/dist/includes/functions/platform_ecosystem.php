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

        return [
            'docspace_url' => $docspace_url,
            'workspace_url' => $workspace_url,
        ];
    }
}
