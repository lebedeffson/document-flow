"""
Storage and catalog for links between objects.

$Editor: vpastukhov $
$Id: DocumentLinkTool.py,v 1.113 2006/07/11 09:10:50 oevsegneev Exp $
"""
__version__ = '$Revision: 1.113 $'[11:-2]

from types import NoneType, StringType, DictType, TupleType

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from AccessControl.Owned import Owned
from AccessControl.SpecialUsers import emergency_user as EmergencyUser
from AccessControl.User import nobody as NobodyUser
from DateTime import DateTime
from ZPublisher.HTTPRequest import record as _zpub_record
from ZODB.PersistentMapping import PersistentMapping

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _checkPermission

import Config, Exceptions
from CatalogTool import CatalogTool
from Monikers import Moniker, LinkMoniker
from ResourceUid import ResourceUid, listResourceKeys, \
        getDefaultResourceType, getResourceHandler, getCatalogByType
from SimpleObjects import ItemBase, InstanceBase, ContentBase, ContainerBase
from SyncableContent import SyncableContent
from Utils import InitializeClass, getObjectByUid, listClipboardObjects, \
        isSequence, cookId, addQueryString, translate, splitpath


class Link( InstanceBase, Owned, SyncableContent ):
    """
        Link represents some relation between two document items.
    """
    _class_version = 1.37

    meta_type = 'Link'

    __resource_type__ = 'link'

    security = ClassSecurityInfo()

    manage_options = InstanceBase.manage_options + \
                     Owned.manage_options

    _properties = InstanceBase._properties + (
            { 'id':'creation_date', 'type':'string', 'mode':'' },
            { 'id':'modification_date', 'type':'string', 'mode':'' },
            { 'id':'source_uid', 'type':'string', 'mode':'' },
            { 'id':'target_uid', 'type':'string', 'mode':'' },
            { 'id':'target_removed', 'type':'boolean', 'mode':'w' },
            { 'id':'relation', 'type':'string', 'mode':'w' },
        )

    # default attribute values
    target_removed = False
    target_locked  = False
    extra          = None

    def __init__( self, id, source, target, relation, lock_target=False, extra=None ):
        """
            Creates persistent link between source and target objects.

            Arguments:

                'id' -- the link identifier, string

                'source' -- UID of the object this link originates from,
                            'ResourceUid' instance

                'target' -- UID of the object this link points to,
                            'ResourceUid' instance

                'relation' -- type ID of the relation

                'extra' -- extra parameters that the link can store
        """
        InstanceBase.__init__( self, id )

        if not isinstance( source, ResourceUid ):
            raise TypeError, source
        if not isinstance( target, ResourceUid ):
            raise TypeError, target

        self.creation_date = self.modification_date = DateTime()

        self.source_uid = source
        self.target_uid = target

        self.relation = relation
        self.target_locked = lock_target

        # extra dictionary handles additional link parameters
        # XXX: ensure that extra values are strings
        if type(extra) is DictType:
            self.extra = extra

        self.source_data = PersistentMapping()
        self.target_data = PersistentMapping()

    def _initstate( self, mode ):
        # initializes attributes
        if not InstanceBase._initstate( self, mode ):
            return 0

        if mode and not hasattr( self, 'creation_date' ): # < 1.35
            self.creation_date = self.bobobase_modification_time()

        if mode and not hasattr( self, 'modification_date' ): # < 1.35
            self.modification_date = self.bobobase_modification_time()

        if hasattr( self, 'source_uid' ) and type( self.source_uid ) is StringType: # < 1.28
            self.source_uid = ResourceUid( self.source_uid )

        if hasattr( self, 'dest_uid' ): # < 1.28
            self.target_uid = ResourceUid( self.dest_uid )
            del self.dest_uid

            extra = self.extra
            if extra:
                source_uid = self.source_uid
                target_uid = self.target_uid
                for key, value in extra.items():
                    if key.startswith('source_'):
                        setattr( source_uid, key[ len('source_'): ], value )
                    elif key.startswith('destination_'):
                        setattr( target_uid, key[ len('destination_'): ], value )
                    elif key in ['field_id','uname','status']:
                        setattr( source_uid, key, value )
                    else:
                        continue
                    del extra[ key ]

        if hasattr( self, 'dest_removed' ): # < 1.29
            self.target_removed = not not self.dest_removed
            del self.dest_removed

        if hasattr( self, 'source' ): # < 1.32
            self.source_data = self.source
            del self.source

        if hasattr( self, 'destination' ): # < 1.32
            self.target_data = self.destination
            del self.destination

        if hasattr( self, 'relation_type' ): # < 1.47.2.1.2.1
            if self.relation_type == 0:
                self.relation = 'dependence'
            else:
                self.relation = 'reference'
            del self.relation_type
            if self.relation_direction:
                temp = self.source_uid
                self.source_uid = self.target_uid
                self.target_uid = temp
                temp = self.source_data
                self.source_data = self.target_data
                self.target_data = temp
            del self.relation_direction

        if mode and self.relation == 'dependence' \
                and not self.__dict__.has_key('target_locked'): # < 1.36
            self.target_locked = True

        return 1

    security.declareProtected( CMFCorePermissions.View, 'Creator' )
    Creator = ContentBase.Creator.im_func

    security.declareProtected( CMFCorePermissions.View, 'created' )
    def created( self ):
        """
            Returns date this link was created (Dublin Core element).

            Result:

                'DateTime' object.
        """
        return self.creation_date

    security.declareProtected( CMFCorePermissions.View, 'modified' )
    def modified( self ):
        """
            Returns date this link was last modified (Dublin Core element).

            Result:

                'DateTime' object.
        """
        return self.modification_date

    security.declareProtected( CMFCorePermissions.View, 'getSourceUid' )
    def getSourceUid( self, name=None, default=None ):
        """
            Returns the link's source object UID.

            Arguments:

                'name' -- optional name of the UID parameter to return

                'default' -- default value for the name of the UID parameter

            Result:

                'ResourceUid' instance or value of the named UID parameter.
        """
        if name:
            return self.source_uid.get( name, default )
        else:
            return self.source_uid

    security.declareProtected( CMFCorePermissions.View, 'getTargetUid' )
    def getTargetUid( self, name=None, default=None ):
        """
            Returns the link's target object UID.

            Arguments:

                'name' -- optional name of the UID parameter to return

                'default' -- default value for the name of the UID parameter

            Result:

                'ResourceUid' instance or value of the named UID parameter.
        """
        if self.target_removed:
            return None
        if name:
            return self.target_uid.get( name, default )
        else:
            return self.target_uid

    security.declareProtected( CMFCorePermissions.View, 'getSourceMetadata' )
    def getSourceMetadata( self, name=None, raise_exc=False ):
        """
            Returns the link's source object metadata.

            Arguments:

                'name' -- attribute name to get
        """
        data = None
        uid  = self.source_uid
        catalog = getCatalogByType( self, uid )

        if catalog:
            data = catalog.getMetadataByUid( uid )
            if data is None and raise_exc:
                raise LookupError

        elif raise_exc:
            raise TypeError

        data = data or self.source_data
        if name and data.has_key(name):
            return data[ name ]
        return data

    security.declareProtected( CMFCorePermissions.View, 'getTargetMetadata' )
    def getTargetMetadata( self, name=None, raise_exc=False ):
        """
            Returns the link's target object metadata.

            Arguments:

                'name' -- attribute name to get
        """
        data = None
        if not self.target_removed:
            uid = self.target_uid
            catalog = getCatalogByType( self, uid )

            if catalog:
                data = catalog.getMetadataByUid( uid )
                if data is None and raise_exc:
                    raise LookupError

            elif raise_exc:
                raise TypeError

        elif raise_exc:
            raise LookupError

        data = data or self.target_data
        if name and data.has_key(name):
            return data[ name ]
        return data

    security.declareProtected( CMFCorePermissions.View, 'getSourceObject' )
    def getSourceObject( self, **kwargs ):
        """
            Returns the object this link originates from.

            Keyword arguments:

                '**kwargs' -- optional name-value pairs to pass
                              to the 'ResourceUid' dereference method

            Result:

                The source object or 'None'.
        """
        try:
            return self.getSourceUid().deref( self, **kwargs )
        except LookupError:
            return None

    security.declareProtected( CMFCorePermissions.View, 'getTargetObject' )
    def getTargetObject( self, **kwargs ):
        """
            Returns the object this link points to.

            Keyword arguments:

                '**kwargs' -- optional name-value pairs to pass
                              to the 'ResourceUid' dereference method

            Result:

                The target object or 'None'.
        """
        if self.target_removed:
            return None
        try:
            return self.getTargetUid().deref( self, **kwargs )
        except LookupError:
            return None

    security.declareProtected( CMFCorePermissions.View, 'isSourceAllowed' )
    def isSourceAllowed( self ):
        """
            Checks whether the user has permission to access the source object.

            Result:

                Boolean.
        """
        try:
            self.getSourceMetadata( raise_exc=True )
        except TypeError:
            return _checkPermission( CMFCorePermissions.View, self.getSourceObject() )
        except LookupError:
            return False
        else:
            return True

    security.declareProtected( CMFCorePermissions.View, 'isTargetAllowed' )
    def isTargetAllowed( self ):
        """
            Checks whether the user has permission to access the target object.

            Result:

                Boolean.
        """
        if self.target_removed:
            return False
        try:
            self.getTargetMetadata( raise_exc=True )
        except TypeError:
            return _checkPermission( CMFCorePermissions.View, self.getTargetObject() )
        except LookupError:
            return False
        else:
            return True

    security.declareProtected( CMFCorePermissions.View, 'getRelation' )
    def getRelation( self ):
        """
            Returns this link's relation type ID.

            Result:

                String.
        """
        return self.relation

    security.declareProtected( CMFCorePermissions.View, 'getRelationInfo' )
    def getRelationInfo( self, name=None ):
        """
            Returns this link's relation type properties structure.

            Arguments:

                'name' -- optional name of the property to return

            Result:

                Mapping object or value of the named property.
        """
        return self.parent().getRelationInfo( self.relation, name )

    security.declarePrivate( 'notifyTargetRemoved' )
    def notifyTargetRemoved( self ):
        """
            Notifies the link of the target object removal.
        """
        self.target_uid = None
        self.target_removed = True
        self.parent().reindexObject( self, idxs=['TargetUid','target_removed'] )
        self.setModificationDate()

    security.declareProtected( CMFCorePermissions.View, 'isTargetRemoved' )
    def isTargetRemoved( self ):
        """
            Returns true if the target object is removed.

            Result:

                Boolean.
        """
        return self.target_removed

    security.declareProtected( CMFCorePermissions.View, 'isTargetLocked' )
    def isTargetLocked( self ):
        """
            Returns true if the target object is locked by the link
            (and thus cannot be removed).

            Result:

                Boolean.
        """
        return self.target_locked

    security.declareProtected( CMFCorePermissions.View, 'isTargetWeak' )
    def isTargetWeak( self ):
        """
            Returns true if the link can be safely deleted along with
            its target object.

            Result:

                Boolean.
        """
        return self.getRelationInfo('weak_target')

    security.declarePrivate( 'updateMetadata' )
    def updateMetadata( self, source=None, target=None ):
        """
            Remembers objects properties according to Config.DocumentLinkProperties.

            These properties could be showed to user if the documents will
            be removed or inaccessible due security restrictions.

            Arguments:

                'source' -- source object

                'target' -- destination object
        """
        for ob, data in (source, self.source_data), \
                        (target, self.target_data):
            if ob is None:
                continue
            data.clear()

            for attr in Config.DocumentLinkProperties:
                if hasattr(aq_base(ob), attr):
                    value = getattr(ob, attr, '')
                    if callable(value):
                        value = value()
                else:
                    value = ''
                data[ attr ] = value

        self.setModificationDate()

    security.declarePrivate( 'setModificationDate' )
    def setModificationDate( self, date=None ):
        """
            Changes the date when the link was last modified.

            Arguments:

                'date' -- 'DateTime' instance; if omitted,
                          sets the date to the current date and time
        """
        if date is None:
            date = DateTime()
        self.modification_date = date
        self.parent().reindexObject( self, idxs=['modified'] )

    security.declarePrivate( 'cloneLink' )
    def cloneLink( self, source=None, raise_exc=False, **kwargs ):
        """
            Creates a copy of this link for another source object.

            Arguments:

                'source' --

                '**kwargs' -- optional name-value pairs to pass
                              to the 'ResourceUid' dereference method
        """
        if source is not None:
            links = getToolByName( source, 'portal_links' )
        else:
            links = self.parent()

        # check for already existing links
        # with the same source if 'unique_source' is set and
        # with the same target if 'unique_target' is set
        duplicates = []
        rel_info = links.getRelationInfo( self.getRelation() )
        if rel_info.get( 'unique_source' ):
            results = links.searchLinks( source=self.getSourceUid() )
            if len( results ) > 0:
                duplicates.append( results[0] )
        if rel_info.get( 'unique_target' ):
            results = links.searchLinks( target=self.getTargetUid() )
            if len( results ) > 0:
                duplicates.append( results[0] )
        if len( duplicates ) > 0:
            if not raise_exc:
                return
            raise Exceptions.SimpleError( "Link to the object %(link.target)s with relation \"%(link.relation)s\" already exists.",
                                          link=LinkMoniker( duplicates[0]['id'] ) )

        # first create a downright copy
        new = self.copyObject( links )
        source_uid = new.source_uid
        target_uid = new.target_uid

        if source is not None:
            # check that type of the new object matches old source type
            uid = links.getResourceUid( source, kwargs, 'source' )
            if not uid or uid.type != self.source_uid.type:
                raise TypeError, source

            # change source uid to the new object's one
            source_uid.update( uid )

            # for intra-object links, change target uid too
            if self.source_uid.base() == self.target_uid.base():
                target_uid.update( uid.base() )

        # update copy's uids from keyword arguments
        for key, value in kwargs.items():
            if key.startswith( 'source_' ):
                setattr( source_uid, key[ len('source_'): ], value )

            elif key.startswith( 'target_' ):
                setattr( target_uid, key[ len('target_'): ], value )

        # TODO add check for already existing link
        #print 'cloneLink', new.source_uid.dict(), new.target_uid.dict(), new.relation
        links.reindexObject( new, idxs=['SourceUid','TargetUid'] )

        if source is None:
            source = source_uid.deref( new )
        new.updateMetadata( source )

    security.declarePrivate( 'SourceUid' )
    def SourceUid( self ):
        # helper method for the links catalog index
        return _getLinkKey( self.source_uid.dict() )

    security.declarePrivate( 'TargetUid' )
    def TargetUid( self ):
        # helper method for the links catalog index
        if self.target_removed:
            return []
        return _getLinkKey( self.target_uid.dict() )

    security.declarePrivate( 'Extra' )
    def Extra( self ):
        # helper method for the links catalog index
        return _getLinkKey( self.extra )

    def _containment_onAdd( self, item, container ):
        self.parent().indexObject( self )

    def _containment_onDelete( self, item, container ):
        self.parent().unindexObject( self )

    security.declarePrivate( 'manage_fixupOwnershipAfterAdd' )
    def manage_fixupOwnershipAfterAdd( self ):
        membership = getToolByName( self, 'portal_membership' )
        user = membership.getAuthenticatedMember().getUser()
        if aq_base(user) is not EmergencyUser:
            self.changeOwnership(user)

