""" Collection of classes used to provide versions in document.
$Id: ContentVersions.py,v 1.113 2008/08/13 10:29:32 oevsegneev Exp $

$Editor: kfirsov $

"""
__version__ = '$Revision: 1.113 $'[11:-2]

from zLOG import LOG, DEBUG, TRACE, INFO

import re, string, sys, urllib
from random import randrange
from types import StringType, TupleType, ListType, InstanceType, DictType
from UserDict import UserDict

from ExtensionClass import Base
from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from AccessControl.Owned import Owned, ownerInfo
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Role import RoleManager
from AccessControl import getSecurityManager, SpecialUsers
from Acquisition import aq_base, aq_get, aq_inner, aq_parent, Acquired, \
        Explicit, Implicit
from DateTime import DateTime
from OFS.ObjectManager import ObjectManager
from webdav.Lockable import WriteLockInterface
from webdav.Resource import Resource
from ZODB.PersistentMapping import PersistentMapping
from ZODB.POSException import ConflictError

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import _checkPermission, getToolByName
from Products.CMFDefault.Document import Document
from Products.Localizer import get_request

import Config, Features, Exceptions
from Config import Roles, Permissions, Restrictions
from ResourceUid import ResourceUid
from SimpleNauItem import SimpleNauItem
from SimpleObjects import Persistent, ItemBase
from Utils import InitializeClass, installPermission, \
                  getObjectImplements, listImplements, _getViewFor


