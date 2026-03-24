"""
Folder (Heading) class.

$Editor: vpastukhov $
$Id: Heading.py,v 1.273 2009/02/18 14:31:21 oevsegneev Exp $
"""
__version__ = '$Revision: 1.273 $'[11:-2]

import re
from string import join
from sys import exc_info
from time import sleep
from types import StringType, ListType, DictType
from urllib2 import urlopen

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from AccessControl.Permission import Permission
from Acquisition import aq_base, aq_get
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from Globals import HTMLFile

from OFS.Moniker import Moniker
from OFS.CopySupport import CopyError, _cb_decode, _cb_encode

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.Expression import Expression
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName, _checkPermission

import Config, Features
from ActionInformation import ActionInformation as AI
from Config import Roles, Permissions
from Exceptions import SimpleError, ResourceLockedError, \
        SentinelError #sentinel hack
from MemberDataTool import MemberData
from SimpleNauItem import SimpleNauItem
from SimpleObjects import ContainerBase, ProxyReaderFactory
from SyncableContent import SyncableContent
from Utils import InitializeClass, refreshClientFrame, isBroken, isSequence, \
        joinpath, splitpath, pathdelim, listClipboardObjects, cookId


HeadingType = { 'id'             : 'Heading'
             , 'meta_type'      : 'Heading'
             , 'title'          : "Folder"
             , 'description'    : "Folder contains other kinds of objects."
             , 'icon'           : 'folder_icon.gif'
             , 'sort_order'     : 0.2
             , 'product'        : 'CMFNauTools'
             , 'factory'        : 'manage_addHeading'
             , 'permissions'    : ( CMFCorePermissions.AddPortalFolders, )
             , 'filter_content_types' : False
             , 'immediate_view' : 'folder'
             , 'actions'        :
                ( { 'id'            : 'view'
                  , 'name'          : "View"
                  , 'action'        : 'folder'
                  , 'permissions'   : ( CMFCorePermissions.View, )
                  , 'category'      : 'folder'
                  }
                , { 'id'            : 'metadata'
                  , 'name'          : "Metadata"
                  , 'action'        : 'metadata_edit_form'
                  , 'permissions'   : ( CMFCorePermissions.View, )
                  , 'category'      : 'folder'
                  }
                , { 'id'            : 'edit'
                  , 'name'          : "Properties"
                  , 'action'        : 'folder_edit_form'
                  , 'permissions'   : ( CMFCorePermissions.ManageProperties, )
                  , 'category'      : 'folder'
                  }
                , { 'id'            : 'filter'
                  , 'name'          : "Content filter"
                  , 'action'        : 'portal_membership/processFilterActions?open_filter_form=1'
                  , 'permissions'   : ( CMFCorePermissions.View, )
                  , 'category'      : 'folder'
                  }
                , { 'id'            : 'viewing_order'
                  , 'name'          : "Viewing order"
                  , 'action'        : 'viewing_order'
                  , 'permissions'   : ( CMFCorePermissions.ManageProperties, )
                  , 'category'      : 'folder'
                  , 'condition'     : 'python: object.getSite() is not None'
                  }
                , { 'id'            : 'accessgroups'
                  , 'name'          : "Access control"
                  , 'action'        : 'manage_access_form'
                  , 'permissions'   : ( CMFCorePermissions.ChangePermissions, )
                  , 'category'      : 'folder'
                  }
                , { 'id'            : 'contents'
                  , 'name'          : "Folder contents"
                  , 'action'        : 'folder_contents'
                  , 'permissions'   : ( CMFCorePermissions.ListFolderContents, )
                  , 'category'      : 'folder'
                  , 'visible'       : False
                  }
                )
             }


# ContainerBase should be the first because of the ObjectManager methods

