"""
$Id: ac_restrictions.py,v 1.4 2004/04/30 18:48:17 vpastukhov Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.4 $'[11:-2]

title = 'Install access control restrictions'
version = '3.1.2.45'
classes = [ 'Products.CMFNauTools.SimpleObjects.InstanceBase',
            'Products.CMFNauTools.ContentVersions.ContentVersion',
            'Products.CMFNauTools.ContentVersions.VersionableContent' ]

from AccessControl.Permission import RestrictedPermission, pname
from Products.CMFNauTools.Utils import SequenceTypes

def check( context, object ):
    for perm in object.__ac_restricted_permissions__.keys():
        if type( object.__dict__.get( pname( perm ) )) in SequenceTypes:
            return True
    return False

def migrate( context, object ):
    for perm in object.__ac_restricted_permissions__.keys():
        p = pname( perm )
        roles = getattr( object, p, None )
        if roles is not None:
            setattr( object, p, RestrictedPermission( perm, roles ) )

    context.markForReindex( object, idxs=['allowedRolesAndUsers'], recursive=True )
