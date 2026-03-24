"""
Member data tool.

$Editor: vpastukhov $
$Id: MemberDataTool.py,v 1.52 2006/05/18 14:17:33 oevsegneev Exp $
"""
__version__ = '$Revision: 1.52 $'[11:-2]

from string import strip
from sys import exc_info
from time import time
from types import StringType
from threading import Event
from random import random

from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from Acquisition import aq_base, aq_parent
from BTrees.OOBTree import OOBTree

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, \
        _getAuthenticatedUser, _checkPermission
from Products.CMFCore.MemberDataTool import \
        MemberDataTool as _MemberDataTool, MemberData as _MemberData
from ZODB.POSException import ConflictError

import Config, Exceptions
from Config import Roles
from SimpleObjects import InstanceBase, ToolBase
from Utils import InitializeClass
from ResourceUid import ResourceUid

# used to split fullname into attributes
_name_parts = ['fname','mname','lname']

_positions_cache = {}
_divisions_cache = {}
CACHE_TIMEOUT = 120

class MemberDataTool( ToolBase, _MemberDataTool ):
    """ Portal member data """
    _class_version = 1.13

    meta_type = 'NauSite Member Data Tool'

    security = ClassSecurityInfo()

    manage_options = _MemberDataTool.manage_options # + ToolBase.manage_options

    _actions = tuple(_MemberDataTool._actions)

    _properties = _MemberDataTool._properties + (
            # CMF properties
            {'id':'email',       'type':'string',  'mode':'w', 'default':'', 'title':'E-mail address'},
            {'id':'portal_skin', 'type':'string',  'mode':'w', 'default':''},
            {'id':'listed',      'type':'boolean', 'mode':'w', 'default':''},
            {'id':'login_time',  'type':'date',    'mode':'w', 'default':''},

            # NauDoc properties
            {'id':'fullname',    'type':'string',  'mode':'w', 'default':'', 'title':'Full name'},
            {'id':'fname',       'type':'string',  'mode':'w', 'default':'', 'title':'First name'},
            {'id':'mname',       'type':'string',  'mode':'w', 'default':'', 'title':'Middle name'},
            {'id':'lname',       'type':'string',  'mode':'w', 'default':'', 'title':'Last name'},
            {'id':'company',     'type':'string',  'mode':'w', 'default':'', 'title':'Company'},
            {'id':'notes',       'type':'text',    'mode':'w', 'default':'', 'title':'Notes'},
            {'id':'phone',       'type':'string',  'mode':'w', 'default':'', 'title':'Phone'},
            {'id':'rate_sum',    'type':'int',     'mode':'w', 'default':0},
            {'id':'rate_users',  'type':'tokens',  'mode':'w', 'default':''},
            {'id':'language',    'type':'string',  'mode':'w', 'default':''},
        )

    def __init__( self ):
        """ Initialize class instance
        """
        ToolBase.__init__( self )
        # NB skip _MemberDataTool.__init__ because it calls _setProperty
        self._members = OOBTree()

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not ToolBase._initstate( self, mode ):
            return 0

        if self._properties is not self.__class__._properties:
            pdict = self.propdict()
            for prop in self.__class__._properties:
                try:
                    pd = pdict[ prop['id'] ]
                    map( pd.setdefault, prop.keys(), prop.values() )
                except KeyError:
                    self._properties += prop

        if mode > 1:
            members = self._members
            for item in members.keys():
                self._upgrade( item, MemberData, container=members )

        return 1

    security.declarePrivate( 'getMemberData' )
    def getMemberData( self, id, default=Missing ):
        """
            Returns member data object for the specified user.
        """
        try:
            return self._members[ id ].__of__( self )
        except KeyError:
            if default is not Missing:
                return default
            raise

    security.declarePrivate( 'listStoredMemberIds' )
    def listStoredMemberIds( self ):
        """
            Returns Ids of users whose records are currently stored.
        """
        return self._members.keys()

    def pruneMemberDataContents( self, ids=Missing ):
        """
            Deletes data of users not found in the portal user folder.
        """
        if ids is Missing:
            return _MemberDataTool.pruneMemberDataContents( self )

        membership = getToolByName( self, 'portal_membership' )
        members = membership.listMemberIds()

        data = self._members
        for id in ids:
            if id not in members and data.has_key( id ):
                del data[ id ]

    def wrapUser( self, u ):
        """
            Wraps User object with MemberData object.

            Arguments:

                'u' -- User object.

            Result:

                Wrapped user object.
        """
        while 1:
            try:
                id = u.getUserName()
                members = self._members
                if not members.has_key(id):
                    # Get a temporary member that might be
                    # registered later via registerMemberData().
                    temps = self._v_temps
                    if temps is not None and temps.has_key(id):
                        m = temps[id]
                    else:
                        base = aq_base(self)
                        m = MemberData(base, id)
                        if temps is None:
                            self._v_temps = {id:m}
                        else:
                            temps[id] = m
                else:
                    m = members[id]

                # Create a wrapper with self as containment and
                # the user as context.
                wrapper = m.__of__(self).__of__(u)
                # update wrapper properties from LDAP attributes
                wrapper._updateProperties()

                return wrapper
            except ConflictError:
                Event().wait( 2 * random() )

    security.declarePrivate('registerMemberData')
    def registerMemberData(self, m, id):
        '''
        Adds the given member data to the _members BTree.
        This is done as late as possible to avoid side effect
        transactions and to reduce the necessary number of
        entries.
        '''
        base_memberdata = aq_base( m )
        self._members[id] = base_memberdata
        if hasattr( base_memberdata, 'manage_afterAdd' ):
            m.manage_afterAdd( m, self ) # here m is wrapped object

