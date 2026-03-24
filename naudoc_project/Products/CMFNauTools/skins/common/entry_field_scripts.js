//
// $Editor: vpastukhov $
// $Id: entry_field_scripts.js,v 1.5 2006/03/06 16:15:47 ypetrov Exp $
// $Revision: 1.5 $
//

fieldEditHandler.int_check =
function ( field )
{
    var v = field.value;
    if (! v.length)
        return true;

    v = parseInt( v, 10 );
    if (isNaN( v )) {
        field.value = '';
        return false;
    }

    field.value = v;
    return true;
};

fieldEditHandler.float_check =
function ( field )
{
    var v = field.value;
    if (! v.length)
        return true;

    v = parseFloat( v );
    if (isNaN( v )) {
        field.value = '';
        return false;
    }

    field.value = v;
    return true;
};

fieldEditHandler.currency_check =
function ( field )
{
    var v = field.value.replace(',','.');
    if (! v.length)
        return true;

    v = parseFloat( v );
    if (isNaN( v )) {
        field.value = '';
        return false;
    }

    field.value = v.toFixed(2);
    return true;
};

var modifier2position = { 'days': 0
                        , 'hours': 1
                        , 'minutes': 2
                        };

fieldEditHandler.time_interval_convert =
function ( field )
{
   var form = field.form,
       field_id = field.id,
       modifier = field.title,
       prefix = field_id.substr( 0, field_id.length - modifier.length - 1 );

   ti_field = form.elements[prefix];

   var dhm = ti_field.value.split(':');
   dhm[ modifier2position[modifier] ] = field.value;

   // set back
   ti_field.value = dhm.join(':');
};

fieldEditHandler.file_clear =
function ( field )
{
    var form = field.form;
    var name = field.getAttribute('field_name');

    form.elements[ name+'.filename:record' ].value = '';

    return true;
};

fieldEditHandler.link_select =
function ( field, scope, features, types, categories )
{
    var form = field.form;
    var name = field.getAttribute('field_name');
    var fuid = form.elements[ name+':uid' ];
    var win  = getWindow( form );

    if (features == null)   features   = fuid.getAttribute('field_features') || '';
    if (types == null)      types      = fuid.getAttribute('field_types') || '';
    if (categories == null) categories = fuid.getAttribute('field_categories') || '';

    win.OpenDocumentSelectionWnd( form.name, 'link_callback',
                                  scope, features, name+':uid', '', categories, types );
    return true;
};

fieldEditHandler.link_clear =
function ( field )
{
    var form = field.form;
    var name = field.getAttribute('field_name');
    var fuid = form.elements[ name+':uid' ];

    fuid.value = '';
    fuid.nextSibling.nextSibling.value = '';

    if (fuid.onchange != null)
        fuid.onchange();

    return true;
};

link_callback =
fieldEditHandler.link_callback =
function ( fname, uid, title, version_id, uid_field, title_field )
{
    var form = this.document.forms[ fname ];
    var fuid = form.elements[ uid_field ];
    var ftitle = title_field ? form.elements[ title_field ]
                             : fuid.nextSibling.nextSibling;
    fuid.value = uid;
    ftitle.value = title;

    if (fuid.onchange != null)
        fuid.onchange();
};

fieldEditHandler.link_properties =
function ( form, name, scope, features, types, categories )
{
    var field = form.elements[ name+':uid' ];
    if (! field)
        return false;

    if (features != null)   field.setAttribute( 'field_features', features );
    if (types != null)      field.setAttribute( 'field_types', types );
    if (categories != null) field.setAttribute( 'field_categories', categories );

    return true;
};

fieldEditHandler.folder_select =
function ( id )
{
    var link = window[ id+'_link' ];
    window.open( link, 'wnd_popup_menu', 'toolbar=no,scrollbars=yes,width=300,height=400,resizable=yes' );
    field_id = id;
    return true;
};

fieldEditHandler.folder_callback =
function ( uid, title )
{
    document.getElementById( field_id+'_uid' ).value = uid;
    document.getElementById( field_id+'_title' ).value = title;
};

function setFolderUrl( uid, title )
{
    fieldEditHandler.folder_callback( uid, title );
}

//
// Advanced userlist stuff
//
function toggleSourcesTab(select)
{
    var name = select.id.substring(0, select.id.length - 8)

    for (var i = 0; i < select.options.length; i++) {
        var option = select.options[i],
            tab_id = name + '_' + option.value
        getElement(tab_id).style.display = (option.selected ? '' : 'none')
    }
}

var fillSources = {}
fillSources['user'] = fillSources['group'] = fillSources['role'] = 
function (callback, source, extract)
{
    if (extract)
        source = source.getElementsByTagName('select')[0]

    for (var i = 0; i < source.options.length; i++) {
        var option = source.options[i]
        if (! option.selected) continue
        callback(option.text, option.value)
    }
}

function addMemberSources(name, source)
{
    var sources_select = getElement(name + '_sources'),
        type   = sources_select.value,
        target = getElement(name + '_items'),
        prefix = sources_select.options[sources_select.selectedIndex].text

    function addSource(text, value)
    {
        for (var i = 0; i < target.options.length; i++)
            if (target.options[i].value == value) return

        addOptionTo(target, prefix + ': ' + text, value)
        addHidden(target.form, name + ':uid:list', value)
    }

    if (source)
        fillSources[type](addSource, source)
    else {
        source = getElement(name + '_' + sources_select.value)
        fillSources[type](addSource, source, true)
    }
}
function deleteMemberSources(select)
{
    var name
    
    if (typeof select == 'string') {
        name = select
        select = getElement(select + '_items')
    }
    else
        name = select.id.substring(0, select.id.length - 6)

    name += ':uid:list'

    while (select.selectedIndex != -1) {
        deleteHidden(select.form, name, select.value)
        select.options.remove(select.selectedIndex)
    }
}
