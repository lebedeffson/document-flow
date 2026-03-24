# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DirectoryObject/tests/testDirectoryExplorer.py
# Compiled at: 2005-12-09 18:35:49
"""

$Id: testDirectoryExplorer.py,v 1.2 2005/12/09 15:35:49 vsafronovich Exp $
"""
__version__ = '$Revision: 1.2 $'[11:-2]
import os, sys
from Products.CMFNauTools.tests import Configurator
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
from Testing import ZopeTestCase
from Products.CMFNauTools.tests import NauDocTestCase
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')
app = ZopeTestCase.app()
ZopeTestCase.utils.setupCoreSessions(app)
ZopeTestCase.close(app)
from thread import get_ident
from ZPublisher import Publish
from ZPublisher.BaseRequest import BaseRequest
from Products.Localizer.AcceptLanguage import AcceptLanguage
from Products.CMFNauTools.Explorer import getExplorerType
from Products.CMFNauTools.JungleTag import IBasicTree
from Products.CMFNauTools.Utils import getObjectImplements
from Products.CMFNauTools.Addons.DirectoryObject.DirectoryBase import DirectoryExplorer

class DirExplorerTests(NauDocTestCase.NauDocTestCase):
    __module__ = __name__
    _remove_naudoc = False
    log_as_user = NauDocTestCase.admin_name
    dir_id = 'test_dir_0_'

    def afterSetUp(self):
        if hasattr(Publish, '_requests'):
            ident = get_ident()
            Publish._requests[ident] = self.app.REQUEST
        request = self.app.REQUEST
        sdm = self.app.session_data_manager
        request.set('SESSION', sdm.getSessionData())
        storage = self.naudoc._getOb('storage')
        storage.invokeFactory(type_name='Directory', id=self.dir_id, title=self.dir_id, description='test description')
        return

    def testExplorerCreation(self):
        obj = self.naudoc._getOb('storage')._getOb(self.dir_id)
        ExplorerType = getExplorerType(obj)
        self.assertEquals(ExplorerType, DirectoryExplorer)
        explorer = ExplorerType(obj, **{})
        self.assert_(explorer is not None)
        self.assert_(explorer._v_object.REQUEST is not None)
        tree = explorer.tree_index(None)
        self.assert_(getObjectImplements(tree, IBasicTree))
        self.assertEquals(tree.root_item, None)
        items = tree.get_items(None)
        self.assert_(len(list(items)) == 0)
        content = explorer.content_index(None)
        self.assertEquals(content['item'], None)
        return

    def beforeTearDown(self):
        ident = get_ident()
        if hasattr(Publish, '_requests') and Publish._requests.has_key(ident):
            Publish._requests[ident].close()
            del Publish._requests[ident]
        self.naudoc.storage.deleteObjects(self.dir_id)
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(DirExplorerTests))
    return suite
    return


if __name__ == '__main__':
    framework()
