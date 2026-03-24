# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DirectoryObject/__init__.py
# Compiled at: 2007-06-06 16:37:09
"""
DirectoryObject add-on initialization script.

$Editor: vpastukhov $
$Id: __init__.py,v 1.17 2007/06/06 12:37:09 oevsegneev Exp $
"""
__version__ = '$Revision: 1.17 $'[11:-2]
AddonId = 'DirectoryObject'
AddonTitle = '"Directory" object type'
AddonVersion = '1.1'
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import AddonDeactivateError
from Products.CMFNauTools.Utils import loadModules
import DirectoryBase, Directory, ExternalDirectory
type_infos = [
 Directory.DirectoryType]
type_ids = [t['id'] for t in type_infos]

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True)
    context.registerDirectory('skin', globals())
    for module in loadModules(package='Addons.%s' % AddonId).values():
        init_func = getattr(module, 'initialize', None)
        if callable(init_func):
            init_func(context)

    return


def activate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.addSkinLayer('directories', 'skin', globals())
    portal.addLocalizerMessages(globals())
    types = getToolByName(portal, 'portal_types')
    for t in type_infos:
        types.addType(t['id'], t)

    workflow = getToolByName(portal, 'portal_workflow')
    workflow.setChainForPortalTypes(type_ids, [])
    return


def deactivate(portal):
    objects = []
    catalog = getToolByName(portal, 'portal_catalog')
    results = catalog.unrestrictedSearch(portal_type=type_ids)
    for r in results:
        objects.append(r['nd_uid'])

    if objects:
        raise AddonDeactivateError(id=AddonId, objects=objects)
    types = getToolByName(portal, 'portal_types')
    types.manage_delObjects(type_ids)
    skins = getToolByName(portal, 'portal_skins')
    skins.deleteSkinLayer('directories')
    return