InitializeClass( Link )

class LinkBrain( object ):

    def getObject(self, REQUEST=None):
        """Try to return the object for this record"""
        return self.aq_parent._getOb( splitpath( self.getPath() )[-1], None )

class DocumentLinkTool( ContainerBase, CatalogTool ):
    """
        Portal document link tool is container for links objects.
        Also provides possibility to catalog links.
    """
    _class_version = 1.26

    meta_type = 'NauSite DocumentLink Tool'
    id = 'portal_links'

    __implements__ = ( ContainerBase.__implements__
                     , CatalogTool.__implements__
                     )

    security = ClassSecurityInfo()

    manage_options = ContainerBase.manage_options[ :1 ] + \
                     CatalogTool.manage_options[ 1: ]

    all_meta_types = [
            { 'name'   : Link.meta_type,
              'action' : manage_options[0]['action'] },
        ]

    _uid_index = 'id'

    _catalog_indexes = [
            ('id', 'FieldIndex'),
            ('Creator', 'FieldIndex'),
            ('created', 'DateIndex'),
            ('modified', 'DateIndex'),
            ('SourceUid', 'KeywordIndex'),
            ('TargetUid', 'KeywordIndex'),
            ('target_removed', 'FieldIndex'),
            ('relation', 'FieldIndex'),
            ('Extra', 'KeywordIndex'),
        ]

    _catalog_metadata = [
            'id',
            'Creator',
            'created',
            'modified',
            'source_uid',
            'target_uid',
            'target_removed',
            'relation',
        ]

    _keyword_indexes = [
            ('source_keys', 'source', 'SourceUid'),
            ('target_keys', 'target', 'TargetUid'),
            ('extra',       '',       'Extra'),
        ]

    _v_brains = LinkBrain

    def __init__( self ):
        CatalogTool.__init__( self )
        ContainerBase.__init__( self )

    security.declarePublic( 'listRelations' )
    def listRelations( self, allow_manual_only=True ):
        """
            Returns types of relation as Dict {'id' : 'title'}.

            Arguments:
            
                'allow_manual_only' -- if True, returns only types that are 
                    _available_for_manual_creation_, otherwise returns all 
                    registered types
        """
        # XXX must return list
        result = {}
        for id, info in _relation_types.items():
            if (not allow_manual_only) or (allow_manual_only and info['allow_manual']):
                result[ id ] = info['title']

        return result or None


    security.declarePublic( 'getRelationInfo' )
    def getRelationInfo( self, id, name=None, default=Missing ):
        """
            Returns relation information.

            Arguments:

                'id' -- relation type id (string)

            Result:

                Dictionary or None.
        """
        try:
            info = _relation_types[ id ]
        except KeyError:
            if default is Missing:
                raise Exceptions.SimpleError( "Invalid relation", id=id )
            return default

        if name:
            if default is Missing:
                default = None
            return info.get( name, default )
        else:
            return info.copy()

    security.declareProtected( CMFCorePermissions.View, 'restrictedLink' )
    def restrictedLink( self, source=None, target=None, relation=None, extra=None, replace=False, REQUEST=None, **kwargs ):
        """
            Creates link object using given data.

            Wrapper for createLink method. Makes all security and other check.
            Converts relation into two parameters - relation_type and relation_direction.
            Then calls createLink(). Returns id of the created link.

            Arguments:

                'source' -- Uid of the 'sourse' object (from which the link being created).

                'target' -- Uid of the 'destination' object (to which the link being created).

                'relation' -- Selected relation id.

                'REQUEST' -- REQUEST object.

                '**kw' -- extra parameters to store

            Result:

                String.
        """
        source   = source   or REQUEST and REQUEST.get('source_uid')
        target   = target   or REQUEST and REQUEST.get('target_uid')
        relation = relation or REQUEST and REQUEST.get('relation')

        link = self.createLink( source, target, relation, extra, replace, True, **kwargs )

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect( addQueryString( REQUEST['HTTP_REFERER'], portal_status_message='Link was successfully created.' ) )

        return link.getId()

    security.declarePrivate( 'createLink' )
    def createLink( self, source, target, relation, extra=None, replace=False, restricted=False, **kwargs ):
        """
            Creates link between source and destination objects.

            Puts created link object in self (as object manager) and catalogs it.
            Returns id of the created link.

            Positional arguments:

                'source' -- the 'source' object (from which the link being created).

                'target' -- the 'destination' object (to which the link being created).

                'relation' -- relation id

            Keyword arguments:

                'extra' -- mapping of arbitrary data for the link to keep

                'replace' -- whether an existing link should be replaced

                'restricted' -- verify current user's permission to link
                                the objects

                '**kwargs' -- additional name-value arguments; names starting
                              with 'source_' or 'target_' will be added to the
                              corresponding object qualification (with the prefix
                              removed), all the rest -- to the 'extra' mapping

            Result:

                'Link' object.
        """
        source_uid = self.getResourceUid( source, kwargs, 'source' )
        target_uid = self.getResourceUid( target, kwargs, 'target' )

        if not (source_uid and target_uid and relation):
            raise Exceptions.SimpleError( "Too few data: source %s --> %s, target %s --> %s, relation %s"% (`source`, source_uid, `target`, target_uid, `relation`) )

        rel_info = self.getRelationInfo( relation )
        query = { 'relation' : relation }

        if not rel_info['allow_internal']:
            if source_uid.base() == target_uid.base():
                raise Exceptions.SimpleError( "The object %(object)s cannot by linked to itself using relation \"%(relation)s\".",
                                              object=Moniker(source_uid),
                                              relation=(translate( self, rel_info['title'] ) or relation) )

        if extra is None:
            extra = kwargs
        else:
            extra.update( kwargs )

        # if an endpoint can have a single bound link,
        # exclude the other endpoint from the query
        # TODO: if both unique_source and unique_target are set,
        # must check existing links twice

        if not rel_info['unique_source']:
            query['target'] = target_uid
        if not rel_info['unique_target']:
            query['source'] = source_uid

        links = self.searchLinks( **query )
        if links:
            if not replace:
                raise Exceptions.SimpleError( "Link to the object %(link.target)s with relation \"%(link.relation)s\" already exists.",
                                              link=LinkMoniker( links[0]['id'] ) )

            for link in links:
                if link['source_uid'] == source_uid and \
                   link['target_uid'] == target_uid: # TODO: and link.extra == extra:
                    #print 'createLink exists', link['id'], source_uid, target_uid, relation
                    return link.getObject()

            # TODO
            #if restricted and not _checkPermission( CMFCorePermissions.View, link ):
            #    raise Exceptions.Unauthorized( "You are not allowed to remove link" )
            links = [ link.getObject() for link in links ]
            for link in links:
                self.removeLink( link, restricted=Trust )

        if not isinstance( source, ItemBase ):
            # check whether the source object exists
            try:
                source = source_uid.deref( self )
            except LookupError:
                raise Exceptions.SimpleError( "Link source does not exist or not available" )

            # check whether the user is permitted to create links from the source
            if restricted and not _checkPermission( CMFCorePermissions.View, source ):
                raise Exceptions.Unauthorized( "You are not allowed to create link between these documents" )

        if not isinstance( target, ItemBase ):
            # check whether the target object exists
            try:
                target = target_uid.deref( self )
            except LookupError:
                raise Exceptions.SimpleError( "Link destination does not exist or not available" )

        if source.implements('isLockable'):
            source.failIfLocked()

        idx = len( self )
        id = cookId( self, prefix='link', idx=idx )
        #print 'createLink', id, source_uid, target_uid, relation, extra, source, target
        link = Link( id, source_uid, target_uid, relation,
                     lock_target=rel_info['lock_target'], extra=extra )

        link = self.addObject( link )
        link.updateMetadata( source, target )

        return link

    security.declareProtected( CMFCorePermissions.View, 'removeLink' )
    def removeLink( self, link, source=None, restricted=True ):
        """
            Removes link from catalog and storage.
            Checks 'delete' permissions on the source object and then removes link with id equal to 'link_id' from catalog and storage.

            Arguments:
                'link_id' -- Id of the link to be removed.
                'source' -- Optional parameter, if omitted, link.getSourceObject() will be called to get it.
        """
        restricted = restricted is not Trust

        if type(link) is StringType:
            link = self._getOb( link, None )
        if link is None:
            return # no such link

        object = source or link.getSourceObject()

        if object is not None:
            if object.implements('isLockable'):
                object.failIfLocked()

            if restricted and not _checkPermission( CMFCorePermissions.ModifyPortalContent, object ):
                raise Exceptions.Unauthorized, 'You are not allowed to remove link between these documents'

        #print 'removeLink', link.getId()
        self.deleteObjects( link.getId() )

    security.declareProtected( CMFCorePermissions.View, 'removeLinks' )
    def removeLinks( self, ids=None, restricted=True, REQUEST=None ):
        """
            Removes posted in REQUEST links.
            Calls removeLink() for each id.

            Arguments:
                'ids' -- List of links identifiers to be removed.
                'REQUEST' -- REQUEST object.
        """
        links_to_remove = ids or REQUEST.get('remove_links', [])
        for link in links_to_remove:
            self.removeLink( link, restricted=restricted )

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(addQueryString(REQUEST['HTTP_REFERER'], portal_status_message='Links were successfully removed.'))

    security.declareProtected( CMFCorePermissions.View, 'removeBoundLinks' )
    def removeBoundLinks( self, object, force=False ):
        """
            Deletes all links bound with the object.

            Deletes all links bound with given object.
            For documents that are source objects all links will be removed,
            for documents that are destination objects for links there will be marked
            (in links) that destination removed.
            Also checks permissions to delete objects.

            Arguments:

                'object' -- Object for which it is needed to remove bound links.

                'force' -- boolean flag, if true then remove links where
                           the object is target; otherwise exception is raised
                           unless no such links exist (default)
        """
        uid = self.getResourceUid( object )
        if not uid:
            return

        links_from = [ link.getObject() for link in self.searchLinks( source=uid ) ]
        links_to   = [ link.getObject() for link in self.searchLinks( target=uid ) ]

        if not links_from and not links_to:
            return

        if not force and links_to:
            for link in links_to:
                if uid <= link.getSourceUid():
                    continue
                if link.isTargetLocked():
                    raise Exceptions.SimpleError( 'links.cannot_remove_target', target=Moniker(object) )

        for link in links_to:
            if link.isTargetWeak():
                self.removeLink( link=link, source=object, restricted=Trust )
            else:
                link.notifyTargetRemoved()

        for link in links_from:
            self.removeLink( link=link, source=object, restricted=Trust )

    security.declarePrivate( 'cloneLinks' )
    def cloneLinks( self, source, other, all=False ):
        """
            Copies links owned by the given object to another one.

            Arguments:

                'source' -- the links owner object

                'other' -- the object for links to copy to

                'all' -- copy links owned by subobjects too;
                         optional boolean flag, false by default
        """
        results = self.searchLinks( source=source )
        if not results:
            return

        if all:
            for item in results:
                item.getObject().cloneLink( other )
            return

        uid = self.getResourceUid( source )
        keys = listResourceKeys( source )

        for item in results:
            uid = item['source_uid']
            relinfo = self.getRelationInfo( item['relation'] )

            # TODO this filtering functionality better go into searchLinks
            known = keys[:]
            known.append( relinfo['source_key'] )
            known.append( relinfo['target_key'] )

            for key in uid.dict().keys():
                if key not in known:
                    break
            else:
                item.getObject().cloneLink( other )

    security.declareProtected( CMFCorePermissions.View, 'searchLinks' )
    def searchLinks( self, internal=True, REQUEST=None, **query ):
        """
            Searches for links meeting condition given in query.

            Arguments:

                'source' -- an object or UID to limit the search to links
                            originating from this object

                'target' -- an object or UID to limit the search to links
                            pointing to this object

                'source_inclusive' -- if true, additionally search for links
                            originating from subobjects of the source object

                'target_inclusive' -- if true, additionally search for links
                            pointing to subobjects of the target object

                'internal' -- boolean flag, whether intra-object links should
                              be included in the result; True by default

                'REQUEST' -- Zope request object

                '**query' -- additional name-value pairs specifying
                             the further search conditions

            Result:

                List of ZCatalog brains.
        """
        # build mapping index_name -> index_type
        all_indexes = {}
        for item in self.enumerateIndexes():
            all_indexes[ item[0] ] = item[1]

        # prepare parameter dictionaries for keyword indexes
        kw_indexes = []
        for name, prefix, index in self._keyword_indexes:
            # extract source_keys and target_keys parameters
            if query.has_key( name ):
                keys = query[ name ]
                del query[ name ]
            else:
                keys = {}

            object = None
            inclusive = False

            if prefix:
                if query.has_key( prefix ):
                    object = query[ prefix ]
                    del query[ prefix ]
                prefix += '_'
                if query.has_key( prefix+'inclusive' ):
                    inclusive = query[ prefix+'inclusive' ]
                    del query[ prefix+'inclusive' ]

            # build query arguments from source and target objects
            if object is not None:
                if isSequence( object ):
                    raise NotImplementedError, "Searching for multiple link endpoints is not supported."

                if not isinstance( object, ResourceUid ):
                    object = self.getResourceUid( object, query, prefix )
                    if object is None:
                        # not a linkable object
                        return []

                object = object.dict()
                if inclusive:
                    for key in listResourceKeys():
                        keys[ key ] = object[ key ]
                else:
                    keys.update( object )

            kw_indexes.append( (prefix, index, keys) )

        # additional parameters can be passed as name-value pairs
        for key, value in query.items():
            # do not search for None in indexes
            if value is None:
                del query[ key ]
                continue

            # leave index queries intact
            if all_indexes.has_key( key ) or key.startswith('sort_'):
                continue
            if key.endswith('_usage') and all_indexes.has_key( key[:-6] ):
                continue
            # remove UID or Extra parameters from the catalog query
            del query[ key ]

            # handle a set of values
            if isSequence( value ):
                # skip an empty sequence
                if not value:
                    continue
                if len(value) > 1:
                    raise NotImplementedError, "Searching for multiple values of UID parameter is not supported."
                # use the first and the only item
                value = value[0]

            # stuff additional parameters into corresponding mappings
            for prefix, index, keys in kw_indexes:
                if prefix and key.startswith( prefix ):
                    keys[ key[ len(prefix): ] ] = value
                    break

        # convert mappings to sequences for keyword indexes
        for prefix, index, keys in kw_indexes:
            if keys:
                if prefix and keys.has_key('uid') and not keys.has_key('type'):
                    # uid is given w/o type, use default one
                    keys['type'] = getDefaultResourceType()
                query[ index ] = { 'query' : _getLinkKey( keys ), 'operator' : 'and' }

        #print 'searchLinks', query
        results = CatalogTool.unrestrictedSearch( self, REQUEST, **query )

        # filter out intra-object links if requested
        if not internal:
            results = [ link for link in results if not link['target_removed'] and \
                                 link['source_uid'].base() != link['target_uid'].base() ]

        return results

    security.declarePrivate( 'getResourceUid' )
    def getResourceUid( self, object, kwargs=None, prefix=None ):
        """
        """
        prefix  = prefix and prefix+'_' or ''
        service = kwargs and kwargs.get( prefix+'service' ) or None

        try:
            # if the object is ResourceUid, this constructor creates a copy (good)
            uid = ResourceUid( object, service=service, context=self )
        except TypeError:
            # not a linkable object
            return None

        if kwargs:
            if prefix:
                keys = kwargs.get( prefix+'keys' )

                if keys is not None:
                    del kwargs[ prefix+'keys' ]
                    for key, value in keys.items():
                        setattr( uid, key, value )

                for key, value in kwargs.items():
                    if key.startswith( prefix ):
                        setattr( uid, key[ len(prefix): ], value )
                        del kwargs[ key ]
            else:
                for key, value in kwargs.items():
                    setattr( uid, key, value )

        return uid

    security.declareProtected( CMFCorePermissions.View, 'getLinkKey' )
    def getLinkKey( self, object ):
        if isinstance( object, ResourceUid ):
            return _getLinkKey( object.dict() )
        return []

    def _exportLinks( self, object ):
        """
            Finds all links bound to the object and exports them.

            Arguments:

                'object' -- object of any registered type

            Result:

                Dictionary { link_id: pickled_data, ... }.
        """
        results = self.searchLinks( source=object ) + self.searchLinks( target=object )
        if not results:
            return None

        data = {}
        for res in results:
            data[ res['id'] ] = res.getObject()._remote_export()

        return data

    def _importLinks( self, file ):
        """
            Imports links exported by '_exportLinks'.
        """
        links = {}
        for id, data in file.items():
            links[ id ] = self._p_jar.importFile( data )

        uids = [ ln.getSourceUid() for ln in links.values() ] + \
               [ ln.getTargetUid() for ln in links.values() ]

        catalog = getToolByName( self, 'portal_catalog' )
        results = catalog.unrestrictedSearch( nd_uid=uids )

        found = {}
        for res in results:
            found[ res['nd_uid'] ] = res.getObject()

        for id, link in links.items():
            src = found.get( link.getSourceUid() )
            dst = found.get( link.getTargetUid() )

            old = self._getOb( id, None )

            if old is not None:
                old.updateMetadata( src, dst )
                continue

            if src is None or ( dst is None and not link.isTargetRemoved() ):
                continue

            self._setObject( id, link )
            self[ id ].updateMetadata( src, dst )

    security.declarePublic( 'listClipboardObjects' )
    def listClipboardObjects( self, item=None, REQUEST=None ):
        """
            Returns a list of objects in the clipboard for which
            current user can create links from or to the *item*.

            Arguments:

                'item' -- Object from or to which user can create links.

                'REQUEST' -- REQUEST object.

            Result:

                List of objects.
        """
        if item is None:
            uid = None
            linked = []
        else:
            uid = item.getUid()
            linked = [ ob['target_uid'].uid for ob in self.searchLinks( source=item, target_type=None, target_removed=False ) ] + \
                     [ ob['source_uid'].uid for ob in self.searchLinks( target=item, source_type=None ) ]

        oblist = listClipboardObjects( self, permission=CMFCorePermissions.ManageProperties, REQUEST=REQUEST )
        result = []

        for ob in oblist:
            # XXX add an argument 'feature' for the method
            if ob.implements('isDocument'):
                other = ob.getUid()
                if uid != other and other not in linked:
                    result.append( ob )

        return result

    security.declarePublic( 'locate' )
    def locate( self, uid=None, action=None, REQUEST=None, **kw ):
        """
            Gets resource by uid and parameters.

            Arguments:

                'uid' -- uid of object

                'REQUEST' -- Zope request object

                'kw' -- additional keyword arguments
        """
        if REQUEST is None:
            return
        if uid:
            object = getObjectByUid( self, uid )
            if object is not None:
                return object.redirect(
                    relative = False,
                    canonical = True,
                    action  = action,
                    REQUEST = REQUEST
                )
        raise 'NotFound'

