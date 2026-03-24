# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/ElaboratedTask.py
# Compiled at: 2006-07-13 14:00:40
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFNauTools import Features
from Products.CMFNauTools.TaskItem import TaskItemBase
from Products.CMFNauTools.Utils import InitializeClass, parseTime, inheritActions, inheritFTIItems, uniqueValues
from DirectiveTask import DirectiveTaskType
ElaboratedTaskType = {'id': 'elaborated', 'meta_type': 'Elaborated Task', 'title': 'Elaborated', 'description': '', 'disallow_manual': 1, 'icon': 'taskitem_icon.gif', 'permissions': (CMFCorePermissions.View), 'actions': (inheritActions(DirectiveTaskType, 'view') + ({'id': 'edit', 'name': 'Change settings', 'action': 'task_elaborate', 'condition': 'python: object.isCreator()', 'permissions': (CMFCorePermissions.View,)},)), 'responses': (inheritFTIItems(DirectiveTaskType, 'responses', 'finalize')), 'results': (inheritFTIItems(DirectiveTaskType, 'results'))}

class ElaboratedTask(TaskItemBase):
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Elaborated Task'
    portal_type = 'elaborated'
    security = ClassSecurityInfo()
    __implements__ = (
     Features.createFeature('isElaboratedTask'), TaskItemBase.__implements__)

    def __init__(self, id, title, items, **kw):
        TaskItemBase.__init__(self, id, title, **kw)
        self.items = items
        return

    def listInvolvedUsers(self, **kw):
        results = []
        for task in self.followup.getBoundTasks():
            results.extend(task.listInvolvedUsers(**kw))

        return uniqueValues(results)
        return

    def listResponseTypes(self):
        results = []
        for task in self.followup.getBoundTasks():
            results.extend(task.listResponseTypes())

        return uniqueValues(results)
        return

    def PendingUsers(self):
        return []
        return

    def canSendNotifications(self):
        return False
        return

    def _edit(self, items=None, **kw):
        changes = TaskItemBase._edit(self, **kw)
        if items is not None:
            self.elaborate(items)
        return changes
        return

    def getFinalizationMode(self):
        return 'manual_creator'
        return

    def elaborate(self, items):
        ids = []
        for (i, item) in enumerate(items):
            params = {'description': (item.get('description')), 'involved_users': (item.get('involved_users')), 'expiration_date': (item.get('expiration_date')), 'duration': (item.get('duration'))}
            brains_type = item.get('brains_type', 'directive')
            if brains_type == 'directive':
                params['plan_time'] = 0
            id = item.get('id')
            if id:
                try:
                    task = self.getTask(id)
                except KeyError:
                    continue
                else:
                    task.edit(**params)
            else:
                title = '%s (%s %d)' % (self.Title(), self.msg('item'), i + 1)
                id = self.followup.createTask(title=title, finalization_mode=self.getFinalizationMode(), type=brains_type, **params)
            ids.append(id)

        for id in self.followup.getBoundTaskIds():
            if id in ids:
                continue
            self.followup.deleteTask(id)

        return

    def searchResponses(self, **kw):
        results = []
        for task in self.followup.getBoundTasks():
            results.extend(task.searchResponses(**kw))

        return results
        return

    def _instance_onCreate(self):
        self.elaborate(self.items)
        return


InitializeClass(ElaboratedTask)

def initialize(context):
    context.registerTaskType(ElaboratedTask, ElaboratedTaskType, activate=False)
    return
