"""
$Editor: ikuleshov $
$Id: setup_membership.py,v 1.7 2007/11/16 13:37:10 oevsegneev Exp $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

title = 'Setup membership'
version = '3.4.0.0'
before_script = 1
order = 10

from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.NauSite import PortalGenerator

def check( context, object ):
    return PortalGenerator().setupMembership( object, check=True ) > 0

def migrate( context, object ):
    PortalGenerator().setupMembership( object )

    membership = getToolByName( object, 'portal_membership' )
    all_group = membership.getGroup( 'all_users', None )
    users = membership.listMemberIds( all=True )

    if users and all_group and not all_group.getUsers():
        acl_users = membership.acl_users
        all_group._setUsers( users )
        # update info in users
        for username in users:
            user = membership.getMemberById( username )
            if user is None:
                continue
            if 'all_users' not in user.getGroups():
                user.getUser()._addGroups(('all_users',))

    if membership.getGroup( 'All users', None ):
        membership._delGroups( ['All users'] )