InitializeClass( MemberDataTool )


class MemberData( InstanceBase, _MemberData ):
    """
        Portal Member object keeps user's settings
    """
    _class_version = 1.9

    meta_type = 'Member Data'

    __resource_type__ = 'user'

    security = ClassSecurityInfo()

    # restore method overridden by PropertyManager in InstanceBase
    getProperty = _MemberData.getProperty

    def __init__( self, tool, id ):
        """ Initialize class instance
        """
        InstanceBase.__init__( self )
        _MemberData.__init__( self, tool, id )

    ### New user object interface methods ###

    def _updateProperties( self ):
        # copies property values from the underlying user object
        # (such as LDAPUser) into the member data
        user = self.getUser()
        userfolder = aq_parent( user )

        if not hasattr( aq_base(userfolder), 'getMappedUserProperties' ):
            return

        mapped = userfolder.getMappedUserProperties()
        tool = self.getTool()

        for prop in mapped:
            # get the property value from LDAPUser object
            value = user.getProperty( prop, None )
            if value is None:
                # try to obtain default value
                value = tool.getProperty( prop )

            # redefine the wrapper value only if it differ
            old = getattr( aq_base(self), prop, None )
            if value is None or value == old:
                continue

            # store new value in the wrapper
            setattr( self, prop, value )

            # special handling for some attributes
            # XXX conflict when both fullname and f/m/l-names are given ?
            if prop == 'fullname' and value:
                for name, value in zip( _name_parts, _parseFullName( value ) ):
                    setattr( self, name, value )

    security.declareProtected( CMFCorePermissions.SetOwnProperties, 'setProperties' )
    def setProperties( self, properties=None, **kwargs ):
        try:
            _MemberData.setProperties( self, properties=properties, **kwargs )
        except:
            if type( exc_info()[0] ) is StringType:
                raise Exceptions.SimpleError, exc_info()[1]
            raise

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setMemberProperties' )
    def setMemberProperties( self, mapping ):
        """
            Sets the properties of the member.
        """
        user = self.getUser()
        userfolder = mapped = None

        if not user.has_role( Roles.Orphaned ):
            userfolder = aq_parent( user )
            if hasattr( aq_base(userfolder), 'getMappedUserProperties' ):
                mapped = userfolder.getMappedUserProperties()

        if mapped:
            updated = {}

            for prop in mapped:
                try:
                    value = mapping[ prop ]
                except KeyError:
                    continue

                old = self.getProperty( prop, None )
                if value != old:
                    updated[ prop ] = value

            if not updated.has_key('fullname'):
                parts = [ mapping.get( prop, '' ) for prop in ['fname','mname','lname'] ]
                value = _formatFullName( parts )
                if value:
                    updated['fullname'] = value

            if updated:
                userfolder.setUserProperties( self.getUserName(), updated )

        _MemberData.setMemberProperties( self, mapping )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setSecurityProfile' )
    def setSecurityProfile( self, password=None, roles=None, domains=None ):
        """
            Sets the user's basic security profile.
        """
        user = self.getUser()
        if user.has_role( Roles.Orphaned ):
            raise Exceptions.SimpleError( "Security settings of a dismissed user cannot be modified.", user=user )

        if roles is None:
            roles = user.getRoles()
        if domains is None:
            domains = user.getDomains()

        userfolder = aq_parent( user )
        userfolder.userFolderEditUser( user.getUserName(), password, roles, domains )

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'getMemberName' )
    def getMemberName( self, brief=False, positions=False ):
        """
            Returns a full name of the user.

            Result:

                String.
        """
        parts = [ self.getProperty(p) for p in ['fname','mname','lname'] ]

        name = brief and _formatBriefName( parts ) \
               or _formatFullName( parts, canonical=0 )

        # add position if it exists
        if positions and name:
            pos = ', '.join( self.listPositions() )
            if pos:
                name += ' [%s]' % pos

        return name or self.getUserName()

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'getMemberBriefName' )
    def getMemberBriefName( self ):
        """
            Returns a brief name of the user.

            Result:

                String.
        """
        import warnings
        warnings.warn('MemberData.getMemberBriefName deprecated,'
                      ' use getMemberName with brief arg', DeprecationWarning)

        parts = [ self.getProperty(p) for p in ['fname','mname','lname'] ]
        return _formatBriefName( parts ) or self.getUserName()

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'getMemberEmail' )
    def getMemberEmail( self ):
        """
            Returns the user's email address.

            Result:

                String.
        """
        return self.getProperty('email') or self.getMemberId()

    def listStaffListEntries( self ):
        """
            Returns all staff list directory entries where user is assigned as 
            employee or deputy.

            XXX: Move to StaffListDirectory class
        """
        membership = getToolByName( self, 'portal_membership' )
        staff_list = membership.getStaffList()
        employee_list = membership.getEmployeeList()
        if not (staff_list and employee_list):
            return []
        entries = employee_list._catalogSearch( associate_user=self.getId() )
        if not entries:
            return []
        entry = employee_list.getEntry( entries[0] )
        entry_uid = str(ResourceUid( entry ))

        # XXX: employ caching
        entries = staff_list._catalogSearch( employee=entry_uid )
        entries += staff_list._catalogSearch( deputy=entry_uid )
        results = [staff_list.getEntry( e ) for e in entries]
        return results

    def listStaffListSuperiorEntries( self, inclusive=False ):
        """
            inclusive -- if true, entries where user is specified as employee 
                         or deputy are added to result; only superior staff list
                         entries are returned otherwise.

            XXX: Add 'level' argument
            XXX: Move to StaffListDirectory class
        """
        entries = self.listStaffListEntries()
        if inclusive:
            results = list( entries )
        else:
            results = []

        for node in entries:
            results.extend( node.listParentNodes() )
        return results

    def listStaffListSubordinateEntries( self, inclusive=False ):
        """
            inclusive -- if true, entries where user is specified as employee 
                         or deputy are added to result; only subordinate staff 
                         listentries are returned otherwise.

            XXX: Add 'level' argument
            XXX: Move to StaffListDirectory class
        """
        entries = self.listStaffListEntries()
        if inclusive:
            results = list( entries )
        else:
            results = []

        for node in entries:
            results.extend( node.listEntries() )
        return results

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listPositions' )
    def listPositions( self ):
        """
            Returns the user's positions list.

            Note that this method returns positions titles. If you want to get 
            entry codes, then you should look at listStaffListEntries method.
        """
        key = self._p_oid
        result, timeout = _positions_cache.get( key, ( None, 0 ) )
        if timeout > time() and result is not None:
            return result

        entries = self.listStaffListEntries()
        result = []
        for node in entries:
            v = node.getEntryAttribute( 'position' )
            if not v:
                continue
            result.append( v.Title() )

        _positions_cache[ key ] = ( result, time() + CACHE_TIMEOUT )

        return result


    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listDivisions' )
    def listDivisions( self ):
        """
            Returns the user's divisions list.

            Note that this method returns divisions titles. If you want to get 
            entry codes, then you should look at listStaffListEntries method.
        """
        key = self._p_oid
        result, timeout = _divisions_cache.get( key, ( None, 0 ) )
        if timeout > time() and result is not None:
            return result

        entries = self.listStaffListSuperiorEntries( inclusive=True )
        result = []
        for node in entries:
            v = node.getEntryAttribute( 'division' )
            if not ( v and node.isBranch() ):
                continue
            result.append( v.Title() )

        _divisions_cache[ key ] = ( result, time() + CACHE_TIMEOUT )

        return result

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listSubordinateMembers' )
    def listSubordinateMembers( self ):
        """
        """
        membership = getToolByName( self, 'portal_membership' )
        entries = self.listStaffListSubordinateEntries()
        return membership.listPlainUsers( entries )

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listSuperiorMembers' )
    def listSuperiorMembers( self ):
        """
        """
        membership = getToolByName( self, 'portal_membership' )
        entries = self.listStaffListSuperiorEntries()
        return membership.listPlainUsers( entries )

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listMates' )
    def listMates( self ):
        """
           Returns the list of all users who are the deputy of the current user 
           and all users for whom the current user is appointed as a deputy.
        """
        membership = getToolByName( self, 'portal_membership' )
        entries = self.listStaffListEntries()
        return membership.listPlainUsers( entries )
        
    security.declareProtected( CMFCorePermissions.SetOwnProperties, 'getHomeFolder' )
    def getHomeFolder( self, create=None ):
        """
            Returns the user's home folder, optionally creates it if it does not exist yet.

            Arguments:

                'create' -- Boolean. Indicates whether it is required to create
                            the home folder if it does not exist.

            Result:

                Folder object reference.
        """
        members = self.getPortalObject().getProperty( 'members_folder', None )
        if members is None:
            if not create:
                return None
            raise Exceptions.SimpleError( "Members folder does not exist." )

        username = self.getUserName()
        home = members._getOb( username, None )
        if home is not None:
            if not _checkPermission( CMFCorePermissions.View, home ):
                raise Exceptions.Unauthorized, username
            return home

        if not create:
            return None

        authuser = _getAuthenticatedUser( self ).getUserName()
        if authuser != username and not _checkPermission( ZopePermissions.manage_users, members ):
            raise Exceptions.Unauthorized, username

        members.manage_addProduct['CMFNauTools'].manage_addHeading( id=username, title=self.getMemberName() )
        home = members[ username ]

        home.changeOwnership( username, recursive=1 )
        home.setLocalRoles( username, [ Roles.Owner, Roles.Editor ] )
        if authuser != username:
            home.delLocalRoles( authuser )

        return home

    security.declareProtected( CMFCorePermissions.SetOwnProperties, 'getPersonalFolder' )
    def getPersonalFolder( self, ftype=None, create=None ):
        """
            Returns the user's personal folder, optionally creates it if it does not exist yet.

            Arguments:

                'create' -- Boolean. Indicates whether it is required to create
                            the personal folder if it does not exist.

                'ftype' -- String. Specifies the personal folder type (i.e.
                          'favorites', 'mail' etc.).

            Result:

                Folder object reference.
        """
        home = self.getHomeFolder( create=create )
        if home is None or ftype is None:
            return home

        # TODO: allow users to assign custom folders in the preferences
        folder = home._getOb( ftype, None )
        if folder is not None:
            return folder

        if not create:
            return None

        for item in Config.PersonalFolders:
            if item['id'] == ftype:
                title = item.get( 'title', ftype )
                break
        else:
            title = ftype

        msgcat = getToolByName( self, 'msg' )
        title = msgcat.gettext( title, lang=msgcat.get_default_language() )

        home.manage_addProduct['CMFNauTools'].manage_addHeading( id=ftype, title=title )
        return home[ ftype ]

    security.declareProtected( CMFCorePermissions.SetOwnProperties, 'getPersonalFolderPath' )
    def getPersonalFolderPath( self, ftype=None, create=None ):
        """
            Returns the path to the user's personal folder by type.

            Arguments:

                'ftype' -- String. Specifies the personal folder type (i.e.
                          'favorites', 'mail' etc.).

                'create' -- Boolean. Indicates whether it is required to create
                            the personal folder if it does not exist.

            Result:

                List containing the folder physical path or None.
        """
        folder = self.getPersonalFolder( ftype, create )
        if folder is None:
            return None
        return folder.physical_path()

    security.declareProtected( CMFCorePermissions.SetOwnProperties, 'getPersonalFolderUrl' )
    def getPersonalFolderUrl( self, ftype=None, create=None, *args, **kw ):
        """
            Returns the URL of the user's personal folder by type.

            Arguments:

                'ftype' -- String. Specifies the personal folder type (i.e.
                          'favorites', 'mail' etc.).

                'create' -- Boolean. Indicates whether it is required to create
                            the personal folder if it does not exist.

                '*args', '**kw' -- Additional arguments to be passed to the
                                   absolute_url method.

            Result:

                String.
        """
        folder = self.getPersonalFolder( ftype, create )
        if folder is None:
            return None
        return folder.absolute_url( *args, **kw )

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'isMemberOfGroup' )
    def isMemberOfGroup( self, group ):
        """
            Checks whether the user participates in the given group.

            Arguments:

                'group' -- either group object or identifier string

            Result:

                Boolean value.
        """
        if type(group) is not StringType:
            group = group.getId()
        return (group in self.getGroups())

    security.declareProtected( CMFCorePermissions.View, 'isActive' )
    def isActive( self ):
        return self.active

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setActive' )
    def setActive( self, active=True ):
        self.active = bool( active )