class Heading( ContainerBase, SimpleNauItem, PortalFolder, SyncableContent ):
    """ Heading class """
    _class_version = 1.113

    meta_type = 'Heading'
    portal_type = 'Heading'

    isPrincipiaFolderish = 1

    __resource_type__ = 'content'

    __implements__ = ( Features.canHaveSubfolders,
                       Features.isContentStorage,
                       Features.isPortalContent,
                       Features.isPrincipiaFolderish,
                       Features.isItemsRealm,
                       Features.hasContentFilter,
                       Features.hasSubscription,
                       Features.isPublishable,
                       Features.isCategorial,
                       Features.isNavigable,
                       ContainerBase.__implements__,
                       SimpleNauItem.__implements__,
                       PortalFolder.__implements__,
                       SyncableContent.__implements__,
                     )

    security = ClassSecurityInfo()
    security.declareObjectProtected( CMFCorePermissions.AccessContentsInformation )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setTitle' )
    security.declareProtected( CMFCorePermissions.ManageProperties, 'setDescription' )
    security.declareProtected( CMFCorePermissions.ManageProperties, 'setSubject' )
    security.declareProtected( CMFCorePermissions.View, 'manage_copyObjects' )
    security.declareProtected( CMFCorePermissions.View, 'manage_cutObjects' )
    security.declareProtected( CMFCorePermissions.AddPortalContent, 'manage_pasteObjects' )
    security.declareProtected( ZopePermissions.delete_objects, 'manage_renameObject' )

    index_html = None
    managed_roles  = Config.ManagedLocalRoles
    manage_options = PortalFolder.manage_options

    icon = SimpleNauItem.icon
    _getCopy = SimpleNauItem._getCopy
    setTitle = SimpleNauItem.setTitle

    content_type = PortalFolder.content_type
    manage_addFolder = PortalFolder.manage_addFolder

    # CMF 1.3 overcome
    indexObject = CMFCatalogAware.indexObject
    #reindexObject = CMFCatalogAware.reindexObject
    unindexObject = CMFCatalogAware.unindexObject

    # attributes saved during remote object synchronization
    _sync_reserved = SyncableContent._sync_reserved + \
                     ( 'subscribed_users', 'pending_subscriptions' )

    _actions = SimpleNauItem._actions + \
        (
            AI(
                id='subscription',
                title="Manage subscription",
                description="Manage subscription to topic updates.",
                action=Expression( 'string: ${object_url}/manage_subscription' ),
                permissions=( CMFCorePermissions.View, ),
                category='folder',
                visible=1,
                condition=Expression('python: object.getSite() is not None'),
            ),
            AI(
                id='subscribed',
                title="View subscribed users",
                description="View subscribed users to topic updates.",
                action=Expression( 'string: ${object_url}/view_subscribed' ),
                permissions=( CMFCorePermissions.AddPortalContent, ),
                category='folder',
                visible=1,
                condition=Expression('python: object.getSite() is not None'),
            ),
        )

    _properties = SimpleNauItem._properties

    # default attribute values
    main_page = ''
    inherit_categories = True
    _maxNumberOfPages = 0
    _archiveProperty  = None

    # is unownerable
    _owner_role = None

    security.declareProtected( CMFCorePermissions.View, 'directive' )
    directive = ProxyReaderFactory( 'directive' )

    def __init__( self, id, title=None, **kwargs ):
        """
            Constructor method.
        """
        SimpleNauItem.__init__( self, id, title, **kwargs )
        PortalFolder.__init__( self, id, self.title )

    def _initstate( self, mode ):
        # initialize attributes
        if not SimpleNauItem._initstate( self, mode ):
            return False

        # set owner the same as the current editor
        if getattr( self, '_owner', None ) is None:
            editors = self.users_with_local_role( Roles.Editor )
            if editors:
                self._v_change_owner = editors[0]

        # fix permissions on old folders
        try:
            perm  = Permission( CMFCorePermissions.View, (), self )
            roles = perm.getRoles()
            if type(roles) is ListType and Roles.Member not in roles:
                perm.setRoles( (Roles.Manager, Roles.Owner, Roles.Author, Roles.Editor, Roles.Reader, Roles.Writer) )
        except:
            pass

        if getattr( self, 'subscribed_users', None ) is None:
            self.subscribed_users = OIBTree()
        if type( self.subscribed_users ) is ListType:
            su = OIBTree()
            for uname in self.subscribed_users:
                su[ uname ] = 1
            self.subscribed_users = su

        if getattr( self, 'pending_subscriptions', None ) is None:
            self.pending_subscriptions = OOBTree()
        if type( self.pending_subscriptions ) is DictType:
            ps = OOBTree()
            ps.update( self.pending_subscriptions )
            self.pending_subscriptions = ps

        if getattr( self, '_viewingOrder', None ) is None:
            self._viewingOrder = [] # tuple of ids

        if getattr( self, '_viewingDocumentOrder', None ) is None:
            self._viewingDocumentOrder = [] # tuple of ids

        try:    delattr( self, '_directives' )
        except: pass
        try:    delattr( self, 'display_mode' )
        except: pass

        return True

    def Creator( self ):
        """ XXX Overriden to apply new owner rules
        """
        owner = getattr( self, '_v_change_owner', None )
        if owner is not None:
            delattr( self, '_v_change_owner' )

            try: self.changeOwnership( owner )
            except: pass

        return SimpleNauItem.Creator( self )

    security.declareProtected( CMFCorePermissions.View, 'editor' )
    def editor( self ):
        """
            Get folder editor
        """
        userids = []
        ob = self

        while not ob.implements('isPortalRoot'):
            userids = ob.users_with_local_role( Roles.Editor )
            if userids:
                break
            ob = ob.parent()

        return userids

    security.declareProtected( CMFCorePermissions.View, 'getEditor' )
    def getEditor( self ):
        """
            Returns this folder's editor.

            Result:

                'MemberData' object or 'None' if editor is unassigned.
        """
        userids = self.editor()
        if not userids:
            return None
        return getToolByName( self, 'portal_membership' ).getMemberById( userids[0] )

    security.declareProtected( CMFCorePermissions.View, 'getFolderFilter' )
    def getFolderFilter( self, REQUEST=None ):
        """ Return and cache current content filter
        """
        REQUEST = REQUEST or self.REQUEST

        mbstool = getToolByName( self, 'portal_membership' )
        filter  = mbstool.getFilter( REQUEST )
        cfilter = filter['filter']
        nfilter = filter['name']

        cfilter = self.decodeFolderFilter( cfilter )
        if nfilter or cfilter:
            cfilter['name'] = nfilter

        return cfilter

    security.declareProtected( CMFCorePermissions.View, 'listDocuments' )
    def listDocuments( self, REQUEST=None, **kw ):
        """ Return visible documents in this folders
        """
        REQUEST = REQUEST or aq_get( self, 'REQUEST' )

        query   = kw
        limit   = query.get('sort_on') and query.has_key('sort_limit') or 0
        cfilter = self.getFolderFilter( REQUEST )
        result  = []

        # TODO: move this to type information
        # should be a list of all nonfolderish types from the types_tool
        allowed_default = [ t.getId() for t in self.allowedContentTypes() ]
        types = list( cfilter.get( 'Type', allowed_default ) )
        if not types:
            return limit and (result, 0) or result

        catalog = getToolByName( self, 'portal_catalog' )
        mstool = getToolByName( self, 'portal_membership' )

        use_path = self.parent().implements('isPortalRoot') \
                   and not cfilter.get('Root', None) \
                   or mstool.getCurrentFolderView() == 'outgoing'
        path_idx = use_path and 'path' or 'parent_path'

        try: arch = int( REQUEST.get('arch_cookie') )
        except (TypeError, ValueError): arch = 0

        query.setdefault(path_idx, self.physical_path())
        query.setdefault('implements', 'isPortalContent')
        query.setdefault('portal_type', types)
        query.setdefault('Creator' , cfilter.get('Creator', ''))
        query.setdefault('state', {'query':'archive', 'operator':(arch and 'or' or 'not')} )

        if path_idx == 'path':
            query.setdefault('nd_uid', { 'query': self.getUid(), 'operator' : 'not' } )

        result = catalog.searchResults( **query )


        if limit:
            return (result, result and result.actual_result_count or 0)
        else:
            return result

    security.declareProtected( CMFCorePermissions.View, 'listDirectives' )
    def listDirectives( self, cfilter=None, REQUEST=None, **kw  ):
        """ Return all directive documents in this and parent folders
        """
        catalog = getToolByName( self, 'portal_catalog', None )
        if catalog is None:
            return ()

        query   = kw
        limit   = query.get('sort_on') and query.has_key('sort_limit') or 0

        top  = len( catalog.getPhysicalPath() )
        path = list( self.getPhysicalPath() )
        #path[0] = pathdelim

        path = [ joinpath( path[:i] ) for i in range( top, len(path) + 1 ) ]

        result = catalog.unrestrictedSearch( parent_path=path, hasBase='Directive', state='effective', allowedRolesAndUsers=[Roles.Reader], **kw )

        if limit:
            return (result, result and result.actual_result_count or 0)
        else:
            return result

    security.declareProtected( CMFCorePermissions.View, 'hasMainPage' )
    def hasMainPage( self ):
        """
           Check whether this folder is in the main page mode
        """
        return not not self.main_page

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setMainPage' )
    def setMainPage( self, object ):
        """
           Set mark on the topic, that some of it's documents
           must be used as index page, when publishing to external site.

           mode values:
              0 - documents list
              1 - main page
        """
        if object is None:
            uid = ''
        else:
            uid = object.getUid()

        if uid == self.main_page:
            return

        self.main_page = uid
        self.updateRemoteCopy( recursive=0 )

    security.declareProtected( CMFCorePermissions.View, 'getMainPage' )
    def getMainPage( self ):
        """ Return main document for topic
        """
        uid = self.main_page
        if not uid:
            return None

        catalog = getToolByName( self, 'portal_catalog' )
        query   = {
                    'path'      : self.physical_path(),
                    'nd_uid'    : uid,
                  }

        results = catalog.searchResults( **query )
        if not results:
            return None

        return results[0].getObject()

    def manage_fixupOwnershipAfterAdd( self ):
        """ Setup local editor role
        """
        if self.parent().implements('isPortalRoot'):
            self.changeOwnership( None, recursive=0, explicit=1 )
            return

        PortalFolder.manage_fixupOwnershipAfterAdd( self )

        member = self.getOwner()
        if member is not None:
            mstool = getToolByName( self, 'portal_membership' )
            member = mstool.getMemberById( member.getUserName() )

        if member is None:
            self.changeOwnership( None, recursive=0, explicit=1 )
            return

        self.setLocalRoles( member.getUserName(), [Roles.Editor] )
        self.manage_permission( CMFCorePermissions.View, Config.FolderViewerRoles, 0 )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'manage_changeProperties' )
    def manage_changeProperties( self, REQUEST=None, **kw ):
        """ Change existing object properties
        """
        res = SimpleNauItem.manage_changeProperties( self, REQUEST, **kw )
        self.reindexObject()
        return res

    security.declareProtected( CMFCorePermissions.ChangePermissions, 'manage_permissions' )
    def manage_permissions( self, REQUEST ):
        """
            Change permissions of the given object.
        """
        membership = getToolByName( self, 'portal_membership' )
        groups = membership.listGroups()
        roles_map = {}

        valid_roles = membership.getPortalObject().valid_roles()
        valid_roles = [ role for role in self.managed_roles if role in valid_roles ]

        # read the desirable configuration from REQUEST
        for group in groups:
            roles = REQUEST.get( group.getId() ) or []
            roles = [ role for role in roles if role in valid_roles ]
            if roles:
                roles_map[ group.getId() ] = roles

        # reset local roles settings
        self.manage_delLocalGroupRoles( [ group.getId() for group in groups ] )

        # assign local roles to the groups
        for group in roles_map.keys():
            self.manage_setLocalGroupRoles( group, roles_map[group] )

        self.reindexObject( idxs=['allowedRolesAndUsers'], recursive=1 )

        if REQUEST is not None:
            self.redirect( action='manage_access_form', REQUEST=REQUEST )

    security.declareProtected( CMFCorePermissions.ChangePermissions, 'setLocalRoles' )
    def setLocalRoles( self, userids, roles, REQUEST=None ):
        """
            Wrapper for the built-in manage_setLocalRoles
        """
        changed = 0

        roles      = list( roles )
        man_roles  = self.managed_roles
        if not isSequence( userids ):
            userids = [ userids ]

        if Roles.Editor in roles and len( userids ) > 1:
            raise SimpleError, 'No more then one editor is allowed'

        for userid in userids:
            old_roles  = list( self.get_local_roles_for_userid( userid ) )
            user_roles = self.getLocalRoles( userid )

            # find all roles inherited from the upper folders
            inherited = {}
            for rlist in user_roles[1:]:
                for role in rlist:
                    inherited[ role ] = 1

            membership = getToolByName( self, 'portal_membership' )
            if not membership.isAnonymousUser():
                cur_user = membership.getAuthenticatedMember().getUserName()
                if cur_user == userid \
                        and Roles.Owner not in old_roles \
                        and not inherited.has_key( Roles.Editor ) \
                        and not _checkPermission( CMFCorePermissions.ManagePortal, self ):
                    if REQUEST is None:
                        return
                    return self.redirect( action='manage_access_form',
                                          message="You are not allowed to change your own access rights." )

            # allow editor role to be reassigned
            try: del inherited[ Roles.Editor ]
            except KeyError: pass

            # don't reassign inherited roles
            roles = filter( lambda r, d=inherited: not d.has_key(r), roles )

            # see whether *userid* is the main editor
            editors   = self.users_with_local_role( Roles.Editor )
            is_editor = len(editors) == 1 and editors[0] == userid

            # *editors* are all the explicit editors excluding *userid*
            try: editors.remove( userid )
            except ValueError: pass

            if Roles.Editor in roles:
                # set *changed* only if *userid* is not the main editor already
                changed = not is_editor
                # the main editor is also the owner of the folder
                self.changeOwnership( userid, recursive=0, explicit=1 )

                # if *changed* then *editors* (may) include previous editor
                if changed and editors:
                    rdict = getattr( self, '__ac_local_roles__', None )

                    # delete all the previous editors
                    for editor in editors:
                        editor_roles = rdict and rdict.get( editor ) or []
                        editor_roles.remove( Roles.Editor )

                        # if *editor* has no other roles in the folder,
                        # grant her the reader role at least
                        if not editor_roles:
                            editor_roles.append( Roles.Reader )

                        self.manage_setLocalRoles( editor, editor_roles )

            elif Roles.Editor in old_roles:
                # editor role is being revoked from *userid*
                changed = 1
                # change owner to the next editor in the list, or no owner
                editor  = editors and editors[0] or None
                self.changeOwnership( editor, recursive=0 )

            if changed:
                # request the nav tree menu refresh when the editor was changed
                refreshClientFrame( Config.NavTreeMenu )

            # preserve system roles (e.g. owner in home folders)
            for role in old_roles:
                if not ( role in man_roles or role in roles ):
                    roles.append( role )

            roles.sort()
            old_roles.sort()

            if roles != old_roles:
                if roles:
                    self.manage_setLocalRoles( userid, roles )
                else:
                    self.manage_delLocalRoles( (userid,) )
                changed = 1

        if changed:
            # update portal_catalog indexes
            self.reindexObject( idxs=['allowedRolesAndUsers','Creator'], recursive=1 )

        if REQUEST is not None:
            # user may have removed her own roles
            if _checkPermission( CMFCorePermissions.ChangePermissions, self ):
                action = 'manage_access_form'
            else:
                action = 'folder'

            return REQUEST.RESPONSE.redirect(
                    self.absolute_url( redirect=1, action=action,
                                       message="Access rights have been granted." ),
                    status=303 )

    security.declareProtected( CMFCorePermissions.ChangePermissions, 'delLocalRoles' )
    def delLocalRoles( self, userids=[], REQUEST=None ):
        """ Wrapper for the built-in manage_delLocalRoles
        """
        if type(userids) is StringType:
            userids = ( userids, )

        if not userids and REQUEST is not None:
            return self.redirect( action='manage_access_form',
                                  message="Please select at least one user." )

        editors = self.users_with_local_role( Roles.Editor )
        is_editor = len(editors) and editors[0] in userids

        membership = getToolByName( self, 'portal_membership' )
        if not membership.isAnonymousUser():
            cur_user = membership.getAuthenticatedMember().getUserName()
            if cur_user in userids and not _checkPermission( CMFCorePermissions.ManagePortal, self ):
                user_roles = self.getLocalRoles( cur_user )
                # find all roles inherited from the upper folders
                inherited = {}
                for rlist in user_roles[1:]:
                    for role in rlist:
                        inherited[ role ] = 1
                if Roles.Editor not in inherited.keys():
                    if REQUEST is None:
                        return
                    return self.redirect( action='manage_access_form',
                                          message="You are not allowed to remove your own access rights." )

        for userid in userids:
            try: editors.remove( userid )
            except ValueError: pass

        if is_editor:
            editor = editors and editors[0] or None
            self.changeOwnership( editor, recursive=0 )

            # request the nav tree menu refresh when editor was changed
            refreshClientFrame( Config.NavTreeMenu )

        man_roles = self.managed_roles

        for userid in userids:
            roles = list( self.get_local_roles_for_userid( userid ) )

            for role in man_roles:
                try: roles.remove( role )
                except ValueError: pass

            if roles:
                self.manage_setLocalRoles( userid, roles )
            else:
                self.manage_delLocalRoles( (userid,) )

        # update portal_catalog indexes
        self.reindexObject( idxs=['allowedRolesAndUsers','Creator'], recursive=1 )

        if REQUEST is not None:
            # user may have removed her own roles
            if _checkPermission( CMFCorePermissions.ChangePermissions, self ):
                action = 'manage_access_form'
            else:
                action = 'folder'

            return REQUEST.RESPONSE.redirect(
                    self.absolute_url( redirect=1, action=action,
                                       message="Access rights have been removed." ),
                    status=303 )

    security.declareProtected( CMFCorePermissions.ChangePermissions, 'getLocalRoles' )
    def getLocalRoles( self, userid=None ):
        """
           Return all local roles assigned over this object
        """
        info   = []
        mroles = self.managed_roles
        object = self

        # walk through the whole CMF Site and gather all
        # acquired roles that are applied to the object
        while not object.implements('isPortalRoot'):
            rdict = getattr( object, '__ac_local_roles__', None )
            if rdict is not None:

                if userid is not None:
                    roles = rdict.get( userid )
                    roles = roles and filter( lambda r, m=mroles: r in m, roles )
                    if roles:
                        info.append( roles )

                else:
                    users = rdict.keys()
                    users.sort()
                    # user is a dict key, value
                    for user in users:
                        # be aware about managed_roles only
                        roles = rdict[ user ]
                        roles = filter( lambda r, m=mroles: r in m, roles )
                        if roles:
                            if object is not self:
                                # mark inherited roles
                                roles.insert( 0, '__inherited' )
                            info.append( (user, roles) )

            if userid and not info:
                info.append( () )

            object = object.parent()

        return tuple(info)

    security.declareProtected(CMFCorePermissions.View, 'user_roles')
    def user_roles(self):
        """
           Get the users' role list within current context
        """
        membership = getToolByName( self, 'portal_membership' )
        roles = membership.getAuthenticatedMember().getRolesInContext(self)
        roles = filter( lambda x, self=self: x in self.managed_roles, roles )

        return roles

    def invokeFactory( self, type_name, id, RESPONSE=None, restricted=True, *args, **kwargs ):
        """
            Invokes the portal types tool to construct a new content
            object in this folder.
        """
        if restricted is not Trust:
            types = getToolByName( self, 'portal_types' )
            info = types.getTypeInfo( type_name )

            if info.typeImplements('isCategorial'):
                # for category-aware types, valid category ID must be
                # specified, and that category must be allowed in properties
                category = kwargs.get('category')

                if type(category) is StringType:
                    metadata = getToolByName( self, 'portal_metadata' )
                    category = metadata.getCategory( category, None )

                if category is None:
                    raise ValueError, kwargs.get('category')

                if category.disallowManual() or \
                        not category.isTypeAllowed( info ) or \
                        not self.isCategoryAllowed( category ):
                    raise SimpleError( 'categories.category_disallowed', category=category.Title() )

        return PortalFolder.invokeFactory( self, type_name, id, RESPONSE, *args, **kwargs )

    def notifyWorkflowCreated( self ):
        SimpleNauItem.notifyWorkflowCreated( self )
        # XXX a hack to make folders searchable from external sites
        if self.getSite() is not None:
            self.changePermission( CMFCorePermissions.View, append=[Roles.Visitor] )

    security.declarePublic( 'allowedContentTypes' )
    def allowedContentTypes( self, construction=False ):
        """ List type info objects for types which can be added in this folder.
        """
        types = []
        tptool = getToolByName( self, 'portal_types' )
        my_type = tptool.getTypeInfo( self )

        if my_type is not None:
            container = construction and self or None
            for tinfo in tptool.listTypeInfo( container ):
                if my_type.allowType( tinfo.getId(), construction=construction ):
                    types.append( tinfo )
        else:
            types = tptool.listTypeInfo()

        if not construction:
            return types

        if self.parent().implements('isPortalRoot'):
            # TODO: must use some property/feature
            types = [ t for t in types if t.getId() in ['Heading','Site Container'] ]

        types = [ t for t in types if t.isConstructionAllowed( self ) ]
        categories = self.listAllowedCategories( construction=construction )
        allowed = []

        for tinfo in types:
            if not tinfo.typeImplements('isCategorial'):
                allowed.append( tinfo )
                continue
            for category in categories:
                if category.isTypeAllowed( tinfo ) and \
                   category.hasInitialStateOrTransition():
                    allowed.append( tinfo )
                    break

        return allowed

    def _verifyObjectPaste(self, object, validate_src = 1):
        """
            Verify whether an object can be pasted here.
        """
        types = getToolByName(self, 'portal_types')
        my_type = types.getTypeInfo(self)
        obj_type = types.getTypeInfo(object)

        if not (my_type and obj_type and my_type.allowType(obj_type.getId())):
            raise CopyError # TODO: add message

        # TODO: better message
        _ = getToolByName(self, 'msg')
        for permission in obj_type.getProperty('permissions', ()):
            if not _checkPermission(permission, self):
                raise SimpleError(
                        "You are not allowed to paste '%(type)s' objects here",
                        type = _(obj_type.Title())
                      )

        return PortalFolder._verifyObjectPaste(self, object, validate_src)


    security.declareProtected( CMFCorePermissions.View, 'deleteObjects' )
    def deleteObjects( self, ids ):
        """
            Check 'delete objects' permission on every remove operation
        """
        allowed = []
        mbtool  = getToolByName( self, 'portal_membership', None )

        for id in ids:
            ob = self._getOb( id, None )
            if ob is None or not mbtool.checkPermission( ZopePermissions.delete_objects, ob ):
                continue

            if ob.implements('isLockable'):
                try: ob.failIfLocked()
                except ResourceLockedError: continue

            allowed.append( id )

        count = len(allowed)
        if count:
            ContainerBase.deleteObjects( self, allowed )

        return count

    security.declareProtected( CMFCorePermissions.ManageProperties, 'reindexObject' )
    def reindexObject( self, idxs=[], recursive=None ):
        """
            Reindex folder and optionally all the objects inside.
        """
        if recursive:
            catalog = getToolByName( self, 'portal_catalog' )
            for item in catalog.unrestrictedSearch( path=self.physical_path() ):
                obj = item.getObject()
                if obj is not None and not isBroken( obj ):
                    if not hasattr( aq_base( obj ), 'reindexObject' ):
                        continue

                    if obj.implements( ['isVersionable','isVersion'] ):
                        # prevents double reindex of versionables and principal versions
                        obj.reindexObject( idxs=idxs, versionable=False )
                    else:
                        obj.reindexObject( idxs=idxs )
        else:
            CMFCatalogAware.reindexObject.im_func( self, idxs )

    def getBadLinks(self):
        """
            this function return list of documents and bad links,
            included in given documents in format
            [[document, links_count, [bad_link1, ...]], ...]
        """
        expr = '<[\s]*a[^<^>]+href[\s]*=[\s]*"([^"]+)"[^<^>]*>[^<]*<[\s]*/a[\s]*>'
        url_expr = re.compile(expr, re.IGNORECASE)
        res = []

        for element in self.objectValues():
            if element.meta_type in ['HTMLDocument']:
                badLinks = []
                link = url_expr.search( element.EditableBody() )
                while link:
                    url = link.groups()[0]
                    try:
                        urlopen(url)
                    except:
                        err=exc_info()
                        try:
                            if not hasattr(err[1], 'code') or err[1].code!=401:
                                badLinks.append(link.groups()[0])
                        finally:
                            err = None
                    link = url_expr.search(element.EditableBody(), link.end())
                if len(badLinks)>0:
                    res.append([element, len(badLinks), badLinks])
            elif isinstance( element, Heading ):
                res = res + element.getBadLinks()
        return res

    #
    # Subscription interface methods
    #

    security.declareProtected( CMFCorePermissions.View, 'subscribe' )
    def subscribe( self, email=None, publisher=None, REQUEST=None ):
        """
          Subscribe user to news on current heading (request confirmation)
        """
        try:
            if email is None: # subscribe member
                membership = getToolByName( self, 'portal_membership' )

                if membership.isAnonymousUser():
                    raise SimpleError, "You must be logged in to subscribe."

                member = membership.getAuthenticatedMember()
                uname  = member.getUserName()
                email  = member.getMemberEmail()

                if not email:
                    raise SimpleError, "You have no configured e-mail address yet. Please specify it in your account preferences."

            # TODO: security check - non-members cannot subscribe to not published topics

            elif email.find('@') < 0: # TODO: make function to check email address
                raise SimpleError, "Incorrect e-mail address."

            else:
                member = None
                uname  = email

            if self._is_subscribed( uname ):
                raise SimpleError, "You already receive announcements from either this or parent topic."

            if member:
                return self.confirm_subscription( member, None, REQUEST )

            secret_code = str(int( DateTime() ))
            self.pending_subscriptions[ uname ] = secret_code

            # Generate an url that must be called to confirm subscription
            server_url = REQUEST is not None and REQUEST['SERVER_URL'] or self.server_url
            subscription_url = server_url + self.external_url( 0, action='subscription',
                params={ 'action':'confirm', 'email':uname, 'secret_code':secret_code } )

            # Send a mail to the user
            try:
                lang = self.msg.get_selected_language()
            except AttributeError:
                lang = self.msg.get_default_language()

            mail_text = self.subscription_on(self, REQUEST,
                                             heading_title = self.title,
                                             subscription_url = subscription_url,
                                             lang = lang
                                            )
            server = getToolByName( self, 'MailHost' )
            server.send( server.createMessage( source=mail_text ), [email] )

        except SimpleError, s:
            status = s

        else:
            status = "Your request processed. Check your e-mail and confirm subscription to start receiving announcements from this folder."
        if REQUEST is None or publisher:
            return status
        else:
            return REQUEST.RESPONSE.redirect(
                    self.absolute_url( action='folder', message=status ),
                    status=303 )

    def confirm_subscription( self, user, secret_code=None, REQUEST=None, publisher=None):
        ##accept user subscription for news on this heading
        try:
            if type(user) is not StringType:
                uname = user.getUserName()
                email = user.getMemberEmail()
                subscription_url = None
            else:
                email = uname = user

                # Ensure that given secret code matches previously set
                # value from pending_subscriptions
                if self.pending_subscriptions.get( uname ) == str(secret_code):
                    del self.pending_subscriptions[ uname ]
                else:
                    raise SimpleError, "You have not been signed up for the topic updates mailing. Try to subscribe again."

                # Generate an url that must be called to cancel subscription
                server_url = REQUEST is not None and REQUEST['SERVER_URL'] or self.server_url
                subscription_url = server_url + self.external_url(1, action='subscription',
                                        params={ 'action':'unsubscribe', 'email':uname } )

            self.subscribed_users[ uname ] = 1

            # Send a mail to the user
            try:
                lang = self.msg.get_selected_language()
            except AttributeError:
                lang = self.msg.get_default_language()

            mail_text = self.subscription_confirm( self, REQUEST,
                                                    heading_title = self.title_or_id(),
                                                    subscription_url = subscription_url,
                                                    lang = lang
                                                )
            server = getToolByName( self, 'MailHost' )
            server.send( server.createMessage( source=mail_text ), [email] )

        except SimpleError, s:
            status = s

        else:
            status = "Now you will receive update notifications for this folder."

        if REQUEST is None or publisher:
            return status
        else:
            return REQUEST.RESPONSE.redirect(
                    self.absolute_url( action='folder', message=status ),
                    status=303 )

    security.declareProtected( CMFCorePermissions.View, 'unsubscribe' )
    def unsubscribe( self, email=None, REQUEST=None, publisher=None ):
        """ Unsubscribe user from news in heading
        """
        if email is None: # unsubscribe member
            membership = getToolByName( self, 'portal_membership' )

            if membership.isAnonymousUser():
                raise SimpleError, "You must be logged in to unsubscribe."

            member = membership.getAuthenticatedMember()
            uname  = member.getUserName()
            email = member.getMemberEmail()
        else:
            uname  = email

        if not self._is_subscribed( uname ):
            status = "You are not subscribed to this folder."

        else:
            if self._is_subscribed( uname, level=1 ):
                self.subscribed_users[ uname ] = 0
            else:
                del self.subscribed_users[ uname ]

            if email:
                # Send a mail to the user
                try:
                    lang = self.msg.get_selected_language()
                except AttributeError:
                    lang = self.msg.get_default_language()

                mail_text = self.subscription_off(self, REQUEST,
                                                  heading_title = self.title_or_id(),
                                                  lang = lang
                                                 )

                server = getToolByName( self, 'MailHost' )
                server.send( server.createMessage( source=mail_text ), [email] )

            status = "You have been unsubscribed."

        if REQUEST is None or publisher:
            return status
        else:
            return REQUEST.RESPONSE.redirect(
                    self.absolute_url( action='folder', message=status ),
                    status=303 )

    security.declarePublic( 'isSubscribed' )
    def isSubscribed( self, REQUEST=None ):
        """ Check whether current user is subscribed to this topic.
        """
        membership = getToolByName( self, 'portal_membership' )
        if membership.isAnonymousUser():
            return 0
        return self._is_subscribed( membership.getAuthenticatedMember() )

    def announce_publication( self, ob, REQUEST=None ):
        """
            Passes document properties to site's announce demon.

            That demon, when starts, generates email message for each
            subscribed user with announces of all documents that were
            published since last start.

            Arguments:

                'ob' -- document which was published

                'REQUEST' -- REQUEST object
        """
        external_site = self.getSite()

        if external_site is None:
            return

        wftool = getToolByName( self, 'portal_workflow' )
        rh = wftool.getInfoFor(ob, 'review_history')

        if not rh:
            return

        if rh[-1]['action']!='publish' or not rh[-1].get('published'):
            return

        external_site.addPublication(self.getUid(), ob.getId(), rh[-1]['time'])


    security.declareProtected( CMFCorePermissions.AddPortalContent, 'listSubscribed' )
    def listSubscribed(self):
        """List users subscribed here or in upper topics."""
        users = {}
        ob = self

        while not ob.implements('isPortalRoot'):
            if ob.implements('hasSubscription'):
                usrs = [ u for u in ob.subscribed_users.items() if u[1] ]
                for usr, val in usrs:
                    users[usr]=val
            ob = ob.parent()

        return users.keys()

    def _is_subscribed( self, user, level=0 ):
        # Walk to the top of the site and check that user
        # is subscribed to the current folder
        uname, = type(user) is StringType and (user,) or (user.getUserName(),)
        if not uname:
            return 0

        ob = self
        while not ob.implements('isPortalRoot'):
            if level <= 0 and ob.implements('hasSubscription'):
                flag = ob.subscribed_users.get( uname )
                if flag is not None:
                    return flag

            ob = ob.parent()
            level -= 1

        return 0

    security.declareProtected(CMFCorePermissions.ChangePermissions, 'setArchiveProperty')
    def setArchiveProperty(self, archiveProperty):
        self._archiveProperty = archiveProperty

    security.declareProtected(CMFCorePermissions.View, 'getArchiveProperty')
    def getArchiveProperty(self):
        return self._archiveProperty

    security.declareProtected(CMFCorePermissions.ChangePermissions, 'setMaxNumberOfPages')
    def setMaxNumberOfPages(self, maxNumberOfPages):
        self._maxNumberOfPages = maxNumberOfPages

    security.declareProtected(CMFCorePermissions.View, 'getMaxNumberOfPages')
    def getMaxNumberOfPages(self):
        """ """
        return self._maxNumberOfPages

    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'listPublications' )
    def listPublications(self, exact = False, meta_types = (),
                         features = ()):
        """ """
        path_index = exact and 'parent_path' or 'path'

        search_args = { path_index: self.physical_path()
                      , 'state': 'published'
                      , 'implements': features or 'isPublishable'
                      , 'sort_on' : 'Date'
                      , 'sort-order' : 'reverse'
                      }

        if meta_types:
            search_args['meta_type'] = meta_types

        catalog = getToolByName(self, 'portal_catalog')
        results = apply(catalog.searchResults, (), search_args )

        #return results
        ordered_documents_list = []
        documents_ids = []
        ordered_indexes = []
        for i in results:
            documents_ids.append(i.id)
        for i in self.getViewingDocumentOrder():
            try:
                ind = documents_ids.index(i)
                ordered_indexes.append( ind )
            except ValueError:
                pass
        for ind in range(0, len(results)):
            if not ind in ordered_indexes:
                ordered_documents_list.append( results[ind] )
        for ind in ordered_indexes:
            ordered_documents_list.append( results[ind] )
        return ordered_documents_list

    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'getPublishedFolders' )
    def getPublishedFolders( self ):
        """ """
        my_path = self.getPhysicalPath()
        my_len  = len(my_path)
        subfolders = {}

        # filter out folders with no published documents inside
        catalog   = getToolByName( self, 'portal_catalog' )
        published = catalog.searchResults( path=joinpath( my_path ), state='published' )

        for item in published:
            path = item.getPath().split( pathdelim )
            id   = (len(path) > my_len + 1) and path[ my_len ] or None
            if id and not subfolders.has_key( id ):
                subfolder = self[ id ]
                if subfolder.implements('isContentStorage'):
                    subfolders[ id ] = subfolder

        # Do not return object instances, we need only hash
        # with some object information
        subfolders_list = map(lambda x: {'absolute_url': x.external_url(),
                                         'meta_type'   : x.meta_type,
                                         'title'       : x.title,
                                         'title_or_id' : x.title_or_id(),
                                         'Description' : x.Description(),
                                         'hasMainPage' : x.hasMainPage(),
                                         'id'          : x.getId()
                                        },
                           subfolders.values() )

        ordered_subfolders_list = []
        subfolders_ids = []
        ordered_indexes = []

        for i in subfolders_list:
            subfolders_ids.append(i['id'])

        for i in self.getViewingOrder():
            try:
                ind = subfolders_ids.index(i)
                ordered_indexes.append( ind )
            except ValueError:
                pass

        for ind in range(0, len(subfolders_list)):
            if not ind in ordered_indexes:
                ordered_subfolders_list.append( subfolders_list[ind] )

        for ind in ordered_indexes:
            ordered_subfolders_list.append( subfolders_list[ind] )

        return ordered_subfolders_list

    security.declareProtected(CMFCorePermissions.ChangePermissions, 'shiftDocument')
    def shiftDocument(self, id, order):
        """ """
        documents_list = self.listPublications( exact=1 )
        self._viewingDocumentOrder = map(lambda x: x.id, documents_list)
        doc_pos = self._viewingDocumentOrder.index(id)
        temp_id = self._viewingDocumentOrder[doc_pos]
        order=int(order)
        if order==1:
            if doc_pos != len(self._viewingDocumentOrder)-1 and doc_pos != self.getMaxNumberOfPages()-1:
                self._viewingDocumentOrder[doc_pos] = self._viewingDocumentOrder[ doc_pos+1]
                self._viewingDocumentOrder[doc_pos+1] = temp_id
        elif order==2:
            last_pos = (self.getMaxNumberOfPages() or len(self._viewingDocumentOrder))-1
            if last_pos > len(self._viewingDocumentOrder)-1:
                last_pos = len(self._viewingDocumentOrder)-1
            self._viewingDocumentOrder = self._viewingDocumentOrder[:doc_pos] + self._viewingDocumentOrder[ (doc_pos+1):(last_pos+1) ] \
                                         + [self._viewingDocumentOrder[doc_pos], ] + self._viewingDocumentOrder[ (last_pos+1): ]
        elif order==-1:
            if doc_pos:
                self._viewingDocumentOrder[doc_pos] = self._viewingDocumentOrder[doc_pos-1]
                self._viewingDocumentOrder[doc_pos-1] = temp_id
        elif order==-2:
            self._viewingDocumentOrder = [self._viewingDocumentOrder[doc_pos], ] + self._viewingDocumentOrder[:doc_pos] \
                                         + self._viewingDocumentOrder[(doc_pos+1):]

        self._p_changed = 1


    security.declareProtected(CMFCorePermissions.ChangePermissions, 'shiftHeading')
    def shiftHeading(self, id, order):
        """ """
        subfolders_list = self.getPublishedFolders()
        self._viewingOrder = map(lambda x: x['id'], subfolders_list)

        doc_pos = self._viewingOrder.index(id)
        temp_id = self._viewingOrder[doc_pos]
        order=int(order)
        if order==1:
            if doc_pos != len(self._viewingOrder)-1:
                self._viewingOrder[doc_pos] = self._viewingOrder[doc_pos+1]
                self._viewingOrder[doc_pos+1] = temp_id
        elif order==2:
            self._viewingOrder = self._viewingOrder[:doc_pos] + self._viewingOrder[ (doc_pos+1): ] \
                                         + [self._viewingOrder[doc_pos], ]
        elif order==-1:
            if doc_pos:
                self._viewingOrder[doc_pos] = self._viewingOrder[doc_pos-1]
                self._viewingOrder[doc_pos-1] = temp_id
        elif order==-2:
            self._viewingOrder = [self._viewingOrder[doc_pos], ] + self._viewingOrder[:doc_pos] \
                                         + self._viewingOrder[(doc_pos+1):]

        self._p_changed = 1


    security.declareProtected(CMFCorePermissions.View, 'getViewingDocumentOrder')
    def getViewingDocumentOrder(self):
        """ """
        try:
            return self._viewingDocumentOrder
        except:
            self._viewingDocumentOrder = []
            self._p_changed = 1
            return self._viewingDocumentOrder

    security.declareProtected(CMFCorePermissions.View, 'getViewingOrder')
    def getViewingOrder(self):
        """ """
        try:
            return self._viewingOrder
        except:
            self._viewingOrder = []
            self._p_changed = 1
            return self._viewingOrder

    security.declareProtected(CMFCorePermissions.View, 'getContentsSize')
    def getContentsSize( self ):
        """
           Returns number of objects in folder
        """
        return len(self.objectIds())

    def _remote_transfer( self, context=None, container=None, server=None, path=None, id=None, parents=None, recursive=None ):
        """
        """
        remote = SyncableContent._remote_transfer( self, context, container, server, path, id, parents, recursive )
        if not recursive:
            return remote

        ppath = joinpath( path, remote.getId() )

        for id, ob in self.objectItems():
            if isinstance( ob, SyncableContent ):
                try: ob._remote_transfer( context, remote, server, ppath, id, 0, recursive )
                except: pass

        return remote

    def _remote_export( self, context=None, file=None, skip_ids=None ):
        # local object export -- leave out local folder contents
        skip_ids = skip_ids or []
        skip_ids.append( '_objects' )
        skip_ids.extend( self.objectIds() )

        return SyncableContent._remote_export( self, context, file, skip_ids )

    def _remote_import( self, file, save_ids=None ):
        # remote object import -- retain remote folder contents
        save_ids = save_ids or []
        save_ids.append( '_objects' )
        save_ids.extend( self.objectIds() )

        return SyncableContent._remote_import( self, file, save_ids )

    security.declareProtected( CMFCorePermissions.View, 'getCategoryInheritance' )
    def getCategoryInheritance( self ):
        """
            Returns allowed categories inheritance flag.

            Result:

                Boolean.
        """
        return self.inherit_categories

    security.declareProtected( CMFCorePermissions.ChangePermissions, 'setCategoryInheritance' )
    def setCategoryInheritance( self, inherit ):
        """
            Sets the allowed categories inheritance flag.

            Arguments:

                'inherit' -- boolean
        """
        self.inherit_categories = bool( inherit )

    security.declareProtected( CMFCorePermissions.View, 'isCategoryAllowed' )
    def isCategoryAllowed( self, category ):
        """
            Checks whether the given content category is allowed
            for objects in this folder.

            Arguments:

                'category' -- either category Id string
                              or category definition object

            Result:

                Boolean value, true if the category is allowed.
        """
        if isinstance( category, StringType ):
            metadata = getToolByName( self, 'portal_metadata' )
            category = metadata.getCategory( category )

        links = getToolByName( self, 'portal_links' )
        results = links.searchLinks( source=self, source_collection='categories',
                                     target=category, relation='collection' )
        if results:
            return True
        if not self.inherit_categories:
            return False

        if self.parent().implements('isPortalRoot'): # XXX need special Feature
            return True

        return self.parent().isCategoryAllowed( category )

    security.declareProtected( CMFCorePermissions.View, 'listAllowedCategories' )
    def listAllowedCategories( self, type_id=None, explicit=None, inherited=None,
                               construction=False, append=None ):
        """
            List category definition objects for allowed categories in this folder.

            Arguments:

                'type_id' -- optional type identifier; if given, limit categories
                             list to those allowed by this object type

                'explicit' -- list only categories explicitly allowed in this folder

                'inherited' -- list only categories allowed in parent folders

                'construction' -- filter out categories disallowed for manual
                                  assignment by the user

                'append' -- id of an extra category to append to the results

            Result:

                List of category definition objects.
        """
        metadata = getToolByName( self, 'portal_metadata' )
        parent = self.parent()

        if explicit is inherited is None:
            explicit  = True
            inherited = self.inherit_categories

        if inherited:
            if self.parent().implements('isPortalRoot'): # XXX need special Feature
                categories = metadata.listCategories()
            else:
                categories = parent.listAllowedCategories()
        else:
            categories = []

        if explicit or append:
            mark   = {}
            marked = mark.has_key
            # TODO should use resource uids in mark
            for category in categories:
                mark[ category.getId() ] = True

        if explicit:
            links = getToolByName( self, 'portal_links' )
            results = links.searchLinks( source=self, source_collection='categories',
                                         relation='collection' )
            for item in results:
                assert not item['target_removed']
                id = item['target_uid'].uid # XXX
                if not marked( id ):
                    categories.append( metadata.getCategory(id) )
                    mark[ id ] = True

        if construction:
            categories = [ category for category in categories
                                    if not category.disallowManual() ]

        if append:
            id = isinstance( append, StringType ) and append or append.getId()
            if not marked( id ):
                categories.append( metadata.getCategory(id) )
                mark[ id ] = True

        if type_id:
            categories = [ category for category in categories
                                    if category.isTypeAllowed( type_id ) and \
                                    category.hasInitialStateOrTransition() ]

        return categories

    security.declareProtected(CMFCorePermissions.ChangePermissions, 'setAllowedCategories')
    def setAllowedCategories( self, categories ):
        """
            Sets allowed categories in this folder.

            Arguments:

                categories -- list of category definition objects or their Ids
        """
        allowed = []
        dropped = []

        metadata = getToolByName( self, 'portal_metadata' )
        for category in categories:
            if isinstance( category, StringType ):
                category = metadata.getCategory( category )
            assert category and category.implements('isCategoryDefinition')
            allowed.append( category.getResourceUid() )

        # TODO must move the following into updateLink or something

        links = getToolByName( self, 'portal_links' )
        results = links.searchLinks( source=self, source_collection='categories',
                                     relation='collection' )
        for item in results:
            assert not item['target_removed']
            try:
                allowed.remove( item['target_uid'] )
            except ValueError:
                dropped.append( item['id'] )

        for uid in allowed:
            links.createLink( source=self, source_collection='categories',
                              target=uid, relation='collection' )
        if dropped:
            links.removeLinks( dropped )

    security.declareProtected(CMFCorePermissions.View, 'popObjectFromClipboard')
    def popObjectFromClipboard(self, context, REQUEST=None, number=0):
        """
            Cuts object from Clipboard and pastes in into current folder.

            Arguments:

                'REQUEST' - optional Zope request object

                'context' - context

                'number'  - number of object in clipboard

            Result:

                ZODB object
        """
        cp_objects = listClipboardObjects( context, REQUEST=REQUEST, feature='isFSFile' )


        source_object = cp_objects[number]
        new_object_id = cookId(context, REQUEST.get('id', source_object.getId()) )
        new_object_title = REQUEST.get('title', source_object.Title())

        context.invokeFactory(
            type_name=REQUEST.get('type_name', 'HTMLDocument'),
            id = new_object_id,
            title=new_object_title,
            category = REQUEST.get('cat_id', 'Document'),
            description = REQUEST.get('description', '')
            )

        new_object = context[ new_object_id ]
        new_object.addFile( source_object.wrapWithFileUpload(), title=new_object_title, try_to_associate=1, paste=1 )

        del cp_objects[number]

        oblist = []
        for ob in cp_objects:
            if not ob.cb_isCopyable():
                raise CopyError, eNotSupported % id
            m=Moniker(ob)
            oblist.append(m.dump())
        cp=(0, oblist)
        cp=_cb_encode(cp)
        REQUEST.RESPONSE.setCookie('__cp', cp, path='%s' % REQUEST['BASEPATH1'] or "/")
        REQUEST.set('__cp', cp)
        return new_object

