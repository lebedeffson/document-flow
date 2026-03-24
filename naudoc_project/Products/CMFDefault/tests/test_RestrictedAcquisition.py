#
# This test module demonstrates a problem caused by the removal of
# a few lines of code from cAccessControl.c and ImplPython.c:
# http://mail.zope.org/pipermail/zope-checkins/2004-August/028152.html
#
# If an object with setDefaultAccess('deny') is used as the context for
# a PythonScript, the script can no longer aquire tools from the portal
# root. Rolling back the abovementioned checkin restores functionality.
#

from unittest import TestSuite, makeSuite, main
import Testing
import Zope
try:
    Zope.startup()
except AttributeError:
    pass

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from Products.CMFCore.tests.base.testcase import RequestTest


class AllowedItem(SimpleItem):
    id = 'allowed'
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

InitializeClass(AllowedItem)

class DeniedItem(SimpleItem):
    id = 'denied'
    security = ClassSecurityInfo()
    security.setDefaultAccess('deny')

InitializeClass(DeniedItem)


class BrokenAcquisitionTest(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        try:
            self.root.manage_addProduct['CMFDefault'].manage_addCMFSite('cmf')
            self.portal = self.root.cmf
            # Make us a Member
            self.uf = self.portal.acl_users
            self.uf.userFolderAddUser('member', '', ['Member'], [])
            newSecurityManager(None, self.uf.getUserById('member').__of__(self.uf))
            # Make our objects
            self.portal._setObject('allowed', AllowedItem())
            self.portal._setObject('denied', DeniedItem())
        except:
            self.tearDown()
            raise

    def tearDown(self):
        noSecurityManager()
        RequestTest.tearDown(self)

    def _makePS(self, context, id, params, body):
        factory = context.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript(id)
        ps = context[id]
        ps.ZPythonScript_edit(params, body)

    def testAcquisitionAllowed(self):
        self._makePS(self.portal, 'ps', '', 'print context.portal_membership')
        self.portal.allowed.ps()

    # This test fails in Zope 2.7.3. But it's a feature.
    # Also see http://zope.org/Collectors/CMF/259
    def DISABLED_testAcquisitionDenied(self):
        self._makePS(self.portal, 'ps', '', 'print context.portal_membership')
        self.portal.denied.ps()


def test_suite():                                                                                           
    suite = TestSuite()                                                                                     
    suite.addTest(makeSuite(BrokenAcquisitionTest))                                                           
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
