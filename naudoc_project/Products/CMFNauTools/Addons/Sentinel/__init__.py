# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/Sentinel/__init__.py
# Compiled at: 2008-12-12 17:12:53
"""
Sentinel initialization script.

$Editor: ypetrov $
$Id: __init__.py,v 1.3 2008/12/12 14:12:53 oevsegneev Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]
from zLOG import LOG, INFO
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import DuplicateIdError
from Products.CMFNauTools.AddonsTool import AddonsTool
from Products.CMFNauTools.Utils import loadModules
AddonId = 'Sentinel'
AddonTitle = 'Sentinel'
AddonVersion = '1.1'
order = 0
OverridedSkins = (
 'manage_addons_form',)

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True)
    registerDirectory('skin', globals())
    for module in loadModules(package='Addons.%s' % AddonId).values():
        init_func = getattr(module, 'initialize', None)
        if callable(init_func):
            init_func(context)

    LOG('Products.CMFNauTools.Addons.%s' % AddonId, INFO, 'overriding skins: %s' % (', ').join(OverridedSkins))
    return


def activate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.addSkinLayer('sentinel', 'skin', globals(), after='custom')
    portal.addLocalizerMessages(globals())
    factory = portal.manage_addProduct['CMFNauTools']
    try:
        factory.manage_addTool('Sentinel Tool', None)
    except DuplicateIdError:
        pass
    else:
        portal_addons = getToolByName(portal, 'portal_addons')
        portal_sentinel = getToolByName(portal, 'portal_sentinel')
        for a in portal_addons.listAddons():
            if portal_addons.getAddonProperty(a['id'], 'is_paid') and a['status'] == 'active':
                portal_sentinel.refreshSpot(a['id'])

    return


def deactivate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.deleteSkinLayer('sentinel')
    return
