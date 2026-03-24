#####################################################################
#
# LDAPGroup     The Group object for the LDAP User Folder
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__ = '$Revision: 1.4 $'[11:-2]

# General python imports
from time import time
from types import ListType

# Zope imports
from Globals import InitializeClass
from Acquisition import Implicit, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import access_contents_information, manage_users
from DateTime import DateTime

# NuxUserGroups package imports
try:
    from Products.NuxUserGroups.UserFolderWithGroups import BasicGroup as _BasicGroup
except ImportError:
    _BasicGroup = None

# LDAPUserFolder package imports
from LDAPDelegate import explode_dn
from SimpleCache import deepCopyExtClass
from utils import GROUP_MEMBER_MAP, _verifyUnicode, encoding, user_encoding, to_utf8


# grrrrrr... why the hell is Nux BasicGroup persistent???
class BasicGroup( Implicit ):
    security = ClassSecurityInfo()

    # derived classes must call the base __init__
    def __init__(self, id, title='', **kw):
        self.id = id
        self.title = title

    #
    # To implement
    #
    security.declareProtected(access_contents_information, 'getId')
    def getId(self):
        return self.id

    security.declareProtected(access_contents_information, 'Title')
    def Title(self):
        return self.title

    security.declareProtected(manage_users, 'getUsers')
    def getUsers(self):
        """Group users"""
        return NotImplemented

    security.declarePrivate('_setUsers')
    def _setUsers(self, usernames):
        # this method is not responsible for keeping in sync
        # with the User objects or the GroupFolder
        return NotImplemented

    security.declarePrivate('_addUsers')
    def _addUsers(self, usernames):
        # this method is not responsible for keeping in sync
        # with the User objects or the GroupFolder
        return NotImplemented

    security.declarePrivate('_delUsers')
    def _delUsers(self, usernames):
        # this method is not responsible for keeping in sync
        # with the User objects or the GroupFolder
        return NotImplemented

    #
    # Basic API
    #

    security.declareProtected(manage_users, 'setTitle')
    def setTitle(self, title):
        self.title = title

    security.declareProtected(manage_users, 'edit')
    def edit(self, title=None, usernames=None, **kw):
        """edit the group"""
        if title is not None:
            self.setTitle(title)
        if usernames is not None:
            self.setUsers(usernames)

InitializeClass(BasicGroup)

class LDAPGroup( BasicGroup ):
    """
    """

    security = ClassSecurityInfo()

    def __init__( self, id, title='', record=None, **kw ):
        BasicGroup.__init__( self, id )

        args = self.parseRecord( record, kw )
        dn = args.get( 'dn', None )
        name = args.get( 'name', None )

        self.dn = dn or id
        self.name = name  or id
        self.title = title or args.get( 'title', '' )

        self.read_only = args.get( 'read_only', 0 )
        self.user_dns = args.get( 'user_dns', [] )

        self._created = time()

    # deepcopy support -- used by SimpleCache
    __deepcopy__ = deepCopyExtClass

    security.declarePublic( 'getGroupName' )
    def getGroupName( self ):
        """ Returns name (LDAP CN) of the group """
        return self.name

    security.declareProtected( access_contents_information, 'getGroupDN' )
    def getGroupDN( self ):
        """ Returns LDAP DN of the group """
        return self.dn

    security.declareProtected( access_contents_information, 'isReadOnly' )
    def isReadOnly( self ):
        """ Checks whether group modification is forbidden """
        return self.read_only

    security.declareProtected( access_contents_information, 'isUsersStorage' )
    def isUsersStorage( self ):
        """ Checks whether the group is a container for user accounts """
        return 0

    def getUsers( self ):
        """ Returns a list of usernames """
        users  = []
        parent = aq_parent( aq_inner(self) )

        for dn in self.user_dns:
            try:
                user = self.getUserByDN( to_utf8(dn) )
            except:
                continue
            if user is not None:
                users.append( user.getUserName() )

        return tuple( users )

    def _setUsers( self, usernames ):
        # sets group members
        if self.read_only:
            raise RuntimeError, "group \"%s\" is read-only" % self.getId()

        add_names = list( usernames )
        del_names = []

        for name in self.getUsers():
            if name in add_names:
                # user is already in group - no need to add
                add_names.remove( name )
            elif name not in usernames:
                # user is not in the list - should be deleted
                del_names.append( name )

        self._delUsers( del_names )
        self._addUsers( add_names )

    def _addUsers( self, usernames ):
        # adds members to the group
        if self.read_only:
            raise RuntimeError, "group \"%s\" is read-only" % self.getId()

        id = self.getId()
        users = self.user_dns
        parent = aq_parent( aq_inner(self) )
        #print '_addUsers', id, usernames, users

        for name in usernames:
            user = parent.getUser( name )
            groups = list( user.getGroups() )
            if id not in groups:
                # XXX assumes that group ID == DN
                groups.append( id )
            parent.manage_editUserRoles( user.getUserDN(), groups )
            users.append( user.getUserDN() )

    def _delUsers( self, usernames ):
        # removes members from the group
        if self.read_only:
            raise RuntimeError, "group \"%s\" is read-only" % self.getId()

        id = self.getId()
        users = self.user_dns
        parent = aq_parent( aq_inner(self) )
        #print '_delUsers', id, usernames, users

        for name in usernames:
            user = parent.getUser( name )
            groups = list( user.getGroups() )
            if id in groups:
                # XXX assumes that group ID == DN
                groups.remove( id )
            parent.manage_editUserRoles( user.getUserDN(), groups )
            users.remove( user.getUserDN() )

    def edit( self, title=None, **kw ):
        """ Modifies the group properties """
        if self.read_only:
            raise RuntimeError, "group \"%s\" is read-only" % self.getId()

        if title is not None:
            self.setTitle( title )

    security.declarePrivate( 'parseRecord' )
    def parseRecord( self, record, props ):
        """ Parses LDAP record into group properties """
        if not record:
            return props

        props.setdefault( 'dn', record['dn'] )

        name = record.get('cn')
        name = name and name[0] or ''
        props.setdefault( 'name', name )

        if not props.has_key('title'):
            title = record.get('description')
            if title:
                title = title[0].strip()
            elif name:
                title = name
            else:
                title = explode_dn( props['dn'] )[0].split('=',1)[1]
            props['title'] = title

        if not props.has_key('user_dns'):
            users = {}
            for attr in GROUP_MEMBER_MAP.values():
                for dn in record.get( attr, [] ):
                    users[ dn ] = 1
            props['user_dns'] = users.keys()

        else:
            props['user_dns'] = list( props['user_dns'] )

        return props

    security.declarePrivate( 'getCreationTime' )
    def getCreationTime( self ):
        """ When was this group object created? """
        return DateTime( self._created )

