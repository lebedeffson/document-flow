"""
Contains the following abstract base classes, that the corresponding
instances must inherit from:

    'Persistent' -- persistent objects

    'ItemBase' -- transient publishable objects

    'InstanceBase' -- persistent publishable objects

    'ContentBase' -- content objects

    'ContainerBase' -- container objects

    'OrderedContainerBase' -- ordered container objects

    'ToolBase' -- portal tools

$Editor: vpastukhov $
$Id: SimpleObjects.py,v 1.189 2008/12/18 15:07:25 oevsegneev Exp $
"""
__version__ = '$Revision: 1.189 $'[11:-2]

from copy import deepcopy
from new import instance as _new_instance
from logging import getLogger
from random import randrange
from re import sub
from sys import exc_info
from time import time
from traceback import format_stack
from types import DictType, StringType, TupleType
from urllib import quote

from webdav.Lockable import LockableItem
from webdav.LockItem import LockItem

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from AccessControl.Owned import Owned, UnownableOwner, ownerInfo
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.User import nobody as NobodyUser

from Acquisition import Implicit, Explicit, Acquired, \
        aq_inner, aq_parent, aq_base, aq_get
from App.Management import Tabs as _Tabs
from App.Undo import UndoSupport
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from DateTime import DateTime
from Globals import REPLACEABLE, NOT_REPLACEABLE, DevelopmentMode
from zLOG import LOG, TRACE, INFO, WARNING, ERROR

from OFS.CopySupport import CopySource
from OFS.Folder import Folder
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import Item
from OFS.Traversable import Traversable
from OFS.Uninstalled import BrokenClass

from ZPublisher.Converters import type_converters as _type_converters
from ZPublisher.HTTPRequest import record as _zpub_record

from Persistence import Persistent as _Persistent
from ZODB.PersistentList import PersistentList
from ZODB.POSException import ConflictError

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.Expression import Expression as CMFCore_Expression
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.interfaces.portal_actions import ActionProvider as IActionProvider
from Products.CMFCore.utils import getToolByName, UniqueObject, _checkPermission, _getAuthenticatedUser
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl, _marker as DublinCore_marker
from Products.DCWorkflow.Expression import Expression as DCWorkflow_Expression
from Products.PageTemplates.Expressions import getEngine

# XXX this class used to live here; should be removed soon
from AccessControl.Permission import RestrictedPermission

import Config, Exceptions, Features
from CatalogSupport import IndexableMethod
from Config import Roles, Permissions, Restrictions
from Exceptions import Unauthorized, formatErrorValue, formatException, getObjectRepr
from Features import createFeature
from Monikers import Moniker
from ResourceUid import ResourceUid, Resourceable
from Utils import InitializeClass, getClassByMetaType, getObjectImplements, \
        applyRecursive, getObjectByUid, readLink, updateLink, \
        cookId, checkValidId, buildUrl, getPublishedInfo, \
        joinpath, splitpath, normpath, _getViewFor


class Lockable(LockableItem):
    """
        Abstract base class for lockable objects.
    """
    _class_verson = 1.0
    __implements__ = ( Features.isLockable,)
    security = ClassSecurityInfo()

    security.declareProtected( CMFCorePermissions.View, 'getLockCreator' )
    def getLockCreator( self, lock=None ):
        """
            Returns username of the lock creator, or None.
        """
        if lock is None:
            lock = self.wl_lockValues( killinvalids=1 )
            lock = lock and lock[0] or None

        return lock and lock.getCreator()[1]

    security.declareProtected( CMFCorePermissions.View, 'isLocked' )
    def isLocked( self ):
        """
            Checks whether the object is locked by _another_ user.
        """
        if not self.wl_isLocked():
            return 0

        return ( _getAuthenticatedUser(self).getUserName() != self.getLockCreator() )

    security.declareProtected( CMFCorePermissions.View, 'isLockPermitted' )
    def isLockPermitted( self ):
        """
            Checks whether the current user can lock or unlock the object.
        """
        return not self.isLocked() or _checkPermission( CMFCorePermissions.ManagePortal, self )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'lock' )
    def lock( self ):
        """
            Locks the object.
        """
        self.failIfLocked()
        if self.wl_isLocked():
            return

        mdtool = getToolByName( self, 'portal_metadata' )
        lock   = LockItem( creator=_getAuthenticatedUser(self), timeout='Seconds-%d' % mdtool.getCategoryById(self.category).getLockTimeout() )

        self.wl_setLock( locktoken=lock.getLockToken(), lock=lock )

    security.declareProtected( CMFCorePermissions.View, 'unlock' )
    def unlock( self ):
        """
            Unlocks the object.
        """
        if not self.isLockPermitted():
            raise Exceptions.Unauthorized( "You have no permission to unlock this object." )

        self.wl_clearLocks()

    security.declarePublic( 'failIfLocked' )
    def failIfLocked( self ):
        """
            Raises an exception if the object is locked by _another_ user.
        """
        if  self.wl_isLocked() and \
            (_getAuthenticatedUser( self ).getUserName() != self.getLockCreator()):
            raise Exceptions.ResourceLockedError, 'This resource is locked'

InitializeClass( Lockable )

class InterfacedBase:
    """
        Abstract base class for objects with interfaces.
    """

    _class_version = 1.0

    __implements__ = ()

    security = ClassSecurityInfo()

    security.declarePublic( 'implements' )
    def implements( self, feature=Missing ):
        """
            Checks whether the object implements given interface or feature.

            See 'getObjectImplements' function for additional information.
        """
        return getObjectImplements( self, feature )

InitializeClass( InterfacedBase )