InitializeClass( MemberData )


# TODO these must be localized

def _parseFullName( name ):
    """
        Splits long human name into first-middle-last name components.

        Arguments:

            'name' -- human name string

        Result:

            Tuple of strings - (first, middle, last).
    """
    parts = name.split()
    if len(parts) == 1:
        return ( parts[0], '', '' )
    # TODO parse "Last F.M." and "F.M. Last"
    if parts[0][-1] == ',':
        return ( parts[1], ' '.join(parts[2:]), parts[0][:-1] )
    else:
        return ( parts[0], ' '.join(parts[1:-1]), parts[-1] )

def _formatFullName( parts, default='', canonical=1 ):
    """
        Returns human name in "First Middle Last" form.

        Arguments:

            'parts' -- tuple of strings (first, middle, last)

            'default' -- value to return if the name is empty

            'canonical' -- optional flag; if true (default),
                        "F-M-L" form is used, "L-M-F" otherwise

        Result:

            String.
    """
    if not canonical:
        parts = parts[-1:] + parts[:-1]
    return ' '.join( filter( None, map( strip, parts ) ) ) or default

def _formatBriefName( parts, default='' ):
    """
        Returns human name in "Last F.M." form.

        Arguments:

            'parts' -- tuple of strings (first, middle, last)

            'default' -- value to return if the name is empty

        Result:

            String.
    """
    fname, mname, lname = map( strip, parts )
    if lname:
        fname, mname = [ n and n[0]+'.' or '' for n in fname, mname ]
        return lname + (fname and ' '+fname+mname or '')
    if fname:
        return fname + (mname and ' '+mname or '')
    return default

class UserResource:

    def identify( portal, object ):
        return { 'uid' : object.getId() }

    def lookup( portal, uid=None, **kwargs ):
        members = getToolByName( portal, 'portal_membership' )
        object = members.getMemberById( uid )
        if object is None:
            raise Exceptions.LocatorError( 'user', uid )
        return object


def initialize( context ):
    # module initialization callback

    context.registerResource( 'user', UserResource, moniker='user' )

    context.registerTool( MemberDataTool )
