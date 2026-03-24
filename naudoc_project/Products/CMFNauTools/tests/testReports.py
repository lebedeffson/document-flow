#! /bin/env python2.3
"""

$Id: testReports.py,v 1.3 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.3 $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


import NauDocTestCase
from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')

class ReportsFunctionalTests( NauDocTestCase.NauFunctionalTestCase ):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def testRootTasks(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/followup_tasks_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testTasksProgress(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/followup_stat' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testDocReport(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/documents_stat' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testNDReport(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/followup_ndreport' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(ReportsFunctionalTests) )
    return suite

if __name__ == '__main__':
    framework()
