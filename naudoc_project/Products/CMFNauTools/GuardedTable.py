"""Guarded Table class.

$Id: GuardedTable.py,v 1.86 2005/06/28 06:33:54 vsafronovich Exp $
"""
__version__ = '$Revision: 1.86 $'[11:-2]

import re
from types import StringType, DictType, TupleType

import Globals
from Acquisition import aq_base, aq_get, aq_parent, Acquired
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from DocumentTemplate.sequence.SortEx import SortEx
from Record import Record
from zExceptions import Unauthorized
from ZODB.PersistentMapping import PersistentMapping
from ZODB.PersistentList import PersistentList

import BTrees.Length

from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser, _checkPermission
from Products.CMFCore import CMFCorePermissions

from Products.PluginIndexes.TextIndex.GlobbingLexicon import GlobbingLexicon

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import Catalog
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

import Config, Exceptions
from File import addFile
from Monikers import Moniker
from SimpleObjects import InstanceBase, ContentBase, ContainerBase, SimpleRecord
from Utils import InitializeClass, parseDate, cookId, \
    getLanguageInfo, translate, readLink, updateLink


class AbstractTabularBrain( AbstractCatalogBrain ):

    def getObject(self, REQUEST=None):
        """Try to return the object for this record"""
        return self.aq_parent.getentry(self.data_record_id_)

    getPath=AbstractCatalogBrain.getRID

ENTRY_ENABLED = 'enabled'

