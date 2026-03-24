# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/tests/testElaboratedTask.py
# Compiled at: 2006-01-26 17:31:22
import os, sys, random, DateTime, DateTime.DateTime
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

class ElaboratedTaskCreationTests(NauDocTestCase.NauDocTestCase):
    __module__ = __name__
    plan_time = 100
    duration = 100

    def afterSetUp(self):
        folder = self.naudoc.storage
        self.task_container = getToolByName(folder, 'portal_followup')
        self.task_container = self.task_container._createFollowupFor(folder)
        self.userids = []
        return

    def testCreateWithItems(self):
        self.task_id = 'new_task'
        brains_types = [2, 3, 4, 5, 6]
        for number in range(len(brains_types)):
            self._addUser(number)

        task_list = []
        for i in range(len(brains_types)):
            title = 'New Information Task%d' % i
            brains_type = brains_types[i]
            duration = Constants.HUGE
            involved_users = [self.userids[i]]
            kw = {'duration': duration, 'involved_users': involved_users, 'brains_type': brains_type, 'description': 'he-he', 'expiration_date': (DateTime.DateTime())}
            task = kw
            task_list.append(task)

        title = 'New Elaborated'
        type = 'elaborated'
        plan_time = self.plan_time
        duration = self.duration
        kw = {'duration': duration, 'items': task_list}
        self.elaborated = self.task_container.getTask(self.task_container.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
        get_transaction().commit()
        return

    def testCreateWithOutItems(self):
        title = 'New Elaborated'
        type = 'elaborated'
        plan_time = Constants.LARGE
        duration = Constants.HUGE
        kw = {'duration': duration, 'items': []}
        self.elaborated = self.task_container.getTask(self.task_container.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
        return

    def beforeTearDown(self):
        self.elaborated.deleteObject()
        self.naudoc.portal_membership.deleteMembers(self.userids)
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


class ElaboratedTaskFunctionalTests(NauDocTestCase.NauFunctionalTestCase):
    __module__ = __name__
    _remove_naudoc = 0
    task_list = []
    log_as_user = NauDocTestCase.admin_name
    users_count = task_count = 5

    def afterSetUp(self):
        self.task_id = 'new_task'
        self.userids = []
        for number in range(self.users_count):
            self._addUser(number)

        folder = self.naudoc.storage
        self.task_container = getToolByName(folder, 'portal_followup')
        self.task_container = self.task_container._createFollowupFor(folder)
        task_list = []
        title = 'New Elaborated'
        type = 'elaborated'
        plan_time = Constants.LARGE
        duration = Constants.HUGE
        kw = {'duration': duration, 'items': task_list}
        self.elaborated = self.task_container.getTask(self.task_container.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
        for i in range(self.task_count):
            title = 'New Information Task%d' % i
            type = 'directive'
            duration = Constants.HUGE
            involved_users = [self.userids[i]]
            kw = {'duration': duration, 'involved_users': involved_users, 'description': 'he-he', 'plan_time': 100}
            task = kw
            task = self.elaborated.followup.getTask(self.elaborated.followup.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
            task_list.append(task)

        items = []
        for i in task_list:
            item = {}
            item['brains_type'] = 'directive'
            item['id'] = getattr(i, 'id')
            item['involved_users'] = getattr(i, 'involved_users')
            item['description'] = getattr(i, 'description')
            item['title'] = getattr(i, 'title')
            item['duration'] = getattr(i, 'duration')
            item['expiration_date'] = getattr(i, 'expiration_date')
            items.append(item)

        self.items = items
        self.task_list = task_list
        get_transaction().commit()
        return

    def testListInvolvedUsers(self):
        elaborated = self.elaborated
        REQUEST = self.app.REQUEST
        kw = {}
        count = 0
        for i in self.userids:
            count += int(i in elaborated.listInvolvedUsers(**kw))

        self.assertEqual(count, self.users_count)
        return

    def testListResponseTypes(self):
        user_number = 0
        elaborated = self.elaborated
        REQUEST = self.app.REQUEST
        self.assertEqual(elaborated.listResponseTypes(), [])
        self.login(self.userids[user_number])
        status = 'commit'
        self.task_list[user_number].Respond(status=status, REQUEST=REQUEST)
        self.login()
        self.assert_(elaborated.listResponseTypes() != [])
        return

    def testPendingUsers(self):
        elaborated = self.elaborated
        REQUEST = self.app.REQUEST
        self.assertEqual(elaborated.PendingUsers(), [])
        return

    def testCanSendNotifications(self):
        elaborated = self.elaborated
        REQUEST = self.app.REQUEST
        self.assert_(not elaborated.canSendNotifications())
        return

    def testGetFinalizationMode(self):
        elaborated = self.elaborated
        REQUEST = self.app.REQUEST
        finalization_mode = 'manual_creator'
        self.assertEqual(elaborated.getFinalizationMode(), finalization_mode)
        return

    def testSearchResponses(self):
        user_number = 0
        elaborated = self.elaborated
        elaborated.elaborate(self.items)
        REQUEST = self.app.REQUEST
        kw = {'status': 'commit'}
        self.assert_(elaborated.searchResponses(**kw) == [])
        self.login(self.userids[user_number])
        self.task_list[user_number].Respond(status='commit', REQUEST=REQUEST)
        self.login()
        kw = {'status': 'commit'}
        self.assert_(elaborated.searchResponses(**kw) != [])
        return

    def testElaborate(self):
        elaborated = self.elaborated
        kw = {}
        elaborated.elaborate(self.items)
        count = 0
        for i in self.userids:
            count += int(i in elaborated.listInvolvedUsers(**kw))

        self.assertEqual(count, self.users_count)
        elaborated.elaborate([])
        self.assertEqual(elaborated.listInvolvedUsers(**kw), [])
        return

    def beforeTearDown(self):
        self.elaborated.deleteObject()
        del self.task_container
        self.naudoc.portal_membership.deleteMembers(self.userids)
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ElaboratedTaskCreationTests))
    return suite
    return


if __name__ == '__main__':
    framework()
