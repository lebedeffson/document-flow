"""
!!! Need manualy remove tasks, users and documents
    Automaticaly removing DO NOT work. why? - may be transaction truble

1. create  users

2. create  documents

3. assign  'information' tasks for each document

4. checking assigned tasks

$Id: testAssignTasks.py,v 1.4 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$ $'[11:-2]
import os, sys
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')


from DateTime import DateTime

class AssignTasksTest(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = False
    number_of_documents = Constants.FEW
    number_of_users = Constants.SMALL
    number_of_tasks = Constants.SMALL

    document_base_name = 'ztc_test_assign_tasks_document_'
    document_base_title = 'NauDoc test case document'

    def afterSetUp(self):
        self.userids = []
        self._create_users()
        self._create_docs()

    def testAssignTasks(self):
        self._assign_tasks()
        #check assigned tasks. Simple check, need better.
        storage = self.naudoc.storage
        for i in range(self.number_of_documents):
            doc_id = self.cookId(i)
            doc = storage._getOb( doc_id )
            self.assertEqual( len(doc.followup.getBoundTaskIds()), self.number_of_tasks)

        self._remove_assigned_tasks()
        for i in range(0,self.number_of_documents):
            doc_id = self.cookId(i)
            doc = storage._getOb( doc_id )
            self.assertEqual( len(doc.followup.getBoundTaskIds()), 0)

    def testFollowupView(self):
        self._assign_tasks()

        basic_auth = "%s:%s" % (self.cookUserId(0), 'secret')
        obj  = self.naudoc
        path = '/%s/followup_in' % obj.absolute_url(1)
        extra = {'showTaskMode':'showNew'}
        response = self.publish(path, basic_auth, extra=extra)

        self.assertResponse( response )

    def _assign_tasks(self):
        storage = self.naudoc.storage
        for i in range(0,self.number_of_documents):
            doc_id = self.cookId(i)
            doc = storage._getOb( doc_id )
            for y in range(0, self.number_of_tasks):
                doc.followup.createTask( title='test title'
                           , description='test description'
                           , involved_users= map(self.cookUserId, range(self.number_of_users))
                           , supervisor=self.cookUserId(0)
                           , effective_date=DateTime()
                           , expiration_date=DateTime()+1
                           , brains_type='information'
                           , REQUEST=None
                           )
        #get_transaction().commit()

    def _remove_assigned_tasks(self):
        storage = self.naudoc.storage
        for i in range(0,self.number_of_documents):
            doc_id = self.cookId(i)
            doc = storage._getOb( doc_id )
            task_ids=doc.followup.getBoundTaskIds()

            for t_id in task_ids:
                doc.followup.deleteTask(t_id)

        #get_transaction().commit()

    def _create_docs(self):
        storage = self.naudoc.storage

        for i in range(0, self.number_of_documents):
            title = "%s %d" % (self.document_base_title, i)
            doc_id=self.cookId(i)

            storage.invokeFactory( type_name='HTMLDocument',
                                   id=doc_id,
                                   title=title,
                                   description='test description',
                                   category='Document' )

            #test that it was created
            obj = storage._getOb( doc_id )

        get_transaction().commit()

    def _create_users(self):
        for i in range(0, self.number_of_users):
            self._addUser(i)

        get_transaction().commit()

    def beforeTearDown(self):

        portal = self.naudoc
        #remove documents
        documents_ids = map(self.cookId, range(0, self.number_of_documents))
        for d_id in documents_ids:
            portal.storage.deleteObjects( [d_id] )

        #remove member data
        portal.portal_membership.deleteMembers( self.userids )

        #remove home folders as well
        #members = portal.getProperty( 'members_folder', None )
        #if members is not None:
        #    members.manage_delObjects( self.userids )

        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

    def cookId(self, i):
        return "%s%d" % (self.document_base_name, i)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(AssignTasksTest))
    return suite

if __name__ == '__main__':
    framework()
