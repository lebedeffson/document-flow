#! /bin/env python2.3
"""

$Id: testActionTemplate.py,v 1.6 2006/02/09 12:09:56 ynovokreschenov Exp $
"""
__version__='$Revision: 1.6 $'[11:-2]

import os, sys
import Configurator
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

class TaskActionTemplateTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata
        self.userids = []
        
        # creating test_category
        self._test_category = 'test_category'

        self.category = portal_metadata.addCategory( cat_id=self._test_category, 
                                                     title=self._test_category, 
                                                     default_workflow=0,
                                                     allowed_types=['HTMLDocument']
                                                    )
        self.category.setBases(['SimpleDocument'])

        # creating a test users
        self._addUser(1)
        self._addUser(2)
        get_transaction().commit()
    
    def testTaskTemplate(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata

        # test task_template_list form
        path = '/%s/task_template_list' % category.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )
        self.naudoc.portal_metadata.deleteCategories( [self._test_category] )

    def testDistributeDocument(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        template_id = 'test_distribute_document_id'
        other_user_emails = ['qwe@qwe.qwe']
        letter_type = ['partial', 'as_is']
        subject = 'test subject'
        letter_parts = ['body', 'attachment', 'metadata', 'link_to_doc']
        comment = 'test comment'

        extra = { 'action':'add_root_task_definition',
                  'task_definition_type':'distribute_document',
                  'template_id':template_id,
                  'name':template_id,
                  'requested_users':['_test_user1','_test_user2'],
                  'other_user_emails':other_user_emails,
                  '_allow_edit':['users'],
                  'letter_type':letter_type[0],
                  'subject':subject,
                  'letter_parts':letter_parts,
                  'comment':comment,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        
        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['requested_users'], extra['requested_users'] )
        self.assertEquals( task_definition['other_user_emails'], extra['other_user_emails'] )
        self.assertEquals( task_definition['letter_type'], extra['letter_type'] )
        self.assertEquals( task_definition['subject'], extra['subject'] )
        self.assertEquals( task_definition['letter_parts'], extra['letter_parts'] )
        self.assertEquals( task_definition['comment'], extra['comment'] )
        self.assertEquals( task_definition['_allow_edit'], extra['_allow_edit'] )
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':'1'
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )

        # change_task_definition
        other_user_emails = ['newqwe@qwe.qwe']
        letter_type = ['partial', 'as_is']
        subject = 'new test subject'
        letter_parts = ['body', 'attachment']
        comment = 'new test comment'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':'1',
                  'template_id':template_id,
                  'name':template_id,
                  'requested_users':['_test_user2'],
                  'other_user_emails':other_user_emails,
                  '_allow_edit':[],
                  'letter_type':letter_type[1],
                  'subject':subject,
                  'letter_parts':letter_parts,
                  'comment':comment,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['requested_users'], extra['requested_users'] )
        self.assertEquals( task_definition['other_user_emails'], extra['other_user_emails'] )
        self.assertEquals( task_definition['letter_type'], extra['letter_type'] )
        self.assertEquals( task_definition['subject'], extra['subject'] )
        self.assertEquals( task_definition['letter_parts'], extra['letter_parts'] )
        self.assertEquals( task_definition['comment'], extra['comment'] )
        self.assertEquals( task_definition['_allow_edit'], extra['_allow_edit'] )

        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':'1'
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')
   
    def testCreateVersion(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'create_version'
        template_id = 'test_create_version_id'
        version_state = 'evolutive'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'version_state':version_state
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['version_state'], extra['version_state'] )

        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        version_state = 'keep_state'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'version_state':version_state
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['version_state'], extra['version_state'] )

        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')
    
    def testCreateSubordinate(self):
        portal_metadata = self.naudoc.portal_metadata
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        c_id = 'SimpleDocument'
        category = portal_metadata.getCategory(c_id)
        
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'create_subordinate'
        template_id = 'test_create_subordinate_id'
        dest_category = self.category.getId()
        object_title_template = 'test_title_template'
        dest_folder_type = 'qwe'
        dest_folder_uid = 'qwe'
        dest_folder_title = 'test_folder'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'dest_category':dest_category,
                  'object_title_template':object_title_template,
                  'dest_folder_type':dest_folder_type,
                  'dest_folder_uid':dest_folder_uid,
                  'dest_folder_title':dest_folder_title
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_category'], extra['dest_category'] )
        self.assertEquals( task_definition['dest_folder_type'], extra['dest_folder_type'] )
        self.assertEquals( task_definition['dest_folder_uid'], extra['dest_folder_uid'] )
        self.assertEquals( task_definition['dest_folder_title'], extra['dest_folder_title'] )
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        object_title_template = 'new_test_title_template'
        dest_folder_type = 'new_qwe'
        dest_folder_uid = 'new_qwe'
        dest_folder_title = 'new_test_folder'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'dest_category':dest_category,
                  'object_title_template':object_title_template,
                  'dest_folder_type':dest_folder_type,
                  'dest_folder_uid':dest_folder_uid,
                  'dest_folder_title':dest_folder_title
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_category'], extra['dest_category'] )
        self.assertEquals( task_definition['dest_folder_type'], extra['dest_folder_type'] )
        self.assertEquals( task_definition['dest_folder_uid'], extra['dest_folder_uid'] )
        self.assertEquals( task_definition['dest_folder_title'], extra['dest_folder_title'] )
        
        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def testMessage(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'message'
        template_id = 'test_message_id'
        message = 'test message'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'message':message
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['message'], extra['message'] )
        
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        message = 'new message'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'message':message
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['message'], extra['message'] )

        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def testRoutingShortcut(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'routing_shortcut'
        template_id = 'test_routing_shortcut_id'
        dest_folder_type = ['path', 'template']
        dest_folder_uid = 'dest_folder_uid'
        dest_folder_template = None#'dest_folder_template'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'dest_folder_type':dest_folder_type[0],
                  'dest_folder_uid':dest_folder_uid,
                  'dest_folder_template':dest_folder_template
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_folder_type'], extra['dest_folder_type'] )
        self.assertEquals( task_definition['dest_folder_uid'], extra['dest_folder_uid'] )
        self.assertEquals( task_definition['dest_folder_template'], extra['dest_folder_template'] )        
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        dest_folder_uid = None#'dest_folder_uid'
        dest_folder_template = '.'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'dest_folder_type':dest_folder_type[1],
                  'dest_folder_uid':dest_folder_uid,
                  'dest_folder_template':dest_folder_template
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_folder_type'], extra['dest_folder_type'] )
        self.assertEquals( task_definition['dest_folder_uid'], extra['dest_folder_uid'] )
        self.assertEquals( task_definition['dest_folder_template'], extra['dest_folder_template'] )        

        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def testCreateDocument(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'create_document'
        template_id = 'test_create_document_id'
        dest_category = 'Document'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'dest_category':dest_category
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_category'], extra['dest_category'] )

        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        dest_category = 'Publication'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'dest_category':dest_category
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_category'], extra['dest_category'] )

        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def testNotification(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'notification'
        template_id = 'test_notification_id'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )

        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )

        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def testSetCategoryAttribute(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'set_category_attribute'
        template_id = 'test_set_category_attribute_id'
        attribute_name = 'test_attribute_name'
        attribute_value = 'attribute_value'
        attribute_value_var = 'attribute_value_var'
        category.addAttributeDefinition( name='test_attribute', type='string', title='test_attribute' )
        
        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'attribute_name':'test_attribute',
                  'value_test_attribute':attribute_value,
                  '_allow_edit':[True],
                  'attribute_value_var':attribute_value_var
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['attribute_name'], extra['attribute_name'] )
        self.assertEquals( task_definition['attribute_value'], extra['value_test_attribute'] )
        self.assertEquals( task_definition['_allow_edit'], extra['_allow_edit'] )
        self.assertEquals( list(task_definition['vars']).sort(), [extra['attribute_value_var']].sort() )

        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        attribute_value = 'new_attribute_value'
        attribute_value_var = 'new_attribute_value_var'
        category.addAttributeDefinition( name='new_test_attribute', type='string', title='new_test_attribute' )
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'attribute_name':'new_test_attribute',
                  'value_new_test_attribute':attribute_value,
                  '_allow_edit':[True],
                  'attribute_value_var':attribute_value_var
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['attribute_name'], extra['attribute_name'] )
        self.assertEquals( task_definition['attribute_value'], extra['value_new_test_attribute'] )
        self.assertEquals( task_definition['_allow_edit'], extra['_allow_edit'] )
        self.assertEquals( list(task_definition['vars']).sort(), [extra['attribute_value_var']].sort() )

        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def testRoutingObject(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'routing_object'
        template_id = 'move_test_routing_object_id'
        dest_folder_type = ['path', 'template']
        dest_folder_uid = 'dest_folder_uid'
        dest_folder_template = None#'.'
        

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'dest_folder_type':dest_folder_type[0],
                  'dest_folder_uid':dest_folder_uid,
                  'dest_folder_template':dest_folder_template
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_folder_type'], extra['dest_folder_type'] )
        self.assertEquals( task_definition['dest_folder_uid'], extra['dest_folder_uid'] )
        self.assertEquals( task_definition['dest_folder_template'], extra['dest_folder_template'] )

        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        dest_folder_type = ['path', 'template']
        dest_folder_uid = None#'dest_folder_uid'
        dest_folder_template = '.'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'dest_folder_type':dest_folder_type[1],
                  'dest_folder_uid':dest_folder_uid,
                  'dest_folder_template':dest_folder_template
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['dest_folder_type'], extra['dest_folder_type'] )
        self.assertEquals( task_definition['dest_folder_uid'], extra['dest_folder_uid'] )
        self.assertEquals( task_definition['dest_folder_template'], extra['dest_folder_template'] )
        
        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')
        
    def testScript(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'script'
        template_id = 'test_script_id'
        # creating test scripts
        self.naudoc.storage.invokeFactory( type_name='Script'
                                         , id='test_script1'
                                         , title='test_script1'
                                         , description='test description'
                                         )
        script = self.naudoc._getOb('storage')._getOb('test_script1')
        script.setBody('# test script1\np = 1 + 1\nreturn p')

        self.naudoc.storage.invokeFactory( type_name='Script'
                                         , id='test_script2'
                                         , title='test_script2'
                                         , description='test description'
                                         )
        
        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'script':script
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['script'], extra['script'] )
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        script = self.naudoc._getOb('storage')._getOb('test_script2')
        script.setBody('# test script2\np = 1 + 1\nreturn p')
                                                            
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'script':script
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['script'], extra['script'] )
        
        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

        self.naudoc.storage.deleteObjects( ['test_script1','test_script2'] )
    
    # TOFIX: this test is failed
    def testExternalMessage(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'external_message'
        template_id = 'test_external_message_id'
        message_service = None
        message_type = None
        message_title = 'message_title'
        message_template = None
        recipient_type = ['username', 'owner', 'editor', 'assigned']
        recipient_id = ''

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'message_service':message_service,
                  'message_type':message_type,
                  'message_title':message_title,
                  'message_template':message_template,
                  'recipient_type':recipient_type[2],
                  'recipient_id':recipient_id,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['message_service'], extra['message_service'] )
        self.assertEquals( task_definition['message_type'], extra['message_type'] )
        self.assertEquals( task_definition['message_title'], extra['message_title'] )
        self.assertEquals( task_definition['message_template'], extra['message_template'] )
        self.assertEquals( task_definition['recipient_type'], extra['recipient_type'] )
        self.assertEquals( task_definition['recipient_id'], extra['recipient_id'] )
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        message_service = None
        message_type = None
        message_title = 'new_message_title'
        message_template = None
        recipient_type = ['username', 'owner', 'editor', 'assigned']
        recipient_id = 'new_recipient_id'        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'message_service':message_service,
                  'message_type':message_type,
                  'message_title':message_title,
                  'message_template':message_template,
                  'recipient_type':recipient_type[1],
                  'recipient_id':recipient_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['message_service'], extra['message_service'] )
        self.assertEquals( task_definition['message_type'], extra['message_type'] )
        self.assertEquals( task_definition['message_title'], extra['message_title'] )
        self.assertEquals( task_definition['message_template'], extra['message_template'] )
        self.assertEquals( task_definition['recipient_type'], extra['recipient_type'] )
        self.assertEquals( task_definition['recipient_id'], extra['recipient_id'] )
        
        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')
        
    def testRegisterVersion(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'register_version'
        template_id = 'test_register_version_id'
        folder = self.naudoc.storage
        folder.manage_addProduct['CMFNauTools'].addRegistrationBook( id='test_registry',
                                                                     title='test_registry',
                                                                     description='test'
                                                                    )
        reg = folder._getOb('test_registry')
        reg.setRegisteredCategory(c_id)
        registry_uid = folder._getOb('test_registry')

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'registry_uid':'test_registry'
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['registry_uid'], extra['registry_uid'] )
        
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'registry_uid':'test_registry'
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['registry_uid'], extra['registry_uid'] )
        
        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')
        
        folder.deleteObjects(['test_registry'])

    
    def testActivateVersion(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'activate_version'
        template_id = 'test_activate_version_id'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        #print task_definition
        self.assertEquals( task_definition['name'], extra['name'] )
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )

        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')
    
    def testSetTimer(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'set_timer'
        template_id = 'test_set_timer_id'
        transition = 'envolve'
        attribute_name = 'test_attribute'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'transition':transition,
                  'attribute_name':attribute_name
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['transition'], extra['transition'] )
        self.assertEquals( task_definition['attribute_name'], extra['attribute_name'] )
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        transition = 'fix'
        attribute_name = 'new_test_attribute'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'transition':transition,
                  'attribute_name':attribute_name
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['transition'], extra['transition'] )
        self.assertEquals( task_definition['attribute_name'], extra['attribute_name'] )
        
        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')
        
    def testAnotherDocumentTransition(self):
        #another_document_transition
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'another_document_transition'
        template_id = 'test_another_document_transition_id'
        document_category = 'Document'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                  'document_category':document_category,
                  'use_inheritance':True,
                  'link_type':'reference',
                  'state_id':'frozen',
                  'transition_id':'edit',
                  'comment':'test_comment'
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['document_category'], extra['document_category'] )
        self.assertEquals( task_definition['use_inheritance'], extra['use_inheritance'] )
        self.assertEquals( task_definition['link_type'], extra['link_type'] )
        self.assertEquals( task_definition['state_id'], extra['state_id'] )
        self.assertEquals( task_definition['transition_id'], extra['transition_id'] )
        self.assertEquals( task_definition['comment'], extra['comment'] )
        
        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        
        # change_task_definition
        document_category = 'Directive'
        
        extra = { 'action':'change_task_definition',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                  'name':template_id,
                  'document_category':document_category,
                  'use_inheritance':False,
                  'link_type':'attribute',
                  'state_id':'fixed',
                  'transition_id':'fix',
                  'comment':'new_test_comment'
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        
        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['document_category'], extra['document_category'] )
        self.assertEquals( task_definition['use_inheritance'], extra['use_inheritance'] )
        self.assertEquals( task_definition['link_type'], extra['link_type'] )
        self.assertEquals( task_definition['state_id'], extra['state_id'] )
        self.assertEquals( task_definition['transition_id'], extra['transition_id'] )
        self.assertEquals( task_definition['comment'], extra['comment'] )
        
        # deleting a new task_definition
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def testClearTimer(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        path = '/%s/action_template_task_definition' % category.absolute_url(1)

        # creating a new task_definition
        task_definition_type = 'clear_timer'
        template_id = 'test_clear_timer_id'

        extra = { 'task_definition_type':task_definition_type,
                  'action':'add_root_task_definition',
                  'template_id':template_id,
                  'name':template_id,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)

        task_definition_id = '1'
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )

        #change_task_definition_title
        extra = { 'action':'change_task_definition_title',
                  'template_id':template_id,
                  'name':'new_title',
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )

        self.assertEquals( task_definition['name'], extra['name'] )
        
        # Here is a tests for tree of nested templates (depth=3)
        # creating nested template (level 2)
        # task_template_task_definition_add_form
        path1 = '/%s/task_template_task_definition_info' % category.absolute_url(1)
        task_definition_id = '1'
        extra = { 'action':'task_template_task_definition_add_form',
                  'task_definition_type':'create_document',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                }
        response = self.publish(path1, basic_auth, extra=extra)
        self.assertResponse(response)
        
        # creating nested template
        task_definition_id = '2'
        extra = { 'action':'add_task_definition',
                  'name':'test_template_level_2',
                  'dest_category':'SimpleDocument',
                  'template_id':template_id,
                  'parent_id':'1',
                  'task_definition_type':'create_document',
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, extra['template_id'], '2' )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_category'], extra['dest_category'] )
        self.assertEquals( task_definition['id'], '2' )
        self.assertEquals( task_definition['type'], extra['task_definition_type'] )

        # creating nested template (level 3)
        # task_template_task_definition_add_form
        path1 = '/%s/task_template_task_definition_info' % category.absolute_url(1)
        task_definition_id = '1'
        extra = { 'action':'task_template_task_definition_add_form',
                  'task_definition_type':'create_document',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                }
        response = self.publish(path1, basic_auth, extra=extra)
        self.assertResponse(response)
        #f = open('qwe.htm', 'w')
        #f.write(str(response))
        
        # creating nested template (level 3)
        task_definition_id = '3'
        extra = { 'action':'add_task_definition',
                  'name':'test_template_level_3',
                  'dest_category':'Folder',
                  'template_id':template_id,
                  'parent_id':'2',
                  'task_definition_type':'create_document',
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, extra['template_id'], '3' )

        self.assertEquals( task_definition['name'], extra['name'] )
        self.assertEquals( task_definition['dest_category'], extra['dest_category'] )
        self.assertEquals( task_definition['id'], '3' )
        self.assertEquals( task_definition['type'], extra['task_definition_type'] )
        
       # checkin result form view
        path1 = '/%s/task_template_task_definition_info' % category.absolute_url(1)
        task_definition_id = '1'
        extra = { 'action':'task_template_task_definition_add_form',
                  'task_definition_type':'create_document',
                  'id_task_definition':task_definition_id,
                  'template_id':template_id,
                }
        response = self.publish(path1, basic_auth, extra=extra)
        self.assertResponse(response)
        if 'test_template_level_3' and 'test_template_level_2' not in str(response):
            self.fail('The names of nested templates must be witten in response!')
        
        # deleting a new task_definition
        task_definition_id = '1'
        extra = { 'action':'delete_task_definition',
                  'template_id':template_id,
                  'id_task_definition':task_definition_id
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse(response)
        try:
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, task_definition_id )
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, '2' )
            task_definition = portal_metadata.taskTemplateContainerAdapter.getTaskDefinitionById( c_id, template_id, '3' )
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')    
        
    def beforeTearDown(self):
        self.naudoc.portal_membership.deleteMembers( self.userids )
        self.naudoc.portal_metadata.deleteCategories( [self._test_category] )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(TaskActionTemplateTests) )

    return suite

if __name__ == '__main__':
    framework()

