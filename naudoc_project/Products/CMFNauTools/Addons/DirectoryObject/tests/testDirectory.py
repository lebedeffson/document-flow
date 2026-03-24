# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DirectoryObject/tests/testDirectory.py
# Compiled at: 2006-01-19 13:33:11
"""
Test Directory.

$Id: testDirectory.py,v 1.6 2006/01/19 10:33:11 siskakov Exp $
"""
__version__ = '$ $'[11:-2]
import os, sys, random
from Products.CMFNauTools.tests import Configurator
Constants = Configurator.Constants
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
from Products.CMFNauTools.tests import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import NauSite
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')
app = ZopeTestCase.app()
ZopeTestCase.utils.setupCoreSessions(app)
ZopeTestCase.close(app)

class DirectoryTests(NauDocTestCase.NauFunctionalTestCase):
    __module__ = __name__
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    doc_count = Constants.LARGE

    def afterSetUp(self):
        self.dir_id = 'Dir'
        title = self.dir_id
        folder = self.naudoc.storage
        folder.invokeFactory(type_name='Directory', id=self.dir_id, title=title, description='test description')
        dir = folder._getOb(self.dir_id)
        get_transaction().commit()
        return

    def cookId(self, i):
        return 'D%s' % i
        return

    def testGetDirectory(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        res = dir.getDirectory()
        self.assertEqual(res, dir)
        return

    def testTpURL(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        res = dir.tpURL()
        self.assertEqual(res, self.dir_id)
        return

    def testColumn(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        column_name = 'TestColumn'
        column_type = 'string'
        res_add = dir.addColumn(name=column_name, type=column_type)
        res_get = dir.getColumn(name=column_name)
        self.assertEqual(res_add, res_get)
        count = Constants.MEDIUM
        for i in xrange(count):
            column_name = 'Column%d' % i
            dir.addColumn(name=column_name, type=column_type)

        res_list = dir.listColumns()
        res = 0
        column_list = [_[1] for i in xrange(count)]
        for i in res_list:
            res += int(i in column_list)

        self.assertEqual(res, count)
        for i in xrange(count):
            dir.deleteColumn(name='Column%d' % i)

        self.assertEqual(len(dir.listColumns()), 1)
        self.assertEqual(dir.getCodeColumn() is None, False)
        self.assertEqual(dir.getTitleColumn() is None, False)
        return

    def testMaxLevel(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        cur_level = dir.getMaxLevel()
        level = 10
        dir.setMaxLevel(level)
        self.assertEqual(level, dir.getMaxLevel())
        dir.setMaxLevel(cur_level)
        self.assertEqual(cur_level, dir.getMaxLevel())
        return

    def testCodePattern(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        old_pattern = dir.getCodePattern()
        dir.setCodePattern('\\Y')
        self.assertEqual(dir.getCodePattern(), '\\Y')
        dir.setCodePattern(old_pattern)
        self.assertEqual(dir.getCodePattern(), old_pattern)
        return

    def testOwnerObject(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        old_owner_obj = dir.getOwnerObject()
        id = 'Test ID'
        title = id
        self.naudoc.storage.invokeFactory(type_name='HTMLDocument', id=id, title=title, description='test description', category='Document')
        new_owner_obj = self.naudoc.storage._getOb(id)
        dir.setOwnerObject(new_owner_obj)
        self.assertEqual(dir.getOwnerObject(), new_owner_obj)
        dir.setOwnerObject(old_owner_obj)
        self.assertEqual(dir.getOwnerObject(), old_owner_obj)
        self.naudoc.storage.deleteObjects(['Test ID'])
        return

    def testTpValues(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        self.assertEqual(dir.tpValues() is None, False)
        return

    def testTpId(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        self.assertEqual(dir.tpId() is None, False)
        return

    def testGetEntry(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        code = 'Test Code'
        x = dir.addEntry(code)
        self.assertEqual(dir.getEntry(x.getId()), x)
        return

    def testListAttributeDefinitions(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        code = 'Test Code'
        branch = dir.addBranch(code=code)
        entry = dir.addEntry(code=code)
        res_list_attr_def = dir.listAttributeDefinitions(id=entry.getId())
        for i in res_list_attr_def:
            if i.has_key('column'):
                self.assertEqual(dir.getAttributeValueFor(object=entry, uid=i) in ['', 'Test Code', None], True)

        entry.setParent(branch)
        res_list_attr_def = dir.listAttributeDefinitions(id=entry.getId())
        for i in res_list_attr_def:
            if i.has_key('column'):
                self.assertEqual(dir.getAttributeValueFor(object=entry, uid=i) in [' / ', 'Test Code / Test Code', branch], True)

        title = 'Test Title'
        entry.setTitle(title)
        res_list_attr_def = dir.listAttributeDefinitions(id=entry.getId())
        for i in res_list_attr_def:
            if i.has_key('column'):
                self.assertEqual(dir.getAttributeValueFor(object=entry, uid=i) in [' / %s' % title, 'Test Code / Test Code', branch], True)

        return

    def testSoleRoot(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        res_sole_root = dir.isSoleRoot()
        dir.setSoleRoot(dir)
        self.assertEqual(dir.isSoleRoot(), True)
        dir.setSoleRoot(res_sole_root)
        self.assertEqual(dir.isSoleRoot(), bool(res_sole_root))
        return

    def testGetDirectoryTree(self):
        dir = self.naudoc.storage._getOb(self.dir_id)
        code = 'Test Code'
        branch1 = dir.addBranch(code='Test Code %d' % 1)
        branch2 = dir.addBranch(code='Test Code %d' % 2)
        branch3 = dir.addBranch(code='Test Code %d' % 3)
        entry1 = dir.addEntry(code=code)
        entry2 = dir.addEntry(code=code)
        entry3 = dir.addEntry(code=code)
        entry4 = dir.addEntry(code=code)
        entry5 = dir.addEntry(code=code)
        branch2.setParent(branch1)
        entry1.setParent(branch1)
        entry2.setParent(branch1)
        entry3.setParent(branch2)
        entry4.setParent(branch2)
        entry1.setTitle('Test Title')
        entry2.setTitle('Test Title')
        directory_tree = dir.getDirectoryTree(dir)
        res = directory_tree.get_items(branch1.getId())
        self.assertEqual(directory_tree is None, False)
        self.assertEqual(len(list(res)), 1)
        branch3.setParent(branch1)
        res = directory_tree.get_items(branch1.getId())
        self.assertEqual(len(list(res)), 2)
        branch3.setParent(branch2)
        res = directory_tree.get_items(branch1.getId())
        self.assertEqual(len(list(res)), 1)
        return

    def beforeTearDown(self):
        folder = self.naudoc.storage
        if folder._getOb(self.dir_id, None):
            folder.deleteObjects([self.dir_id])
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


class DirCreationTests(NauDocTestCase.NauDocTestCase):
    __module__ = __name__
    _remove_naudoc = 0
    number_of_directories = Constants.LARGE

    def testDocumentCreation(self):
        storage = self.naudoc.storage
        for i in range(self.number_of_directories):
            id = self.cookId(i)
            title = id
            storage.invokeFactory(type_name='Directory', id=id, title=title, description='test description')
            self.assert_(storage.hasObject(id))
            obj = storage._getOb(id)
            self.assert_(obj is not None)

        get_transaction().commit()
        return

    def cookId(self, i):
        return 'dir_%d' % i
        return

    def beforeTearDown(self):
        dir_ids = map(self.cookId, range(self.number_of_directories))
        self.naudoc.storage.deleteObjects(dir_ids)
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown(self)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(DirectoryTests))
    suite.addTest(makeSuite(DirCreationTests))
    return suite
    return


if __name__ == '__main__':
    framework()
