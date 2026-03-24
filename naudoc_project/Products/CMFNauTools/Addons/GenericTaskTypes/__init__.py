# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/__init__.py
# Compiled at: 2008-05-27 14:14:07
"""
$Editor: ikuleshov $
$Id: __init__.py,v 1.7 2008/05/27 10:14:07 oevsegneev Exp $
"""
__version__ = '$Revision: 1.7 $'[11:-2]
AddonId = 'GenericTaskTypes'
AddonTitle = 'Generic task types'
AddonVersion = '1.0'
from types import StringType
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import AddonDeactivateError
from Products.CMFNauTools.FollowupActionsTool import task_type_information
from Products.CMFNauTools.Utils import loadModules, getClassName

def isLocalClass(klass):
    if not isinstance(klass, StringType):
        klass = getClassName(klass)
    return klass.startswith(__name__)
    return


def listTaskTypes():
    type_infos = []
    for t in task_type_information:
        if not isLocalClass(t['factory']):
            continue
        type_infos.append(t)

    return type_infos
    return


def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True)
    for module in loadModules(package='Addons.%s' % AddonId).values():
        init_func = getattr(module, 'initialize', None)
        if callable(init_func):
            init_func(context)

    return


def activate(portal):
    types = getToolByName(portal, 'portal_types')
    for t in listTaskTypes():
        types.addType(t['id'], t)

    workflow = getToolByName(portal, 'portal_workflow')
    workflow.setChainForPortalTypes([t['id'] for t in listTaskTypes()], [])
    portal.addLocalizerMessages(globals())
    return


def deactivate(portal):
    type_infos = listTaskTypes()
    type_ids = [t['id'] for t in type_infos]
    if not type_ids:
        return
    objects = []
    catalog = getToolByName(portal, 'portal_catalog')
    results = catalog.unrestrictedSearch(portal_type=type_ids)
    for r in results:
        objects.append(r['nd_uid'])

    if objects:
        raise AddonDeactivateError(id=AddonId, objects=objects)
    types = getToolByName(portal, 'portal_types')
    for t in type_infos:
        try:
            types._delObject(t['id'])
        except AttributeError:
            pass

    workflow = getToolByName(portal, 'portal_workflow')
    cbt = workflow._chains_by_type
    for id in type_ids:
        try:
            del cbt[id]
        except KeyError:
            pass

    return
