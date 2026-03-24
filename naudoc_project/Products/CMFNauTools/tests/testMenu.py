#! /bin/env python2.3
"""

$Id: testMenu.py,v 1.2 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

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

class MenuFunctionalTests( NauDocTestCase.NauFunctionalTestCase ):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def testMenuTools(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/listGroupActions' % obj.absolute_url(1)
        extra = {'type':'global'}
        response = self.publish(path, basic_auth, extra=extra)

        self.assertResponse( response )

    def testMenuTree(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/navTree' % obj.absolute_url(1)
        extra = {'disable_dynamic':0}
        response = self.publish(path, basic_auth, extra=extra)

        self.assertResponse( response )

    def testMenuFollowup(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/followup_menu' % obj.absolute_url(1)
        extra = {'disable_dynamic':0}
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testMenuSearch(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/search_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testMenuUser(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/listGroupActions' % obj.absolute_url(1)
        extra = {'type':'user'}
        response = self.publish(path, basic_auth, extra=extra)

        self.assertResponse( response )


    def testMenuArchive(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/navTree' % obj.absolute_url(1)
        extra = {'disable_dynamic':0, 'arch':1}
        response = self.publish(path, basic_auth, extra=extra)

        self.assertResponse( response )

    def testMenuHelp(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        # get the script with params
        obj  = self.naudoc
        path = '/%s/listGroupActions' % obj.absolute_url(1)
        extra = {'type':'help'}
        response = self.publish(path, basic_auth, extra=extra)

    def testFavorites(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        # get the script with params
        obj  = self.naudoc
        path = '/%s/member_favorites' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(MenuFunctionalTests) )
    return suite

if __name__ == '__main__':
    framework()
