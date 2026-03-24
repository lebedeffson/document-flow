# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DigitalSignature/HTMLDocument.py
# Compiled at: 2008-10-22 13:21:33
"""
Patch of HTMLDocument class.

$Editor: oevsegneev $
$Id: HTMLDocument.py,v 1.4 2008/10/22 09:21:33 oevsegneev Exp $
"""
__version__ = '$Revision: 1.4 $'[11:-2]
from Acquisition import aq_get
from ZODB.PersistentList import PersistentList
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.CMFNauTools.HTMLDocument import HTMLDocument
from utils import class_patch

class HTMLDocument_patch(class_patch):
    """
        Patch of subclassed Document type
    """
    __module__ = __name__
    security = ClassSecurityInfo()

    def listTabs(self):
        tabs = self.old_listTabs()
        REQUEST = aq_get(self, 'REQUEST')
        msg = getToolByName(self, 'msg')
        append_tab = tabs.append
        type = self.getTypeInfo()
        link = REQUEST.get('link', '')
        action = type.getActionById('signatures', None)
        if not action:
            return tabs
        signatureCounts = len(self.getSignatures())
        append_tab({'url': (self.relative_url(action=action, frame='inFrame')), 'title': (msg('ds.signatures') + ' (' + (msg('n/a'), str(signatureCounts))[signatureCounts > 0] + ')')})
        if link.find(action) >= 0:
            tabs[-1]['selected'] = True
            tabs[-1]['selected_color'] = '#ffffff'
        return tabs
        return

    security.declareProtected(CMFCorePermissions.View, 'getSignatures')

    def getSignatures(self, task_id=None):
        """
            Returns list of signatures
        """
        if task_id:
            return [_[1] for s in self._signatures if task_id == s['task_id']]
        else:
            return [_[1] for s in self._signatures if not s['task_id']]
        return

    security.declareProtected(CMFCorePermissions.View, 'getSignature')

    def getSignature(self, task_id=None, response_id=None):
        """
            Returns list of signatures for tasks
        """
        for s in self._signatures:
            if s['task_id'] == task_id and s['response_id'] == response_id:
                return s

        return None
        return

    security.declareProtected(CMFCorePermissions.View, 'addSignature')

    def addSignature(self, signature=None, task=None, response_id=None):
        """
            Add new signature
        """
        action = 'document_signatures_form'
        redirect = self.redirect
        task_id = task and task.getId()
        if task:
            action = None
            redirect = task.redirect
        msg = getToolByName(self, 'msg')
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('DigitalSignature'):
            return redirect(action=action, message=msg('sentinel.trial_expired') % msg('Digital Signature'))
        if signature is None:
            signature = self.REQUEST.get('sign_cont', '')
        if not signature:
            return redirect(action=action, message=msg('ds.error.on_signing'))
        member = getToolByName(self, 'portal_membership').getAuthenticatedMember()
        certificate = member.getProperty('ds_certificate')
        new_signature = {'certificate': certificate, 'signature': signature, 'member_id': (member.getId()), 'date': (DateTime()), 'task_id': task_id, 'response_id': response_id}
        if not self._signatures:
            self._signatures = PersistentList()
        if not task_id:
            for i in range(len(self._signatures)):
                if not self._signatures[i]['task_id'] and self._signatures[i]['certificate'] == certificate:
                    self._signatures[i] = new_signature
                    return redirect(action=action, message=msg('ds.sign_added'))

        self._signatures.append(new_signature)
        return redirect(action=action, message=msg('ds.sign_added'))
        return


def initialize(context):
    HTMLDocument_patch(HTMLDocument, versionable_methods=('listTabs', 'getSignatures', 'addSignature', 'getSignature'), versionable_attrs=('_signatures',))
    return
