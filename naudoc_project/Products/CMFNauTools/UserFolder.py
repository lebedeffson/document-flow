"""
NauDoc user folder class.

$Editor: vpastukhov $
$Id: UserFolder.py,v 1.26 2005/10/19 05:01:43 vsafronovich Exp $
"""
__version__ = '$Revision: 1.26 $'[11:-2]

from base64 import encodestring
from re import search
from types import StringType

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from AccessControl.User import BasicUserFolder
from AccessControl.ZopeSecurityPolicy import _noroles
from Acquisition import aq_base
from DateTime import DateTime

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.NuxUserGroups.UserFolderWithGroups import \
        UserFolderWithGroups, BasicGroupFolderMixin

import Config, Exceptions
from Config import Roles
from SimpleObjects import ContainerBase, SimpleRecord
from Utils import InitializeClass, cookId

if Config.UseLDAPUserFolder:
    from Products.LDAPUserFolder import LDAPUserFolder

class UserFolder( ContainerBase, BasicUserFolder, BasicGroupFolderMixin ):
    """
    """
    _class_version = 1.5

    meta_type = 'NauDoc User Folder'
    id        = 'acl_users'
    title     = 'NauDoc User Folder'
    icon      = 'misc_/OFSP/UserFolder_icon.gif'

    isPrincipiaFolderish = BasicUserFolder.isPrincipiaFolderish

    security = ClassSecurityInfo()

    _properties = ContainerBase._properties + (
            {'id':'auth_frontend', 'type':'boolean', 'mode':'w', 'default':0},
            {'id':'managers_group', 'type':'string', 'mode':'w', 'default':''},
            {'id':'locked_group', 'type':'string', 'mode':'w', 'default':''},
        )

    manage = UserFolderWithGroups.manage
    manage_main = UserFolderWithGroups.manage_main
    manage_options = UserFolderWithGroups.manage_options + \
                     ContainerBase.manage_options

    __users_source__  = None
    __groups_source__ = None

    security.declarePublic( 'getUsersType' )
    def getUsersType( self ):
        """
        """
        return _getAuthType( self.__users_source__ )

    security.declarePublic( 'getGroupsType' )
    def getGroupsType( self ):
        """
        """
        return _getAuthType( self.__groups_source__ )

    security.declarePrivate( 'getSourceFolder' )
    def getSourceFolder( self, auth=None, default=Missing, id=None ):
        """
        """
        folder = id and self._getOb( id, None ) or None

        if folder is None:
            if auth is None:
                auth = _auth_default
            folders = self.objectValues( spec=_auth_types[auth]['meta_type'] )
            if folders:
                # TODO handle multiple subfolders of the same type
                folder = folders[0]

        if folder is None:
            if default is Missing:
                raise ValueError, id or auth
            return default

        return folder

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setSourceFolder' )
    def setSourceFolder( self, auth=None, id=None, users=None, groups=None ):
        """
        """
        if users is None and groups is None:
            users = groups = 1

        folder = self.getSourceFolder( auth, id=id )
        folder = aq_base( folder )
        info   = _getAuthInfo( folder )

        # set users source
        ufolder = self.__users_source__
        if users and info['users'] and folder != ufolder:
            ufolder = self.__users_source__ = folder

        # check whether new groups source supports detached groups
        if groups and not info['detached_groups']:
            groups = ( folder.getId() == ufolder.getId() )

        # set groups source
        gfolder = self.__groups_source__
        if groups and info['groups'] and folder != gfolder:
            gfolder = self.__groups_source__ = folder

        # check whether current groups source supports detached groups
        if ufolder != gfolder and not _getAuthInfo( gfolder, 'detached_groups' ):
            # set groups source to either users source or default folder
            if _getAuthInfo( ufolder, 'groups' ):
                self.setSourceFolder( id=ufolder.getId(), groups=1 )
            else:
                # XXX may cause recursion if default type does not support groups
                self.setSourceFolder( _auth_default, groups=1 )
            gfolder = self.__groups_source__

        # XXX a hack to turn local groups on/off in LDAPUserFolder
        if _getAuthType( ufolder ) == 'ldap':
            ufolder._local_groups = ( ufolder != gfolder )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'createAuthFolder' )
    def createAuthFolder( self, auth=None, id=None ):
        """
        """
        info = _auth_types[ auth ]
        folder = info['factory']( *info['args'] )
        if id:
            folder.id = id # XXX _setId is disabled in BasicUserFolder
        self._setObject( folder.getId(), folder, set_owner=0 )
        return self._getOb( folder.getId() )

    def __setattr__( self, name, value ):
        # XXX a hack to prevent subfolders from changing __allow_groups__
        if name == '__allow_groups__':
            return
        ContainerBase.__setattr__(self, name, value)

    #
    # Implementation of BasicUserFolder methods
    #

    def getUserNames( self ):
        return self.__users_source__.getUserNames()

    def getUsers( self ):
        users = self.__users_source__.getUsers()
        self._restoreGroups( users )
        return users

    def getUser( self, name ):
        user = self.__users_source__.getUser( name )
        if user is not None and not hasattr( user, '_usergroups' ):
            self._restoreGroups( [user] )
        return user

    def userFolderAddUser( self, name, password, roles, domains, **kw ):
        """
            API method for creating a new user object.
        """
        if not name:
            raise Exceptions.SimpleError, "A username must be specified."

        if self.getUser(name) or ( self._emergency_user and
                                   name == self._emergency_user.getUserName() ):
            raise Exceptions.SimpleError, "A user with the specified name already exists."

        if domains and not self.domainSpecValidate( domains ):
            raise Exceptions.SimpleError, "Illegal domain specification."

        if not roles:   roles   = []
        if not domains: domains = []

        self._doAddUser( name, password, roles, domains, **kw )

    def _doAddUser( self, name, password, roles, domains, groups=Missing, **kw ):
        """
            Creates a new user.
        """
        # BasicUserFolder does not check already existing user
        if self.getUser( name ):
            raise KeyError, name

        ufolder = self.__users_source__
        gfolder = self.__groups_source__

        if groups is Missing:
            groups = []

        if ufolder == gfolder:
            ufolder._doAddUser( name, password, roles, domains, groups, **kw )

        else:
            ufolder._doAddUser( name, password, roles, domains, **kw )
            self.addGroupsToUser( groups, name )

    def _doChangeUser( self, name, password, roles, domains, groups=Missing, **kw ):
        """
            Modifies an existing user.
        """
        ufolder = self.__users_source__
        gfolder = self.__groups_source__

        if ufolder == gfolder:
            if groups is Missing:
                groups = self.getUserById( name ).getGroups()
            ufolder._doChangeUser( name, password, roles, domains, groups, **kw )

        else:
            # NB the methods order is significant for LDAP group-role mapping
            if groups is not Missing:
                self.setGroupsOfUser( groups, name )
            ufolder._doChangeUser( name, password, roles, domains, **kw )

    def _doDelUsers( self, names ):
        """
            Deletes one or more users.
        """
        ufolder = self.__users_source__

        for username in names:
            user = self.getUser( username )
            if user is not None:
                self.delGroupsFromUser( user.getGroups(), username )

        ufolder._doDelUsers( names )

    def authenticate( self, name, password, request ):
        if not name:
            return None

        user = self.getUser( name )
        if user is None or Roles.Locked in user.getRoles():
            return None

        if self.auth_frontend and request.environ.get('REMOTE_USER'):
            # skip password checking in case frontend authentication is used
            pass

        else:
            user = self.__users_source__.authenticate( name, password, request )
            if user is None:
                return None
            if not hasattr( user, '_usergroups' ):
                self._restoreGroups( [user] )

        if not request.SESSION.get('_LoginTime'):
            tool = getToolByName( self, 'portal_membership' )
            tool.updateLoginTime( user )
            request.SESSION.set('_LoginTime', DateTime())

        return user

    def validate( self, request, auth='', roles=_noroles ):
        # adds support for MS IIS frontend + NTLM authentication
        auth_type = auth and auth.split()[0].lower()
        if not auth_type:
            auth_type = request.environ.get('AUTH_TYPE','').lower()
        use_ntlm  = auth_type in Config.WindowsIntegratedAuth

        if not auth or use_ntlm:
            # try to obtain frontend-authenticated username
            name = request.environ.get('REMOTE_USER') or None
            if name and use_ntlm:
                name = name.split('\\')[-1]   # 'DOMAIN\username'
            # stick non-empty username into the request
            if name:
                auth = 'Basic %s' % encodestring( '%s:%s' % (name,'') )
                request._auth = auth
                request.RESPONSE._auth = True

        return BasicUserFolder.validate( self, request, auth, roles )

    #
    # Implementation of BasicGroupFolderMixin methods
    #

    def getGroupNames( self ):
        """
        """
        groups = ()
        usrc = self.__users_source__
        gsrc = self.__groups_source__

        if gsrc:
            groups = gsrc.getGroupNames()

        if usrc != gsrc \
                and _getAuthInfo( usrc, 'pseudogroups' ) \
                and usrc.enable_pseudogroups:
            groups += usrc.getPseudoGroupNames()

        return groups

    def getGroupById( self, groupname, default=Missing ):
        """
        """
        group = None
        usrc = self.__users_source__
        gsrc = self.__groups_source__

        if gsrc:
            group = gsrc.getGroupById( groupname, None )

        if group is None and usrc != gsrc \
                and _getAuthInfo( usrc, 'pseudogroups' ) \
                and usrc.enable_pseudogroups:
            group = usrc.getPseudoGroupById( groupname, None )

        if group is None:
            if default is Missing:
                raise KeyError, groupname
            return default

        return group.__of__( self )

    def userFolderAddGroup( self, groupname, title='', **kw ):
        """
        """
        if not hasattr( self, '__groups_source__' ):
            raise NotImplementedError, "No groups source defined."

        self.__groups_source__.userFolderAddGroup( groupname, title, **kw )

    def userFolderDelGroups( self, groupnames ):
        """
        """
        if not hasattr( self, '__groups_source__' ):
            return NotImplementedError, "No groups source defined."

        self.__groups_source__.userFolderDelGroups( groupnames )

    def _restoreGroups( self, users ):
        # LDAP user is not persistent object
        # thus its groups must be restored every time
        groups = {}
        for group in self.getGroupNames():
            groups[ group ] = self.getGroupById( group ).getUsers()
        if not groups:
            return

        for user in users:
            if hasattr( user, '_usergroups' ):
                continue
            name = user.getUserName()
            current = list( user.getGroups() )
            for group, members in groups.items():
                if name in members and group not in current:
                    current.append( group )
            user._setGroups( current )

    #
    # ItemBase methods
    #

    def _instance_onCreate( self ):
        if not self.objectIds():
            folder = self.createAuthFolder( _auth_default )
            self.setSourceFolder( id=folder.getId() )

    def _containment_onAdd( self, item, container ):
        BasicUserFolder.manage_afterAdd( self, item, container )

    def _containment_onDelete( self, item, container ):
        BasicUserFolder.manage_beforeDelete( self, item, container )

    #
    # ObjectManager methods
    #

    def _setObject( self, id, object, roles=None, user=None, set_owner=0 ):
        # XXX a hack to enable multiple userfolders inside
        if id == 'acl_users':
            id = cookId( self, prefix=_getAuthType( object, 'acl' ) )
            # XXX _setId is disabled in BasicUserFolder
            object.id = id

        ContainerBase._setObject( self, id, object, roles, user, set_owner )

    def _delObject( self, id ):
        if self.__users_source__.getId() == id:
            del self.__users_source__

        if self.__groups_source__.getId() == id:
            del self.__groups_source__

        ContainerBase._delObject( self, id )

    #
    # LDAP support
    #

    security.declarePrivate( 'getLDAPSettings' )
    def getLDAPSettings( self, id=None ):
        """
        """
        ldap = self.getSourceFolder( 'ldap', None, id=id )
        if ldap is None:
            return None

        info = SimpleRecord()

        servers = ldap.getServers()
        server  = servers and servers[0]
        if server and server['host']:
            info.address = '%s:%s' % (server['host'], server['port'])
        else:
            info.address = ''

        info.login_attr = ldap._login_attr
        info.rdn_attr   = ldap._rdnattr

        info.users_base   = ldap.users_base # list
        info.users_scope  = ldap.users_scope
        info.users_filter = ldap.users_filter
        info.user_classes = ldap._user_objclasses # list

        info.binduid    = ldap._binduid
        info.read_only  = ldap.read_only # bool
        info.encryption = ldap._pwd_encryption # id

        info.encryptions = ldap.getEncryptions()
        info.schema = ldap.getSchemaDict()

        info.groups_base   = ldap.groups_base
        info.groups_scope  = ldap.groups_scope
        info.groups_filter = ldap.groups_filter

        info.enable_pseudogroups = ldap.enable_pseudogroups
        info.pseudogroup_classes = ldap.pseudogroup_classes

        mgroup = lgroup = None
        for name, role in ldap.getGroupMappings():
            if role == Roles.Manager:
                mgroup = name
            elif role == Roles.Locked:
                lgroup = name

        info.groups = []
        info.managers_group = None
        info.locked_group = None

        for id in ldap.getGroupNames():
            group = ldap.getGroupById( id )
            name = group.getGroupName()

            # only groups with non-empty CN can be mapped to roles
            if not name:
                continue

            if name == mgroup:
                info.managers_group = id
            elif name == lgroup:
                info.locked_group = id

            info.groups.append( {
                        'id'    : id,
                        'name'  : name,
                        'title' : group.Title(),
                    } )

        return info

    security.declarePrivate( 'setLDAPSettings' )
    def setLDAPSettings( self, data=None, id=None, **kw ):
        """
        """
        ldap = self.getSourceFolder( 'ldap', None, id=id )
        if ldap is None:
            return

        data = data or SimpleRecord( kw )
        data.updatedefault( self.getLDAPSettings( id=ldap.getId() ) )

        if 'address' in data:
            parts = data.address.split(':')
            host = parts.pop(0)
            port = parts and parts.pop(0) or 389

            if ldap.getServers():
                ldap.manage_deleteServers( [0] )

            ldap.manage_addServer( host, port )

        if 'binduid' in data:
            # usage is an integer, not boolean
            data.binduid_usage = data.binduid and 1 or 0
        else:
            data.binduid_usage = ldap._binduid_usage

        if 'bindpwd' not in data or search( r'^\*+$', data.bindpwd ):
            data.bindpwd = ldap._bindpwd

        roles = ldap._roles
        if Roles.Member not in roles:
            roles.append( Roles.Member )

        ldap.manage_edit(
                ldap.title, data.login_attr, data.users_base,
                data.users_scope, roles, data.groups_base, data.groups_scope,
                data.binduid, data.bindpwd, data.binduid_usage, data.rdn_attr,
                data.user_classes, ldap._local_groups,
                data.encryption, not not data.read_only,
                data.users_filter, data.groups_filter,
                data.enable_pseudogroups, data.pseudogroup_classes
            )

        gmap_add = {}
        gmap_del = []

        if data.managers_group:
            gmap_add[ Roles.Manager ] = data.managers_group
        else:
            gmap_del.append( Roles.Manager )

        if data.locked_group:
            gmap_add[ Roles.Locked ] = data.locked_group
        else:
            gmap_del.append( Roles.Locked )

        if gmap_add:
            for role, group in gmap_add.items():
                group = ldap.getGroupById( group )
                ldap.manage_addGroupMapping( group.getGroupName(), role )

        if gmap_del:
            groups = ldap.getGroupMappings()
            groups = [ name for name, role in groups if role in gmap_del ]
            ldap.manage_deleteGroupMappings( groups )

    security.declarePrivate( 'setLDAPSchemaMapping' )
    def setLDAPSchemaMapping( self, mapping, id=None ):
        """
        """
        ldap = self.getSourceFolder( 'ldap', None, id=id )
        if ldap is None:
            return

        # reverse schema
        rschema = {}
        for key, value in mapping.items():
            if value:
                rschema[ value ] = key

        config = ldap.getSchemaConfig()

        for attr, info in config.items():
            if rschema.get( attr ):
                info['public_name'] = rschema[ attr ]
            else:
                info['public_name'] = ''

        ldap.setSchemaConfig( config )

    security.declarePrivate( 'changeLDAPSchemaAttribute' )
    def changeLDAPSchemaAttribute( self, name, title='', property=None, id=None ):
        """
        """
        ldap = self.getSourceFolder( 'ldap', None, id=id )
        if ldap is None:
            return

        if ldap.getSchemaConfig().has_key( name ):
            ldap.manage_deleteLDAPSchemaItems( [name] )

        ldap.manage_addLDAPSchemaItem( name,
                friendly_name=title, public_name=(property or '') )

    security.declarePrivate( 'getMappedUserProperties' )
    def getMappedUserProperties( self ):
        users = self.__users_source__
        if _getAuthType( users ) == 'ldap':
            return [ a[1] for a in users.getMappedUserAttrs() ]
        return []

    security.declareProtected( ZopePermissions.manage_users, 'setUserProperties' )
    def setUserProperties( self, name, mapping ):
        users = self.__users_source__
        if _getAuthType( users ) == 'ldap' and not users.read_only:
            users.setUserProperties( name, mapping )

    security.declarePrivate( 'invalidateCache' )
    def invalidateCache( self ):
        users = self.__users_source__
        if _getAuthType( users ) == 'ldap':
            users.manage_reinit()

