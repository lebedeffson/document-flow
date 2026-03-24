# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/MaintenancePack/__init__.py
# Compiled at: 2009-02-17 18:04:21
"""
TaskPack add-on initialization script.

$Editor: oevsegneev $
$Id: __init__.py,v 1.1 2009/02/17 15:04:21 oevsegneev Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
AddonId = 'MaintenancePack'
AddonTitle = 'Maintenance Pack Addon'
AddonVersion = '1.0'
IsPaid = True
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Utils import loadModules
from utils import registerAction, unregisterAction
tools = [{'id': 'portal_notifications', 'title': 'Notifications Tool'}, {'id': 'portal_sanation', 'title': 'Sanation Tool'}]

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True, is_paid=IsPaid)
    registerDirectory('skin', globals())
    for module in loadModules(package='Addons.%s' % AddonId).values():
        init_func = getattr(module, 'initialize', None)
        if callable(init_func):
            init_func(context)

    return


def activate(portal):
    portal_sentinel = getToolByName(portal, 'portal_sentinel')
    if not portal_sentinel.checkActivation(AddonId):
        return False
    skins = getToolByName(portal, 'portal_skins')
    skins.addSkinLayer('maintenance_pack', 'skin', globals(), after='custom')
    portal.addLocalizerMessages(globals())
    registerAction(getToolByName(portal, 'portal_membership', None), id='switchMember', title='Switch member', description='Switch member', form='switch_member_form', category='user')
    factory = portal.manage_addProduct['CMFNauTools']
    action_tool = getToolByName(portal, 'portal_actions', None)
    if action_tool is None:
        return
    for tool in tools:
        if hasattr(portal, tool['id']):
            portal._delObject(tool['id'])
        factory.manage_addTool(tool['title'], None)
        if tool['id'] not in action_tool.action_providers:
            action_tool.action_providers = action_tool.action_providers + (tool['id'],)

    portal.portal_notifications.resetNotifications()
    return


def deactivate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.deleteSkinLayer('maintenance_pack')
    unregisterAction(getToolByName(portal, 'portal_membership', None), 'switchMember')
    action_tool = getToolByName(portal, 'portal_actions', None)
    if action_tool is None:
        return
    for tool in tools:
        if tool['id'] in action_tool.action_providers:
            action_providers = list(action_tool.action_providers)
            action_providers.remove(tool['id'])
            action_tool.action_providers = tuple(action_providers)
        if hasattr(portal, tool['id']):
            portal._delObject(tool['id'])

    return
