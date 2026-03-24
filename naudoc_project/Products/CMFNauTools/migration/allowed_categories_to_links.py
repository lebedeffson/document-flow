"""
$Id: allowed_categories_to_links.py,v 1.1 2004/09/14 11:39:31 vpastukhov Exp $
$Editor: vpastukhov $
"""
__version__ = '$Revision: 1.1 $'[11:-2]

title = 'Update allowed categories in folders'
classes = ['Products.CMFNauTools.Heading.Heading']
version = '3.2.0.77'

from types import StringType
from Products.CMFCore.utils import getToolByName

def check( context, object ):
    return hasattr( object, '_allowed_categories' ) \
        or hasattr( object, '_category_inheritance' )

def migrate( context, object ):
    if hasattr( object, '_allowed_categories' ):
        metadata = getToolByName( object, 'portal_metadata' )
        categories = []

        # filter out removed categories
        for category in object._allowed_categories:
            if isinstance( category, StringType ):
                category = metadata.getCategory( category, None )
            if category is not None:
                categories.append( category )

        object.setAllowedCategories( categories )
        del object._allowed_categories

    if hasattr( object, '_category_inheritance' ):
        # default in the class is True
        if not object._category_inheritance:
            object.inherit_categories = False
        del object._category_inheritance
