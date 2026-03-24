#! /bin/env python2.3
"""
Create and implement NauDoc tasks. Measure time needed.

$Id: testTaskSignatureRequest.py,v 1.2 2006/02/22 11:34:26 ynovokreschenov Exp $
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

class TaskSignatureRequestTests(NauDocTestCase.NauFunctionalTestCase):

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

    def testTaskSignatureRequestSign(self):
        users = self.naudoc.acl_users.getUsers()
        portal_followup = getToolByName( self.naudoc, 'portal_followup' )
        storage = self.naudoc.storage.members
        doc = storage._getOb( self.test_document )
        brains_type = 'signature_request'
        date_time = DateTime()
        
        basic_auth = "%s:%s" % (self.log_as_admin, 'secret')
        
        # test document_confirmation_form
        path = '/%s/%s/document_confirmation_form' % (storage.absolute_url(1), doc.getId())
        extra = { 'brains_type':brains_type, }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        # test document_confirmation
        involved_users = [str(users[1])]
        path = '/%s/document_confirmation' % doc.absolute_url(1)
        extra = { 'brains_type':brains_type,
                  'involved_users':involved_users,
                  'expiration':date_time+1,
                  'confirm_by_turn':False,
                  'comment':'test comment...',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        task = portal_followup.searchTasks()[0]
        self.assertEquals( task.BrainsType, extra['brains_type'] )
        self.assertEquals( task.getObject().involved_users, extra['involved_users'] )
        self.assertEquals( task.getObject().expiration_date, extra['expiration'] )
        self.assertEquals( task.getObject().description, extra['comment'] )

        # test document_follow_up_form
        path = '/%s/document_follow_up_form' % doc.absolute_url(1)
        extra = { 'brains_type':brains_type, }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        self.assert_( task.getObject().title in str(response) )

        # logging in as TestUser2 to reply the task
        # test followup_in?showTaskMode=incoming_tasks
        user = involved_users[0]
        user_auth = "%s:%s" % (user, 'secret')
        path = '/%s/followup_in' % doc.absolute_url(1)
        extra = { 'showTaskMode':'incoming_tasks', }
        response = self.publish(path, user_auth, extra=extra )
        self.assertResponse( response )

        self.assert_( task.getObject().title in str(response) )

        # test viewing new task followup/task_001/view
        path = '/%s/view' % task.getObject().absolute_url(1)
        response = self.publish(path, user_auth )
        self.assertResponse( response )

        self.assert_(task.getObject().title in str(response))

        # test followup/task_001/task_response_form?status=sign
        path = '/%s/task_response_form?status=sign' % task.getObject().absolute_url(1)
        response = self.publish(path, user_auth )
        self.assertResponse( response )

        self.assert_(task.getObject().title in str(response))

        # test Respond?status=sign
        path = '/%s/Respond' % task.getObject().absolute_url(1)
        extra = { 'status':'sign',
                  'text':'comments..',
                }
        response = self.publish(path, user_auth, extra=extra )
        self.assertResponse( response )

        self.logout()

        # checking that user is signatured
        self.login( self.log_as_admin )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='sign':
                    self.assertEquals( user, str(users[1]) )
        
        # checking that task is finalized
        self.assert_( task.getObject().finalized )
        
    def testTaskSignatureRequestReject(self):
        users = self.naudoc.acl_users.getUsers()
        portal_followup = getToolByName( self.naudoc, 'portal_followup' )
        storage = self.naudoc.storage.members
        doc = storage._getOb( self.test_document )
        brains_type = 'signature_request'
        date_time = DateTime()
        
        basic_auth = "%s:%s" % (self.log_as_admin, 'secret')
        
        # test document_confirmation_form
        path = '/%s/%s/document_confirmation_form' % (storage.absolute_url(1), doc.getId())
        extra = { 'brains_type':brains_type, }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        # test document_confirmation
        involved_users = [str(users[1])]
        path = '/%s/document_confirmation' % doc.absolute_url(1)
        extra = { 'brains_type':brains_type,
                  'involved_users':involved_users,
                  'expiration':date_time+1,
                  'confirm_by_turn':False,
                  'comment':'test comment...',
                }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        task = portal_followup.searchTasks()[0]
        self.assertEquals( task.BrainsType, extra['brains_type'] )
        self.assertEquals( task.getObject().involved_users, extra['involved_users'] )
        self.assertEquals( task.getObject().expiration_date, extra['expiration'] )
        self.assertEquals( task.getObject().description, extra['comment'] )

        # test document_follow_up_form
        path = '/%s/document_follow_up_form' % doc.absolute_url(1)
        extra = { 'brains_type':brains_type, }
        response = self.publish(path, basic_auth, extra=extra )
        self.assertResponse( response )

        self.assert_( task.getObject().title in str(response) )

        # logging in as TestUser2 to reply the task
        # test followup_in?showTaskMode=incoming_tasks
        user = involved_users[0]
        user_auth = "%s:%s" % (user, 'secret')
        path = '/%s/followup_in' % doc.absolute_url(1)
        extra = { 'showTaskMode':'incoming_tasks', }
        response = self.publish(path, user_auth, extra=extra )
        self.assertResponse( response )

        self.assert_( task.getObject().title in str(response) )

        # test viewing new task followup/task_001/view
        path = '/%s/view' % task.getObject().absolute_url(1)
        response = self.publish(path, user_auth )
        self.assertResponse( response )

        self.assert_(task.getObject().title in str(response))

        # test followup/task_001/task_response_form?status=reject
        path = '/%s/task_response_form?status=reject' % task.getObject().absolute_url(1)
        response = self.publish(path, user_auth )
        self.assertResponse( response )

        self.assert_(task.getObject().title in str(response))

        # test Respond?status=satisfy
        path = '/%s/Respond' % task.getObject().absolute_url(1)
        extra = { 'status':'reject',
                  'text':'comments..',
                }
        response = self.publish(path, user_auth, extra=extra )
        self.assertResponse( response )

        self.logout()

        # checking that user is satisfacted
        self.login( self.log_as_admin )

        task = portal_followup.listOutgoingTasks()[0]
        for response in task['StateKeys']:
            try:
                code, user = response.split(':', 1)
            except ValueError:
                pass
            else:
                if code=='reject':
                    self.assertEquals( user, str(users[1]) )

        # checking that task is finalized
        self.assert_( task.getObject().finalized )

    def beforeTearDown(self):
        self.login(self.log_as_admin)
        users = [str(i) for i in self.naudoc.acl_users.getUsers()]
        self.naudoc.storage.members.deleteObjects( [self.test_document] )
        self.naudoc.portal_membership.deleteMembers( users )
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(TaskSignatureRequestTests) )
    return suite

if __name__ == '__main__':
    framework()
