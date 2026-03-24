# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/TrayAgent/__init__.py
# Compiled at: 2008-10-15 16:38:04
"""
TrayAgent add-on initialization script.

$Editor: ikuleshov$
$Id: __init__.py,v 1.4 2008/10/15 12:38:04 oevsegneev Exp $
"""
__version__ = '$Revision: 1.4 $'[11:-2]
AddonId = 'TrayAgent'
AddonTitle = 'Tray agent support'
AddonVersion = '1.1'
IsPaid = True
from Products.CMFCore.DirectoryView import registerDirectory, createDirectoryView
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import AddonDeactivateError
from Products.CMFNauTools.Utils import makepath
from TrayAgentFeeder import TrayAgentFeeder, MemberDataExtensions, FeederId

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True, is_paid=IsPaid)
    registerDirectory('skin', globals())
    registerDirectory('distr', globals())
    return


def activate(portal):
    portal_sentinel = getToolByName(portal, 'portal_sentinel')
    if not portal_sentinel.checkActivation(AddonId):
        return False
    skins = getToolByName(portal, 'portal_skins')
    skins.addSkinLayer('trayagent', 'skin', globals(), before='tasks')
    createDirectoryView(portal, makepath('Addons', AddonId, 'distr'), 'trayagent')
    portal.addLocalizerMessages(globals())
    portal._setObject(FeederId, TrayAgentFeeder())
    actions = getToolByName(portal, 'portal_actions')
    if FeederId not in actions.action_providers:
        actions.action_providers += (FeederId,)
    member_data = getToolByName(portal, 'portal_memberdata')
    for p in MemberDataExtensions:
        member_data._setProperty(p['id'], p['default'], p['type'])

    return True
    return


def deactivate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.deleteSkinLayer('trayagent')
    if hasattr(portal, FeederId):
        portal._delObject(FeederId)
    if hasattr(portal, 'trayagent'):
        portal._delObject('trayagent')
    actions = getToolByName(portal, 'portal_actions')
    if FeederId in actions.action_providers:
        actions.action_providers = tuple([x for x in actions.action_providers if x != FeederId])
    member_data = getToolByName(portal, 'portal_memberdata')
    for p in MemberDataExtensions:
        if member_data.hasProperty(p['id']):
            member_data._delProperty(p['id'])

    return