class ContentVersion( Persistent, Implicit, Owned, CMFCatalogAware,
                      RoleManager, Resource, ObjectManager, DynamicType ):
    """ Simple version class.

        ContentVersion takes some properties from parent document and store it as its own.
        So one document can have multiple independent versions.
    """
    _class_version = 1.3

    meta_type = 'Content Version'
    portal_type = 'Content Version'

    meta_types = ({'name':'Image Attachment',
                   'permission':CMFCorePermissions.View,
                   'action':''},
                 )

    __implements__ = Features.isVersion, \
                     WriteLockInterface, \
                     ObjectManager.__implements__

    __unimplements__ = Features.isPortalContent, \
                       Features.isVersionable, \
                       Features.isPublishable

    manage_options = ObjectManager.manage_options + \
                     RoleManager.manage_options + \
                     Owned.manage_options

    __allow_access_to_unprotected_subobjects__ = 1
    __propsets__ = ()

    __resource_type__ = Acquired

    _stx_level = Acquired

    text = ''
    cooked_text = ''
    _owner = None

    associated_with_attach = None

    content_type = Acquired
    reindexObject = Acquired
    listActions = Acquired

    _safety_belt_update = Acquired

    __ac_roles__ = (Roles.VersionOwner,)
    __ac_restrictions__ = None
    __ac_restricted_permissions__ = Acquired

    security = ClassSecurityInfo()

    # hack for CMFCatalogAware
    def _CMFCatalogAware__recurse( self, name, *args ):
        values = [ i[1] for i in self.objectItems() ]
        opaque_values = self.opaqueValues()
        for subobjects in values, opaque_values:
            for ob in subobjects:
                s = getattr(ob, '_p_changed', 0)
                if hasattr(aq_base(ob), name):
                    getattr(ob, name)(*args)
                if s is None: ob._p_deactivate()

    # hack for ObjectManager
    def _subobject_permissions( self ):
        return ()

    # notify document
    def _notifyAttachChanged( self, id ):
        self.getVersionable()._notifyAttachChanged( id )

    # notify document
    def _notifyOnDocumentChange( self ):
        self.getVersionable()._notifyOnDocumentChange()

    def _initstate( self, mode ):
        """
            Initialize attributes
        """
        if not Persistent._initstate( self, mode ):
            return 0

        if not hasattr( self, 'registry_data' ):
            self.registry_data = {}

        dict = self.__ac_local_roles__ or {}
        for userid, roles in dict.items():
            if type( roles ) is TupleType:
                dict[userid] = list( roles )
        self.__ac_local_roles__ = dict

        if not hasattr( self, 'workflow_history' ):
            self.workflow_history = PersistentMapping()

        if not hasattr( self, '_copies_holders' ):
            self._copies_holders = []

        return 1


    def __init__( self, id, title='', description='' ):
        """
            Initialize class instance
        """
        Persistent.__init__(self)
        self.id = id
        self.title = title
        self.description = description
        self.modification_date = self.creation_date = DateTime()
        self.workflow_history = PersistentMapping()

        self.attachments = []

    security.declareProtected(CMFCorePermissions.View, '__call__')
    def __call__(self, *args, **kw):
        """
            Default view
        """
        self._setVersionInRequest( self.id, self.REQUEST )
        #copied from PortalContent.__call__
        view = _getViewFor(self)
        if getattr(aq_base(view), 'isDocTemp', 0):
            return view(self, self.REQUEST)
        else:
            return view()

    def __getitem__( self, key ):
        # if this is attache, return it
        if key in self.objectIds():
            return  self._getOb( key )
        # recursion
        #return aq_parent(self)[ key ]

    def __cmp__(self, other):
        #Compare operations support.
        if getObjectImplements(other, 'isVersionable'):
            other = other.getVersion()
        assert isinstance( other, ContentVersion ), "(%s) is not a supported instance" % repr(other)
        return cmp(self.getVersionNumber(), other.getVersionNumber())

    def implements( self, feature=Missing ):
        """
            Checks whether the object implements given interface or feature.
        """
        return getObjectImplements( self.getVersionable(), feature,
                                    name='__version_implements__' )
    
    security.declarePublic( 'getResourceUid' )
    def getResourceUid(self):
        return ResourceUid(self)

    security.declarePublic('registry_ids')
    def registry_ids(self):
        """
            Used by catalog.
        """
        return self.registry_data.keys()


    def _setVersionInRequest(self, ver_id=None, REQUEST=None):
        """
            Places in the request pointer to the version.

            This is almost the same as making the version current.
            If ver_id is None, the current version will be chosen.
            Returns id of the version previously placed version (or None if there was no
            such version).

            Arguments:

                'ver_id' -- Identifier of the version. None means to use this version.

                'REQUEST' -- REQUEST object.

            Result:

                String or None
        """
        doc_uid = self.getVersionable().getPrincipalVersion().getUid()
        if REQUEST is None:
            REQUEST = aq_get( self.__of__( self.getVersionable() ), 'REQUEST', None ) or get_request()

        prev_ver = REQUEST.get( (doc_uid, 'version') )
        ver_id = ver_id or self.id 
        if prev_ver == ver_id:
            return

        REQUEST.set( (doc_uid, 'version'), ver_id )

        return prev_ver

    security.declareProtected(CMFCorePermissions.View, 'makeCurrent')
    def makeCurrent(self, REQUEST=None):
        """
            Public interface for _setVersionInRequest (and uses only this version).

            Arguments:

                'REQUEST' -- REQUEST object.

            Result:

                String or None
        """
        if self.getVersionable().getCurrentVersionId() == self.getId():
            return self.getId()
        return self._setVersionInRequest( None, REQUEST) or self.getPrincipalVersionId()

    def Type(self):
        """
            Returns type of object for catalog.
        """
        return "%s %s" %( self.getVersionable().Type(), 'Version')

    def getTypeInfo(self):
        return self.getVersionable().getTypeInfo()

    def title_or_id(self):
        """
            Returns version title otherwise version id.

            Result:

                String.
        """
        return self.Title() or self.id

    security.declarePublic( 'physical_path' )
    physical_path = ItemBase.physical_path.im_func

    # These methods are redefined to use desired version properties when
    # called _version_.method(). Otherwise will be called
    # HTMLDocument.method() -> getVersion().property, but getVersion()
    # and _version_ may be different

    Title=SimpleNauItem.Title.im_func
    Description=SimpleNauItem.Description.im_func
    Creator=SimpleNauItem.Creator.im_func
    CreationDate=SimpleNauItem.CreationDate.im_func
    ModificationDate=SimpleNauItem.ModificationDate.im_func
    modified=SimpleNauItem.modified.im_func
    absolute_url=SimpleNauItem.absolute_url.im_func
    redirect=SimpleNauItem.redirect.im_func

    def relative_url( self, **kwargs ):
        """
            Returns version's URL relative to the requested URL.
        """
        content   = self.getVersionable()
        principal = content.getPrincipalVersionId()
        REQUEST   = aq_get( content, 'REQUEST', None ) or get_request()
        published = REQUEST and REQUEST.get( (content._p_oid, 'publish') )

        if principal == self.id and published is None:
            return self.getVersionable().relative_url( **kwargs )
        else:
            return SimpleNauItem.relative_url.im_func( self, **kwargs )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'lockAttachment' )
    def lockAttachment(self, id):
        """
            Locks attachment file.

            See HTMLDocument.lockAttachment for further details.
        """
        return self.getVersionable().lockAttachment( id )

    def EditableBody(self, view=None):
        """
            Returns the editable body of the version.

            See HTMLDocument.EditableBody for further details.
        """
        old = self._setVersionInRequest()
        text = self.getVersionable().EditableBody(view=view)
        self._setVersionInRequest(old)
        return text

    security.declareProtected( CMFCorePermissions.View, 'manage_FTPget' )
    def manage_FTPget(self):
        """
            Gets the version body for FTP download (also used for the WebDAV SRC)

            See Document.manage_FTPget for further details.
        """
        old = self._setVersionInRequest()
        bodytext = self.getVersionable().manage_FTPget()
        self._setVersionInRequest(old)
        return bodytext

    def PUT( self, REQUEST, RESPONSE ):
        """
            Handles HTTP (and presumably FTP?) PUT requests.

            See HTMLDocument.PUT for further details.
        """
        doc_uid = self.getVersionable().getPrincipalVersion().getUid()
        oldver = REQUEST and REQUEST.get( (doc_uid, 'version') )
        REQUEST.set( (doc_uid, 'version'), self.id )
        result = self.getVersionable().PUT( REQUEST, RESPONSE )
        REQUEST.set( (doc_uid, 'version'), oldver )
        return result

    security.declarePublic('getId')
    def getId(self):
        """
            Returns id of this version.

            Result:

                String.
        """
        return self.id

    security.declarePublic('getVersionNumber')
    def getVersionNumber(self):
        """
            Returns id part from getId().

            Result:

                String.
        """
        id = self.getId()
        number = id.replace('version_','')
        return number

    security.declareProtected( CMFCorePermissions.View, 'getVersionTitle' )
    def getVersionTitle( self ):
        """
            Returns title of this version object.

            Result:

                String.
        """
        return self.title

    # XXX move methods below to another class
    # (if we will inherit DTMLDocument from this class , we'll have to remove them)

    def removeAssociation(self, id):
        """
            See HTMLDocument.removeAssociation for further details.
        """
        return self.getVersionable().removeAssociation( id )

    def associateWithAttach(self, *args, **kw):
        """
            See HTMLDocument.associateWithAttach for further details.
        """
        return self.getVersionable().associateWithAttach(*args, **kw)

    def addFile(self, *args, **kw):
        """
            Attaches a file to the document.

            See HTMLDocument.associateWithAttach for further details.
        """
        return self.getVersionable().addFile(*args, **kw)

    def removeFile( self, id ):
        """
            Removes all links pointing to the given file and deletes file.

            See HTMLDocument.removeFile for further details.
        """
        return self.getVersionable().removeFile(id)

    def manage_fixupOwnershipAfterAdd(self):
        """
            Changes the ownership and permissions after the version is created.
        """
        user=getSecurityManager().getUser()

        if (SpecialUsers.emergency_user and
            aq_base(user) is SpecialUsers.emergency_user):
            __creatable_by_emergency_user__=getattr(
                self,'__creatable_by_emergency_user__', None)
            if (__creatable_by_emergency_user__ is None or
                (not __creatable_by_emergency_user__())):
                raise EmergencyUserCannotOwn, (
                    "Objects cannot be owned by the emergency user")

