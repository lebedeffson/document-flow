# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/tests/testRecurrentTask.py
# Compiled at: 2006-01-26 17:31:22
import os, sys, random, time
from Products.CMFNauTools.tests import Configurator
Constants = Configurator.Constants
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
from Products.CMFNauTools.tests import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName
from Products.NauScheduler.TemporalExpressions import TemporalExpression
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')
app = ZopeTestCase.app()
ZopeTestCase.utils.setupCoreSessions(app)
ZopeTestCase.close(app)

class RecurrentTaskFunctionalTests(NauDocTestCase.NauDocTestCase):
    __module__ = __name__
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    plan_time = 20
    duration = 100
    users_count = 3

    def afterSetUp(self):
        self.task_id = 'new_task'
        self.userids = []
        for number in range(self.users_count):
            self._addUser(number)

        folder = self.naudoc.storage
        self.task_container = getToolByName(folder, 'portal_followup')
        self.task_container = self.task_container._createFollowupFor(folder)
        title = 'New Recurrent'
        type = 'recurrent'
        plan_time = self.plan_time
        duration = self.duration
        temporal_expr = TemporalExpression(id='TE_Id', title='title')
        self.temporal_expr = temporal_expr
        involved_users = self.userids
        kw = {'duration': duration, 'temporal_expr': temporal_expr, 'involved_users': involved_users}
        self.recurrent = self.task_container.getTask(self.task_container.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
        get_transaction().commit()
        return

    def testPendingUsers(self):
        recurrent = self.recurrent
        self.assertEqual(recurrent.PendingUsers(), [])
        return

    def testInvolvedUsers(self):
        recurrent = self.recurrent
        self.assertEqual(recurrent.InvolvedUsers(), [])
        return

    def testSchedule(self):
        recurrent = self.recurrent
        new_duration = 50
        new_temporal_expr = TemporalExpression(id='new_id', title='new_title')
        recurrent.resetSchedule()
        schedule = recurrent.getSchedule()
        self.assertEqual(schedule.duration, self.duration)
        self.assertEqual(schedule.temporal_expr, self.temporal_expr)
        duration = new_duration
        temporal_expr = new_temporal_expr
        recurrent.setSchedule(temporal_expr=temporal_expr, duration=duration)
        schedule = recurrent.getSchedule()
        self.assertEqual(schedule.duration, new_duration)
        self.assertEqual(schedule.temporal_expr, new_temporal_expr)
        recurrent.resetSchedule()
        schedule = recurrent.getSchedule()
        self.assertEqual(schedule.duration, new_duration)
        self.assertEqual(schedule.temporal_expr, new_temporal_expr)
        return

    def testListAllowedResponseTypes(self):
        recurrent = self.recurrent
        self.assertEqual(recurrent.listAllowedResponseTypes(uname=None), [])
        return

    def testCanSendNotifications(self):
        recurrent = self.recurrent
        for i in range(self.users_count):
            self.login(self.userids[i])
            self.assert_(not recurrent.canSendNotifications())

        self.login
        return

    def beforeTearDown(self):
        self.recurrent.deleteObject()
        del self.task_container
        self.naudoc.portal_membership.deleteMembers(self.userids)
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RecurrentTaskFunctionalTests))
    return suite
    return


if __name__ == '__main__':
    framework()
