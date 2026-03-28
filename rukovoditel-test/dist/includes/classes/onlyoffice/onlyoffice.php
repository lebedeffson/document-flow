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

class onlyoffice
{
    private $entity_id;
    
    function __construct($entity_id)
    {
        $this->entity_id = $entity_id;
    }
    
    static function genFileKey($file_id)
    {                
        return $_SERVER['HTTP_HOST'] . '-' . $file_id . '-' . time();
    }
    
    static function callback_error_log($msg)
    {
        error_log(date('Y-m-d H:i:s') . ' Error: ' . $msg . "\n _GET params: " . print_r($_GET,true) . "\n\n",3,'log/onlyoffice_callback.log');
        
        $response = [
            'error'=>1,
            'status' => 'success'
            ];
        
       die(json_encode($response));
    }

    static function getIntegrationBaseUrl()
    {
        $base_url = trim((string) getenv('ONLYOFFICE_INTEGRATION_BASE_URL'));
        return strlen($base_url) ? rtrim($base_url, '/') : '';
    }

    static function getDocumentServerInternalBaseUrl()
    {
        $base_url = trim((string) getenv('ONLYOFFICE_INTERNAL_BASE_URL'));
        if (strlen($base_url))
        {
            return rtrim($base_url, '/');
        }

        $upstream = trim((string) getenv('GATEWAY_ONLYOFFICE_UPSTREAM'));
        if (!strlen($upstream))
        {
            return '';
        }

        if (!preg_match('/^https?:\\/\\//i', $upstream))
        {
            $upstream = 'http://' . $upstream;
        }

        return rtrim($upstream, '/');
    }

    static function getDocumentServerFetchUrl($url)
    {
        $url = trim((string) $url);
        if (!strlen($url))
        {
            return $url;
        }

        $base_url = self::getDocumentServerInternalBaseUrl();
        if (!strlen($base_url) || !preg_match('/^https?:\\/\\//i', $url))
        {
            return $url;
        }

        $url_parts = parse_url($url);
        $base_parts = parse_url($base_url);

        if (!$url_parts || !$base_parts)
        {
            return $url;
        }

        $path = $url_parts['path'] ?? '';
        if (strpos($path, '/office/') === 0)
        {
            $path = substr($path, strlen('/office'));
            if (!strlen($path))
            {
                $path = '/';
            }
        }

        $result = ($base_parts['scheme'] ?? 'http') . '://' . ($base_parts['host'] ?? '');

        if (isset($base_parts['port']))
        {
            $result .= ':' . $base_parts['port'];
        }

        $result .= $path;

        if (isset($url_parts['query']) && strlen($url_parts['query']))
        {
            $result .= '?' . $url_parts['query'];
        }

        if (isset($url_parts['fragment']) && strlen($url_parts['fragment']))
        {
            $result .= '#' . $url_parts['fragment'];
        }

        return $result;
    }

    static function buildAbsoluteUrl($url, $base_url = '')
    {
        if (!strlen($url))
        {
            return $url;
        }

        $base_url = strlen($base_url) ? rtrim($base_url, '/') : self::getIntegrationBaseUrl();
        $is_absolute = preg_match('/^https?:\\/\\//i', $url);

        if (!strlen($base_url))
        {
            return $url;
        }

        if ($is_absolute)
        {
            $base_parts = parse_url($base_url);
            $url_parts = parse_url($url);

            if (!$base_parts || !$url_parts)
            {
                return $url;
            }

            $result = ($base_parts['scheme'] ?? 'http') . '://' . ($base_parts['host'] ?? '');

            if (isset($base_parts['port']))
            {
                $result .= ':' . $base_parts['port'];
            }

            if (isset($base_parts['path']) && strlen(rtrim($base_parts['path'], '/')))
            {
                $result .= rtrim($base_parts['path'], '/');
            }

            $result .= $url_parts['path'] ?? '';

            if (isset($url_parts['query']) && strlen($url_parts['query']))
            {
                $result .= '?' . $url_parts['query'];
            }

            if (isset($url_parts['fragment']) && strlen($url_parts['fragment']))
            {
                $result .= '#' . $url_parts['fragment'];
            }

            return $result;
        }

        return $base_url . '/' . ltrim($url, '/');
    }

