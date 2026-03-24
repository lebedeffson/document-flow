"""
Migration script -- setting appropriate categories for non-versionable content.

$Editor: ishabalin $
$Id: fix_nonversionable_content.py,v 1.4 2004/04/30 10:08:12 vpastukhov Exp $
"""
__version__ = '$Revision: 1.4 $'[11:-2]

title = 'Set appropriate categories for non-versionable content'
version = '3.1.2.64'
classes = [ 'Products.CMFNauTools.SiteImage.SiteImage',
            'Products.CMFNauTools.DTMLDocument.DTMLDocument' ]

default_category = 'SimpleDocument'
replaced_categories = { 'Document': 'SimpleDocument',
                        'Publication': 'SimplePublication',
                        }

def check( context, object ):
    category = object.getCategory()
    return not category or replaced_categories.has_key( category.getId() )

def migrate( context, object ):
    category = object.getCategory()
    if category:
        category = replaced_categories[ category.getId() ]
    object.setCategory( category or default_category )