class Persistent( _Persistent, InterfacedBase ):
    """
        Abstract base class for persistent objects.

        Objects inheriting this class have built-in support for instance
        version tracking and automatic update of properties.
    """
    _class_version = 1.3

    __implements__ = createFeature('isPersistent')

    security = ClassSecurityInfo()

    # attributes for version tag support
    _class_tag   = None
    _version_tag = None
    __changed    = None

    def __init__( self ):
        """
            Initializes new persistent object.

            Sets initial version of the instance and invokes  '_initstate()'.
            Constructors in derived classes must be desinged to call this
            method in order for the object to be properly initialized.
        """
        self._version_tag = None
        aq_base( self )._initstate( 0 )

    def __setstate__( self, state ):
        # this method is called to unpickle object
        try:
            _Persistent.__setstate__( self, state )
        except AttributeError:
            return

        # check whether an autoupdate feature is enabled
        if not ( Config.AutoUpdateObjects or \
                 getattr( self.__class__, '_force_autoupdate', None ) ):
            return

        if self._p_jar is None:
            LOG( 'Persistent.__setstate__', WARNING, 'object %s has no connection' % getObjectRepr(self) )
            return

        # check for remote ZEO objects
        if hasattr( self._p_jar._storage, '_connection' ) and not Config.AutoUpdateRemote:
            return

        try:
            if aq_base( self )._initstate( 1 ):
                # reset is needed to register self in transaction
                self._p_changed = 0
                self._p_changed = self.__changed = 1
        except ConflictError:
            # Don't swallow ConflictError
            raise
        except:
            LOG( 'Persistent.__setstate__', ERROR, 'initstate error:', error=exc_info() )

    def _initstate( self, mode ):
        """
            Callback method for object initialization.

            The purpose of this method is to initialize crucial attributes
            and bring the instance into some consistent state.  The stored
            object can become inconsistent after new version of the class
            is installed, which requires additional attributes to exist that
            old instances may not have.

            This method is called several times during object's lifetime
            - during construction, after loading from the persistent storage
            if the class version tag has changed, and when the object is
            converted to another class.  The on-load call can be disabled
            globally by changing value of 'Config.AutoUpdateObjects'
            variable to false.

            This basic implementation checks for new properties in the
            '_properties' map of the class and adds missing attributes to the
            instance, using value of either '"default"' map entry or 'None'.
            Derived classes should define their own implementations in order
            to initialize additional attributes.

            Arguments:

                'mode' -- integer code, defined by conditions under which
                        the method was called: 0 - construction, 1 - load
                        from storage, 2 - convertation to another class

            Result:

                Boolean value, true if the object has changed.

            Note:

                The 'self' reference is an unwrapped object.
        """
        if mode < 2 and getattr( self, '_version_tag', None ) == self._class_tag:
            return 0

        self._version_tag = self._class_tag

        prop_map = getattr( self.__class__, '_properties', None )
        if prop_map:

            prop_self = self.__dict__.get( '_properties' )
            if prop_self is not None:
                prop_found = {}

                for prop in prop_self:
                    id = prop.get( 'id' )
                    if id is not None:
                        prop_found[ id ] = 1

            for prop in prop_map:
                id = prop.get( 'id' )
                if id is None:
                    continue

                if not hasattr( self, id ):
                    value = prop.get( 'default' )
                    if value is not None or not hasattr( self.__class__, id ):
                        # make a copy of value so that lists and dicts can be used
                        setattr( self, id, deepcopy(value) )

                if not ( prop_self is None or prop_found.get( id ) ):
                    prop_self = prop_self + ( prop, )

            if prop_self is not None:
                self._properties = prop_self

        return 1

    def _upgrade( self, id, klass, container=None, args=() ):
        """
            Converts a specified subobject to another class.

            Sometimes class of the existing persistent object needs to be
            changed, for example when the class is moved to another module.
            This procedure can be accomplished by calling this method on its
            container, specifying identifier of the subobject to be converted
            and the target class.  If the subobject is not a direct attribute
            of the container, but is located in a simple subcontainer such as
            list or dictionary, this subcontainer can be passed along.

            The target class must be derived from the old, unless the old
            class is broken.  Class convertation can be globally disabled by
            changing value of 'Config.AutoUpgradeObjects' variable to false.

            Arguments:

                'id' -- identifier under which the subobject is bound

                'klass' -- reference to the target class object

                'container' -- optional subcontainer of indirect subobjects,
                            'id' being the key into it

            Result:

                Converted subobject.
        """
        if not Config.AutoUpgradeObjects:
            return None

        base = aq_base( self )

        if container is not None:
            try:
                old = container[ id ]
            except ( TypeError, KeyError, IndexError, AttributeError ):
                base = aq_base( container )
                container = None

        if container is None:
            old = getattr( base, id, None )

        # do nothing if the object is already an instance of the *klass*
        if old is None or isinstance( old, klass ):
            return old

        # check whether the object can be upgraded

        try:    issub = issubclass( klass, old.__class__ ) or isinstance( old, BrokenClass )
        except AttributeError: issub = 0 # old is not a class instance

        if not issub:
            # better not raise exception from __setstate__
            #raise TypeError, '%s must be a subclass of %s' % ( klass.__name__,
            #                old.__class__.__module__ + '.' + old.__class__.__name__ )
            return old

        LOG( 'Persistent._upgrade', TRACE, 'upgrading %s to %s' % (getObjectRepr(old), klass.__name__) )

        # persistent object is actually loaded from the storage on _p_mtime access
        getattr( old, '_p_mtime', None )

        # create empty instance of the new *klass*
        if hasattr( klass, '__basicnew__' ):
            new = klass.__basicnew__()
        else:
            new = _new_instance( klass )

        # copy object data
        new.__dict__.update( old.__dict__ )

        # replace *old* object in the container with the *new*
        if container is None:
            setattr( base, id, new )
            if getattr( base, 'isAnObjectManager', None ):
                # ObjectManager stores object's meta_type, fix it
                for info in base._objects:
                    if info.get('id') == id:
                        info['meta_type'] = getattr( new, 'meta_type', None )
                        break
        else:
            container[ id ] = new

        if hasattr( old, '_p_oid' ) and hasattr( new, '_p_oid' ):
            # copy persistence attributes
            for attr in ['_p_jar','_p_oid','_p_serial']:
                setattr( new, attr, getattr( old, attr ) )

            # forget about casual changes of the *old*
            old.__changed  = 0
            old._p_changed = 0

            cache = new._p_jar._cache
            # try to free cache slot (for Zope >= 2.6)
            try: del cache[ new._p_oid ]
            except KeyError: pass

            # update object cache in this connection
            cache[ new._p_oid ] = new

        # unlink reference to the *old* object
        del old

        # bring the *new* object into valid state
        if isinstance( new, Persistent ):
            new._initstate( 2 )

        # set special "__changed" flag to be on the safe side
        if hasattr( new, '_p_oid' ):
            new._p_changed = new.__changed = 1

        # notify container of changed subobject
        if hasattr( base, '_p_oid' ):
            base._p_changed = 1

        return new

InitializeClass( Persistent )

class Tabs(_Tabs):

    __implements__= ()

    security = ClassSecurityInfo()

    security.declareProtected( CMFCorePermissions.View, 'listTabs' )
    def listTabs(self):
        """
            See Feature.hasTabs interface
        """
        return []

InitializeClass( Tabs )

class Logger( object ):

    def LOG( self, message ):
        if DevelopmentMode and __debug__:
             getLogger(self.__name__).info( message )
    LOG = classmethod( LOG )

class ItemBase( Implicit, Traversable, Resourceable, PropertyManager, CopySource, Tabs, InterfacedBase, Logger ):
    """
        Abstract base class for transient publishable objects.

        Objects inheriting this class have support for instance
        version tracking and auto-update

        Properties descriptor '_properties' mapping
    """
    meta_type = 'unspecified'

    __implements__ = ( createFeature('isItem')
                     , Tabs.__implements__
                     )

    security = ClassSecurityInfo()
    security.declareObjectProtected( CMFCorePermissions.View )

    __ac_restrictions__ = { Restrictions.NoAccess: ( CMFCorePermissions.View, ),
                            Restrictions.NoModificationRights:
                              ( CMFCorePermissions.ModifyPortalContent,
                                CMFCorePermissions.ManageProperties,
                                ZopePermissions.take_ownership,
                              )
                          }

    manage_options = PropertyManager.manage_options

    _properties = (
            { 'id':'title', 'type':'string', 'mode':'cw' },
        )

    # core properties
    isPrincipiaFolderish = 0
    isTopLevelPrincipiaApplicationObject = 0
    title = ''
    icon = ''

    # always acquired from context
    REQUEST = Acquired

    __instance_created = False
    __instance_destroyed = False
    __instance_cloned = None
    __instance_unrestricted = None

    def __init__( self, id=None, title=None ):
        """
            Arguments:

                'id' --

                'title' --
        """
        self.__instance_created = True
        if id is not None:
            try: self._setId( id )
            except AttributeError: self.id = id
        if title is not None:
            self.setTitle( title )

    security.declarePublic( 'getId' )
    getId = Item.getId.im_func