    static function detectEditorType()
    {
        $user_agent = strtolower((string) ($_SERVER['HTTP_USER_AGENT'] ?? ''));
        if (preg_match('/android|iphone|ipad|ipod|mobile|tablet/i', $user_agent))
        {
            return 'mobile';
        }

        return 'desktop';
    }
    
    static function getDownloadUrl($file, $absolute = false, $base_url = '')
    {
        $download_token = $file['download_token'];
        if(!strlen($download_token))
        {
            $download_token = users::get_random_password(12, false);
            
            db_query("update app_onlyoffice_files set download_token='{$download_token}' where id={$file['id']}");
        }
        
        $url = url_for('onlyoffice/download','file=' . $file['id'] . '&field=' . $file['field_id']. '&token=' . $download_token);

        if ($absolute)
        {
            return self::buildAbsoluteUrl($url, $base_url);
        }

        return $url;
    }
    
    /*
    * Defines the document type to be opened:
    * https://api.onlyoffice.com/editors/config/#documentType
    */ 
    static function getDocumentInfo($filename)
    {
        $documentType = [
            'word' =>['.djvu','.doc','.docm','.docx','.docxf','.dot','.dotm','.dotx','.epub','.fb2','.fodt','.htm','.html','.mht','.mhtml','.odt','.oform','.ott','.oxps','.pdf','.rtf','.stw','.sxw','.txt','.wps','.wpt','.xml','.xps'],
            'cell' =>['.csv','.et','.ett','.fods','.ods','.ots','.sxc','.xls','.xlsb','.xlsm','.xlsx','.xlt','.xltm','.xltx','.xml'],
            'slide' =>['.dps','.dpt','.fodp','.odp','.otp','.pot','.potm','.potx','.pps','.ppsm','.ppsx','.ppt','.pptm','.pptx','.sxi'],
        ];
        
        $pathinfo = pathinfo($filename);
        $extension = $pathinfo['extension']??'word';
        
        $documentInfo = [
            'documentType' => '',
            'fileType' => $extension,
        ];
        
        foreach($documentType as $k=>$v)
        {
            if(in_array('.' . $extension,$v))
            {
                $documentInfo['documentType'] = $k;
            }
        }
        
        return $documentInfo;
    }
    
    static function getMode($cfg,$entity_id, $item_id)
    {
        global $app_fields_cache, $app_user;
        
        $mode = 'view';
        
        switch($cfg->get('allow_edit'))
        {
            case 'users_view_access':
                $mode = 'edit';
                break;
            case 'users_edit_access':
                $item_info = db_find('app_entity_' . $entity_id,$item_id);
                $access_rules = new access_rules($entity_id, $item_info);
                if(users::has_access('update', $access_rules -> get_access_schema()))
                {
                    $mode = 'edit';
                }
                break;
            case 'assigned_users':
                $item_info = db_find('app_entity_' . $entity_id,$item_id);
                $assigned_users_fields = $cfg->get('assigned_users_fields');
                
                if(is_array($assigned_users_fields))
                {
                    foreach($assigned_users_fields as $field_id)
                    {
                        if($app_fields_cache[$entity_id][$field_id]['type']=='fieldtype_created_by')
                        {
                            if($item_info['created_by']==$app_user['id'])
                            {
                                $mode = 'edit';
                            }
                        }
                        elseif(isset($item_info['field_' . $field_id]) and in_array($app_user['id'],explode(',',$item_info['field_' . $field_id])))
                        {
                            $mode = 'edit';
                        }
                            
                    }
                }
                break;            
        }
        
        return $mode;
    }

    static function xml_escape($value)
    {
        return htmlspecialchars((string) $value, ENT_XML1 | ENT_COMPAT, 'UTF-8');
    }

