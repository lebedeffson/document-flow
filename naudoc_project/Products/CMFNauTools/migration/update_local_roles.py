"""
$Id: update_local_roles.py,v 1.2 2004/09/08 09:40:15 vpastukhov Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = 'Update local group roles'
version = '3.1.5.41'
classes = ['AccessControl.Role.RoleManager']

def check( context, object ):
    return not not object.get_local_roles_for_groupid( 'All users' )

def migrate( context, object ):
    roles = object.get_local_roles_for_groupid( 'All users' )
    object.manage_addLocalGroupRoles( 'all_users', roles )
    object.manage_delLocalGroupRoles( ['All users'] )
    context.markForReindex( object,
                            idxs=['allowedRolesAndUsers'],
                            catalog='portal_catalog',
                            recursive=True
                          )
