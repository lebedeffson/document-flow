#! /bin/env python2.3

"""
Tests for PatternProcessor class

$Id: testPatternProcessor.py,v 1.3 2006/01/10 11:42:04 ynovokreschenov Exp $
"""
__version__='$Revision: 1.3 $'[11:-2]

import os, sys, random
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.Utils import getToolByName
from Products.CMFNauTools.PatternProcessor import *
import AccessControl.SecurityManagement, AccessControl.SpecialUsers

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class PatternTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0
    def afterSetUp(self):
        self.naudoc.storage.manage_addProduct['CMFNauTools'].addHTMLDocument('doc_test' , category='Document', title='qwerty')
        self.d = self.naudoc.storage.doc_test
        self.naudoc.storage.manage_addProduct['CMFNauTools'].addRegistrationBook( 'reg' )
        self.r = self.naudoc.storage.reg

    def testSimpleReplace(self):
        self.assertEquals(SimpleReplacePattern().search( '' ), 1 )
        self.assertEquals(SimpleReplacePattern().search( './qwe' ), 6 )

    def testReplacePPattern(self):
        folder = self.naudoc
        self.assertEquals(ReplacePPattern().search( './qwe' ), True )
        self.assertEquals(ReplacePPattern().search( '/qwe./rty' ), False )
        self.assertEquals(ReplacePPattern().search( '' ), False )
        self.assertEquals(ReplacePPPattern().process( '../qwe', doc=self.d ), folder.physical_path() + '/qwe' )

    def testReplacePPPattern(self):
        folder = self.naudoc
        self.assertEquals(ReplacePPPattern().search( '../qwe' ), True )
        self.assertEquals(ReplacePPPattern().search( '/qwe../rty' ), False )
        self.assertEquals(ReplacePPPattern().search( '../../../qwe' ), True )
        self.assertEquals(ReplacePPPattern().process( '../qwe', doc=self.d ), folder.physical_path() + '/qwe' )

    def testPathPrefixPattern(self):
        folder = self.naudoc
        self.assertEquals(PathPrefixPattern().process( '../qwe', doc=self.d ), '../qwe' )
        self.assertEquals(PathPrefixPattern().process( './qwe', doc=self.d ), './qwe' )
        self.assertEquals(ReplacePPPattern().process( '../qwe', doc=self.d ), folder.physical_path() + '/qwe' )

    def testReplaceDatePattern(self):
        now = DateTime()
        self.assertEquals(ReplaceDatePattern().process( '\\y' ), now.strftime('%' + 'y') )
        self.assertEquals(ReplaceDatePattern().process( '\\Y' ), now.strftime('%' + 'Y') )
        self.assertEquals(ReplaceDatePattern().process( '\\m' ), now.strftime('%' + 'm') )
        self.assertEquals(ReplaceDatePattern().process( '\\d' ), now.strftime('%' + 'd') )
        self.assertEquals(ReplaceDatePattern().process( '\\H' ), now.strftime('%' + 'H') )
        self.assertEquals(ReplaceDatePattern().process( '\\M' ), now.strftime('%' + 'M') )
        self.assertEquals(ReplaceDatePattern().process( '' ), '' )

    def testReplaceDPattern(self):
        self.assertEquals(ReplaceDPattern().process( 'qwe%Dqwe', doc=self.d ), 'qwe'+'doc_test'+'qwe' )
        self.assertEquals(ReplaceDPattern().process( '', doc=self.d ), '' )
        self.assertEquals(ReplaceDPattern().process( 'qwe', doc=self.d ), 'qwe' )

    def testReplaceTPattern(self):
        self.assertEquals(ReplaceTPattern().process( '%Tqwe', doc=self.d ), 'qwertyqwe' )
        self.assertEquals(ReplaceTPattern().process( 'qwe', doc=self.d ), 'qwe' )
        self.assertEquals(ReplaceTPattern().process( '', doc=self.d ), '' )

    def testReplaceTTranslitPattern(self):
        self.assertEquals(ReplaceTTranslitPattern().process( '%Tqwe', doc=self.d ), 'qwertyqwe' )
        self.assertEquals(ReplaceTTranslitPattern().process( 'qwe', doc=self.d ), 'qwe' )
        self.assertEquals(ReplaceTTranslitPattern().process( '', doc=self.d ), '' )

    def testReplaceVPattern(self):
        rez = self.d.getCurrentVersionId().replace('.', '_')
        self.assertEquals(ReplaceVPattern().process( '%Vqwe', doc=self.d ), rez+'qwe' )
        self.assertEquals(ReplaceVPattern().process( 'qwe', doc=self.d ), 'qwe' )
        self.assertEquals(ReplaceVPattern().process( '', doc=self.d ), '' )

    def testReplaceVTranslatePattern(self):
        rez = self.d.getVersion().getVersionNumber()
        self.assertEquals(ReplaceVTranslatePattern().process( '%Vqwe', doc=self.d ), 'Version '+rez+'qwe' )
        self.assertEquals(ReplaceVTranslatePattern().process( 'qwe', doc=self.d ), 'qwe' )
        self.assertEquals(ReplaceVTranslatePattern().process( '', doc=self.d ), '' )   

    def testReplaceFnumPattern(self):
        self.naudoc.storage.setCategoryAttribute('nomenclative_number', 'NewValue')
        self.assertEquals(ReplaceFnumPattern().process( 'qwe\\Fnumrty', doc=self.d ), 'qweNewValuerty' )
        self.assertEquals(ReplaceFnumPattern().process( 'qwe', doc=self.d ), 'qwe' )
        self.assertEquals(ReplaceFnumPattern().process( '', doc=self.d ), '' )

    def testReplaceFpfxPattern(self):
        self.naudoc.storage.setCategoryAttribute('postfix', 'NewValue')
        self.assertEquals(ReplaceFpfxPattern().process( 'qwe\\Fpfxrty', doc=self.d ), 'qweNewValuerty' )
        self.assertEquals(ReplaceFpfxPattern().process( 'qwe', doc=self.d ), 'qwe' )
        self.assertEquals(ReplaceFpfxPattern().process( '', doc=self.d ), '' )

    def testReplaceCpfxPattern(self):
        folder = self.naudoc.storage
        folder.setCategoryAttribute('postfix', 'NewValue')
        self.assertEquals(ReplaceCpfxPattern().process( '\\Cpfx', obj=folder ), 'NewValue' )
        self.assertEquals(ReplaceCpfxPattern().process( 'qwe', obj=folder ), 'qwe' )
        self.assertEquals(ReplaceCpfxPattern().process( '', obj=folder ), '' )

    def testReplaceRdptPattern(self):
        self.r.setDepartment('NewDep')
        self.assertEquals(ReplaceRdptPattern().process( '\\Rdpt', obj=self.r ), 'NewDep' )

    def testReplaceSeqPattern(self):
        self.assertEquals(ReplaceSeqPattern().process( 'qwe' ), 'qwe' )
        self.assertEquals(ReplaceSeqPattern().process( 'qwe\\Seqqwe', obj=self.r ), 'qwe1qwe' )
        self.assertEquals(ReplaceSeqPattern().process( 'qwe\\Seq:3#qwe', obj=self.r ), 'qwe001qwe' )

    def testReplaceSqdPattern(self):
        self.assertEquals(ReplaceSqdPattern().process( 'qwe\\qwe', obj=self.r ), 'qwe\\qwe' )
        self.assertEquals(ReplaceSqdPattern().process( 'qwe\\Sqd:3#qwe', obj=self.r ), 'qwe001qwe' )


    def beforeTearDown(self):
        #remove document
        self.naudoc.storage.deleteObjects( ['doc_test'] )
        self.naudoc.storage.deleteObjects( ['reg'] )
        get_transaction().commit()
        del self.d
        del self.r
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(PatternTests) )
    return suite

if __name__ == '__main__':
    framework()
