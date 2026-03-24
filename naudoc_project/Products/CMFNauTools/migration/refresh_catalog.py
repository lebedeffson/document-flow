"""
$Id: refresh_catalog.py,v 1.11 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.11 $'[11:-2]

title = 'Refresh the portal catalog'
version = '3.4.0.0'
after_script = 1
order = 5

from Products.CMFNauTools import Config

_catalog_tools = tuple( Config.CatalogTools )

from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Utils import joinpath

def migrate( context, object ):
    for id in _catalog_tools:
        catalog = getToolByName( object, id )
        catalog = catalog.__of__( context.request )

        # remove invalid records
        catalog.refreshCatalog( clear=True, update=False )

        # remove records for objects in external
        if catalog._catalog.indexes.has_key( 'path' ):
            extpath = joinpath( object.getPhysicalPath(), 'external' )
            for rec in list( catalog.unrestrictedSearch( path=extpath ) ):
                catalog.uncatalog_object( rec.getPath() )

        # remove NauSite instance record
	bad_path = '/%s' % object.getId()
        if bad_path in catalog._catalog.paths.values():
            catalog.uncatalog_object(path)

        if context.mark_catalog.get( id ):
            # update everything
            catalog.refreshCatalog()

        elif context.mark_indexes.get( id ):
            # update only requested indexes
            for idx in context.mark_indexes[ id ].keys():
                catalog.reindexIndex( idx, context.request )
