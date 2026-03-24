"""
DocflowReport class.
$Id: DocflowReport.py,v 1.24 2007/07/23 07:47:14 oevsegneev Exp $
$Editor: ishabalin $
"""

__version__ = '$Revision: 1.24 $'[11:-2]

import operator

from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser

import Features
from Utils import InitializeClass
from Config import Roles, Permissions
from SimpleObjects import InstanceBase
from ReferenceTable import ReferenceTable

DocflowReportType = { 'id'              : 'Docflow Report'
                    , 'meta_type'       : 'Docflow Report'
                    , 'title'           : "Docflow Report"
                    , 'description'     : "Docflow Report"
                    , 'icon'            : 'virt_doc_icon.gif'
                    , 'product'         : 'CMFNauTools'
                    , 'factory'         : 'addDocflowReport'
                    , 'immediate_view'  : 'docflow_report_edit_form'
                    , 'permissions'     : ( CMFCorePermissions.AddPortalContent, )
                    , 'actions'         :
                      ( { 'id'          : 'view'
                        , 'name'        : "View"
                        , 'action'      : 'docflow_report_view_form'
                        , 'permissions' : ( CMFCorePermissions.View, )
                        },
                        { 'id'          : 'edit'
                        , 'name'        : 'Settings'
                        , 'action'      : 'docflow_report_edit_form'
                        , 'permissions' : ( ZopePermissions.change_configuration, )
                        },
                      )
                    }


def addDocflowReport( self, id, REQUEST=None, **kwargs ):
    """
        Adds Docflow Report
    """

    obj = DocflowReport( id, **kwargs )
    self._setObject( id, obj )


class DocflowReport( ReferenceTable ):
    """
        DocflowReport class
    """

    _class_version = 1.2
    meta_type = 'Docflow Report'
    portal_type = 'Docflow Report'


    __implements__ = (  ReferenceTable.__implements__,
                        )
    category_id = None
    include_inherited = False
    search_all = False

    security = ClassSecurityInfo()

    _meta_columns = ('Id', 'Title', 'Description', 'Owner')

    def __init__( self, id, **kwargs ):
        """
            Initialize Class Instance
        """
        ReferenceTable.__init__( self, id, **kwargs )

    security.declareProtected(  CMFCorePermissions.ModifyPortalContent,
                                'setSearchableCategory')
    def setSearchableCategory(  self,
                                category_id,
                                include_inherited=None,
                                search_all=None):
        """
            Stores the category id. When displaying docflow report the search
            will be taken upon the documents of given category.

            Arguments:

                'category_id'       --  the category id.

                'allow_inherited'   --  indicates whether the search will
                                        consider categories inherited from the
                                        given one.

                'search_all'        --  indicates whether the search will be
                                        taken in all accessible documents.
        """

        self.category_id = category_id

        if include_inherited is not None:
            self.include_inherited = not not include_inherited

        if search_all is not None:
            self.search_all = not not search_all

    security.declareProtected(  CMFCorePermissions.View,
                                'getSearchableCategory')
    def getSearchableCategory(self):
        """
            Returns the id of the category upon which the search is taken.
        """

        return self.category_id

    security.declareProtected(  CMFCorePermissions.View,
                                'isIncludeInherited')
    def isIncludeInherited(self):
        """
            Indicates whether the search will consider categories inherited from
            the given one.
        """

        return self.include_inherited

    security.declareProtected(  CMFCorePermissions.View,
                                'isSearchAll')
    def isSearchAll(self):
        """
            Indicates either all accessible documents will match (true)
            or only documents located in current folder (false).
        """

        return self.search_all

    security.declareProtected(  CMFCorePermissions.View,
                                'searchEntries')
    def searchEntries(self, show_all_versions=0, **kw):
        """
            Returns a list of documents.

            Result:

                Dictionary (column id -> data)
        """

        search_path = (not self.search_all) and self.parent_path() or ''
        category_id = self.getSearchableCategory()
        kw['path'] = search_path

        if self.isIncludeInherited():
            kw['hasBase'] = category_id
        else:
            kw['category'] = category_id

        if show_all_versions:
            kw['implements'] = 'isVersion'
        else:
            kw['implements'] = 'isVersionable'

        catalog_tool = getToolByName(self, 'portal_catalog')
        results = catalog_tool.searchResults(**kw)
        return results

    security.declareProtected(  CMFCorePermissions.View, 'executeQuery')
    def executeQuery(self, REQUEST):
        catalog_tool = getToolByName(self, 'portal_catalog')
        SESSION = REQUEST['SESSION']
        r = REQUEST.get
        s = SESSION.get
        uid = self.getUid()

        sort_on    = r( 'sort_on',    s( '%s_sort_params' % uid, {} ).get( 'sort_on' ) )
        sort_attr  = r( 'sort_attr',  s( '%s_sort_params' % uid, {} ).get( 'sort_attr' ) )
        sort_order = r( 'sort_order', s( '%s_sort_order' % uid ) )
        sort_params = { 'sort_on': sort_on, 'sort_attr': sort_attr }

        show_all_versions = r( 'show_all', s( '%s_show_all_versions' % uid, 0 ) )

        table_columns = self.getFilterColumns()
        default_filter = { 'query'     : {},
                           'columns'   : table_columns
                         }

        filter_id = uid
        profile_id = r('profile_id', None)

        profile_filter = None
        if profile_id and s('load_filter', None):
            # remove flag
            SESSION.delete('load_filter')

            profile = catalog_tool.getObjectByUid(profile_id, feature = 'containsQuery')

            if profile:
                # load profile filter from filter object
                profile_query = profile.getQuery().copy()
                profile_filter = { 'query': profile_query.filter_query,
                                   'columns': table_columns,
                                   'profile_id': profile_id,
                                   'profile_title': profile.Title(),
                                 }

        filter = profile_filter or s( '%s_filter' % filter_id, default_filter )

        results = self.searchEntries( show_all_versions=show_all_versions
                                    , REQUEST=REQUEST
                                    , sort_on=sort_on
                                    , sort_order=sort_order
                                    , sort_attr=sort_attr, **filter['query'] )

        # 'table_pages_list' related stuff
        batch_size = int( r( 'batch_size', s( '%s_batch_size' % uid, 10 ) ) )
        qs_old     = int( r('qs', s( '%s_qs' % uid, 1 ) ) )
        qs_0       = qs_old - qs_old % batch_size + 1

        results_count = len( results )
        total_count = len( self.searchEntries() )

        total_pages = ( results_count / batch_size ) + ( results_count % batch_size and 1 ) or 1
        current_page = ( qs_0 / batch_size ) + ( qs_0 % batch_size and 1 )
        qs = current_page > total_pages and ( (total_pages - 1) * batch_size + 1) or qs_0

        def session_set( k, v ):
            if SESSION.get( k ) != v: SESSION.set( k, v )

        session_set( '%s_sort_params' % uid, sort_params )
        session_set( '%s_sort_order' % uid, sort_order )
        session_set( '%s_show_all_versions' % uid, show_all_versions )
        session_set( '%s_qs' % uid, qs )
        session_set( '%s_batch_size' % uid, batch_size )

        return { 'results'          : results
               , 'results_count'    : results_count
               , 'total_count'      : total_count

               , 'batch_size'       : batch_size
               , 'qs'               : qs

               , 'sort_on'          : sort_on
               , 'sort_order'       : sort_order
               , 'sort_attr'        : sort_attr
               , 'sort_params'      : sort_params
               
               , 'filter'           : filter
               , 'filter_id'        : filter_id
              
               , 'show_all_versions': show_all_versions
               }


    security.declareProtected(  CMFCorePermissions.View,
                                'getFilterColumns')
    def getFilterColumns(self):
        """
            Returns a list of columns for catalog_filter_form.
        """
        cols = [    {   'id':       'Title',
                        'title':    'Title',
                        'type':     'string',
                        },
                    {   'id':       'Creator',
                        'title':    'Owner',
                        'type':     'userlist',
                        'multiple': 1
                        },
            ]

        metadata = getToolByName( self, 'portal_metadata' )
        workflow = getToolByName( self, 'portal_workflow' )
        category = metadata.getCategoryById( self.getSearchableCategory() )
        if category:
            wf = category.getWorkflow()
            states = wf.states.objectIds()
            cols.append(    {   'id':       'state',
                                'title':    'State',
                                'type':     'list',
                                'multiple': 1,
                                'options':  [( x, workflow.getStateTitle(wf.getId(), x) )
                                                for x in states],
                                } )
            attributes = category.listAttributeDefinitions()
            for attr in attributes:
                cols.append(    {   'id':       '%s/%s' % (category.getId(), attr.getId()),
                                    'title':    attr.Title(),
                                    'type':     attr.Type(),
                                    'multiple': attr.isMultiple(),
                                    'options':  attr.getProperty('options',[]),
                                    'attributes_index' : 1
                                    } )
        return cols

