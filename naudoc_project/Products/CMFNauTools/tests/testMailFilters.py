#! /bin/env python2.3
"""
Create and destroy NauDoc mail folders. Measure time needed.

$Id: testMailFilters.py,v 1.2 2006/02/15 07:29:18 ynovokreschenov Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

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

class MailFiltersTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    incoming_folder = 'incoming_folder'

    def afterSetUp(self):
        storage = self.naudoc.storage.members
        id = self.incoming_folder
        title = id
        description = 'test description'
        cat_id = 'Folder'
        storage.invokeFactory( type_name='Incoming Mail Folder',
                               id=id,
                               
                               title=title,
                               description=description,
                               category=cat_id
                             )

        self.folder_id = 'test_folder'
        storage.invokeFactory( type_name='Heading',
                               id=self.folder_id,
                               
                               title='title',
                               description='test description',
                               category='Folder'
                             )
        
    def testIcomingFolderFilters(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        log_as_user = NauDocTestCase.admin_name
        storage = self.naudoc.storage.members     
        id = self.incoming_folder
        obj = storage._getOb( id )

        # test mail_filters_form form
        path = '/%s/mail_filters_form' % obj.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response ) 

        # test mail_filter_handler
        title = 'test_filter'
        path = '/%s/mail_filter_handler' % obj.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder',
                  'title':title,
                  'add_filter':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test mail_filter_handler
        folder_id = self.folder_id
        folder_obj = storage._getOb( folder_id )

        path = '/%s/mail_filter_handler' % obj.absolute_url(1)
        test_filter_id = title
        action = ['mail_filter_move', 'mail_filter_delete', 'mail_filter_copy', 'mail_filter_default']
        dest_folder = folder_obj
        extra = { 'type_name':'Incoming Mail Folder',
                  'id':test_filter_id,
                  
                  'title':title,
                  'action':action[0],
                  'param/destination':dest_folder,
                  'save_filter':True,
                }
        
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        filter = obj.getFilter(test_filter_id)
        self.assertEquals( filter.title, extra['title'] )
        self.assertEquals( filter.id, extra['id'] )

        ai = filter.getActionInfo( extra['action'] )
        self.assert_( ai.getParameters() is not [])

        # test add new condition
        path = '/%s/mail_filter_handler' % obj.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder',
                  'id':test_filter_id,
                  
                  'test':'sender',
                  'operation':'+',
                  'header':'test_header',
                  'patterns':'test_patterns',
                  'add_test':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        self.assert_(obj.getFilter(test_filter_id) is not None)
        filter = obj.getFilter(test_filter_id)

        test_values = filter.tests[0].values()
        self.assertEquals( test_values[1], [extra['patterns']] )
        self.assertEquals( test_values[2], extra['test'] )
        self.assertEquals( test_values[4], extra['operation'] )

        # test set conditions
        path = '/%s/mail_filter_handler' % obj.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder',
                  'id':test_filter_id,
                  
                  'selected':[0],
                  'patternrec':{'0':'qwe'},
                  'save_filter':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        test_values = filter.tests[0].values()
        self.assertEquals( test_values[1], [extra['patternrec']['0']] )
        
        # test delete conditions
        path = '/%s/mail_filter_handler' % obj.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder',
                  'id':test_filter_id,
                  
                  'selected':[0],
                  'delete_tests':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        try:
            filter.tests[0].values()
        except IndexError:
            pass
        else:
            self.fail('error deleting')
            
        # test enable filters
        path = '/%s/mail_filter_handler' % obj.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder',
                  
                  'selected':[test_filter_id],
                  'enable_filters':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        filter = obj.getFilter(test_filter_id)
        self.assert_( filter.enabled )

        # test enable filters
        path = '/%s/mail_filter_handler' % obj.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder',
                  
                  'selected':[test_filter_id],
                  'disable_filters':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        filter = obj.getFilter(test_filter_id)
        self.assert_( not filter.enabled )

        # test delete filters
        path = '/%s/mail_filter_handler' % obj.absolute_url(1)
        extra = { 'type_name':'Incoming Mail Folder',
                  
                  'selected':[test_filter_id],
                  'delete_filters':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        try:
            obj.getFilter(test_filter_id)
        except KeyError:
            pass
        else:
            self.fail('error deleting folder')
                
    def beforeTearDown(self):
        storage = self.naudoc.storage.members 
        storage.deleteObjects( [self.folder_id, self.incoming_folder] )
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(MailFiltersTests) )
    return suite

if __name__ == '__main__':
    framework()