InitializeClass( DocumentLinkTool )


def registerRelation( id, **info ):
    """
        Registers relation type for inter-object links.

        Positional arguments:

            'id' -- relation type Id, string

        Keyword arguments:

            'title' -- human-readable relation name, string

            'verb' -- verbalization of the relation, string; applied as
                    in "source verb target"

            'allow_manual' -- whether the users are allowed to create the
                    relation by hand, otherwise only application code can
                    do this; 'True' by default

            'allow_internal' -- whether intra-object links are allowed,
                    e.g. between document versions; 'False' by default

            'unique_source' -- whether only one link having this relation
                    is allowed from the specific source; 'False' by default

            'unique_target' -- whether only one link having this relation
                    is allowed to the specific target; 'False' by default

            'lock_target' -- whether the object pointed to by the link should
                    be locked (and cannot be deleted) while the link remains;
                    'False' by default

            'source_key' -- optional name of the resource Uid key that is used
                    to designate the virtual source endpoint

            'target_key' -- optional name of the resource Uid key that is used
                    to designate the virtual target endpoint

        Exceptions:

            'ValueError' -- the relation type is already registered
    """
    global _relation_types
    if _relation_types.has_key( id ):
        raise ValueError, id

    # apply default options
    info.setdefault( 'id', id )
    info.setdefault( 'title', id )
    info.setdefault( 'verb', id )
    info.setdefault( 'allow_manual', True )
    info.setdefault( 'allow_internal', False )
    info.setdefault( 'unique_source', False )
    info.setdefault( 'unique_target', False )
    info.setdefault( 'lock_target', False )
    info.setdefault( 'weak_target', False )
    info.setdefault( 'source_key', None )
    info.setdefault( 'target_key', None )

    # add to the types registry
    _relation_types[ id ] = info

