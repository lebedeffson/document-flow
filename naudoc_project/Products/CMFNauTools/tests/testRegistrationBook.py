#! /bin/env python2.3
"""
Create and destroy NauDoc registration_book. Measure time needed.

$Id: testRegistrationBook.py,v 1.3 2006/02/15 13:23:17 ynovokreschenov Exp $
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
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.SimpleObjects import ItemBase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class RegistrationBookTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def testRegistrationBook(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        log_as_user = NauDocTestCase.admin_name
        storage = self.naudoc.storage.members
        
        # test registration_book_factory_form
        path = '/%s/registration_book_factory_form' % storage.absolute_url(1)
        extra = { 'type_name':'RegistrationBook' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test invoke_factory_form
        path = '/%s/invoke_factory_form' % storage.absolute_url(1)
        extra = { 'type_name':'RegistrationBook' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # test registration_book_add
        path = '/%s/registration_book_add' % storage.absolute_url(1)
        id = 'test_reg_book'
        title = id
        description = 'test description'
        cat_id = 'SimpleDocument'
        extra = { 'type_name':'RegistrationBook',
                  'id':id,
                  'title':title,
                  'description':description,
                  'cat_id':cat_id,
                  'create':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        obj = storage._getOb( id )

        self.assertEquals( obj.getId(), extra['id'] )
        self.assertEquals( obj.title, extra['title'] )
        self.assertEquals( obj.description, extra['description'] )
        self.assertEquals( obj.meta_type, extra['type_name'] )
        self.assertEquals( obj.category_id, extra['cat_id'] )

        # test registration_book_edit_form
        path = '/%s/registration_book_edit_form' % obj.absolute_url(1)
        extra = {}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # test registration_book_edit
        path = '/%s/registration_book_edit' % obj.absolute_url(1)
        extra = { 'title':'new_title',
                  'description':'new description',
                  'category':'Document',
                  'reg_no_attr':None,
                  'reg_no_rule':'\Seq',
                  'department':'test_department',
                  'dest_folder_uid':'qwe',
                  'change_counter':'change',
                  'last_id':'2',
                  'recency_period':'1',
                  'hide_registration_date':True,
                  'hide_creator':True,
                  'hide_version':True,

                  'meta':'State',
                  'add_meta_column':True,
                  
                  'save':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        self.assertEquals( obj.title, extra['title'] )
        self.assertEquals( obj.description, extra['description'] )
        self.assertEquals( obj.category_id, extra['category'] )
        self.assertEquals( obj.reg_no_attr_id, extra['reg_no_attr'] )
        self.assertEquals( obj.reg_no_forming_rule, extra['reg_no_rule'] )
        self.assertEquals( obj.department, extra['department'] )
        self.assertEquals( obj.papers_folder_uid, extra['dest_folder_uid'] )
        self.assertEquals( obj.safe_sequence.getLastValue(), extra['last_id'] )
        self.assertEquals( obj.recency_period, int(extra['recency_period']) )
        self.assertEquals( obj.hide_registration_date, int(extra['hide_registration_date']) )
        self.assertEquals( obj.hide_creator, int(extra['hide_creator']) )
        self.assertEquals( obj.hide_version, int(extra['hide_version']) )

        columns = [i.id for i in obj.listColumns()]
        self.assert_(extra['meta'] in columns)

        # creating additional column
        path = '/%s/registration_book_edit' % obj.absolute_url(1)
        extra = { 'category':'Document',
                  'meta':'Owner',
                  'add_meta_column':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        columns = [i.id for i in obj.listColumns()]
        self.assert_(extra['meta'] in columns)
        
        # test moveColumns
        i1 = columns.index('State')

        path = '/%s/moveColumn?direction:int=-1&id=State' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        columns = [i.id for i in obj.listColumns()]
        i2 = columns.index('State')
        self.assertEquals( i2, (i1+1) )
       
        # test registration_book_edit deleting columns
        path = '/%s/registration_book_edit' % obj.absolute_url(1)
        extra_del = { 'category':'Document',
                      'del_Owner':True,
                      'delete_columns':True,
                    }
        response = self.publish(path, basic_auth, extra=extra_del)
        self.assertResponse( response )        

        columns = [i.id for i in obj.listColumns()]
        self.assert_( extra['meta'] not in columns )

        storage.deleteObjects( [id] )

    def beforeTearDown(self):
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(RegistrationBookTests) )
    return suite

if __name__ == '__main__':
    framework()