# Item.getId also checks __name__
#    def getId( self ):
#        """
#            Returns the identifier of the object.
#        """
#        id = self.id
#        if callable( id ):
#            return id()
#        return id

    security.declarePublic( 'Title' )
    def Title( self ):
        """
            Returns the object title (Dublin Core element - resource name).

            Result:

                String.
        """
        return self.title

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setTitle' )
    def setTitle( self, title ):
        """
            Sets the object title (Dublin Core element - resource name).

            Arguments:

                'title' -- title string of the object
        """
        self.title = title

    security.declareProtected( CMFCorePermissions.View, 'getHeadingInfo' )
    def getHeadingInfo(self):
        """
            TODO
        """
        return self.title_or_id()


    security.declarePublic( 'getResourceUid' )
    def getResourceUid( self ):
        """
            Returns the resource's unique ID.
        """
        return ResourceUid( self )

    def hasProperty( self, id ):
        """
            Checks whether the object has a property 'id'.

            Arguments:

                'id' -- property name

            Result:

                Boolean value.
        """
        for info in self._propertyMap():
            if info['id'] == id:
                return 1
        return 0

    def getProperty( self, id, default=Missing, uid=False, moniker=False ):
        """
            Returns value of the property 'id' of this object.

            In case the property exists but is unset, and 'default'
            argument is not given, *default* value from the corresponding
            entry of the properties descriptor is used.  If the property
            value cannot be determined, returns 'default' value or 'None'
            as a last resort.

            Arguments:

                'id' -- property name

                'default' -- value to be returned if the property does
                             not exist or is unset; 'None' if not given

                'uid' -- boolean flag; if true then return Uid of
                         the target object for  properties; by default
                         the object itself is returned

                'moniker' -- boolean flag; if true then return moniker
                             of the target object for 'link' properties

            Result:

                Value of the property.
        """
        for info in self._propertyMap():
            if info['id'] == id:
                break
        else:
            if default is Missing:
                return None
            return default

        value = getattr( aq_base(self), id, Missing )
        if value is Missing:
            if default is Missing:
                return info.get('default')
            return default

        # TODO document this fragment
        if info.get('type') == 'link' and value is not None:
            value = readLink( self, info.get('relation','property'), id, value, uid=uid, moniker=moniker )

        if 'c' in info.get('mode','') and callable( value ):
            value = value()

        return value

    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'getProperties' )
    def getProperties( self, default=Missing, uids=False, monikers=False ):
        """
            Returns all properties of the object in a single mapping.

            Arguments:

                'default' -- value to return if the property does not exist

                'uids', 'monikers' -- see 'getProperty' for 'uid' and 'moniker' arguments

            Result:

                Mapping from property Ids to values.
        """
        result = {}
        for info in self._propertyMap():
            result[ info['id'] ] = self.getProperty( info['id'], default, uid=uids, moniker=monikers )
        return result

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setProperties' )
    def setProperties( self, properties ):
        """
            Changes values of one or more properties of the object.

            Arguments:

                'properties' -- mapping from property Ids to new values
        """
        if isinstance( properties, _zpub_record ):
            properties = properties.__dict__
        self.manage_changeProperties( None, **properties )

    def propertyLabel( self, id ):
        """
            Returns text label for the given object property.

            The label is taken from the 'title' item
            of the corresponding property descriptor entry.
            If the title is unknown, uses property identifier.

            Arguments:

                'id' -- property identifier

            Result:

                String.
        """
        for info in self._propertyMap():
            if info['id'] == id:
                return info.get( 'title', id )
        return id

    def propdict( self, id=Missing ):
        # helper method for PropertyManager implementation
        # (standard method does not use _propertyMap)
        if id is not Missing:
            for info in self._propertyMap():
                if info['id'] == id:
                    return info
            # TODO implement moniker for ItemBase
            raise Exceptions.SimpleError( "The object %(object)s has no property '%(id)s'.",
                                          object=self.getId(), id=id )

        result = {}
        for info in self._propertyMap():
            result[ info['id'] ] = info

        return result

    security.declareProtected( CMFCorePermissions.View, 'listEditableProperties' )
    def listEditableProperties( self, monikers=False ):
        """
            Returns a list of properties which may be directly
            edited from the user interface.

            Editable properties are those that have non-empty title
            and 'w' mode flag turned on in the properties descriptor.

            Arguments:

                'monikers' -- used as per 'moniker' argument of the
                              'getProperty' method

            Result:

                A list of dictionary items, each being a copy of the
                corresponding property descriptor with an additional
                field 'value' set to the current property value.
        """
        # TODO allow reordering of items
        results = []
        for prop in self._propertyMap():
            if prop.has_key('title') and prop.has_key('mode') and 'w' in prop['mode']:
                item = prop.copy()
                # XXX getProperty uselessly loops over _propertyMap items
                item['value'] = self.getProperty( item['id'], moniker=monikers )
                results.append( item )
        return results

    security.declarePublic( 'physical_path' )
    def physical_path( self ):
        """
            Returns path to this object from the application root.

            Result:

                String of slash-separated path components.
        """
        return joinpath( self.getPhysicalPath() )

    security.declarePublic( 'parent' )
    def parent( self, feature=(), moniker=False, inner=True ):
        """
            Returns the container of this object.

            Keyword arguments:

                'feature' -- interface or feature specification;
                             find the nearest enclosing container that
                             satisfies it

                'moniker' -- boolean flag, false by default;
                             return parent object's moniker if true

            Result:

                Either an object instance or its moniker, maybe 'None'
                if no ancestor satisfying the 'feature' was found.

            Note:

                Needs correct acquisition context.
        """
        # XXX should this method be public?
        parent = inner and aq_parent(aq_inner( self )) or aq_parent( self )

        if feature:
            # check all ancestors up to the portal object
            try:
                while not parent.implements( feature ):
                    if parent.implements( 'isPortalRoot' ):
                        return None
                    parent = inner and aq_parent(aq_inner( parent )) or aq_parent( parent )
            except AttributeError:
                return None
        if moniker:
            return Moniker( parent )

        return parent

    security.declarePublic( 'parent_path' )
    def parent_path( self ):
        """
            Returns path to the containter as a string.

            Result:

                String of slash-separated path components.

            Note:

               Used by portal catalog index.
        """
        return joinpath( aq_parent(aq_inner(self)).getPhysicalPath() )

    security.declareProtected( CMFCorePermissions.View, 'listParents' )
    def listParents( self, feature='isPrincipiaFolderish'
                   , exclude_root=False, monikers=False ):
        """
            Returns the object's ancestors list.

            Arguments:

                'exclude_root' -- Exclude root object from result.

                'monikers' -- Return monikers instead of the actual parent
                              objects.
        """
        parents = []
        parent  = self

        while not parent.implements( 'isPortalRoot' ):
            if parent.implements( feature ):
                parents.insert( 0, parent )
            parent = parent.parent()

        if exclude_root:
            parents = parents[1:]

        if monikers:
            return [ Moniker( p ) for p in parents ]
        return parents

    security.declarePublic( 'absolute_url' )
    def absolute_url( self, relative=False, canonical=None, REQUEST=None, **kwargs ):
        """
            Returns absolute URL of the object.

            This method supersedes Traversable's one.

            Arguments:

                'relative' -- boolean flag for path relative to site root

                'action' -- the name of the target form

                'params' -- parameters dictionary for the target form

                'message' -- message text to display at the top of the page

                'fragment' -- URL fragment string

                'canonical' -- use primary server address of the portal

                'frame' -- the name of the page for the outer frame

                'redirect' -- boolean, for redirection links

                'popup' -- boolean, for links opening in new browser window

                'REQUEST' -- optional Zope request object

            Result:

                URL string.
        """
        if REQUEST is None:
            REQUEST = aq_get( self, 'REQUEST', None )

        if not canonical and (relative or REQUEST is not None):
            url = Traversable.absolute_url.im_func( self, relative )
            if REQUEST and REQUEST.get('ExternalPublish'):
                # XXX workaround for the situation when Traversable.getPhysicalPath finds storage in acquisition
                url = sub(r'(/go)/storage($|/)', r'\1\2', url)

        else:
            # XXX external site has its own properties tool
            props = getToolByName( self, 'portal_properties' )
            srv = props.getProperty('server_url')
            url = Traversable.absolute_url.im_func( self, True )
            url = joinpath( srv, url )

        return buildUrl( url, REQUEST=REQUEST, **kwargs )

    security.declarePublic( 'relative_url' )
    def relative_url( self, REQUEST=None, **kwargs ):
        """
            Returns this object's URL relative to the requested URL.
        """
        if REQUEST is None:
            REQUEST = aq_get( self, 'REQUEST', None )

        if REQUEST is None or not REQUEST.has_key('PUBLISHED'):
            # XXX add path from server_url ???
            url = joinpath( '', Traversable.absolute_url.im_func( self, True ) )

        elif REQUEST.has_key( (id(aq_base(self)), 'relative_url') ):
            url = REQUEST.get( (id(aq_base(self)), 'relative_url') )

        else:
            # TODO: check REQUEST.base
            published, object, is_method, \
                    path_id, has_slash, rel_path = getPublishedInfo( self, REQUEST )

            url_tool = getToolByName( self, 'portal_url' )
            self_path = list( url_tool.getRelativeContentPath( self ) )
            rel_path = list( rel_path ) # create mutable copy

            while self_path and rel_path and self_path[0]==rel_path[0]:
                del self_path[0], rel_path[0]
            url = quote( joinpath( ['..'] * len( rel_path ), self_path ) )

            # normalize URL to remove './' and 'foo/..' from it
            url = normpath(url)
            # cache result
            REQUEST.set( (id(aq_base(self)), 'relative_url'), url )

        return buildUrl( url, REQUEST=REQUEST, **kwargs )

    security.declarePublic( 'redirect' )
    def redirect( self, status=None, REQUEST=None, relative=True, **kwargs ):
        """
            Redirects browser to another view of this object.
        """
        REQUEST = REQUEST or aq_get( self, 'REQUEST', None )
        if REQUEST is None or not hasattr( REQUEST, 'RESPONSE' ):
            return None

        method = relative and self.relative_url or self.absolute_url
        url = method( redirect=True, REQUEST=REQUEST, **kwargs )

        if not status:
            status = (REQUEST.REQUEST_METHOD == 'POST') and 303 or 302

        return REQUEST.RESPONSE.redirect( url, status=status )

    def raise_standardErrorMessage( self, client=None, REQUEST=None,
                error_type=None, error_value=None, tb=None,
                error_tb=None, error_message='', *args, **kwargs ):
        """
            Called by Zope exception handler to prepare error message
            for the user.
        """
        if REQUEST is None:
            REQUEST = {}

        # setup skin to find proper standard_error_message template
        try:
            # portal's _v_skindata may have been cleared
            # as a result of the aborted transation
            urltool = getToolByName( self, 'portal_url' )
            urltool.getPortalObject().setupCurrentSkin( REQUEST )
        except (AttributeError, KeyError):
            pass

        error_value = formatErrorValue( error_type, error_value )

        if not error_message:
            if isinstance( error_value, Exceptions.SimpleError ):
                error_message = error_value

        Item.raise_standardErrorMessage.im_func( self, client, REQUEST, \
                error_type, error_value, tb, error_tb, error_message, args, **kwargs )

    security.declareProtected( CMFCorePermissions.View, 'cb_isCopyable' )
    def cb_isCopyable( self ):
        """ Checks whether the object can be copied via clipboard
        """
        if self.__instance_unrestricted is Trust:
            return True 

        return CopySource.cb_isCopyable( self ) and \
               _checkPermission( CMFCorePermissions.View, self )

    security.declareProtected( CMFCorePermissions.View, 'cb_isMoveable' )
    def cb_isMoveable( self ):
        """ Checks whether the object can be moved via clipboard
        """
        if self.__instance_unrestricted is Trust:
            return True 

        if self.implements('isLockable'):
            try: self.failIfLocked()
            except Exceptions.ResourceLockedError: return 0

        return CopySource.cb_isMoveable( self ) and \
               _checkPermission( ZopePermissions.delete_objects, self )

    def _getCopy( self, container ):
        #
        # Called by CopyContainer to perform object clone operation.
        #
        new = CopySource._getCopy( self, container )
        new.__instance_cloned = self

        return new

    def _postCopy(self, container, op=0):
        # Called after the copy is finished to accomodate special cases.
        # The op var is 0 for a copy, 1 for a move.

        if self.__instance_unrestricted is not None:
            del self.__instance_unrestricted

    def manage_afterAdd( self, item, container ):
        #
        # Called by ObjectManager after the object is added to the container.
        # We use it to launch our creation/clone and add hooks.
        #
        if self.__instance_created:
            try:
                applyRecursive( ItemBase._instance_onCreate, 0, self )
            finally:
                del self.__instance_created

        elif self.__instance_cloned is not None:
            source = self.__instance_cloned
            try:
                applyRecursive( ItemBase._instance_onClone, 0, self, source, item )
            finally:
                del self.__instance_cloned

        applyRecursive( ItemBase._containment_onAdd, 0, self, item, container )

    def manage_afterClone( self, item ):
        #
        # Called by CopyContainer on the copy after the object is copied
        # and added to the container. Exists here only for completeness.
        #
        if isinstance( item, ItemBase ) and item.__instance_cloned is not None:
            subpath = self.getPhysicalPath()[ len( item.getPhysicalPath() ): ]
            source = item.__instance_cloned.unrestrictedTraverse( subpath )
            applyRecursive( ItemBase._instance_onClone, 0, self, source, item )

    def manage_beforeDelete( self, item, container ):
        #
        # Called by ObjectManager before the object is removed from its container.
        # We use it to launch our delete and destroy hooks.
        #
        #print 'manage_beforeDelete', `self`, `item`
        try:
            applyRecursive( ItemBase._containment_onDelete, 1, self, item, container )

            if self.__instance_destroyed:
                try:
                    applyRecursive( ItemBase._instance_onDestroy, 1, self )
                finally:
                    del self.__instance_destroyed

            elif isinstance( item, ItemBase ) and item.__instance_destroyed:
                applyRecursive( ItemBase._instance_onDestroy, 1, self )

        except ConflictError:
            raise
        except:
            # override ObjectManager's policy to ignore most errors
            etype, exc, tb = exc_info()
            try:
                raise Exceptions.BeforeDeleteError( exc=exc ), None, tb
            finally:
                tb = None

    def _instance_onCreate( self ):
        """
            Instance creation event hook.

            This method is invoked upon the instance creation and normally
            is called only once in the object's lifetime just after
            the instance initialization.
        """
        if hasattr( aq_base(self), 'setupResourceUid' ):
            self.setupResourceUid()

    def _instance_onClone( self, source, item ):
        """
            Instance clone event hook.

            This method is invoked upon the instance creation in case it was
            added by means of copy/paste operation.

            Arguments:

                'source' -- copy source object

                'item' -- the copy operation's target object
        """
        # generate another UID -- for cloneLinks to work right away
        if hasattr( aq_base(self), 'setupResourceUid' ):
            self.setupResourceUid( force=True )

    def _instance_onClone_subargs( self, id, source, item ):
        # returns arguments for subobject onClone callback
        return (getattr( source, id ), item), {}

    def _instance_onDestroy( self ):
        """
            Instance destroy event hook.

            This method is invoked in case the instance is going to be
            totally removed from the storage.
        """
        pass

    def _containment_onAdd( self, item, container ):
        """
            Containment add event hook.

            This method is invoked after the object is added to the
            container.

            Arguments:

                'item' -- added object

                'container' -- item container object

            Note: there is a difference between '_instance_onCreate'
            and '_containment_onAdd' hooks. The first is called only
            once after the object creation time while the last method
            is invoked on every cut/paste operation that moves object
            to the new container.
        """
        pass

    def _containment_onAdd_subargs( self, id, item, container ):
        # returns arguments for subobject onAdd callback
        return (item, self), {}

    def _containment_onDelete( self, item, container ):
        """
            Containment delete event hook.

            This method is invoked before deleting the object from it's
            container.

            Arguments:

                'item' -- added object

                'container' -- item container object

            Note: see '_containment_onAdd' for further explanations.
        """
        pass

    def _containment_onDelete_subargs( self, id, item, container ):
        # returns arguments for subobject onDelete callback
        return (item, self), {}

    def _setAcquisition(self, source):
        """
            Sets acquisition wrapper of given *source*.

            This somewhat hackish method used to fix acquisition after
            object was moved to another location. It allows to continue
            using it's methods in context of real location.
        """
        assert source.aq_base is self.aq_base, \
               "Could not set acqusition from another object"
        assert source.aq_parent.aq_base is not self.aq_base, \
               "Object could not be acquisition parent of self"

        self.aq_parent = source.aq_parent

