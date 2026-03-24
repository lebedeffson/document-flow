#! /bin/env python2.3
"""

$Id: testScript.py,v 1.2 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


import NauDocTestCase
from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')

class DummyNameSpace:
    def listNamespaceItems( self ):
        return {}

    def getType(self):
        return 'dummy'

class ScriptTests( NauDocTestCase.NauDocTestCase ):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        storage = self.naudoc.storage

        storage.invokeFactory( type_name='Script'
                             , id='test_script1'
                             , title='test_script1'
                             , description='test description'
                             )

        storage.invokeFactory( type_name='Script'
                             , id='test_script2'
                             , title='test_script2'
                             , description='test description'
                             )


        script = self.naudoc._getOb('storage')._getOb('test_script1')
        script.setBody('# test script1\np = 1 + 1\nreturn p')

        script = self.naudoc._getOb('storage')._getOb('test_script2')
        script.addParameter( 'foo', 'string', 'Foo', 'foo-foo-foo' )
        script.setBody('# test script2\nreturn foo')
    
        get_transaction().commit()        

    def testCompile( self ):

        script = self.naudoc._getOb('storage')._getOb('test_script1')

        script._params = ''
        try:
            try:
                script._compile()
            except:
                self.fail( 'error shouldn`t happen' )
        finally:
            del script._params

    def testEvaluate( self ):

        script = self.naudoc._getOb('storage')._getOb('test_script1')

        res = script.evaluate( DummyNameSpace() )
        self.assertEqual( res, 2 )

    def testEvaluateWithParam( self):

        script2 = self.naudoc._getOb('storage')._getOb('test_script2')

        self.assertEqual( script2.getParameterDefaultValue( 'foo' ), 'foo-foo-foo' )
        self.assertEqual( script2.listParameterNames(), 'foo' )
        res = script2.evaluate( DummyNameSpace(), parameters={'foo':'new_value_of_foo'} )
        self.assertEqual( res, 'new_value_of_foo' )

    def beforeTearDown(self):
        self.naudoc.storage.deleteObjects( ['test_script1','test_script2'] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class ScriptFunctionalTests( NauDocTestCase.NauFunctionalTestCase ):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    afterSetUp = ScriptTests.afterSetUp.im_func

    def testScriptView(self):

        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc.storage._getOb('test_script1')
        path = '/%s/view' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testScriptConfiguration(self):

        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc.storage._getOb('test_script1')
        path = '/%s/script_metadata_edit_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testScriptParameters(self):

        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        # get the script with params
        obj  = self.naudoc.storage._getOb('test_script2')
        path = '/%s/script_parameters_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testScriptTest(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        # get the script with params
        obj  = self.naudoc.storage._getOb('test_script2')
        path = '/%s/script_test_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    beforeTearDown = ScriptTests.beforeTearDown.im_func

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(ScriptTests) )
    suite.addTest( makeSuite(ScriptFunctionalTests) )
    return suite

if __name__ == '__main__':
    framework()
