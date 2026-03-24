#! /bin/env python2.3
"""

$Id: testReconfig.py,v 1.4 2006/01/30 11:12:59 ynovokreschenov Exp $
"""
__version__='$Revision: 1.4 $'[11:-2]

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

class ConfigFormTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        self.naudoc.storage.manage_addProduct['CMFNauTools']\
                                                 .addFSFolder('test_members_folder')
        self.naudoc.storage.manage_addProduct['CMFNauTools']\
                                                 .addFSFolder('test_defaults_folder')
        self.naudoc.storage.manage_addProduct['CMFNauTools']\
                                                 .addFSFolder('test_templates_folder')
        self.naudoc.storage.manage_addProduct['CMFNauTools']\
                                                 .addFSFolder('test_messages_folder')
        self.naudoc.storage.manage_addProduct['CMFNauTools']\
                                                 .addFSFolder('test_scripts_folder')
        self.naudoc.storage.manage_addProduct['CMFNauTools']\
                                                 .addFSFolder('test_directories_folder')

    def testFormFunctional(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/reconfig' % obj.absolute_url(1)

        old_title = self.naudoc.portal_properties.getProperty( 'title' )
        old_description = self.naudoc.portal_properties.getProperty( 'description' )
        old_server_url = self.naudoc.portal_properties.getProperty( 'server_url' )
        old_email_from_name = self.naudoc.portal_properties.getProperty( 'email_from_name' )
        old_email_from_address = self.naudoc.portal_properties.getProperty( 'email_from_address' )
        old_smtp_server = self.naudoc.portal_properties.smtp_server()
        old_smtp_login = self.naudoc.portal_properties.smtp_login()
        old_smtp_password = self.naudoc.portal_properties.smtp_password()
        old_mail_pop = self.naudoc.portal_properties.mail_pop()
        old_mail_imap = self.naudoc.portal_properties.mail_imap()
        
        old_members_folder = self.naudoc.portal_properties.getProperty( 'members_folder' )
        new_members_folder = self.naudoc.storage.test_members_folder
        old_defaults_folder = self.naudoc.portal_properties.getProperty( 'defaults_folder' )
        new_defaults_folder = self.naudoc.storage.test_defaults_folder
        old_templates_folder = self.naudoc.portal_properties.getProperty( 'templates_folder' )
        new_templates_folder = self.naudoc.storage.test_templates_folder
        old_messages_folder = self.naudoc.portal_properties.getProperty( 'messages_folder' )
        new_messages_folder = self.naudoc.storage.test_messages_folder
        old_scripts_folder = self.naudoc.portal_properties.getProperty( 'scripts_folder' )
        new_scripts_folder = self.naudoc.storage.test_scripts_folder
        old_directories_folder = self.naudoc.portal_properties.getProperty( 'directories_folder' )
        new_directories_folder = self.naudoc.storage.test_directories_folder

        extra = { 'title':'portal_title', 'description':'qwe\\nqwe',\
                  'server_url':'http://localhost:8080', 'email_from_name':'test_name', \
                  'email_from_address':'test@email', 'smtp_server':'test_smtp', 'smtp_login':'test_smtp',\
                  'smtp_password':'qwe', 'mail_pop':'test_pop', 'mail_imap':'test_imap',\
                  'members_folder':new_members_folder, 'defaults_folder':new_defaults_folder,\
                  'templates_folder':new_templates_folder, 'messages_folder':new_messages_folder,\
                  'scripts_folder':new_scripts_folder, 'directories_folder':new_directories_folder }

        response = self.publish(path, basic_auth, extra=extra)
        
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'title' ), extra['title'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'description' ), extra['description'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'server_url' ), extra['server_url'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'email_from_name' ), extra['email_from_name'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'email_from_address' ), extra['email_from_address'] )
        self.assertEquals( self.naudoc.portal_properties.smtp_server(), extra['smtp_server'] )
        self.assertEquals( self.naudoc.portal_properties.smtp_login(), extra['smtp_login'] )
        self.assertEquals( self.naudoc.portal_properties.smtp_password(), extra['smtp_password'] )
        self.assertEquals( self.naudoc.portal_properties.mail_pop(), extra['mail_pop'] )
        self.assertEquals( self.naudoc.portal_properties.mail_imap(), extra['mail_imap'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'members_folder' ), extra['members_folder'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'defaults_folder' ), extra['defaults_folder'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'templates_folder' ), extra['templates_folder'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'messages_folder' ), extra['messages_folder'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'scripts_folder' ), extra['scripts_folder'] )
        self.assertEquals( self.naudoc.portal_properties.getProperty( 'directories_folder' ), extra['directories_folder'] )

        #clearing targets to temporary files
        extra = { 'title':old_title, 'description':old_description,\
                  'server_url':old_server_url, 'email_from_name':old_email_from_name, \
                  'email_from_address':old_email_from_address, 'smtp_server':old_smtp_server, 'smtp_login':old_smtp_login,\
                  'smtp_password':old_smtp_password, 'mail_pop':old_mail_pop, 'mail_imap':old_mail_imap,\
                  'members_folder':old_members_folder, 'defaults_folder':old_defaults_folder,\
                  'templates_folder':old_templates_folder, 'messages_folder':old_messages_folder,\
                  'scripts_folder':old_scripts_folder, 'directories_folder':old_directories_folder }

        response = self.publish(path, basic_auth, extra=extra)
    
    def beforeTearDown(self):
        self.naudoc.storage.deleteObjects( ['test_members_folder', 'test_defaults_folder',\
                                            'test_templates_folder', 'test_messages_folder',\
                                            'test_scripts_folder', 'test_directories_folder'] )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(ConfigFormTests) )
    return suite

if __name__ == '__main__':
    framework()
