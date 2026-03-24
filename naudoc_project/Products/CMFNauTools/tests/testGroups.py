#! /bin/env python2.3
"""

$Id: testGroups.py,v 1.3 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.3 $'[11:-2]

import os, sys
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

# Tests for manage_groups_form
class ManageGroupsFormTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        pass

    def testAddGroup(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/manage_groups' % obj.absolute_url(1)

        extra = { 'group':'test_group', 'addGroup':True }
        response = self.publish(path, basic_auth, extra=extra)
        group_list = []
        for groups in self.naudoc.portal_membership.listGroups():
            group_list.append( groups.title )

        self.assert_( 'test_group' in group_list )
        self.naudoc.portal_membership._delGroups( ['test_group'] )

    def testDelGroup(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/manage_groups' % obj.absolute_url(1)

        self.naudoc.portal_membership._addGroup( 'test_group' )
        extra = { 'groups':['test_group'], 'delGroup':True }
        response = self.publish(path, basic_auth, extra=extra)
        group_list = []
        for groups in self.naudoc.portal_membership.listGroups():
            group_list.append( groups.title )

        self.assert_( 'test_group' not in group_list )

    def testEditGroup(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/manage_groups' % obj.absolute_url(1)

        self.naudoc.portal_membership._addGroup( 'test_group' )
        extra = { 'groups':['test_group'] }
        response = self.publish(path, basic_auth, extra=extra)
        if 'OK' not in str(response):
            self.fail( 'Error: group_edit_form does not loaded!' )

        self.naudoc.portal_membership._delGroups( ['test_group'] )


    def beforeTearDown(self):
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )

# Tests for group_edit_form
class GroupEditFormTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    _user_basename = 'test_user_'
    number_of_users = Constants.FEW
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        self.naudoc.portal_membership._addGroup( 'first_users_group' )
        self.naudoc.portal_membership._addGroup( 'second_users_group', 'title' )

    def testGroupEditFormAppear(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/group_edit_form' % obj.absolute_url(1)

        self.naudoc.portal_membership._addGroup( 'test_group' )
        extra = { 'group_id':'test_group' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        self.naudoc.portal_membership._delGroups( ['test_group'] )

    def testGroupEditForm(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/group_edit_handler' % obj.absolute_url(1)

        for i in range(self.number_of_users):
            self._create_user(i)

        test_users = self.naudoc.portal_membership.listMemberIds()
        self.naudoc.portal_membership.manage_changeGroup( group='first_users_group', group_users=test_users )

        first_group = self.naudoc.portal_membership.getGroup( 'first_users_group' )
        first_group_users = first_group.listMemberIds()
        
        extra = { 'group':'second_users_group', 'title':'test_title', 'group_users':first_group_users }
        response = self.publish(path, basic_auth, extra=extra)

        second_group = self.naudoc.portal_membership.getGroup( 'second_users_group' )
        second_group_users = second_group.listMemberIds()

        self.assertEquals( first_group_users, second_group_users )
        self.assertEquals( second_group.Title(), extra['title'] )

        self.naudoc.portal_membership.deleteMembers(test_users)
      
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
        REQUEST['fname']='User'
        REQUEST['lname']='Userov%d' % number
        REQUEST['mname']='Testovich'
        REQUEST['groups']=['all_users']
        REQUEST['email']=email
        REQUEST['phone']=("%.3d" % number) * 3
        REQUEST['position']='tester %d' % number
        REQUEST['company']='Naumen'
        REQUEST['notes']='Notes goes here...'

        member = portal_registration.addMember( username, password, roles, [], properties=REQUEST )

        portal_membership.setDefaultFilters( username )
        username = member.getUserName()
        home     = member.getHomeFolder( create=1 )

    def cookUserId(self, i):
        return '%s%d'%(self._user_basename, i)

    def beforeTearDown(self):
        self.naudoc.portal_membership._delGroups( ['first_users_group', 'second_users_group'] )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(ManageGroupsFormTests) )
    suite.addTest( makeSuite(GroupEditFormTests) )
    return suite

if __name__ == '__main__':
    framework()