    static function build_package_content($entries)
    {
        $tmp_file = tempnam(sys_get_temp_dir(), 'onlyoffice_blank_');
        $zip = new ZipArchive();

        if($zip->open($tmp_file, ZipArchive::OVERWRITE) !== true)
        {
            @unlink($tmp_file);
            return false;
        }

        foreach($entries as $path => $content)
        {
            $zip->addFromString($path, $content);
        }

        $zip->close();

        $data = file_get_contents($tmp_file);
        @unlink($tmp_file);

        return $data;
    }

    static function build_blank_docx()
    {
        return self::build_package_content([
            '[Content_Types].xml' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>',
            '_rels/.rels' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>',
            'word/document.xml' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/2006/relationships" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 wp14">
  <w:body>
    <w:p/>
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>',
            'word/_rels/document.xml.rels' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>',
        ]);
    }

    static function build_blank_xlsx()
    {
        return self::build_package_content([
            '[Content_Types].xml' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>',
            '_rels/.rels' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>',
            'docProps/app.xml' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>DocFlow</Application>
</Properties>',
            'docProps/core.xml' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Blank spreadsheet</dc:title>
  <dc:creator>DocFlow</dc:creator>
</cp:coreProperties>',
            'xl/workbook.xml' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <bookViews>
    <workbookView xWindow="0" yWindow="0" windowWidth="28800" windowHeight="18120"/>
  </bookViews>
  <sheets>
    <sheet name="Лист1" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>',
            'xl/_rels/workbook.xml.rels' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>',
            'xl/styles.xml' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>',
            'xl/worksheets/sheet1.xml' => '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="A1"/>
  <sheetViews><sheetView workbookViewId="0"/></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <sheetData/>
</worksheet>',
        ]);
    }

    static function build_blank_file_content($file_type)
    {
        switch(strtolower($file_type))
        {
            case 'docx':
                return self::build_blank_docx();
            case 'xlsx':
                return self::build_blank_xlsx();
            default:
                return false;
        }
    }

    protected function can_update_item($item)
    {
        global $app_user;

        $access_rules = new access_rules($this->entity_id, $item);
        $access_schema = $access_rules->get_access_schema();

        if(users::has_access('update', $access_schema))
        {
            return true;
        }

        if(
            users::has_access('update_creator', $access_schema)
            && (int) ($item['created_by'] ?? 0) === (int) ($app_user['id'] ?? 0)
        )
        {
            return true;
        }

        return false;
    }

    protected function can_edit_blank_by_field($field, $item)
    {
        if(!is_array($field) || !is_array($item) || (int) ($item['id'] ?? 0) <= 0)
        {
            return false;
        }

        $cfg = new settings($field['configuration'] ?? '');

        return self::getMode($cfg, $this->entity_id, (int) $item['id']) === 'edit';
    }

    protected function can_create_blank_for_field($field, $item, $file_type = 'docx')
    {
        $file_type = strtolower(trim((string) $file_type));

        if(!in_array($file_type, ['docx', 'xlsx'], true))
        {
            return false;
        }

        if(!$this->can_edit_blank_by_field($field, $item))
        {
            return false;
        }

        $cfg = new fields_types_cfg($field['configuration'] ?? '');
        $allowed_extensions = is_array($cfg->get('allowed_extensions')) ? $cfg->get('allowed_extensions') : ['.docx', '.xlsx'];

        return in_array('.' . $file_type, $allowed_extensions, true);
    }

    function can_create_blank($field_id, $item, $file_type = 'docx')
    {
        $field_query = db_query(
            "select * from app_fields where id='" . db_input($field_id) . "' and entities_id='" . db_input($this->entity_id) . "' and type='fieldtype_onlyoffice'"
        );

        if(!$field = db_fetch_array($field_query))
        {
            return false;
        }

        return $this->can_create_blank_for_field($field, $item, $file_type);
    }

