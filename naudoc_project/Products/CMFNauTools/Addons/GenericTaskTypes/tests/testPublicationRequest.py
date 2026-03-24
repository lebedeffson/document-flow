# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/GenericTaskTypes/tests/testPublicationRequest.py
# Compiled at: 2006-01-30 11:13:54
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

class PublicationRequestFunctionalTests(NauDocTestCase.NauDocTestCase):
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
        title = 'New Publication'
        type = 'publication_request'
        plan_time = self.plan_time
        duration = self.duration
        kw = {'duration': duration}
        self.publication_request = self.task_container.getTask(self.task_container.createTask(title, type=type, bind_to=None, creator=None, REQUEST=None, **kw))
        get_transaction().commit()
        return

    def testOnFinalize(self):
        publication_request = self.publication_request
        REQUEST = self.app.REQUEST
        result_code = 'success'
        publication_request.onFinalize(REQUEST=REQUEST, result_code=result_code)
        self.assert_(publication_request.isFinalized())
        return

    def testOnSatisfy(self):
        publication_request = self.publication_request
        REQUEST = self.app.REQUEST
        publication_request.onSatisfy(REQUEST=REQUEST)
        return

    def testOnReject(self):
        publication_request = self.publication_request
        REQUEST = self.app.REQUEST
        publication_request.onReject(REQUEST=REQUEST)
        self.assertEqual(publication_request.result, 'failed')
        return

    def testOnRespond(self):
        publication_request = self.publication_request
        REQUEST = self.app.REQUEST
        publication_request.onRespond(REQUEST=REQUEST)
        self.assertEqual(publication_request.result, 'success')
        return

    def testDoWorkflowAction(self):
        publication_request = self.publication_request
        REQUEST = self.app.REQUEST
        action = 'publish'
        comment = 'Test Comment'
        publication_request.doWorkflowAction(action=action, comment=comment)
        return

    def beforeTearDown(self):
        self.publication_request.deleteObject()
        del self.task_container
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PublicationRequestFunctionalTests))
    return suite
    return


if __name__ == '__main__':
    framework()
