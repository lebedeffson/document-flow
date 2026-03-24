"""
Object cataloguing tool.

$Editor: vpastukhov $
$Id: CatalogTool.py,v 1.95 2006/08/09 11:56:14 oevsegneev Exp $
"""
__version__ = '$Revision: 1.95 $'[11:-2]

from AccessControl import ClassSecurityInfo
from Acquisition import aq_get

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CatalogTool import CatalogTool as _CatalogTool
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser

import Config, Exceptions, Features
from CatalogSupport import QueryContext
from CompoundObjects import ZCatalogBase
from Monikers import MonikerBase
from ResourceUid import ResourceUid
from SearchProfile import SearchQuery
from SimpleObjects import ToolBase
from Utils import InitializeClass, getObjectImplements, \
        getSecurityManager


class CatalogTool( ToolBase, ZCatalogBase, _CatalogTool ):
    """ Portal catalog """
    _class_version = 1.16

    meta_type = 'NauSite Catalog Tool'
    id = _CatalogTool.id
    isPrincipiaFolderish = _CatalogTool.isPrincipiaFolderish

    security = ClassSecurityInfo()

    __implements__ = ( ToolBase.__implements__
                     , _CatalogTool.__implements__
                     , Features.isCatalog
                     )

    manage_options = _CatalogTool.manage_options # + ToolBase.manage_options
    manage_catalogFind = _CatalogTool.manage_catalogFind

    _catalog_key = 'nd_uid'
    _catalog_attr_key = 'CategoryAttributes'

    _catalog_indexes = [
            ('Title', 'FieldIndex'),
            ('Subject', 'KeywordIndex'),
            ('Description', 'FieldIndex'),
            ('Creator', 'FieldIndex'),
            ('SearchableText', 'TextIndexNG2'),
            ('Date', 'FieldIndex'),
            ('created', 'DateIndex'),
            ('effective', 'DateIndex'),
            ('expires', 'DateIndex'),
            ('modified', 'DateIndex'),
            ('allowedRolesAndUsers', 'KeywordIndex'),
            ('state', 'FieldIndex'),
            ('in_reply_to', 'FieldIndex'),
            ('registry_ids', 'KeywordIndex'),
            ('nd_uid', 'FieldIndex'),
            ('category', 'FieldIndex'),
            ('meta_type', 'FieldIndex'),
            ('portal_type', 'FieldIndex'),
            ('id', 'FieldIndex'),
            ('title', 'TextIndex'),
            ('path','PathIndex'),
            ('parent_path', 'FieldIndex'),
            ('implements', 'KeywordIndex'),
            ('hasBase', 'KeywordIndex'),
            ('CategoryAttributes', 'AttributesIndex'),
        ]

    _catalog_metadata = [
            'id',
            'Subject',
            'Title',
            'Description',
            'Type',
            'state',
            'Creator',
            'Date',
            'getIcon',
            'created',
            'effective',
            'expires',
            'modified',
            'CreationDate',
            'EffectiveDate',
            'ExpirationDate',
            'ModificationDate',
            'registry_ids',
            'category',
            'meta_type',
            'portal_type',
            'nd_uid',
            'implements',
            'CategoryAttributes',
            'hasBase',
            'getPrincipalVersionId',
        ]

    def __init__( self ):
        # instance constructor
        ToolBase.__init__( self )
        ZCatalogBase.__init__( self )

    security.declarePublic( 'attachmentSearchEnabled' )
    def attachmentSearchEnabled( self ):
        """
        """
        return Config.AttachmentSearchable

    def getQuery( self, id=None, profile=None, copy=None, REQUEST=None ):
        """
        """
        REQUEST = REQUEST or aq_get( self, 'REQUEST' )
        query   = None

        SESSION = REQUEST.SESSION
        if id is not None:
            query = SESSION.get(( 'search',id ))
            # the query may have expired from session
            #if query is None:
            #    raise KeyError, id

        elif profile is not None:
            ob = self.getObjectByUid( profile, feature='containsQuery' )
            if ob is None:
                raise KeyError, profile
            query = ob.getQuery()

        if query is None:
            query = SearchQuery()
        elif copy:
            query = query.clone()

        key = ('search', query.getId())
        if SESSION.get( key ) != query:
            SESSION.set( key, query )

        return query

    def executeQuery( self, query ):
        """
        """
        indexes = {}

        if query.state:
            indexes['state'] = query.state

        indexes['SearchableText'] = query.text
        indexes['id'] = query.oid
        indexes['Title'] = query.title
        indexes['Description'] = query.description

        if query.category:
            if query.derivatives:
                indexes['hasBase'] = query.category
            else:
                indexes['category'] = query.category

        if query.creation:
            if query.creation[0] and query.creation[1]:
                indexes['created'] = { 'query':query.creation
                                     , 'range':'min:max'
                                     }
            elif query.creation[0]:
                indexes['created'] = { 'query':query.creation[0]
                                     , 'range':'min'
                                     }
            elif query.creation[1]:
                indexes['created'] = { 'query':query.creation[1]
                                     , 'range':'max'
                                     }

        if query.owners:
            indexes['Creator'] = query.owners

        if query.types:
            indexes['meta_type'] = query.types

        else:
            features = indexes['implements'] = []

            if 'bodies' in query.objects:
                features.append('isDocument')

            if 'attachments' in query.objects:
                features.append('isAttachment')

            if 'folders' in query.objects:
                features.append('isContentStorage')

            if 'versions' in query.objects:
                features.append('isVersion')

        if query.implements:
            indexes['implements'] = query.implements

        if not query.location:
            pass

        elif query.scope == 'recursive':
            indexes['path'] = query.location

        elif query.scope == 'local':
            indexes['parent_path'] = query.location

        if hasattr(query, 'attributes'):
            indexes['CategoryAttributes'] = query.attributes
            # XXX why deleting category value?
            del indexes['category']

        results = self.searchResults( **indexes )
        results = query.filter( results, parent=self.parent() )

        return self.sortResults( results, merge=1 )

    def searchResults( self, REQUEST=None, restricted=True, **kwargs ):
        """
            Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        if restricted is not Trust and 'allowedRolesAndUsers' in self.indexes():
            user = _getAuthenticatedUser( self )
            kwargs['allowedRolesAndUsers'] = QueryContext( self._listAllowedRolesAndUsers( user ) )

        return self.unrestrictedSearch( REQUEST, **kwargs )

    __call__ = searchResults

    def _listAllowedRolesAndUsers( self, user ):
        
        result = user.listAccessTokens( include_userid=True,
                                        userid_prefix='user:',
                                        include_positions=True,
                                        include_divisions=True,
                                        include_groups=True,
                                        include_roles=True,
                                        role_prefix=''
                                      )
    #    result.append('Anonymous')
        return result

    def getObjectByUid( self, uid, feature=(), restricted=True ):
        """
            Returns an object, given it's UID.
        """
        # TODO should take 'default' argument
        if not uid:
            return None

        if isinstance( uid, MonikerBase ):
            uid = uid.uid()

        if isinstance( uid, ResourceUid ):
            # dereference Uid
            try:
                object = uid.deref( self )
            except Exceptions.LocatorError:
                return None

            # verify requested features
            if feature and not getObjectImplements( object, feature ):
                return None

            if restricted is Trust:
                return object

            # check permission to access the object
            validate = getSecurityManager().validate
            parent   = object.parent()
            # validate is a mess -- either returns False or raises exception
            try:
                if validate( parent, parent, object.getId(), object ):
                    return object
                return None
            except Exceptions.Unauthorized:
                return None

        # uid is a plain string -- fetch and dereference brains item
        metadata = self.getMetadataByUid( uid, feature, restricted )
        if metadata is None:
            return None
        return metadata.getObject()

    def getMetadataByUid( self, uid, feature=(), restricted=True ):
        """
            Returns an object's metadata, given it's UID.
        """
        if not uid:
            return None
        if isinstance( uid, MonikerBase ):
            uid = uid.uid()
        if isinstance( uid, ResourceUid ):
            uid = str(uid)

        query = { self._catalog_key : uid,
                  'implements'      : feature,
                  'restricted'      : restricted }

        results = self.searchResults( **query )
        if not results:
            return None

        assert len(results) == 1, 'uid %s is not unique' % str(uid)
        return results[0]

    def notifyCatalogRefreshed( self ):
        """
            Callback. invoked after catalog refreshed
        """
        #XXX do not inherit FollowupTool and DocumentLinkTool from CatalogTool
        if 'implements' not in self.indexes():
            return

        items = self.unrestrictedSearch( implements='reindexAfterRefresh' )
        for item in items:
            item.getObject().reindexObject( idxs=['getIcon'] )

    def getIndexableObjectVars( self, object ):
        # Wraps the object with workflow and accessibility
        # information just before cataloging.
        wf = getToolByName( self, 'portal_workflow', None )
        if wf is not None:
            vars = wf.getCatalogVariablesFor( object )
        else:
            vars = super(CatalogTool, self).getIndexableObjectVars( object )
        return vars


InitializeClass( CatalogTool )

def initialize( context ):
    # module initialization callback

    context.registerTool( CatalogTool )
