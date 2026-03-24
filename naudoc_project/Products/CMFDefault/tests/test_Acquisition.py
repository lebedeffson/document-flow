#
# This test module demonstrates a problem caused by the removal of
# a few lines of code from cAccessControl.c and ImplPython.py:
# http://mail.zope.org/pipermail/zope-checkins/2004-August/028152.html
# http://zope.org/Collectors/CMF/259
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
from AccessControl.Permissions import view_management_screens

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

class ProtectedItem(SimpleItem):
    id = 'protected'
    security = ClassSecurityInfo()
    security.declareObjectProtected(view_management_screens)

InitializeClass(ProtectedItem)


params = 'name, default=None'
body = '''
from Products.CMFCore.utils import getToolByName
return getToolByName(context, name, default)
'''


class TestGetToolByName(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        try:

            # Set up a portal
            self.root.manage_addProduct['CMFDefault'].manage_addCMFSite('cmf')
            self.portal = self.root.cmf

            # Set up a manager user
            self.uf = self.portal.acl_users
            self.uf.userFolderAddUser('manager', '', ['Manager'], [])
            self.login('manager')

            # Make a string property we want to acquire later
            self.portal.manage_addProperty(id='simple_type', type='string', value='a string')

            # Make the objects we want to acquire from
            self.portal._setObject('allowed', AllowedItem())
            self.portal._setObject('denied', DeniedItem())
            self.portal._setObject('protected', ProtectedItem())

            # Make a script that calls getToolByName
            self._makePS(self.portal, 'get_tool_by_name', params, body)

        except:
            self.tearDown()
            raise

    def tearDown(self):
        self.logout()
        RequestTest.tearDown(self)

    def login(self, name):
        user = self.uf.getUserById(name)
        user = user.__of__(self.uf)
        newSecurityManager(None, user)

    def logout(self):
        noSecurityManager()

    def _makePS(self, context, id, params, body):
        context.manage_addProduct['PythonScripts'].manage_addPythonScript(id)
        context[id].ZPythonScript_edit(params, body)

    def testGetPortalCatalogByName(self):
        self.logout() # become Anonymous

        o = self.portal.allowed.get_tool_by_name('portal_catalog')
        self.failIfEqual(o, None)

        o = self.portal.denied.get_tool_by_name('portal_catalog')
        self.failIfEqual(o, None)

        # passes -> we can acquire portal_catalog
        o = self.portal.protected.get_tool_by_name('portal_catalog')
        self.failIfEqual(o, None)

    def testGetMailHostByName(self):
        self.logout() # become Anonymous

        o = self.portal.allowed.get_tool_by_name('MailHost')
        self.failIfEqual(o, None)

        # passes!
        o = self.portal.denied.get_tool_by_name('MailHost')
        self.failIfEqual(o, None)

        # XXX: fails -> we can *not* acquire MailHost
        o = self.portal.protected.get_tool_by_name('MailHost')
        self.failIfEqual(o, None)

    def testGetSimpleTypeByName(self):
        self.logout() # become Anonymous

        o = self.portal.allowed.get_tool_by_name('simple_type')
        self.failIfEqual(o, None)

        # passes!
        o = self.portal.denied.get_tool_by_name('simple_type')
        self.failIfEqual(o, None)

        # XXX: fails -> we can *not* acquire a simple type
        o = self.portal.protected.get_tool_by_name('simple_type')
        self.failIfEqual(o, None)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetToolByName))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
