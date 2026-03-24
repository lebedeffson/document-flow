#! /bin/env python2.3

"""
Tests for TabularReport class

$Id: testTabularReport.py,v 1.3 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.3 $'[11:-2]

import os, sys, random
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class TabularReportCreationTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0
    report_base_name = 'ztc_test_document_'
    report_base_title = 'NauDoc test case document'
    reports_count = Constants.LARGE

    def testTabularReportCreation(self):
        storage = self.naudoc.storage

        for i in range(self.reports_count):
            id = self.cookId( i )
            title = "%s %d" % (self.report_base_title, i)

            storage.invokeFactory( type_name='Tabular Report',
                                       id=id,
                                       title=title,
                                       category='SimplePublication' )

            #test that it was created
            obj = storage._getOb( id )
            self.assert_( obj is not None )

        get_transaction().commit()

    def cookId(self, i):
        return '%s%d' % (self.report_base_name, i)

    def beforeTearDown(self):
        #remove reports
        reports_ids = map(self.cookId, range(self.reports_count))
        self.naudoc.storage.deleteObjects( reports_ids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )


#####-------------

class TabularReportFunctionalTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        self.naudoc.storage.manage_addProduct['CMFNauTools']\
                   .addReport('report_test', 'TabularReport')
        self.d = self.naudoc.storage.report_test

    def testReportView(self):
        path = '/%s/report_view' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

    def testReportOptionsForm(self):
        path = '/%s/report_options_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

    def testMetadataEditForm(self):
        path = '/%s/metadata_edit_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

    def beforeTearDown(self):
        del self.d
        self.naudoc.storage.deleteObjects(['report_test'])
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

####-------------

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(TabularReportCreationTests) )
    suite.addTest( makeSuite(TabularReportFunctionalTests) )
    return suite

if __name__ == '__main__':
    framework()
