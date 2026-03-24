"""
Contains the following compound base classes, that the corresponding
instances must inherit from:
      
     CatalogBase

     ZCatalogBase

$Id: CompoundObjects.py,v 1.12 2006/08/08 11:36:23 oevsegneev Exp $
"""
__version__ = '$Revision: 1.12 $'[11:-2]

import sys, traceback
from bisect import bisect

from AccessControl import ClassSecurityInfo
from Acquisition import Acquired, aq_base
from BTrees.IIBTree import intersection, difference, IISet

from Products.ZCatalog.Catalog import Catalog, CatalogSearchArgumentsMap, CatalogError
from Products.ZCatalog.CatalogBrains import NoBrainer, AbstractCatalogBrain
from Products.ZCatalog.Lazy import Lazy, LazyCat, LazyMap, LazyValues
from Products.ZCatalog.ZCatalog import ZCatalog

import Config
from CatalogSupport import IndexableObjectWrapper
from SimpleObjects import InstanceBase, SimpleRecord
from Utils import InitializeClass, getLanguageInfo

ZCATALOG_CACHE = False

# basic class getted from http://docs.python.org/tut/node11.html
class LazyReverse( Lazy ):
    "Iterator for looping over a sequence backwards"
    def __init__(self, data):
        self.data = data
        self.index = self._len = len(data)

    def __getitem__(self, i):
        return self.data[ len(self) - 1 - i ]

    def __iter__(self):
        return self

    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]

