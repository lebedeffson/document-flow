#! /bin/env python2.3
"""
Create and destroy NauDoc users. Measure time needed.

$Id: testUserCreation.py,v 1.1 2005/12/09 15:12:02 vsafronovich Exp $
"""
__version__='$Revision: 1.1 $'[11:-2]

import os, sys
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')




class UserRegistrationTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0
    _user_basename = 'test_user_'
    number_of_users = Constants.LARGE

    def testCreateUser(self):

        uf = self.naudoc.acl_users
        users_before = len( uf.getUsers() )

        for i in range(self.number_of_users):
            self._create_user(i)

        #some checks goes here...

        self.assertEqual( len(uf.getUsers()), self.number_of_users + users_before)

        #XXX: test users names, their data etc

        get_transaction().commit()

    def _create_user(self, number):

        username = self.cookUserId( number )
        email = 'foo%d@bar.baz' % number

        portal_membership=self.naudoc.portal_membership
        portal_registration = self.naudoc.portal_registration
        failMessage = portal_registration.testPropertiesValidity(
                                     {'username':username,
                                      'email':email
                                     } )
        roles = [ 'Member' ]

        REQUEST = self.app.REQUEST
        REQUEST['username'] = username

        password = REQUEST['password'] = REQUEST['confirm'] = 'secret'
        #REQUEST['home']=''
        #REQUEST['domains']=[]
        REQUEST['fname']='User'
        REQUEST['lname']='Userov%d' % number
        REQUEST['mname']='Testovich'

        REQUEST['groups']=['all_users']
        REQUEST['email']=email
        REQUEST['phone']=("%.3d" % number) * 3

        REQUEST['position']='tester %d' % number
        REQUEST['company']='Naumen'
        REQUEST['notes']='Notes goes here...'
        #REQUEST['noHome']='on' create home folder.

        member = portal_registration.addMember( username, password, roles, [], properties=REQUEST )

        portal_membership.setDefaultFilters( username )
        username = member.getUserName()
        home     = member.getHomeFolder( create=1 )

    def cookUserId(self, i):
        return '%s%d'%(self._user_basename, i)

    def beforeTearDown(self):

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




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UserRegistrationTests))
    return suite

if __name__ == '__main__':
    framework()
