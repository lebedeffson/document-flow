"""
$Id: update_actions.py,v 1.2 2007/06/01 10:25:35 oevsegneev Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = 'Update portal actions'
version = '3.2.1.1'
before_script = 1
order = 0

from Products.CMFCore.utils import getToolByName

def migrate( context, object ):
    portal_types = getToolByName( object, 'portal_actions' )
    if portal_types.__dict__.has_key('action_providers'):
        del portal_types.action_providers
