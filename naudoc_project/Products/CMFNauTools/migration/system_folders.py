"""
Migration script -- setup the system folders.

TODO: remove outdated folders.

$Editor: vpastukhov $
$Id: system_folders.py,v 1.11 2007/11/16 13:37:10 oevsegneev Exp $
"""
__version__ = '$Revision: 1.11 $'[11:-2]

title = 'Setup the system folders'
version = '3.4.0.0'
after_script = 1
order = 10

from Products.CMFNauTools.NauSite import PortalGenerator

def check( context, object ):
    return PortalGenerator().setupFolders( object, check=True ) > 0

def migrate( context, object ):
    PortalGenerator().setupFolders( object )
