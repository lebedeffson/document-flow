#! /bin/env python2.3
# -*- coding: cp1251 -*-

"""
Tests for VarFormatter class

$Id: testUtils.py,v 1.5 2006/03/17 15:19:32 ypetrov Exp $
"""
__version__='$Revision: 1.5 $'[11:-2]

import os, sys, random

from types import MethodType

import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
    
from unittest import TestCase
from cgi import escape as escapeHTML
from DateTime import DateTime
from ZPublisher.TaintedString import TaintedString

from Products.CMFNauTools.Utils import escapeJScript

class FakeContext:
    def registerVarFormat(self, *ignore ):
        pass

class FormattersWrapper:
    def __init__(self, formatters):
        self._formatters = formatters
    
    def __getattr__(self, name):
        value = getattr(self._formatters, name)

        if name != 'register' and isinstance(value, MethodType):
            return value.im_func

        return value

class VarFormatterTests(TestCase):
 
    def setUp( self):
        from Products.CMFNauTools.Utils import VarFormatters
        self.formatter = FormattersWrapper(VarFormatters)
        self.formatter.register( FakeContext() )
 
    def testUntaint(self):
        self.assertEquals(
            self.formatter.untaint( TaintedString('<html>') ),
            '<html>'
        )

    def testChecked(self):
        self.assertEquals(self.formatter.checked(True), 'checked="checked"')
        self.assertEquals(self.formatter.checked(False), '')
        self.assertEquals(self.formatter.checked(object),\
                                                'checked="checked"')

    def testSelected(self):
        self.assertEquals(self.formatter.selected(True), 'selected="selected"')
        self.assertEquals(self.formatter.selected(False), '')
        self.assertEquals(self.formatter.selected(object),\
                                                 'selected="selected"')

    def testDisabled(self):
        self.assertEquals(self.formatter.disabled(True), 'disabled="disabled"')
        self.assertEquals(self.formatter.disabled(False), '')
        self.assertEquals(self.formatter.disabled(object),\
                                                 'disabled="disabled"')

    def testReadonly(self):
        self.assertEquals(self.formatter.readonly(True), 'readonly="readonly"')
        self.assertEquals(self.formatter.readonly(False), '')
        self.assertEquals(self.formatter.readonly(object),\
                                                 'readonly="readonly"')

    def testMultiple(self):
        self.assertEquals(self.formatter.multiple(True), 'multiple="multiple"')
        self.assertEquals(self.formatter.multiple(False), '')
        self.assertEquals(self.formatter.multiple(object),\
                                                 'multiple="multiple"')

    def testJscript(self):
        self.assertEquals(self.formatter.jscript( '</script>' ), '<\\057script>')
        self.assertEquals(self.formatter.jscript( '\n' ), '\\n\\\n')
        self.assertEquals(self.formatter.jscript( '\'' ), '\\\'')
        self.assertEquals(self.formatter.jscript( '\"' ), '\\\"')
        self.assertEquals(self.formatter.jscript( '\\' ), '\\\\')

    def testJscriptBool(self):
        self.assertEquals(self.formatter.jscript_bool(True), 'true')
        self.assertEquals(self.formatter.jscript_bool(False), 'false')
        self.assertEquals(self.formatter.jscript_bool(object), 'true')

    def testStrip(self):
        self.assertEquals(self.formatter.strip( ' i am a bad str ' ),\
                                               'i am a bad str' )

    def testClass(self):
        self.assertEquals(self.formatter.Class(''), '')
        self.assertEquals(self.formatter.Class( 'Test' ), 'class="Test"' )

    def testPercent(self):
        self.assertEquals(self.formatter.percent( 0.5 ), '50%' )

class ZopeConverterTests(TestCase):

    def setUp(self):
        from Products.CMFNauTools.Utils import RequestConverters
        self.converter = RequestConverters
    
    def testCurrencyConverter(self):
        self.assertEquals(self.converter.currency( '123.50' ), 123.5 )
        self.assertEquals(self.converter.currency( '123,50' ), 123.5 )
        try:
            self.converter.int('Infinite')
        except ValueError:
            pass
        else:
            self.fail('This value cant be converted to currency type')
   
    def testIntConverter(self):
        self.assertEquals(self.converter.int( '123' ), 123 )
        self.assertEquals(self.converter.int( '-123' ), -123 )
        try:
            self.converter.int('Infinite')
        except ValueError:
            pass
        else:
            self.fail('This value cant be converted to integer type')

    def testFloatConverter(self):
        self.assertEquals(self.converter.float( '123' ), 123.0 )
        self.assertEquals(self.converter.float( '-123' ), -123.0 )
        try:
            self.converter.int('Infinite')
        except ValueError:
            pass
        else:
            self.fail('This value cant be converted to float type')

    def testSentencesConverter(self):
        self.assertEquals(self.converter.sentences( ' qwe' ), ['qwe'] )
        self.assertEquals(self.converter.sentences( '  qwe' ), ['qwe'] )
        self.assertEquals(self.converter.sentences( 'qwe, rty' ),\
                                                             ['qwe', 'rty'] )
        self.assertEquals(self.converter.sentences( '' ), [] )

    def testLinesConverter(self):
        self.assertEquals(self.converter.lines( '\nq w e\nrty' ),\
                                                         ['', 'q w e', 'rty'] )
        self.assertEquals(self.converter.lines( '' ), [] )

    def testBooleanConverter(self):
        self.assertEquals(self.converter.boolean( 'False' ), False )
        self.assertEquals(self.converter.boolean( 'True' ), True )
        self.assertEquals(self.converter.boolean( '' ), False )
        self.assertEquals(self.converter.boolean( '1' ), True )
        self.assertEquals(self.converter.boolean( '0' ), True )

    def testNoneConverter(self):
        self.assertEquals(self.converter.none( '' ), None )
        self.assertEquals(self.converter.none( 'qwe' ), 'qwe' )

    def testDateConverter(self):
        self.assertEquals(self.converter.date_( '12.10.2005' ),\
                                                        DateTime('2005/10/12') )

    def testDateTimeConverter(self):
        self.assertEquals(self.converter.datetime_( '12.10.2005 10:50' ),\
                                                DateTime('2005/10/12 10:50:00') )

    def testUidConverter(self):
        self.assertEquals(self.converter.uid( '' ), None )
        #TODO

#      def testMonikerConverter(self): TODO
#          self.assertEquals(self.converter.moniker( '' ), None )

    def testTimePeriodConverter(self):
        self.assertEquals(self.converter.time_period( '52:10:15' ),\
                                                                4529700 )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(VarFormatterTests) )
    suite.addTest( makeSuite(ZopeConverterTests) )
    return suite

if __name__ == '__main__':
    framework()
