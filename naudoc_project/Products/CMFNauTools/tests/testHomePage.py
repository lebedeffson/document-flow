#! /bin/env python2.3
"""
Test user home folder.

$Id: testHomePage.py,v 1.2 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


import NauDocTestCase

from Testing import ZopeTestCase

from Products.CMFNauTools import NauSite
from Products.CMFNauTools.Utils import getToolByName

import AccessControl.SecurityManagement, AccessControl.SpecialUsers

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')
#ZopeTestCase.installProduct('Sessions')

class HomePageTests(NauDocTestCase.NauFunctionalTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    def testHomePage(self):
        path = '/%s/home' % self.naudoc.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(HomePageTests))
    return suite

if __name__ == '__main__':
    framework()
