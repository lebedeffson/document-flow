# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/LDAP/__init__.py
# Compiled at: 2008-12-05 14:22:33
"""
LDAP add-on initialization script.

$Editor: oevsegneev $
$Id: __init__.py,v 1.1 2008/12/05 11:22:33 oevsegneev Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
AddonId = 'LDAP'
AddonTitle = 'LDAP Integration'
AddonVersion = '1.0'
IsPaid = True
from OFS.Uninstalled import BrokenClass
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import Config
from Products.CMFNauTools.Exceptions import DuplicateIdError
from Products.CMFNauTools.Utils import loadModules
from utils import registerAction, unregisterAction

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True, is_paid=IsPaid)
    registerDirectory('skin', globals())
    for module in loadModules(package='Addons.%s' % AddonId).values():
        if module == 'LDAPUserFolder' and Config.UseLDAPUserFolder:
            init_func = getattr(module, 'initialize', None)
            if callable(init_func):
                init_func(context)

    return


def activate(portal):
    portal_sentinel = getToolByName(portal, 'portal_sentinel')
    if not portal_sentinel.checkActivation(AddonId):
        return False
    skins = getToolByName(portal, 'portal_skins')
    skins.addSkinLayer('ldap', 'skin', globals(), after='custom')
    portal.addLocalizerMessages(globals())
    registerAction(getToolByName(portal, 'portal_membership', None), id='manageLDAP', title='LDAP settings', description='LDAP settings', form='manage_ldap_form', category='global', visible=Config.UseLDAPUserFolder)
    return


def deactivate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.deleteSkinLayer('ldap')
    unregisterAction(getToolByName(portal, 'portal_membership', None), 'manageLDAP')
    return
