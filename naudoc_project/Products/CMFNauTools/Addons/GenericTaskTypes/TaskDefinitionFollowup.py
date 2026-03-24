# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/TaskDefinitionFollowup.py
# Compiled at: 2009-01-12 17:43:29
"""

  TaskDefinitionFollowup classes

  It consist of:
    -- model (TaskDefinitionFollowup)
    -- controller (TaskDefinitionControllerFollowup)
    -- view (TaskDefinitionFormFollowup)
    -- register (TaskDefinitionRegistryFollowup)

  They are inherited from appropriated TaskDefinitionAbstract classes

  Them provide functions for create action templates for task creation.

$Editor: inemihin $
$Id: TaskDefinitionFollowup.py,v 1.15 2009/01/12 14:43:29 oevsegneev Exp $
"""
from DateTime import DateTime
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.DFRoleManager import DFRoleManager
from Products.CMFNauTools.TaskDefinitionAbstract import TaskDefinition
from Products.CMFNauTools.TaskDefinitionAbstract import TaskDefinitionForm
from Products.CMFNauTools.TaskDefinitionAbstract import TaskDefinitionController
from Products.CMFNauTools.TaskDefinitionAbstract import TaskDefinitionRegistry
from Products.CMFNauTools.TaskItem import flattenUsers
from Products.CMFNauTools.Utils import InitializeClass, parseDateTime

