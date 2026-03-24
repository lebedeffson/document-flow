#! /bin/env python2.3
"""

$Id: testAttributeIndex.py,v 1.2 2005/12/10 14:29:55 vsafronovich Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

import os, sys
import Configurator


if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase

ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('TextIndexNG2')

attrs_schema = [ ('Dummy/string_field', 'string'),
                 ('Dummy/string_field2', 'string'),
                 ('Dummy/int_field', 'int'),
                 ('Dummy/text_field', 'text'),
               ]


class DummyDocument:

    meta_type = 'DummyDocument'

    category = 'Dummy'

    def __init__( self, attributes ):
        self.attributes = attributes

    def index_testAttributes( self ):
        return self.attributes

    def implements( self, features ):
        return 1

    def getCategory( self ):
        return DummyCategoryDefinition( self.category )

class DummyCategoryDefinition:
    def __init__( self, id ):
        self.id = id

    def getAttributeDefinition( self, name ):
        return DummyAttributeDefinition( name, self.id )

class DummyAttributeDefinition:
    def __init__( self, id, category ):
        self.id = id
        self.category = category

    def Type( self ):
        for name, typ in attrs_schema:
            if name == "%s/%s" % ( self.category, self.id ):
                return typ


class DummyPropertiesTool:
    def __init__( self, properties ):
        self.properties = properties

    def getProperty( self, name ):
        return self.properties[ name ]

class DummyMsg:
    def get_default_language( self ):
        return 'ru'

# List of the ( document_id, properties_mapping ) pairs. We should explicitly
# specify document_id for the purpose of index query tests. Thus, it is
# possible to ensure that query results are valid by looking for particular
# document_ids in the _apply_index response.

sample_data = [ ( 100, { 'string_field': 'Green apple',
                         'int_field': 1,
                         'text_field': 'Orange book',
                         'string_field2': 'Peach',
                       }
                ),
                ( 101, { 'string_field': 'Red apple',
                         'int_field': 50,
                         'text_field': '',
                       }
                ),
                ( 102, { 'string_field': 'Yellow lime',
                         'int_field': 22,
                         'text_field': 'Take an apple',
                       }
                ),
                ( 103, { 'string_field': 'Orange',
                         'int_field': 64,
                         'text_field': 'Book store',
                         'string_field2': 'Peach',
                       }
                ),
                ( 104, { 'string_field': 'Banana',
                         'int_field': 21,
                         'text_field': 'Panorama',
                       }
                ),
                ( 105, { 'string_field': 'Peach',
                         'int_field': 91,
                         'text_field': 'Beach',
                       }
                ),
                ( 106, { 'string_field': 'Peach',
                         'int_field': 50,
                         'text_field': '',
                         'string_field2': 'Reach',
                       }
                ),
              ]

class AttributesIndexTests( ZopeTestCase.ZopeTestCase ):

    _setup_fixture = False

    def afterSetUp( self ):
        from Products.CMFNauTools.AttributesIndex import AttributesIndex

        self.app.portal_properties = DummyPropertiesTool({'stemmer': False})#'russian'})
        self.app.msg = DummyMsg()
        self.app.idx = AttributesIndex('index_testAttributes')

        self.app.getPortalObject = lambda:self.app.portal_properties
        try:
            self.app.idx.setupIndexes()
        finally:
            del self.app.getPortalObject

#        for attr_name, index_name in attrs_schema:
#            self.app.idx.registerAttribute( attr_name, index_name )

        get_transaction().commit()

    def testIndexesConfiguration( self ):
        from Products.CMFNauTools import Config
        self.assert_(self.app.idx._catalog.indexes, 'No indexes were created during setup')

        text_index = Config.UseTextIndexNG2 and 'TextIndexNG2' or 'TextIndex'

        _catalog_indexes = [ ('string_value', text_index),
                             ('int_value', 'FieldIndex'),
                             ('boolean_value', 'FieldIndex'),
                             ('float_value', 'FieldIndex'),
                             ('currency_value', 'FieldIndex'),
                             ('date_value', 'DateIndex'),
                             ('list_value', 'FieldIndex'),
                             ('lines_value', 'KeywordIndex'),
                             ('userlist_value', 'KeywordIndex'),
                             ('text_value', text_index),
                             ('name', 'FieldIndex'),
                             ('record', 'FieldIndex'),
                           ]
        for name, meta_type in _catalog_indexes:
            idx = self.app.idx._catalog.indexes.get( name, None )

            self.assert_( idx is not None, 'No %s index' % name)
            self.assertEquals( idx.meta_type, meta_type, 'Wrong %s index type (%s),'
                                                         ' gotten %s' % ( name, meta_type, idx.meta_type ) )

    def testObjectIndexing( self ):
        """
            Ensure that number of the catalog records matches the number of indexed attributes.
        """
        expected_count = 0

        idx = self.app.idx
        for document_id, attributes in sample_data:
            idx.index_object( document_id, DummyDocument( attributes ) )

            records_count = len( idx.searchResults() )
            expected_count = expected_count + len( attributes )

            self.assertEquals( records_count, expected_count
                             , 'Wrong catalog size while '
                               'indexing (got: %s, expected: %s)' % ( records_count, expected_count ) )

        for document_id, attributes in sample_data:
            idx.unindex_object( document_id )

            records_count = len( idx.searchResults() )
            expected_count = expected_count - len( attributes )

            self.assertEquals( records_count, expected_count
                             , 'Wrong catalog size while '
                               'unindexing (got: %s, expected: %s)' % ( records_count, expected_count ) )

    def testApplyIndex( self ):
        # Create initial index contents.
        items_count = len( sample_data )
        for i in range( 0, items_count ):
            document_id, attributes = sample_data[i]
            self.app.idx.index_object( document_id, DummyDocument( attributes ) )


        # Simple attribute search.
        self.assertQuery( { 'query': [ { 'query': 'Banana',
                                         'attributes': ['Dummy/string_field']
                                       }
                                     ]
                          },
                          [ 104 ]
                        )

        self.assertQuery( [ { 'query': 'Peach',
                              'attributes': ['Dummy/string_field']
                            }
                          ]
                          ,
                          [ 105, 106 ]
                        )

        # Search for value in several indexes of the different type.
        self.assertQuery( { 'query': [ { 'query': 'Orange',
                                         'attributes': ['Dummy/string_field', 'Dummy/text_field' ]
                                       }
                                     ]
                          },
                          [ 100, 103 ]
                        )

        # Pass additional arguments to the attribute index.
        self.assertQuery( { 'query': [ { 'query': 22,
                                         'range': 'max',
                                         'attributes': ['Dummy/int_field']
                                       }
                                     ]
                          },
                          [ 100, 102, 104 ]
                        )

        # OR search
        self.assertQuery( { 'query': [ { 'query': 50,
                                         'attributes': ['Dummy/int_field']
                                       },
                                       { 'query': 'text sample',
                                         'attributes': ['Dummy/text_field']
                                       },
                                     ]
                          },
                          [ 101, 106 ]
                        )


        self.assertQuery( { 'query': [ { 'query': 60,
                                         'range': 'min',
                                         'attributes': ['Dummy/int_field', 'ignore_this']
                                       },
                                       { 'query': 'Peach',
                                         'attributes': ['Dummy/string_field']
                                       },
                                     ],
                            'operator': 'or'
                          },
                          [ 103, 105, 106 ]
                        )

        # AND search
        self.assertQuery( { 'query': [ { 'query': 91,
                                         'attributes': ['Dummy/int_field']
                                       },
                                       { 'query': 'Yellow lime',
                                         'attributes': ['Dummy/string_field']
                                       },
                                     ],
                            'operator': 'and'
                          },
                          []
                        )

        self.assertQuery( { 'query': [ { 'query': 91,
                                         'attributes': ['Dummy/int_field']
                                       },
                                       { 'query': 'Peach',
                                         'attributes': ['Dummy/string_field']
                                       },
                                     ],
                            'operator': 'and'
                          },
                          [ 105 ]
                        )

        self.app.idx._catalog.clear()

    def testSortIndex( self ):
        # Create initial index contents.
        items_count = len( sample_data )
        for i in range( 0, items_count ):
            document_id, attributes = sample_data[i]
            self.app.idx.index_object( document_id, DummyDocument( attributes ) )

        sort_index = self.app.idx.getSortIndex( {'sort_attr': 'Dummy/string_field'} )

        self.assert_(sort_index is not None, 'Missing sort index')

        self.assertRaises( AttributeError, lambda si=sort_index: getattr(si, 'keyForDocument') )

        sort_index = self.app.idx.getSortIndex( {'sort_attr': 'Dummy/int_field'} )

        self.assert_(sort_index is not None, 'Missing sort index')

        for document_id, attributes in sample_data:
            key = sort_index.keyForDocument( document_id )
            expected_key = attributes['int_field']
            self.assertEquals( key, expected_key
                             , 'Sort index error (expected '
                               'key: %s, got: %s)' % ( key, expected_key ) )

        items = sort_index.items()

        expected_items_count = len( sample_data )
        items_count = len( items )
        self.assertEquals( items_count, expected_items_count
                         , 'Sort index error (expected '
                           'items: %s, got: %s)' % ( expected_items_count, items_count ) )

        for document_id, attributes in sample_data:
            expected_item = ( attributes['int_field'], document_id )
            self.assert_( expected_item in items, 'Sort index error'
                                                  ' (missing item: %s)' % str(expected_item) )

    def assertQuery( self, query, expected ):
        """
             Query index and look for particular document ids in _apply_index response.
        """
        result, id = self.app.idx._apply_index( { 'index_testAttributes': query } )
        lst = list( result.keys() )
        lst.sort()

        expected_lst = list( expected )
        expected_lst.sort()

        self.assertEquals( lst, expected_lst
                         , 'Query: "%s", got: %s,'
                           ' expected: %s' % (query, lst, expected) )

    def beforeTearDown(self):
        app = self.app
        del app.msg
        del app.idx
        del app.portal_properties
        get_transaction().commit()         

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(AttributesIndexTests) )
    return suite

if __name__ == '__main__':
    framework()