#        if user is None:
#            self.changeOwnership( None, recursive=0, explicit=1 )
#            return
        self._owner=ownerInfo(user)

        self.manage_setLocalRoles( user.getUserName(), [Roles.VersionOwner] )

    def getStatus( self ):
        """
          Gets status of current version

          Result:

            Status of version (id)
        """
        portal_workflow = getToolByName( self, 'portal_workflow' )
        wf = self.getCategory().getWorkflow()
        wf_id = wf.getId()
        status = portal_workflow.getStatusOf(wf_id, self)
        return status and status.get( wf.state_var, None ) or None

    def state(self):
        return self.getStatus()

    def getStatusTitle( self ):
        """
          Gets status of current version

          Result:

            Status of version - title
        """
        portal_workflow = getToolByName( self, 'portal_workflow' )
        wf_id = self.getCategory().getWorkflow().getId()
        return portal_workflow.getStateTitle(wf_id, self.getStatus())

    # Prevent infinite loop while cataloging.
    def objectValues( self ):
        return ()

    # OriginalHolder
    def addLocalRoleVersionOwner( self, user_ids ):
        for u_id in user_ids:
            self.manage_addLocalRoles( u_id, [Roles.VersionOwner] )

    def delLocalRoleVersionOwner( self, user_ids ):
        self.manage_delLocalRoles( user_ids, [Roles.VersionOwner] )

    def getVersionOwners( self ):
        user_ids = self.users_with_local_role( Roles.VersionOwner )
        user_ids.sort()
        return user_ids

    def getVersionable( self, unwrap=False ):
        """
            Acquires versionable content from the content version context.
        """
        context = aq_parent( self )

        container = aq_parent(aq_inner( self ))
        object = aq_parent(aq_inner( container ))

        if unwrap or context is container:
            return object
        return object.__of__( context )

    def isEditable(self):
        """
            Checks whether the version is editable.
        """
        return  _checkPermission( CMFCorePermissions.ModifyPortalContent, self ) or \
                self.getStatus()=='group' and Roles.VersionOwner in \
                rolesForPermissionOn( CMFCorePermissions.ModifyPortalContent, self) and \
                _checkPermission( Permissions.CreateObjectVersions, self )

    def _versionable_onReindex( self, idxs=[], versionable=True ):
        """
            Called when reindex of a version is performed.
        """
        if versionable:
            obj = self.getVersionable()
            if obj.getPrincipalVersionId() == self.getId():
                obj.reindexObject( idxs, versionable=False )
        return True

    # XXX should inherit this class from InstanceBase

    def manage_afterClone( self, item ):
        CMFCatalogAware.manage_afterClone.im_func( self, item )

        cloned = getattr( item, '_ItemBase__instance_cloned', None )
        links = getToolByName( self, 'portal_links', None )

        # copy links from the copy source
        if not ( cloned is None or links is None ):
            subpath = self.getPhysicalPath()[ len( item.getPhysicalPath() ): ]
            source = cloned.unrestrictedTraverse( subpath )
            links.cloneLinks( source, self )

    def manage_beforeDelete( self, item, container ):
        CMFCatalogAware.manage_beforeDelete.im_func( self, item, container )

        destroyed = getattr( item, '_ItemBase__instance_destroyed', None )
        links = getToolByName( self, 'portal_links', None )

        # remove links bound to this object
        if destroyed and links is not None:
            try:
                links.removeBoundLinks( self )
            except ConflictError:
                raise
            except:
                etype, exc, tb = sys.exc_info()
                try:
                    raise Exceptions.BeforeDeleteError( exc=exc ), None, tb
                finally:
                    tb = None