class GuardedEntry( ContentBase ):
    """
      Table entry with data security machinery
    """
    _class_version = 1.30

    meta_type = 'Guarded Entry'
    _default_view = 'view'
    isPortalContent = False

    security = ClassSecurityInfo()

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not ContentBase._initstate( self, mode ):
            return False

        if getattr(self, 'modification_history', None) is None:
            self.modification_history = PersistentList()

        if getattr(self, 'state', None) is None:
            self.state = ENTRY_ENABLED # Why this???

        if getattr(self, '_data', None) is None:
            self._data = PersistentMapping()
        elif type(self._data) is DictType:
            self._data = PersistentMapping(self._data)

        if hasattr( self, 'record_id'): # < 1.30
            delattr( self, 'record_id')

        if hasattr( self, '_table'):
            delattr( self, '_table') # <1.30

        if hasattr( self, '_files' ):
            delattr( self, '_files')

        return True

    def index_html( self, REQUEST, RESPONSE ):
        """
            Returns the entry contents
        """
        return self.table_entry_form( self, REQUEST, RESPONSE )

    # Alias for catalog indexing
    RecordId = ContentBase.getId

    getTable = ContentBase.parent

    def __getattr__(self, name):
        """
        """
        if name != '_data' and self._data.has_key(name):
            return self._data.get(name)
        raise AttributeError, name

    security.declarePrivate( 'reindex' )
    def reindex( self, idxs=[] ):
        """
        """
        self.catalog_object(self, self.getId(), idxs)

    security.declarePrivate( 'set' )
    def set(self, name, value):
        """
          Sets up an entry field with the given name/value.

          Arguments:

            'name' -- entry field id string

            'value' -- entry field value

          Write operation is allowed only if the 'isSetAllowed' guard
          method returns True value. 'Unauthorized' exception will raise
          otherwise.

        """
        if self.isSetAllowed(name) or getattr(self.parent(), '_v_table_update', 0):
            column = self.parent().getColumnById(name)
            if column is not None:
                ftype = column.Type()
                data = self._data

                if ftype == 'file':

                    # Need updateFile here
                    if value.file:
                        value = addFile( self.parent(), file=value.file )
                        if data.get(name):
                            self.parent().manage_delObjects( data.get(name) )
                    elif not value.filename:
                        value = ''
                        if data.get(name):
                            self.parent().manage_delObjects( data.get(name) )
                    else:
                        value = data.get(name)

                elif ftype == 'link':
                    value = updateLink(self, 'field', name, value)

                data[name] = value
                data['ModificationDate'] = DateTime()

            if name in self.enumerateIndexes():
                self.reindex(idxs=[name,])

        else:
            raise Unauthorized, name

    security.declarePrivate( 'update' )
    def update(self, mapping):
        """
        """
        for key, item in mapping.items():
            self.set( key, item )

    security.declareProtected(CMFCorePermissions.View, 'get')
    def get(self, name, default=None, moniker=False):
        """
          Returns an entry field.

          Arguments:

            'name' -- entry field id string

            'default' -- default field value

          Read operation is allowed only if the 'isGetAllowed' guard
          method returns True value. 'Unauthorized' exception will raise
          otherwise.

          Result:

            Entry field value.
        """
        if not self.isGetAllowed(name):
            raise Unauthorized, name

        data = self._data
        if data.has_key(name):
            column = self.getTable().getColumnById(name)
            if not column:
                return default #XXX burned away this
            value = data[name]

            if column.Type() == 'link':
                value = readLink(self, 'field', name, value, moniker=moniker)

            return value

        return default

    security.declareProtected(CMFCorePermissions.View, 'isGetAllowed')
    def isGetAllowed(self, name):
        """
          Checks whether the user is allowed to get a particular entry field.

          Arguments:

            'name' -- entry field id string

          Result:

             Boolean.
        """
        return True

    security.declareProtected(CMFCorePermissions.View, 'isSetAllowed')
    def isSetAllowed(self, name):
        """
          Checks whether the user is allowed to set a particular entry field.

          Arguments:

            'name' -- entry field id string

          Result:

             Boolean.
        """
        return self.allowed()

    security.declareProtected(CMFCorePermissions.View, 'updateHistory')
    def updateHistory(self, **kwargs):
        """
          Adds a record to the entry changes history.

          Arguments:

            'kwargs' -- keyword arguments, mapping

        """
        uname = _getAuthenticatedUser(self).getUserName()

        kwargs.setdefault( 'date', DateTime() )
        kwargs.setdefault( 'actor', uname )
        kwargs.setdefault( 'action', '' )
        kwargs.setdefault( 'text', '' )

        self.modification_history.append( kwargs )

    security.declareProtected(CMFCorePermissions.View, 'getHistory')
    def getHistory(self):
        """
          Returns the entry changes history.

          Result:

            List of dictionaries. Each dictionary has the following keys:

              'date' -- log record date

              'actor' -- user id string

              'action' -- action id string

              'text' -- user comment

        """
        return self.modification_history

    security.declareProtected(CMFCorePermissions.View, 'getData')
    def getData(self, columns=Missing, moniker=False):
        """
          Returns all read-allowed entry fields.

          Arguments:

            'columns' -- List of the column ids to be queried. Empty list
                         indicates that every column value should be
                         included into results.

          Result:

            Dictionary. Entry fields are mapped as the dictionary keys and
            values.
        """
        results = {}
        columns = columns or self.parent().listColumnIds()
        for col_id in columns:
            try:
                results[col_id] = self.get(col_id, '', moniker=moniker)
            except Unauthorized:
                pass
        return results

    security.declarePrivate('notify_afterAdd')
    def notify_afterAdd(self):
        """
            Method is invoked after the entry was created.

            XXX: _instance_onCreate should be used instead.
        """
        pass

    security.declareProtected(CMFCorePermissions.View, 'allowed')
    def allowed(self):
        """
          Checks whether the user is able to manage this entry.

        """
        creator = self._data.get('Creator')
        uname = _getAuthenticatedUser(self).getUserName()

        return creator == uname or _checkPermission(CMFCorePermissions.ModifyPortalContent, self.parent() )

    def validate(self):
        """
            Same as 'allowed' but raises Unauthorized in case the security check failed.

        """
        if not self.allowed():
            raise Unauthorized, "you are not allowed to manage '%s' entry" % self.getId()

        return True

    def SearchableText( self ):
        """
        """
        return ' '.join( map( str, self.getData().values() ) )

InitializeClass( GuardedEntry )