# mapping relation_id => relation_info structure
_relation_types = {}


def _getLinkKey( mapping ):
    # converts mapping to sequence for KeywordIndex
    if mapping is None:
        return []
    return [ key + '/'+ (value is not None and str(value) or '')
             for key, value in mapping.items() ]


def readLink( object, relation, id, value=Missing, default=Missing, uid=False, moniker=False, **kwargs ):
    """
    """
    links = getToolByName( object, 'portal_links' )
    key = links.getRelationInfo( relation ).get('source_key')
    if not key:
        raise TypeError, relation

    if value is Missing:
        kwargs[ key ] = id
        results = links.searchLinks( source=object, relation=relation, source_keys=kwargs )
        if not results:
            return None
        if len(results) != 1:
            assert len(results) < 1, "Duplicate unique-source links found."
            if default is not Missing:
                return default
            raise ValueError, id
        link = results[0]._unrestrictedGetObject()

    elif value is None:
        return None

    else:
        link = links[ value ]
        if link.getRelation() != relation or link.getSourceUid( key ) != id:
            raise TypeError, '%s=%s,%s=%s' % ( `link.getRelation()`, `relation`
                                             , `link.getSourceUid( key )`, `id`)

    if moniker:
        return Moniker( link.getTargetUid() )

    elif uid:
        return link.getTargetUid()

    return link.getTargetObject()

