"""
Migration script -- fix RegistrationBook objects.

$Editor: ishabalin $
$Id: fix_registration_book.py,v 1.1 2004/04/30 07:23:33 ishabalin Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]


from Products.CMFNauTools.Utils import getToolByName
from Products.CMFNauTools.RegistrationBook import RegistrationBookColumn
from Products.CMFNauTools.ReferenceTable import AttributeReferenceColumn

title = 'Fix Registration books'
classes = [ 'Products.CMFNauTools.RegistrationBook.RegistrationBook' ]

version = '3.1.2.64'

def check(context, object):
    for column in object.listColumns():
        if isinstance( column, RegistrationBookColumn ):
            return 1
    return 0

def migrate(context, object):
    metadata = getToolByName( object, 'portal_metadata' )
    category_id = object.getRegisteredCategory()
    category = metadata.getCategoryById( category_id )
    old_columns = object.listColumns()
    for column in old_columns:
        if isinstance( column, RegistrationBookColumn ):
            column_id = column.getId()
            column_title = column.Title()
            attribute_id = column.getAttributeId()
            column_sort_index = column.sort_index
            sort_query = {'sort_on': 'CategoryAttributes', 'sort_attr': '%s/%s' % (category_id, attribute_id) }
            new_column = AttributeReferenceColumn( column_id, column_title, attribute_id, sort_query )
            new_column.sort_index = column_sort_index
            object.delColumn( column_id )
            object.columns = object.columns + (new_column,)
