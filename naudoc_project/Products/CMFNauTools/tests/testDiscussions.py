#! /bin/env python2.3
"""
Create and destroy NauDoc documents. Measure time needed.

$Id: testDiscussions.py,v 1.1 2005/12/09 15:12:02 vsafronovich Exp $
"""
__version__='$Revision: 1.1 $'[11:-2]

import os, sys
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

class DiscussionTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = False
    document_base_name = 'ztc_test_document_'
    document_base_title = 'NauDoc test case document'
    number_of_documents = Constants.FEW

    def afterSetUp(self):
        storage = self.naudoc._getOb('storage')
        
        storage.invokeFactory( type_name='HTMLDocument',
                               id=self.document_base_name,
                               title=self.document_base_title,
                               description='test description',
                               category='Document' )

        get_transaction().commit()

        self.doc = storage._getOb(self.document_base_name)

    def testDiscussionCreation(self):
        doc = self.doc

        dt = getToolByName(doc, 'portal_discussion')

        dcontainer = dt._createDiscussionFor( doc )
        self.assert_(hasattr(doc, 'talkback'))
        self.assertEquals(dcontainer.objectIds(), [])

        id = dcontainer.createReply('title1', 'text1', Creator='test_nd_user_1_') 

        self.assertEquals(id, 'discussion_001')
        self.assertEquals(dcontainer.objectIds(), ['discussion_001'])

        reply = dcontainer._getOb(id)
        self.assertEquals( reply.id , id)
        self.assertEquals( reply.Title() , 'title1')

    def beforeTearDown(self):
        #remove folders
        self.naudoc.storage.deleteObjects( [self.document_base_name] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(DiscussionTests) )
    return suite

if __name__ == '__main__':
    framework()