InitializeClass( ItemBase )


class InstanceBase( Persistent, ItemBase ):
    """
        Abstract base class for persistent publishable objects.
    """
    _class_version = 1.0

    __implements__ = Persistent.__implements__, \
                     ItemBase.__implements__

    security = ClassSecurityInfo()

    def __init__( self, id=None, title=None ):
        Persistent.__init__( self )
        ItemBase.__init__( self, id, title )

    def _updateProperty( self, id, value ):
        """
            Changes value of the specified property of the object.
        """
        info  = self.propdict( id )
        ptype = info.get( 'type', 'string' )
        pmode = info.get( 'mode', '' )
        #print 'updateProperty', id, `value`, ptype, type(value)

        # try to transform string value using Zope type converter
        if type(value) is StringType and _type_converters.has_key( ptype ):
            value = _type_converters[ ptype ]( value )

        if ptype == 'link':
            value = updateLink( self, info.get('relation','property'), id, value )

        elif ptype == 'lines':
            if len(value) == 1 and not len(value[0]):
                # XXX empty textarea gets converted into
                # a single-element list containing an empty string
                value.pop(0)

        elif ptype == 'string':
            if 'n' in pmode and value == 'None':
                # a hack to preserve None values in ZMI
                value = None

        self._setPropValue( id, value )

    def _delProperty( self, id ):
        """
            Removes the specified property from the object.
        """
        info = self.propdict( id )

        # remove associated link for the link type
        if info.get('type') == 'link':
            updateLink( self, info.get('relation','property'), id, None )

        ItemBase._delProperty( self, id )

    security.declarePrivate( 'copyObject' )
    def copyObject( self, target ):
        """
            Copies this object to another container.

            Arguments:

                'target' -- receiving container object
                            (ContainerBase derivative)

            Result:

                The copy object in context of the target container.
        """
        if not isinstance( target, ContainerBase ):
            raise TypeError, type(target)

        try:
            self._notifyOfCopyTo( target, op=0 )
        except Exceptions.SimpleError:
            raise
        except:
            raise Exceptions.CopyError( "Copy error" )

        copy = self._getCopy( target )

        id = target._get_id( self.getId() )
        copy._setId( id )

        target._setObject( id, copy, set_owner=0 )
        return target._getOb( id )

    security.declarePrivate( 'moveObject' )
    def moveObject( self, target ):
        """
            Moves this object to another container.

            Arguments:

                'target' -- receiving container object
                            (ContainerBase derivative)

            Result:

                This object in context of the target container.
        """
        if not isinstance( target, ContainerBase ):
            raise TypeError, type(target)

        try:
            self._notifyOfCopyTo( target, op=1 )
        except Exceptions.SimpleError:
            raise
        except:
            raise Exceptions.CopyError( "Move error" )

        id = self.getId()
        self.parent()._delObject( id )

        id = target._get_id( id )
        self._setId( id )

        target._setObject( id, self, set_owner=0 )
        return target._getOb( id )

    security.declarePrivate( 'deleteObject' )
    def deleteObject( self ):
        """
            Deletes this object from its container.
        """
        self._ItemBase__instance_destroyed = True
        self.parent()._delObject( self.getId() )

    def _instance_onClone( self, source, item ):
        # copy direct links
        links = getToolByName( self, 'portal_links', None )
        if links is not None:
            links.cloneLinks( source, self )

    def _instance_onDestroy( self ):
        # remove links bound to this object
        links = getToolByName( self, 'portal_links', None )
        if links is not None:
            links.removeBoundLinks( self )

