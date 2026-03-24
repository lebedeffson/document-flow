# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/ModificationTask.py
# Compiled at: 2006-04-27 13:18:13
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFNauTools import Features
from Products.CMFNauTools.TaskItem import TaskItemBase, TASK_RESULT_SUCCESS, TASK_RESULT_FAILED, TASK_RESULT_CANCELLED
from Products.CMFNauTools.Utils import InitializeClass, parseTime, inheritActions, inheritFTIItems
from DirectiveTask import DirectiveTaskType
ModificationTaskType = {'id': 'modification', 'meta_type': 'Modification Task', 'title': 'Modification request', 'description': '', 'icon': 'taskitem_icon.gif', 'factory_form': 'modification_add_form', 'condition': "python: here.implements('isDocument') and here.hasBase ('NormativeDocument')", 'permissions': (CMFCorePermissions.View), 'actions': (inheritActions(DirectiveTaskType)), 'responses': ({'id': 'commit', 'title': 'Accept', 'description': 'Accept', 'progresslist_title': 'User(s) committed to a task', 'message': 'You have committed to this task', 'url': 'task_response_form', 'handler': 'onCommit', 'icon': 'task_user_committed.gif', 'layer': 'startpad', 'condition': (Expression('python: here.isInvolved(member)'))}, {'id': 'reject', 'title': 'Decline', 'description': 'Decline', 'progresslist_title': 'User(s) rejected a task', 'message': 'You have rejected this task', 'url': 'task_response_form', 'handler': 'onReject', 'icon': 'task_user_rejected.gif', 'layer': 'startpad', 'condition': (Expression('python: here.isInvolved(member)'))}, {'id': 'finalize', 'title': 'Finalize', 'description': 'Finalize task', 'progresslist_title': 'User(s) finalized a task', 'message': 'You have finalized this task', 'url': 'task_finalize_form', 'handler': 'onFinalize', 'layer': 'superusers', 'condition': (Expression('python: here.isSupervisor(member)'))}, {'id': 'cancel', 'title': 'Cancel request', 'description': 'Cancel request', 'progresslist_title': 'User(s) cancelled a task', 'message': 'You have cancelled this task', 'url': 'task_response_form', 'handler': 'onCancel', 'layer': 'superusers', 'condition': (Expression('python: here.isCreator(member)'))}), 'results': (inheritFTIItems(DirectiveTaskType, 'results', TASK_RESULT_SUCCESS, TASK_RESULT_CANCELLED))}

class ModificationTask(TaskItemBase):
    """
        Modification Request
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Modification Task'
    portal_type = 'modification'
    security = ClassSecurityInfo()
    mail_user_committed = 'task.directive_committed'
    mail_user_rejected = 'task.directive_rejected'
    mail_user_failed = 'task.directive_failed'
    mail_user_accepted = 'task.directive_accepted'

    def onCommit(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_committed')
        return

    def onReject(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_rejected')
        return

    def onFinalize(self, REQUEST=None, result_code=None):
        notify_list = self.listInvolvedUsers(flatten=True)
        supervisor = self.Supervisor()
        user_who_finalize = _getAuthenticatedUser(self)
        if supervisor and supervisor not in notify_list:
            notify_list.append(supervisor)
        self.send_mail(notify_list, 'mail_finalized', user_who_finalize=user_who_finalize)
        TaskItemBase.onFinalize(self, REQUEST, result_code)
        return

    def onCancel(self, REQUEST=None):
        result_code = 'cancelled'
        notify_list = self.listInvolvedUsers(flatten=True)
        supervisor = self.Supervisor()
        user_who_finalize = _getAuthenticatedUser(self)
        if supervisor and supervisor not in notify_list:
            notify_list.append(supervisor)
        self.send_mail(notify_list, 'mail_finalized', user_who_finalize=user_who_finalize)
        TaskItemBase.onFinalize(self, REQUEST, result_code)
        return


InitializeClass(ModificationTask)

def initialize(context):
    context.registerTaskType(ModificationTask, ModificationTaskType, activate=False)
    return
