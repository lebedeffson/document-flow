"""
Create FS folder.

$Id: testFSFolder.py,v 1.4 2005/12/10 15:50:12 vsafronovich Exp $
"""
__version__='$ $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import tempfile, shutil, time
import NauDocTestCase

from DateTime import DateTime
from Testing import ZopeTestCase
from Products.CMFNauTools import NauSite

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')

# External Editor is needed because it patched manage_main, which is rendered in manage_pasteObjects
ZopeTestCase.installProduct('ExternalEditor')

class FSFolderCreationTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    def createFSObjects(self):
        # create Folder
        self.file_system_path = tempfile.mkdtemp()
 
        # create 2 files
        fn1 = tempfile.mktemp(dir=self.file_system_path)
        file1 = open(fn1,'w')
        try:
            file1.write('privet')
        finally:
            file1.close()
        self.fn1 = fn1

        fn2 = tempfile.mktemp(dir=self.file_system_path)
        file2 = open(fn2,'w')
        try:
            file2.write('privet\n' * 80 )
        finally:
            file2.close()
        self.fn2 = fn2

    def destroyFSObjects(self):
        shutil.rmtree(self.file_system_path)

    def afterSetUp(self):
        self.createFSObjects()

    def testFSFolderCreation(self):
        storage = self.naudoc.storage
        storage.manage_addProduct['CMFNauTools'].addFSFolder( id='FSF'
                                                            , title='FSF'
                                                            , description='FSF description'
                                                            , path=self.file_system_path
                                                            )
        get_transaction().commit()

    def beforeTearDown(self):
        folder = self.naudoc.storage
        if folder._getOb( 'FSF', None ):
            folder.deleteObjects( ['FSF'] )
        get_transaction().commit()

        self.destroyFSObjects()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class FSFolderMovingTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    temp_folder = 'F0'
    FS_folder = 'FSF'

    def afterSetUp(self):
        FSFolderCreationTests.createFSObjects.im_func(self)

        storage = self.naudoc.storage
        #create FS folder.

        storage.manage_addProduct['CMFNauTools'].addFSFolder( id=self.FS_folder
                                                            , title=self.FS_folder
                                                            , description='FSF description'
                                                            , path=self.file_system_path
                                                            )
        #create temporary folder 'F0'
        storage.invokeFactory( type_name='Heading'
                             , id=self.temp_folder
                             , title=self.temp_folder
                             , description='description'
                             , category='Folder'
                             )

        get_transaction().commit()

    def testFSFolderMoving(self):
        REQUEST = self.naudoc.REQUEST

        folder_from = self.naudoc.storage
        folder_to = self.naudoc.storage._getOb(self.temp_folder)

        folder_from.manage_cutObjects([self.FS_folder], REQUEST)
        folder_to.manage_pasteObjects( REQUEST=REQUEST )
        get_transaction().commit()

    def beforeTearDown(self):
        folder = self.naudoc.storage
        folder.deleteObjects([self.FS_folder, self.temp_folder])
        get_transaction().commit()

        FSFolderCreationTests.destroyFSObjects.im_func(self)

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class FSObjectTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    createFSObjects = FSFolderCreationTests.createFSObjects.im_func
    destroyFSObjects = FSFolderCreationTests.destroyFSObjects.im_func

    def afterSetUp(self):
        self.createFSObjects()

        storage = self.naudoc.storage
        storage.manage_addProduct['CMFNauTools'].addFSFolder( id='FSF'
                                                            , title='FSF'
                                                            , description='FSF description'
                                                            , path=self.file_system_path
                                                            )
       
        get_transaction().commit()

        self.fsfolder = self.naudoc.storage.FSF
        self.fsfile1 = self.fsfolder._getOb(os.path.splitext(os.path.basename(self.fn1))[0])


    def testUpdateModificationDate( self ):
        fn3 = tempfile.mktemp(dir=self.file_system_path)
        file3 = open(fn3,'w')
        try:
            file3.write('privet\n' * 3 )
        finally:
            file3.close()
        self.fn3 = fn3

        fsfolder = self.fsfolder
        fsfile1 = self.fsfile1

        #test that folder's modif time is invalid because creation of file must change it
        lastFolderMTime = DateTime( os.path.getmtime( self.file_system_path ) )
        #self.assertNotEqual( fsfolder.modification_date,
        #                     lastFolderMTime,
        #                     "Folder modification date did not changed after new file creation")

        #update folder mtime and test that folder's modif time is ok
        fsfolder.updateModificationDate()
        self.assertEqual( fsfolder.modification_date,
                        lastFolderMTime,
                        "FSObject (folder) did not update its modification time" )

        #test that file's modif time is ok
        lastFileMTime = DateTime( os.path.getmtime( self.fn1 ) )
        self.assertEqual( fsfile1.modification_date, lastFileMTime )

        #edit file
        time.sleep(1)
        temp_file = open( self.fn1, 'w')
        temp_file.write('123')
        temp_file.close()


        #test that file time became invalid
        lastFileMTime = DateTime( os.path.getmtime( self.fn1 ) )
        self.assertNotEqual( fsfile1.modification_date, lastFileMTime,
                "File modification date did not changed after editing" )

        #update file and test that file time is ok
        fsfile1.updateModificationDate()
        lastFileMTime = DateTime( os.path.getmtime( self.fn1 ) )
        self.assertEqual( fsfile1.modification_date, lastFileMTime,
                "FSObject (file) did not update its modification time" )

        # if folder modif time has changed - its ok,
        # although is ok too if modif time has not changed :)

    def testGetObjectFSPath( self ):
        fsfolder = self.fsfolder
        fsfile1 = self.fsfile1

        self.assertEqual( fsfolder.getObjectFSPath(), self.file_system_path )
        self.assertEqual( fsfile1.getObjectFSPath(), self.fn1 )

    def testIsAccessibeFSAndCheckExists( self ):
        fsfolder = self.fsfolder
        fsfile1 = self.fsfile1

        self.assert_( fsfolder.checkExists() )
        self.assert_( fsfile1.isAccessibeFS() )

        os.remove( self.fn1 )

        self.failIf( fsfile1.checkExists() )
        self.failIf( fsfile1.isAccessibeFS() )

        self.assert_( fsfolder.checkExists() )
        self.assert_( fsfolder.isAccessibeFS() )

        temp_file = open( self.fn1, 'w')
        temp_file.close()

    def beforeTearDown(self):
        del self.fsfolder, self.fsfile1
        folder = self.naudoc.storage
        folder.deleteObjects( ['FSF'] )
        get_transaction().commit()

        self.destroyFSObjects()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(FSFolderCreationTests) )
    suite.addTest( makeSuite(FSFolderMovingTests) )
    suite.addTest( makeSuite(FSObjectTests) )

    return suite

if __name__ == '__main__':
    framework()
