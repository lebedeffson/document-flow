"""
$Id: fix_currency_attributes.py,v 1.5 2007/04/27 11:24:01 oevsegneev Exp $
$Editor: vsafronovich $
"""
__version__ = '$Revision: 1.5 $'[11:-2]

title = "Update values of the currency category attributes"
version = '3.2.0.173'

order = 75
before_script = 1

from types import StringTypes

from ZPublisher.Converters import type_converters

from Products.CMFCore.utils import getToolByName

def check( context, object ):
    catalog = getToolByName( object, 'portal_catalog' )
    res = catalog.searchResults( implements=['isCategorial'] )
    for item in res:
        item = item.getObject()
        if not item:
            continue

        for attr, value in item.listCategoryAttributes(restricted=Trust):
            if attr.Type() != 'currency' or attr.isDerived():
                continue

            if isinstance(attr.getDefaultValue(), StringTypes):
                return True

            if isinstance(value , StringTypes):
                return True
    else:
        return False

def migrate( context, object, convert=type_converters['currency'] ):
    catalog = getToolByName( object, 'portal_catalog' )

    res = catalog.searchResults( implements=['isCategorial'] )
    for item in res:
        item = item.getObject()
        if not item:
            continue

        for attr, value in item.listCategoryAttributes(restricted=Trust):
            if attr.Type() != 'currency' or attr.isDerived():
                continue

            if isinstance(attr.getDefaultValue(), StringTypes):
                attr.setDefaultValue( convert( attr.getDefaultValue() ) )

            if isinstance(value , StringTypes):
                item._setCategoryAttribute( attr, value ) # _updateProperty do the work
