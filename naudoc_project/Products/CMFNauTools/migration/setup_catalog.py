"""
$Id: setup_catalog.py,v 1.9 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.9 $'[11:-2]

title = 'Setup the portal catalog'
version = '3.4.0.0'
before_script = 1
order = 55

from Products.CMFNauTools import Config

_catalog_tools = tuple( Config.CatalogTools )

from Products.CMFCore.utils import getToolByName

def check( context, object ):
    for id in _catalog_tools:
        if getToolByName( object, id ).setupIndexes( check=True ):
            return True
    return False

def migrate( context, object ):
    for id in _catalog_tools:
        catalog = getToolByName( object, id )
        indexes, columns = catalog.setupIndexes()
        if columns and not indexes:
            # there is no way to update metadata only
            indexes.append( 'id' )
        if indexes:
            # TODO add support for update_metadata
            context.markForReindex( catalog=id, idxs=indexes )