installPermission( ContentVersion, Permissions.CreateObjectVersions )
InitializeClass( ContentVersion )


class VersionsContainer(Persistent, ObjectManager):
    """
        Version container class.
    """
    _class_version = 1.0

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    __ac_restrictions__ = None
    __ac_restricted_permissions__ = Acquired

    #define it here to prevent 'maximum recursion depth exceeded' error
    def changeOwnership(self, *args, **kw):
        """
            Really does nothing.
        """
        pass

    def __init__(self, id):
        """
            Creates instance.

            Creates in it default version with id='version_0.1',
            sets editable and principal version properties.
        """
        Persistent.__init__(self)
        self.id = id

        # create default version
        ver=ContentVersion(id='version_0.1', title='', description='')
        self._setObject('version_0.1', ver)

        self._principal_version='version_0.1'
        self._v_use_version = None

    #very XXXXXX inherit ContainerBase
    security.declarePublic('getId')   
    def getId(self):
        return self.id

    security.declareProtected(CMFCorePermissions.View, 'getCurrentVersionId')
    def getCurrentVersionId( self ):
        """
            Returns current version id we work with or None.
        """
        doc = aq_parent(self)
        REQUEST = aq_get( self.__of__(doc), 'REQUEST', None ) or get_request()
        num = REQUEST and REQUEST.get( (doc.getPrincipalVersion().getUid(), 'version') ) or self.getPrincipalVersionId()

        ver_ids=self.objectIds()

        if num and num in ver_ids:
            return num
        return None

    security.declareProtected(CMFCorePermissions.View, 'getVersion')
    def getVersion(self, num=None):
        """
            Return current or principal Version object.

            Arguments:

                'num' -- Id of the version to be retrieved. If None, principal
                    version will be returned.

            Result:

                ContentVersion.
        """
        num = num or self.getCurrentVersionId() or self._principal_version
        try:
            return self._getOb(num)
        except:
            return self._getOb(self._principal_version)

    __getitem__ = getVersion

    def __bobo_traverse__( self, REQUEST, name ):
        """
            This method will make this container traversable.

            Returns version with id=name (if exists), or property with id=name.
            If version is accessed, sets a flag in the request object indicating
            currently selected version.  Also sets auxiliary request variables
            for 'absolute_url' and 'relative_url' methods to work correctly
            with versions.

            Arguments:

                'REQUEST' -- REQUEST object.

                'name' -- Next part of URL.

            Result:

                ContentVersion or something else (depends on 'name' argument).
        """
        REQUEST = REQUEST or aq_get( self, 'REQUEST', None )
        result = self._getOb( name, None )
        if result is None or name != getattr( result, 'id', None ):
            return getattr(self, name)
            #return getattr(aq_parent(self), name)

        doc = aq_parent( self )

        if name in self.objectIds() and not isinstance( REQUEST, DictType ):
            REQUEST.set( (self.parent()._p_oid, 'publish'), self.id )
            result._setVersionInRequest( REQUEST=REQUEST )

        return result

    security.declareProtected(Permissions.CreateObjectVersions, 'createVersion')
    def createVersion(self, old_id, new_id, title='', description=''):
        """
            Creates new version with given properties based on the version with id=old_id.

            Returns id of the created version.

            Arguments:

                'old_id' -- Id of the version which is considered the base for new one.
                'new_id' -- Identifier for new version.
                'title' -- New version's title.
                'description' -- New version's description.

            Result:

                String.
        """
        object = ContentVersion(id=new_id, title=title, description=description)
        old = self.getVersion(old_id)

        object.text = old.text
        object.cooked_text = old.cooked_text

        # copy propertysheets from the old version object
        psets = ()
        for old_ps in old.__propsets__:
            old_ps._p_mtime
            new_ps = old_ps.__class__.__basicnew__()
            new_ps.__dict__.update( old_ps.__dict__ )
            psets = psets + (new_ps, )
        object.__propsets__ = psets

        #object.attachments=old.attachments[:]
        object.associated_with_attach=old.associated_with_attach
        #old.associated_with_attach = None

        self._setObject(new_id, object)

        return new_id

    _listVersions = ObjectManager.objectValues