InitializeClass( InstanceBase )


class ContentBase( InstanceBase, DefaultDublinCoreImpl, Lockable, PortalContent ):
    """
        Abstract base class for content objects.
    """
    _class_version = 1.0

    __resource_type__ = 'content'

    __implements__ = ( InstanceBase.__implements__
                     , DefaultDublinCoreImpl.__implements__
                     , PortalContent.__implements__
                     , IActionProvider
                     )


    security = ClassSecurityInfo()

    manage_options = InstanceBase.manage_options + \
                     PortalContent.manage_options

    __ac_restrictions__ = { Restrictions.NoModificationRights:
                              ( Permissions.EmployPortalContent,
                                Permissions.PublishPortalContent,
                                Permissions.ArchivePortalContent,
                              )
                          }

    _properties = InstanceBase._properties + (
            #DefaultDublinCoreImpl._properties +
            {'id':'nd_uid', 'type':'string', 'mode':'w'},
        )

    # object owner will have this role
    _owner_role = Roles.Owner

    # name of the default object view method
    _default_view = None

    # default attribute values
    nd_uid = None
    state = None

    # default actions list for actions tool
    _actions = ()

    # override alwasy effective and never expires times
    # this needed to friend with DateIndex
    _DefaultDublinCoreImpl__FLOOR_DATE = DateTime( 1970, 0 )
    _DefaultDublinCoreImpl__CEILING_DATE = DateTime( 4000, 0 )

    def __init__( self, id=None, title=None, **kwargs ):
        """ Initialize class instance
        """
        InstanceBase.__init__( self, id, title )
        DefaultDublinCoreImpl.__init__( self, title=self.Title(), **kwargs )

    def __call__( self, REQUEST=None ):
        """
            Invokes the default view.
        """
        try:
            view = _getViewFor( self )

        except 'Not Found':
            name = self._default_view
            if not name:
                raise

            view = getattr( self, name )
            if not getSecurityManager().validate( self, self, name, view ):
                raise Unauthorized( name, self )

        if getattr( aq_base(view), 'isDocTemp', None ):
            return apply( view, (self, REQUEST or self.REQUEST) )
        else:
            return view( REQUEST )

    security.declarePublic( 'getUid' )
    def getUid( self ):
        """
            Returns unique object ID.
        """
        return self.nd_uid

    security.declarePrivate( 'setupResourceUid' )
    def setupResourceUid( self, force=False ):
        """
            Prepares the object's resource UID for use.
        """
        if not ( force or self.getProperty( 'nd_uid' ) is None ):
            return

        uid = '%012uX%05u%05u' % ( long( time()*100 ), id(self)%100000, randrange(100000) )
        self._setPropValue( 'nd_uid', uid )

        self.reindexObject( idxs=['nd_uid'] )

    security.declarePrivate( 'listActions' )
    def listActions( self, info=None ):
        """
            Adds object-defined actions to the global actions list.
        """
        return self._actions

    def Creator( self ):
        """
            Returns username of the resource creator -- Dublin Core element.

            Result:

                String; empty string if creator is not known.
        """
        owner = self.getOwner()
        if owner is NobodyUser:
            # support Z27
            return self.owner_info()['id']
        if owner and hasattr( owner, 'getUserName' ):
            return owner.getUserName()
        return ''

    security.declareProtected( ZopePermissions.take_ownership, 'changeOwnership' )
    def changeOwnership( self, user, recursive=None, explicit=None ):
        """
            Change owner of the object.
            If 'recursive' is 0 keep sub-objects ownership information.
        """
        if type(user) is StringType:
            member = getToolByName( self, 'portal_membership' ).getMemberById( user )
            user   = member is not None and member.getUser() or None

        #elif isinstance(user, MemberData):
        #    user = user.getUser()

        if user is None:
            if explicit:
                self._owner = None
            else:
                try: del self._owner
                except AttributeError: pass

        elif recursive is None or recursive:
            # TODO support explicit
            Item.changeOwnership( self, user, recursive )

        else:
            new = ownerInfo( user )
            old = aq_get( self, '_owner', None, 1 )
            if old is not UnownableOwner and \
               new is not None and ( new != old or explicit ):
                self._owner = new

        idxs  = ['Creator']
        owner = self.getOwner()
        owner = owner is not None and owner.getUserName() or None
        owner_role = self._owner_role

        if owner and owner_role:
            owners = self.users_with_local_role( owner_role )

            if owner not in owners:
                roles = [ owner_role ]
                roles.extend( self.get_local_roles_for_userid( owner ) )
                self.manage_setLocalRoles( owner, roles )
                idxs.append('allowedRolesAndUsers')

            elif owner and len(owners) > 1:
                owners = [ o for o in owners if o != owner ]
                if owners:
                    idxs.append('allowedRolesAndUsers')

            for name in owners:
                roles = self.get_local_roles_for_userid( name )
                roles = [ r for r in roles if r != owner_role ]
                if roles:
                    self.manage_setLocalRoles( name, list(roles) )
                else:
                    self.manage_delLocalRoles( (name,) )

        # at first call abject is not indexed yet
        if self.getUid():
            self.reindexObject( idxs=idxs )

    security.declarePrivate( 'changePermission' )
    def changePermission( self, permission, roles=Missing, acquire=Missing, append=(), remove=() ):
        if acquire is Missing:
            acquire = not not self.acquiredRolesAreUsedBy( permission )
        if roles is Missing:
            roles = self.rolesOfPermission( permission )
            roles = [ r['name'] for r in roles if r['selected'] ]
        for role in append:
            roles.append( role )
        for role in remove:
            roles.remove( role )
        self.manage_permission( permission, roles, acquire )

    security.declareProtected( CMFCorePermissions.View, 'getContentsSize' )
    def getContentsSize( self ):
        """
            Returns size of the object's body.

            Result:

                Integer value (number of bytes).
        """
        if hasattr( aq_base(self), 'get_size' ):
            return self.get_size()
        return 0

    security.declareProtected( CMFCorePermissions.View, 'isContentEmpty' )
    def isContentEmpty( self ):
        """
            Checks whether the object's body is empty.

            Result:

                Boolean value.
        """
        return not self.getContentsSize()

    def externalEdit( self, REQUEST ):
        """
            Opens this object in the External Editor.

            Should be directly called by the Web browser.
        """
        REQUEST['target'] = self.getId()
        return self.parent().externalEdit_.index_html( REQUEST, REQUEST.RESPONSE )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'editMetadata' )
    def editMetadata( self, **kwargs ):
        """
            Updates the editable metadata for this resource.
            Do not complete reindex object as the original method does.
            each indexable DublinCore element reindexes itself.
        """
        if self.implements('isLockable'):
            self.failIfLocked()

        # replace Missing with DublinCore marker
        for k, i in kwargs.items():
            if i is Missing:
                kwargs[k] = DublinCore_marker

        self._editMetadata( **kwargs )

    def getIcon( self ):
        """
            Returns url of this object's icon relative to portal.
        """
        if self.implements('isPortalContent'):
            ti = self.getTypeInfo()
            if ti is None:
                return ''
            icon = ti.getIcon()

            if icon:
                return quote(icon)

        return 'help.gif'

    def icon( self ):
        """
            Returns relative url of this object's icon (for use by ZMI)
        """
        url_tool = getToolByName(self, 'portal_url')
        return joinpath(url_tool(relative = 1), self.getIcon())

    def _getCopy( self, container ):
        new = InstanceBase._getCopy( self, container )
        new.creation_date = DateTime()

        # reset global unique object id
        try: new._updateProperty( 'nd_uid', None )
        except: pass

        return new

    def _instance_onClone( self, source, item ):
        PortalContent.manage_afterClone( self, item )

        # prepend 'Copy' prefix to the object's title
        if self.implements('isPortalContent') and self.parent().isParentOf( source ):
            msg = getToolByName( self, 'msg' )

            if self.implements('hasLanguage'):
                lang = self.Language()
            else:
                lang = msg.get_default_language()

            prefix = msg.gettext( 'common.copy_title_prefix', lang=lang )
            if self.getId().startswith('copy'):
                prefix += self.getId()[ 4:self.getId().find('_') ]

            self.setTitle( prefix + ' ' + self.Title() )

    def _containment_onAdd( self, item, container ):
        PortalContent.manage_afterAdd( self, item, container )

    def _containment_onDelete( self, item, container ):
        PortalContent.manage_beforeDelete( self, item, container )

    def _remote_onTransfer( self, remote ):
        # transfer local object to the remote server
        dltool   = getToolByName( self,   'portal_links', None )
        dlremote = getToolByName( remote, 'portal_links', None )

        if dltool is None or dlremote is None:
            return

        file = dltool._exportLinks( self )
        if file:
            dlremote._importLinks( file )

    setTitle          = IndexableMethod( InstanceBase.setTitle
                                       , title=['title','Title','SearchableText'] )
    setDescription    = IndexableMethod( DefaultDublinCoreImpl.setDescription
                                       , description=['Description','SearchableText'] )
    setSubject        = IndexableMethod( DefaultDublinCoreImpl.setSubject
                                       , subject=['Subject'] )
    setEffectiveDate  = IndexableMethod( DefaultDublinCoreImpl.setEffectiveDate
                                       , effective_date=['effective'] )
    setExpirationDate = IndexableMethod( DefaultDublinCoreImpl.setExpirationDate
                                       , expiration_date=['expires'] )

