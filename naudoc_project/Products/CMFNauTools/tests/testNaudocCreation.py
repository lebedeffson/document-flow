#! /bin/env python2.3
"""
Test NauDoc object creation.

$Id: testNaudocCreation.py,v 1.3 2005/12/14 08:55:01 vsafronovich Exp $

"""
__version__='$Revision: 1.3 $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase # for patches

from Products.CMFNauTools import NauSite
from Products.CMFNauTools.Heading import Heading
from Products.CMFNauTools.WorkflowTool import WorkflowTool
from Products.CMFNauTools.CatalogTool import CatalogTool
from Products.CMFNauTools.SimpleObjects import ItemBase
from Products.Localizer.MessageCatalog import MessageCatalog
from Products.NauScheduler.Scheduler  import Scheduler

ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('TextIndexNG2')

naudoc_id = 'test_docs_1_'

user_role = 'Manager'

class testNaudocCreate(ZopeTestCase.ZopeTestCase):

    def _setupUser(self):
        '''
            Creates the default user.
            We want him to be a manager.
        '''
        uf = self.folder.acl_users
        uf.userFolderAddUser(ZopeTestCase.user_name, 'secret', [user_role], [])

    def testCreation(self):
        #Just create NauDoc object in folder and test it.
        called = {}

        old = ItemBase._instance_onCreate
        def _instance_onCreate(self):
            old(self)
            uid = self.physical_path()
            called[uid] = called.get(uid,0) + 1

        ItemBase._instance_onCreate = _instance_onCreate
        try:
            NauSite.manage_addNauSite( \
            self.folder,
            id=naudoc_id,
            title='NauDoc',
            description='',
            email_from_address=None,
            email_from_name=None,
            validate_email=0,
            language='ru',
            stemmer='russian')
        finally:
            ItemBase._instance_onCreate = old

        get_transaction().commit()

        len_called = len(called)
        not_one_called = [ '%s called %d' % (k,v) for k,v in called.items() if v!=1 ]
        self.assertEquals( called.values().count(1), len_called
                         , '\n'.join(not_one_called) )

        #test that instance created
        docs_instance = getattr(self.folder, naudoc_id, None)
        self.assert_( docs_instance )
        self.assert_( isinstance( docs_instance, NauSite.NauSite) )
        self.assert_( docs_instance.physical_path() in called )

        #test some tools were created
        msg = getattr( docs_instance,  'msg', None )
        self.assert_( msg )
        self.assert_( isinstance( msg, MessageCatalog) )

        scheduler = getattr( docs_instance,  'portal_scheduler', None )
        self.assert_( scheduler )
        self.assert_( isinstance( scheduler, Scheduler) )
        self.assert_( scheduler.physical_path() in called )

        workflow = getattr( docs_instance,  'portal_workflow', None )
        self.assert_( workflow )
        self.assert_( isinstance( workflow, WorkflowTool) )
        self.assert_( workflow.physical_path() in called )

        catalog = getattr( docs_instance,  'portal_catalog', None )
        self.assert_( catalog )
        self.assert_( isinstance( catalog, CatalogTool) )
        self.assert_( catalog.physical_path() in called )

        storage = getattr( docs_instance,  'storage', None )
        self.assert_( storage )
        self.assert_( isinstance( storage, Heading) )
        self.assert_( storage.physical_path() in called )


    def beforeTearDown(self):
        try:
            self.folder._delObject( naudoc_id )
        except:
            pass
        try:
            self.app._delObject(ZopeTestCase.folder_name)
        except:
            pass
        get_transaction().commit()

class testNaudocDestroy(ZopeTestCase.ZopeTestCase):
    def testCreation(self):
        #Just create NauDoc object in folder and test it.
        NauSite.manage_addNauSite( \
            self.folder,
            id=naudoc_id,
            title='NauDoc',
            description='',
            email_from_address=None,
            email_from_name=None,
            validate_email=0,
            language='ru',
            stemmer='russian')

        get_transaction().commit()
        naudoc_path = self.folder._getOb( naudoc_id ).physical_path()

        called = {}

        def _containment_onDelete(self, item, container):
            uid = self.physical_path()
            called[uid] = called.get(uid,0) + 1

        old = ItemBase._containment_onDelete
        ItemBase._containment_onDelete = _containment_onDelete
        try:
            self.folder._delObject( naudoc_id )
        finally:
            ItemBase._containment_onDelete = old

        get_transaction().commit()
     
        len_called = len(called)
        self.assert_( naudoc_path + '/storage' in called )
        #print called.values().count(2)
        not_one_called = [ '%s called %d' % (k,v) for k,v in called.items() if v!=1 ]
        self.assertEquals( called.values().count(1), len_called
                         , '\n'.join(not_one_called) )
        
    def beforeTearDown(self):
        try:
            self.app._delObject(ZopeTestCase.folder_name)
        except:
            pass
        get_transaction().commit()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testNaudocCreate))
    suite.addTest(makeSuite(testNaudocDestroy))
    return suite

if __name__ == '__main__':
    framework()
