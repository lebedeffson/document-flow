# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/SiteObject/__init__.py
# Compiled at: 2008-10-24 15:09:58
"""
Site add-on initialization script.

$Editor: oevsegneev $
$Id: __init__.py,v 1.3 2008/10/24 11:09:58 oevsegneev Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]
AddonId = 'SiteObject'
AddonTitle = '"Site" object type'
AddonVersion = '1.1'
IsPaid = True
from OFS.Uninstalled import BrokenClass
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import DuplicateIdError
from Products.CMFNauTools.Utils import loadModules, joinpath
from SiteImage import SiteImage
from Site import SiteContainer, SitesInstaller, SiteContainterType
from NauPublishTool import NauPublisher
type_infos = [
 SiteContainterType]
type_ids = [t['id'] for t in type_infos]

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
    skins.addSkinLayer('sites', 'skin', globals(), after='custom')
    portal.addLocalizerMessages(globals())
    factory = portal.manage_addProduct['CMFNauTools']
    try:
        factory.manage_addTool('NauSite Design Repository Tool', None)
    except DuplicateIdError:
        pass

    try:
        factory.manage_addTool('NauSite Publisher Tool', None)
    except DuplicateIdError:
        pass

    types = getToolByName(portal, 'portal_types')
    for t in type_infos:
        types.addType(t['id'], t)

    fix_sites(portal)
    if not hasattr(portal, 'external'):
        SitesInstaller().install(portal)
    return


def deactivate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.deleteSkinLayer('sites')
    if hasattr(portal, 'portal_site_skins'):
        portal._delObject('portal_site_skins')
    if hasattr(portal, 'portal_publisher'):
        portal._delObject('portal_publisher')
    types = getToolByName(portal, 'portal_types')
    try:
        types.manage_delObjects(type_ids)
    except:
        pass

    return


def fixBrokenState(object):
    object._p_jar.setstate(object)
    return


def fix_sites(portal):
    sites = portal.portal_catalog.searchResults(implements=['isSiteRoot'])
    for site_brains in sites:
        site = site_brains.getObject()
        if not isinstance(site, BrokenClass):
            continue
        container = site.aq_parent
        fixBrokenState(site)
        site = container._upgrade(site_brains['id'], SiteContainer)
        site = container[site_brains['id']]
        container = portal.external[site_brains['id']]
        storage_url = joinpath(site.getPhysicalPath(), site.storage_id)
        container.manage_delObjects('go')
        container.manage_addProduct['CMFNauTools'].manage_addNauPublisher(id='go', internal=storage_url)
        container = container.portal_skins.images
        for object in container.objectValues():
            fixBrokenState(object)
            container._upgrade(object.getId(), SiteImage)

    return
