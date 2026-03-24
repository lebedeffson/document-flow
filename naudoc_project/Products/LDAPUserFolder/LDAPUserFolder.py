#####################################################################
#
# LDAPUserFolder	An LDAP-based user source for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__='$Revision: 1.15 $'[11:-2]

# General python imports
import re, os, urllib
from copy import deepcopy
from time import time
from types import StringType

# Zope imports
from Globals import DTMLFile, package_home, InitializeClass
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from AccessControl.User import BasicUserFolder, domainSpecMatch
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.Permissions import view_management_screens, \
                                      manage_users, \
                                      view
from OFS.SimpleItem import SimpleItem
from BTrees.OOBTree import OOBTree

# LDAPUserFolder package imports
from LDAPUser import LDAPUser
from LDAPGroup import LDAPGroup, LDAPPseudoGroup
from LDAPDelegate import LDAPDelegate, explode_dn
from LDAPDelegate import ADD, DELETE, REPLACE, BASE
from SimpleLog import SimpleLog
from SimpleCache import getSimpleCache
from utils import _createLDAPPassword, crypt
from utils import ldap_scopes, GROUP_MEMBER_MAP, from_utf8, to_utf8

_marker = []
_dtmldir = os.path.join(package_home(globals()), 'dtml')
addLDAPUserFolderForm = DTMLFile('addLDAPUserFolder', _dtmldir)
EDIT_PERMISSION = 'Change user folder'

DEFAULT_FILTER = 'objectClass=*'
DEFAULT_TIMEOUT = 600

DEFAULT_SCHEMA = {
        'cn' : { 'ldap_name'     : 'cn',
                 'friendly_name' : 'Canonical Name',
                 'public_name'   : '',
                 'multivalued'   : '',
               },
        'sn' : { 'ldap_name'     : 'sn',
                 'friendly_name' : 'Last Name',
                 'public_name'   : '',
                 'multivalued'   : '',
               },
    }