    function create_blank($field_id, $item_id, $file_type = 'docx')
    {
        global $app_user;

        $field_query = db_query("select * from app_fields where id='" . db_input($field_id) . "' and entities_id='" . db_input($this->entity_id) . "' and type='fieldtype_onlyoffice'");
        if(!$field = db_fetch_array($field_query))
        {
            redirect_to_404();
        }

        $item_query = db_query("select * from app_entity_" . (int) $this->entity_id . " where id='" . db_input($item_id) . "'");
        if(!$item = db_fetch_array($item_query))
        {
            redirect_to_404();
        }

        $file_type = strtolower(trim((string) $file_type));
        if(!$this->can_create_blank_for_field($field, $item, $file_type))
        {
            redirect_to_forbidden();
        }

        $binary_content = self::build_blank_file_content($file_type);
        if($binary_content === false)
        {
            redirect_to_404();
        }

        $timestamp = date('Ymd-His');
        $base_filename = ($file_type === 'xlsx' ? 'blank-spreadsheet-' : 'blank-document-') . $timestamp . '.' . $file_type;
        $filename = $this->remove_special_characters($base_filename);

        $sql_data = [
            'entity_id' => $this->entity_id,
            'field_id' => $field_id,
            'form_token' => '',
            'filename' => $filename,
            'date_added' => time(),
            'created_by' => $app_user['id'],
        ];

        db_perform('app_onlyoffice_files', $sql_data);
        $file_id = db_insert_id();

        $folder = $this->prepare_file_folder($filename);
        if(!is_dir(DIR_WS_ONLYOFFICE . $folder . '/' . $file_id))
        {
            mkdir(DIR_WS_ONLYOFFICE . $folder . '/' . $file_id);
            $folder = $folder . '/' . $file_id;
        }

        $file_path = DIR_WS_ONLYOFFICE . $folder . '/' . $filename;
        if(file_put_contents($file_path, $binary_content) === false)
        {
            db_delete_row('app_onlyoffice_files', $file_id);
            exit('Unable to create ONLYOFFICE file');
        }

        db_perform('app_onlyoffice_files', [
            'folder' => $folder,
            'filekey' => self::genFileKey($file_id),
        ], 'update', 'id=' . $file_id);

        $field_key = 'field_' . $field_id;
        $existing_files = array_filter(array_map('trim', explode(',', (string) ($item[$field_key] ?? ''))));
        array_unshift($existing_files, (string) $file_id);
        $existing_files = array_values(array_unique($existing_files));

        db_perform('app_entity_' . (int) $this->entity_id, [
            $field_key => implode(',', $existing_files),
            'date_updated' => time(),
        ], 'update', "id='" . db_input($item_id) . "'");

        return [
            'file_id' => $file_id,
            'filename' => $filename,
            'editor_url' => url_for(
                'items/onlyoffice_editor',
                'path=' . (int) $this->entity_id . '-' . (int) $item_id . '&action=open&field=' . (int) $field_id . '&file=' . (int) $file_id
            ),
        ];
    }
    
    function upload()
    {        
        global $app_user,$app_session_token;
                
        if(isset($_SESSION['app_logged_users_id']))
        {
            $verifyToken = md5($app_user['id'] . $_POST['timestamp']);
        }
        else
        {
            $verifyToken = md5($app_session_token . $_POST['timestamp']);
        }
        
        $field_id = _GET('field_id');
                                        
        if (strlen($_FILES['Filedata']['tmp_name']) and $_POST['token'] == $verifyToken)
        {
            $filename = $_FILES['Filedata']['name'];
            
            if(isset($_POST['filename_template']) and strlen($_POST['filename_template']) and isset($_POST['form_data']))
            {
                $filename = attachments::get_filename_by_template($_POST['filename_template'],$_POST['form_data'],$filename);
            }
            else
            {            
                $filename =  $this->remove_special_characters($filename);
            }
            
            $sql_data = [
                'entity_id' => $this->entity_id,
                'field_id' => $field_id,
                'form_token' => $verifyToken,
                'filename' => $filename,                
                'date_added' => time(),
                'created_by' => $app_user['id']                
            ];
            
            db_perform('app_onlyoffice_files', $sql_data);
            $file_id = db_insert_id();
            
            $folder = $this->prepare_file_folder($filename);
            
            if(!is_dir(DIR_WS_ONLYOFFICE . $folder . '/' . $file_id))
            {
                mkdir(DIR_WS_ONLYOFFICE . $folder . '/' . $file_id);
                
                $folder  = $folder . '/' . $file_id;
            }

            if (move_uploaded_file($_FILES['Filedata']['tmp_name'], DIR_WS_ONLYOFFICE . $folder . '/' . $filename))
            {                
                 $sql_data = [
                     'folder' => $folder,
                     'filekey' => self::genFileKey($file_id),
                 ];
                 
                 db_perform('app_onlyoffice_files', $sql_data,'update','id=' . $file_id);
            }
        }
    }
    
