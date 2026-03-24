"""
$Id: fix_version_roles.py,v 1.4 2004/04/30 10:08:12 vpastukhov Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.4 $'[11:-2]

title = 'Fix role settings on the versionable content'
version = '2.12'
classes = ['Products.CMFNauTools.HTMLDocument.HTMLDocument']

from types import DictType
from Products.CMFNauTools.ContentVersions import VersionableRoles

def check( context, object ):
    return type( object.__ac_local_roles__ ) is DictType

def migrate( context, object ):
    object.__ac_local_roles__ = VersionableRoles( object.__ac_local_roles__ )
    object.reindexObject( idxs=['allowedRolesAndUsers','Creator'] )