class CatalogBase( InstanceBase, Catalog ):

    _class_version = 1.0

    _v_brains = AbstractCatalogBrain

    security = ClassSecurityInfo()

    def __init__(self, id=None, title=None):
        InstanceBase.__init__(self, id, title=title)
        Catalog.__init__(self)

    def __setstate__(self, state):
        InstanceBase.__setstate__(self, state)
        self.updateBrains()
 
    def useBrains(self, brains):
        """ Sets up the Catalog to return an object (ala ZTables) that
        is created on the fly from the tuple stored in the self.data
        Btree.
        """
        class mybrains( self._v_brains ):
            pass

        scopy = self.schema.copy()

        scopy['data_record_id_']=len(self.schema.keys())
        scopy['data_record_score_']=len(self.schema.keys())+1
        scopy['data_record_normalized_score_']=len(self.schema.keys())+2

        mybrains.__record_schema__ = scopy

        #self._v_brains = brains
        self._v_result_class = mybrains

    def _getSortIndex(self, args):
        """Returns a search index object or None."""
        sort_index_name = self._get_sort_attr("on", args)
        if sort_index_name is not None:
            # self.indexes is always a dict, so get() w/ 1 arg works
            sort_index = self.indexes.get(sort_index_name)
            if sort_index is None:
                raise CatalogError, 'Unknown sort_on index'
            else:
                sort_index = sort_index.__of__(self) # XXX use self.getIndex instead
                if hasattr(sort_index, 'getSortIndex'):
                    sort_index = sort_index.getSortIndex(args)

                if not hasattr(sort_index, 'keyForDocument'):
                    raise CatalogError(
                        'The index chosen for sort_on is not capable of being'
                        ' used as a sort index.'
                        )
            return sort_index
        else:
            return None

    # partilly copied from Catalog class
    def sortResults(self, rs, sort_index, reverse=0, limit=None, merge=1
                   # cached lazies
                   , _lazycat = LazyCat, _lazymap = LazyMap
                   , _lazyvalues = LazyValues, _lazyreverse = LazyReverse
                   ):
        # Sort a result set using a sort index. Return a lazy
        # result set in sorted order if merge is true otherwise
        # returns a list of (sortkey, uid, getter_function) tuples
        #
        # The two 'for' loops in here contribute a significant
        # proportion of the time to perform an indexed search.
        # Try to avoid all non-local attribute lookup inside
        # those loops.
        return super( CatalogBase, self ).sortResults( rs, sort_index
                                                     , reverse=reverse
                                                     , limit=limit
                                                     , merge=merge )
        assert limit is None or limit > 0, 'Limit value must be 1 or greater'
        _intersection = intersection
        _difference = difference
        _self__getitem__ = self.__getitem__
        index_key_map = sort_index.documentToKeyMap()
        _None = None
        _keyerror = KeyError
        result = []
        append = result.append
        insert = result.insert
        if hasattr(rs, 'keys'):
            rs = rs.keys()
        rlen = len(rs)

        limit = limit or rlen

        try:
            _intersection(rs, IISet(()))
        except TypeError:
            # rs is not an object in the IIBTree family.
            # Try to turn rs into an IISet.
            rs = IISet(rs)
         
        if merge and (
            #rlen > (len(sort_index) * (rlen / 100 + 1))):
            rlen > len(sort_index) * 500):
            # The result set is much larger than the sorted index,
            # so iterate over the sorted index for speed.
            # This is rarely exercised in practice...
            
            length = 0

            for k, intset in sort_index.items():
                # We have an index that has a set of values for
                # each sort key, so we intersect with each set and
                # get a sorted sequence of the intersections.
                if not rs:
                    break

                intset = _intersection(rs, intset)
                if intset:
                    length += len(intset)
                    append((k, intset))
                    # Note that sort keys are unique.
                    if length > limit:
                        break

                    rs = _difference( rs, intset )
            
            if reverse:
                result = _lazyreverse(result)
            result = _lazycat( _lazyvalues(result), min(limit, length) )
        elif limit * 4 > rlen:
            # Iterate over the result set getting sort keys from the index
            for did in rs:
                try:
                    key = index_key_map[did]
                except _keyerror:
                    # This document is not in the sort key index, skip it.
                    pass
                else:
                    append((key, did, _self__getitem__))
                    # The reference back to __getitem__ is used in case
                    # we do not merge now and need to intermingle the
                    # results with those of other catalogs while avoiding
                    # the cost of instantiating a LazyMap per result
            if merge:
                result.sort()
                if reverse:
                    results = _lazyreverse(result)
                result = _lazyvalues(result)
            else:
                return result
        elif reverse: 
            # Limit/sort results using N-Best algorithm
            # This is faster for large sets then a full sort
            # And uses far less memory
            keys = []
            n = 0
            worst = None
            for did in rs:
                try:
                    key = index_key_map[did]
                except _keyerror:
                    # This document is not in the sort key index, skip it.
                    pass
                else:
                    if n >= limit and key <= worst:
                        continue
                    i = bisect(keys, key)
                    keys.insert(i, key)
                    insert(i, (key, did, _self__getitem__))
                    if n == limit:
                        del keys[0], result[0]
                    else:
                        n += 1
                    worst = keys[0]
            results = _lazyreverse(result)
            if merge:
                result = _lazyvalues(result) 
            else:
                return result
        elif not reverse:
            # Limit/sort results using N-Best algorithm in reverse (N-Worst?)
            keys = []
            n = 0
            best = None
            for did in rs:
                try:
                    key = index_key_map[did]
                except _keyerror:
                    # This document is not in the sort key index, skip it.
                    pass
                else:
                    if n >= limit and key >= best:
                        continue
                    i = bisect(keys, key)
                    keys.insert(i, key)
                    insert(i, (key, did, _self__getitem__))
                    if n == limit:
                        del keys[-1], result[-1]
                    else:
                        n += 1
                    best = keys[-1]
            if merge:
                result = _lazyvalues(result) 
            else:
                return result
        
        result = _lazymap( _self__getitem__, result, min(limit, len(result)) )
        result.actual_result_count = rlen
        return result
 
    if ZCATALOG_CACHE:
        # do not set cache to object, this is a class attribute
        cache = OOBTree()
 
InitializeClass( CatalogBase )