class LDAPUserFolder(BasicUserFolder):
    """
        LDAPUserFolder

        The LDAPUserFolder is a user database.  It contains management
        hooks so that it can be added to a Zope folder as an 'acl_users'
        database.  Its important public method is validate() which
        returns a Zope user object of type LDAPUser
    """
    security = ClassSecurityInfo()

    meta_type = 'LDAPUserFolder'
    id = 'acl_users'
    isAUserFolder = 1

    # Make sure we always have the verbose attribute, otherwise logs break
    verbose = 2

    users_filter = ''
    groups_filter = ''
    enable_pseudogroups = 0
    pseudogroup_classes = ()

    _v_userlist_expire = 0
    _v_grouplist_expire = 0
    _v_pseudogrouplist_expire = 0

    #################################################################
    #
    # Setting up all ZMI management screens and default login pages
    #
    #################################################################

    manage_options=(
        (
        {'label' : 'Configure',	'action' : 'manage_main',
         'help'  : ('LDAPUserFolder','Configure.stx')},
        {'label' : 'LDAP Schema', 'action' : 'manage_ldapschema',
         'help'  : ('LDAPUserFolder', 'Schema.stx')},
        {'label' : 'Caches', 'action' : 'manage_cache',
         'help'  : ('LDAPUserFolder', 'Caches.stx')},
        {'label' : 'Users', 'action' : 'manage_userrecords',
         'help'  : ('LDAPUserFolder', 'Users.stx')},
        {'label' : 'Groups', 'action' : 'manage_grouprecords',
         'help' : ('LDAPUserFolder', 'Groups.stx')},
        {'label' : 'Log', 'action' : 'manage_log',
         'help'  : ('LDAPUserFolder', 'Log.stx')},
        )
        + SimpleItem.manage_options
        )

    security.declareProtected(view_management_screens, 'manage')
    security.declareProtected(view_management_screens, 'manage_main')
    manage = manage_main = DTMLFile('dtml/properties', globals())
    manage_main._setName('manage_main')

    security.declareProtected(view_management_screens, 'manage_ldapschema')
    manage_ldapschema = DTMLFile('dtml/ldapschema', globals())

    security.declareProtected(view_management_screens, 'manage_log')
    manage_log = DTMLFile('dtml/log', globals())

    security.declareProtected(view_management_screens, 'manage_cache')
    manage_cache = DTMLFile('dtml/cache', globals())

    security.declareProtected(view_management_screens, 'manage_userrecords')
    manage_userrecords = DTMLFile('dtml/users', globals())

    security.declareProtected(view_management_screens, 'manage_grouprecords')
    manage_grouprecords = DTMLFile('dtml/groups', globals())


    #################################################################
    #
    # Initialization code
    #
    #################################################################


    def __setstate__(self, v):
        """
            __setstate__ is called whenever the instance is loaded
            from the ZODB, like when Zope is restarted.
        """
        # Call inherited __setstate__ methods if they exist
        LDAPUserFolder.inheritedAttribute('__setstate__')(self, v)

        # Reset log
        self._log = SimpleLog()

        # Configure user and group caches
        for cache_type in ['anonymous', 'authenticated', 'group']:
            timeout = self.getCacheTimeout( cache_type )
            self._getCache( cache_type ).setTimeout( timeout )

        if self.verbose > 2:
            self._log.log(3, 'LDAPUserFolder reinitialized by __setstate__')


    def __init__( self, title, LDAP_server, login_attr, users_base
                , users_scope, roles , groups_base, groups_scope
                , binduid, bindpwd, binduid_usage, rdn_attr
                , local_groups=0, encryption='SHA'
                , use_ssl=0, read_only=0, schema=None, REQUEST=None
                ):
        """ Create a new LDAPUserFolder instance """
        self.verbose = 2    # _log needs it
        self._log = SimpleLog()
        self._delegate = LDAPDelegate()
        self._ldapschema = deepcopy( schema or DEFAULT_SCHEMA )

        # Local DN to role tree for storing roles
        self._groups_store = OOBTree()
        # List of additionally known roles
        self._additional_groups = []
        # Place to store mappings from LDAP group to Zope role
        self._groups_mappings = {}

        # Caching-related
        for cache_type in ['anonymous', 'authenticated', 'group']:
            self._getCache( cache_type ).clear()
            self.setCacheTimeout( cache_type, DEFAULT_TIMEOUT )

        if LDAP_server.find(':') != -1:
            self.LDAP_server = LDAP_server.split(':')[0].strip()
            self.LDAP_port = int(LDAP_server.split(':')[1])
        else:
            if use_ssl:
                self.LDAP_port = 636
            else:
                self.LDAP_port = 389

            self.LDAP_server = LDAP_server.strip()

        if not not use_ssl:
            self._conn_proto = 'ldaps'
        else:
            self._conn_proto = 'ldap'

        self._delegate.addServer( self.LDAP_server
                                , self.LDAP_port
                                , use_ssl
                                )

        self.manage_edit( title, login_attr, users_base, users_scope
                        , roles, groups_base, groups_scope, binduid
                        , bindpwd, binduid_usage, rdn_attr, 'top,person'
                        , local_groups, encryption, read_only
                        )


    security.declarePrivate('_lookupuser')
    def _lookupuser(self, uid, pwd=None):
        """
            returns a unique RID and the groups a uid belongs to
            as well as a dictionary containing user attributes
        """
        search_str = '(%s)' % (self.users_filter or DEFAULT_FILTER)

        if self._login_attr == 'dn':
            users_base = to_utf8(uid)
        else:
            users_base = self.users_base
            search_str = '(&(%s=%s)%s)' % (self._login_attr, uid, search_str)

        # Step 1: Bind either as the Manager or anonymously to look
        #         us the user from the login given
        if self._binduid_usage > 0:
            bind_dn = self._binduid
            bind_pwd = self._bindpwd
        else:
            bind_dn = bind_pwd = ''

        if self.verbose > 8:
            msg = '_lookupuser: Binding as "%s:%s"' % (bind_dn, bind_pwd)
            self._log.log(9, msg)

        known_attrs = self.getSchemaConfig().keys()

        res = self._delegate.search( base=users_base
                                   , scope=self.users_scope
                                   , filter=search_str
                                   , attrs=known_attrs
                                   , bind_dn=bind_dn
                                   , bind_pwd=bind_pwd
                                   )

        if res['size'] == 0 or res['exception']:
            msg = '_lookupuser: No user "%s" (%s)' % (uid, res['exception'])
            self.verbose > 3 and self._log.log(4, msg)
            return None, None, None

        user_attrs = res['results'][0]
        dn = user_attrs.get('dn')

        # Step 2: Re-bind using the password that was passed in and the DN we
        #         looked up in Step 1. This will catch bad passwords. If no
        #         password was handed in we bind according to the rules
        #         configured with the Manager DN usage property.
        if pwd is not None and self._binduid_usage != 1:
            user_dn = dn
            user_pwd = pwd
        elif self._binduid_usage == 1:
            user_dn = self._binduid
            user_pwd = self._bindpwd

            # Even though I am now going to use the Manager DN and password
            # to do the "final" lookup I *must* ensure that the password, if
            # one was specified, is not a bad password. Since LDAP passwords
            # are one-way encoded I must ask the LDAP server itself to verify
            # the password, I cannot do it myself.
            if pwd is not None:
                try:
                    self._delegate.connect(bind_dn=to_utf8(dn), bind_pwd=pwd)
                except:
                    # Something went wrong, most likely bad credentials
                    msg = '_lookupuser: Binding as "%s:%s" fails' % (dn, pwd)
                    self.verbose > 3 and self._log.log(4, msg)
                    return None, None, None

        else:
            user_dn = user_pwd = ''

        if self.verbose > 8:
            msg = '_lookupuser: Re-binding as "%s:%s"' % (user_dn, user_pwd)
            self._log.log(9, msg)

        auth_res = self._delegate.search( base=to_utf8(dn)
                                        , scope=BASE
                                        , attrs=known_attrs
                                        , bind_dn=user_dn
                                        , bind_pwd=user_pwd
                                        )

        if auth_res['size'] == 0 or auth_res['exception']:
            msg = '_lookupuser: "%s" lookup fails bound as "%s"' % (dn, dn)
            self.verbose > 3 and self._log.log(4, msg)
            return None, None, None

        user_attrs = auth_res['results'][0]

        self.verbose > 4 and self._log.log(5,
             '_lookupUser: user_attrs = %s' % str(user_attrs))

        groups = list(self.getGroups(dn=dn, attr='cn', pwd=user_pwd))
        roles = self._mapRoles(groups)
        roles.extend(self._roles)

        return roles, dn, user_attrs


    security.declareProtected(manage_users, 'manage_reinit')
    def manage_reinit(self, REQUEST=None):
        """ re-initialize and clear out users and log """
        self._clearCaches()
        self._v_conn = None
        self.verbose > 2 and self._log.log(3, 'Cleared caches on Caches tab')

        if REQUEST:
            msg = 'User caches cleared'
            return self.manage_cache(manage_tabs_message=msg)


    #################################################################
    #
    # Configuration of the user folder
    #
    #################################################################


    security.declareProtected(view_management_screens, 'getProperty')
    def getProperty(self, prop_name, default=''):
        """ Get at LDAPUserManager properties """
        return getattr(self, prop_name, default)


    security.declarePrivate('_setProperty')
    def _setProperty(self, prop_name, prop_value):
        """ Set a property on the LDAP User Folder object """
        if not hasattr(self, prop_name):
            msg = 'No property "%s" on the LDAP User Folder' % prop_name
            raise AttributeError, msg

        setattr(self, prop_name, prop_value)


    security.declareProtected(EDIT_PERMISSION, 'manage_changeProperty')
    def manage_changeProperty( self
                             , prop_name
                             , prop_value
                             , client_form='manage_main'
                             , REQUEST=None
                             ):
        """ The public front end for changing single properties """
        try:
            self._setProperty(prop_name, prop_value)
            self._clearCaches()
            msg = 'Attribute "%s" changed.' % prop_name
        except AttributeError, e:
            msg = e.args[0]

        if REQUEST is not None:
            form = getattr(self, client_form)
            return form(manage_tabs_message=msg)


    security.declareProtected(EDIT_PERMISSION, 'manage_edit')
    def manage_edit( self, title, login_attr, users_base
                   , users_scope, roles,  groups_base, groups_scope
                   , binduid, bindpwd, binduid_usage=1, rdn_attr='cn'
                   , obj_classes='top,person', local_groups=0
                   , encryption='SHA', read_only=0
                   , users_filter='', groups_filter=''
                   , enable_pseudogroups=0, pseudogroup_classes=()
                   , REQUEST=None
                   ):
        """ Edit the LDAPUserFolder Object """
        if not binduid:
            binduid_usage = 0

        if isinstance( users_base, StringType ):
            users_base = re.split(r';\s*', users_base)

        #groups_base = re.split(r';\s*', groups_base) TODO
        groups_base = groups_base or users_base[0]

        self.title = title
        self.read_only = not not read_only

        self.users_base = users_base
        self.users_scope = users_scope
        self.users_filter = users_filter

        self.groups_base = groups_base or users_base
        self.groups_scope = groups_scope or users_scope
        self.groups_filter = groups_filter

        self.enable_pseudogroups = not not enable_pseudogroups
        if isinstance( pseudogroup_classes, StringType ):
            pseudogroup_classes = [ x.strip() for x in pseudogroup_classes.split(',') ]
        self.pseudogroup_classes = pseudogroup_classes

        self._delegate.edit( login_attr, users_base[0], rdn_attr
                           , obj_classes, binduid, bindpwd
                           , binduid_usage, read_only
                           )

        if isinstance(roles, StringType):
            roles = roles and [x.strip() for x in roles.split(',')] or []
        self._roles = roles

        self._binduid = binduid
        self._bindpwd = bindpwd
        self._binduid_usage = int(binduid_usage)

        self._local_groups = not not local_groups

        if encryption == 'crypt' and crypt is None:
            encryption = 'SHA'

        self._pwd_encryption = encryption

        if isinstance(obj_classes, StringType):
            obj_classes = [x.strip() for x in obj_classes.split(',')]
        self._user_objclasses = obj_classes

        my_attrs = self.getSchemaConfig().keys()

        if rdn_attr not in my_attrs:
            self.manage_addLDAPSchemaItem( ldap_name=rdn_attr
                                         , friendly_name=rdn_attr
                                         )
        self._rdnattr = rdn_attr

        if login_attr not in my_attrs:
            self.manage_addLDAPSchemaItem( ldap_name=login_attr
                                         , friendly_name=login_attr
                                         )
        self._login_attr = login_attr

        self._clearCaches()
        self.verbose > 1 and self._log.log(2, 'Properties changed')
        msg = 'Properties changed'

        try:
            connection = self._delegate.connect()
        except:
            msg = 'Cannot+connect+to+LDAP+server'

        if REQUEST:
            return self.manage_main(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'manage_addServer')
    def manage_addServer(self, host, port='389', use_ssl=0, REQUEST=None):
        """ Add a new server to the list of servers in use """
        self._delegate.addServer(host, port, use_ssl)
        msg = 'Server at %s:%s added' % (host, port)

        if REQUEST:
            return self.manage_main(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'getServers')
    def getServers(self):
        """ Proxy method used for the ZMI """
        return tuple(self._delegate.getServers())


    security.declareProtected(manage_users, 'manage_deleteServers')
    def manage_deleteServers(self, position_list=[], REQUEST=None):
        """ Delete servers from the list of servers in use """
        if len(position_list) == 0:
            msg = 'No servers selected'
        else:
            self._delegate.deleteServers(position_list)
            msg = 'Servers deleted'

        if REQUEST:
            return self.manage_main(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'getUsers')
    def getUsers(self, authenticated=1):
        """Return a list of *cached* user objects"""
        if authenticated:
            return self._getCache('authenticated').getCache()
        else:
            return self._getCache('anonymous').getCache()


    security.declareProtected(manage_users, 'getUserNames')
    def getUserNames(self):
        """ Return a list of usernames """
        now = time()
        if self._v_userlist_expire > now:
            return self._v_userlist

        s = {}
        lscope = ldap_scopes[self.users_scope]
        login_attr = self._login_attr

        if login_attr == 'dn':
            wanted_attrs = []
        else:
            wanted_attrs = [login_attr]

        search_str = '(%s)' % (self.users_filter or DEFAULT_FILTER)

        res = self._delegate.search( base=self.users_base
                                   , scope=self.users_scope
                                   , filter=search_str
                                   , attrs=wanted_attrs
                                   )

        if res['size'] == 0 or res['exception']:
            msg = 'getUserNames: Cannot find any users (%s)' % res['exception']
            self._log.log(2, msg)

            return []

        result_dicts = res['results']
        for i in range(res['size']):
            if login_attr != 'dn':
                name_list = result_dicts[i].get(login_attr, [])
            else:
                name_list = result_dicts[i].get(login_attr)

            for name in name_list:
                s[name] = None

        self._v_userlist = s.keys()
        self._v_userlist.sort()
        self._v_userlist_expire = now + self.getCacheTimeout('userlist')

        return self._v_userlist


    security.declareProtected(manage_users, 'getUser')
    def getUser(self, name, pwd=None):
        """Return the named user object or None"""
        if pwd is not None:
            cache_type = 'authenticated'
            cached_user = self._getCache('authenticated').get(name, pwd)
        else:
            cache_type = 'anonymous'
            cached_user = self._getCache('anonymous').get(name)

        if cached_user:
            if self.verbose > 6:
                msg = 'getUser: "%s" cached in %s cache' % (name, cache_type)
                self._log.log(7, msg)
            return cached_user

        now = time()
        if self._v_userlist_expire > now and name not in self._v_userlist:
            return None

        user_roles, user_dn, user_attrs = self._lookupuser(uid=name, pwd=pwd)
        if user_dn is None:
            msg = 'getUser: "%s" not found' % name
            self.verbose > 3 and self._log.log(4, msg)
            return None

        if user_attrs is None:
            msg = 'getUser: "%s" has no properties, bailing' % name
            self.verbose > 3 and self._log.log(4, msg)
            return None

        if user_roles is None or user_roles == self._roles:
            msg = 'getUser: "%s" only has roles %s' % (name, str(user_roles))
            self.verbose > 8 and self._log.log(9, msg)

        user_obj = LDAPUser( user_attrs.get(self._login_attr)[0]
                           , pwd or 'undef'
                           , user_roles or []
                           , []
                           , user_dn
                           , user_attrs
                           , self.getMappedUserAttrs()
                           , self.getMultivaluedUserAttrs()
                           )

        if not self._local_groups:
            # restore groups on the user object
            groups = self.getGroups( dn=user_dn, attr='dn' )
            if self.enable_pseudogroups:
                parts = user_dn.split(',')
                for i in range( 1, len(parts) ):
                    group = self.getPseudoGroupById( ','.join(parts[ -i: ]), None )
                    if group is not None:
                        groups.append( group.getId() )
            user_obj._setGroups( groups )

        return self._getCache( cache_type ).set( name, user_obj )


    security.declareProtected(manage_users, 'getUserById')
    def getUserById(self, id, default=_marker):
        """ Return a user object by ID (in this case by username) """
        try:
            return self.getUser(id)

        except:
            if default is _marker:
                raise

            return default


    def getUserByDN(self, user_dn):
        """ Make a user object from a DN """
        search_str = '(%s)' % (self.users_filter or DEFAULT_FILTER)

        res = self._delegate.search( base=user_dn
                                   , scope=BASE
                                   , filter=search_str
                                   , attrs=[self._login_attr]
                                   )

        if res['exception'] or res['size'] == 0:
            return None

        if self._login_attr == 'dn':
            user_id = to_utf8(res['results'][0].get(self._login_attr))
        else:
            user_id = res['results'][0].get(self._login_attr)[0]

        user_obj = self.getUser(user_id)

        return user_obj


    def authenticate(self, name, password, request):
        super = self._emergency_user

        if name is None:
            return None

        if super and name == super.getUserName():
            user = super
        else:
            user = self.getUser(name, password)

        if user is not None:
            domains = user.getDomains()
            if domains:
                return (domainSpecMatch(domains, request) and user) or None

        return user


    #################################################################
    #
    # Implementation of BasicUserFolder internal interface
    #
    #################################################################


    def _doAddUser( self, name, password, roles, domains, groups=_marker, **kw ):
        """ Create a new user """
        kw[ self._rdnattr ] = name
        kw['cn'] = kw['sn'] = name
        kw['user_pw'] = kw['confirm_pw'] = password

        if not self._local_groups and groups:
            for gid in groups:
                group = self.getGroup(gid)
                if group.isUsersStorage():
                    if kw.has_key('parent_dn'):
                        raise ValueError, "Only one parent DN may be given."
                    kw['parent_dn'] = group.getGroupDN()

        msg = self.manage_addUser( kwargs=kw )
        if msg:
            raise RuntimeError, msg

        self._setRolesAndGroups( name, roles, groups )

        # this is required if stored password is encrypted
        # and must be mailed to the user after registration
        user = self.getUser( name )
        user.__ = password


    def _doChangeUser( self, name, password, roles, domains, groups=_marker, **kw ):
        """ Modify an existing user """
        user = self.getUser( name )

        if password is not None:
            msg = self.manage_editUserPassword( user.getUserDN(), password )
            if msg:
                raise RuntimeError, msg

        # TODO set domains

        self._setRolesAndGroups( name, roles, groups )


    def _doDelUsers( self, names ):
        """ Delete one or more users """
        user_dns = []
        for name in names:
            user = self.getUser( name )
            if user is None:
                raise KeyError, name
            user_dns.append( user.getUserDN() )

        self.manage_deleteUsers( user_dns )


    def _setRolesAndGroups( self, name, roles=(), groups=_marker ):
        """ Set roles and groups for the user """
        user   = self.getUser( name )
        local  = self._local_groups
        droles = self._roles
        oroles = user.getRoles()

        mapping = {}
        for cn, role in self.getGroupMappings():
            mapping[ cn ] = role

        new = []
        old = list( user.getGroups() )
        if groups is _marker:
            groups = old

        # merge real groups and groups mapped through roles
        for cn, dn in self.getGroups():
            role = mapping.get( cn, local and cn or None )
            if not role:
                # no mapping exists -- an ordinary group
                if dn in groups:
                    new.append( dn )
                continue
            if role in droles:
                # role is default role -- skip it
                continue
            # found group-to-role mapping
            if role in oroles:
                old.append( dn )
            if role in roles:
                new.append( dn )

        old.sort()
        new.sort()
        if new == old:
            return

        if local:
            self.manage_editUserRoles( user.getUserDN(), new )
        else:
            self.setGroupsOfUser( new, name )


    #################################################################
    #
    # Implementation of UserFolderWithGroups interface
    #
    #################################################################


    def getGroupNames( self ):
        """ Return a list of group names """
        if self._local_groups:
            return []

        now = time()
        if self._v_grouplist_expire > now:
            return self._v_grouplist

        groups = [ g[1] for g in self.getGroups() ]

        if self.enable_pseudogroups:
            groups.extend( self.getPseudoGroupNames() )

        self._v_grouplist = groups = tuple( groups )
        self._v_grouplist_expire = now + self.getCacheTimeout('grouplist')

        return groups


    def getGroupById( self, groupname, default=_marker ):
        """ Return the given group """
        if self._local_groups:
            raise KeyError, groupname

        if '=' not in groupname:
            groupname = 'cn=%s,%s' % (groupname, self.groups_base)

        group = self._getCache( 'group' ).get( groupname )
        if group is not None:
            if self.verbose > 6:
                self._log.log( 7, "getGroupById: \"%s\" cached" % groupname )
            return group.__of__( self )

        classes = GROUP_MEMBER_MAP.keys()
        group_filter = '(|%s)' % ''.join([ '(objectClass=%s)' % x for x in classes ])

        if self.groups_filter:
            group_filter = '(&%s(%s))' % (group_filter, self.groups_filter or DEFAULT_FILTER)

        res = self._delegate.search( base=to_utf8(groupname), scope=BASE, filter=group_filter )

        if not res['exception'] and res['size'] == 1:
            group = LDAPGroup( groupname, record=res['results'][0], read_only=self.read_only )
            group = self._getCache( 'group' ).set( groupname, group )
            return group.__of__( self )

        if self.enable_pseudogroups:
            try: return self.getPseudoGroupById( groupname )
            except KeyError: pass

        exc = res['exception'] or (res['size'] and "invalid result" or "empty result")
        self._log.log( 3, "getGroupById: No group \"%s\" (%s)" % (groupname, exc) )

        if default is _marker:
            raise KeyError, groupname
        return default


    def getPseudoGroupNames( self ):
        """ Return a list of pseudogroup names """
        if not self.pseudogroup_classes:
            return ()

        now = time()
        if self._v_pseudogrouplist_expire > now:
            return self._v_pseudogrouplist

        search_str = '(|%s)' % ''.join([ '(objectClass=%s)' % c for c in self.pseudogroup_classes ])

        res = self._delegate.search( base=self.users_base,
                   scope=self.users_scope, filter=search_str )

        if res['size'] == 0 or res['exception']:
            self._log.log( 2, "getPseudoGroupNames: Cannot find any pseudogroups (%s)" % res['exception'] )
            return ()

        groups = [ r['dn'] for r in res['results'] ]
        groups.sort()

        self._v_pseudogrouplist = groups = tuple( groups )
        self._v_pseudogrouplist_expire = now + self.getCacheTimeout('pseudogrouplist')

        return groups


    def getPseudoGroupById( self, groupname, default=_marker ):
        """ Return the given pseudogroup """
        if not self.pseudogroup_classes:
            if default is _marker:
                raise KeyError, groupname
            return default

        group = self._getCache( 'group' ).get( groupname )
        if group is not None:
            if self.verbose > 6:
                self._log.log( 7, "getPseudoGroupById: \"%s\" cached" % groupname )
            return group.__of__( self )

        search_str = '(|%s)' % ''.join([ '(objectClass=%s)' % c for c in self.pseudogroup_classes ])

        res = self._delegate.search( base=groupname, scope=BASE, filter=search_str )

        if res['exception'] or res['size'] != 1:
            exc = res['exception'] or (res['size'] and "invalid result" or "empty result")
            self._log.log( 2, "getPseudoGroupById: No pseudogroup \"%s\" (%s)" % (groupname, exc) )
            if default is _marker:
                raise KeyError, groupname
            return default

        group = LDAPPseudoGroup( groupname, record=res['results'][0] )
        group = self._getCache( 'group' ).set( groupname, group )

        return group.__of__( self )


    security.declareProtected( manage_users, 'userFolderAddGroup' )
    def userFolderAddGroup( self, groupname, title='', **kw ):
        """ Create a new group """
        self.manage_addGroup( groupname, description=title, **kw )


    security.declareProtected( manage_users, 'userFolderDelGroups' )
    def userFolderDelGroups( self, groupnames ):
        """ Delete one or more groups """
        # XXX assumes that group ID == DN
        self.manage_deleteGroups( groupnames )


    #################################################################
    #
    # Stuff formerly in LDAPShared.py
    #
    #################################################################


    security.declareProtected(manage_users, 'getUserDetails')
    def getUserDetails(self, encoded_dn, format=None, attrs=[]):
        """ Return all attributes for a given DN """
        dn = urllib.unquote(encoded_dn)
        search_str = '(%s)' % (self.users_filter or DEFAULT_FILTER)

        res = self._delegate.search( base=to_utf8(dn)
                                   , scope=self.users_scope
                                   , filter=search_str
                                   , attrs=attrs
                                   )

        if res['exception']:
            if format == None:
                result = ((res['exception'], res),)
            elif format == 'dictionary':
                result = { 'cn': '###Error: %s' % res['exception'] }
        elif res['size'] > 0:
            value_dict = res['results'][0]

            if format == None:
                result = value_dict.items()
                result.sort()
            elif format == 'dictionary':
                result = value_dict
        else:
            if format == None:
                result = ()
            elif format == 'dictionary':
                result = {}

        return result


    security.declareProtected(manage_users, 'getGroupDetails')
    def getGroupDetails(self, encoded_cn):
        """ Return all group details """
        result = ()
        cn = urllib.unquote(encoded_cn)
        search_str = '(&(cn=%s)(%s))' % (cn, self.groups_filter or DEFAULT_FILTER)

        if not self._local_groups:
            res = self._delegate.search( base=self.groups_base
                                       , scope=self.groups_scope
                                       , filter=search_str
                                       , attrs=['uniqueMember', 'member']
                                       )

            if res['exception']:
                exc = res['exception']
                msg = 'getGroupDetails: No group "%s" (%s)' % (cn, exc)
                self._log.log(3, msg)
                result = (('Exception', exc),)

            elif res['size'] > 0:
                result = res['results'][0].items()
                result.sort()

            else:
                msg = 'getGroupDetails: No group "%s"' % cn
                self._log.log(3, msg)

        else:
            g_dn = ''
            all_groups = self.getGroups()
            for group_cn, group_dn in all_groups:
                if group_cn == cn:
                    g_dn = group_dn
                    break

            if g_dn:
                users = []

                for user_dn, role_dns in self._groups_store.items():
                    if g_dn in role_dns:
                        users.append(user_dn)

                result = [('', users)]

        return result


    security.declareProtected(manage_users, 'getGroupedUsers')
    def getGroupedUsers(self, groups=None):
        """ Return all those users that are in a group """
        all_dns = {}
        users = []
        member_attrs = GROUP_MEMBER_MAP.values()

        if groups is None:
            groups = self.getGroups()

        for group_id, group_dn in groups:
            group_details = self.getGroupDetails(group_id)
            for key, vals in group_details:
                if key in member_attrs:
                    for dn in vals:
                        all_dns[dn] = 1

        for dn in all_dns.keys():
            try:
                user = self.getUserByDN(to_utf8(dn))
            except:
                user = None

            if user is not None:
                users.append(user.__of__(self))

        return tuple(users)


    security.declareProtected(manage_users, 'getLocalUsers')
    def getLocalUsers(self):
        """ Return all those users who are in locally stored groups """
        local_users = []

        for user_dn, user_roles in self._groups_store.items():
            local_users.append((user_dn, user_roles))

        return tuple(local_users)


    security.declareProtected(manage_users, 'findUser')
    def findUser(self, search_param, search_term, attrs=[]):
        """ Look up matching user records based on attributes """
        lscope = ldap_scopes[self.users_scope]
        users  = []
        search_str = '(%s)' % (self.users_filter or DEFAULT_FILTER)

        if search_param == 'dn':
            users_base = search_term
        else:
            users_base = self.users_base
            search_term = search_term and search_term or '*' # '*%s*' does not compatible with AD
            search_str = '(&(%s=%s)%s)' % (search_param, search_term, search_str)

        res = self._delegate.search( base=users_base
                                   , scope=self.users_scope
                                   , filter=search_str
                                   , attrs=attrs
                                   )

        if res['exception']:
            msg = 'findUser Exception (%s)' % res['exception']
            self.verbose > 1 and self._log.log(2, msg)
            users = [{ 'dn' : res['exception']
                     , 'cn' : 'n/a'
                     , 'sn' : 'Error'
                     }]

        elif res['size'] > 0:
            res_dicts = res['results']
            for i in range(res['size']):
                dn = res_dicts[i].get('dn')
                rec_dict = {}
                rec_dict['sn'] = rec_dict['cn'] = ''

                for key, val in res_dicts[i].items():
                    rec_dict[key] = val[0]

                rec_dict['dn'] = dn

                users.append(rec_dict)

        return users


    security.declareProtected(manage_users, 'getGroups')
    def getGroups(self, dn='*', attr=None, pwd=''):
        """
            returns a list of possible groups from the ldap tree
            (Used e.g. in showgroups.dtml) or, if a DN is passed
            in, all groups for that particular DN.
        """
        group_list = []
        no_show = ('Anonymous', 'Authenticated', 'Shared')

        if self._local_groups:
            if dn != '*':
                all_groups_list = self._groups_store.get(dn) or []
            else:
                all_groups_dict = {}
                zope_roles = list(self.valid_roles())
                zope_roles.extend(list(self._additional_groups))

                for role_name in zope_roles:
                    if role_name not in no_show:
                        all_groups_dict[role_name] = 1

                all_groups_list = all_groups_dict.keys()

            for group in all_groups_list:
                if attr is None:
                    group_list.append((group, group))
                else:
                    group_list.append(group)

            group_list.sort()

        else:
            gscope = ldap_scopes[self.groups_scope]

            if dn != '*':
                f_template = '(&(objectClass=%s)(%s=%s))'
                group_filter = '(|'

                for g_name, m_name in GROUP_MEMBER_MAP.items():
                    group_filter += f_template % (g_name, m_name, dn)

                group_filter += ')'

            else:
                group_filter = '(|'

                for g_name in GROUP_MEMBER_MAP.keys():
                    group_filter += '(objectClass=%s)' % g_name

                group_filter += ')'

            if self.groups_filter:
                group_filter = '(&%s(%s))' % (group_filter, self.groups_filter or DEFAULT_FILTER)

            res = self._delegate.search( base=self.groups_base
                                       , scope=gscope
                                       , filter=group_filter
                                       , attrs=['cn']
                                       , bind_dn=''
                                       , bind_pwd=''
                                       )

            if res['exception']:
                if self.verbose > 1:
                    self._log.log( 2, "getGroups: Search failed (%s)" % res['exception'] )
                return group_list

            elif res['size'] > 0:
                res_dicts = res['results']
                for i in range(res['size']):
                    dn = res_dicts[i].get('dn')
                    try:
                        cn = res_dicts[i]['cn'][0]
                    except KeyError:    # NDS oddity
                        cn = explode_dn(dn, 1)[0]

                    if attr is None:
                        group_list.append((cn, dn))
                    elif attr == 'cn':
                        group_list.append(cn)
                    elif attr == 'dn':
                        group_list.append(dn)

        return group_list


    security.declareProtected(manage_users, 'getGroupType')
    def getGroupType(self, group_dn):
        """ get the type of group """
        if self._local_groups:
            if group_dn in self._additional_groups:
                group_type = 'Custom Role'
            else:
                group_type = 'Zope Built-in Role'

        else:
            group_type = 'n/a'
            res = self._delegate.search( base=to_utf8(group_dn)
                                       , scope=BASE
                                       , attrs=['objectClass']
                                       )

            if res['exception']:
                msg = 'getGroupType: No group "%s" (%s)' % ( group_dn
                                                           , res['exception']
                                                           )
                self.verbose > 1 and self._log.log(2, msg)

            else:
                groups = GROUP_MEMBER_MAP.keys()
                l_groups = [x.lower() for x in groups]
                g_attrs = res['results'][0]
                group_obclasses = g_attrs.get('objectClass', [])
                group_obclasses.extend(g_attrs.get('objectclass', []))
                g_types = [x for x in group_obclasses if x.lower() in l_groups]

                if len(g_types) > 0:
                    group_type = g_types[0]

        return group_type


    security.declareProtected(manage_users, 'getGroupMappings')
    def getGroupMappings(self):
        """ Return the dictionary that maps LDAP groups map to Zope roles """
        mappings = getattr(self, '_groups_mappings', {})

        return mappings.items()


    security.declareProtected(manage_users, 'manage_addGroupMapping')
    def manage_addGroupMapping(self, group_name, role_name, REQUEST=None):
        """ Map a LDAP group to a Zope role """
        mappings = getattr(self, '_groups_mappings', {})
        mappings[group_name] = role_name

        self._groups_mappings = mappings
        self._clearCaches()
        msg = 'Added LDAP group to Zope role mapping: %s -> %s' % (
                group_name, role_name)

        if REQUEST:
            return self.manage_grouprecords(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'manage_deleteGroupMappings')
    def manage_deleteGroupMappings(self, group_names, REQUEST=None):
        """ Delete mappings from LDAP group to Zope role """
        mappings = getattr(self, '_groups_mappings', {})

        for group_name in group_names:
            if mappings.has_key(group_name):
                del mappings[group_name]

        self._groups_mappings = mappings
        self._clearCaches()
        msg = 'Deleted LDAP group to Zope role mapping for: %s' % (
            ', '.join(group_names))

        if REQUEST:
            return self.manage_grouprecords(manage_tabs_message=msg)


    def _mapRoles(self, groups):
        """ Perform the mapping of LDAP groups to Zope roles """
        mappings = getattr(self, '_groups_mappings', {})
        roles = []

        for group in groups:
            roles.append(group)
            mapped_role = mappings.get(group, None)
            if mapped_role is not None and mapped_role not in roles:
                roles.append(mapped_role)

        return roles


    #################################################################
    #
    # Attribute mapping and LDAP schema support
    #
    #################################################################


    security.declareProtected( manage_users, 'getMappedUserAttrs' )
    def getMappedUserAttrs(self):
        """ Return the mapped user attributes """
        schema = self.getSchemaDict()
        pn = 'public_name'
        ln = 'ldap_name'

        return tuple([(x[ln], x[pn]) for x in schema if x.get(pn, '')])


    security.declareProtected( manage_users, 'getMultivaluedUserAttrs' )
    def getMultivaluedUserAttrs(self):
        """ Return sequence of user attributes that are multi-valued"""
        schema = self.getSchemaDict()
        mv = [x['ldap_name'] for x in schema if x.get('multivalued', '')]

        return tuple(mv)


    security.declareProtected( manage_users, 'setUserProperties' )
    def setUserProperties( self, name, mapping ):
        """ Changes the mapped user attributes """
        user = self.getUser( name )
        if user is None:
            raise KeyError, name

        attrs = {}
        for item in self.getSchemaConfig().values():
            pname = item.get('public_name')
            if pname and mapping.has_key( pname ):
                attrs[ item['ldap_name'] ] = mapping[ pname ]

        if not attrs:
            return

        msg = self.manage_editUser( user.getUserDN(), kwargs=attrs )
        if msg:
            raise RuntimeError, msg


    security.declareProtected(manage_users, 'getLDAPSchema')
    def getLDAPSchema(self):
        """ Retrieve the LDAP schema this product knows about """
        raw_schema = self.getSchemaDict()
        schema = [(x['ldap_name'], x['friendly_name']) for x in raw_schema]
        schema.sort()

        return tuple(schema)


    security.declareProtected(manage_users, 'getSchemaDict')
    def getSchemaDict(self):
        """ Retrieve schema as list of dictionaries """
        all_items = self.getSchemaConfig().values()
        all_items.sort()

        return tuple(all_items)


    security.declareProtected(EDIT_PERMISSION, 'setSchemaConfig')
    def setSchemaConfig(self, schema):
        """ Set the LDAP schema configuration """
        self._ldapschema = schema
        self._clearCaches()


    security.declareProtected(manage_users, 'getSchemaConfig')
    def getSchemaConfig(self):
        """ Retrieve the LDAP schema configuration """
        return self._ldapschema


    security.declareProtected(EDIT_PERMISSION, 'manage_addLDAPSchemaItem')
    def manage_addLDAPSchemaItem( self
                                , ldap_name
                                , friendly_name=''
                                , multivalued=''
                                , public_name=''
                                , REQUEST=None
                                ):
        """ Add a schema item to my list of known schema items """
        schema = self.getSchemaConfig()
        if ldap_name not in schema.keys():
            schema[ldap_name] = { 'ldap_name' : ldap_name
                                , 'friendly_name' : friendly_name
                                , 'public_name' : public_name
                                , 'multivalued' : multivalued
                                }

            self.setSchemaConfig(schema)
            msg = 'LDAP Schema item "%s" added' % ldap_name
        else:
            msg = 'LDAP Schema item "%s" already exists'  % ldap_name

        if REQUEST:
            return self.manage_ldapschema(manage_tabs_message=msg)


    security.declareProtected(EDIT_PERMISSION, 'manage_deleteLDAPSchemaItems')
    def manage_deleteLDAPSchemaItems(self, ldap_names=[], REQUEST=None):
        """ Delete schema items from my list of known schema items """
        if len(ldap_names) < 1:
            msg = 'Please select items to delete'

        else:
            schema = self.getSchemaConfig()
            removed = []

            for ldap_name in ldap_names:
                if ldap_name in schema.keys():
                    removed.append(ldap_name)
                    del schema[ldap_name]

            self.setSchemaConfig(schema)

            rem_str = ', '.join(removed)
            msg = 'LDAP Schema items %s removed.' % rem_str

        if REQUEST:
            return self.manage_ldapschema(manage_tabs_message=msg)


    #################################################################
    #
    # Users and groups manipulations
    #
    #################################################################


    security.declareProtected(manage_users, 'manage_addGroup')
    def manage_addGroup( self
                       , newgroup_name
                       , newgroup_type='groupOfUniqueNames'
                       , REQUEST=None
                       , **kw
                       ):
        """ Add a new group in groups_base """
        if not newgroup_name:
            msg = 'No group name specified'

        elif self._local_groups:
            add_groups = self._additional_groups

            if newgroup_name not in add_groups:
                add_groups.append(newgroup_name)

            self._additional_groups = add_groups
            msg = 'Added new group %s' % (newgroup_name)

        else:
            attributes = kw
            attributes['cn'] = [newgroup_name]
            attributes['objectClass'] = ['top', newgroup_type]

            if self._binduid:
                initial_member = self._binduid
            else:
                user = getSecurityManager().getUser()
                try:
                    initial_member = user.getUserDN()
                except:
                    initial_member = ''

            attributes[GROUP_MEMBER_MAP.get(newgroup_type)] = initial_member

            err_msg = self._delegate.insert( base=self.groups_base
                                           , rdn='cn=%s' % newgroup_name
                                           , attrs=attributes
                                           )

            if not err_msg:
                # group has been added => invalidate groupnames cache
                self._v_grouplist_expire = 0

            msg = err_msg or 'Added new group %s' % (newgroup_name)

        if REQUEST:
            return self.manage_grouprecords(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'manage_addUser')
    def manage_addUser(self, REQUEST=None, kwargs={}):
        """ Add a new user record to LDAP """
        if REQUEST is None:
            source = kwargs
        else:
            source = REQUEST

        base = source.get('parent_dn', self.users_base)
        if not isinstance(base, StringType):
            base = base[0]

        attr_dict = {}
        rdn_attr = self._rdnattr
        attr_dict[rdn_attr] = source.get(rdn_attr)
        rdn = '%s=%s' % (rdn_attr, source.get(rdn_attr))
        sub_loc = source.get('sub_branch', '')
        if sub_loc:
            base = '%s,%s' % (rdn, base)
        password = source.get('user_pw', '')
        confirm  = source.get('confirm_pw', '')

        if password != confirm or password == '':
            msg = 'The password and confirmation do not match!'

        else:
            encrypted_pwd = _createLDAPPassword( password
                                               , self._pwd_encryption
                                               )
            attr_dict['userPassword'] = encrypted_pwd
            attr_dict['objectClass'] = self._user_objclasses

            for attribute, names in self.getSchemaConfig().items():
                attr_val = source.get(attribute, None)

                if attr_val:
                    attr_dict[attribute] = attr_val
                elif names.get('public_name', None):
                    attr_val = source.get(names['public_name'], None)

                    if attr_val:
                        attr_dict[attribute] = attr_val

            msg = self._delegate.insert( base=base
                                       , rdn=rdn
                                       , attrs=attr_dict
                                       )

        if msg:
            if REQUEST:
                return self.manage_userrecords(manage_tabs_message=msg)
            return msg

        # user has been added => invalidate usernames cache
        self._v_userlist_expire = 0

        user_dn = '%s,%s' % (rdn, base)
        user_roles = source.get('user_roles', [])

        try:
            if self._local_groups:
                self._groups_store[user_dn] = user_roles

            elif len(user_roles) > 0:
                group_dns = []

                for role in user_roles:
                    try:
                        exploded = explode_dn(role)
                        elements = len(exploded)
                    except:
                        elements = 1

                    if elements == 1:  # simple string
                        role = 'cn=%s,%s' % ( str(role)
                                            , self.groups_base
                                            )

                    group_dns.append(role)

                self.manage_editUserRoles(user_dn, group_dns)

            msg = 'New user %s added' % user_dn

        except Exception, e:
            msg = str(e)
            user_dn = ''

        if REQUEST:
            return self.manage_userrecords( manage_tabs_message=msg
                                          , user_dn='%s,%s' % (rdn, base)
                                          )


    security.declareProtected(manage_users, 'manage_deleteGroups')
    def manage_deleteGroups(self, dns=[], REQUEST=None):
        """ Delete groups from groups_base """
        if len(dns) < 1:
            msg = 'You did not specify groups to delete!'

        else:
            msg = ''

            if self._local_groups:
                add_groups = self._additional_groups
                for dn in dns:
                    if dn in add_groups:
                        del add_groups[add_groups.index(dn)]

                self._additional_groups = add_groups

            else:
                for dn in dns:
                    msg = self._delegate.delete(dn)
                    if msg:
                        break

            msg = msg or 'Deleted group(s):<br> %s' % '<br>'.join(dns)
            # expire deleted groups and members of these groups
            self._clearCaches()

        if REQUEST:
            return self.manage_grouprecords(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'manage_deleteUsers')
    def manage_deleteUsers(self, dns=[], REQUEST=None):
        """ Delete all users in list dns """
        if len(dns) < 1:
            msg = 'You did not specify users to delete!'

        elif self._delegate.read_only:
            msg = 'Running in read-only mode, deletion is disabled'

        else:
            for dn in dns:
                msg = self._delegate.delete(dn)
                if msg:
                    break

                user_groups = self.getGroups(dn=dn, attr='dn')

                if self._local_groups:
                    if dn in self._groups_store.keys():
                        del self._groups_store[dn]

                    continue

                for group in user_groups:
                    group_type = self.getGroupType(group)
                    member_type = GROUP_MEMBER_MAP.get(group_type)

                    msg = self._delegate.modify( dn=group
                                               , mod_type=DELETE
                                               , attrs={member_type : [dn]}
                                               )

                    if msg:
                        break

            msg = 'Deleted user(s):<br> %s' % '<br>'.join(dns)
            # expire deleted users and groups they were members of
            self._clearCaches()

        if REQUEST:
            return self.manage_userrecords(manage_tabs_message=msg)


    security.declareProtected(manage_users, 'manage_editUserPassword')
    def manage_editUserPassword(self, dn, new_pw, REQUEST=None):
        """ Change a user password """
        hidden = '<input type="hidden" name="user_dn" value="%s">' % (dn)
        err_msg = msg = ''

        if new_pw == '':
            msg = 'The password cannot be empty!'

        else:
            ldap_pw = _createLDAPPassword(new_pw, self._pwd_encryption)
            err_msg = self._delegate.modify( dn=dn
                                           , attrs={'userPassword':[ldap_pw]}
                                           )
            if not err_msg:
                msg = 'Password changed for "%s"' % dn
                user_obj = self.getUserByDN(to_utf8(dn))
                self._expireUser(user_obj)

        if REQUEST:
            return self.manage_userrecords( manage_tabs_message=err_msg or msg
                                          , user_dn=dn
                                          )
        else:
            return err_msg


    security.declareProtected(manage_users, 'manage_editUserRoles')
    def manage_editUserRoles(self, user_dn, role_dns=[], REQUEST=None):
        """ Edit the roles (groups) of a user """
        msg = ''
        all_groups = self.getGroups(attr='dn')
        cur_groups = self.getGroups(dn=user_dn, attr='dn')
        group_dns = []
        for group in role_dns:
            if group.find('=') == -1:
                group_dns.append('cn=%s,%s' % (group, self.groups_base))
            else:
                group_dns.append(group)

        if self._local_groups:
            if len(role_dns) == 0:
                del self._groups_store[user_dn]
            else:
                self._groups_store[user_dn] = role_dns

        else:
            for group in all_groups:
                if group in cur_groups and group not in group_dns:
                    cmd = DELETE
                elif group not in cur_groups and group in group_dns:
                    cmd = ADD
                else:
                    continue

                member_attr = GROUP_MEMBER_MAP.get(self.getGroupType(group))

                err_msg = self._delegate.modify( group
                                               , cmd
                                               , {member_attr : [user_dn]}
                                               )
                if err_msg:
                    if msg: msg += "\n"
                    msg += err_msg

                self._expireGroup(group)

        user_obj = self.getUserByDN(to_utf8(user_dn))
        if user_obj is not None:
            self._expireUser(user_obj)

        if REQUEST:
            msg = msg or 'Roles changed for %s' % (user_dn)
            return self.manage_userrecords( manage_tabs_message=msg
                                          , user_dn=user_dn
                                          )
        else:
            return msg


    security.declareProtected(manage_users, 'manage_setUserProperty')
    def manage_setUserProperty(self, user_dn, prop_name, prop_value):
        """ Set a new attribute on the user record """
        if isinstance(prop_value, StringType):
            prop_value = [x.strip() for x in prop_value.split(';')]

        cur_rec = self._delegate.search( base=user_dn
                                       , scope=BASE
                                       )

        if cur_rec['exception'] or cur_rec['size'] == 0:
            exc = cur_rec['exception']
            msg = 'manage_setUserProperty: No user "%s" (%s)' % (user_dn, exc)
            self.verbose > 1 and self._log.log(2, msg)

            return

        user_rec = cur_rec['results'][0]
        cur_prop = user_rec.get(prop_name, [''])

        if cur_prop != prop_value:
            if prop_value != ['']:
                mod = REPLACE
            else:
                mod = DELETE

            err_msg = self._delegate.modify( dn=user_dn
                                           , mod_type=mod
                                           , attrs={prop_name:prop_value}
                                           )

            if not err_msg:
                user_obj = self.getUserByDN(to_utf8(user_dn))
                self._expireUser(user_obj)


    security.declareProtected(manage_users, 'manage_editUser')
    def manage_editUser(self, user_dn, REQUEST=None, kwargs={}):
        """ Edit a user record """
        msg = ''
        new_attrs = {}
        if REQUEST is None:
            source = kwargs
        else:
            source = REQUEST

        rdn = self._rdnattr
        mod_rdn = 0

        for attr in self.getSchemaConfig().keys():
            if source.has_key(attr) and (mod_rdn or attr != rdn):
                new = source.get(attr, '')
                if isinstance(new, StringType):
                    new = [x.strip() for x in new.split(';')]

                new_attrs[attr] = new

        if new_attrs:
            msg = err_msg = self._delegate.modify(user_dn, attrs=new_attrs)
        else:
            msg = 'No attributes changed'
            err_msg = ''

        if msg:
            if REQUEST:
                return self.manage_userrecords( manage_tabs_message=msg
                                              , user_dn=user_dn
                                              )
            else:
                return err_msg

        new_cn = mod_rdn and source.get(rdn, '')
        new_dn = ''
        old_dn_exploded = explode_dn(user_dn)
        cur_rdn = old_dn_exploded[0]
        cur_cn = cur_rdn.split('=')[1]

        if new_cn and cur_cn != new_cn:
            old_dn = user_dn
            old_dn_exploded[0] = '%s=%s' % (rdn, new_cn)
            new_dn = ','.join(old_dn_exploded)

            old_groups = self.getGroups(dn=old_dn, attr='dn')

            if self._local_groups:
                if self._groups_store.get(old_dn):
                    del self._groups_store[old_dn]

                self._groups_store[new_dn] = old_groups

            else:
                for group in old_groups:
                    group_type = self.getGroupType(group)
                    member_type = GROUP_MEMBER_MAP.get(group_type)

                    msg = self._delegate.modify( group
                                               , DELETE
                                               , {member_type : [old_dn]}
                                               )
                    msg = self._delegate.modify( group
                                               , ADD
                                               , {member_type : [new_dn]}
                                               )
                    self._expireGroup(group)

        self._expireUser(cur_cn)
        msg = msg or 'User %s changed' % (new_dn or user_dn)

        if REQUEST:
            return self.manage_userrecords( manage_tabs_message=msg
                                          , user_dn=new_dn or user_dn
                                          )


    security.declareProtected(manage_users, 'isUnique')
    def isUnique(self, attr, value):
        """
            Find out if any objects have the same attribute value.
            This method should be called when a new user record is
            about to be created. It guards uniqueness of names by
            warning for items with the same name.
        """
        search_str = '(&(%s=%s)(%s))' % (attr, str(value), self.users_filter or DEFAULT_FILTER)

        res = self._delegate.search( base=self.users_base
                                   , scope=self.users_scope
                                   , filter=search_str
                                   )

        if res['exception']:
            return res['exception']

        return res['size'] < 1


    def getEncryptions(self):
        """ Return the possible encryptions """
        if not crypt:
            return ('SHA', 'SSHA', 'clear')
        else:
            return ('crypt', 'SHA', 'SSHA', 'clear')


    def getLog(self):
        """ Get the log for displaying """
        return self._log.getLog()


    #################################################################
    #
    # Users and groups caching
    #
    #################################################################


    def _getCache( self, cache_type='anonymous' ):
        """ Return object cache of the given type """
        try:
            return getattr( self, '_v_%s_cache' % cache_type )
        except AttributeError:
            cache = getSimpleCache( self, cache_type )
            setattr( self, '_v_%s_cache' % cache_type, cache )
            return cache


    def _clearCaches( self ):
        """ Clear all logs and caches """
        for cache_type in ['anonymous', 'authenticated', 'group']:
            self._getCache( cache_type ).clear()

        self._log.clear()

        for item in ['userlist', 'grouplist', 'pseudogrouplist']:
            try:
                delattr( self, '_v_%s' % item )
                delattr( self, '_v_%s_expire' % item )
            except:
                pass


    security.declareProtected( manage_users, '_expireUser' )
    def _expireUser( self, user ):
        """ Purge user object from caches """
        if not user:
            return

        if type(user) is not StringType:
            user = user.getId()

        self._getCache( 'authenticated' ).remove( user )
        self._getCache( 'anonymous' ).remove( user )


    security.declareProtected( manage_users, '_expireGroup' )
    def _expireGroup( self, group ):
        """ Purge group object from cache """
        # XXX assumes that group ID == DN
        if not group:
            return

        if type(group) is not StringType:
            group = group.getId()

        self._getCache( 'group' ).remove( group )


    security.declareProtected(manage_users, 'getCacheTimeout')
    def getCacheTimeout(self, cache_type='anonymous'):
        """ Retrieve the cache timout value (in seconds) """
        return getattr( self, '_%s_timeout' % cache_type.lower(), DEFAULT_TIMEOUT )


    security.declareProtected(manage_users, 'setCacheTimeout')
    def setCacheTimeout( self
                       , cache_type='anonymous'
                       , timeout=None
                       , REQUEST=None
                       ):
        """ Set the cache timeout """
        if not timeout and timeout != 0:
            timeout = DEFAULT_TIMEOUT
        else:
            timeout = int(timeout)

        setattr( self, '_%s_timeout' % cache_type, timeout )
        self._getCache( cache_type ).setTimeout( timeout )

        if REQUEST is not None:
            msg = 'Cache timeout changed'
            return self.manage_cache(manage_tabs_message=msg)



