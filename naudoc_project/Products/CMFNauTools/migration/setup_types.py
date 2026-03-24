"""
$Id: setup_types.py,v 1.12 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.12 $'[11:-2]

title = 'Update object types'
version = '3.4.0.0'
before_script = 1
order = 5

from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.TypesTool import TypesInstaller

def migrate( context, object ):
    types = getToolByName( object, 'portal_types' )
    seen = {}

    for ftis in TypesInstaller._ftiss:
        for tp in ftis:
            id = tp['id']
            seen[ id ] = tp

            # rebuild existing types
            if types.getTypeInfo( id ):
                types._delObject( id )
                types.addType( id, tp )

            # add new types
            elif tp.get( 'activate', True ):
                types.addType( id, tp )

    for id in types.objectIds():
        # drop outdated types
        if not seen.has_key( id ):
            types._delObject( id )
