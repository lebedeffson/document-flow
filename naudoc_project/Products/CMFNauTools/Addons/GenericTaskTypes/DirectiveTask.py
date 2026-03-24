# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/DirectiveTask.py
# Compiled at: 2008-07-28 16:45:16
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFNauTools import Features
from Products.CMFNauTools.TaskItem import TaskItemBase, TASK_RESULT_SUCCESS, TASK_RESULT_FAILED, TASK_RESULT_CANCELLED
from Products.CMFNauTools.Utils import InitializeClass, getToolByName
DirectiveTaskType = {'id': 'directive', 'meta_type': 'Directive Task', 'title': 'Directive', 'icon': 'taskitem_icon.gif', 'factory_form': 'task_add_form', 'permissions': (CMFCorePermissions.View), 'actions': ({'id': 'view', 'name': 'View', 'action': 'task_view', 'permissions': (CMFCorePermissions.View,)}, {'id': 'edit', 'name': 'Change settings', 'action': 'task_edit_form', 'condition': 'python: object.isCreator()', 'permissions': (CMFCorePermissions.View,)}), 'responses': ({'id': 'commit', 'title': 'Commit task', 'description': 'Commit task', 'progresslist_title': 'User(s) committed to a task', 'message': 'You have committed to this task', 'url': 'task_response_form', 'handler': 'onCommit', 'icon': 'task_user_committed.gif', 'layer': 'involved_users', 'manual_report_close': 1, 'condition': (Expression("python: here.isInvolved(member) and not here.searchResponses(member=mates, status='reject')"))}, {'id': 'failure', 'title': 'Report task failure', 'description': 'Report task failure', 'progresslist_title': 'User(s) failed to commit task', 'message': 'You have failed to commit this task', 'url': 'task_response_form', 'handler': 'onFailure', 'icon': 'task_user_rejected.gif', 'layer': 'involved_users', 'manual_report_close': 1, 'condition': (Expression("python: here.isInvolved(member) and here.searchResponses(member=mates) and not here.searchResponses(member=mates, status='reject')"))}, {'id': 'task_start', 'title': 'Accept task', 'description': '', 'progresslist_title': 'User(s) accepted the task', 'message': 'You have accepted this task', 'url': 'task_response_form', 'handler': 'onAccept', 'icon': 'task_user_accepted.gif', 'layer': 'startpad', 'condition': (Expression("python: here.isInvolved(member) and not (here.searchResponses(member=mates, layer='startpad') or here.searchResponses(member=mates, layer='involved_users'))"))}, {'id': 'reject', 'title': 'Reject task', 'description': 'Reject task', 'progresslist_title': 'User(s) rejected a task', 'message': 'You have rejected this task', 'url': 'task_response_form', 'handler': 'onReject', 'icon': 'task_user_rejected.gif', 'layer': 'startpad', 'condition': (Expression("python: here.isInvolved(member) and not (here.searchResponses(member=mates, layer='startpad') or here.searchResponses(member=mates, layer='involved_users'))"))}, {'id': 'review', 'title': 'Review', 'description': 'Review task', 'progresslist_title': 'User(s) reviewed a task', 'message': 'You have reviewed this task', 'url': 'task_response_form', 'handler': 'onReview', 'layer': 'reviewers', 'condition': (Expression('python: here.isSupervisor(member)'))}, {'id': 'finalize', 'title': 'Finalize', 'description': 'Finalize task', 'progresslist_title': 'User(s) finalized a task', 'message': 'You have finalized this task', 'url': 'task_finalize_form', 'handler': 'onFinalize', 'layer': 'superusers', 'condition': (Expression('python: here.isCreator(member)'))}), 'results': ({'id': TASK_RESULT_SUCCESS, 'title': 'success'}, {'id': TASK_RESULT_CANCELLED, 'title': 'cancelled'}, {'id': TASK_RESULT_FAILED, 'title': 'failed'})}

class DirectiveTask(TaskItemBase):
    """
      Directive task type definition

      Directive is an imperative task given by the leader to it's subordinates.
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Directive Task'
    portal_type = 'directive'
    __implements__ = (
     Features.createFeature('isDirectiveTask'), TaskItemBase.__implements__)
    security = ClassSecurityInfo()
    mail_user_committed = 'task.directive_committed'
    mail_user_rejected = 'task.directive_rejected'
    mail_user_failed = 'task.directive_failed'
    mail_user_accepted = 'task.directive_accepted'

    def __init__(self, id, title, plan_time, **kw):
        TaskItemBase.__init__(self, id, title, **kw)
        self.setPlanTime(plan_time)
        return

    def onAccept(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_accepted')
        return

    def onRespond(self, REQUEST=None, **kw):
        try:
            actual_time = REQUEST['actual_time']
        except KeyError:
            pass
        else:
            name = _getAuthenticatedUser(self).getUserName()
            self.setActualTimeFor(name, actual_time)

        if not self.isFinalized() and kw['close_report'] and (self.getFinalizationMode() == 'auto_any_user' or self.getFinalizationMode() == 'auto_every_user' and self.isClosed()):
            if self.searchResponses(status=['reject', 'failure']):
                code = TASK_RESULT_FAILED
            else:
                code = TASK_RESULT_SUCCESS
            self.Finalize(code, Trust)
        else:
            portal_workflow = getToolByName(self, 'portal_workflow')
            portal_workflow.onRespond(self)
        return

    def onCommit(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_committed')
        return

    def onReject(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_rejected')
        return

    def onFailure(self, REQUEST=None):
        self.send_mail((self.Creator(), self.Supervisor()), 'mail_user_failed')
        return

    def onReview(self, REQUEST=None):
        self.send_mail((self.Creator(),), 'mail_user_reviewed')
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

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setPlanTime')

    def setPlanTime(self, time):
        """
            Sets the time required to accomplish with the task as it was planned by the task author.

            Arguments:

                'time' -- Integer. Planned time in seconds.
        """
        self.plan_time = time
        return

    security.declareProtected(CMFCorePermissions.View, 'getPlanTime')

    def getPlanTime(self):
        """
            Returns the time required to accomplish with the task as it was planned by the task author.

            Result:

              'time' -- Integer. Planned time in seconds.
        """
        return self.plan_time
        return

    security.declarePrivate('setActualTimeFor')

    def setActualTimeFor(self, uname, time):
        """
           Sets the time actual required to accomplish with the task as it was reported by the involved user.

           Arguments:

               'uname' -- User id string.

               'time' -- Integer. Planned time in seconds.
        """
        self.actual_times[uname] = time
        return

    security.declareProtected(CMFCorePermissions.View, 'getActualTimeFor')

    def getActualTimeFor(self, uname):
        """
            Returns the actual time required to accomplish with the task as it was reported by the involved user.

            Result:

                'time' -- Integer. Planned time in seconds.
        """
        return self.actual_times.get(uname, None)
        return

    def _edit(self, plan_time=None, **kw):
        changes = TaskItemBase._edit(self, **kw)
        if plan_time is not None:
            self.setPlanTime(plan_time)
            changes['plan_time'] = plan_time
        return changes
        return


InitializeClass(DirectiveTask)

def initialize(context):
    context.registerTaskType(DirectiveTask, DirectiveTaskType, activate=False)
    return
