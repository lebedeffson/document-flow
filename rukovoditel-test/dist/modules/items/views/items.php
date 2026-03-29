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

<?php require(component_path('items/navigation')) ?>

<?php
app_reset_selected_items();

//print_rr($reports_info);

$listing_container = 'entity_items_listing' . (isset($force_filters_reports_id) ? $force_filters_reports_id : $reports_info['id']) . '_' . $reports_info['entities_id'];

if(isset($force_filters_reports_id))
{
    $reports_info = $default_reports_info;
}

echo input_hidden_tag('entity_items_listing_path', $_GET['path']);
?>

<?php
if(!function_exists('platform_first_entity_item_id'))
{
    function platform_first_entity_item_id($entity_id)
    {
        $row = db_fetch_array(db_query("select id from app_entity_" . (int) $entity_id . " order by id limit 1"));
        return $row ? (int) $row['id'] : 0;
    }
}

if(in_array($current_entity_id, [1, 25, 26, 27]))
{
    $banner_title = '';
    $banner_text = '';
    $demo_item_url = '';
    $demo_item_label = '';
    $demo_editor_url = '';
    $docspace_url = '';
    $workspace_url = '';
    $workspace_calendar_url = '';
    $workspace_create_meeting_url = '';
    $workspace_community_url = '';
    $create_item_url = url_for('items/form', 'path=' . $_GET['path']);
    if($current_entity_id == 1)
    {
        $user_item_id = platform_first_entity_item_id(1);
        if($user_item_id > 0)
        {
            $demo_item_url = url_for('items/info', 'path=1-' . $user_item_id);
        }

        $banner_title = 'Пользователи';
        $banner_text = 'Здесь администратор заводит новых сотрудников, находит существующие профили, назначает роли и ведет рабочий каталог пользователей.';
        $demo_item_label = 'Открыть профиль пользователя';
    }
    elseif($current_entity_id == 25)
    {
        $onlyoffice_demo = platform_first_onlyoffice_demo(25);
        $demo_item_url = url_for('items/items', 'path=25');

        if($onlyoffice_demo['item_id'] > 0)
        {
            $demo_item_url = url_for('items/info', 'path=25-' . $onlyoffice_demo['item_id']);
        }

        $banner_title = 'Карточки документов';
        $banner_text = 'Создайте карточку документа, откройте ее и используйте кнопки "Создать пустой документ" или "Создать пустую таблицу". Готовый файл сразу открывается в ONLYOFFICE.';
        $demo_item_label = 'Открыть рабочий документ';

        if($onlyoffice_demo['item_id'] > 0 and $onlyoffice_demo['field_id'] > 0 and $onlyoffice_demo['file_id'] > 0)
        {
            $demo_editor_url = url_for(
                'items/onlyoffice_editor',
                'path=25-' . $onlyoffice_demo['item_id'] . '&action=open&field=' . (int) $onlyoffice_demo['field_id'] . '&file=' . (int) $onlyoffice_demo['file_id']
            );
        }

        if(platform_service_enabled('docspace'))
        {
            $docspace_url = platform_service_entry_url('docspace', 25, (int) $onlyoffice_demo['item_id']);
        }

        if(platform_service_enabled('workspace'))
        {
            $workspace_url = platform_service_entry_url('workspace', 25, (int) $onlyoffice_demo['item_id']);
            $workspace_calendar_url = platform_service_module_entry_url('workspace', 'calendar', 25, (int) $onlyoffice_demo['item_id']);
            $workspace_create_meeting_url = platform_workspace_create_meeting_url(25, (int) $onlyoffice_demo['item_id']);
            $workspace_community_url = platform_service_module_entry_url('workspace', 'community', 25, (int) $onlyoffice_demo['item_id']);
        }
    }
    elseif($current_entity_id == 26)
    {
        $doc_base_item_id = platform_first_entity_item_id(26);
        if($doc_base_item_id > 0)
        {
            $demo_item_url = url_for('items/info', 'path=26-' . $doc_base_item_id);
        }

        $banner_title = 'База документов';
        $banner_text = 'Готовые материалы и шаблоны доступны для поиска, просмотра и перехода в официальный контур.';
        $demo_item_label = 'Открыть пример материала';

        if(platform_service_enabled('docspace'))
        {
            $docspace_url = platform_service_entry_url('docspace', 26, $doc_base_item_id);
        }

        if(platform_service_enabled('workspace'))
        {
            $workspace_url = platform_service_entry_url('workspace', 26, $doc_base_item_id);
            $workspace_calendar_url = platform_service_module_entry_url('workspace', 'calendar', 26, $doc_base_item_id);
            $workspace_create_meeting_url = platform_workspace_create_meeting_url(26, $doc_base_item_id);
            $workspace_community_url = platform_service_module_entry_url('workspace', 'community', 26, $doc_base_item_id);
        }
    }
    elseif($current_entity_id == 27)
    {
        $mts_item_id = platform_first_entity_item_id(27);
        if($mts_item_id > 0)
        {
            $demo_item_url = url_for('items/info', 'path=27-' . $mts_item_id);
        }

        $banner_title = 'Заявки на МТЗ';
        $banner_text = 'Процессы обеспечения связаны с рабочим и официальным документным контуром.';
        $demo_item_label = 'Открыть пример заявки';

        if(platform_service_enabled('docspace'))
        {
            $docspace_url = platform_service_entry_url('docspace', 27, $mts_item_id);
        }

        if(platform_service_enabled('workspace'))
        {
            $workspace_url = platform_service_entry_url('workspace', 27, $mts_item_id);
            $workspace_calendar_url = platform_service_module_entry_url('workspace', 'calendar', 27, $mts_item_id);
            $workspace_create_meeting_url = platform_workspace_create_meeting_url(27, $mts_item_id);
            $workspace_community_url = platform_service_module_entry_url('workspace', 'community', 27, $mts_item_id);
        }
    }

    echo '<div class="platform-context-banner">';
    echo '<div class="platform-context-banner-copy">';
    echo '<div class="platform-context-banner-title">' . $banner_title . '</div>';
    echo '<p>' . $banner_text . '</p>';
    echo '</div>';
    echo '<div class="platform-context-banner-actions">';

    if(strlen($demo_item_url))
    {
        echo link_to('<i class="fa fa-file-text-o"></i> ' . $demo_item_label, $demo_item_url, ['class' => 'btn btn-info']);
    }

    if($current_entity_id == 1)
    {
        echo link_to('<i class="fa fa-user-plus"></i> Создать пользователя', $create_item_url, ['class' => 'btn btn-primary']);
        echo link_to('<i class="fa fa-users"></i> Группы доступа', url_for('users_groups/users_groups'), ['class' => 'btn btn-default']);
    }
    elseif($current_entity_id == 25)
    {
        echo link_to('<i class="fa fa-plus"></i> Создать карточку документа', $create_item_url, ['class' => 'btn btn-primary']);

        if(strlen($demo_editor_url))
        {
            echo link_to('<i class="fa fa-pencil-square-o"></i> Открыть ONLYOFFICE', $demo_editor_url, ['class' => 'btn btn-default', 'target' => '_blank']);
        }
    }

    if(strlen($docspace_url))
    {
        echo link_to('<i class="fa fa-users"></i> Открыть DocSpace', $docspace_url, ['class' => 'btn btn-default']);
    }

    if(strlen($workspace_url))
    {
        echo link_to('<i class="fa fa-briefcase"></i> Открыть Workspace', $workspace_url, ['class' => 'btn btn-default']);
    }

    if(strlen($workspace_calendar_url))
    {
        echo link_to('<i class="fa fa-calendar"></i> Встречи Workspace', $workspace_calendar_url, ['class' => 'btn btn-default']);
    }

    if(strlen($workspace_create_meeting_url))
    {
        echo link_to('<i class="fa fa-calendar-plus-o"></i> Создать встречу', $workspace_create_meeting_url, ['class' => 'btn btn-default']);
    }

    if(strlen($workspace_community_url) && $current_entity_id == 26)
    {
        echo link_to('<i class="fa fa-book"></i> Workspace Community', $workspace_community_url, ['class' => 'btn btn-default']);
    }

    echo link_to('<i class="fa fa-archive"></i> Открыть NauDoc', '/docs/', ['class' => 'btn btn-default', 'target' => '_blank']);

    echo '</div>';
    echo '</div>';
}
?>

