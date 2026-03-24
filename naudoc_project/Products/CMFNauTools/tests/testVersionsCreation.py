"""
Creates 20 versions of document.

$Id: testVersionsCreation.py,v 1.1 2005/12/09 15:12:02 vsafronovich Exp $
"""
__version__='$ $'[11:-2]

import os, sys
import Configurator
Constants = Configurator.Constants

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
ZopeTestCase.installProduct('ExternalEditor')

class VersionsCreationTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    versions_count = Constants.LARGE

    def afterSetUp(self):
        storage = self.naudoc.storage
        storage.invokeFactory( type_name='HTMLDocument'
                              ,id='D0'
                              ,title='D0'
                              ,description='test description'
                              ,category='Document'
                             )
        get_transaction().commit()

    def testVersionsCreation(self):
        REQUEST = self.naudoc.REQUEST

        doc = self.naudoc.storage._getOb('D0')

        for i in range(self.versions_count):
            version = doc.getVersion()
            new_ver_id = doc.createVersion(ver_id=version.id, title=version.title, description=version.description)

        get_transaction().commit()

    def beforeTearDown(self):
        storage = self.naudoc.storage
        if storage._getOb('D0', None):
            storage.deleteObjects(['D0'])
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(VersionsCreationTests))
    return suite

if __name__ == '__main__':
    framework()