    function copy_from_attachments($field_id, $attachments = [], $delete_source_file = true)
    {
        global $app_user;
        
        $onlyoffice_files = [];
        foreach($attachments as $attachment)
        {
            $file = attachments::parse_filename($attachment);
            
            if(!is_file($file['file_path'])) continue;
            
            $filename = $file['name'];
            
            $sql_data = [
                'entity_id' => $this->entity_id,
                'field_id' => $field_id,
                'form_token' => '',
                'filename' => $filename,                
                'date_added' => time(),
                'created_by' => $app_user['id']                
            ];
            
            db_perform('app_onlyoffice_files', $sql_data);
            $file_id = db_insert_id();
            
            $onlyoffice_files[] = $file_id;
            
            $folder = $this->prepare_file_folder($filename);
            
            if(!is_dir(DIR_WS_ONLYOFFICE . $folder . '/' . $file_id))
            {
                mkdir(DIR_WS_ONLYOFFICE . $folder . '/' . $file_id);
                
                $folder  = $folder . '/' . $file_id;
            }

            if (copy($file['file_path'], DIR_WS_ONLYOFFICE . $folder . '/' . $filename))
            {        
                if($delete_source_file)
                {
                    unlink($file['file_path']);
                }
                
                 $sql_data = [
                     'folder' => $folder,
                     'filekey' => self::genFileKey($file_id),
                 ];
                 
                 db_perform('app_onlyoffice_files', $sql_data,'update','id=' . $file_id);                 
            }                        
        }
        
        return $onlyoffice_files;
        
    }
    
    function remove_special_characters($string)
    {
        return preg_replace('/-+/', '-', preg_replace('/[^\w._-]+/u', '', preg_replace('/\s+/', '-', trim($string))));
    }
    
    function prepare_file_folder($filename)
    {
                
        if(!is_dir(DIR_WS_ONLYOFFICE . $this->entity_id))
        {
            mkdir(DIR_WS_ONLYOFFICE . $this->entity_id);
        }

        if(!is_dir(DIR_WS_ONLYOFFICE . $this->entity_id . '/' . date('Y')))
        {
            mkdir(DIR_WS_ONLYOFFICE . $this->entity_id . '/'  . date('Y'));
        }

        if(!is_dir(DIR_WS_ONLYOFFICE . $this->entity_id . '/'  . date('Y') . '/' . date('m')))
        {
            mkdir(DIR_WS_ONLYOFFICE . $this->entity_id . '/' . date('Y') . '/' . date('m'));
        }

        if(!is_dir(DIR_WS_ONLYOFFICE . $this->entity_id . '/' . date('Y') . '/' . date('m') . '/' . date('d')))
        {
            mkdir(DIR_WS_ONLYOFFICE . $this->entity_id . '/' . date('Y') . '/' . date('m') . '/' . date('d'));
        }

        return  $this->entity_id . '/' . date('Y') . '/' . date('m') . '/' . date('d');
    }
    
