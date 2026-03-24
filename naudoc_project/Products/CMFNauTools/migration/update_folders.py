"""
$Id: update_folders.py,v 1.8 2005/05/14 05:43:46 vsafronovich Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.8 $'[11:-2]

title = 'Update the portal folders'
classes = [ 'Products.CMFNauTools.Heading.Heading',
            'Products.CMFNauTools.MailFolder.IncomingMailFolder',
            'Products.CMFNauTools.MailFolder.OutgoingMailFolder',
            'Products.CMFNauTools.Storefront.Storefront',
          ]
strict_classes = 1
version = '3.1.5.23'

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

def check( context, object ):
    base = aq_base( object )
    metadata_tool = getToolByName( object, 'portal_metadata' )
    allowed_category_ids = [ x.getId() for x in metadata_tool.listCategories( base ) ]
    category = getattr( base, 'category', None )
    return ( not category or category not in allowed_category_ids ) \
           or hasattr( base, '_postfix') or hasattr( base, '_nomenclative_number' )

def migrate( context, object ):
    base = aq_base( object )
    metadata_tool = getToolByName( object, 'portal_metadata' )
    allowed_category_ids = [ x.getId() for x in metadata_tool.listCategories( base ) ]
    category = getattr( base, 'category', None )

    if not category or category not in allowed_category_ids:
        object.setCategory( 'Folder' )

    if hasattr( base, '_postfix' ):
        try:
            if not object._getCategoryAttribute( 'postfix' ):
                object._setCategoryAttribute( 'postfix', base._postfix )
        except KeyError: pass
        delattr( base, '_postfix' )

    if hasattr( base, '_nomenclative_number' ):
        try:
            if not object._getCategoryAttribute( 'nomenclative_number' ):
                object._setCategoryAttribute( 'nomenclative_number', base._nomenclative_number )
        except KeyError: pass
        delattr( base, '_nomenclative_number' )
