"""
Migration script -- fix DocflowReport objects.

$Editor: ishabalin $
$Id: fix_docflow_report.py,v 1.3 2004/04/30 07:23:33 ishabalin Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]


from Products.CMFNauTools.Utils import getToolByName
from Products.CMFNauTools.DocflowReport import DocflowReportColumn
from Products.CMFNauTools.ReferenceTable import ReferenceColumn,            \
                                                AttributeReferenceColumn,   \
                                                StateFlagReferenceColumn,   \
                                                MemberReferenceColumn,      \
                                                HyperlinkReferenceColumn

title = 'Fix Docflow reports'
classes = [ 'Products.CMFNauTools.DocflowReport.DocflowReport' ]

version = '3.1.2.61'

def check(context, object):
    for column in object.listColumns():
        if isinstance( column, DocflowReportColumn ):
            return 1
    return 0

def migrate(context, object):
    metadata = getToolByName( object, 'portal_metadata' )
    category_id = object.getSearchableCategory()
    category = metadata.getCategoryById( category_id )
    old_columns = object.listColumns()
    for column in old_columns:
        if isinstance( column, DocflowReportColumn ):
            column_id = column.getId()
            column_title = column.Title()
            column_origin_type = column.getOriginType()
            column_origin_id = column.getOriginId()
            column_sort_index = column.sort_index
            object.delColumn( column_id )
            klass = None
            argument = None
            sort_query = {}
            if column_origin_type == 'attribute':
                klass = AttributeReferenceColumn
                argument = column_origin_id
                sort_query = {'sort_on': 'CategoryAttributes', 'sort_attr': '%s/%s' % (category_id, argument) }
            elif column_origin_type == 'state':
                klass = StateFlagReferenceColumn
                argument = column_origin_id
            elif column_origin_type == 'metadata':
                if column_origin_id == 'Id':
                    klass = HyperlinkReferenceColumn
                    argument = 'object.getId()'
                    sort_query = { 'sort_on': 'id' }
                elif column_origin_id == 'Title':
                    klass = HyperlinkReferenceColumn
                    argument = 'object.Title()'
                    sort_query = { 'sort_on': 'Title' }
                elif column_origin_id == 'Description':
                    klass = ReferenceColumn
                    argument = 'object.Description()'
                    sort_query = { 'sort_on': 'Description' }
                elif column_origin_id == 'Owner':
                    klass = MemberReferenceColumn
                    argument = 'object.Creator()'
                    sort_query = { 'sort_on': 'Creator' }
            if klass:
                new_column = klass( column_id, column_title, argument, sort_query )
                new_column.sort_index = column_sort_index
                object.columns = object.columns + (new_column,)
