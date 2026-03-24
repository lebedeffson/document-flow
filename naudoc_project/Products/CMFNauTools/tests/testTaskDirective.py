#! /bin/env python2.3
"""
Create and implement NauDoc tasks. Measure time needed.

$Id: testTaskDirective.py,v 1.2 2006/02/21 12:43:56 ynovokreschenov Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

import os, sys
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
import string
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.SimpleObjects import ItemBase
from DateTime import DateTime

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class TaskDirectiveTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_admin = NauDocTestCase.admin_name
    _user_basename = 'test_user_'

    def afterSetUp(self):
        self.userids = []
        self._addUser(1)
        self._addUser(2)
        self._addUser(3)
        storage = self.naudoc.storage.members
        self.test_document = 'test_document'
        storage.invokeFactory( type_name='HTMLDocument',
                               id=self.test_document,
                               title='test_document',
                               description='test description',
                               category='Document' )
        obj = storage._getOb( self.test_document )
        get_transaction().commit()
        
    # in this case - finalization_mode = manual_creator so only creater can finalize the task
    def testTaskDirectiveImplementation_manual_creator(self):
        users = self.naudoc.acl_users.getUsers()
        portal_followup = getToolByName( self.naudoc, 'portal_followup' )
        storage = self.naudoc.storage

        basic_auth = "%s:%s" % (self.log_as_admin, 'secret')
        # test followup_tasks_form
        path = '/%s/followup_tasks_form' % self.naudoc.absolute_url(1)
        response = self.publish(path, basic_auth )
        self.assertResponse( response )
        
        # test task_add_form
        path = '/%s/task_add_form' % self.naudoc.absolute_url(1)
        extra = { 'brains_type':'directive' }
        response = self.publish(path, basic_auth , extra=extra)
        self.assertResponse( response )

        # test followup_tasks_form
        date_time = DateTime()
        path = '/%s/task_edit' % self.naudoc.followup.absolute_url(1)
        extra = { 'brains_type':'directive',
                  'title':'test_task',
                  'description':'test description',
                  'effective_date':date_time,
                  'expiration_date':date_time+1,
                  'plan_time':1.0,
                  'periodical':False,
                  'involved_users':[str(users[0]), str(users[1])],
                  'supervisor':str(users[2]),
                  'finalization_mode':'manual_creator',
                }
        response = self.publish(path, basic_auth , extra=extra)
        self.assertResponse( response )
        
        task_created_ids = self.naudoc.followup.getBoundTaskIds()
        task = portal_followup.listOutgoingTasks()[0]
        obj = task.getObject()
        self.assertEquals( task.Title, extra['title'] )
        self.assertEquals( obj.plan_time, extra['plan_time'] )
        self.assertEquals( obj.finalization_mode, extra['finalization_mode'] )
        self.assertEquals( task.Description, extra['description'] )
        self.assertEquals( task.effective, extra['effective_date'] )
        self.assertEquals( task.expires, extra['expiration_date'] )
        self.assertEquals( task.InvolvedUsers, extra['involved_users'] )
        self.assertEquals( task.Supervisor, extra['supervisor'] )
        self.assertEquals( task.BrainsType, extra['brains_type'] )

        self.logout()
        
        # authorize as users[1] to checking new task
        user = str(users[0])
        basic_auth = "%s:%s" % (user, 'secret')

        path = '/%s/followup_in' % self.naudoc.absolute_url(1)
        extra = { 'showTaskMode':'incoming_tasks' }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )
        self.assert_('test_task' in str(response))

        task_user = portal_followup.searchTasks()[0]
        
        self.assertEquals( task_user.Title, task.Title )
        self.assertEquals( task_user.Description, task.Description )
        self.assertEquals( task_user.effective, task.effective )
        self.assertEquals( task_user.expires, task.expires )
        self.assertEquals( task_user.InvolvedUsers, task.InvolvedUsers )
        self.assertEquals( task_user.Supervisor, task.Supervisor )
        self.assertEquals( task_user.BrainsType, task.BrainsType )
        
        # test viewing new task followup/task_001/view
        path = '/%s/followup/%s/view' % (self.naudoc.absolute_url(1), task_user.id )
        response = self.publish(path, basic_auth )
        self.assertResponse( response )
        self.assert_('test_task' in str(response))
        
        # test task_response_form
        path = '/%s/followup/%s/task_response_form' % (self.naudoc.absolute_url(1), task_user.id )
        extra = { 'status':'task_start' } 
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )
        self.assert_('test_task' in str(response))
        
        # test user responses
        # status = task_start
        path = '/%s/followup/%s/Respond' % (self.naudoc.absolute_url(1), task_user.id )
        extra = { 'status':'task_start',
                  'text':'comments..',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        self.logout()
        
        # checking that user is informed
        self.login( self.log_as_admin )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='task_start':
                    self.assertEquals( user, str(users[0]) )

        # status = reject
        path = '/%s/followup/%s/Respond' % (self.naudoc.absolute_url(1), task_user.id )
        extra = { 'status':'reject',
                  'text':'comments..',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        self.logout()
        
        # checking that user is informed
        self.login( self.log_as_admin )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='reject':
                    self.assertEquals( user, str(users[0]) )
        
        # status = commit
        #document_uid = storage._getOb(self.test_document).getUid()
        #print document_uid
        path = '/%s/followup/%s/Respond' % (self.naudoc.absolute_url(1), task_user.id )
        extra = { 'status':'commit',
                  'actual_time':2.0,
                  #'close_report':1,
                  #'documents':[self.test_document],
                  'text':'comments..',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        self.logout()
        
        # checking that user is informed
        self.login( self.log_as_admin )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='commit':
                    self.assertEquals( user, str(users[0]) )

        self.assertEquals( task.getObject().actual_times[str(users[0])], extra['actual_time'] )
        
        # test finalize task
        basic_auth = "%s:%s" % (self.log_as_admin, 'secret')
        path = '/%s/followup/%s/Respond' % (self.naudoc.absolute_url(1), task_created_ids[0] )
        extra = { 'status':'finalize',
                  'text':'comments..',
                  'result_code':'success',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='finalize':
                    self.assertEquals( user, str(self.log_as_admin) )
        
        basic_auth = "%s:%s" % (self.log_as_admin, 'secret')
        path = '/%s/task_delete' % self.naudoc.absolute_url(1)

        task_uid = task.getObject().getUid()
        
        extra = { 'showTaskMode':'outgoing_tasks',
                  'ids':[task_uid],
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        tasks = portal_followup.listOutgoingTasks()
        self.assertEquals( list(tasks), [] )

        self.logout()
        
        """
        # Some bugs should be fixed first
        # test task_elaborate
        #path = '/%s/followup/%s/task_reportwizard_step1' % (self.naudoc.absolute_url(1), task_created_ids[0] )
        
        path = '/%s/task_elaborate' % self.naudoc.followup.absolute_url(1)
        extra = { 'brains_type':'information',
                  'title':'test_task',
                  'description':'test description',
                  'effective_date':date_time,
                  'expiration_date':date_time+1,
                  'plan_time':'0:0:0',
                  'periodical':False,
                  'involved_users':[str(users[0]), str(users[1])],
                  'finalization_mode':'manual_creator',
                }
        response = self.publish(path, basic_auth , extra=extra)
        self.assertResponse( response )

        # test task_elaborate_form
        s = str(response).find('wizard_data_id')
        s = s + len('wizard_data_id=')
        wizard_data_id = str(response)[s:s+28]
        path = '/%s/followup/task_elaborate_form' % self.naudoc.absolute_url(1)
        extra = { 'wizard_data_id':wizard_data_id }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        # test task_elaborate
        path = '/%s/followup/task_elaborate' % self.naudoc.absolute_url(1)
        extra = { 'wizard_data_id':wizard_data_id,
                  'description':'test description..',
                  'expiration_date':date_time+1,
                  'selected_members':[str(users[0])],
                  'add':True,
                  'finish':True
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )
        # TODO

        # testing templates
        # task_reportwizard_step1
        path = '/%s/followup/%s/task_reportwizard_step1' % (self.naudoc.absolute_url(1), task_created_ids[0] )
        response = self.publish(path, basic_auth )
        self.assertResponse( response )

        # task_reportwizard_step2
        path = '/%s/followup/%s/task_reportwizard_step2' % (self.naudoc.absolute_url(1), task_created_ids[0] )
        extra = { 'selected_tasks':[task.id],
                  'task_type':'information',
                  'template':'task_reportgenerator_tabular',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )
        
        # task_reportwizard_step3
        path = '/%s/followup/%s/task_reportwizard_step3' % (self.naudoc.absolute_url(1), task_created_ids[0] )
        extra = { 'task_type':'information',
                  'template':'task_reportgenerator_tabular',
                  'inc_inf':'',
                  'doc_view':'',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        # task_reportwizard_step4
        # TODO
        """
    # in this case - finalization_mode = auto_any_user so user can finalize the task
    def testTaskDirectiveImplementation_auto_any_user(self):
        users = self.naudoc.acl_users.getUsers()
        portal_followup = getToolByName( self.naudoc, 'portal_followup' )
        storage = self.naudoc.storage

        basic_auth = "%s:%s" % (self.log_as_admin, 'secret')
        # test followup_tasks_form
        path = '/%s/followup_tasks_form' % self.naudoc.absolute_url(1)
        response = self.publish(path, basic_auth )
        self.assertResponse( response )
        
        # test task_add_form
        path = '/%s/task_add_form' % self.naudoc.absolute_url(1)
        extra = { 'brains_type':'directive' }
        response = self.publish(path, basic_auth , extra=extra)
        self.assertResponse( response )

        # test followup_tasks_form
        date_time = DateTime()
        path = '/%s/task_edit' % self.naudoc.followup.absolute_url(1)
        extra = { 'brains_type':'directive',
                  'title':'test_task',
                  'description':'test description',
                  'effective_date':date_time,
                  'expiration_date':date_time+1,
                  'plan_time':1.0,
                  'periodical':False,
                  'involved_users':[str(users[0]), str(users[1])],
                  'supervisor':str(users[2]),
                  'finalization_mode':'auto_any_user',
                }
        response = self.publish(path, basic_auth , extra=extra)
        self.assertResponse( response )
        
        task_created_ids = self.naudoc.followup.getBoundTaskIds()
        task = portal_followup.listOutgoingTasks()[0]
        obj = task.getObject()
        self.assertEquals( task.Title, extra['title'] )
        self.assertEquals( obj.plan_time, extra['plan_time'] )
        self.assertEquals( obj.finalization_mode, extra['finalization_mode'] )
        self.assertEquals( task.Description, extra['description'] )
        self.assertEquals( task.effective, extra['effective_date'] )
        self.assertEquals( task.expires, extra['expiration_date'] )
        self.assertEquals( task.InvolvedUsers, extra['involved_users'] )
        self.assertEquals( task.Supervisor, extra['supervisor'] )
        self.assertEquals( task.BrainsType, extra['brains_type'] )

        self.logout()
        
        # authorize as users[1] to checking new task
        user = str(users[0])
        basic_auth = "%s:%s" % (user, 'secret')

        path = '/%s/followup_in' % self.naudoc.absolute_url(1)
        extra = { 'showTaskMode':'incoming_tasks' }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )
        self.assert_('test_task' in str(response))

        task_user = portal_followup.searchTasks()[0]
        
        self.assertEquals( task_user.Title, task.Title )
        self.assertEquals( task_user.Description, task.Description )
        self.assertEquals( task_user.effective, task.effective )
        self.assertEquals( task_user.expires, task.expires )
        self.assertEquals( task_user.InvolvedUsers, task.InvolvedUsers )
        self.assertEquals( task_user.Supervisor, task.Supervisor )
        self.assertEquals( task_user.BrainsType, task.BrainsType )
        
        # test viewing new task followup/task_001/view
        path = '/%s/followup/%s/view' % (self.naudoc.absolute_url(1), task_user.id )
        response = self.publish(path, basic_auth )
        self.assertResponse( response )
        self.assert_('test_task' in str(response))
        
        # test task_response_form
        path = '/%s/followup/%s/task_response_form' % (self.naudoc.absolute_url(1), task_user.id )
        extra = { 'status':'task_start' } 
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )
        self.assert_('test_task' in str(response))
        
        # test user responses
        # status = task_start
        path = '/%s/followup/%s/Respond' % (self.naudoc.absolute_url(1), task_user.id )
        extra = { 'status':'task_start',
                  'text':'comments..',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        self.logout()
        
        # checking that user is start
        self.login( self.log_as_admin )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='task_start':
                    self.assertEquals( user, str(users[0]) )

        # status = reject
        path = '/%s/followup/%s/Respond' % (self.naudoc.absolute_url(1), task_user.id )
        extra = { 'status':'reject',
                  'text':'comments..',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        self.logout()
        
        # checking that user is reject
        self.login( self.log_as_admin )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='reject':
                    self.assertEquals( user, str(users[0]) )

        self.logout()

        # status = commit
        path = '/%s/followup/%s/Respond' % (self.naudoc.absolute_url(1), task_user.id )
        extra = { 'status':'commit',
                  'actual_time':2.0,
                  'close_report':True,
                  #'documents':[self.test_document],
                  'text':'comments..',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        self.logout()
        
        # checking that user is commit
        self.login( self.log_as_admin )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='commit':
                    self.assertEquals( user, str(users[0]) )

        self.assertEquals( task.getObject().actual_times[str(users[0])], extra['actual_time'] )
        self.assert_( task.getObject().finalized )

        # deleting task
        basic_auth = "%s:%s" % (self.log_as_admin, 'secret')
        path = '/%s/task_delete' % self.naudoc.absolute_url(1)

        task_uid = task.getObject().getUid()
        
        extra = { 'showTaskMode':'outgoing_tasks',
                  'ids':[task_uid],
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        tasks = portal_followup.listOutgoingTasks()
        self.assertEquals( list(tasks), [] )

        self.logout()

    def beforeTearDown(self):
        self.login(self.log_as_admin)
        users = [str(i) for i in self.naudoc.acl_users.getUsers()]
        self.naudoc.portal_membership.deleteMembers( users )
        self.naudoc.storage.members.deleteObjects( [self.test_document] )
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(TaskDirectiveTests) )
    return suite

if __name__ == '__main__':
    framework()
