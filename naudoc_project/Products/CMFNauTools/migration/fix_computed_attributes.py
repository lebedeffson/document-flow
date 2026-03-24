"""
$Id: fix_computed_attributes.py,v 1.2 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = "Update type of the computed category attributes with missing script"
version = '3.4.0.1'

order = 75
before_script = 1

from Products.CMFCore.utils import getToolByName

def check( context, object ):
    metadata = getToolByName( object, 'portal_metadata' )
    cats = metadata.listCategories()
    for cat in cats:
        for attr in cat.listAttributeDefinitions():
            if attr.isDerived() and attr.Type() is None:
                return True
    else:
        return False

def migrate( context, object ):
    metadata = getToolByName( object, 'portal_metadata' )
    cats = metadata.listCategories()
    for cat in cats:
        for attr in cat.listAttributeDefinitions():
            if attr.isDerived() and attr.Type() is None:
                attr.type = 'unknown_value'