InitializeClass( Heading )

def manage_addHeading( self, id, title=None, category='Folder', set_owner=True, REQUEST=None, **kwargs ):
        """ Add a new Heading object with id *id*.
        """
        obj = Heading( id, title, category=category, **kwargs )
        self._setObject( id, obj, set_owner=set_owner )

        #if REQUEST is not None:
        #    return self.folder_contents( self, REQUEST, portal_status_message="Topic added" )

# this installer depends on Config.SystemFolders constant
class FoldersInstaller:
    after = True
    name = 'setupFolders'
    priority = 70 # depends on CatPhaseOne and Workflow installers
    
    def install(self, portal, force=True, check=False):
        membership = getToolByName( portal, 'portal_membership' )
        msgcat = getToolByName( portal, 'msg' )

        lang = msgcat.get_default_language()
        count = 0

        for item in Config.SystemFolders:
            if item.get('optional') and not force:
                continue

            prop = item.get('property')
            if prop and portal.getProperty(prop) is not None:
                continue

            count += 1
            if check:
                continue

            container = portal
            path = item['path'].split('/')
            id = path.pop()

            for cid in path:
                container = container._getOb( cid )

            folder = container._getOb( id, None )
            if folder is None:
                title = msgcat.gettext( item.get('title', id), lang=lang )
                container.invokeFactory( type_name=item.get( 'type', 'Heading' )
                                       , id=id
                                       , title=title
                                       , category='Folder'
                                       )
                folder = container._getOb( id )

            if prop:
                portal._updateProperty( prop, folder )

            if item.get('permissions'):
                for entry in item['permissions']:
                    folder.manage_permission( *entry )
                folder.reindexObject( idxs=['allowedRolesAndUsers'], recursive=1 )

            if item.get('roles'):
                for name, roles, group in item['roles']:
                    if group:
                        if membership.getGroup( name, None ) is None:
                            continue
                        folder.manage_addLocalGroupRoles( name, roles )
                    else:
                        if membership.getMemberById( name ) is None:
                            continue
                        folder.manage_addLocalRoles( name, roles )
                folder.reindexObject( idxs=['allowedRolesAndUsers'], recursive=1 )

        return count

    __call__ = install


def initialize( context ):
    # module initialization callback

    context.registerContent( Heading, manage_addHeading, HeadingType )

    context.registerInstaller( FoldersInstaller )