InitializeClass( ContentBase )


class ContainerBase( InstanceBase, ObjectManager ):
    """
        Abstract base class for container objects.
    """
    _class_version = 1.0

    isPrincipiaFolderish = 0

    security = ClassSecurityInfo()

    __ac_restrictions__ = { Restrictions.NoModificationRights:
                              ( CMFCorePermissions.AddPortalContent,
                                ZopePermissions.delete_objects,
                              )
                          }


    manage_options = (
            { 'label'  : 'Contents',
              'action' : 'manage_contents',
              'help'   : ('OFSP', 'ObjectManager_Contents.stx') },
         ) + InstanceBase.manage_options

    _super_checkId = ObjectManager._checkId

    security.declareProtected( ZopePermissions.view_management_screens, 'manage_contents' )
    manage_contents = ObjectManager.manage_main
    manage_contents._setName( 'manage_contents' )

    security.declarePublic( 'isParentOf' )
    def isParentOf( self, object, distant=False, identic=False ):
        """
            Checks whether an object resides in this container.

            Arguments:

                'object' -- the object to check ('ItemBase' derivative)

                'distant' -- optional boolean flag, if true also succeed
                             when the object is underneath at any level

                'identic' -- optional boolean flag, if true also succeed
                             when this is one and the same object

            Result:

                Boolean value.
        """
        my_path  = self.getPhysicalPath()
        my_level = len(my_path)
        ob_path  = object.getPhysicalPath()
        ob_level = len(ob_path)

        if ob_level < my_level:
            return False
        if not identic and ob_level == my_level:
            return False
        if not distant and ob_level > my_level + 1:
            return False

        return ob_path[ :my_level ] == my_path

    security.declarePublic( 'checkId' )
    def checkId( self, id, allow_dup=0 ):
        """
            Checks that *id* does not exist in container.
        """
        try:
            self._checkId( id, allow_dup )
        except Exceptions.InvalidIdError, exc:
            return exc
        return None

    def _checkId( self, id, allow_dup=False ):
        """
            This method prevents people other than the portal manager
            from overriding skinned names.
        """
        checkValidId( self, id, allow_dup )

        if allow_dup or id == 'index_html' or \
           id in getattr( self, '_reserved_names', () ):
            return

        ob = self
        while ob is not None and not getattr( ob, '_isPortalRoot', 0 ):
            # XXX fix CMFSite and replace this with parent() eventually
            ob = aq_parent(aq_inner( ob ))
        if ob is None or not hasattr( aq_base(ob), id ):
            # if the portal root has no object by this name, allow an override
            return

        item = getattr( ob, id )
        flags = getattr( item, '__replaceable__', NOT_REPLACEABLE )
        if flags & REPLACEABLE:
            # the object explicitly allows to override itself
            return

        if isinstance( item, ContentBase ):
            # allow storages in site containers
            return
        if id not in ob.objectIds() and isinstance( item, Folder ):
            # XXX skins tool should be fixed to never return skin folders
            return

        # portal manager may override anything
        #if _checkPermission( CMFCorePermissions.ManagePortal, self ):
        #    return

        raise Exceptions.ReservedIdError( "This identifier is reserved.", id=id )

    def objectIds( self, spec=None, feature=() ):
        # Returns a list of subobject ids of the current object.
        # If 'spec' is specified, returns objects whose meta_type
        # matches 'spec'.
        # if 'feature' is specified, returns objects that
        # implement any of the interfaces
        if spec is None and not feature:
            return [ ob['id'] for ob in self._objects ]

        if type(spec) is StringType:
            spec = [spec]

        set = []
        checked = {}

        for ob in self._objects:
            mtype = ob['meta_type']
            if spec and mtype not in spec:
                continue

            if feature:
                if not checked.has_key( mtype ):
                    checked[ mtype ] = 0

                    klass = getClassByMetaType( mtype, None )
                    if klass and getObjectImplements( klass, feature ):
                        checked[ mtype ] = 1

                if not checked[ mtype ]:
                    continue

            set.append( ob['id'] )

        return set

    def objectValues( self, spec=None, feature=() ):
        # Returns a list of actual subobjects of the current object.
        # If 'spec' is specified, returns only objects whose meta_type
        # match 'spec'.
        return [ self._getOb(id) for id in self.objectIds( spec, feature ) ]

    def objectItems( self, spec=None, feature=() ):
        # Returns a list of (id, subobject) tuples of the current object.
        # If 'spec' is specified, returns only objects whose meta_type match
        # 'spec'
        return [ (id, self._getOb(id)) for id in self.objectIds( spec, feature ) ]

    def manage_delObjects( self, ids=(), REQUEST=None ):
        """
            Deletes one or more subordinate objects.

            Arguments:

                'ids' -- either list of object IDs to delete
                         or a single ID string

                'REQUEST' -- optional Zope request object; if given,
                             redirect to ZMI is initiated
        """
        if type(ids) is StringType:
            ids = [ ids ]

        # let the objects know that they are being permanently deleted
        for id in ids:
            ob = self._getOb( id, None )
            if hasattr( ob, '_ItemBase__instance_destroyed' ):
                ob._ItemBase__instance_destroyed = True

        try:
            # NB ObjectManager tampers ids list
            return ObjectManager.manage_delObjects( self, list(ids), REQUEST )

        except:
            # some objects may have not been deleted, unset the flag
            for id in ids:
                ob = self._getOb( id, None )
                if getattr( ob, '_ItemBase__instance_destroyed', None ):
                    del ob._ItemBase__instance_destroyed

            # re-raise exception
            raise

    security.declarePrivate( 'addObject' )
    def addObject( self, obj, id=Missing, set_owner=True ):
        """
        """
        if id is Missing:
            id = obj.getId()
        if set_owner:
            set_owner = isinstance( obj, Owned )
        ObjectManager._setObject( self, id, obj, set_owner=set_owner )
        return self._getOb( id )

    security.declarePrivate( 'hasObject' )
    def hasObject( self, id ):
        """
        """
        for info in self._objects:
            if info['id'] == id:
                return True
        return False

    security.declareProtected( ZopePermissions.delete_objects, 'deleteObjects' )
    def deleteObjects( self, ids ):
        """
        """
        self.manage_delObjects( ids )
        return ids

    def _setObject( self, id, obj, roles=None, user=None, set_owner=True ):
        # overriden to check Owned inheritance
        return ObjectManager._setObject( self, id, obj, roles, user, (set_owner and isinstance(obj, Owned)) )

    def _containment_onAdd( self, item, container ):
        if 0:#isinstance(self, ContentBase):
            return

        ObjectManager.manage_afterAdd( self, item, container )

    def _instance_onClone( self, source, item ):
        if 0:#isinstance(self, ContentBase):
            return

        ObjectManager.manage_afterClone( self, item )

    def _containment_onDelete( self, item, container ):
        if 0:#isinstance(self, ContentBase):
            return

        ObjectManager.manage_beforeDelete( self, item, container )

    def _CMFCatalogAware__recurse(self, *args, **kw):
        pass

