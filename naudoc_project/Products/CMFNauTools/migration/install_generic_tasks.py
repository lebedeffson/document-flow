"""
$Id: install_generic_tasks.py,v 1.4 2008/04/08 13:11:18 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.4 $'[11:-2]

title = 'Enable task types addon'
version = '3.3.1.2'
before_script = 1
#order = 3

from Products.CMFNauTools.Exceptions import MigrationError
from Products.CMFCore.utils import getToolByName

TaskTypesAddonId = 'GenericTaskTypes'

def check( context, object ):
    addons = getToolByName( object, 'portal_addons' )
    infos = addons.listAddons()
    for info in infos:
        if not info['id'] == TaskTypesAddonId:
	    continue

        if info['status'] == 'active':
            return False
        elif info['status'] == 'inactive':
            return True

    catalog = getToolByName( object, 'portal_catalog' )
    if catalog.searchResults( portal_type='Task Item' ):
        raise MigrationError, 'Cannot update task items without %s addon.' % TaskTypesAddonId
    return False
        
def migrate( context, object ):
    addons_tool = getToolByName( object, 'portal_addons' )
    addons_tool.activateAddons( TaskTypesAddonId )
    context.markForReindex( catalog='portal_followup', idxs=['isFinalized'] )