class GuardedColumn(InstanceBase):
    """
      Table column definition
    """
    _class_version = 1.30

    _properties = InstanceBase._properties + (
                    { 'id':'type', 'type':'string', 'mode':'w', 'default':'string' },
                    { 'id':'allows_input', 'type':'boolean', 'mode':'w', 'default':True },
                    { 'id':'mandatory', 'type':'boolean', 'mode':'w', 'default':False }
                  )

    security = ClassSecurityInfo()

    absolute_url = Acquired
    relative_url = Acquired

    def __init__(self, id, title=None, type='string', **kwargs):
        """
        """
        if not Config.AllowedColumnTypes.has_key(type):
            raise KeyError, type # TODO: add comment

        InstanceBase.__init__( self, id, title )
        self._updateProperty('type', type)

        if type in ['lines','list']:
            self._setProperty('options',[],'lines')

        # check default values
        kwargs.setdefault( 'allows_input', True )
        kwargs.setdefault( 'mandatory', False )

        for key, item in kwargs.items():
            self._updateProperty(key, item)

    security.declareProtected(CMFCorePermissions.View, 'Type')
    def Type(self):
        """
          Returns the column type

          Allowed column types are enumerated in the
          Config.allowed_column_types list.

          Result:

            String.
        """
        return self.getProperty( 'type' )

    security.declareProtected(CMFCorePermissions.View, 'allowsInput')
    def allowsInput(self):
        """
          Indicates whether the column allows user input.

          Result:

            Boolean.
        """
        return self.getProperty( 'allows_input' )

    security.declareProtected(CMFCorePermissions.View, 'isMandatory')
    def isMandatory(self):
        """
          Indicates whether the column is not removable.

          Result:

            Boolean.
        """
        return self.getProperty( 'mandatory' )

    security.declarePublic( 'DefaultValue' )
    def DefaultValue(self):
        """
          Returns the default column value regarding the column type.

          Result:

            Default column value.
        """
        # XXX: Should be moved out of the method code
        defaults = { 'string': ''
                   , 'text': ''
                   , 'float': 0.0
                   , 'int': 0
                   , 'currency' : '0.00'
                   , 'boolean': False
                   , 'date': DateTime()
                   , 'file': ''
                   , 'lines': []
                   , 'link': None
                   }
        return defaults.get( self.Type() )

    security.declareProtected( CMFCorePermissions.View, 'getColumnDescriptor' )
    def getColumnDescriptor( self, view=True, modify=True, edit=False, **kwargs ):
        """
            Returns UI field descriptor corresponding to this attribute,
            for use in 'entry_field' templates.

            Result:

                Mapping object.
        """
        modify = modify and (self.allowsInput() or edit)

        id = self.getId()
        title = self.Title()
        type = self.Type()

        desc = { 'id'          : id
               , 'name'        : id
               , 'type'        : type
               , 'multiple'    : False #self.isMultiple(),
               , 'mandatory'   : not edit #self.isMandatory() and not edit,
               , 'options'     : type=='lines' and self.getProperty('options') or []
               #, 'properties'  : self.getProperties(),
               , 'field_title' : title
               , 'title'       : title
               , 'used_NG2'     : type in ['string', 'text'] and Config.UseTextIndexNG2
               , 'message'     : ''
               , 'comment'     : ''
               , 'view'        : view
               , 'modify'      : view and modify
               }
        desc.update( kwargs )
        return desc


InitializeClass( GuardedColumn )

class TabularCatalog(Catalog):
    """
      Modified ZCatalog with TabularBrains support
    """
    def useBrains(self, brains):
        """ Sets up the Catalog to return an object (ala ZTables) that
        is created on the fly from the tuple stored in the self.data
        Btree.
        """

        class tabularbrains(AbstractTabularBrain, brains):
            pass

        scopy = self.schema.copy()

        scopy['data_record_id_']=len(self.schema.keys())
        scopy['data_record_score_']=len(self.schema.keys())+1
        scopy['data_record_normalized_score_']=len(self.schema.keys())+2

        tabularbrains.__record_schema__ = scopy

        self._v_brains = brains
        self._v_result_class = tabularbrains