InitializeClass(VersionsContainer)


class VersionableContent(Persistent, Base):
    """ VersionableContent class provides functions for supporting versions.

        VersionableContent class provides functions for supporting versions
        in data classes (such as HTMLDocument). To provide versions, child
        class must be subclassed from VersionableContent (and if it is
        multiple inheritance, VersionableContent have to be first in classes
        list).
    """
    _class_version = 1.0

    __implements__ = Features.isVersionable

    __ac_restrictions__ = { Restrictions.NoModificationRights:
                            ( Permissions.MakeVersionPrincipal,
                              Permissions.CreateObjectVersions,
                            )
                          }

    security = ClassSecurityInfo()

    _versionable_methods = ()
    _versionable_methods_common = ()
    _versionable_attrs = ()
    _versionable_perms = ()

    def __init__( self, container='version' ):
        self.__ac_local_roles__ = VersionableRoles()
        self._setObject( container, VersionsContainer( container ) )

    def __getattr__(self, name):
        """
            Returns attribue 'name' of current version.

            Returns attribue'name' of current version if 'name'
            is among self._versionable_attrs or self._versionable_perms.
            Raises AttributeError exception otherwise.

            Arguments:

                'name' -- attribute name

            Result:

                Attribute value.
        """
        if name in self._versionable_attrs + self._versionable_perms: # and name!='_owner':
            #FIXME!!! check permissions
            version = self.version.getVersion()
            if getattr(aq_base(version), name, Missing) is not Missing:
                return getattr(version, name)

        raise AttributeError, name

    def __setattr__(self, name, value):
        """
            Sets name=value in current version or content object itself.

            If 'name' is among self._versionable_attrs then sets name=value
            in current version otherwise sets it to document itself.

            Arguments:

                'name' -- attribute name to set
                'value' -- attribute value to set
        """

        if name in self._versionable_attrs + self._versionable_perms: # and name!='_owner':
            ver = self.getVersion()
            setattr(ver, name, value)