InitializeClass(DocflowReport)

#
# XXX: DocflowReportColumn class is needed to migrate properly.
#

class DocflowReportColumn(InstanceBase):
    """
        DocflowReportColumn class.
    """
    _class_version = 1.1
    security = ClassSecurityInfo()

    def __init__(self, id, type, title='', origin_id=None, origin_type=None, sort_index=0, multiple=0):
        InstanceBase.__init__(self, id, title)
        self.type = type
        self.origin_id = origin_id
        self.origin_type = origin_type
        self.sort_index = sort_index
        self.multiple = multiple

    def __cmp__(self, other):
        assert isinstance( other, self.__class__ )
        return cmp(self.sort_index, other.sort_index)

    security.declarePublic('Type')
    def Type(self):
        """
            Returns the type the attribute, pointed by 'attr_id'.
        """
        return self.type

    security.declarePublic('getSortIndex')
    def getSortIndex(self):
        """
            Returns sort_index of the column.
        """
        return self.sort_index

    security.declarePublic('setSortIndex')
    def setSortIndex(self, si):
        """
            Sets sort_index for the column.
        """
        try:
            self.sort_index = int(si)
        except:
            pass

    security.declarePublic('getOriginId')
    def getOriginId(self):
        """
            Returns the origin id.
        """
        return self.origin_id

    security.declarePublic('getOriginType')
    def getOriginType(self):
        """
            Returns the origin type.
            Results:
                Either 'metadata' or 'attribute' or 'state'.
        """
        return self.origin_type

    security.declarePublic('isMultiple')
    def isMultiple(self):
        """
            Indicates whether the field is multivalued.
            Results:
                Boolean.
        """
        return self.multiple

InitializeClass(DocflowReportColumn)

def initialize( context ):
    # module initialization callback

    context.registerContent( DocflowReport, addDocflowReport, DocflowReportType )