<?php
if(filters_preivew::has_default_panel_access($entity_cfg))
{
    $filters_preivew = new filters_preivew($reports_info['id'], false);
    $filters_preivew->path = $current_path;
    $filters_preivew->redirect_to = 'listing';

    if(!in_array($app_user['group_id'], explode(',', $entity_cfg->get('listing_config_access'))) and strlen($entity_cfg->get('listing_config_access')))
    {
        $filters_preivew->has_listing_configuration = false;
    }

    echo $filters_preivew->render();
}

//print_rr($reports_info);

$filters_panels = new filters_panels($current_entity_id, $reports_info['id'], $listing_container, $parent_entity_item_id);
echo $filters_panels->render_horizontal();

//get listing switchetrs
$listing = new items_listing($reports_info['id']);
$curren_listing_type = $listing->get_listing_type();
$listing_switches = (isset($force_filters_reports_id) ? '' : listing_types::render_switches($reports_info, $curren_listing_type))
?>

<div class="row">
    <div class="col-sm-<?php echo (strlen($listing_switches) ? '5' : '7') ?>">
        <div class="entitly-listing-buttons-left">
            <?php if(users::has_access('create') and access_rules::has_add_buttons_access($current_entity_id, $parent_entity_item_id)) echo button_tag((strlen($entity_cfg->get('insert_button')) > 0 ? $entity_cfg->get('insert_button') : TEXT_ADD), url_for('items/form', 'path=' . $_GET['path'])) . ' '; ?>

            <?php
            $with_selected_menu = '';
            if(users::has_access('export_selected') and users::has_access('export'))
            {
                $with_selected_menu .= '<li>' . link_to_modalbox('<i class="fa fa-file-excel-o"></i> ' . TEXT_EXPORT, url_for('items/export', 'path=' . $_GET['path'] . '&reports_id=' . $reports_info['id'])) . '</li>';
            }

            if(is_ext_installed())
            {
                $processes = new processes($reports_info['entities_id']);
                $processes->rdirect_to = 'items';
                $with_selected_menu .= $processes->render_buttons('menu_with_selected', $reports_info['id']);
            }


            $with_selected_menu .= plugins::render_simple_menu_items('with_selected', '&reports_id=' . $reports_info['id']);
            
            if(users::has_access('update_selected') and listing_types::has_tree_table($current_entity_id))
            {
                $with_selected_menu .= '<li>' . link_to_modalbox('<i class="fa fa-sitemap"></i> ' . TEXT_CHANGE_PARENT_ITEM, url_for('items/change_parent_selected', 'path=' . $_GET['path'] . '&reports_id=' . $reports_info['id'])) . '</li>';
            }


            if(users::has_access('delete') and users::has_access('delete_selected') and $current_entity_id != 1)
            {
                $with_selected_menu .= '<li>' . link_to_modalbox('<i class="fa fa-trash-o"></i> ' . TEXT_BUTTON_DELETE, url_for('items/delete_selected', 'path=' . $_GET['path'] . '&reports_id=' . $reports_info['id'])) . '</li>';
            }




            if(strlen($with_selected_menu))
            {
            ?>      
                <div class="btn-group">
                    <button class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown" data-hover="dropdown">
                        <?php echo TEXT_WITH_SELECTED ?> <i class="fa fa-angle-down"></i>
                    </button>
                    <ul class="dropdown-menu" role="menu">										
                        <?php echo $with_selected_menu ?>
                    </ul>
                </div>  
<?php
    if(in_array($curren_listing_type, ['grid', 'mobile']))
    {
        if(listing_types::has_action_field($curren_listing_type, $reports_info['entities_id']))
        {
            echo '  	
	  			<label>' . input_checkbox_tag('select_all_items', $reports_info['id'], array('class' => $listing_container . '_select_all_items_force', 'data-container-id' => $listing_container)) . ' ' . TEXT_SELECT_ALL . '</label>  		
  			';
        }
    }
}
if(is_ext_installed())
{
    echo $processes->render_buttons('in_listing', $reports_info['id']);
}