#            if ver.id==self.getEditableVersionId():
#                # FIXME !!!
#                # and utils._checkPermission(CMFCorePermissions.ModifyPortalContent, ver):
#                setattr(ver, name, value)
        else:
            Persistent.__setattr__(self, name, value )

    def __delattr__(self, name):
        """
            Removes attribute 'name' from current version.

            If 'name' is among self._versionable_attrs or
            self._versionable_perms, only TRIES to remove attribute.
            Otherwise directly remover attribute 'name' in content object.

            Arguments:

                'name' -- attribute to remove
        """
        if name in self._versionable_attrs + self._versionable_perms:
            try:
                Persistent.__delattr__(self, name )
            except: #XXX
                pass 
        else:
            Persistent.__delattr__(self, name )

    def __getitem__( self, key ):
        return self.getVersion()[key]

    security.declareProtected( CMFCorePermissions.View, 'getVersionable' )
    def getVersionable( self ):
        """
            Returns document object.
        """
        return self

    security.declareProtected(CMFCorePermissions.View, 'getVersion')
    def getVersion(self, num=None ):
        """
            Returns version with id 'num' or default version of document.

            Arguments:

                'num' -- Id of the version to retrieve. If None, returns
                    principal version.

            Result:

                ContentVersion.

        """
        return self.version.getVersion(num)

    security.declareProtected(CMFCorePermissions.View, 'getEditableVersion')
    def getEditableVersion( self, wrap_selected=True, latest=True ):
        """
            Returns the user's latest editable document version.

        """
        current = self.getVersion()
        if not latest and current.isEditable():
            return wrap_selected and self.getVersionable() or current
        versions = self.listEditableVersions( wrap_selected )
        if versions:
            return versions[-1]
        return None

    security.declareProtected(CMFCorePermissions.View, 'listEditableVersions')
    def listEditableVersions( self, wrap_selected=True ):
        """
            Returns a list of editable versions sorted by version number.

            Arguments:

                'wrap_selected' -- Return the versionable content instance
                                   instead of the version object in case the
                                   editable version was already selected by the user.
        """
        versions = []
        for version in self.version._listVersions():
            # XXX move this condition to the 'modify' transition's guard expr
            if version.isEditable():
                if wrap_selected and version is self.getVersion():
                    version = self.getVersionable()
                versions.append( version )
        versions.sort()
        return versions

    def getPrincipalVersion( self ):
        return self.getVersion( self.getPrincipalVersionId() )

    security.declareProtected(CMFCorePermissions.View, 'getPrincipalVersionId')
    def getPrincipalVersionId( self ):
        """
            Returns id of the principal version.

            Result:

                String.
        """
        return self.version._principal_version

    security.declareProtected(CMFCorePermissions.View, 'getCurrentVersionId')
    def getCurrentVersionId( self ):
        """
            Returns id of currently used version.

            If can not find (object uid, 'version') key in REQUEST, returns None.

            Result:

                String or None.
        """
        return self.version.getCurrentVersionId()

    security.declareProtected(CMFCorePermissions.View, 'isCurrentVersionPrincipal')
    def isCurrentVersionPrincipal(self):
        """
            Returns true if current version is principal.

            Result:

                Boolean.
        """
        return self.getPrincipalVersionId() == self.getCurrentVersionId() or \
            self.getCurrentVersionId()==None

    security.declareProtected(CMFCorePermissions.View, 'getMaxMajorAndMinorNumbers')
    def getMaxMajorAndMinorNumbers(self):
        """
            Returns tuple with the major and minor parts of id of the version
            with maximal id.

            Note: used to show how will new created version id looks like.

            Result:

                Tuple.
        """
        vers_ids = self.version.objectIds()
        #calculate max major version and is's max minor version
        versions_mm = []
        for test_id in vers_ids:
            mm = re.findall(r'version_(\d+)[_\.](\d+)', test_id)
            versions_mm.append( (int(mm[0][0]), int(mm[0][1])) )
        versions_mm.sort()
        return versions_mm[-1]


    security.declareProtected(Permissions.CreateObjectVersions, 'createVersion')
    def createVersion(self, ver_id, ver_weight='minor', title='', description='', REQUEST=None, **kw):
        """
            Creates new version. Returns id of created version.

            Arguments:

                'ver_id' -- Id of the version on the basis of which to create new one.
                'ver_weight' -- Weight of created version. Should be 'minor'
                    (default) or 'major'. Affects on id of new version.
                'title' -- Title of version.
                'description' -- Description of version.
                'REQUEST' -- REQUEST object.

            Result:

                String.
        """
        major, minor = self.getMaxMajorAndMinorNumbers()
        if ver_weight=='major':
            major += 1
            minor = 0
        else:
            minor += 1
        id = 'version_'+ str(major)+'.'+str(minor)

        new_id = self.version.createVersion( old_id=ver_id,
                                             new_id=id,
                                             title=title,
                                             description=description
                                           )
        self._version_onCreate( new_id, **kw )

        # copy attachments to new version

        new = self.getVersion(new_id)
        old = self.getVersion(ver_id)

        new.manage_pasteObjects( old.manage_copyObjects( old.objectIds() ) )

        # Copy document links from the source version
        links_tool = getToolByName(self, 'portal_links')
        link_brains = links_tool.searchLinks( source=self, source_ver_id=ver_id )
        for brain in link_brains:
            old_link = brain.getObject().cloneLink( source_ver_id=id )
        # Explicitly copy attributes of type 'link'
        for a, v in self.listCategoryAttributes():
            if a.Type() == 'link':
                new._setCategoryAttribute( a, v )

        if REQUEST is not None:
            return new.redirect( action='document_edit_form', REQUEST=REQUEST )
        else:
            return new_id

    security.declareProtected(CMFCorePermissions.View, 'listVersions')
    def listVersions(self):
        """
            Returns list of existing versions mappings.

            Each item in resulted list has next keys:
                'id' -- id of the version
                'Title' -- version title
                'Number' -- version number (see getVersionNumber() for more datails)
                'Description' -- version description
                'Creator' -- creator of the version
                'CreationDate' -- creation date
                'ModificationDate' -- last modification date
                'Editable' -- is the version editable or no
                'Principal' -- is the version principal or no.

            Result:

                List of mappings.
        """
        result = []
        principal_id = self.getPrincipalVersionId()
        for version in self.version._listVersions():
            if not _checkPermission(CMFCorePermissions.View, version):
                continue
            res = { 'id'            : version.id,
                    'Title'         : version.Title(),
                    'Number'        : version.getVersionNumber(),
                    'Description'   : version.Description(),
                    'Creator'       : version.Creator(),
                    'VersionOwners' : version.getVersionOwners(),
                    'CreationDate'  : version.CreationDate(),
                    'ModificationDate' : version.ModificationDate(),
                    'State'         : version.getStatus(),
                    'StateTitle'    : version.getStatusTitle(),
                    'Principal'     : self.getPrincipalVersionId() == version.id,
                    'Current'       : self.getCurrentVersionId() == version.id,
                  }
            if version.id == principal_id:
                res['URL'] = self.relative_url( action='view' )
            else:
                res['URL'] = version.relative_url( action='view' )
            result.append(res)
        return result

    security.declareProtected(Permissions.MakeVersionPrincipal, 'activateCurrentVersion')
    def activateCurrentVersion(self):
        """
            Makes current version principal.
        """
        if self.getCurrentVersionId():
            self.version._principal_version = self.getCurrentVersionId()

    def externalEditLink_(self, object, borrow_lock=0):
        """
            Inserts the external editor link to an object if appropriate.

            Returns html text for that link.

            Note:

                See Products.ExternalEditor.ExternalEditor.EditLink() for more details.

            Result:

                String
        """
        if not Config.UseExternalEditor:
            return ''

        base = aq_base(object)
        user = getSecurityManager().getUser()
        editable = (hasattr(base, 'manage_FTPget')
                    or hasattr(base, 'EditableBody')
                    or hasattr(base, 'document_src')
                    or hasattr(base, 'read'))

        if editable and user.has_permission( Permissions.UseExternalEditor, object ):
            if object.implements('isVersion'):
                #object is version
                obj_url = self.version.absolute_url()
            else:
                #object is attachment
                #use this way to prevent adding subpath (version/version_id) of currently using version
                obj_url = aq_parent(self).absolute_url() + '/' + urllib.quote(self.getId())
            url = "%s/externalEdit_/%s" % (
                obj_url, urllib.quote(object.getId()))
            if borrow_lock:
                url += '?borrow_lock=1'
            return ('<a href="%s" '
                    'title="Edit using external editor">'
                    '<img src="%s/misc_/ExternalEditor/edit_icon" '
                    'align="middle" hspace="2" border="0" alt="External Editor" />'
                    '</a>' % (url, object.REQUEST.BASEPATH1)
                   )
        else:
            return ''

    def _versionable_onReindex( self, idxs=[], versionable=True ):
        """
            Called when reindex of the versionable object is performed.
        """
        if versionable:
            self.getVersion().reindexObject( idxs, versionable=False )
        return self.isCurrentVersionPrincipal()

    # callback function, is called from within VersionContainer
    def _version_onCreate( self, version_id, **kw ):
        version = self.getVersion( version_id )
        cat = version.getCategory()
        wf = cat.getWorkflow()

        back_version_id = version.makeCurrent()

        #new_state_id = kw.get( 'new_state', wf.states.initial_state )
        new_state = kw.get( 'new_state' )
        state_id = new_state and new_state.get( 'state' ) or wf.initial_state
        if state_id is wf.initial_state is None:
            # the category has no initial state, so assume it has an initial
            # transition, and state_id is initial transition's destination state
            try:
                tdef = wf.transitions[wf.initial_transition]
                state_id = tdef.new_state_id
            except KeyError:
                pass

        cat.parent().versionWorkflowLogic._logicForVersionExclusion( self, new_state_id=state_id )
        #if need to keep state then pass initial transitions and other actions
        if not kw.has_key('keep_state'):
            self.notifyWorkflowCreated()

        if new_state:
            # setup initial workflow state
            workflow_tool = getToolByName( self, 'portal_workflow' )
            # XXX need wf.setStatusOf( new_state )
            new_state['time'] = DateTime()
            workflow_tool.setStatusOf( wf.getId(), version, new_state )
            wf.updateRoleMappingsFor( self )

        # XXX
        if self.getCategory().hasBase( 'NormativeDocument' ):
            creator = version.Creator()
            self.setCategoryAttribute('ResponsAuthor', creator)
        for attr, value in version.listCategoryAttributes():
            self._category_onChangeAttribute( attr.getId(), value )

        # XXX need try - finally
        self.getVersion(back_version_id).makeCurrent()

        # XXX is this redundant?
        version.reindexObject()


