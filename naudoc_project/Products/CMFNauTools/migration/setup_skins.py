"""                                   
$Id: setup_skins.py,v 1.21 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.21 $'[11:-2]

title = 'Update portal skins'
version = '3.4.0.0'
remove_prefixes = ['lib/python/Products/', 'Products/']
after_script = 1
order = 2

from Globals import DTMLFile

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.DirectoryView import _dirreg
from Products.CMFCore.utils import getToolByName

from Products.CMFNauTools.Config import SkinViews, PublicViews, Roles, SiteSkinViews
from Products.CMFNauTools.Utils import pathdelim

configuration_form = DTMLFile( 'dtml/setup_skins_form', globals() )

outdated_skins = ( 'content', 'zpt_content'
                 , 'control', 'zpt_control'
                 , 'generic', 'zpt_generic'
                 , 'Images', 'img', 'nauboard'
                 , 'no_css', 'nouvelle'
                 )

extra_skin_ids = ('fckeditor', 'manual')

site_subfolders = ( 'images', 'custom' )

def check(context, object):
    skins_tool = getToolByName(object, 'portal_skins')
    site_skins_tool = getToolByName( object, 'portal_site_skins' )

    extra_skins = []
    for skin_id in extra_skin_ids:
        skin_object = object._getOb(skin_id, None)
        if skin_object:
            extra_skins.append(skin_object)

    existing_skins = []
    result = False
    for view in SkinViews:
        if skins_tool._getOb( view, None ) is None:
            #need to add skin
            result = True
            break

    for id, dw in skins_tool.objectItems():
        if not hasattr( dw, '_isDirectoryView' ):
            continue

        existing_skins.append( id )

        dirpath = dw._dirpath
	for remove_prefix in remove_prefixes:
            if dirpath.startswith( remove_prefix ):
                result = True
                continue

	if '\\' in dirpath:
            result = True
            continue

        if not _dirreg.getDirectoryInfo( dirpath ):
            # Directory view refers to nonexistent filesystem path.
            result = True
            continue

        if id.startswith('site_') and not site_skins:
            # Directory view refers to the site skins.
            result = True
            #existing_skins.remove( id )
            continue

    site_skins = []
    for id, obj in site_skins_tool.objectItems():
	site_skins.extend([obj._getOb(id) for id in site_subfolders])

    for dw in site_skins + extra_skins:
	if not dw:
	    result = True
	    continue

        dirpath = dw._dirpath

        for remove_prefix in remove_prefixes:
            if dirpath.startswith( remove_prefix ):
	        result = True
		continue

	if '\\' in dirpath:
            # Directory view need update path
            result = True
            continue

    skins_to_remove = []
    for skin in existing_skins:
        if (skin in outdated_skins) and (skin not in SkinViews):
            skins_to_remove.append(skin)

    skins_to_add = [skin for skin in SkinViews if skin not in existing_skins]

    if skins_to_remove or skins_to_add:
        context.script_init[ __name__ ] =  { 'skins_to_remove' : skins_to_remove,
                                             'skins_to_add'    : skins_to_add }
    else:
        try:
            del globals()['configuration_form']
        except:
            pass

    return result

def migrate(context, object):
    def fix_path(path):
        if '\\' in path:
            path = path.replace( '\\', pathdelim )

        for remove_prefix in remove_prefixes:
            if path.startswith( remove_prefix ):
                path = path[ len(remove_prefix): ]    
        return path
    
    skins_tool = getToolByName(object, 'portal_skins')
    site_skins_tool = getToolByName( object, 'portal_site_skins' )

    extra_skins = []
    for skin_id in extra_skin_ids:
        skin_object = object._getOb(skin_id, None)
        if skin_object:
            extra_skins.append(skin_object)

    skins_to_remove = []
    if context.script_options.has_key( __name__ ):
        script_options = context.script_options[ __name__ ]
        skins = context.script_init[ __name__ ][ 'skins_to_remove' ]
        skins_to_remove = [s for s in skins if script_options.get( s, None ) == 'remove']


    plugin_skins = []
    for id, dw in skins_tool.objectItems():
        if not ( hasattr( dw, '_isDirectoryView' ) and dw._dirpath ):
            continue

	dw._dirpath = fix_path(dw._dirpath)

        if not _dirreg.getDirectoryInfo( dw._dirpath ) or id.startswith('site_') or (id in skins_to_remove):
            # directory view refers to nonexistent filesystem path or to the site skin
            skins_tool._delObject( id )

        elif id not in SkinViews:
            plugin_skins.append( id )

    site_skins = []
    for id, obj in site_skins_tool.objectItems():
        site_skins.extend([obj._getOb(id) for id in site_subfolders])

    for dw in site_skins + extra_skins:
        dw._dirpath = fix_path(dw._dirpath)

    for view in SkinViews:
        if skins_tool._getOb( view, None ) is None:
            # Have to register new directory view.
            skins_tool.addSkinLayer( view, 'skins/%s' % view )

    # these skin elements are available for anonymous visitors
    # for name in PublicViews:
    #  skins_tool[ name ].manage_permission( CMFCorePermissions.View, [Roles.Anonymous], 1 )

    default_skins = ','.join( ['custom'] + SkinViews + plugin_skins )
    skins_tool.addSkinSelection( 'Site', default_skins, make_default=1 )
    skins_tool.addSkinSelection( 'Mail', 'mail_templates' )

    object.setupCurrentSkin()
