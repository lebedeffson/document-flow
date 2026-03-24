# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/tests/testTemplates.py
# Compiled at: 2006-02-09 10:23:38
"""

$Id: testTemplates.py,v 1.2 2006/02/09 07:23:38 ynovokreschenov Exp $
"""
__version__ = '$Revision: 1.2 $'[11:-2]
import os, sys, Configurator
Constants = Configurator.Constants
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
import NauDocTestCase
from Testing import ZopeTestCase
from DateTime import DateTime
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.Utils import getToolByName
from Products.CMFNauTools.DefaultWorkflows import assignActionTemplateToTransition
import AccessControl.SecurityManagement, AccessControl.SpecialUsers
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class TaskTemplateTests(NauDocTestCase.NauFunctionalTestCase):
    __module__ = __name__
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata
        self.userids = []
        self._test_category = 'test_category'
        self.category = portal_metadata.addCategory(cat_id=self._test_category, title=self._test_category, default_workflow=0, allowed_types=['HTMLDocument'])
        self.category.setBases(['SimpleDocument'])
        self._addUser(1)
        self._addUser(2)
        get_transaction().commit()
        return

    def testTaskTemplate(self):
        basic_auth = '%s:%s' % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/task_template_list' % category.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse(response)
        self.naudoc.portal_metadata.deleteCategories([self._test_category])
        return

    def testFollowupDirective(self):
        basic_auth = '%s:%s' % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)
        task_definition_type = 'followup_directive'
        template_id = 'test_followup_directive_id'
        extra = {'task_definition_type': task_definition_type, 'action': 'add_root_task_definition', 'template_id': template_id, 'name': template_id, 'title': 'test_title', '_allow_edit': [True, True, False, False], 'title_var': 'title_var', 'involved_users': ['_test_user1', '_test_user2'], '_full_userlist': True, 'involved_users_var': 'involved_users_var', 'supervisor_user': '_test_user1', 'supervisor_user_var': 'supervisor_user_var', 'duration_time': '1:0:0', 'interval_var': 'interval_var', 'description': 'test description'}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        self.assertEquals(task_definition['title'], extra['title'])
        self.assertEquals(task_definition['_allow_edit'], extra['_allow_edit'])
        self.assertEquals(task_definition['involved_users'], extra['involved_users'])
        self.assertEquals(task_definition['_full_userlist'], extra['_full_userlist'])
        self.assertEquals(task_definition['supervisor_user'], extra['supervisor_user'])
        self.assertEquals(task_definition['interval'], extra['duration_time'])
        self.assertEquals(task_definition['description'], extra['description'])
        self.assertEquals(list(task_definition['vars']).sort(), [extra['title_var'], extra['involved_users_var'], extra['supervisor_user_var'], extra['interval_var']].sort())
        extra = {'action': 'change_task_definition_title', 'template_id': template_id, 'name': 'new_title', 'id_task_definition': task_definition_id}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        extra = {'task_definition_type': task_definition_type, 'id_task_definition': task_definition_id, 'action': 'change_task_definition', 'template_id': template_id, 'name': template_id, 'title': 'new_test_title', '_allow_edit': [False, True, False, False], 'title_var': 'new_title_var', 'involved_users': ['_test_user2'], '_full_userlist': False, 'involved_users_var': 'new_involved_users_var', 'supervisor_user': '_test_user2', 'supervisor_user_var': 'new_supervisor_user_var', 'duration_time': '1:1:0', 'interval_var': 'new_interval_var', 'description': 'new test description'}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        self.assertEquals(task_definition['title'], extra['title'])
        self.assertEquals(task_definition['_allow_edit'], extra['_allow_edit'])
        self.assertEquals(task_definition['involved_users'], extra['involved_users'])
        self.assertEquals(task_definition['_full_userlist'], extra['_full_userlist'])
        self.assertEquals(task_definition['supervisor_user'], extra['supervisor_user'])
        self.assertEquals(task_definition['interval'], extra['duration_time'])
        self.assertEquals(task_definition['description'], extra['description'])
        self.assertEquals(list(task_definition['vars']).sort(), [extra['title_var'], extra['involved_users_var'], extra['supervisor_user_var'], extra['interval_var']].sort())
        extra = {'action': 'delete_task_definition', 'template_id': template_id, 'id_task_definition': task_definition_id}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

        return

    def testFollowupSignatureRequest(self):
        basic_auth = '%s:%s' % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)
        template_id = 'test_followup_signature_request_id'
        title = 'test_title'
        title_var = 'title_var'
        involved_users_var = 'involved_users_var'
        confirm_by_turn_var = 'confirm_by_turn_var'
        interval_var = 'interval_var'
        description = 'test_description'
        description_var = 'description_var'
        extra = {'action': 'add_root_task_definition', 'task_definition_type': 'followup_signature_request', 'template_id': template_id, 'name': template_id, 'title': title, 'title_var': title_var, 'involved_users': ['_test_user1', '_test_user2'], '_full_userlist': True, 'involved_users_var': involved_users_var, 'confirm_by_turn': True, 'confirm_by_turn_var': confirm_by_turn_var, 'duration_time': '1:0:0', 'interval_var': interval_var, 'description': description, 'description_var': description_var, '_allow_edit': [19, 20, 24, 29, 27]}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        self.assertEquals(task_definition['title'], extra['title'])
        self.assertEquals(task_definition['involved_users'], extra['involved_users'])
        self.assertEquals(task_definition['_full_userlist'], extra['_full_userlist'])
        self.assertEquals(task_definition['confirm_by_turn'], extra['confirm_by_turn'])
        self.assertEquals(task_definition['interval'], extra['duration_time'])
        self.assertEquals(task_definition['description'], extra['description'])
        self.assertEquals(task_definition['_allow_edit'], extra['_allow_edit'])
        self.assertEquals(list(task_definition['vars']).sort(), [extra['involved_users_var'], extra['confirm_by_turn_var'], extra['interval_var'], extra['description_var']].sort())
        extra = {'action': 'change_task_definition_title', 'template_id': template_id, 'name': 'new_title', 'id_task_definition': '1'}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        title = 'new_test_title'
        title_var = 'new_title_var'
        involved_users_var = 'new_involved_users_var'
        confirm_by_turn_var = 'new_confirm_by_turn_var'
        interval_var = 'new_interval_var'
        description = 'new_test_description'
        description_var = 'new_description_var'
        extra = {'action': 'change_task_definition', 'id_task_definition': '1', 'template_id': template_id, 'name': template_id, 'title': title, 'title_var': title_var, 'involved_users': ['_test_user1'], '_full_userlist': False, 'involved_users_var': involved_users_var, 'confirm_by_turn': True, 'confirm_by_turn_var': confirm_by_turn_var, 'duration_time': '1:2:0', 'interval_var': interval_var, 'description': description, 'description_var': description_var, '_allow_edit': ['involved_users', 'confirm_by_turn', 'interval', 'description']}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['title'], extra['title'])
        self.assertEquals(task_definition['involved_users'], extra['involved_users'])
        self.assertEquals(task_definition['_full_userlist'], extra['_full_userlist'])
        self.assertEquals(task_definition['confirm_by_turn'], extra['confirm_by_turn'])
        self.assertEquals(task_definition['interval'], extra['duration_time'])
        self.assertEquals(task_definition['description'], extra['description'])
        self.assertEquals(task_definition['_allow_edit'], extra['_allow_edit'])
        self.assertEquals(list(task_definition['vars']).sort(), [extra['involved_users_var'], extra['confirm_by_turn_var'], extra['interval_var'], extra['description_var']].sort())
        extra = {'action': 'delete_task_definition', 'template_id': template_id, 'id_task_definition': '1'}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

        return

    def testFollowupRequest(self):
        basic_auth = '%s:%s' % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)
        template_id = 'test_followup_request_id'
        title = 'test_title'
        title_var = 'title_var'
        involved_users_var = 'involved_users_var'
        confirm_by_turn_var = 'confirm_by_turn_var'
        interval_var = 'interval_var'
        description = 'test_description'
        description_var = 'description_var'
        extra = {'action': 'add_root_task_definition', 'task_definition_type': 'followup_request', 'template_id': template_id, 'name': template_id, 'title': title, 'title_var': title_var, 'involved_users': ['_test_user1', '_test_user2'], '_full_userlist': True, 'involved_users_var': involved_users_var, 'confirm_by_turn': True, 'confirm_by_turn_var': confirm_by_turn_var, 'duration_time': '1:0:0', 'interval_var': interval_var, 'description': description, 'description_var': description_var, '_allow_edit': [19, 20, 24, 29, 27]}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        self.assertEquals(task_definition['title'], extra['title'])
        self.assertEquals(task_definition['involved_users'], extra['involved_users'])
        self.assertEquals(task_definition['_full_userlist'], extra['_full_userlist'])
        self.assertEquals(task_definition['confirm_by_turn'], extra['confirm_by_turn'])
        self.assertEquals(task_definition['interval'], extra['duration_time'])
        self.assertEquals(task_definition['description'], extra['description'])
        self.assertEquals(task_definition['_allow_edit'], extra['_allow_edit'])
        self.assertEquals(list(task_definition['vars']).sort(), [extra['involved_users_var'], extra['confirm_by_turn_var'], extra['interval_var'], extra['description_var']].sort())
        extra = {'action': 'change_task_definition_title', 'template_id': template_id, 'name': 'new_title', 'id_task_definition': '1'}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        title = 'new_test_title'
        title_var = 'new_title_var'
        involved_users_var = 'new_involved_users_var'
        confirm_by_turn_var = 'new_confirm_by_turn_var'
        interval_var = 'new_interval_var'
        description = 'new_test_description'
        description_var = 'new_description_var'
        extra = {'action': 'change_task_definition', 'id_task_definition': '1', 'template_id': template_id, 'name': template_id, 'title': title, 'title_var': title_var, 'involved_users': ['_test_user1'], '_full_userlist': False, 'involved_users_var': involved_users_var, 'confirm_by_turn': True, 'confirm_by_turn_var': confirm_by_turn_var, 'duration_time': '1:2:0', 'interval_var': interval_var, 'description': description, 'description_var': description_var, '_allow_edit': ['involved_users', 'confirm_by_turn', 'interval', 'description']}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['title'], extra['title'])
        self.assertEquals(task_definition['involved_users'], extra['involved_users'])
        self.assertEquals(task_definition['_full_userlist'], extra['_full_userlist'])
        self.assertEquals(task_definition['confirm_by_turn'], extra['confirm_by_turn'])
        self.assertEquals(task_definition['interval'], extra['duration_time'])
        self.assertEquals(task_definition['description'], extra['description'])
        self.assertEquals(task_definition['_allow_edit'], extra['_allow_edit'])
        self.assertEquals(list(task_definition['vars']).sort(), [extra['involved_users_var'], extra['confirm_by_turn_var'], extra['interval_var'], extra['description_var']].sort())
        extra = {'action': 'delete_task_definition', 'template_id': template_id, 'id_task_definition': '1'}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

        return

    def testFollowupInformation(self):
        basic_auth = '%s:%s' % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)
        template_id = 'test_followup_information_id'
        title = 'test_title'
        title_var = 'title_var'
        involved_users_var = 'involved_users_var'
        confirm_by_turn_var = 'confirm_by_turn_var'
        interval_var = 'interval_var'
        description = 'test_description'
        description_var = 'description_var'
        extra = {'action': 'add_root_task_definition', 'task_definition_type': 'followup_information', 'template_id': template_id, 'name': template_id, 'title': title, 'title_var': title_var, 'involved_users': ['_test_user1', '_test_user2'], '_full_userlist': True, 'involved_users_var': involved_users_var, 'confirm_by_turn': True, 'confirm_by_turn_var': confirm_by_turn_var, 'duration_time': '1:0:0', 'interval_var': interval_var, 'description': description, 'description_var': description_var, '_allow_edit': [19, 20, 24, 29, 27]}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        self.assertEquals(task_definition['title'], extra['title'])
        self.assertEquals(task_definition['involved_users'], extra['involved_users'])
        self.assertEquals(task_definition['_full_userlist'], extra['_full_userlist'])
        self.assertEquals(task_definition['confirm_by_turn'], extra['confirm_by_turn'])
        self.assertEquals(task_definition['interval'], extra['duration_time'])
        self.assertEquals(task_definition['description'], extra['description'])
        self.assertEquals(task_definition['_allow_edit'], extra['_allow_edit'])
        self.assertEquals(list(task_definition['vars']).sort(), [extra['involved_users_var'], extra['confirm_by_turn_var'], extra['interval_var'], extra['description_var']].sort())
        extra = {'action': 'change_task_definition_title', 'template_id': template_id, 'name': 'new_title', 'id_task_definition': '1'}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['name'], extra['name'])
        title = 'new_test_title'
        title_var = 'new_title_var'
        involved_users_var = 'new_involved_users_var'
        confirm_by_turn_var = 'new_confirm_by_turn_var'
        interval_var = 'new_interval_var'
        description = 'new_test_description'
        description_var = 'new_description_var'
        extra = {'action': 'change_task_definition', 'id_task_definition': '1', 'template_id': template_id, 'name': template_id, 'title': title, 'title_var': title_var, 'involved_users': ['_test_user1'], '_full_userlist': False, 'involved_users_var': involved_users_var, 'confirm_by_turn': True, 'confirm_by_turn_var': confirm_by_turn_var, 'duration_time': '1:2:0', 'interval_var': interval_var, 'description': description, 'description_var': description_var, '_allow_edit': ['involved_users', 'confirm_by_turn', 'interval', 'description']}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        self.assertEquals(task_definition['title'], extra['title'])
        self.assertEquals(task_definition['involved_users'], extra['involved_users'])
        self.assertEquals(task_definition['_full_userlist'], extra['_full_userlist'])
        self.assertEquals(task_definition['confirm_by_turn'], extra['confirm_by_turn'])
        self.assertEquals(task_definition['interval'], extra['duration_time'])
        self.assertEquals(task_definition['description'], extra['description'])
        self.assertEquals(task_definition['_allow_edit'], extra['_allow_edit'])
        self.assertEquals(list(task_definition['vars']).sort(), [extra['involved_users_var'], extra['confirm_by_turn_var'], extra['interval_var'], extra['description_var']].sort())
        extra = {'action': 'delete_task_definition', 'template_id': template_id, 'id_task_definition': '1'}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById(c_id, template_id, task_definition_id)
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

        return

    def beforeTearDown(self):
        self.naudoc.portal_membership.deleteMembers(self.userids)
        self.naudoc.portal_metadata.deleteCategories([self._test_category])
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TaskTemplateTests))
    return suite
    return


if __name__ == '__main__':
    framework()