InitializeClass(VersionableContent)


class VersionableMethod( Explicit ):
    """
        Provides document method's call on version rather than on document itself.
    """

    # simulate Script object for getPublishedInfo
    func_code = None

    def __init__( self, func, common=False ):
        if hasattr( func, 'im_func' ):
            func = func.im_func
        self.__name__ = func.__name__
        self._func = func
        self._common = common

    def __call__( self, *args, **kw ):
        context = aq_parent( self )
        previous = None

        if isinstance( context, VersionableContent ):
            if not self._common:
                context = context.getVersion()

        elif isinstance( context, ContentVersion ):
            previous = context.makeCurrent()
            if previous == context.getId():
                previous = None

        else:
            raise TypeError, `context`

        try:
            return self._func( context, *args, **kw )

        finally:
            if previous is not None:
                context.getVersion( previous ).makeCurrent()


class VersionableAttribute( Explicit ):
    """
        VersionableAttribute class.

        This is attribute in document, which must be taken from version
        (even when attribute with the same name is presented in document).
        See ComputedAttribute for more details.
    """
    def __init__( self, attr, default=Missing, acquires=False ):
        """
            Initializes class instance.

            Arguments:

                'attr' -- Attribute name.

                'acquires' -- Boolean. Indicates whether the versionable attribute
                              requires acquisition context.

        """
        self._attr = attr
        self._default = default
        self._acquires = acquires

    def __of__( self, parent ):
        if self._acquires and aq_parent( parent ) is None:
            return self
        try:
            result = parent.__getattr__( self._attr )
        except AttributeError:
            if self._default is Missing:
                raise
            return self._default
        return result


