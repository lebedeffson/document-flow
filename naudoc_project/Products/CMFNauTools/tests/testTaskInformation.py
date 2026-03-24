#! /bin/env python2.3
"""
Create and implement NauDoc tasks. Measure time needed.

$Id: testTaskInformation.py,v 1.2 2006/02/21 12:44:10 ynovokreschenov Exp $
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

class TaskInformationTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_admin = NauDocTestCase.admin_name
    _user_basename = 'test_user_'

    def afterSetUp(self):
        self.userids = []
        self._addUser(1)
        self._addUser(2)
        self._addUser(3)
        get_transaction().commit()
        
    def testTaskInformationImplementation(self):
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
        extra = { 'brains_type':'information' }
        response = self.publish(path, basic_auth , extra=extra)
        self.assertResponse( response )
        
        # test followup_tasks_form
        date_time = DateTime()
        path = '/%s/task_edit' % self.naudoc.followup.absolute_url(1)
        extra = { 'brains_type':'information',
                  'title':'test_task',
                  'description':'test description',
                  'effective_date':date_time,
                  'expiration_date':date_time+1,
                  'plan_time':'0:0:0',
                  'periodical':False,
                  'involved_users':[str(users[0]), str(users[1])],
                  'supervisor':str(users[2]),
                  'finalization_mode':'manual_creator',
                }
        response = self.publish(path, basic_auth , extra=extra)
        self.assertResponse( response )
        
        task_created_ids = self.naudoc.followup.getBoundTaskIds()
        task = portal_followup.listOutgoingTasks()[0]
        self.assertEquals( task.Title, extra['title'] )
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
        path = '/%s/followup/%s/view' % (self.naudoc.absolute_url(1), task_created_ids[0] )
        response = self.publish(path, basic_auth )
        self.assertResponse( response )
        self.assert_('test_task' in str(response))

        # test task_response_form
        path = '/%s/followup/%s/task_response_form' % (self.naudoc.absolute_url(1), task_created_ids[0] )
        extra = { 'status':'informed' } 
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )
        self.assert_('test_task' in str(response))

        # test user response
        path = '/%s/followup/%s/Respond' % (self.naudoc.absolute_url(1), task_created_ids[0] )
        extra = { 'status':'informed',
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
                if code=='informed':
                    self.assertEquals( user, str(users[0]) )

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
        
    def beforeTearDown(self):
        self.login(self.log_as_admin)
        users = [str(i) for i in self.naudoc.acl_users.getUsers()]
        self.naudoc.portal_membership.deleteMembers( users )
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(TaskInformationTests) )
    return suite

if __name__ == '__main__':
    framework()