InitializeClass( ContainerBase )


class OrderedContainerBase( ContainerBase ):
    """
        Abstract base class for ordered containers.
    """
    _class_version = 1.0

    security = ClassSecurityInfo()

    # TODO
    # - support id renaming
    # - method for quering subobject position

    def __init__( self, *args, **kw ):
        # initializes ordered container
        ContainerBase.__init__( self, *args, **kw )
        self._order = PersistentList()

    def objectIds( self, spec=None, feature=() ):
        # returns ordered subobject IDs
        ids = ContainerBase.objectIds( self, spec, feature )
        order = self._order
        return [ id for id in order if id in ids ]

    def addObject( self, obj, id=Missing, set_owner=True, position=None, offset=None ):
        """
        """
        obj = ContainerBase.addObject( self, obj, id, set_owner=set_owner )
        if not ( position is offset is None ):
            self._moveObject( obj.getId(), position, offset )
        return obj

    def _moveObject( self, id, position=None, offset=None ):
        """
            Changes subobject position in the list.

            The desired subobject placement can be specified either
            as a position in the list, or as an offset from the current
            position.  Both can be either positive or negative numbers.

            Arguments:

                'id' -- string ID of the object in question

                'position' -- new position of the object, integer number
                        starting at zero; if negative, the position is counted
                        from the end of the list, with -1 being the last

                'offset' -- difference of the new position and the current
                        one; if positive, the subobject is moved towards
                        the end of the list; if negative, to the beginning
        """
        if not (position is None) ^ (offset is None):
            raise TypeError, None

        order = self._order
        try:
            previous = order.index( id )
        except ValueError:
            self[ id ] # raises KeyError
            previous = len(order)
        else:
            del order[ previous ]

        if offset is not None:
            position = previous + offset
        elif position < 0:
            position = len(order) + position + 1

        order.insert( position, id )

    def _setOb( self, id, object ):
        # appends subobject ID to the list
        ContainerBase._setOb( self, id, object )
        if id not in self._order:
            self._order.append( id )

    def _delOb( self, id ):
        # removes subobject ID from the list
        ContainerBase._delOb( self, id )
        if id in self._order:
            self._order.remove( id )

InitializeClass( OrderedContainerBase )

class BTreeContainerBase( BTreeFolder2Base, ContainerBase ):
    
    def __init__(self, *args, **kwargs):
        BTreeFolder2Base.__init__(self, None)
        ContainerBase.__init__(self, *args, **kwargs)

    __setstate__ = ContainerBase.__setstate__

    def _checkId(self, *ignore):
        # need rewrite
        pass

    def _setObject( self, id, obj, roles=None, user=None, set_owner=True ):
        # overriden to check Owned inheritance
        return BTreeFolder2Base._setObject( self, id, obj, roles, user, (set_owner and isinstance(obj, Owned)) )

class ToolBase( UniqueObject, InstanceBase, ActionProviderBase, UndoSupport ):
    """
        Abstract base class for portal tools.
    """
    _class_version = 1.0

    __implements__ = ( Features.isTool
                     , InstanceBase.__implements__
                     #, ActionProviderBase.__implements__
                     , IActionProvider
                     )

    __resource_type__ = 'item'

    #  overrided by Base in UniqueObject
    __delattr__ = InstanceBase.__delattr__
    __setattr__ = InstanceBase.__setattr__
    __setstate__  = InstanceBase.__setstate__

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    manage_options = ActionProviderBase.manage_options + \
                     InstanceBase.manage_options + \
                     UndoSupport.manage_options

    _actions = tuple( ActionProviderBase._actions )

    site_tool = False
    site_action_provider = False

    def listActions( self, info=None ):
        """
            Returns all the actions defined by the tool.

            Result:

                List of 'ActionInformation' instances.
        """
        # CMF 1.3.x returns None by default, which is bad
        return self._actions

    security.declarePublic( 'getPortalObject' )
    getPortalObject = InstanceBase.parent

    def redirect( self, status=None, REQUEST=None, action=None, **kwargs ):
        """
            Redirects browser to the specified portal action.
        """
        REQUEST = REQUEST or aq_get( self, 'REQUEST', None )
        if REQUEST is None or not hasattr( REQUEST, 'RESPONSE' ):
            return None

        if action is not None:
            actions = getToolByName( self, 'portal_actions' )
            actinfo = actions.getAction( action )
            if actinfo:
                url = buildUrl( actinfo['url'], REQUEST=REQUEST, **kwargs )
                if not status:
                    status = (REQUEST.REQUEST_METHOD == 'POST') and 303 or 302
                return REQUEST.RESPONSE.redirect( url, status=status )

        return InstanceBase.redirect( self, status, REQUEST, action=action, **kwargs )

    def Title( self ):
        """
            XXX: remove dynamic translation of title
        """
        return self.msg( self.title )

InitializeClass( ActionProviderBase ) # CMF 1.3.1 bug
InitializeClass( ToolBase )


class ExpressionWrapper( InstanceBase ):
    """
    """
    _class_version = 1.4

    meta_type = 'Expression Wrapper'

    _properties = InstanceBase._properties + (
            {'id':'factory',  'type':'string', 'mode':'w'},
            {'id':'text',     'type':'string', 'mode':'w'},
            {'id':'use_dict', 'type':'int',    'mode':'w'},
        )

    # default property values
    factory  = 'cmf_core'
    use_dict = 0

    def __init__( self, id=None, title=None, text=None, factory=None, use_dict=None ):
        """
            Instance constructor.
        """
        InstanceBase.__init__( self, id, title )

        if factory is not None:
            if not _expression_factories.has_key( factory ):
                raise ValueError, factory
            self.factory = factory

        if use_dict is not None:
            self.use_dict = int(use_dict)

        self.setExpression( text )

    def _initstate( self, mode ):
        # update attributes
        if not InstanceBase._initstate( self, mode ):
            return 0

        if hasattr( self, 'usefirst' ): # < 1.3
            self.use_dict = 1
            del self.usefirst

        if type(self.factory) is not StringType: # < 1.4
            self.factory = 'dc_workflow'

        return 1

    def __call__( self, *args, **kw ):
        """
            Executes expression.
        """
        if self.use_dict and len(args) >= self.use_dict:
            adict = args[ self.use_dict - 1 ]
            if type(adict) is DictType:
                kw.update( adict )
            elif hasattr( adict, '__dict__' ):
                kw.update( adict.__dict__ )

        for i in range( len(args) ):
            kw[ 'arg' + str(i+1) ] = args[i]

        return self.expr( getEngine().getContext( kw ) )

    def setExpression( self, text ):
        """
            Changes expression text.
        """
        if text:
            self.expr = _expression_factories[ self.factory ]( text )
        else:
            self.expr = None

    def getProperty( self, id, default=None ):
        # support text property
        if id == 'text':
            return self.expr and self.expr.text or ''
        return InstanceBase.getProperty( self, id, default )

    def _updateProperty( self, id, value ):
        # support text property
        if id == 'text':
            return self.setExpression( value )
        InstanceBase._updateProperty( self, id, value )

