"""
1. create  users

2. create  documents

3. assign  'information' tasks for each document

4. checking publish followup_report DTML

$Id: testFollowupReport.py,v 1.4 2006/01/29 14:41:12 vsafronovich Exp $
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

class FollowupReportTest( NauDocTestCase.NauFunctionalTestCase ):
    admin_password = 'secret'
    admin_name = NauDocTestCase.admin_name

    _remove_naudoc = 0
    document_base_title = 'ztc_test_followup_test_doc_'
    document_base_name = 'ztc_test_followup_test_doc_'
    user_base_name = 'ztc_test_followup_test_user'

    number_of_users = Constants.MEDIUM
    number_of_documents = Constants.FEW
    number_of_tasks = Constants.FEW

    def afterSetUp(self):
        self._create_docs()   #create  documents
        self._create_users()  #create  users
        self._assign_tasks()  #assign  'information' tasks for each document

    def testFollowupReport(self):
        self.path = '%s/followup_in' % self.naudoc.absolute_url(1)
        self.basic_auth = '%s:%s' % (self.admin_name, self.admin_password)
        extra={ 'showTaskMode':'all'
              }

        response = self.publish(self.path, self.basic_auth, extra=extra)
       
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
        portal_membership=self.naudoc.portal_membership
        portal_registration = self.naudoc.portal_registration

        for i in range(0, self.number_of_users):
            username = self.cookUserId( i )
            email = 'foo%d@bar.baz' % i

            failMessage = portal_registration.testPropertiesValidity(
                                             {'username':username,
                                              'email':email
                                             } )
            roles = [ 'Member' ]

            REQUEST = self.app.REQUEST
            REQUEST['username'] = username

            password = REQUEST['password'] = REQUEST['confirm'] = 'secret'
            REQUEST['fname']='User'
            REQUEST['lname']='Userov%d' % i
            REQUEST['mname']='Testovich'

            REQUEST['groups']=['all_users']
            REQUEST['email']=email
            REQUEST['phone']=("%.3d" % i) * 3

            REQUEST['position']='tester %d' % i
            REQUEST['company']='Naumen'
            REQUEST['notes']='Notes goes here...'
            #REQUEST['noHome']='on' create home folder.

            member = portal_registration.addMember( username, password, roles, [], properties=REQUEST )

            portal_membership.setDefaultFilters( username )
            username = member.getUserName()
            home     = member.getHomeFolder( create=1 )

        get_transaction().commit()


    def beforeTearDown(self):
        #remove documents
        documents_ids = map(self.cookId, range(0, self.number_of_documents))
        self.naudoc.storage.deleteObjects( documents_ids )

        #remove member data
        members_ids = map(self.cookUserId, range(self.number_of_users))
        self.naudoc.portal_membership.deleteMembers( members_ids )

        #remove home folders as well
        portal = self.naudoc.portal_url.getPortalObject()
        members = portal.getProperty( 'members_folder', None )
        if members is not None:
            members.manage_delObjects( members_ids )

        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

    def cookId(self, i):
        return "%s%d" % (self.document_base_name, i)

    def cookUserId(self, i):
        return '%s%d'%(self.user_base_name, i)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(FollowupReportTest))
    return suite


if __name__ == '__main__':
    framework()
