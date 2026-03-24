# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/InformationalTask.py
# Compiled at: 2005-12-07 18:44:38
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFNauTools import Features
from Products.CMFNauTools.TaskItem import TaskItemBase, TASK_RESULT_SUCCESS
from Products.CMFNauTools.Utils import InitializeClass, parseTime, inheritActions, inheritFTIItems
from DirectiveTask import DirectiveTaskType
InformationalTaskType = {'id': 'information', 'meta_type': 'Informational Task', 'title': 'Information', 'factory_form': 'task_add_form', 'icon': 'taskitem_icon.gif', 'description': '', 'permissions': (CMFCorePermissions.View), 'actions': (inheritActions(DirectiveTaskType)), 'responses': (({'id': 'informed', 'title': 'Informed', 'description': 'Confirm that you have been informed about the document contents', 'progresslist_title': 'User(s) familiarized with the document', 'message': 'You have familiarized with the document', 'url': 'task_response_form', 'handler': 'onInform', 'icon': 'task_user_committed.gif', 'layer': 'involved_users', 'condition': (Expression('python: here.isInvolved(member)'))},) + inheritFTIItems(DirectiveTaskType, 'responses', 'review', 'finalize')), 'results': (inheritFTIItems(DirectiveTaskType, 'results', TASK_RESULT_SUCCESS))}

class InformationalTask(TaskItemBase):
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Informational Task'
    portal_type = 'information'
    security = ClassSecurityInfo()
    mail_user_informed = 'task.info_user_informed'

    def onInform(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_informed')
        isReviewed = self.searchResponses(status='review') or not self.Supervisor()
        if self.isEnabled() and not self.PendingUsers() and not self.isFinalized() and isReviewed:
            self._finalize(TASK_RESULT_SUCCESS)
        return

    def onReview(self, REQUEST=None):
        self.send_mail((self.Creator(),), 'mail_user_reviewed')
        isInformed = reduce((lambda x, y, self=self: x and self.searchResponses(member=y, status='informed')), self.listInvolvedUsers(flatten=True), True)
        if self.isEnabled() and not self.PendingUsers() and not self.isFinalized() and isInformed:
            self._finalize(TASK_RESULT_SUCCESS)
        return

    def onFinalize(self, REQUEST=None, result_code=None):
        notify_list = self.PendingUsers()
        supervisor = self.Supervisor()
        user_who_finalize = _getAuthenticatedUser(self)
        if supervisor and supervisor not in notify_list:
            notify_list.append(supervisor)
        self.send_mail(notify_list, 'mail_finalized', user_who_finalize=user_who_finalize)
        TaskItemBase.onFinalize(self, REQUEST, result_code)
        return


InitializeClass(InformationalTask)

def initialize(context):
    context.registerTaskType(InformationalTask, InformationalTaskType, activate=False)
    return