def manage_addLDAPUserFolder( self, title, LDAP_server, login_attr
                            , users_base, users_scope, roles, groups_base
                            , groups_scope, binduid, bindpwd, binduid_usage=1
                            , rdn_attr='cn', local_groups=0, use_ssl=0
                            , encryption='SHA', read_only=0, REQUEST=None
                            ):
    """ Called by Zope to create and install an LDAPUserFolder """
    this_folder = self.this()

    if hasattr(aq_base(this_folder), 'acl_users') and REQUEST is not None:
        msg = 'This+object+already+contains+a+User+Folder'

    else:
        n = LDAPUserFolder( title, LDAP_server, login_attr, users_base, users_scope
                          , roles, groups_base, groups_scope, binduid, bindpwd
                          , binduid_usage, rdn_attr, local_groups=local_groups
                          , use_ssl=not not use_ssl, encryption=encryption
                          , read_only=read_only, REQUEST=REQUEST
                          )

        this_folder._setObject('acl_users', n)
        this_folder.__allow_groups__ = self.acl_users

        msg = 'Added+LDAPUserFolder'

    # return to the parent object's manage_main
    if REQUEST:
        url = REQUEST['URL1']
        qs = 'manage_tabs_message=%s' % msg
        REQUEST.RESPONSE.redirect('%s/manage_main?%s' % (url, qs))


InitializeClass(LDAPUserFolder)