InitializeClass( LDAPGroup )


class LDAPPseudoGroup( BasicGroup ):
    """
    """

    security = ClassSecurityInfo()

    def __init__( self, id, title='', record=None, **kw ):
        BasicGroup.__init__( self, id )

        args = self.parseRecord( record, kw )
        self.dn = args.get( 'dn', id )
        self.name = args.get( 'name', id )
        self.title = title or args.get( 'title', '' )

        self._created = time()

    # deepcopy support -- used by SimpleCache
    __deepcopy__ = deepCopyExtClass

    security.declareProtected(access_contents_information, 'Title')
    def Title(self):
        return self.getGroupName()

    security.declarePublic( 'getGroupName' )
    def getGroupName( self ):
        """ Returns name (LDAP CN) of the group """
        return self.name

    security.declareProtected( access_contents_information, 'getGroupDN' )
    def getGroupDN( self ):
        """ Returns LDAP DN of the group """
        return self.dn

    security.declareProtected( access_contents_information, 'isReadOnly' )
    def isReadOnly( self ):
        """ Checks whether group modification is forbidden """
        return 1

    security.declareProtected( access_contents_information, 'isUsersStorage' )
    def isUsersStorage( self ):
        """ Checks whether the group is a container for user accounts """
        return 1

    def getUsers( self ):
        """ Returns a list of usernames """
        users  = []
        parent = aq_parent( aq_inner(self) )
        login  = parent._login_attr

        for record in parent.findUser( 'memberOf', self.dn ):
            name = record[ login ]
            if type(name) is ListType and name:
                name = name[0]
            if name:
                users.append( str(name) )

        return tuple( users )

    def edit( self, title=None, **kw ):
        """ Modifies the group properties """
        if title is not None:
            self.setTitle( title )

    security.declarePrivate( 'parseRecord' )
    def parseRecord( self, record, props ):
        """ Parses LDAP record into pseudogroup properties """
        if not record:
            return props

        props.setdefault( 'dn', record['dn'] )

        name = record.get('cn')
        name = name and name[0] or ''
        props.setdefault( 'name', name )

        if not props.has_key('title'):
            title = record.get('description')
            if title:
                title = title[0].strip()
            elif name:
                title = name
            else:
                title = explode_dn( props['dn'] )[0].split('=',1)[1]
            props['title'] = title

        return props

    security.declarePrivate( 'getCreationTime' )
    def getCreationTime( self ):
        """ When was this pseudogroup object created? """
        return DateTime( self._created )

InitializeClass( LDAPPseudoGroup )
