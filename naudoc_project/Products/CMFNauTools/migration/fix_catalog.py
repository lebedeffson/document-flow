"""
$Id: fix_catalog.py,v 1.4 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.4 $'[11:-2]

title = 'Fix catalog'
version = '3.4.0.0'
before_script = 1
order = 56

# TODO: valid check

from Products.CMFNauTools import Config

_catalog_tools = tuple(Config.CatalogTools)

from Products.CMFCore.utils import getToolByName

def migrate( context, object ):

    catalog_tools = [getToolByName(object, id) for id in _catalog_tools]

    portal_catalog = getToolByName(object, 'portal_catalog')
    directory_catalogs = [brain.getObject() for brain in portal_catalog.searchResults(implements=['isDirectory'])]
    category_atributes_catalog = portal_catalog._catalog.getIndex('CategoryAttributes')

    catalogs = catalog_tools + directory_catalogs + [category_atributes_catalog]

    for catalog in catalogs:

	print context.class_scripts['Products.ZCatalog.ZCatalog.ZCatalog']
	context.class_scripts['Products.ZCatalog.ZCatalog.ZCatalog'][0] \
	       .migrate(context, catalog)

