"""
Search profile and search query classes.

$Editor: vpastukhov $
$Id: SearchProfile.py,v 1.29 2005/11/01 09:36:10 vsafronovich Exp $
"""
__version__ = '$Revision: 1.29 $'[11:-2]

from copy import deepcopy
from random import randrange
from types import DictType

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from Acquisition import aq_get

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Features
from Features import createFeature
from SimpleObjects import ContentBase
from Utils import InitializeClass, joinpath


SearchProfileType = { 'id'             : 'Search Profile'
                    , 'meta_type'      : 'Search Profile'
                    , 'title'          : "Search Profile"
                    , 'description'    : "Stored search profile"
                    , 'icon'           : 'view.gif'
                    , 'product'        : 'CMFNauTools'
                    , 'factory'        : 'addSearchProfile'
                    , 'permissions'    : ( ZopePermissions.search_zcatalog, )
                    , 'disallow_manual': 0
                    , 'actions'        :
                      ( { 'id'            : 'view'
                        , 'name'          : "Execute"
                        , 'action'        : 'execute'
                        , 'permissions'   : ( CMFCorePermissions.View, )
                        }
                      , { 'id'            : 'metadata'
                        , 'name'          : "Metadata"
                        , 'action'        : 'metadata_edit_form'
                        , 'permissions'   : ( CMFCorePermissions.ModifyPortalContent, )
                        }
                      )
                    }

class SearchProfile( ContentBase ):
    """
        A persistent Search Profile
    """
    _class_version = 1.0

    meta_type   = 'Search Profile'
    portal_type = 'Search Profile'

    __implements__ = createFeature('isSearchProfile'), \
                     Features.containsQuery, \
                     Features.isPortalContent, \
                     ContentBase.__implements__

    security = ClassSecurityInfo()
    security.declareProtected( CMFCorePermissions.View, 'query' )

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
        if REQUEST is None:
            return ''

        params = { 'profile_id' : self.getUid()
                 , 'batch_length' : getToolByName(self, 'portal_membership')\
                                   .getInterfacePreferences('viewing_document_number')
                 }

        if 'normative_filter' in self.getQuery().filters:
            action = 'search_results_ndocument'
        else:
            action = 'search_results'

        if REQUEST.has_key('portal_status_message'):
            params['portal_status_message'] = REQUEST['portal_status_message']

        return self.redirect(action = action, params=params)

InitializeClass( SearchProfile )

def addSearchProfile( self, id, query_id=None, title='', description='', REQUEST=None ):
    """
        Add a Search Profile
    """
    req = REQUEST or aq_get( self, 'REQUEST' )
    query = (query_id and req) and req.SESSION.get( ('search',query_id) ) or None
    self._setObject( id, SearchProfile( id, title, query, description=description ) )

    if REQUEST is not None:
        return self.redirect( message="Search profile added.", REQUEST=REQUEST )


class SearchQuery:

    security = ClassSecurityInfo()
    security.setDefaultAccess(1)

    text = ''
    oid = ''
    title = ''
    description = ''
    creation = ('','')
    owners = ()
    objects = ['bodies']
    implements = ()
    types = ()
    scope = 'global'
    location = None
    filters = ()
    transitivity = None
    doc_in_plan = None
    category = None
    state = None
    derivatives = None # if 1 - mean hasBase(category)
    filter_conditions = ()
    filter_query = None
    viewer = ''
    viewer_mode = ''

    def __init__( self, id=None, params=None ):
        if params:
            self.__dict__ = deepcopy( params )
        if id is None:
            id = str( randrange(1000000000) )
        self.id = id

    def __guarded_setattr__( self, name, value ):
        setattr( self, name, value )# why use this( above used setDefaultAccess(1) )

    def getId( self ):
        return self.id

    def copy( self ):
        return self.__class__(None, self.__dict__)
    clone=copy # remove clone in future

    def filter( self, results, parent ):
        for id in self.filters:
            if _registered_filters.has_key( id ):
                results = _registered_filters[ id ]( results, query=self, parent=parent )
        return results

    def __repr__( self ):
        return "<%s.%s instance at 0x%x, DATA='%s'>" % \
               ( self.__class__.__module__, self.__class__.__name__
               , id(self), repr(self.__dict__) )


InitializeClass( SearchQuery )

def registerFilter( id, filter ):
    _registered_filters[ id ] = filter

_registered_filters = {}

def initialize( context ):
    # module initialization callback
    context.register( registerFilter )

    context.registerContent( SearchProfile, addSearchProfile, SearchProfileType )
