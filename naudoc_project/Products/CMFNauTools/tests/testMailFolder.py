#! /bin/env python2.3
"""
Create and destroy NauDoc mail folders. Measure time needed.

$Id: testMailFolder.py,v 1.4 2006/02/15 07:28:43 ynovokreschenov Exp $
"""
__version__='$Revision: 1.4 $'[11:-2]

import os, sys
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.SimpleObjects import ItemBase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class MailFoldersTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    incoming_folder = 'incoming_folder'
    outgoing_folder = 'outgoing_folder'

    def testIcomingFolder(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        log_as_user = NauDocTestCase.admin_name
        storage = self.naudoc.storage.members
        
        # test invoke_factory_form form
        path = '/%s/invoke_factory_form' % storage.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # test creation incoming_folder
        path = '/%s/invoke_factory' % storage.absolute_url(1)
        id = self.incoming_folder
        title = id
        description = 'test description'
        cat_id = 'Folder'
        extra = { 'type_name':'Incoming Mail Folder',
                  'id':id,
                  'title':title,
                  'description':description,
                  'cat_id':cat_id,
                  'attr/nomenclative_number':'123',
                  'attr/postfix':'qwe',
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        obj = storage._getOb( id )
        self.assertEquals( obj.getId(), extra['id'] )
        self.assertEquals( obj.title, extra['title'] )
        self.assertEquals( obj.description, extra['description'] )

        # testing attribute values
        portal_metadata = self.naudoc.portal_metadata
        category = portal_metadata.getCategoryById(cat_id)
        self.assertEquals( category.listAttributeDefinitions()[0].getValueFor(obj), extra['attr/nomenclative_number'] )
        self.assertEquals( category.listAttributeDefinitions()[1].getValueFor(obj), extra['attr/postfix'] )

        # test folder_edit_form for incoming_folder
        path = '/%s/folder_edit_form' % storage.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test folder_edit
        path = '/%s/folder_edit?mail_login=test_login&mail_password=123&mail_password2=123&mail_type=pop&mail_category=IncomingMail&mail_keep=1&mail_interval=10' % obj.absolute_url(1)
        extra = {'allowed_categories':['IncomingMail']}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        self.assertEquals( obj.mail_interval, 10 )
        self.assertEquals( obj.mail_login, 'test_login' )
        self.assertEquals( obj.mail_password, '123' )
        self.assertEquals( obj.mail_type, 'pop' )
        self.assertEquals( obj.mail_category, 'IncomingMail' )
        self.assertEquals( obj.mail_keep, True )

        # test deleting incoming_folder
        path = '/%s/folder_delete' % storage.absolute_url(1)
        extra = { 'ids':[id], 'folder_delete':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        try:
            storage._getOb( id )
        except AttributeError:
            pass
        else:
            self.fail('error deleting folder')

    def testOutgoingFolder(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        log_as_user = NauDocTestCase.admin_name
        storage = self.naudoc.storage.members
        
        # test invoke_factory_form form
        path = '/%s/invoke_factory_form' % storage.absolute_url(1)
        extra = { 'type_name':'Outgoing Mail Folder' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # test creation outgoing_folder
        path = '/%s/invoke_factory' % storage.absolute_url(1)
        id = self.outgoing_folder
        title = id
        description = 'test description'
        cat_id = 'Folder'
        extra = { 'type_name':'Outgoing Mail Folder',
                  'id':id,
                  'title':title,
                  'description':description,
                  'cat_id':cat_id,
                  'attr/nomenclative_number':'123',
                  'attr/postfix':'qwe',
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        obj = storage._getOb( id )
        self.assertEquals( obj.getId(), extra['id'] )
        self.assertEquals( obj.title, extra['title'] )
        self.assertEquals( obj.description, extra['description'] )
        
        # testing attribute values
        portal_metadata = self.naudoc.portal_metadata
        category = portal_metadata.getCategoryById(cat_id)
        self.assertEquals( category.listAttributeDefinitions()[0].getValueFor(obj), extra['attr/nomenclative_number'] )
        self.assertEquals( category.listAttributeDefinitions()[1].getValueFor(obj), extra['attr/postfix'] )
        
        # test folder_edit_form for incoming_folder
        path = '/%s/folder_edit_form' % storage.absolute_url(1)
        extra = { 'type_name':'Outgoing Mail Folder' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # test folder_edit
        path = '/%s/folder_edit?mail_from_name=test_name&mail_from_address=qwe@qwe.qwe&mail_recipients=asd@asd.asd' % obj.absolute_url(1)
        extra = {'allowed_categories':['OutgoingMail']}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        self.assertEquals( obj.mail_from_name, 'test_name' )
        self.assertEquals( obj.mail_from_address, 'qwe@qwe.qwe' )
        self.assertEquals( list(obj.mail_recipients), ['asd@asd.asd'] )

        # test deleting outgoing_folder
        path = '/%s/folder_delete' % storage.absolute_url(1)
        extra = { 'ids':[id], 'folder_delete':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        try:
            storage._getOb( id )
        except AttributeError:
            pass
        else:
            self.fail('error deleting folder')

    def beforeTearDown(self):
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(MailFoldersTests) )
    return suite

if __name__ == '__main__':
    framework()
