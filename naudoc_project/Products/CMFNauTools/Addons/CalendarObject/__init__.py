# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/CalendarObject/__init__.py
# Compiled at: 2008-10-15 16:35:59
"""
CalendarObject add-on initialization script.

$Editor: vpastukhov $
$Id: __init__.py,v 1.4 2008/10/15 12:35:59 oevsegneev Exp $
"""
__version__ = '$Revision: 1.4 $'[11:-2]
AddonId = 'CalendarObject'
AddonTitle = '"Calendar" object type'
AddonVersion = '1.2'
IsPaid = True
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import AddonDeactivateError
import Calendar, CalendarBase
type_infos = [
 Calendar.CalendarType]
type_ids = [t['id'] for t in type_infos]

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True, is_paid=IsPaid)
    registerDirectory('skin', globals())
    registerDirectory('skin/images', globals())
    CalendarBase.initialize(context)
    Calendar.initialize(context)
    return


def activate(portal):
    portal_sentinel = getToolByName(portal, 'portal_sentinel')
    if not portal_sentinel.checkActivation(AddonId):
        return False
    skins = getToolByName(portal, 'portal_skins')
    skins.addSkinLayer('calendaries', 'skin', globals())
    skins.addSkinLayer('calendaries_images', 'skin/images', globals())
    portal.addLocalizerMessages(globals())
    types = getToolByName(portal, 'portal_types')
    for t in type_infos:
        types.addType(t['id'], t)

    workflow = getToolByName(portal, 'portal_workflow')
    workflow.setChainForPortalTypes(type_ids, [])
    return True
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
    skins.deleteSkinLayer('calendaries')
    skins.deleteSkinLayer('calendaries_images')
    return
