"""
Migration script -- setup the default scripts.

$Editor: mbernatski $
$Id: setup_scripts.py,v 1.12 2006/09/27 10:03:45 oevsegneev Exp $
"""
__version__ = '$Revision: 1.12 $'[11:-2]

title = 'Setup the system scripts'
before_script = 1
order = 65
version = '3.2.0.189'

from Globals import DTMLFile
from Products.CMFCore.utils import getToolByName

from Products.CMFNauTools.DefaultScripts import Scripts
from Products.CMFNauTools.Script import Script, getNamespace

configuration_form = DTMLFile( 'dtml/setup_scripts_form', globals() )

def check( context, object ):
    flag = False
    folder = getToolByName( object, 'portal_properties' ).getProperty('scripts_folder')
    if folder is None:
        try:
            del globals()['configuration_form']
        except:
            pass
        return True
    scripts_to_update = []
    script_ids = Scripts.keys()
    ids = [ x for x in folder.objectIds() ]

    for id in script_ids:
        if id not in ids:
            flag = True
        elif folder._getOb( id ).body().strip() != Scripts[id]['data'].strip():
            scripts_to_update.append( id )
        else:
            continue

    if len( scripts_to_update ) > 0:
        context.script_init[ __name__ ] =  { 'scripts_to_update' : scripts_to_update }
        return True
    else:
        try:
            del globals()['configuration_form']
        except:
            pass
        return flag

def migrate( context, object ):
    scripts_to_update = []
    if context.script_options.has_key( __name__ ):
        script_options = context.script_options[ __name__ ]
        fields = script_options.get( 'fields', None )
        scripts_to_update = fields is not None and fields or []
    folder = getToolByName( object, 'portal_properties' ).getProperty( 'scripts_folder' )
    for script in Scripts.values():
        id = script['id']
        title = script['title']
        present_script = folder._getOb( id, None )
        if present_script is not None:
            if present_script.id in scripts_to_update:
                obj = folder[ id ]
                obj.setTitle( title )
                obj.write( script['data'] )
                obj.namespace_factory = getNamespace( script['namespace_factory'] )
                obj._allowed_types = script['_allowed_types']
                obj.setResultType( script.get( 'result_type' ) )
            continue
        obj = Script( id, title=title )
        folder._setObject( id, obj )
        obj = folder[id]
        obj.write( script['data'] )
        obj.namespace_factory = getNamespace( script['namespace_factory'] )
        obj._allowed_types = script['_allowed_types']
        obj.setResultType( script.get( 'result_type' ) )
