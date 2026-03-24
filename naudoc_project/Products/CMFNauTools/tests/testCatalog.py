#! /bin/env python2.3
"""
Follow up Tests.

$Id: testCatalog.py,v 1.1 2005/12/09 15:12:02 vsafronovich Exp $
$Editor: vsafronovich $
"""
__version__='$Revision: 1.1 $'[11:-2]

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase

ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('TextIndexNG2')

class CatalogToolTests( NauDocTestCase.NauDocTestCase ):

    log_as_user = NauDocTestCase.admin_name

    def testgetObjectByUid(self):
        tool = self.naudoc.portal_catalog

        storage = tool.getObjectByUid( self.naudoc.storage.getUid() )

        self.assert_( storage is not None )

    def testserachResults(self):
        tool = self.naudoc.portal_catalog

        results = tool.searchResults()

        self.assert_( len(results) > 0 )

    def beforeTearDown(self):
        self.naudoc.storage.deleteObjects( ['test'] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(CatalogToolTests) )
    return suite

if __name__ == '__main__':
    framework()
