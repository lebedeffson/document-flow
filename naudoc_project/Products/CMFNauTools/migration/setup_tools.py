"""
Migration script -- setup the portal tools.

TODO: remove outdated tools.

$Editor: vpastukhov $
$Id: setup_tools.py,v 1.9 2007/11/16 13:37:10 oevsegneev Exp $
"""
__version__ = '$Revision: 1.9 $'[11:-2]

title = 'Setup the portal tools'
version = '3.4.0.0'
before_script = 1

# must be run before setup_skins
#order = 25
order = 0

from Products.CMFNauTools.Exceptions import DuplicateIdError
from Products.CMFNauTools.NauSite import PortalGenerator

from fix_folders_map import repair

def check( context, object ):
    return PortalGenerator().setupTools( object, check=True ) > 0

def migrate( context, object ):
    repair( object )
    while 1:
        try:
            PortalGenerator().setupTools( object )

        except DuplicateIdError, exc:
            factory = object.manage_addProduct['CMFNauTools']
            for tool in factory.toolinit.tools:
                if tool.id == exc['id']:
                    break
            else:
                raise
            object._upgrade( tool.id, tool )
        else:
            break
