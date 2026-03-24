#! /bin/env python2.3

"""
Tests for Bisiness Procedure ( VDocument ) class

$Id: testVDocument.py,v 1.3 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.3 $'[11:-2]

import os, sys, random
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase

from Testing import ZopeTestCase

from DateTime import DateTime
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.Utils import getToolByName

import AccessControl.SecurityManagement, AccessControl.SpecialUsers

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
#ZopeTestCase.installProduct('TextIndexNG2')


class VDocumentCreationTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0
    document_base_name = 'ztc_test_document_'
    document_base_title = 'NauDoc test case document'
    number_of_documents = Constants.LARGE

    def testVDocumentCreation(self):
        storage = self.naudoc.storage

        for i in range(self.number_of_documents):
            id = self.cookId( i )
            title = "%s %d" % (self.document_base_title, i)

            storage.invokeFactory( type_name='Business Procedure',
                                       id=id,
                                       title=title,
                                       description='test description' )

            #test that it was created
            obj = storage._getOb( id )
            self.assert_( obj is not None )

        get_transaction().commit()
        #XXX tests needed

    def cookId(self, i):
        return '%s%d' % (self.document_base_name, i)

    def beforeTearDown(self):
        #remove folders
        documents_ids = map(self.cookId, range(self.number_of_documents))
        self.naudoc.storage.deleteObjects( documents_ids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )


#####-------------

class VDocFunctionalTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):

        self.naudoc.storage.manage_addProduct['CMFNauTools'].addVDocument('vdoc_test', 'vdoc', 'VDoc testing')
        self.d = self.naudoc.storage.vdoc_test

    def testView(self):
        path = '/%s/vdocument_view' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testOptions(self):
        path = '/%s/vdocument_options_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def beforeTearDown(self):
        del self.d

        self.naudoc.storage.deleteObjects(['vdoc_test'])
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

####-------------

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(VDocumentCreationTests) )
    #suite.addTest( makeSuite(VDocumentEditTests) )
    #suite.addTest( makeSuite(DocumentTests) )
    suite.addTest( makeSuite(VDocFunctionalTests) )
    return suite

if __name__ == '__main__':
    framework()
