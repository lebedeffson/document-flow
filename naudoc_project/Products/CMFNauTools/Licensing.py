""" LicensingTool class

SOURCE OF THIS MODULE IS NOT INTENDED TO BE OPEN TO THE CUSTOMERS

$Id: Licensing.py,v 1.3 2006/02/06 08:31:13 vsafronovich Exp $
"""
__version__='$Revision: 1.3 $'[11:-2]

from time import time
from types import StringType

from AccessControl import ClassSecurityInfo
from AccessControl.SpecialUsers import emergency_user as EmergencyUser, nobody as AnonymousUser
from Acquisition import aq_base
from zLOG import LOG, INFO

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

from ActionInformation import ActionInformation
from Config import Roles, ProductName
from Exceptions import LicensingError
from SimpleObjects import ToolBase
from Utils import InitializeClass, uniqueValues

MaxActiveUsers = 1000
ActiveUsersCacheTimeout = 6000

class LicensingTool( ToolBase ):

    _class_version = 1.00

    meta_type = 'NauSite Licensing Tool'
    id = 'portal_licensing'

    security = ClassSecurityInfo()

    _actions = ToolBase._actions + \
               ( ActionInformation(id='licensing'
                            , title='Licensing'
                            , action=Expression(text='string: ${portal_url}/licensing_form')
                            , permissions=(CMFCorePermissions.ManagePortal,)
                            , category='user'
                            , condition=None
                            , visible=1
                            ),
               )

    security.declareProtected( CMFCorePermissions.View, 'listActiveUsers' )
    def listActiveUsers( self, raise_exc=True ):
        """
        """
        global _active_users, _active_users_timeout
        users = _active_users.get( self._p_oid )
        timeout = _active_users_timeout.get( self._p_oid )
        membership = getToolByName( self, 'portal_membership' )
        if not ( timeout and timeout > time() and users is not None ):
            users = []
            for name in membership.listMemberIds():
                user = membership.getMemberById( name )
                if user is None:
                    continue
                if Roles.Active in user.getRoles():
                    users.append( name )
            _active_users[ self._p_oid ] = users
            _active_users_timeout[ self._p_oid ] = time() + ActiveUsersCacheTimeout
            LOG( ProductName, INFO, "License usage: %s" % self.getLicenseUsage() )

        user = membership.getAuthenticatedMember()
        if raise_exc and len( users ) > MaxActiveUsers:
            if aq_base( user.getUser() ) is not EmergencyUser:
                raise LicensingError, 'Your NauDoc license permits up to %d active users, not %s' % ( MaxActiveUsers, len( users ) )

        return list( users )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setActiveUsers' )
    def setActiveUsers( self, users ):
        """
        """
        if isinstance( users, StringType ):
            users = [ users ]

        users = uniqueValues( users )
        if len( users ) > MaxActiveUsers:
            raise LicensingError, 'Your NauDoc license permits up to %d active users, not %s' % ( MaxActiveUsers, len( users ) )

        membership = getToolByName( self, 'portal_membership' )
        for name in membership.listMemberIds():
            user = membership.getMemberById( name )
            if user is None:
                continue
            if user.getId() in users:
                if Roles.Active not in user.getRoles():
                    roles = list( user.getRoles() ) + [ Roles.Active ]
                    user.setSecurityProfile( roles=roles )
            else:
                if Roles.Active in user.getRoles():
                    roles = list( user.getRoles() )
                    roles.remove( Roles.Active )
                    user.setSecurityProfile( roles=roles )

        global _active_users
        _active_users[ self._p_oid ] = None
         
    security.declareProtected( CMFCorePermissions.ManagePortal, 'addActiveUsers' )
    def addActiveUsers( self, users ):
        if isinstance( users, StringType ):
            users = [ users ]
        active_users = self.listActiveUsers()
        active_users.extend( users )
        self.setActiveUsers( active_users )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'delActiveUsers' )
    def delActiveUsers( self, users ):
        if isinstance( users, StringType ):
            users = [ users ]
        active_users = self.listActiveUsers()
        for user in users:
            if user in active_users:
                active_users.remove( user )
        self.setActiveUsers( active_users )

    security.declareProtected( CMFCorePermissions.View, 'getMaxActiveUsers' )
    def getMaxActiveUsers( self ):
        return MaxActiveUsers

    security.declareProtected( CMFCorePermissions.View, 'getActiveUsersCount' )
    def getActiveUsersCount( self ):
        return len( self.listActiveUsers() )

    security.declareProtected( CMFCorePermissions.View, 'validateUser' )
    def validateUser( self, user=None, raise_exc=True ):
        membership = getToolByName( self, 'portal_membership' )
        if user is None:
            user = membership.getAuthenticatedMember()

        if isinstance( user, StringType ):
            user = membership.getMemberById( user )
        if user is None:
            return False

        if aq_base( user ) is AnonymousUser or aq_base( user.getUser() ) is EmergencyUser:
            return True

        if user.getId() not in membership.listMemberIds() and Roles.Manager in user.getRoles():
            return True

        if user.getUserName() in self.listActiveUsers():
            return True

        if raise_exc:
            raise LicensingError, 'User %s is not allowed to use this service due to licensing policy limitations.' % user
        return False

    security.declareProtected( CMFCorePermissions.View, 'getLicenseUsage' )
    def getLicenseUsage( self ):
        membership = getToolByName( self, 'portal_membership' )
        total = len( membership.listMemberIds() )
        return 'maximum active users: %s, now active: %s, total: %s' % ( self.getMaxActiveUsers(), self.getActiveUsersCount(), total )
    

InitializeClass( LicensingTool )

def initialize( context ):
    # module initialization callback

    context.registerTool( LicensingTool )

_active_users = {}
_active_users_timeout = {}