class TaskDefinitionFollowup(TaskDefinition):
    """
      Class-model.

      Store fields needed for createTask method:
        -- task_brains - id of task's brains (see TaskBrains.py)
        -- title - task's title
        -- involved_users - involved to task users
        -- supervisor - task's supervisor
        -- duration_time - duration_time for create expiration date
        -- description - task's description

      Based on this fields in 'activate' method will be maden task.

    """
    __module__ = __name__
    _class_version = 1.04
    task_brains = ''
    title = ''
    involved_users = []
    duration_time = 0
    description = ''
    finalization_mode = 'manual_creator'
    notification_level = 0
    _full_userlist = 0
    confirm_by_turn = 0
    supervisor_user = ''
    alarm_settings = None

    def __init__(self, task_brains=''):
        TaskDefinition.__init__(self)
        self.task_brains = task_brains
        self.type = 'followup_' + self.task_brains
        return

    def toArray(self):
        """
          Converting object's fields to dictionary

          Result:

            Dictionary as { 'field_name': 'field_value', ... }

        """
        arr = TaskDefinition.toArray(self)
        arr['title'] = self.title
        arr['involved_users'] = self.involved_users
        arr['duration_time'] = self.duration_time
        arr['description'] = self.description
        arr['supervisor_user'] = self.supervisor_user
        arr['_full_userlist'] = self._full_userlist
        arr['confirm_by_turn'] = self.confirm_by_turn
        arr['finalization_mode'] = self.finalization_mode
        arr['notification_level'] = self.notification_level
        arr['alarm_settings'] = self.alarm_settings
        return arr
        return

    def changeTo(self, taskDefinition):
        """
          Changes object's values to news

          Arguments:

            'taskDefinition' -- object to values of which need to change self

        """
        TaskDefinition.changeTo(self, taskDefinition)
        self.title = taskDefinition.title
        self.involved_users = taskDefinition.involved_users
        self.supervisor_user = taskDefinition.supervisor_user
        self.duration_time = taskDefinition.duration_time
        self.description = taskDefinition.description
        self._allow_edit = taskDefinition._allow_edit
        self._full_userlist = taskDefinition._full_userlist
        self.confirm_by_turn = taskDefinition.confirm_by_turn
        self.finalization_mode = taskDefinition.finalization_mode
        self.notification_level = taskDefinition.notification_level
        self.alarm_settings = taskDefinition.alarm_settings
        return

    def getResultCodes(self):
        """
          Returns result codes of task which will be maded based on
          this template.

          Asked information from task's brains

          Result:

            >>>return = (
            >>>    { 'id': 'result_code1', 'title': 'title_result_code1' },
            >>>     ...
            >>> )
        """
        followup = getToolByName(self, 'portal_followup')
        task_type = followup.getTaskType(self.task_brains)
        finalization_codes = task_type.listResults()
        return finalization_codes
        return

    def activate(self, object, context, transition):
        """
            Create task to specific object, with fields from template's values

           Arguments:

              'object' -- object for which task will be maden (generally HTMLDocument)

              'context' -- common actions context - dictionary, if this action template
                         are included, otherwise dictionary have key 'task_template_id'
                         which have id of task_template, this attribute are stored to task

            Result:

              Dictionary, have key 'task_id' - result of execution method
              TaskItemcontainer.createTask(), this needed to included action templates
              (if exists), to 'bind' task to this task.

        """
        self.loadParams(context, object)
        if self.amIonTop():
            task_template_id = context['task_template_id']
            bind_to = None
        else:
            task_template_id = None
            bind_to = context['task_id']
        membership = getToolByName(self, 'portal_membership')
        involved_users = self._getField('involved_users')
        if not involved_users:
            return
        r = []
        role_manager = DFRoleManager(object, context=self)
        for value in involved_users:
            if value.startswith('role:'):
                r.extend(role_manager.getUsersByRole(value[5:]))
            else:
                r.append(value)

        involved_users = r
        self.saveParams(context)
        alarm_settings = self._getAlarmSettings()
        params = {'title': (self._getField('title')), 'description': (self._getField('description')), 'involved_users': involved_users, 'supervisor': (self._getSupervisor(object)), 'type': (self.task_brains), 'expiration_date': (self._getExpirationDate()), 'task_template_id': task_template_id, 'alarm_settings': (alarm_settings or self.alarm_settings), 'bind_to': bind_to, 'finalization_mode': (self.finalization_mode)}
        ordered = self._getField('confirm_by_turn')
        if ordered:
            params['ordered'] = ordered
        notification_level = self._getField('notification_level')
        if notification_level:
            params['notification_level'] = notification_level
        if self.task_brains == 'directive':
            params['plan_time'] = 0
        task_id = object.followup.createTask(**params)
        context['task_id'] = task_id
        return

    def _getExpirationDate(self):
        """
            Returns expiration date by current date and duration_time

            Result:

              Instance on DateTime
        """
        duration_time = self._getField('duration_time')
        return DateTime(float(DateTime().timeTime() + duration_time))
        return

    def _getSupervisor(self, object):
        supervisor_user_id = self._getField('supervisor_user')
        if supervisor_user_id.startswith('role:'):
            RM = DFRoleManager(object, context=self)
            users = RM.getUsersByRole(supervisor_user_id[5:])
            if users:
                supervisor_user_id = users[0]
        if supervisor_user_id == '':
            return None
        return supervisor_user_id
        return

    def _getAlarmSettings(self, REQUEST=None):
        if REQUEST is None:
            if hasattr(self, 'REQUEST'):
                REQUEST = self.REQUEST
            else:
                return self.alarm_settings
        alarm_type = REQUEST.get('alarm_type')
        alarm_settings = {}
        if alarm_type == 'percents':
            alarm_settings['value'] = REQUEST['alarm_percents']
        elif alarm_type == 'periodical':
            alarm_settings['value'] = REQUEST['alarm_period']
            alarm_settings['period_type'] = REQUEST['alarm_period_type']
        elif alarm_type == 'custom':
            alarm_settings['value'] = map(parseDateTime, REQUEST.get('alarm_dates', ()))
        if alarm_settings:
            alarm_settings['type'] = alarm_type
            alarm_settings['note'] = REQUEST['alarm_note']
            alarm_settings['include_descr'] = not not REQUEST.get('alarm_includes_descr')
        else:
            alarm_settings = None
        return alarm_settings
        return


InitializeClass(TaskDefinitionFollowup)

class TaskDefinitionFormFollowup(TaskDefinitionForm):
    """
      Class-view.

      Showing form for edit action template's fields.

    """
    __module__ = __name__
    _template = 'task_definition_followup'

    def onSubmit(self):
        """
          Returns java-script fragment, to check form's fields on submit

        """
        msg = getToolByName(self, 'msg')
        script = TaskDefinitionForm.onSubmit(self)
        script += "\n        if (! window.document.getElementsByName('title')[0].value) {\n          alert('%(title_absent)s');\n          return false;\n        }\n\n        check_iu = window.document.getElementsByName('involved_users_var')[0].value == '';\n\n        if (! window.document.getElementsByName('involved_users:list')[0].options.length && check_iu) {\n          if ( !window.document.getElementsByName('_full_userlist')[0].checked ) {\n            alert('%(users_absent)s');\n            return false;\n          }\n        }\n        selectAll( form['involved_users:list'] );\n        return true;\n        " % {'title_absent': (msg('Please specify task title')), 'users_absent': (msg('Please specify responsible members'))}
        return script
        return

    getTaskDefinitionFormScriptOnSubmit = onSubmit


