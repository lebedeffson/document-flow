# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/MaintenancePack/MembershipTool.py
# Compiled at: 2009-03-10 16:38:45
"""
Membership tool class patch.

$Editor: oevsegneev $
$Id: MembershipTool.py,v 1.2 2009/03/10 13:38:45 oevsegneev Exp $
"""
__version__ = '$Revision: 1.2 $'[11:-2]
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import SentinelError
from Products.CMFNauTools.MembershipTool import MembershipTool
from Products.CMFNauTools.Utils import uniqueValues
from utils import class_patch

class MembershipTool_patch(class_patch):
    """ 
        Portal Membership Tool class patch
    """
    __module__ = __name__
    security = ClassSecurityInfo()

    def switchFolders(self, old_u, new_u):
        old_user = old_u.getId()
        new_user = new_u.getId()
        portal_catalog = getToolByName(self, 'portal_catalog')
        ds = portal_catalog.searchResults(Creator=old_user, implements=['isPrincipiaFolderish', 'isHTMLDocument', 'isAttachment'])
        for db in ds:
            d = db.getObject()
            d.changeOwnership(new_u)

        fs = portal_catalog.searchResults(implements=['isPrincipiaFolderish'])
        for fb in fs:
            f = fb.getObject()
            roles = f.get_local_roles_for_userid(old_user)
            f.delLocalRoles(old_user)
            f.setLocalRoles(new_user, roles)
            f.reindexObject(idxs=['allowedRolesAndUsers', 'Creator'], recursive=1)

        return len(fs)
        return

    def switchTasks(self, old_u, new_u, switch_opened):
        old_user = old_u.getId()
        new_user = new_u.getId()
        portal_catalog = getToolByName(self, 'portal_catalog')
        portal_followup = getToolByName(self, 'portal_followup')
        ref_kw = {}
        if switch_opened:
            ref_kw['isFinalized'] = 0
        tasks = []
        kw = ref_kw.copy()
        kw['InvolvedUsers'] = [old_user]
        ts = portal_followup.searchResults(**kw)
        for tb in ts:
            t = tb.getObject()
            t.involved_users = [_[1] for u in t.involved_users if u != old_user]
            t.involved_users.append(new_user)
            tasks.append(t)

        kw = ref_kw.copy()
        kw['Supervisor'] = old_user
        ts = portal_followup.searchResults(**kw)
        for tb in ts:
            t = tb.getObject()
            t.supervisor = new_user
            tasks.append(t)

        kw = ref_kw.copy()
        kw['Creator'] = old_user
        ts = portal_followup.searchResults(**kw)
        for tb in ts:
            t = tb.getObject()
            t.changeOwnership(new_u)
            t.creator = new_user
            tasks.append(t)

        tasks = uniqueValues(tasks)
        for t in tasks:
            roles = t.get_local_roles_for_userid(old_user)
            t.delLocalRoles(old_user)
            t.setLocalRoles(new_user, roles)
            portal_followup.reindexObject(t, [5, 7, 6, 8, 9])
            portal_catalog.reindexObject(t, ['allowedRolesAndUsers', 'Creator'])
            rs = t.searchResponses(member=old_user)
            if rs:
                ids = [_[1] for r in rs]
                for id in ids:
                    r = t.get_responses().collection[id]
                    r['member'] = new_user
                    t.get_responses().unindexResponse(id)
                    t.get_responses().indexResponse(id, r)

        return len(tasks)
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'switchMember')

    def switchMember(self, old_member, new_member, switch_opened):
        """
        """
        msg = getToolByName(self, 'msg')
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('MaintenancePack'):
            raise SentinelError, msg('sentinel.trial_expired') % msg('Maintenance Pack Addon')
        old_user = self.getMemberById(old_member).getUser()
        new_user = self.getMemberById(new_member).getUser()
        self.switchFolders(old_user, new_user)
        self.switchTasks(old_user, new_user, switch_opened)
        return


def initialize(context):
    MembershipTool_patch(MembershipTool)
    return
