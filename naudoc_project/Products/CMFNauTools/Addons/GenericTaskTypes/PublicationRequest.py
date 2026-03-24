# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/PublicationRequest.py
# Compiled at: 2007-10-19 16:35:11
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import _getAuthenticatedUser, getToolByName
from Products.CMFNauTools import Features
from Products.CMFNauTools.TaskItem import TaskItemBase, TASK_RESULT_SUCCESS, TASK_RESULT_FAILED, TASK_RESULT_CANCELLED
from Products.CMFNauTools.Utils import InitializeClass, parseTime, inheritActions, inheritFTIItems
from DirectiveTask import DirectiveTaskType
from RequestTask import RequestTask
PublicationRequestTaskType = {'id': 'publication_request', 'meta_type': 'Publication Request Task', 'title': 'Publication request', 'description': '', 'icon': 'taskitem_icon.gif', 'factory_form': 'document_confirmation_form', 'condition': "python: here.implements('isDocument') and here.hasBase('SimplePublication')", 'permissions': (CMFCorePermissions.View), 'actions': (inheritActions(DirectiveTaskType)), 'responses': ({'id': 'publish', 'title': 'Publish', 'description': 'Publish the document', 'progresslist_title': 'User(s) published the document', 'message': 'You have published the document', 'url': 'task_response_form', 'handler': 'onSatisfy', 'icon': 'task_user_committed.gif', 'layer': 'involved_users', 'condition': (Expression('python: here.isInvolved(member)'))}, {'id': 'reject', 'title': 'Reject publication request', 'description': 'Reject publication request', 'progresslist_title': 'User(s) rejected the publication', 'message': 'You have rejected the publication', 'url': 'task_response_form', 'handler': 'onReject', 'icon': 'task_user_rejected.gif', 'layer': 'involved_users', 'condition': (Expression('python: here.isInvolved(member)'))}, {'id': 'finalize', 'title': 'Finalize', 'description': 'Finalize request', 'progresslist_title': 'User(s) finalized the request', 'message': 'You have finalized this request', 'url': 'task_finalize_form', 'handler': 'onFinalize', 'layer': 'superusers', 'condition': (Expression('python: here.isCreator(member)'))}), 'results': ({'id': TASK_RESULT_SUCCESS, 'title': 'document published', 'disallow_manual': 1}, {'id': TASK_RESULT_FAILED, 'title': 'publication rejected', 'disallow_manual': 1}, {'id': TASK_RESULT_CANCELLED, 'title': 'cancelled'})}

class PublicationRequestTask(RequestTask):
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Publication Request Task'
    portal_type = 'publication_request'
    security = ClassSecurityInfo()

    def onSatisfy(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_satisfied')
        return

    def onReject(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_rejected')
        self._finalize(TASK_RESULT_FAILED)
        return

    def onFinalize(self, REQUEST=None, result_code=None):
        self.doWorkflowAction('evolve', REQUEST.get('text'))
        RequestTask.onFinalize(self, REQUEST, result_code)
        return

    def onRespond(self, REQUEST=None, **kw):
        if self.isEnabled() and not self.PendingUsers() and not self.isFinalized():
            root = self.findRootTask()
            portal_followup = getToolByName(self, 'portal_followup')
            logger = portal_followup.getLogger()
            logger.delSeenByFor(root)
            text = self.REQUEST.get('text')
            if self.searchResponses(status='reject'):
                code = TASK_RESULT_FAILED
                self.findRootTask()._finalize(code)
                for task_id in self.listFollowupTasks():
                    task = self.getTask(task_id)
                    if not task.isFinalized():
                        task._finalize(result_code=TASK_RESULT_CANCELLED)

            else:
                code = TASK_RESULT_SUCCESS
                base = self.getBase()
                user_id = _getAuthenticatedUser(self).getUserName()
                roles = list(base.get_local_roles_for_userid(user_id))
                base.manage_setLocalRoles(user_id, ['Editor'])
                self.doWorkflowAction('publish', text)
                roles and base.manage_setLocalRoles(user_id, roles) or base.manage_delLocalRoles((user_id,))
                self.findRootTask()._finalize(code)
            self._finalize(code)
        TaskItemBase.onRespond(self, REQUEST, **kw)
        return

    def doWorkflowAction(self, action, comment):
        workflow = getToolByName(self, 'portal_workflow')
        try:
            workflow.doActionFor(self.getBase(), action, comment=comment)
        except:
            pass

        return


InitializeClass(PublicationRequestTask)

def initialize(context):
    context.registerTaskType(PublicationRequestTask, PublicationRequestTaskType, activate=False)
    return