class GuardedTable( ContainerBase, ContentBase, ZCatalog ):

    _class_version = 1.32

    isPrincipiaFolderish = 0

    __resource_type__ = 'content'

    __implements__ = ( ZCatalog.__implements__,
                       ContentBase.__implements__,
                     )

    security = ClassSecurityInfo()

    manage_options = ZCatalog.manage_options

    addMetaColumn = ZCatalog.addColumn
    delMetaColumn = ZCatalog.delColumn

    setTitle = ContentBase.setTitle

    def __init__( self, id, title=None, **kwargs ):
        ContentBase.__init__( self, id, title, **kwargs )

        self.columns = []
        self._catalog = TabularCatalog()
        self.__len__ = BTrees.Length.Length()

    def _initstate( self, mode ):
        # initialize attributes
        if not ContentBase._initstate( self, mode ):
            return False

        if hasattr( self, 'columns' ) and type(self.columns) is TupleType: # < 1.32
            self.columns = list(self.columns)

        return True

    def _instance_onCreate( self ):
        self._initIndexes()

    def __nonzero__( self ):
        # used to override __len__
        return True

    security.declarePublic( 'enumerateIndexes' )
    def enumerateIndexes( self ):
        """
          Returns the catalog indexes list.

          Result:

            A list of ( index_name, type ) pairs for the initial index set.
        """
        return ( ('Creator', 'FieldIndex')
               , ('ModificationDate', 'FieldIndex')
               , ('RecordId', 'FieldIndex')
               , ('allowedRolesAndUsers', 'KeywordIndex')
               )

    security.declarePublic( 'enumerateColumns' )
    def enumerateColumns( self ):
        """
          Returns the sequence of schema names to be cached in the catalog.

          Result:

            A list of strings.
        """
        return ( 'Creator',
                 'ModificationDate',
                 'RecordId',
               )

    def _initIndexes( self, clean=False ):
        # Content indexes
        indexes = self.enumerateIndexes()
        columns = self.enumerateColumns()

        for index_name, index_type in indexes:
            self.addIndex( index_name, index_type )

        # Cached metadata
        for column_name in columns:
            self.addMetaColumn( column_name )

        # Remove redundant indexes/columns
        if clean:
            all_indexes = [ i[0] for i in indexes ] \
                        + self.listColumnIds()

            for column in self.schema():
                if column not in columns:
                    self.delColumn(column)

            for index in self.indexes():
                if index not in all_indexes:
                    self.delIndex(index)

    def catalog_object(self, obj, uid=None, idxs=[]):
        """ wrapper around catalog """
        # Enable catalog to index entries using
        # getattr without any security checks
        obj._v_catalog_entry = 1  #XXX at catalog must be its own attribute????
        self._catalog.catalogObject( obj, uid, None, idxs )
        # Turn careless security policy off
        obj._v_catalog_entry = 0

    def uncatalog_object(self, uid):
        """ wrapper around catalog """
        self._catalog.uncatalogObject( uid )

    security.declareProtected( CMFCorePermissions.View, 'searchEntries' )
    def searchEntries( self, REQUEST=None, used=None, **kw ):
        """
        """
        return apply( ZCatalog.searchResults, (self, REQUEST or {}, used), kw )

    security.declareProtected( CMFCorePermissions.View, 'executeQuery' )
    def executeQuery( self, REQUEST=None, **kwargs ):
        """
        """
        REQUEST = REQUEST or aq_get(self, 'REQUEST', Globals.get_request() )

        uid = self.getUid()
        session = REQUEST['SESSION']

        sort_order = REQUEST.get('sort_order', session.get( (uid, 'sort_order'), 'asc'))
        pre_sort_on = REQUEST.get('sort_on', session.get( (uid, 'sort_on'), None))
        sort_on = self.getColumnById(pre_sort_on) is not None and pre_sort_on or self.columns[0].getId()
        batch_size= int( REQUEST.get('batch_size', session.get( (uid, 'batch_size'), 10)) )
        qs_old = int( REQUEST.get('qs', session.get( (uid, 'qs'),  1)) )
        qs = qs_old / batch_size * batch_size + 1

        query = self.getFilter(REQUEST)['query']
        query.update( kwargs )
        results = self.searchEntries( **query )

        results = SortEx( [x.getObject() for x in results], ((sort_on, 'cmp', sort_order),) )

        results_count = len(results)
        total_count = len(self)

        for name in ('qs', 'sort_order', 'sort_on', 'batch_size', 'total_count', 'results_count'):
            not name.endswith('_count') and session.set((uid, name), locals()[name])

            #to use in dtml
            REQUEST.set(name, locals()[name])

        return results

    def getFilter(self, REQUEST):
        """
        """
        default_filter = { 'conditions': REQUEST.get('conditions',[] ),
                           'query': REQUEST.get('query', {} ),
                           'query_id': REQUEST.get('query_id' ,''),
                           'profile_id': REQUEST.get('profile_id', ''),
                           'columns': self.listColumnsMetadata() # XXX when i deleted column, filter did know about this
                                                                 # need special parametr 'columns' for 'catalog_filter'
                                                                 # that updated every time
                         }

        filter_id = '%s_filter' % self.getUid()
        filter = REQUEST['SESSION'].get(filter_id, default_filter)
        return filter

    security.declareProtected( CMFCorePermissions.View, 'addEntry' )
    def addEntry( self, data=None, REQUEST=None ):
        """
            Adds a new entry to the table.

            Arguments:

              'data' -- Dictionary representing entry contents.

              'REQUEST' -- REQUEST object containing the form data to be
                           used as the entry contents. This argument is
                           effective only if the 'data' parameter is None.
        """
