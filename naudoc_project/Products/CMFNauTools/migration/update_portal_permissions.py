"""
$Id: update_portal_permissions.py,v 1.2 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: inemihin $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = 'Update portal permissions settings'
version = '3.4.0.0'

from Products.CMFNauTools.NauSite import PortalGenerator

def check(context, object):
    return PortalGenerator().setupPermissions( object, check=True ) > 0

def migrate(context, object):
    PortalGenerator().setupPermissions( object )
