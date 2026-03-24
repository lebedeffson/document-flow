"""
$Id: testGuardedTable.py,v 1.2 2005/12/09 15:40:59 vsafronovich Exp $
"""
__version__='$ $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import tempfile, shutil
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

class GuardedTableTests(NauDocTestCase.NauDocTestCase):

    def afterSetUp(self):
        from Products.CMFNauTools.GuardedTable import GuardedTable

        self.naudoc._setObject( 'test', GuardedTable('test') )
        self.table = self.naudoc._getOb('test')

    def testColumns(self):
        table = self.table

        col1 = table.addColumn('col1', 'Column 1', 'string')
        col2 = table.addColumn('col2', 'Column 2', 'string')
        col3 = table.addColumn(title='Column 3', type='string')
        columns = table.listColumnIds()
        self.assert_( col1 in columns )
        self.assert_( col2 in columns )
        self.assert_( col3 in columns )

        self.assertEqual( table.getColumnById(col1).getId(), col1 )
        self.assertEqual( table.getColumnById(col2).getId(), col2 )
        self.assertEqual( table.getColumnById(col3).getId(), col3 )

        self.assertEqual( table.getColumnById(col1).Title(), 'Column 1' )
        self.assertEqual( table.getColumnById(col2).Title(), 'Column 2' )
        self.assertEqual( table.getColumnById(col3).Title(), 'Column 3' )

    def testEntries(self):
        table = self.table

        col1 = table.addColumn('string_col', 'Column 1', 'string')
        col2 = table.addColumn('int_col', 'Column 2', 'int')
        col3 = table.addColumn('date_col', 'Column 3', 'date')
        col4 = table.addColumn('boolean_col', 'Column 4', 'boolean')
        col5 = table.addColumn('string2_col', 'Column 5', 'string', index_type='FieldIndex' )

        from DateTime import DateTime
        current_date = DateTime()

        data1 = {  'string_col': 'string there'
                ,     'int_col': 654321
                , 'boolean_col': 1
                ,    'date_col': current_date
                , 'string2_col': 'string there'
                }

        table.addEntry(data1)

        data2 = {  'string_col': 'string here'
                ,     'int_col': 123456
                , 'boolean_col': 0
                ,    'date_col': current_date + 1.0
                , 'string2_col': 'string here'
                }

        table.addEntry(data2)

        REQUEST = self.app.REQUEST
        REQUEST.string_col = 'where is the string?'
        REQUEST.int_col = 135780
        REQUEST.date_col = current_date - 1.0
        REQUEST.boolean_col = 1

        table.addEntry(REQUEST=REQUEST)

        results = table.searchEntries(string2_col='string there')
        self.assertEquals( len(results), 1)

        entry = results[0].getObject()
        self.assertEquals(entry.get('string_col'), 'string there')
        self.assertEquals(entry.get('int_col'), 654321)
        self.assertEquals(entry.get('boolean_col'), 1)
        self.assertEquals(entry.get('date_col'), current_date)

        record_id = entry.getId()
        table.delEntries([record_id])
        results = table.searchEntries(string2_col='string there')
        self.failIf( results )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(GuardedTableTests) )

    return suite

if __name__ == '__main__':
    framework()

