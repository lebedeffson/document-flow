# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/RecurrentTask.py
# Compiled at: 2007-07-23 11:40:43
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import Features
from Products.CMFNauTools.TaskItem import TaskItemBase
from Products.CMFNauTools.Utils import InitializeClass, parseTime, inheritActions, inheritFTIItems
from Products.NauScheduler.TemporalExpressions import TemporalExpression
from DirectiveTask import DirectiveTaskType
RecurrentTaskType = {'id': 'recurrent', 'meta_type': 'Recurrent Task', 'title': 'Recurrent', 'icon': 'taskitem_icon.gif', 'description': '', 'disallow_manual': 1, 'permissions': (CMFCorePermissions.View), 'actions': (inheritActions(DirectiveTaskType)), 'responses': (inheritFTIItems(DirectiveTaskType, 'responses', 'finalize')), 'results': (inheritFTIItems(DirectiveTaskType, 'results'))}

class RecurrentTask(TaskItemBase):
    __module__ = __name__
    _class_version = 1.0
    __implements__ = (
     Features.createFeature('isRecurrentTask'), TaskItemBase.__implements__)
    meta_type = 'Recurrent Task'
    portal_type = 'recurrent'
    security = ClassSecurityInfo()
    recurrent_type = 'directive'

    def __init__(self, id, title, recurrent_type, temporal_expr, duration, **kw):
        if not duration:
            raise ValueError, 'Duration time is required for reccurent tasks.'
        TaskItemBase.__init__(self, id, title, duration=duration, **kw)
        self.temporal_expr = temporal_expr
        self.duration = duration
        self.recurrent_type = recurrent_type
        return

    def PendingUsers(self):
        return []
        return

    def InvolvedUsers(self):
        return []
        return

    security.declareProtected(CMFCorePermissions.View, 'getSchedule')

    def getSchedule(self):
        """
            Returns schedule element associated with the task.
        """
        scheduler = getToolByName(self, 'portal_scheduler', None)
        element_id = self._task_schedule_id
        if scheduler is not None and element_id:
            return scheduler.getScheduleElement(element_id)
        return None
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setSchedule')

    def setSchedule(self, temporal_expr, duration):
        """
            Sets up the periodical task schedule

            Arguments:

                'temporal_expr' --

                'duration' -- Integer. Event duration in seconds.
        """
        if not isinstance(temporal_expr, TemporalExpression):
            raise ValueError, temporal_expr
        self.temporal_expr = temporal_expr
        self.duration = duration
        self.plan_time = duration
        scheduler = getToolByName(self, 'portal_scheduler', None)
        element_id = self._task_schedule_id
        if scheduler is not None and element_id:
            scheduler.delScheduleElement(element_id)
        kwargs = {'title': (self.Title()), 'description': (self.Description()), 'creator': (self.Creator()), 'involved_users': (self.involved_users), 'duration': (self.duration), 'bind_to': (self.getId()), 'alarm_settings': (self.alarm_settings), 'type': (self.recurrent_type)}
        if self.recurrent_type == 'directive':
            kwargs['plan_time'] = self.plan_time
        self._task_schedule_id = scheduler.addScheduleElement(self.createTask, temporal_expr=self.temporal_expr, title=self.Title(), kwargs=kwargs)
        return

    security.declarePrivate('resetSchedule')

    def resetSchedule(self):
        """
            Restarts all recurrent events associated with the task.
        """
        TaskItemBase.resetSchedule(self)
        self.setSchedule(self.temporal_expr, self.duration)
        return

    def _edit(self, duration=None, temporal_expr=None, **kw):
        changes = TaskItemBase._edit(self, **kw)
        if temporal_expr or duration:
            if not temporal_expr:
                temporal_expr = self.temporal_expr
            elif temporal_expr != self.temporal_expr:
                changes['task_te'] = temporal_expr
            if not duration:
                duration = self.duration
            elif duration != self.duration:
                changes['task_duration'] = duration
            self.setSchedule(temporal_expr, duration)
        return changes
        return

    def listAllowedResponseTypes(self, uname=None):
        return []
        return

    def canSendNotifications(self):
        return False
        return


InitializeClass(RecurrentTask)

def initialize(context):
    context.registerTaskType(RecurrentTask, RecurrentTaskType, activate=False)
    return
