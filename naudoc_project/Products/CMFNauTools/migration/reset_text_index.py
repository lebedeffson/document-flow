"""
$Id: reset_text_index.py,v 1.2 2005/05/14 05:43:46 vsafronovich Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = 'Reset the full text search index'
before_script = 1
version = '3.2.0.44'
order = 49 # Must be run before setup_catalog


from Products.CMFCore.utils import getToolByName

def check( context, object ):
    catalog = getToolByName( object, 'portal_catalog' )
    return 'SearchableText' in catalog.indexes()

def migrate( context, object ):
    catalog = getToolByName( object, 'portal_catalog' )
    catalog._catalog.delIndex( 'SearchableText' )