#        if not self.allowed():
#           return

        if data is None and REQUEST is not None:
            # Get entry info from REQUEST and place it into
            # the 'data' vocabulary
            data = self.parseEntryForm( self.listColumnIds(), REQUEST )

        entry = self._store(data, factory=GuardedEntry)
        entry.reindexObject()

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry added' )

    security.declareProtected( CMFCorePermissions.View, 'editEntry' )
    def editEntry( self, record_id, data=None, comment='', REQUEST=None, redirect=1 ):
        """
           Changes the table entry.

           Arguments:

             'record_id' -- entry id string

             'data' -- Dictionary representing entry contents.

             'common' -- user comment

             'REQUEST' -- REQUEST object containing the form data to be
                          used as the entry contents. This argument is
                          effective only if the 'data' parameter is None.

             'redirect' -- Boolean. Indicates whether it is required to
                           redirect the user to the primary object view
                           form after the entry contents was updated.
        """
        entry = self.getEntryById(record_id)
        entry.validate()

        if data is None and REQUEST is not None:
            # Get entry info from REQUEST and place it into
            # the 'data' vocabulary
            expected_columns = self.listColumnIds()
            data = self.parseEntryForm(expected_columns, REQUEST)

        self._edit(data, record_id)

        entry.updateHistory(text=comment)
        entry.reindexObject()

        if redirect and REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry updated' )

    security.declareProtected( CMFCorePermissions.View, 'delEntries' )
    def delEntries( self, selected_entries=Missing, REQUEST=None ):
        """
          Removes particular entries from the table.

          Arguments:

            'selected_entries' -- list of entries id to be removed

          Note:

            User must be granted with the 'Manage portal'
            permission to remove the entry.

        """
        selected_entries = selected_entries or []

        for id in selected_entries:
            if self.getEntryById(id).validate():
                self._remove(id)

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry deleted' )

    def listEntries(self):
        """
        """
        return [ entry for entry in self.objectValues() if isinstance(entry, GuardedEntry) ]

    security.declareProtected( CMFCorePermissions.View, 'getEntryById' )
    getEntryById = ContainerBase._getOb

    security.declarePrivate( 'parseEntryForm' )
    def parseEntryForm( self, expected_columns=Missing, REQUEST=None ):
        """
          Parses entry data from REQUEST.

          Arguments:

            'expected_columns' -- List of field ids that should be received
            from the form. This argument is essentially important for the
            processing of the boolean fields.

            'REQUEST' -- REQUEST object containing the user form data.

          Result:

            Dictionary containing the data extracted from the REQUEST form.
        """
        entry_mapping = {}
        expected_columns = expected_columns or self.listColumnIds()

        for column_id in expected_columns:
            column = self.getColumnById( column_id )
            if not (column and column.allowsInput()):
                continue

            fname = column.getId()
            ftype = column.Type()
            value = REQUEST.get( fname )
            if value is None:
                continue

            if ftype == 'date':
                value = parseDate( fname, REQUEST, None )

            if value is None:
                # should not happen
                value = column.DefaultValue()

            entry_mapping[ fname ] = value

        return entry_mapping

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'listColumnTypes' )
    def listColumnTypes(self):
        """
        """
        return Config.AllowedColumnTypes.keys()

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'getDefaultColumnType' )
    def getDefaultColumnType(self):
        """
        """
        return Config.DefaultColumnType

    security.declareProtected( CMFCorePermissions.View, 'listColumns' )
    def listColumns( self, wrapped=True ):
        """
          Returns a table columns list.

          Result:

            List of GuardedColumn class instances.
        """
        return [ wrapped and column.__of__(self) or column for column in self.columns]

    security.declareProtected( CMFCorePermissions.View, 'listColumnIds' )
    def listColumnIds( self ):
        """
          Returns a list of table columns.

          Result:

            List of columns id strings.
        """
        return [ column.getId() for column in self.columns]

    def listColumnsMetadata( self ):
        """
        """
        return [ col.getColumnDescriptor() for col in self.listColumns(False) ]

    security.declareProtected( CMFCorePermissions.View, 'listWritableColumnIds' )
    def listWritableColumnIds( self ):
        """
          Returns a list of writable columns.

          Result:

            List of columns id strings.
        """
        return self.listColumnIds()

    security.declareProtected( CMFCorePermissions.View, 'listReadableColumnIds' )
    def listReadableColumnIds( self ):
        """
          Returns a list of readable columns.

          Result:

            List of columns id strings.
        """
        return self.listColumnIds()

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'addColumn')
    def addColumn( self, id=None, title='', type='', factory=GuardedColumn, index_type=Missing, **kwargs):
        """
          Adds a new table column.

          Arguments:

            'id' -- Column id string.

            'title' -- Column title.

            'type' -- Column type string.

            'index_type' -- String representing the type of index to be
                            used for the column data indexing in the
                            catalog. TextIndex is used by default for
                            'string' and 'text' columns; FieldIndex is used
                            for other column types.

            'factory' -- Class to be used for constructing the column
                         object. GuardedColumn class is used by default.

            '**kwargs' -- Additional arguments will be passed to the factory
                          constructor.
        """
        id = cookId(self.columns, id, prefix='column', title=title, context=self)

        if id in ['data'] or hasattr( GuardedEntry, id ): # 'data' is parameter of the 'addEntry' method
            raise Exceptions.ReservedIdError( "This identifier is reserved.", id=id )

        self.columns.append( factory( id=id
                                    , title=title
                                    , type=type
                                    , **kwargs
                                    )
                           )
        self._p_changed = 1

        index_extra = None
        if index_type is Missing:
            if type in [ 'string', 'text' ]:
                if Config.UseTextIndexNG2:
                    index_type = 'TextIndexNG2'
                    properties = getToolByName( self, 'portal_properties' )

                    index_extra = SimpleRecord( Config.TextIndexNG2Options )
                    index_extra.use_stemmer = properties.getProperty('stemmer')
                    index_extra.default_encoding = getLanguageInfo( self )['python_charset']

                else:
                    index_type = 'TextIndex'
            elif type in [ 'list', 'lines', 'userlist' ]: # userlist not implemented
                index_type = 'KeywordIndex'
            elif type in [ 'date' ]:
                index_type = 'DateIndex'
            else:
                index_type = 'FieldIndex'

        self.addIndex(id, index_type, index_extra)

        if index_type == 'TextIndex':
            index = self._catalog.getIndex(id)
            index._lexicon = GlobbingLexicon()

        return id

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'delColumn')
    def delColumn( self, id ):
        """
          Removes the column from the table.

          Arguments:

            'id' -- column id string
        """
        column = self.getColumnById(id, False)

        if not column or column.isMandatory():
            return

        ctype = column.Type()
        self.columns.remove( column)
        for entry in self.listEntries():
            if ctype == 'link':
                updateLink(entry, 'field', id, None)
            elif ctype == 'file' and entry._data.get(id):
                self.manage_delObjects( entry._data.get(id) )

            if entry._data.has_key(id):
                del entry._data[id]
        self.delIndex(id)
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.View, 'getColumnById' )
    def getColumnById( self, id , wrapped=True):
        """
          Returns the column object.

          Arguments:

            'id' - column id string

        """
        for column in self.listColumns( wrapped=wrapped ):
            if column.getId() == id:
                return column
        #raise KeyError, id

    def _store( self, entry_data, factory=GuardedEntry ):
        """
          Low-level entry store routine.

          Arguments:

            'entry_data' -- Dictionary containing the entry contents.

            'factory' -- Class to be used for constructing the entry
                         object. GuardedEntry class is used by default.

           Result:

             Instantiated entry object.
        """
        id = cookId(self, prefix='entry')

        entry_number = id[id.index('_')+1:]
        title = "%s / %s %s" % (self.Title(), translate( self, 'Entry'), entry_number )

        self._setObject(id, factory(id, title) )

        entry = self.getEntryById(id)

        if not getattr(self, '_v_table_update', 0): # for what this
            entry._data['Creator'] = _getAuthenticatedUser(self).getUserName()
        # self._edit(entry_data, id)
        # must use _edit here, but fucking registry has own _edit

        entry.update( entry_data )

        self.catalog_object(entry, id)
        self.__len__.change(1)

        return entry

    def _edit( self, entry_data, id ):
        """
          Low-level entry editing routine.

            'entry_data' -- Dictionary containing the entry contents.

            'id' -- entry id
        """
        entry = self.getEntryById(id)
        entry.update( entry_data )

        self.catalog_object(entry, id)

    def _remove( self, id ):
        """
          Low-level entry deletion routine.
        """
        self.uncatalog_object(id)
        self.manage_delObjects([id])

        self.__len__.change(-1)

    def getentry(self, rid):
        """
        """
        uid = self._catalog.paths[rid]
        return self._getOb(uid)

    def getListById(self, id):
        """
            Returns elements of 'list' field

            Arguments:

                'id' -- id of requisite field

            Result:

                List.

        """
        return self.getColumnById(id).getProperty( 'options' )

InitializeClass( GuardedTable )
