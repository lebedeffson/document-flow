"""
Migration script -- setup the licensing tool.

$Editor: ikuleshov $
$Id: setup_licensing.py,v 1.3 2007/06/01 10:25:35 oevsegneev Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

from Products.CMFCore.utils import getToolByName

title = 'Setup the licensing tool'
version = '3.3.1.3'
before_script = 1
order = 30 # Must be run after setup_tools and setup_roles scripts

tool_id = 'portal_licensing'

def migrate( context, object ):
    actions = getToolByName( object, 'portal_actions')
    if tool_id not in actions.action_providers:
        actions.action_providers += ( tool_id, )

    membership = getToolByName( object, 'portal_membership' )
    licensing = getToolByName( object, 'portal_licensing' )
    names = membership.listMemberIds()
    # TODO: allow manager to specify the active users list during migration process

    if len( names ) <= licensing.getMaxActiveUsers():
        licensing.setActiveUsers( names )