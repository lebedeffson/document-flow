"""
$Id: update_category_attributes.py,v 1.3 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

title = "Update default values of the category attributes"
version = '3.4.0.0'
classes = [ 'Products.CMFNauTools.CategoryAttribute.CategoryAttribute' ]

from Products.CMFNauTools import Exceptions
from Products.CMFNauTools.Utils import readLink

def check( context, object ):
    if not ( object.type == 'link' and object.defvalue ):
        return False

    try:
        readLink( object, 'property', 'default', object.defvalue )
        return False
    except KeyError:
        return True

def migrate( context, object ):
    try:
        object.setDefaultValue( object.defvalue )
    except Exceptions.SimpleError:
        object.setDefaultValue( None )
