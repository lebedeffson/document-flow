# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/tests/testDirectiveTask.py
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

class DirectiveTaskFunctionalTests(NauDocTestCase.NauDocTestCase):
    __module__ = __name__
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    doc_count = Constants.LARGE
    plan_time = 20
    duration = 100

    def afterSetUp(self):
        self.task_id = 'new_task'
        folder = self.naudoc.storage
        self.task_container = getToolByName(folder, 'portal_followup')
        self.task_container = self.task_container._createFollowupFor(folder)
        title = 'New Directive'
        type = 'directive'
        plan_time = self.plan_time
        duration = self.duration
        kw = {'plan_time': plan_time, 'duration': duration}
        self.directive = self.task_container.getTask(self.task_container.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
        get_transaction().commit()
        return

    def testOnRespond(self):
        actual_time = 10
        directive = self.directive
        REQUEST = self.app.REQUEST
        REQUEST['actual_time'] = actual_time
        directive.onRespond(REQUEST=REQUEST)
        self.assertEqual(directive.getActualTimeFor(self.log_as_user), actual_time)
        return

    def testOnFinalize(self):
        directive = self.directive
        REQUEST = self.app.REQUEST
        result_code = 'success'
        directive.finalized = True
        directive.onFinalize(REQUEST=REQUEST, result_code=result_code)
        self.assert_(directive.isFinalized())
        return

    def testPlanTime(self):
        directive = self.directive
        old_plan_time = directive.getPlanTime()
        plan_time = int(random.random() * 100)
        directive.setPlanTime(plan_time)
        self.assertEqual(directive.getPlanTime(), plan_time)
        directive.setPlanTime(old_plan_time)
        self.assertEqual(directive.getPlanTime(), old_plan_time)
        return

    def testOnAccept(self):
        directive = self.directive
        REQUEST = self.app.REQUEST
        directive.onAccept(REQUEST=REQUEST)
        return

    def testOnCommit(self):
        directive = self.directive
        REQUEST = self.app.REQUEST
        directive.onCommit(REQUEST=REQUEST)
        return

    def testOnReject(self):
        directive = self.directive
        REQUEST = self.app.REQUEST
        directive.onReject(REQUEST=REQUEST)
        return

    def testOnFailure(self):
        directive = self.directive
        REQUEST = self.app.REQUEST
        directive.onFailure(REQUEST=REQUEST)
        return

    def testOnReview(self):
        directive = self.directive
        REQUEST = self.app.REQUEST
        directive.onReview(REQUEST=REQUEST)
        return

    def beforeTearDown(self):
        del self.task_container
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(DirectiveTaskFunctionalTests))
    return suite
    return


if __name__ == '__main__':
    framework()
