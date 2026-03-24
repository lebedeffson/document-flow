#! /bin/env python2.3
"""
Follow up Tests.

$Id: testFollowup.py,v 1.1 2005/12/09 15:12:02 vsafronovich Exp $
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

from Products.ZCatalog.Lazy import Lazy

class FollowupToolTests( NauDocTestCase.NauDocTestCase ):

    log_as_user = NauDocTestCase.admin_name

    def testFollowupMethods(self):
        tool = self.naudoc.portal_followup

        for name, attr in tool.__class__.__dict__.items():
            if name.startswith('_') or name.endswith('__roles__'):
                continue

            list = name.startswith('list')
            count = name.startswith('count')

            if not( list or count ):
                continue

            #print i[4:][:8]
            if name[4:][:8] not in ( 'Outgoing', 'Incoming', 'Supervis' ):
                continue

            res = attr(tool)
            self.assertEquals( len(res), 0 )
            self.assert_( isinstance( res, Lazy) )

        self.assertEquals( len(tool.searchTasks() ), 0 )
        self.assert_( isinstance( tool.searchTasks(), Lazy) )

    def beforeTearDown(self):
        self.naudoc.storage.deleteObjects( ['test'] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(FollowupToolTests))
    return suite

if __name__ == '__main__':
    framework()
