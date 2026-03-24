"""
Test user storage folder.

$Id: testStorage.py,v 1.1 2005/12/09 15:12:02 vsafronovich Exp $
"""
__version__='$ $'[11:-2]

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFNauTools import NauSite

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')

# Open ZODB connection
app = ZopeTestCase.app()

# Set up sessioning objects
ZopeTestCase.utils.setupCoreSessions(app)

# Close ZODB connection
ZopeTestCase.close(app)

class StorageTests(NauDocTestCase.NauFunctionalTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        # Put SESSION object into REQUEST
        request = self.app.REQUEST
        sdm = self.app.session_data_manager
        request.set('SESSION', sdm.getSessionData())
        self.session = request.SESSION

    def testStorageView(self):
        naudoc = self.app._getOb( self.naudoc_id )
 
        # test default view
        naudoc.storage()

        path = '/%s/folder/' % self.naudoc.storage.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(StorageTests))
    return suite

if __name__ == '__main__':
    framework()