class TaskDefinitionControllerFollowup(TaskDefinitionController):
    """
      Class-controller.

      Takes values from request, and store them to model.

    """
    __module__ = __name__

    def __init__(self, task_brains=''):
        self.task_brains = task_brains
        return

    def getEmptyArray(self):
        """
          Return empty dictionary

        """
        emptyArray = TaskDefinitionController.getEmptyArray(self)
        emptyArray['title'] = ''
        emptyArray['involved_users'] = []
        emptyArray['supervisor_user'] = ''
        emptyArray['duration_time'] = 86400
        emptyArray['description'] = ''
        emptyArray['_full_userlist'] = 0
        emptyArray['confirm_by_turn'] = 0
        emptyArray['finalization_mode'] = 'manual_creator'
        emptyArray['notification_level'] = 0
        emptyArray['alarm_settings'] = None
        return emptyArray
        return

    def getTaskDefinitionByRequest(self, request):
        """
          Return task definition instance by request

          Arguments:

            'request' -- REQUEST

          Result:

            Filled by form 'TaskDefinitionFollowup' instance

        """
        taskDefinition = TaskDefinitionFollowup(self.task_brains)
        TaskDefinitionController.getTaskDefinitionByRequest(self, request, taskDefinition)
        var_postfix = '_var'
        params = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for param in params:
            if request.has_key(param):
                if param == 'duration_time':
                    setattr(taskDefinition, 'duration_time', request['duration_time'])
                    param = 'duration_time'
                elif param == 'alarm_type':
                    setattr(taskDefinition, 'alarm_settings', taskDefinition._getAlarmSettings(request))
                else:
                    setattr(taskDefinition, param, request[param])
            elif param == 'confirm_by_turn' or param == '_full_userlist':
                setattr(taskDefinition, param, 0)
            elif param == 'supervisor_user':
                setattr(taskDefinition, param, '')
            elif param == '_allow_edit':
                setattr(taskDefinition, param, [])
            elif param == 'notification_level':
                setattr(taskDefinition, param, 0)
            pkey = param + var_postfix
            if request.has_key(pkey) and request[pkey]:
                taskDefinition.vars[param] = request[pkey]

        return taskDefinition
        return


class TaskDefinitionRegistryFollowup(TaskDefinitionRegistry):
    """
      Class-registry

      Register information to factory.

    """
    __module__ = __name__
    type_list = ({'id': 'followup_request', 'title': "Creating task 'Request'"}, {'id': 'followup_directive', 'title': "Creating task 'Directive'"}, {'id': 'followup_information', 'title': "Creating task 'Information'"}, {'id': 'followup_signature_request', 'title': "Creating task 'Signature request'"})
    Form = TaskDefinitionFormFollowup()
    dtml_token = 'followup'
    condition = Expression("python: portal.portal_addons.hasActiveAddon('GenericTaskTypes')")

    def getControllerImplementation(self, task_definition_type):
        """
          Returns class-controller implementation by type

          Arguments:

            'task_definition_type' -- type

          Result:

            Instance of 'TaskDefinitionControllerFollowup'

        """
        return TaskDefinitionControllerFollowup(self._getTaskDefinitionTaskBrainsByType(task_definition_type))
        return

    def _getTaskDefinitionTaskBrainsByType(self, task_definition_type):
        """
          Returns appropriate task's brains by specified task_defintion_type

          Arguments:

            'task_definition_type' -- type of task definition

        """
        return task_definition_type.replace('followup_', '')
        return


def patch_module():
    """
        XXX
        this is needed for ZODB class identify
        TODO: add message to log
        TODO: remove this in 3.6
    """
    import sys
    sys.modules['Products.CMFNauTools.TaskDefinitionFollowup'] = sys.modules['Products.CMFNauTools.Addons.GenericTaskTypes.TaskDefinitionFollowup']
    return


def initialize(context):
    patch_module()
    context.registerAction(TaskDefinitionRegistryFollowup())
    return