class ZCatalogBase( InstanceBase, ZCatalog ):

    _class_version = 1.0

    __implements__ = ( InstanceBase.__implements__
                     , ZCatalog.__implements__
                     )

    Catalog = CatalogBase

    IndexableObjectWrapper = IndexableObjectWrapper

    _catalog_indexes = NotImplemented
    _catalog_metadata = NotImplemented

    security = ClassSecurityInfo()

    def __init__(self, id=None, title=None ):
        InstanceBase.__init__(self, id, title=title)
        self._catalog = self.Catalog()

    def _instance_onCreate(self):
        self.setupIndexes()

    def _containment_onAdd( self, item, container ):
        self._catalog.clear()

    def executeQuery(self, query):
        raise NotImplementedError

    security.declarePrivate( 'unrestrictedSearch' )
    def unrestrictedSearch( self, REQUEST=None, **kwargs ):
        """
        """
        return ZCatalog.searchResults( self, REQUEST, **kwargs )

    def sortResults( self, results, unique=None, **kw ):
        """
            Sort results from the previous searches.

            If 'merge' argument is not None, duplicate records
            are removed from the results set
        """
        if unique:
            results = self.uniqueResults(results)

        catalog = self._catalog
        if not hasattr( catalog, '_getSortIndex' ):
            # Zope 2.5.x
            return results

        index = catalog._getSortIndex( kw )
        if index is None:
            return results

        limit   = catalog._get_sort_attr( 'limit', kw )
        order   = catalog._get_sort_attr( 'order', kw )
        reverse = order and order.lower() in ('reverse', 'descending') or 0

        return catalog.sortResults( map( lambda r: r.getRID(), results ), index, reverse, limit )

    def uniqueResults( self, results ):
        """
            Removes duplicate records from the results set.
        """
        rid_map = {}
        for r in results:
            rid_map[r.getRID()] = r

        return LazyMap( self._catalog.__getitem__, rid_map.keys(), len( rid_map ) )

    def enumerateIndexes( self ):
        """
            Returns a list of (index_name, type) pairs for the initial index set.
        """
        # create a list copy
        indexes = list( self._catalog_indexes )

        for i in range( len(indexes) ):
            index = indexes[i]
            if index[1] != 'TextIndexNG2':
                continue

            # if TextIndexNG2 is installed, tweak its options,
            # otherwise use TextIndex
            if Config.UseTextIndexNG2:
                options = SimpleRecord( Config.TextIndexNG2Options )
                options.use_stemmer = self.getPortalObject().getProperty( 'stemmer' )
                options.default_encoding = getLanguageInfo( self )['python_charset']

                indexes[i] = (index[0], index[1], options)
            else:
                indexes[i] = (index[0], 'TextIndex')

        return indexes

    def enumerateColumns( self ):
        """
            Returns a sequence of schema names to be cached.
        """
        return self._catalog_metadata

    def setupIndexes( self, idxs=Missing, check=False ):
        """
          Configure the catalog indexes/columns settings.

          Arguments:

              'idxs' -- Not implemented.

              'check' -- If true, indicates that only catalog configuration
                         analysis to be perfomed.

          Result:

              Unless 'check' is used, tuple with two lists of identifiers
              (added_indexes, added_columns).  Boolean if 'check' is on,
              indicates whether the catalog configuration needs to be update.
        """
        #print 'setup indexes of ', `self`
        indexes = []
        columns = []
        removed = 0

        index_defs  = self.enumerateIndexes()
        index_ids   = [ idx[0] for idx in index_defs ]
        column_defs = self.enumerateColumns()

        # Setup new indexes/columns
        for column in column_defs:
            if column not in self.schema():
                columns.append( column )
                if not check:
                    self.addColumn( column )

        # NB don't forget to update catalog after index was added!
        for item in index_defs:
            index, typ = item[0:2]
            extra = len(item) == 3 and item[2]
            if index in self.indexes():
                if self._catalog.getIndex( index ).meta_type != typ:
                    indexes.append( index )
                    if not check:
                        self.delIndex( index )
                        self.addIndex( index, typ, extra )
            elif index not in self.indexes():
                indexes.append( index )
                if not check:
                    self.addIndex( index, typ, extra )

        # Remove redundant indexes/columns
        for column in self.schema():
            if column not in column_defs:
                removed += 1
                if not check:
                    self.delColumn(column)

        for index in self.indexes():
            if index not in index_ids:
                removed += 1
                if not check:
                    self.delIndex(index)

        if check:
            return not not (indexes or columns or removed)
        else:
            return indexes, columns

    def addIndex(self, name, type,extra=None):
        ZCatalog.addIndex( self, name, type, extra )

        idx = self._catalog.getIndex( name )
        if hasattr( aq_base( idx ), 'manage_afterAdd' ):
            idx.manage_afterAdd( idx, self._catalog )

    def delIndex(self, name ):
        idx = self._catalog.getIndex( name )
        if hasattr( aq_base( idx ), 'manage_beforeDelete' ):
            idx.manage_beforeDelete( idx, self._catalog )

        ZCatalog.delIndex( self, name )

    def getIndexableObjectVars( object ):
        return {}

    def catalog_object( self, object, uid, idxs=[], pghandler=None ):
        #print 'catalog', uid, idxs, `object`
        vars = self.getIndexableObjectVars( object )
        w = self.IndexableObjectWrapper( vars, object )
        ZCatalog.catalog_object( self, w, uid, idxs, pghandler=pghandler )

    def uncatalog_object( self, uid ):
        #print 'uncatalog', uid
        ZCatalog.uncatalog_object( self, uid )

    # do not make private to easy reuse in subclasses
    def _url(self, ob):
        return ob.physical_path()

    security.declarePrivate('indexObject')
    def indexObject(self, object, pghandler=None):
        '''Add to catalog.
        '''
        url = self._url(object)
        self.catalog_object(object, url, pghandler=pghandler)

    security.declarePrivate('unindexObject')
    def unindexObject(self, object):
        '''Remove from catalog.
        '''
        url = self._url(object)
        self.uncatalog_object(url)

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=None):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        '''
        if idxs is None:
            idxs = []

        url = self._url(object)
 
        # check for empty tuple to only update metadata in Zope 2.6.1
        if idxs not in [ [], () ]:
            # Filter out invalid indexes.
            valid_indexes = self._catalog.indexes.keys()
            idxs = [i for i in idxs if i in valid_indexes]
        self.catalog_object(object, url, idxs=idxs)


    def refreshCatalog( self, clear=False, update=True, pghandler=None ):
        """
            Overrides ZCatalog.refreshCatalog in order to update fields for
            catalog-dependent attributes.
            Reindexes necessary objects after total catalog update.
        """
        if update:
            #ZCatalog.refreshCatalog( self, clear )

            cat = self._catalog
            paths = cat.paths.values()

            if pghandler is not None:
                pghandler.init('Refreshing catalog: %s' % self.physical_path(), len(paths))

            for i, p in enumerate(paths):
                if pghandler is not None:
                    pghandler.report(i)

                obj = self.resolve_path(p)

                if obj is None:
                    obj = self.resolve_url(p, self.REQUEST)
                if obj is not None:
                    self.indexObject( obj, pghandler=pghandler )

            self.notifyCatalogRefreshed()

        elif clear:
            # only remove invalid records
            paths = list( self._catalog.paths.values() )
            for path in paths:
                if self.resolve_path( path ) is None:
                    self.uncatalog_object( path )

    def isValidSortQuery( self, **kw ):
        """
            Checks whether it is possible to sort catalog search results with
            given sort query.
        """
        try:
            sort_index = self._catalog._getSortIndex(
                CatalogSearchArgumentsMap( None, kw )
                )
        except:
            return False
        return sort_index is not None

    def notifyCatalogRefreshed(self):
        """
            Callback. invoked after catalog refreshed 
        """
        pass

InitializeClass( ZCatalogBase )