InitializeClass( ExpressionWrapper )

_expression_factories = {
        'cmf_core'    : CMFCore_Expression,
        'dc_workflow' : DCWorkflow_Expression,
    }


class ProxyAccessProvider( Implicit ):

    security = ClassSecurityInfo()

    def __init__( self, base, parent, permissions, roles ):
        """ Construct instance
        """
        self.id = getattr( base, 'id', cookId( parent, prefix='proxy' ) )
        self.base = base
        self.permissions   = permissions
        self.allowed_roles = roles

        wrapped = self.__of__( parent )
        wrapped.securityUserChanged()

        security = getSecurityManager()
        security.addContext( wrapped, force=1 )

    def securityUserChanged( self ):
        security = getSecurityManager()

        for perm in self.permissions:
            if security.checkPermission( perm, self ):
                self._proxy_roles = self.allowed_roles
                return

        self._proxy_roles = ()

    def getOwner( self ):
        return None

    security.declarePublic( 'getId' )
    def getId( self ):
        """ Return object id
        """
        return self.id

    security.declarePublic( 'implements' )
    def implements( self, feature=Missing):
        """
            Returns 'implements' for the base object.
        """
        return getObjectImplements( self.base, feature )

InitializeClass( ProxyAccessProvider )


class ProxyReaderFactory( Explicit ):

    id = None

    def __init__( self, id='' ):
        """
            Initializes new instance.

            Arguments:

                'id' -- identifier of the instance

        """
        self.id = id

    def __bobo_traverse__( self, REQUEST, name ):
        # get target object wrapped with access proxy
        object = self._wrapObject( name, REQUEST )
        # insert access provider into the traverse stack
        return ( aq_parent(object), object )

    def _wrapObject( self, uid, REQUEST=None ):
        """
            Returns target object wrapped with access proxy instance.

            The target object is fetched using portal_catalog tool
            by 'uid' and additional search specification given in
            constructor.  The object is put into context of new access
            proxy instance and wrapped object is returned.

            Raises ValueError or notFoundError if the object was not
            found.

            Arguments:

                'uid' -- unique identifier of the target object

                'REQUEST' -- optional Zope request object

            Returns:

                Target object in acquisition context of the access
                proxy and upper container.
        """
        parent  = aq_parent( aq_inner( self ) )

        try:
            object = ResourceUid(uid).deref(self)
        except Exceptions.LocatorError:
            object = None

        if object is None:
            if REQUEST is not None:
                REQUEST.RESPONSE.notFoundError( '%s\n%s' % (uid, '') )
            raise ValueError, uid

        if self.implements('isShortcut'):
            return object.__of__( parent )

        proxy = ProxyAccessProvider( self, parent, \
                ( CMFCorePermissions.View, ), ( Roles.Member, Roles.Reader, ) )

        return object.__of__( proxy.__of__( parent ) )

class ReaderProxy( ProxyReaderFactory ):
    """
        Serves as a read-proxy thus providing access to every linked object
        for content viewers even if those objects are inaccessible directly.
        Instances of this class are intended to be an attribute of the content
        objects.
    """
    __allow_access_to_unprotected_subobjects__ = 1

    def __bobo_traverse__( self, REQUEST, name ):
        links = getToolByName( self, 'portal_links' )
        parent = aq_parent( aq_inner( self ) )
        if not links.searchLinks( source=parent,
                                  source_inclusive=True,
                                  target=name
                                ):
            raise Exceptions.Unauthorized( name )

        return ProxyReaderFactory.__bobo_traverse__( self, REQUEST, name )

    def checkPermission( self, permission, name ):
        parent, object = self.__bobo_traverse__( None, name )
        return _checkPermission(permission, object)
	
    def relative_url( self, action ):
        parent, object = self.__bobo_traverse__( None, action )
        return object.relative_url()
						
# install reader proxy
InstanceBase.proxy = ReaderProxy( 'proxy' )

class SimpleRecord:

    def __init__( self, data=None, *args, **kwargs ):
        if args and data:
            for name in args:
                self.__dict__[ name ] = data[ name ]

        elif type(data) is DictType:
            self.__dict__.update( data )

        elif isinstance( data, _zpub_record ):
            self.__dict__.update( data.__dict__ )

        if kwargs:
            self.__dict__.update( kwargs )
#        for key, value in self.__dict__.items():
#            if isinstance( value, _zpub_record ):
#                self.__dict__[ key ] = SimpleRecord( value )

    def __getitem__( self, key ):
        return self.__dict__[ key ]

    def __setitem__( self, key, value ):
        self.__dict__[ key ] = value

    def __contains__( self, key ):
        return self.__dict__.has_key( key )

    def keys( self ):
        return self.__dict__.keys()

    def values( self ):
        return self.__dict__.values()

    def items( self ):
        return self.__dict__.items()

    def get( self, key, default=None ):
        return self.__dict__.get( key, default )

    def setdefault( self, key, value ):
        return self.__dict__.setdefault( key, value )

    def updatedefault( self, data ):
        for key, value in data.items():
            self.__dict__.setdefault( key, value )

    def setactive( self, key, value ):
        if not value and self.__dict__.has_key( key ):
            return self.__dict__[ key ]
        self.__dict__[ key ] = value
        return value

    def copy( self ):
        return self.__class__( self.__dict__ )

    has_key = __contains__


class ItemResource:

    id = 'item'

    def identify( portal, object ):
        try:
            uid = object.physical_path()
        except AttributeError:
            uid = '/'.join( object.getPhysicalPath() )
        return { 'uid' : uid }

    def lookup( portal, uid=None, **kwargs ):
        object = portal.unrestrictedTraverse( str(uid), None )
        if object is None:
            raise Exceptions.LocatorError( 'item', uid )
        return object


class ContentResource:

    id = 'content'
    keys = ['ver_id']
    default = True

    def identify( portal, object ):
        if getObjectImplements( object, 'isVersion' ):
            version = object
            object  = version.getVersionable()
        else:
            version = None

        #if not isinstance( object, ContentBase ):
        #    raise TypeError( '%s: wrong object of type %s' % (object, type(object)) )

        uid = object.getUid()
        if not uid:
            raise TypeError( '%s: no uid' % object )

        uid = { 'uid' : uid }
        if version:
            uid['ver_id'] = version.getId()

        return uid

    def lookup( portal, uid=None, ver_id=None, **kwargs ):
        catalog = getToolByName( portal, 'portal_catalog' )
        results = catalog.unrestrictedSearch( nd_uid=str(uid) )

        if len(results) == 1:
            try:
                object = results[0]._unrestrictedGetObject()
            except Unauthorized:
                object = None
            if object is None:
                raise Exceptions.LocatorError( 'content', uid )
        else:
            # TODO add len(results) to error message
            raise Exceptions.LocatorError( 'content', uid )

        if getObjectImplements( object, 'isVersionable' ) and ver_id:
            object = object.getVersion( ver_id )

        return object

class ToolsInstaller:
    priority = 10
    name = 'setupTools'

    def install(self, p, check=False):
        """ Set up initial tools"""
        count = 0
        current = [ d['meta_type'] for d in p.objectMap() ]

        for name in Config.PortalTools:
            if name in current:
                continue

            count += 1
            if check:
                continue

            if name.startswith('CMF '):
                factory = p.manage_addProduct['CMFCore']
            elif name.startswith('Default '):
                factory = p.manage_addProduct['CMFDefault']
            else:
                factory = p.manage_addProduct['CMFNauTools']

            factory.manage_addTool( name, None )

        return count

    __call__ = install



def initialize( context ):
    # module initialization callback

    context.registerResource( 'item', ItemResource, path=1 )
    context.registerResource( 'content', ContentResource, default=1, moniker='content', catalog='portal_catalog' )

    context.registerInstaller( ToolsInstaller )