    function preview($field_id, $token, $item_id)
    {
        global $app_session_token, $app_module_path;

        $html = '';

        $field_query = db_query("select id, name, configuration,type from app_fields where id='" . $field_id . "'");
        if($field = db_fetch_array($field_query))
        {
            $cfg = new fields_types_cfg($field['configuration']);
        }
        else
        {
            return '';
        }
        
        //get attachments 
        $attachments = [];
        
        //get exist attachment for item
        if($item_id>0)
        {
            $item = db_find('app_entity_' . $this->entity_id,$item_id);
            if(isset($item['field_' . $field_id]) and strlen($item['field_' . $field_id]))
            {
                $files_query = db_query("select * from app_onlyoffice_files where id in (" . db_input_in($item['field_' . $field_id]) . ") and field_id='" . db_input($field_id) . "'", false);
                while ($file = db_fetch_array($files_query))
                {
                    $attachments[] = $file;
                }
            }
        }
        
        //get new attachments by form token
        if(strlen($token))
        {
            $files_query = db_query("select * from app_onlyoffice_files where form_token='" . db_input($token) . "' and field_id='" . db_input($field_id) . "'", false);
            while ($file = db_fetch_array($files_query))
            {
                $attachments[] = $file;
            }
        }
        
        if(!count($attachments)) return '';
                        
        //print_rr($attachments);
        
        //check delete access
        $has_delete_access = true;        
        if($cfg->get('check_delete_access')==1)
        {
            $has_delete_access = users::has_access('delete');
        }
        
        
        //check delete access
        $allow_change_file_name = false;
        if($cfg->get('allow_change_file_name')==1)
        {
            $allow_change_file_name = true;
        }
        
        
        foreach($attachments as $file)
        {           
            $filepathinfo = pathinfo($file['filename']);
                        
            $row_id = 'attachments_row_' . $field_id . '_' . $file['id'];

            $html .= '
                <div class="input-group input-group-attachments ' . $row_id . '">
                    ' . input_hidden_tag('fields[' . $field_id . '][' . $file['id'] . '][id]', $file['id']);
            
            if($allow_change_file_name)
            {
                $html .= input_tag('fields[' . $field_id . '][' . $file['id'] . '][name]',$filepathinfo['filename'],['class'=>'form-control input-sm']) ;

                if(strlen($filepathinfo['extension']??''))
                {
                    $html .= '
                        <span class="input-group-addon">
                            .' . $filepathinfo['extension'] . '
                        </span>
                        ';
                }
            }
            else
            {
                $html .= input_tag('fields[' . $field_id . '][' . $file['id'] . '][name]',$file['filename'],['class'=>'form-control input-sm','readonly'=>'readonly']) ;
            }

            if($has_delete_access)
            {
                $html .= '
                    <span class="input-group-addon">
                        <i class="fa fa-trash-o pointer delete_attachments_icon" data-id="' . $file['id'] . '" data-row_id="' . $row_id . '" data-name="' . $file['filename'] . '" title="' . TEXT_DELETE . '"></i>
                    </span> 
                    
                    ';
            }

            $html .= ' 
                </div>
                ';
        }
        
        if($has_delete_access)
        {
            $html .= '
                    <script>
                        $("#uploadifive_attachments_list_' . $field_id. ' .delete_attachments_icon").click(function(){
                            rowData = $(this).data()
                            info = $("#uploadifive_attachments_list_' . $field_id. '").data()
                            if(confirm(rowData.name+"\n' . addslashes(TEXT_DELETE_FILE). '?"))
                            {                                
                                $("."+rowData.row_id).fadeOut()
                                $.ajax({
                                    method: "POST",
                                    url: info.delete_url,
                                    data: {file: rowData.id}
                                }).done(function(){
                                    $("."+rowData.row_id).remove()
                                })
                                
                            }
                            
                        })
                    </script>
                ';
        }
        
        return $html;
    }
    
    static function get_file_info($file)
    {
        $pathinfo = pathinfo($file['filename']);
        $extension = $pathinfo['extension']??'';
        
        if(is_file('images/fileicons/' . $extension . '.png'))
        {
            $icon = 'images/fileicons/' . $extension . '.png';
        }
        else
        {
            $icon = 'images/fileicons/attachment.png';
        }
        
        if(is_file($file_path = DIR_WS_ONLYOFFICE . $file['folder'] . '/' . $file['filename']))
        {            
            $size = attachments::file_size_convert(filesize($file_path));            
        }
        else
        {
            $size = 0;
        }
        
        return [
                'size'=>$size,
                'icon'=>$icon,
                'name'=>$pathinfo['filename'],
                'extension'=>$extension,
            ];
    }
    
