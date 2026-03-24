#! /bin/env python2.3
"""
Tests for absolute_url and relative_url.

$Id: testResponseCollection.py,v 1.1 2005/12/09 15:12:02 vsafronovich Exp $
$Editor: vsafronovich $
"""
__version__='$Revision: 1.1 $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase

from Zope2 import zpublisher_validated_hook

ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')

import transaction
from Products.CMFNauTools.ResponseCollection import ResponseCollection

class ResponceCollectionTests( NauDocTestCase.NauDocTestCase ):

    _remove_naudoc = False
    log_as_user = NauDocTestCase.admin_name

    _default_values = ( {'layer':'1', 'status':'commit', 'member':'user1'}
                      , {'layer':'1', 'status':'reject', 'member':'user1'}
                      , {'layer':'1', 'status':'reject', 'member':'user2'}
                      , {'layer':'2', 'status':'commit', 'member':'user2'}
        )

    def afterSetUp(self):
        self.responses = self.naudoc.test_responses = ResponseCollection()

        transaction.commit()

    def _populateCollection(self):
        responses = self.responses
        for item in self._default_values:
            responses.addResponse( **item )

        transaction.commit()

    def testSearch(self):
        self._populateCollection()
        responses = self.responses
        self.assertEquals( list(responses._searchResponsesIds( status='commit'))
                         , [1,4] )
        self.assertEquals( list(responses._searchResponsesIds()) # test all
                         , [1,2,3,4] )
        self.assertEquals( list(responses._searchResponsesIds(response_id=[1,2])) # test response_id index
                         , [1,2] )
        self.assertEquals( list(responses._searchResponsesIds( status=['commit','reject'])) # test multiple query
                         , [1,2,3,4] )

        self.assertEquals( list(responses.getIndexKeys( 'status' ))
                         , ['commit', 'reject'] )
        

    def beforeTearDown(self):
        del self.naudoc.test_responses
        transaction.commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ResponceCollectionTests))
    return suite

if __name__ == '__main__':
    framework()