InitializeClass( UserFolder )


def manage_addUserFolder( dispatcher, id=None, REQUEST=None ):
    """
        Adds a User Folder.
    """
    folder = UserFolder()
    dispatcher._setObject( folder.getId(), folder )

    if REQUEST is not None:
        dispatcher.manage_main( dispatcher, REQUEST )


def registerAuthType( id, **info ):
    """
        Registers users and/or groups source type.
    """
    global _auth_types, _auth_default
    if _auth_types.has_key( id ):
        raise ValueError, id

    # apply default options
    info.setdefault( 'id', id )
    info.setdefault( 'args', () )
    info.setdefault( 'users', 1 )
    info.setdefault( 'groups', 1 )
    info.setdefault( 'pseudogroups', 0 )
    info.setdefault( 'detached_groups', 0 )

    # the type will be used for default user folder
    if info.get('default'):
        _auth_default = id

    # add to the types registry
    _auth_types[ id ] = info

# mapping auth_id => auth_info structure
_auth_types = {}
_auth_default = None

def _getAuthInfo( mtype, prop=None, default=Missing ):
    # returns authentication type information by meta type
    if type(mtype) is not StringType:
        mtype = mtype.meta_type

    for info in _auth_types.values():
        if info['meta_type'] == mtype:
            if prop is None:
                return info
            if info.has_key( prop ):
                return info[ prop ]
            break

    if default is Missing:
        raise ValueError, mtype
    return default

