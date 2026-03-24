# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/tests/testRequestTask.py
# Compiled at: 2006-01-26 17:31:22
import os, sys, random
from Products.CMFNauTools.tests import Configurator
Constants = Configurator.Constants
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
from Products.CMFNauTools.tests import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')
app = ZopeTestCase.app()
ZopeTestCase.utils.setupCoreSessions(app)
ZopeTestCase.close(app)

class RequestTaskFunctionalTests(NauDocTestCase.NauDocTestCase):
    __module__ = __name__
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    plan_time = 20
    duration = 100
    users_count = 3

    def afterSetUp(self):
        self.task_id = 'new_task'
        self.userids = []
        self.ordered = True
        for number in range(self.users_count):
            self._addUser(number)

        folder = self.naudoc.storage
        self.task_container = getToolByName(folder, 'portal_followup')
        self.task_container = self.task_container._createFollowupFor(folder)
        title = 'New Request'
        type = 'request'
        plan_time = self.plan_time
        duration = self.duration
        involved_users = self.userids
        kw = {'duration': duration, 'involved_users': involved_users, 'ordered': (self.ordered)}
        self.request = self.task_container.getTask(self.task_container.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
        get_transaction().commit()
        return

    def testOnFinalize(self):
        request = self.request
        REQUEST = self.app.REQUEST
        result_code = 'success'
        request.onFinalize(REQUEST=REQUEST, result_code=result_code)
        self.assert_(request.isFinalized())
        return

    def testNotifiedUsers(self):
        request = self.request
        self.assertEqual(request.notifiedUsers(), self.userids)
        return

    def testIsOrdered(self):
        request = self.request
        self.assertEqual(request.isOrdered(), self.ordered)
        return

    def testPendingUsers(self):
        request = self.request
        request.ordered = True
        REQUEST = self.app.REQUEST
        self.assertEqual(request.PendingUsers(), [self.userids[0]])
        request.ordered = False
        self.assertEqual(request.PendingUsers(), self.userids)
        request.ordered = self.ordered
        self.assertEqual(request.PendingUsers(), [self.userids[0]])
        self.login(self.userids[0])
        status = 'satisfy'
        request.Respond(status=status, REQUEST=REQUEST)
        self.assertEqual(request.PendingUsers(), [self.userids[1]])
        self.login()
        return

    def testInvolvedUsers(self):
        request = self.request
        REQUEST = self.app.REQUEST
        kw = {}
        request.ordered = True
        self.assertEqual(request.InvolvedUsers(**kw), [self.userids[0]])
        request.ordered = False
        self.assertEqual(request.InvolvedUsers(**kw), self.userids)
        request.ordered = self.ordered
        self.login(self.userids[0])
        status = 'reject'
        request.Respond(status=status, REQUEST=REQUEST)
        self.assertEqual(request.InvolvedUsers(), [self.userids[0], self.userids[1]])
        self.login()
        return

    def beforeTearDown(self):
        self.request.deleteObject()
        del self.task_container
        self.naudoc.portal_membership.deleteMembers(self.userids)
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RequestTaskFunctionalTests))
    return suite
    return


if __name__ == '__main__':
    framework()
