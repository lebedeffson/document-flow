#! /bin/env python2.3
"""

$Id: testRegister.py,v 1.3 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.3 $'[11:-2]

import os, sys
import Configurator

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

class RegisterUserTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        self.naudoc.storage.members.user_defaults.manage_addProduct['CMFNauTools']\
                                .addHTMLDocument('html_test' , category='Document')
        self.naudoc.portal_membership._addGroup( 'test_group' )
            
    def testForm(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/join_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

    def testRegisterUser(self):# Theese tests are using a valid valiables to confirm
                               # that there is no errors follows
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/register' % obj.absolute_url(1)
        error = '<p class="error">'

        # There is a new user adding with some parameters. Then theese parameters 
        # should be checked to confirm settings
        extra = {'username':'uname', 'email':'qwe@qwe.qwe', 'password':'qwe', \
                 'confirm':'qwe', 'home':'HomeFolder', 'groups':['test_group'],\
                 'lname':'popov', 'fname':'ivan', 'mname':'petrovich', 'company':'NauMen',\
                 'phone':'123', 'notes':'qwe\\nqwe', 'asManager':True,\
                 'noHome':False, 'noDefaults':False, 'mail_me':False, 'active':True}
        
        response = self.publish(path, basic_auth, extra=extra)
        if error in str(response):
            self.fail( 'Your password and confirmation did not match. Please try again.' )

        folder = self.naudoc.storage.members.uname
        if folder is None:
           self.fail('Error: The users folder is not created')

        member = self.naudoc.portal_membership.getMemberById( 'uname' )
        uname_roles = member.getRoles()
        uinfo = self.naudoc.portal_membership.getUserInfo( 'uname' )
        active_users = getToolByName(self.naudoc, 'portal_licensing').listActiveUsers()
        users = self.naudoc.portal_membership.listGroupMembers( 'test_group' )

        self.assert_( extra['username'] in self.naudoc.portal_membership.listMemberIds() )
        self.assert_( 'Manager' in member.getRoles() )
        self.assert_( 'uname' in active_users )
        self.assert_( member in users )
        self.assertEquals( self.naudoc.portal_membership.getMemberEmail( 'uname' ), extra['email'] )
        self.assertEquals( self.naudoc.portal_membership.getMemberName( 'uname' ), extra['lname'] \
                           + ' ' + extra['fname'] + ' ' + extra['mname'] )
        self.assertEquals( uinfo[ 'mname' ], extra['mname'] )
        self.assertEquals( uinfo[ 'company' ], extra['company'] )        
        self.assertEquals( uinfo[ 'phone' ], extra['phone'] )
        self.assertEquals( uinfo[ 'notes' ], extra['notes'] )
        self.assertEquals( member.getHomeFolder( create=1 ).title, extra['home'] )
        self.assertEquals( self.naudoc.storage.members.user_defaults.objectIds(), \
                           self.naudoc.storage.members.uname.objectIds() )

        # Checking: noDefaults = True, active = False, source_user=uname
        # (The rest parameters are the same as in the previous test)
        extra = {'username':'uname1', 'email':'qwe1@qwe.qwe', 'password':'qwe', \
                 'confirm':'qwe', 'home':'', 'groups':'',\
                 'lname':'sidirov', 'fname':'ivan', 'mname':'petrovich', 'company':'NauMen',\
                 'phone':'', 'notes':'qwe\\nqwe', 'asManager':True,\
                 'noHome':False, 'noDefaults':True, 'mail_me':False, 'active':False}

        response = self.publish(path, basic_auth, extra=extra)
        active_users = getToolByName(self.naudoc, 'portal_licensing').listActiveUsers()
        folder = self.naudoc.storage.members.uname1
        if folder is None:
           self.fail('Error: The users folder is not created')
        
        self.assert_( 'uname1' not in active_users )
        self.assertEquals( self.naudoc.storage.members.uname1.objectIds(), [] )
        # Checking: noHome = True
        extra = {'username':'uname2', 'email':'qwe2@qwe.qwe', 'password':'qwe', \
                 'confirm':'qwe', 'home':'', 'groups':['test_group'],\
                 'lname':'sidorov', 'fname':'ivan', 'mname':'petrovich', 'company':'NauMen',\
                 'phone':'', 'notes':'qwe\\nqwe', 'asManager':True,\
                 'noHome':True, 'noDefaults':True, 'mail_me':False, 'active':False}

        response = self.publish(path, basic_auth, extra=extra)
        
        folders = self.naudoc.storage.members.objectIds()
        if 'uname2' in folders:
            self.fail('Error: The users folder is created but it should not ')
        #Checking source_user=source_name
        extra_source = {'username':'source_name', 'email':'qwe@qwe.qwe', 'password':'qwe', \
                       'confirm':'qwe', 'home':'HomeFolder', 'groups':['test_group'],\
                       'lname':'popov', 'fname':'ivan', 'mname':'petrovich', 'company':'NauMen',\
                       'phone':'123', 'notes':'qwe\\nqwe', 'asManager':True,\
                       'noHome':False, 'noDefaults':False, 'mail_me':False, 'active':True}
        self.publish(path, basic_auth, extra=extra_source)
        
        extra_target = {'username':'target_name', 'email':'target@qwe.qwe', 'password':'qwe', \
                       'confirm':'qwe', 'home':'Hfolder', 'groups':'',\
                       'lname':'userlname', 'fname':'userfname', 'mname':'', 'company':'NauMen',\
                       'phone':'1233', 'notes':'qwe\\nqwe', 'source_user':'source_name', 'asManager':True,\
                       'noHome':False, 'noDefaults':False, 'mail_me':False, 'active':True}
        self.publish(path, basic_auth, extra=extra_target)

        source_user = extra_source['username']
        target_user = extra_target['username']

        portal_catalog = getToolByName( self.naudoc, 'portal_catalog' )
        source_users_groups = self.naudoc.storage.portal_membership.getMemberById( source_user,\
                                                                                  raise_exc=True ).getGroups()
        target_users_groups = self.naudoc.storage.portal_membership.getMemberById( target_user,\
                                                                                  raise_exc=True ).getGroups()
        self.assertEquals( source_users_groups, target_users_groups )

        source_users_allowed_folders = portal_catalog.unrestrictedSearch(allowedRolesAndUsers='user:'+source_user,\
                                                                         implements='isPrincipiaFolderish')
        target_users_allowed_folders = portal_catalog.unrestrictedSearch(allowedRolesAndUsers='user:'+target_user,\
                                                                         implements='isPrincipiaFolderish')

        source_list = []
        target_list = []
        for folder in source_users_allowed_folders:
            source_list.append( folder.getPath() )
        
        for folder in target_users_allowed_folders:
            target_list.append( folder.getPath() )

        for folder_path in source_list:
            self.assert_( folder_path in target_list )

        # Theese tests are using an invalid valiables. In theese cases tests should be failed.
        # In this case 'username' is invalid
        extra = {'username':'u name', 'email':'qwe@qwe.qwe', 'password':'qwe', \
                 'confirm':'qwe', 'domains':'', 'home':'home', 'lname':'popov',\
                 'fname':'ivan', 'mname':'qwe', 'company':'NauMEN', 'phone':'321321',\
                 'notes':'qwe\\newq', 'source_user':None, 'asManager':True, 'noHome':True,\
                 'noDefaults':True, 'mail_me':True, 'active':False}
        response = self.publish(path, basic_auth, extra=extra)
        if error not in str(response):
            self.fail( 'Your password and confirmation did not match. Please try again.' )

        # In this case 'password' and its confirmation are not the same
        extra = {'username':'uname', 'email':'qwe@qwe.qwe', 'password':'qwhe', \
                 'confirm':'qwe', 'domains':'', 'home':'home', 'lname':'popov',\
                 'fname':'ivan', 'mname':'qwe', 'company':'NauMEN', 'phone':'321321',\
                 'notes':'qwe\\newq', 'source_user':None, 'asManager':True, \
                 'noHome':True, 'noDefaults':True, 'mail_me':True, 'active':False}
        response = self.publish(path, basic_auth, extra=extra)
        if error not in str(response):
            self.fail( 'Your password and confirmation did not match. Please try again.' )

    def beforeTearDown(self):
        self.naudoc.storage.members.user_defaults.deleteObjects( ['html_test'] )
        self.naudoc.portal_membership._delGroups( ['test_group'] )
        self.naudoc.storage.members.deleteObjects( ['uname', 'uname1', 'source_name', 'target_name'] )
        self.naudoc.portal_membership.deleteMembers(['uname', 'uname1', 'source_name', 'target_name'])
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(RegisterUserTests) )
    return suite

if __name__ == '__main__':
    framework()