def _getAuthType( mtype, default=Missing ):
    # returns authentication type ID by meta type
    return _getAuthInfo( mtype, 'id', default )


# parameters for LDAPUserFolder constructor
_ldap_args = (
        '',                  # title
        'localhost',         # LDAP_server
        'uid',               # login_attr
        '',                  # users_base
        2,                   # users_scope -- subtree
        [Roles.Member],      # roles
        '',                  # groups_base
        2,                   # groups_scope -- subtree
        '',                  # binduid
        '',                  # bindpwd
        0,                   # binduid_usage -- never
        'uid',               # rdn_attr
        0,                   # local_groups -- no
        'clear',             # encryption
        0,                   # use_ssl -- no
        1,                   # read_only -- yes
        Config.LDAPSchema,   # schema
        #'objectClass=inetOrgPerson', # users filter
    )

class UserFolderInstaller:
    def install(self, p):
        p.manage_addProduct['CMFNauTools'].manage_addUserFolder()


def initialize( context ):
    # module initialization callback

    context.register( registerAuthType )

    context.registerInstaller( UserFolderInstaller )

    context.registerClass(
            UserFolder,
            permission = ZopePermissions.add_user_folders,
            constructors = (manage_addUserFolder,),
            #icon = 'UserFolder_icon.gif',
        )

    context.registerAuthType(
            'nux',
            meta_type           = UserFolderWithGroups.meta_type,
            detached_groups     = 1,
            factory             = UserFolderWithGroups,
            default             = 1,
        )

    if Config.UseLDAPUserFolder:
        context.registerAuthType(
                'ldap',
                meta_type       = LDAPUserFolder.meta_type,
                pseudogroups    = 1,
                detached_groups = 0,
                factory         = LDAPUserFolder,
                args            = _ldap_args,
            )
