"""
Search profile and search query classes.

$Editor: vsafronovich $
$Id: Filter.py,v 1.3 2005/11/01 09:36:10 vsafronovich Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

from types import DictType, StringType

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from Acquisition import aq_get

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Features
from Features import createFeature
from SearchProfile import SearchQuery
from SimpleObjects import ContentBase
from Utils import getObjectByUid, InitializeClass

FilterType = { 'id'             : 'Filter'
             , 'meta_type'      : 'Filter'
             , 'title'          : "Filter"
             , 'description'    : "Stored filter"
             , 'icon'           : 'view.gif'
             , 'product'        : 'CMFNauTools'
             , 'factory'        : 'addFilter'
             , 'permissions'    : ( ZopePermissions.search_zcatalog, )
             , 'disallow_manual': 0
             , 'actions'        :
               ( { 'id'            : 'view'
                 , 'name'          : 'Execute'
                 , 'action'        : 'execute'
                 , 'permissions'   : ( CMFCorePermissions.View, )
                 },
                 { 'id'            : 'metadata'
                 , 'name'          : 'Metadata'
                 , 'action'        : 'metadata_edit_form'
                 , 'permissions'   : ( CMFCorePermissions.ModifyPortalContent, )
                 }
               )
             }

class Filter( ContentBase ):
    """
        A persistent filter
    """
    _class_version = 1.0

    meta_type   = 'Filter'
    portal_type = 'Filter'

    __implements__ = createFeature('isFilter'), \
                     Features.containsQuery, \
                     Features.isPortalContent, \
                     ContentBase.__implements__

    security = ClassSecurityInfo()
    security.declareProtected( CMFCorePermissions.View, 'query' )

    link_id = None
    query = None

    def __init__( self, id, title='', query=None, **kwargs ):
        """
        """
        ContentBase.__init__( self, id, title, **kwargs)

        self.setQuery( query )

    security.declareProtected( CMFCorePermissions.View, 'getQuery' )
    def getQuery( self ):
        """
        """
        return self.query

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setQuery' )
    def setQuery( self, query ):
        """
        """
        if query is None:
            self.query = SearchQuery()
        elif type(query) is DictType:
            self.query = SearchQuery( params=query )
        else:
#           self.query = query.clone()
            assert isinstance( query, SearchQuery ), "Query must be 'SearchQuery' class instance"
            self.query = query

    security.declareProtected( CMFCorePermissions.View, 'execute' )
    def execute( self, REQUEST=None ):
        """
            Redirects to the search results page.
        """
        REQUEST = REQUEST or aq_get( self, 'REQUEST', {} )

        params = { 'profile_id' : self.getUid()
                 , 'batch_length' : getToolByName(self, 'portal_membership')\
                                   .getInterfacePreferences('viewing_document_number')
                  }

        object = self.getObject()

        action = None
        if object.implements('isPortalRoot'):
            mode = self.getQuery().viewer_mode
            action = mode.endswith('_out') and 'followup_out' or 'followup_in'
            params['showTaskMode'] = mode

        if REQUEST.has_key('portal_status_message'):
            params['portal_status_message'] = REQUEST['portal_status_message']

        REQUEST['SESSION'].set('load_filter',True)#XXX
        return object.redirect( action=action, params=params, relative=False )

    def getObject(self):
        """
          Returns the actual object that the Shortcut is linking to
        """
        link = self._getLink()
        return link and link.getSourceObject()

    def getObjectUid(self):
        """
          Returns the actual object uid that the Shortcut is linking to
        """
        link = self._getLink()
        return link and link.getSourceUid()

    def _getLink(self):
        if not self.link_id:
            return None
        return getToolByName( self, 'portal_links' )._getOb( self.link_id, None )

    def edit( self, source, **kwargs):
        """
          Edits the Shortcut
        """
        links_tool =  getToolByName( self, 'portal_links' )

        if isinstance(source, StringType) and source=='portal':
            source = links_tool.getPortalObject()
        elif isinstance(source, StringType):
            source = getObjectByUid( self, source )

        mode = self.getQuery().viewer_mode   

        if self.link_id:
            links_tool.removeLink( self.link_id )

        self.link_id = links_tool.restrictedLink( source=source
                                                , source_collection='filters'
                                                , source_mode=mode or None
                                                , target=self
                                                , relation='collection' )


InitializeClass( Filter )
                     
def addFilter( self, id, query_id=None, source=None, title='', description='', REQUEST=None ):
    """
        Add a Search Profile
    """
    REQUEST = REQUEST or aq_get( self, 'REQUEST' )
    query = (query_id and REQUEST) and REQUEST.SESSION.get( ('search',query_id) ) or None
    self._setObject( id, Filter( id, title, query, description=description ) )

    filter = self._getOb(id)
    filter.edit(source)

def initialize( context ):
    # module initialization callback

    context.registerContent( Filter, addFilter, FilterType )