def updateLink( object, relation, id, value, old=Missing, **kwargs ):
    """
    """
    links = getToolByName( object, 'portal_links' )
    key = links.getRelationInfo( relation ).get('source_key')
    if not key:
        raise TypeError, relation

    link = target = None
    #print 'updateLink', type(value)

    if type(value) is StringType:
        # the target object's UID
        target = value

    elif isinstance( value, _zpub_record ):
        # 'record' object from HTML form
        link = value.get('value') or None
        if link is None:
            target = value.get('uid') or None

    elif value is not None:
        # the target object itself
        target = value

    # None value clears the property
    value = None
    kwargs[ key ] = id

    if link is not None:
        # check validity of the link ID
        uid = links[ link ].getSourceUid()
        if uid['type'] != relation or uid.base() != object \
                                   or uid.get( key ) != id:
            raise ValueError, link
        value = link

    elif target is not None:
        # create new link to the target
        link = links.createLink( object, target, relation, replace=1, source_keys=kwargs )
        value = link.getId()

    else:
        if old is Missing:
            for old in links.searchLinks( source=object, relation=relation, source_keys=kwargs ):
                links.removeLink( old.getObject(), restricted=Trust )
        elif old is not None:
            links.removeLink( old, restricted=Trust )

    #print 'updateLink', id, `value`, `target`
    return value

