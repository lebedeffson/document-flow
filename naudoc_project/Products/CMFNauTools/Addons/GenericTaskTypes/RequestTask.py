# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/RequestTask.py
# Compiled at: 2007-10-19 16:35:11
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import _getAuthenticatedUser, getToolByName
from Products.CMFNauTools import Features
from Products.CMFNauTools.TaskItem import TaskItemBase, flattenUsers, TASK_RESULT_SUCCESS, TASK_RESULT_FAILED, TASK_RESULT_CANCELLED
from Products.CMFNauTools.Utils import InitializeClass, parseTime, inheritActions, inheritFTIItems, uniqueValues
from DirectiveTask import DirectiveTaskType
RequestTaskType = {'id': 'request', 'meta_type': 'Request Task', 'title': 'Request', 'description': '', 'icon': 'taskitem_icon.gif', 'factory_form': 'document_confirmation_form', 'condition': "python: here.implements('isDocument')", 'permissions': (CMFCorePermissions.View), 'actions': (inheritActions(DirectiveTaskType)), 'responses': ({'id': 'satisfy', 'title': 'Satisfy request', 'description': 'Satisfy request', 'progresslist_title': 'User(s) satisfied the request', 'message': 'You have satisfied this request', 'url': 'task_response_form', 'handler': 'onSatisfy', 'icon': 'task_user_committed.gif', 'layer': 'involved_users', 'condition': (Expression('python: here.isInvolved(member)'))}, {'id': 'reject', 'title': 'Reject request', 'description': 'Reject request', 'progresslist_title': 'User(s) rejected the request', 'message': 'You have rejected this request', 'url': 'task_response_form', 'handler': 'onReject', 'icon': 'task_user_rejected.gif', 'layer': 'involved_users', 'condition': (Expression('python: here.isInvolved(member)'))}, {'id': 'finalize', 'title': 'Finalize', 'description': 'Finalize request', 'progresslist_title': 'User(s) finalized the request', 'message': 'You have finalized this request', 'url': 'task_finalize_form', 'handler': 'onFinalize', 'layer': 'superusers', 'condition': (Expression('python: here.isCreator(member)'))}), 'results': (({'id': TASK_RESULT_SUCCESS, 'title': 'success', 'disallow_manual': 1},) + inheritFTIItems(DirectiveTaskType, 'results', TASK_RESULT_FAILED, TASK_RESULT_CANCELLED))}

