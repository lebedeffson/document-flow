#! /bin/env python2.3
"""
Tests for class ActionInformation.

$Id: testActions.py,v 1.2 2006/02/06 08:12:41 vsafronovich Exp $
$Editor: vsafronovich $
"""
__version__='$Revision: 1.2 $'[11:-2]

import os, sys
import Configurator

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

class ActionsTests( NauDocTestCase.NauDocTestCase ):

    _remove_naudoc = False
    log_as_user = NauDocTestCase.admin_name

    def testMenuActions(self):
        actions_dict = self.naudoc.portal_actions.listFilteredActionsFor( self.naudoc )

        self.assert_( actions_dict.has_key('menu') )
        menu_actions = actions_dict['menu']
      
        menu_actions_ids = [ a['id'] for a in menu_actions ]

        self.assert_( 'navTree' in menu_actions_ids )

    def testReportActions(self):
        actions_dict = self.naudoc.portal_actions.listFilteredActionsFor( self.naudoc )

        self.assert_( actions_dict.has_key('report') )
        menu_actions = actions_dict['report']
      
        menu_actions_ids = [ a['id'] for a in menu_actions ]

        self.assert_( 'followup_stat' in menu_actions_ids )



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ActionsTests))
    return suite

if __name__ == '__main__':
    framework()
