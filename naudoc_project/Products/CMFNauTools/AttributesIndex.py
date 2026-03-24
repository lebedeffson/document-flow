"""
AttributesIndex

AttributesIndex class provides document category attributes search/sort
functionality. Though AttributesIndex implements the Pluggable Index interface,
it maintains it's own ZCatalog.

During the object indexing process, document category attributes are
represented as an attribute name to value mapping. Then, a special transient
object is instantiated for each attribute. According to the attribute's type,
it's value is set into the particular transient object's property. Transient
attribute object is then being cataloged and therefore every attribute is
indexed with index according to the predefined schema. While searching for the
attribute values, query is passed to the corresponding index.

$Id: AttributesIndex.py,v 1.31 2007/07/04 08:28:32 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.31 $'[11:-2]

from cgi import escape
from types import ListType, TupleType, IntType, StringType

from Globals import DTMLFile
from BTrees.IIBTree import IISet, intersection, union, multiunion
from ZODB.PersistentMapping import PersistentMapping

from Products.CMFCore.utils import getToolByName
from Products.PluginIndexes.common.PluggableIndex import \
     PluggableIndexInterface
from Products.PluginIndexes.common.util import parseIndexRequest
from Products.ZCatalog.Catalog import Catalog
from Products.ZCatalog.ZCatalog import ZCatalog

import Config
from Config import Permissions
from CatalogTool import CatalogTool
from SimpleObjects import ContainerBase
from Utils import InitializeClass, isSequence


class AttributeObject:

    meta_type = 'AttributeObject'

    def __init__( self, name, value, index_name, record ):
        self.name = name
        self.record = record
        setattr( self, index_name, value )

class AttributesIndex( ContainerBase, ZCatalog ):
    """
        Category attributes index.
    """
    _class_version = 1.00

    __implements__ = ( ContainerBase.__implements__,
                       ZCatalog.__implements__,
                       PluggableIndexInterface,
                     )

    meta_type = 'AttributesIndex'

    manage_options = ZCatalog.manage_options

    query_options = ['query', 'operator']
    operators = ['or', 'and']
    default_operator = 'or'

    _catalog_indexes = [ ('string_value', 'TextIndexNG2'),
                         ('int_value', 'FieldIndex'),
                         ('float_value', 'FieldIndex'),
                         ('currency_value', 'FieldIndex'),
                         ('boolean_value', 'FieldIndex'),
                         ('date_value', 'DateIndex'),
                         ('list_value', 'FieldIndex'),
                         ('lines_value', 'KeywordIndex'),
                         ('userlist_value', 'KeywordIndex'),
                         ('text_value', 'TextIndexNG2'),
                         ('name', 'FieldIndex'),
                         ('record', 'FieldIndex'),
                       ]

    _catalog_metadata = []

    setupIndexes = CatalogTool.setupIndexes.im_func
    enumerateIndexes = CatalogTool.enumerateIndexes.im_func
    enumerateColumns = CatalogTool.enumerateColumns.im_func

    def __init__( self, id, caller=None, ):
        ContainerBase.__init__( self, id )
        self._catalog = Catalog()
        self.attr_schema = PersistentMapping()

    def this(self):
        return self

    def clear(self):
        return self._catalog.clear()

    def _instance_onCreate( self ):
        self.setupIndexes()

    def getEntryForObject(self, document_id, default=None):
        """
           Returns all the information we have on that specific object.
        """
        record_idx = self._catalog.getIndex('record')
        attribute_ids = record_idx._index.get( document_id ) or []
        if type( attribute_ids ) is IntType:
            attribute_ids = [ attribute_ids ]
        elif attribute_ids:
            attribute_ids = attribute_ids.keys()

        return [ self._catalog.getIndexDataForRID( id ) for id in attribute_ids ]

    def registerAttribute( self, id, typ ):
        """
            Adds new attribute to the indexing schema.

            Arguments:

                'id' -- Full attribute name in a form '<Category id>.<Attribute id>',
                        e.g. 'Document.field1'.
                 TODO : use ResourceUid as id

                'typ' -- Attribute type. According to the given type, an appropriate index
                         will be selected for storing the attribute data.

            Result:

                Returns the name of index associated with given attribute type in case
                an attribute was succesfully registered. Returns None otherwise.
        """
        if not typ:
            return

        index_name = '%s_value' % typ

        if self._catalog.indexes.get(index_name) is not None:
            self.attr_schema[ id ] = index_name
            return index_name

    def unregisterAttribute( self, id ):
        """
            Adds new attribute to the indexing schema.

            Arguments:

                'id' -- Full attribute name in a form '<Category id>.<Attribute id>'.
                 TODO : use ResourceUid as id

        """
        try:
            del self.attr_schema[ id ]
        except KeyError:
            # unregister without register
            # may happen with derived attributes
            pass

    def getAttributesSchema( self ):
        """
            Returns the attribute indexing schema.

            Result:

                Dictionary. Mapping from attribute name to index name.
        """
        return self.attr_schema

    #
    # Pluggable index interface

    def index_object(self, document_id, obj, threshold=None):
        category = getattr( obj, 'category', None )
        if category is None or not obj.implements('isCategorial'):
            return 0

#        source = getattr(obj, self.source_name, None)
        source = getattr(obj, self.getId(), None)
        if source is not None:
            try:
                source = source()
            except TypeError:
                pass
            try:
                source = source.items()
            except (TypeError, AttributeError):
                pass
        else:
            return 0

        for attr_name, attr_value in source:
            # TODO as full_attr_name use ResourceUid of the attr
            full_attr_name = "%s/%s" % ( category, attr_name )
            index_name = self.attr_schema.get( full_attr_name )
            if not index_name:
                # Don't know how to handle attribute.
                cdef = obj.getCategory()
                adef = cdef and cdef.getAttributeDefinition( attr_name )
                typ = adef and adef.Type()
                index_name = self.registerAttribute( full_attr_name, typ )
                if not index_name:
                    continue

            attr_obj = AttributeObject( name=full_attr_name,
                                        value=attr_value,
                                        index_name=index_name,
                                        record=document_id,
                                      )
            self.catalog_object( attr_obj, '%s/%s' % ( full_attr_name, document_id ) )

        return 1

    def unindex_object(self, document_id):
        # Find every attribute associated with given document_id
        # and uncatalog it.
        attribute_ids = self._catalog.getIndex('record')._index.get( document_id )
        if attribute_ids is None:
            return

        if type( attribute_ids ) is IntType:
            attribute_ids = [ attribute_ids ]
        else: # attibute_ids is IITreeSet
            attribute_ids = list(attribute_ids.keys())

        for attr_id in attribute_ids:
            uid = self._catalog.paths[ attr_id ]
            self.uncatalog_object( uid )

    def _apply_index(self, request, cid=''):
        record = parseIndexRequest(request, self.getId(), self.query_options)
        if Config.Use27CatalogQuery and record.keys is None or not record.keys:
            return

        operator = record.get('operator', self.default_operator)
        if not operator in self.operators:
            raise RuntimeError,"operator not valid: %s" % escape(operator)

        if operator=='or':  set_func = union
        else:               set_func = intersection

        keys = record.keys
        if not isSequence(keys):
            keys = [keys]

        r = None
        record_idx = self._catalog.getIndex('record')

        # make locals
        _union = union
        _IISet = IISet
        _self_searchAttributes = self.searchAttributes
        _record_idx_keyForDocument = record_idx.keyForDocument
        _self_attr_schema_get = self.attr_schema.get
        for query in keys:
            query = query.copy()
            attributes = query['attributes']# query.pop('attributes')
            del query['attributes'] 

            if type( attributes ) is StringType:
                attributes = [ attributes ]

            # Find out attribues of the same index.
            query_indexes = {}
            for attr_name in attributes:
                index_name = _self_attr_schema_get( attr_name )
                if index_name:
                    query_indexes.setdefault( index_name, []).append( attr_name )

            document_ids = None
            for index_name, attr_names in query_indexes.items():
                attribute_ids = _self_searchAttributes( { 'name': attr_names,
                                                          index_name: query
                                                        }
                                                      )
                                                     
                document_ids = _union( document_ids, _IISet([ _record_idx_keyForDocument(id) for id in attribute_ids ]) )

            r = set_func( r, document_ids )

        if r is None:
            return IISet(), (self.id,)
        elif isinstance( r, IntType ):
            return IISet([r]), (self.id,)
        else:
            return r, (self.id,)

    def numObjects(self):
        """
            Returns the number of indexed objects.
        """
        record_idx = self._catalog.indexes.get('record', None)
        return record_idx is not None and record_idx.numObjects()

    def searchAttributes( self, REQUEST=None, **kw ):
        """
            Result:

                List of the attribute record ids.
        """
        results = self.searchResults( REQUEST, **kw )
        return [ r.getRID() for r in results ]

    def getSortIndex(self, args):
        """
            Returns a transient index object suitable for sorting on the particular attribute.
        """
        attr_name = self._catalog._get_sort_attr("attr", args)

        category_id, attribute_id = attr_name.split('/')
        category = getToolByName(self, 'portal_metadata').getCategory(category_id)

        sort_names = \
            [attr_name] + \
            ['%s/%s' % (category_id, attribute_id)
             for category_id in category._listDependentCategoryIds(attribute_id)]

        for name in sort_names:
            if self.attr_schema.has_key(name):
                index_name = self.attr_schema[name]
                break
        else:
            # raises CatalogError next
            return

        return TransientSortIndex(
            sort_names,
            self._catalog.getIndex(index_name),
            self._catalog.getIndex('record'),
            self._catalog.getIndex('name')
        )

InitializeClass( AttributesIndex )


class TransientSortIndex:

    def __init__(self, names, value_index, record_index, name_index):
        self.value_index = value_index
        self.record_index = record_index
        self.name_index = name_index

        # Store record ids of all AttributeObjects which are associated with the
        # given attribute names.
        attribute_ids = []
        for name in names:
            if name_index._index.has_key(name):
                attribute_ids.append(name_index._index[name])

        assert attribute_ids

        self.attribute_ids = multiunion(attribute_ids)

    def __getattr__(self, attr):
        return getattr(self.value_index, attr)

    def _keyForDocument(self, id):
        intset = intersection( self.record_index._index[ id ], self.attribute_ids )
        if not intset:
            raise KeyError, id
        return self.value_index.keyForDocument( intset[0] )

    # XXX ZCatalog in Zope 2.8 uses documentToKeyMap instead of _keyForDocument
    __getitem__ = _keyForDocument
    def documentToKeyMap(self):
        return self

    def items( self ):
        _value_index_keyForDocument = self.value_index.keyForDocument
        _record_index_keyForDocument = self.record_index.keyForDocument
        return [ ( _value_index_keyForDocument( id ), _record_index_keyForDocument( id ) ) for id in self.attribute_ids.keys() ]

    def __len__( self ):
        return len( self.attribute_ids )


manage_addAttributesIndexForm = DTMLFile('dtml/addAttributesIndex', globals())


def manage_addAttributesIndex(self, id, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a field index"""
    return self.manage_addIndex(id, 'AttributesIndex', extra=None, \
             REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)


def initialize( context ):
    # module initialization callback

    context.registerClass(
        AttributesIndex,
        permission   = Permissions.AddPluggableIndex,
        constructors = (manage_addAttributesIndexForm, manage_addAttributesIndex),
        visibility   = None,
    )