    static function download($entity_id, $item_id, $file_id)
    {
        //check if ID exist in DB
        $file_query = db_query("select * from app_onlyoffice_files where id={$file_id}");
        if(!$file = db_fetch_array($file_query))
        {
            die(TEXT_FILE_NOT_FOUD);
        }
        
        //check if file exist on disk
        if(!is_file($file_path = DIR_WS_ONLYOFFICE . $file['folder'] . '/' . $file['filename']))
        {
            die(TEXT_FILE_NOT_FOUD);
        }
        
        //check if file assigend to record
        $item = db_find('app_entity_' . $entity_id,$item_id);       
        if(isset($item['field_' . $file['field_id']]) and !in_array($file['field_id'],explode(',', $file['field_id'])))
        {
            die(TEXT_FILE_NOT_FOUD);
        }
        
        header('Content-Description: File Transfer');
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename='.$file['filename']);
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($file_path));

        flush();

        readfile($file_path);
        
        exit();
    }
    
    static function download_all($entity_id, $item_id, $field_id)
    {
        $item_query = db_query("select * from app_entity_{$entity_id} where id={$item_id}");
        if(!$item = db_fetch_array($item_query))
        {
            die(TEXT_FILE_NOT_FOUD);
        }
        
        if(!isset($item['field_' . $field_id]) or (isset($item['field_' . $field_id]) and !strlen($item['field_' . $field_id])))
        {
            die(TEXT_FILE_NOT_FOUD);
        }
        
        $zip = new ZipArchive();
        $zip_filename = "attachments-{$item_id}.zip";
        $zip_filepath = DIR_FS_UPLOADS . $zip_filename;                
        
        //open zip archive        
        $zip->open($zip_filepath, ZipArchive::CREATE);
                        
        //add files to archive   
        $files_query = db_query("select * from app_onlyoffice_files where find_in_set(id,'" . $item['field_' . $field_id] . "') and field_id='" . db_input($field_id) . "'", false);
        while ($file = db_fetch_array($files_query))
        {
           $zip->addFile(DIR_WS_ONLYOFFICE . $file['folder'] . '/' . $file['filename'],$file['filename']);                                       
        }
                        
        $zip->close();
        
        //check if zip archive created
        if (!is_file($zip_filepath)) 
        {
            exit("Error: cannot create zip archive in " . $zip_filepath );
        }
        
        //download file
        header('Content-Description: File Transfer');
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename='.$zip_filename);
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($zip_filepath));
        
        flush();
              
        readfile($zip_filepath);   
        
        //delete temp zip archive file
        @unlink($zip_filepath); 
        
        exit();
    }
    
    static function delete($file_id)
    {
        $file_query = db_query("select * from app_onlyoffice_files where id={$file_id}");
        if($file = db_fetch_array($file_query))
        {
            if(is_file($file_path = DIR_WS_ONLYOFFICE . $file['folder'] . '/' . $file['filename']))
            {
                unlink($file_path);
            }
            
            db_delete_row('app_onlyoffice_files', $file_id);
        }
    }
    
    public static function delete_attachments($entities_id, $items_id)
    {
        $items_query = db_query("select * from app_entity_" . $entities_id . " where id='" . db_input($items_id) . "'");
        if($items = db_fetch_array($items_query))
        {
            $fields_query = db_query("select * from app_fields where entities_id='" . db_input($entities_id) . "' and type in ('fieldtype_onlyoffice')");
            while($fields = db_fetch_array($fields_query))
            {            
                if(strlen($files = $items['field_' . $fields['id']]) > 0)
                {
                    $files_query = db_query("select * from app_onlyoffice_files where field_id='" . db_input($fields['id']) . "' and id in (" . db_input_in($files) . ")", false);
                    while ($file = db_fetch_array($files_query))
                    {
                        if(is_file($filepath = DIR_WS_ONLYOFFICE . $file['folder'] . '/' . $file['filename']))
                        {
                            unlink($filepath);
                        }
                        
                        db_delete_row('app_onlyoffice_files', $file['id']);
                    }
                }
            }
        }
    }
}
