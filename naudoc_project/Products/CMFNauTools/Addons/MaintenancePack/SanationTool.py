# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/MaintenancePack/SanationTool.py
# Compiled at: 2009-03-10 16:38:45
"""
Sanation -- service class for storage maintenance

$Editor: oevsegneev $
$Id: SanationTool.py,v 1.2 2009/03/10 13:38:45 oevsegneev Exp $
"""
__version__ = '$Revision: 1.2 $'[11:-2]
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.ActionInformation import ActionInformation as AI
from Products.CMFNauTools.Exceptions import SentinelError
from Products.CMFNauTools.SimpleObjects import ToolBase, Persistent, ContentBase
from Products.CMFNauTools.Utils import InitializeClass
MAX_I = 5

class SanationTool(ToolBase):
    """
        Storage sanation service class.
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Sanation Tool'
    id = 'portal_sanation'
    security = ClassSecurityInfo()
    _actions = ToolBase._actions + (AI(id='manageSanation', title='Manage Sanation', action=Expression(text='string: ${portal_url}/manage_sanation_form'), category='global', permissions=(CMFCorePermissions.ManagePortal,), visible=1),)
    security.declareProtected(CMFCorePermissions.ManagePortal, 'rebuildCatalogs')

    def rebuildCatalogs(self, ids):
        """
        """
        msg = getToolByName(self, 'msg')
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('MaintenancePack'):
            raise SentinelError, msg('sentinel.trial_expired') % msg('Maintenance Pack Addon')
        if 'portal_catalog' in ids:
            self.rebuildPortalCatalog()
        if 'portal_followup' in ids:
            self.rebuildPortalFollowup()
        return

    def rebuildPortalCatalog(self):
        """
        """

        def fixob(ob, path):
            if ob.__class__.__name__ not in ('VersionsContainer',) and (ob.__class__.__name__ in ('GuardedEntry', 'TabularReport', 'DocflowReport') or ob.implements([5, 6, 7, 8, 9, 10, 11, 12, 13, 14])):
                self.aq_parent.portal_catalog.catalog_object(ob, path)
            return

        portal = self.aq_parent
        catalog = getToolByName(self, 'portal_catalog')
        storage = portal.storage
        catalog._catalog.clear()
        catalog.ZopeFindAndApply(storage, search_sub=1, REQUEST=None, apply_func=fixob, apply_path=storage.physical_path())
        catalog.catalog_object(storage, '/docs/storage')
        for t in portal.followup.getBoundTasks(recursive=1):
            catalog.catalog_object(t, t.physical_path())

        return

    def rebuildPortalFollowup(self):
        """
        """

        def fixob(ob, path):
            if ob.implements(['isTaskItem']):
                self.aq_parent.portal_followup.catalog_object(ob, path)
            return

        portal = self.aq_parent
        catalog = getToolByName(self, 'portal_followup')
        storage = portal.storage
        catalog._catalog.clear()
        catalog.ZopeFindAndApply(storage, search_sub=1, REQUEST=None, apply_func=fixob, apply_path=storage.physical_path())
        for t in portal.followup.getBoundTasks(recursive=1):
            catalog.catalog_object(t, t.physical_path())

        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'refreshCatalogs')

    def refreshCatalogs(self, ids):
        """
        """
        msg = getToolByName(self, 'msg')
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('MaintenancePack'):
            raise SentinelError, msg('sentinel.trial_expired') % msg('Maintenance Pack Addon')
        for id in ids:
            catalog = getToolByName(self, id)
            catalog.refreshCatalog(clear=True, update=True)

        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'cleanFolder')

    def cleanFolder(self, target_uid, date):
        """
        """
        msg = getToolByName(self, 'msg')
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('MaintenancePack'):
            raise SentinelError, msg('sentinel.trial_expired') % msg('Maintenance Pack Addon')
        removed = bad = 0
        catalog = getToolByName(self, 'portal_catalog')
        folder = catalog.getObjectByUid(target_uid)
        linked_objects = []
        kw = {'implements': {'query': 'isPrincipiaFolderish', 'operator': 'not'}}
        docs = [_[1] for doc in folder.listDocuments(**kw)]
        for doc in docs:
            try:
                folder.deleteObjects([doc.getId()])
            except:
                bad += 1
            else:
                removed += 1

        subfolder_brains = catalog.searchResults(parent_path=folder.physical_path(), implements='isPrincipiaFolderish')
        for brain in subfolder_brains:
            linked_objects.extend(self.clearFolder(brain.getObject()))

        return (removed, bad)
        return


InitializeClass(SanationTool)

def initialize(context):
    context.registerTool(SanationTool)
    return