if(users::has_access('import'))
{
    echo link_to_modalbox('<i class="fa fa-upload"></i>', url_for('items/import', 'path=' . $_GET['path']), array('class' => 'btn btn-default', 'title' => TEXT_IMPORT));
}

if(is_ext_installed())
{
    echo xml_import::get_users_templates_by_position($current_entity_id, 'in_listing');
    echo export_selected::get_users_templates_by_position($current_entity_id, 'in_listing','&reports_id=' . $reports_info['id']) . export_selected::get_users_templates_by_position($current_entity_id, 'menu_export','&reports_id=' . $reports_info['id']);
}
?>
        </div>
    </div>

<?php if(strlen($listing_switches)) echo '<div class="col-sm-2">' . $listing_switches . '</div>'; ?>  

    <div class="col-sm-5">
        <div class="entitly-listing-buttons-right1">    
<?php echo render_listing_search_form($entity_info['id'], $listing_container, $reports_info['id']) ?>

            <?php
            if(!filters_preivew::has_default_panel_access($entity_cfg) and!isset($force_filters_reports_id) and (in_array($app_user['group_id'], explode(',', $entity_cfg->get('listing_config_access'))) or!strlen($entity_cfg->get('listing_config_access'))))
            {
                $html = '
			      <div class="btn-group hidden-in-mobile" style="float:right">
							<a class="btn dropdown-toggle" href="#" data-toggle="dropdown" data-hover="dropdown">
							<i class="fa fa-gear"></i></i>
							</a>
							<ul class="dropdown-menu pull-right">
								<li>
			            ' . link_to_modalbox('<i class="fa fa-sort-amount-asc"></i> ' . TEXT_HEADING_REPORTS_SORTING, url_for('reports/sorting', 'reports_id=' . $reports_info['id'] . '&redirect_to=listing' . (strlen($app_path) > 0 ? '&path=' . $app_path : ''))) . '
			            ' . link_to_modalbox('<i class="fa fa-wrench"></i> ' . TEXT_NAV_LISTING_CONFIG, url_for('reports/configure', 'reports_id=' . $reports_info['id'] . '&redirect_to=listing' . (strlen($app_path) > 0 ? '&path=' . $app_path : ''))) . '
			      		
								</li>
							</ul>
						</div>
			    ';

                echo $html;
            }
            ?>        
        </div>

    </div>
</div> 

<div class="row">
    <div class="col-sm-<?php echo (12 - $filters_panels->vertical_width) ?>">
        <div id="<?php echo $listing_container ?>" class="entity_items_listing entity_items_listing_loading"></div>
    </div>

<?php echo $filters_panels->render_vertical(); ?>
</div>

<?php echo input_hidden_tag($listing_container . '_order_fields', $reports_info['listing_order_fields']) ?>
<?php echo input_hidden_tag($listing_container . '_has_with_selected', (strlen($with_selected_menu) ? 1 : 0)) ?>

<?php require(component_path('items/load_items_listing.js')); ?>

<?php
$gotopage = 1;
if(isset($_GET['gotopage'][$reports_info['id']]))
{
    $gotopage = (int) $_GET['gotopage'][$reports_info['id']];
}
elseif(isset($listing_page_keeper[$reports_info['id']]))
{
    $gotopage = $listing_page_keeper[$reports_info['id']];
    unset($listing_page_keeper[$reports_info['id']]);
}
?>

<script>
    $(function ()
    {
        load_items_listing('<?php echo $listing_container ?>',<?php echo $gotopage ?>);
    });
</script> 
