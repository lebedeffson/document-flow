"""
Migration script -- setup portal roles.

$Editor: ikuleshov $
$Id: setup_roles.py,v 1.4 2007/11/16 13:37:10 oevsegneev Exp $
"""
__version__ = '$Revision: 1.4 $'[11:-2]

title = 'Setup portal roles'
version = '3.4.0.0'
before_script = 1
order = 20

from Products.CMFNauTools.NauSite import RolesInstaller

def migrate( context, object ):
    RolesInstaller().install( object )