# prevent circular references
import Utils
Utils._readLink = readLink
Utils._updateLink = updateLink


class LinkResource:

    id = 'link'

    def identify( portal, object ):
        return { 'uid':object.getId() }

    def lookup( portal, uid=None, **kwargs ):
        object = getToolByName( portal, 'portal_links' )._getOb( uid, None )
        if object is None:
            raise Exceptions.LocatorError( 'link', uid )
        return object


def initialize( context ):
    # module initialization callback

    context.register( registerRelation )

    context.registerTool( DocumentLinkTool )

    context.registerResource( 'link', LinkResource, moniker='link', catalog='portal_links' )

    context.registerRelation( 'property',
                              title="Property of the object", verb="has a property value",
                              allow_manual=False, allow_internal=True,
                              unique_source=True, lock_target=True,
                              source_key='property',
                              source_permission=CMFCorePermissions.ModifyPortalContent,
                              target_permission=CMFCorePermissions.View )

    context.registerRelation( 'collection',
                              title="Property of the object", verb="has a property value",
                              allow_manual=False, allow_internal=True, weak_target=True,
                              source_key='collection' )

    context.registerRelation( 'attribute',
                              title="Attribute of the object", verb="has an attribute value",
                              allow_manual=False, unique_source=True, lock_target=True,
                              source_key='attribute' )

    context.registerRelation( 'field',
                              title="Field of the entry", verb="has a field value",
                              allow_manual=False, unique_source=True, allow_internal=True,
                              source_key='field' )

    context.registerRelation( 'dependence',
                              title="Unidirectional dependence", verb="depends on",
                              lock_target=True,
                              source_permission=CMFCorePermissions.ModifyPortalContent,
                              target_permission=CMFCorePermissions.ModifyPortalContent )

    context.registerRelation( 'reference',
                              title="Informational reference", verb="references",
                              weak_target=True,
                              source_permission=CMFCorePermissions.ModifyPortalContent,
                              target_permission=CMFCorePermissions.View )

    context.registerRelation( 'subordination',
                              title="Reference to primary document", verb="is subordinated to",
                              allow_manual=False, unique_source=True, lock_target=True )

    context.registerRelation( 'shortcut',
                              title="Shortcut", verb="points to",
                              allow_manual=False, unique_source=True,
                              source_permission=CMFCorePermissions.ModifyPortalContent,
                              target_permission=CMFCorePermissions.View )
