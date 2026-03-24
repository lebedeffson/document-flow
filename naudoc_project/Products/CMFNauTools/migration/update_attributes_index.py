"""
$Id: update_attributes_index.py,v 1.2 2006/09/27 10:03:45 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = "Update category attributes index"
before_script = 1
order = 51 # Must be run before setup_catalog

from Products.CMFCore.utils import getToolByName

def check( context, object ):
    catalog = getToolByName( object, 'portal_catalog' )
    try:
        index = catalog._catalog.getIndex('CategoryAttributes')
    except KeyError:
        return False # setup_catalog will do the work
    else:
        return index.setupIndexes( check=True )

def migrate( context, object ):
    catalog = getToolByName( object, 'portal_catalog' )
    catalog._catalog.getIndex('CategoryAttributes').setupIndexes()
    context.markForReindex( catalog='portal_catalog', idxs=['CategoryAttributes'] )
