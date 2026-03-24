"""
Migration script -- setup the portal categories phase 2.

$Editor: oevsegneev $
$Id: setup_categories_phase2.py,v 1.7 2005/05/14 05:43:46 vsafronovich Exp $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

title = 'Setup the portal categories phase 2'
version = '3.2.0.115'

order = 70
before_script = 1

from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.NauSite import PortalGenerator

def migrate( context, object ):
    wftool = getToolByName( object, 'portal_workflow' )
    if hasattr( wftool, 'heading_workflow' ):
        wftool._delObject( 'heading_workflow' )

    PortalGenerator().setupCategories( object, 2 )
