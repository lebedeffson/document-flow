# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DigitalSignature/__init__.py
# Compiled at: 2008-10-22 13:21:33
"""
DirectoryObject add-on initialization script.

$Editor: vpastukhov $
$Id: __init__.py,v 1.5 2008/10/22 09:21:33 oevsegneev Exp $
"""
__version__ = '$Revision: 1.5 $'[11:-2]
AddonId = 'DigitalSignature'
AddonTitle = 'Digital Signature'
AddonVersion = '1.6'
IsPaid = True
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.ActionInformation import ActionInformation as AI
from Products.CMFNauTools.Exceptions import DuplicateIdError
from Products.CMFNauTools.MembershipTool import MembershipTool
from Products.CMFNauTools.NauSite import PortalGenerator
from Products.CMFNauTools.Utils import loadModules
MemberDataExtensions = [{'id': 'ds_certificate', 'type': 'string', 'mode': 'w', 'default': ''}]
InterfacePropertiesExtensions = [{'id': 'ds_auto_verify', 'default': 1}]

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True, is_paid=IsPaid)
    registerDirectory('skin', globals())
    MembershipTool._interface_properties = MembershipTool._interface_properties + InterfacePropertiesExtensions
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
    skins.addSkinLayer('signature', 'skin', globals(), after='custom')
    portal.addLocalizerMessages(globals())
    mdata = getToolByName(portal, 'portal_memberdata')
    for p in MemberDataExtensions:
        mdata._setProperty(p['id'], p['default'], p['type'])

    factory = portal.manage_addProduct['CMFNauTools']
    try:
        factory.manage_addTool('Digital Signature Tool', None)
    except DuplicateIdError:
        pass

    tool = getToolByName(portal, 'portal_actions', None)
    if tool is None:
        return
    if 'portal_signature' not in tool.action_providers:
        tool.action_providers = tool.action_providers + ('portal_signature',)
    types = getToolByName(portal, 'portal_types', None)
    _fti_action = AI(id='signatures', title='Signatures', action='document_signatures_form', permissions=(CMFCorePermissions.View,))
    actions = list(types['HTMLDocument']._actions)
    actions.append(_fti_action)
    types['HTMLDocument']._actions = tuple(actions)
    return


def deactivate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.deleteSkinLayer('signature')
    member_data = getToolByName(portal, 'portal_memberdata')
    for p in MemberDataExtensions:
        if member_data.hasProperty(p['id']):
            member_data._delProperty(p['id'])

    types = getToolByName(portal, 'portal_types', None)
    _actions = []
    for action in types['HTMLDocument']._actions:
        if action.id != 'signatures':
            _actions.append(action)

    types['HTMLDocument']._actions = tuple(_actions)
    tool = getToolByName(portal, 'portal_actions', None)
    if tool is None:
        return
    if 'portal_signature' in tool.action_providers:
        action_providers = list(tool.action_providers)
        action_providers.remove('portal_signature')
        tool.action_providers = tuple(action_providers)
    portal._delObject('portal_signature')
    return