class RequestTask(TaskItemBase):
    """
        Request task type definition.
    """
    __module__ = __name__
    _class_version = 1.0
    __implements__ = (
     Features.createFeature('isRequestTask'), TaskItemBase.__implements__)
    meta_type = 'Request Task'
    portal_type = 'request'
    security = ClassSecurityInfo()
    mail_user_included = 'task.request_user_included'
    mail_user_excluded = 'task.request_user_excluded'
    mail_user_satisfied = 'task.request_satisfied'
    mail_user_rejected = 'task.request_rejected'
    mail_notify_turn = 'task.request_user_turn'
    notification_level = 0

    def __init__(self, id, title, ordered=False, notification_level=0, **kw):
        TaskItemBase.__init__(self, id, title, **kw)
        self.ordered = ordered
        self.notification_level = notification_level
        return

    def notifiedUsers(self, all=False):
        users = [
         self.Creator()]
        if self.Supervisor():
            users.append(self.Supervisor())
        if not all and self.notification_level == 1:
            users.extend(self.listInvolvedUsers(flatten=True))
        users = uniqueValues(users)
        name = _getAuthenticatedUser(self).getUserName()
        if name in users:
            users.remove(name)
        return users
        return

    def onSatisfy(self, REQUEST=None):
        responses = self.searchResponses(member=_getAuthenticatedUser(self).getUserName())
        response = responses and responses[0] or None
        self.send_mail(self.notifiedUsers(), 'mail_user_satisfied', response=response)
        return

    def onReject(self, REQUEST=None):
        self.send_mail(self.notifiedUsers(), 'mail_user_rejected')
        return

    def onFinalize(self, REQUEST=None, result_code=None):
        self.send_mail(self.notifiedUsers(all=True), 'mail_finalized', user_who_finalize=_getAuthenticatedUser(self))
        TaskItemBase.onFinalize(self, REQUEST, result_code)
        return

    def onRespond(self, REQUEST=None, **kw):
        if self.isEnabled() and not self.isFinalized() and (self.getFinalizationMode() == 'auto_any_user' or self.getFinalizationMode() == 'auto_every_user' and not self.PendingUsers()):
            if self.searchResponses(status='reject'):
                code = TASK_RESULT_FAILED
            else:
                code = TASK_RESULT_SUCCESS
            self.onFinalize(REQUEST, code)
            self._finalize(code)
        self.updateIndexes()
        if self.isOrdered():
            if self.searchResponses(status='reject'):
                self._finalize(TASK_RESULT_FAILED)
            self.send_mail(self.PendingUsers(), 'mail_notify_turn')
        return

    def isOrdered(self):
        return getattr(self, 'ordered', False)
        return

    def isEnabled(self):
        return 1
        return

    def PendingUsers(self):
        """ """
        if self.isOrdered():
            membership = getToolByName(self, 'portal_membership')
            involved_users = self.listInvolvedUsers()
            responded_users = self.listRespondedUsers()
            tokens = []
            for name in responded_users:
                user = membership.getMemberById(name)
                if user is None:
                    continue
                tokens.extend(user.listAccessTokens(include_userid=True, include_positions=True, include_divisions=True, include_groups=True, include_roles=False))

            for user in involved_users:
                if user in tokens:
                    continue
                return [
                 user]

        return TaskItemBase.PendingUsers(self)
        return

    def InvolvedUsers(self, **kw):
        """
            Indexing routine.
        """
        if self.isOrdered():
            involved_users = self.listRespondedUsers()
            involved_users.extend(self.PendingUsers())
            return involved_users
        return TaskItemBase.InvolvedUsers(self, **kw)
        return

    def Enable(self, no_mail=None):
        if self.isOrdered() and not no_mail:
            old_involved_users = getattr(self, '_old_involved_users', [])
            pending_users = self.PendingUsers()
            involved_users = self.listInvolvedUsers()
            included_users = [_[1] for u in involved_users if u not in old_involved_users + pending_users]
            excluded_users = [_[1] for u in old_involved_users if u not in involved_users]
            if included_users:
                self.send_mail(flattenUsers(self, included_users), 'mail_user_included', defer=True)
            if excluded_users:
                self.send_mail(flattenUsers(self, excluded_users), 'mail_user_excluded', defer=True)
            old_supervisor = getattr(self, '_old_supervisor', [])
            supervisor = self.Supervisor()
            if supervisor != old_supervisor:
                if old_supervisor:
                    self.send_mail([old_supervisor], 'mail_supervisor_canceled')
                if supervisor:
                    self.send_mail([supervisor], 'mail_supervisor_notify')
            self.send_mail(self.PendingUsers(), 'mail_user_included', defer=False)
            no_mail = True
        return TaskItemBase.Enable(self, no_mail=no_mail)
        return

    def _edit(self, notification_level=None, **kw):
        changes = TaskItemBase._edit(self, **kw)
        if notification_level is not None:
            self.notification_level = notification_level
            changes['notification_level'] = notification_level
        return changes
        return


InitializeClass(RequestTask)
SignatureRequestTaskType = {'id': 'signature_request', 'meta_type': 'Signature Request Task', 'title': 'Signature request', 'description': '', 'icon': 'taskitem_icon.gif', 'factory_form': 'document_confirmation_form', 'condition': "python: here.implements('isDocument')", 'permissions': (CMFCorePermissions.View), 'actions': (inheritActions(DirectiveTaskType)), 'responses': ({'id': 'sign', 'title': 'Sign', 'description': 'Sign the document', 'progresslist_title': 'User(s) signed the document', 'message': 'You have signed the document', 'url': 'task_response_form', 'handler': 'onSatisfy', 'icon': 'task_user_committed.gif', 'layer': 'involved_users', 'condition': 'python: here.isInvolved(member)'}, {'id': 'reject', 'title': 'Reject signature request', 'description': 'Reject signature request', 'progresslist_title': 'User(s) rejected to sign', 'message': 'You have rejected to sign', 'url': 'task_response_form', 'handler': 'onReject', 'icon': 'task_user_rejected.gif', 'layer': 'involved_users', 'condition': 'python: here.isInvolved(member)'}, {'id': 'finalize', 'title': 'Finalize', 'description': 'Finalize request', 'progresslist_title': 'User(s) finalized the request', 'message': 'You have finalized this request', 'url': 'task_finalize_form', 'handler': 'onFinalize', 'layer': 'superusers', 'condition': 'python: here.isCreator(member)'}), 'results': ({'id': TASK_RESULT_SUCCESS, 'title': 'document signed', 'disallow_manual': 1}, {'id': TASK_RESULT_FAILED, 'title': 'document was not signed', 'disallow_manual': 1}, {'id': TASK_RESULT_CANCELLED, 'title': 'cancelled'})}

class SignatureRequestTask(RequestTask):
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Signature Request Task'
    portal_type = 'signature_request'


InitializeClass(SignatureRequestTask)

def initialize(context):
    context.registerTaskType(RequestTask, RequestTaskType, activate=False)
    context.registerTaskType(SignatureRequestTask, SignatureRequestTaskType, activate=False)
    return
