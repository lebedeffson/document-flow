"""
$Id: update_workflows.py,v 1.3 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

title = 'Update workflow chains'
version = '3.4.0.0'
before_script = 1
order = 10

from Products.CMFNauTools.NauSite import PortalGenerator

def check( context, object ):
    return PortalGenerator().setupWorkflow( object, check=True )

def migrate( context, object ):
    PortalGenerator().setupWorkflow( object )