class VersionableRoles( UserDict, Explicit ):

    def __getitem__( self, key ):
        roles = self.data.get( key )
        roles = roles and list(roles) or []

        parent = aq_parent( self )
        if parent is not None and not getattr( parent, '_v_disable_versionable_roles', None ):
            roles.extend( parent.getVersion().__ac_local_roles__.get( key ) or [] )

        # XXX See Patches.cmfcore_checkPermission comments for details.
        if hasattr( parent, '_v_disable_versionable_roles' ):
            del parent._v_disable_versionable_roles

        if not roles:
            raise KeyError, key
        return roles

    def get( self, key, default=None ):
        try: return self[ key ]
        except KeyError: return default

    def __setitem__( self, key, roles ):
        if Roles.VersionOwner in roles:
            if type(roles) is TupleType:
                roles = list(roles)
            roles.remove( Roles.VersionOwner )
        self.data[ key ] = roles

    def __len__( self ):
        return 1

    def __call__( self ):
        return self


def InitializeVersionableClass( klass ):
    """
        Initializes versionable methods, attributes and permissions
        in 'VersionableContent' derivative classes.

        Arguments:

            'klass' -- target class object
    """
    version = ContentVersion

    names = getattr( klass, '_versionable_methods', () )
    for name in names:
        value = getattr( klass, name )
        if not isinstance( value.im_func, VersionableMethod ):
            setattr( klass, name, VersionableMethod( value ) )
        if name.startswith('_') and not hasattr( version, name ):
            setattr( version, name, Acquired )

    names = getattr( klass, '_versionable_methods_common', () )
    for name in names:
        value = getattr( klass, name )
        if not isinstance( value.im_func, VersionableMethod ):
            setattr( klass, name, VersionableMethod( value, True ) )
        if name.startswith('_') and not hasattr( version, name ):
            setattr( version, name, Acquired )

    perms = ()
    for name in getattr( klass, '_versionable_perms', () ):
        if not name.startswith('_'):
            name = '_%s_Permission' % name.replace( ' ', '_' )
        perms += (name,)
    klass._versionable_perms = perms

    names = getattr( klass, '_versionable_attrs', () ) + perms
    for name in names:
        if name in perms:
            acquires = True
        else:
            acquires = False

        if not hasattr( klass, name ):
            setattr( klass, name, VersionableAttribute( name, acquires=acquires ) )
        else:
            value = getattr( klass, name )
            if not hasattr( value, 'im_func' ) or \
               not isinstance( value.im_func, VersionableAttribute ):
                setattr( klass, name, VersionableAttribute( name, value, acquires ) )

    if not hasattr( klass, '__version_implements__' ):
        klass.__version_implements__ = \
            listImplements( klass, append=ContentVersion.__implements__,
                                   remove=ContentVersion.__unimplements__ )
