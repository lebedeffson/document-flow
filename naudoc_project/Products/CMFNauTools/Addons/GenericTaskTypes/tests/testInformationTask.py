# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/tests/testInformationTask.py
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

class InformationTaskFunctionalTests(NauDocTestCase.NauDocTestCase):
    __module__ = __name__
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    plan_time = 20
    duration = 100

    def afterSetUp(self):
        self.task_id = 'new_task'
        folder = self.naudoc.storage
        self.task_container = getToolByName(folder, 'portal_followup')
        self.task_container = self.task_container._createFollowupFor(folder)
        title = 'New Information'
        type = 'information'
        plan_time = self.plan_time
        duration = self.duration
        kw = {'duration': duration}
        self.information = self.task_container.getTask(self.task_container.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
        get_transaction().commit()
        return

    def testOnFinalize(self):
        information = self.information
        REQUEST = self.app.REQUEST
        result_code = 'success'
        information.onFinalize(REQUEST=REQUEST, result_code=result_code)
        self.assert_(information.isFinalized())
        return

    def testOnInform(self):
        information = self.information
        REQUEST = self.app.REQUEST
        information.onInform(REQUEST=REQUEST)
        self.assertEqual(information.result, 'success')
        return

    def testOnReview(self):
        information = self.information
        REQUEST = self.app.REQUEST
        information.onReview(REQUEST=REQUEST)
        self.assertEqual(information.result, 'success')
        return

    def beforeTearDown(self):
        self.information.deleteObject()
        del self.task_container
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(InformationTaskFunctionalTests))
    return suite
    return


if __name__ == '__main__':
    framework()
