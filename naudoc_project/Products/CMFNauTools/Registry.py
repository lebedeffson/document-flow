"""
Implementation of the registry mechanism for documents and other objects.

Contains RegistryColumn, RegistryEntry, Registry and some auxiliary classes and methods.

$Id: Registry.py,v 1.87 2005/11/14 18:00:44 vsafronovich Exp $
"""

__version__ = '$Revision: 1.87 $'[11:-2]

import Globals
import re, string, os.path, time
from string import join, strip
from types import ListType, StringType
from random import random

from AccessControl import Permissions as ZopePermissions
from Acquisition import aq_base, aq_parent
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from ZPublisher.Converters import type_converters as _type_converters
from ZODB.POSException import ConflictError

import BTrees.Length

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import _getAuthenticatedUser, _checkPermission

from RegistrationBook import TotalSequence as RegistrySequenceStorage, \
    DailySequence as DailyCounter

import Features
from Exceptions import SimpleError
from Features import createFeature
from GuardedTable import GuardedTable, GuardedEntry, GuardedColumn
from Config import Roles
from Monikers import Moniker
from Utils import InitializeClass, getObjectByUid, formatPlainText, updateLink


RegistryType = { 'id'             : 'Registry'
               , 'meta_type'      : 'Registry'
               , 'title'          : "Registry"
               , 'description'    : "Registry"
               , 'icon'           : 'registry_icon.gif'
               , 'product'        : 'CMFNauTools'
               , 'factory'        : 'addRegistry'
               , 'permissions'    : ( CMFCorePermissions.ModifyPortalContent, )
               , 'immediate_view' : 'registry_options_form'
               , 'condition'      : 'python: 0'
               , 'actions'        :
                 ( { 'id'            : 'view'
                   , 'name'          : "View"
                   , 'action'        : 'registry_view'
                   , 'permissions'   : (CMFCorePermissions.View,)
                   },
                   { 'id'            : 'edit'
                   , 'name'          : "Registry options"
                   , 'action'        : 'registry_options_form'
                   , 'permissions'   : (CMFCorePermissions.ModifyPortalContent,)
                   },
                   { 'id'            : 'import'
                   , 'name'          : "Import from file"
                   , 'action'        : 'registry_import_form'
                   , 'permissions'   : (CMFCorePermissions.ModifyPortalContent,)
                   , 'category'      : 'object'
                   },
                   { 'id'            : 'export'
                   , 'name'          : "Export to MS Excel"
                   , 'action'        : 'registry_export_form'
                   , 'permissions'   : (CMFCorePermissions.View,)
                   , 'category'      : 'object'
                   },
                 )
               }

def addRegistry(self, id, title='', description=''):
    """
        Creates the Registry object.

        Arguments:

          id -- Id of the registry.

          title -- Title of the registry.

          description -- Short description of the registry.

        Result:

          None
    """
    self._setObject( id, Registry(id, title, description) )


class RegistryColumn(GuardedColumn):
    """
        Registry column definition.
    """

    _properties = GuardedColumn._properties + (
                    { 'id':'editable_after_reg', 'type':'boolean', 'mode':'w', 'default':False },
                    { 'id':'_onCreateExpression', 'type': 'string', 'mode':'w','default':None},
                    { 'id':'sort_index', 'type':'int', 'mode':'w', 'default':False },
                    { 'id':'visible', 'type':'boolean', 'mode':'w', 'default':True },
                    { 'id':'width', 'type':'int', 'mode':'w', 'default':100 },
                    { 'id':'exportable', 'type':'boolean', 'mode':'w', 'default':True },
                  )

    security = ClassSecurityInfo()

    _class_version = 1.6


#    def __init__(self, id,
#                 title=None,
#                 type=None,
#                 allows_input=1,
#                 mandatory=0,
#                 editable=0,
#                 visible=1,
#                 width=100,
#                 exportable=1, **kwargs):
#       """
#            Constructs new registry column.
#
#            Extends GuardedColumn.__init__() - adds property 'editable after
#            regisration'.
#
#            Arguments:
#
#                'id' -- Id of the column.
#
#                'title' -- Columns's title.
#
#                'typ' -- Type of the column. For now it may be one of the following:
#                    'int', 'float', 'string', 'text', 'boolean', 'date', 'file'.
#
#                'allows_input' -- If true, column will allows input. Otherwise
#                    it will not be available for input.
#
#                'mandatory' -- The mandatory column is not allowed for removal.
#
#                'container' -- Container for the registry column object (Registry).
#
#                'editable' -- If true, this column will allows data modification by
#                    creator of the entry.
#
#                'visible' -- If false, this column is not shown
#
#                'width' -- width of the column, that will use in export to excel
#        """
#
#        GuardedColumn.__init__(self, id, title, type, allows_input, mandatory)
#        self._updateProperty( 'visible', visible )
#        self._updateProperty( 'width', width )
#        self._updateProperty( 'editable_after_reg', editable )
#        self._updateProperty( 'exportable', exportable )


    def _initstate(self,mode):
        """ Initialize attributes
        """
        if not GuardedColumn._initstate( self, mode ):
            return 0

        if not hasattr(self, 'visible'):
            self.visible = True

        if not hasattr(self, 'width'):
            self.width = 100

        if not hasattr(self, 'exportable'):
            self.exportable = True

        return 1

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'edit')
    def edit( self
            , title=Missing
            , editable=Missing
            , allows_input=Missing
            , visible=Missing
            , width=Missing
            , exportable=Missing):
        """
            Changes title, 'editable' property and input characteristics.

            Arguments:

                'title' -- Title of the column to be shown.

                'editable' -- Boolean value (not None). If true, records
                    in this column will allow edit.

                'allows_input' -- Boolean value (not None). If true, column
                    will allow data input.

                'visible' -- Boolean value. If false, this column is not shown.

                'width' -- width of the column, that will used in export to excel.

            Result:

                None

        """
        if title is not Missing:
            self._updateProperty( 'title', title )

        if allows_input is not Missing:
            self._updateProperty( 'allows_input', allows_input )

        if editable is not Missing:
            self._updateProperty( 'editable_after_reg', editable )

        if visible is not Missing:
            self._updateProperty( 'visible', visible )

        if width is not Missing:
            self._updateProperty( 'width', width )

        if exportable is not Missing:
            self._updateProperty( 'exportable', exportable )

    def __cmp__(self, other):
        #Compare operations support.
        #Used to build sorted list of columns.
        return cmp(self.sort_index, other.sort_index)

    security.declareProtected(CMFCorePermissions.View, 'isEditableAfterReg')
    def isEditableAfterReg(self):
        """
            Returns true if column allows edit after the entry hes been added.

            Result:

                Boolean
        """
        return self.getProperty('editable_after_reg')

    security.declareProtected(CMFCorePermissions.View, 'computeValue')
    def computeValue(self, entry):
        """
            Returns current value from portal_catalog for registered object
            in the entry according self._onCreateExpression.

            Arguments:

                'entry' -- RegistryEntry object.

            Note:

                If called in some context that has no acquisition wrapper
                (e.g. __getattr__()), it will be returned empty value correspnding
                column's type. Result will be the same if there is no registered
                object.

            Result:

                Type of returned value depends on columns's type.
        """
        registry_id = entry and entry.get('ID')
        catalog = getToolByName(entry, 'portal_catalog')
        res = catalog.unrestrictedSearch(registry_ids=registry_id, implements='isDocument')
        result = None
        if res:
            try:
                result = res[0][ self._onCreateExpression ]
            except:
                pass
        if result:
            if self._onCreateExpression=='category':
                mdtool = getToolByName(entry, 'portal_metadata')
                category = mdtool.getCategoryById(result)
                if category:
                    result = category.Title()
            elif self._onCreateExpression=='state':
                cat = res and res[0][ 'category' ]
                wftool = getToolByName(entry, 'portal_workflow')
                wf_id = wftool._getCategoryWorkflowFor( res[0].getObject(), category=cat )
                state_title = None
                try:
                    state_title = wftool.getStateTitle(wf_id, result)
                except TypeError:
                    pass
                result = state_title or result

        result = self.convertToType(result)
        return result

    security.declareProtected(CMFCorePermissions.View, 'isComputed')
    def isComputed(self):
        """
            Returns true if no input data needed (the value is computed).

            Result:

                Boolean
        """
        return not not self.getProperty('_onCreateExpression')

    security.declareProtected(CMFCorePermissions.View, 'convertToType')
    def convertToType(self, value):
        """
            Converts data to type self.Type().

            Arguments:

                'data' -- Object of any type (usually string, numeric, DateTime or None)

            Note:

                If the attempt of type cast to column's type will fail, the
                    default value for this type will be returned.
        """
        ctype = self.Type()

        if type(value) is StringType and _type_converters.has_key( ctype ):
            try:
                value = _type_converters[ ctype ]( value )
            except (IndexError, ValueError, TypeError):
                value = self.DefaultValue()

        return value

    security.declareProtected( CMFCorePermissions.View, 'getSystemFieldType' )
    def getSystemFieldType( self ):
        """
            Returns type of system field.

            Result:

                _onCreateExpression string
        """
        return self.getProperty('_onCreateExpression')

    security.declareProtected( CMFCorePermissions.View, 'isVisible' )
    def isVisible( self ):
        """
            Returns true if column is visible (is shown in view mode), or false otherwise.

            Result:

                Boolean
        """
        return self.getProperty('visible')

    security.declareProtected( CMFCorePermissions.View, 'isExportable' )
    def isExportable( self ):
        """
            Returns true if column is exportable to excel, or false otherwise.

            Result:

                Boolean
        """
        return self.getProperty('exportable')


    security.declareProtected( CMFCorePermissions.View, 'getWidth' )
    def getWidth( self ):
        """
           Returns the width of the column

           Results :

               integer width
        """
        return self.getProperty( 'width' )

InitializeClass( RegistryColumn )

class RegistryEntry(GuardedEntry):
    """
        Registry enty definition.
    """

    _class_version = 1.3

    security = ClassSecurityInfo()

    def index_html( self, REQUEST, RESPONSE ):
        """
            Returns the entry contents
        """
        return self.registry_entry_form( self, REQUEST, RESPONSE )

    security.declareProtected(CMFCorePermissions.View, 'isEditAllowed')
    def isEditAllowed(self, name):
        """
            Defines whether the current user is allowed to set an entry record

            Arguments:

                'name' -- Requested record id (same as column id).
        """
        column = self.parent().getColumnById(name)
        if not column:
            return 0

        has_perm = _checkPermission(CMFCorePermissions.ModifyPortalContent, self.parent() )
        is_owner = self._data.get('Creator', None) == _getAuthenticatedUser(self).getUserName()
        is_editable_column = column.isEditableAfterReg()

        if has_perm or (is_owner and is_editable_column):
            return 1

        return 0

    def get(self, name, default=None, moniker=False):
        """
            Reads record with the given name from the entry or computes
            the result if the requested column is computed.

            Arguments:

                'name' -- Column id.

                'default' -- The default value (if no result found).

            Result:

                Found data or value given in 'default' argument or None.

        """
        if not self.isGetAllowed( name):
            raise Unauthorized, name

        column = self.parent().getColumnById(name)
        if column is None:
            return

        value = GuardedEntry.get(self, name, default=default, moniker=moniker)

        if column.isComputed():
            try:
                value = column.computeValue( self )
            finally:
                self.parent()._edit( entry_data={name:value}, index = self.getId() )

        return value


InitializeClass( RegistryEntry )

class Registry(GuardedTable):
    """ Registry class

        Registry establishes an interaction between NauDoc and conventional docflow.
    """
    _class_version = 1.46

    meta_type = 'Registry'
    portal_type= 'Registry'

    __implements__ = ( createFeature('isRegistry')
                     , Features.isPortalContent
                     , Features.isPrintable
                     , GuardedTable.__implements__
                     )

    _properties = GuardedTable._properties + (
                    { 'id':'department', 'type':'string', 'mode':'w', 'default':'' },
                    { 'id':'_author_can_delete_entry', 'type':'boolean', 'mode':'w', 'default':False },
                    { 'id':'reg_num_forming_rule', 'type':'string', 'mode':'w', 'default':'\Seq' },
                    { 'id':'excel_font_size', 'type':'int', 'mode':'w', 'default':10 },
                    { 'id':'excel_landscape_view', 'type':'boolean', 'mode':'w', 'default':False },
                    { 'id':'parent_registry', 'type':'string', 'mode':'w', 'default':'' },
                  )

    security = ClassSecurityInfo()

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'delColumn' )

    export_excel_form = Globals.DTMLFile( 'skins/registry/excel_export_form', globals() )

    def __init__( self, id, title='', description='' ):
        """
            Constructs new registry instance.

            Arguments:

                'id' -- Id of the registry.

                'title' -- Title of the registry.

                'description' -- Description of the registry.
        """
        GuardedTable.__init__( self, id, title, description )

    def _initstate( self, mode ):
        # initialize attributes
        if not GuardedTable._initstate( self, mode ):
            return 0

        if not hasattr(self, 'parent_registry'):
            self.parent_registry = None

        if not hasattr(self, 'reg_num_forming_rule'):
            self.reg_num_forming_rule = '\Seq'

        if not hasattr(self, '_author_can_delete_entry'):
            self._author_can_delete_entry = None

        if not hasattr(self, '_kw_list'):
            self._kw_list = {}

        for id in self.objectIds():
            self._upgrade( id, RegistryEntry, container=self )

        if hasattr( self, 'columns' ):
            for i in range( len(self.columns) ):
                self._upgrade( i, RegistryColumn, container=self.columns )
            si = 0
            for column in self.listColumns():
                column.sort_index = si
                si += 1

        if not hasattr(self, 'excel_font_size'):
            self.excel_font_size = 10

        if not hasattr(self, 'excel_landscape_view'):
            self.excel_landscape_view = False

        # update only OLD registries
        if mode and not hasattr( self, 'daily_counter' ):
            self.daily_counter = DailyCounter( "%s_daily" % self.getUid(), start_value=1 )

        if mode and not hasattr( self, 'safe_sequence' ):
            if hasattr(self, 'last_id'):
                last_id = self.last_id
                del self.last_id
            else:
                last_id = 1
            self.safe_sequence = RegistrySequenceStorage( self.getUid(), start_value=last_id )

        if mode:
            if not hasattr( self.safe_sequence, 'setValue' ):
                self.safe_sequence = RegistrySequenceStorage( self.getUid(), start_value=self.safe_sequence.last_value )

            elif getattr( self.safe_sequence, 'id', None ) is None:
                self.safe_sequence = RegistrySequenceStorage( self.getUid(), start_value=self.safe_sequence.getLastValue() )
                self.daily_counter = DailyCounter( "%s_daily" % self.getUid(), start_value=self.daily_counter.getLastValue() )

        return 1

    def _instance_onCreate( self ):
        # instance creation event callback
        self.safe_sequence = RegistrySequenceStorage( self.getUid(), start_value=1 )
        self.daily_counter = DailyCounter( "%s_daily" % self.getUid(), start_value=1 )

        self.addColumn(id='ID', title='Registration number', type='string', allows_input=0, mandatory=1, index_type='FieldIndex')
        self.addColumn(id='receipt_date', title='Receipt date', type='date')
        self.addColumn(id='creation_date', title='Creation date', type='date', allows_input=0, mandatory=1)
        self.addColumn(id='Creator', title='Entry creator', type='string', allows_input=0, mandatory=1)
        self.addColumn(id='contents', title='Brief contents', type='text', editable_after_reg=1)
        self.addColumn(id='instructions', title='Instructions', type='text', editable_after_reg=1)
        self.addColumn(id='forwarded_to', title='Forwarded to', type='string', editable_after_reg=1)
        self.addColumn(id='filed_to', title='Filed to', type='string', editable_after_reg=1)

    def _instance_onClone( self, source, item ):
        # instance clone event callback
        self.safe_sequence = RegistrySequenceStorage( self.getUid(), start_value=source.safe_sequence.getLastValue() )
        self.daily_counter = DailyCounter( "%s_daily" % self.getUid(), start_value=source.daily_counter.getLastValue() )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'editColumn' )
    def editColumn(self, id=None, title=None, editable_after_reg=None, allows_input=None, visible=None, REQUEST=None):
        """
            Changes column properties.

            Arguments:

                'id' -- Column id.

                'title' -- Column's new title.

                'editable_after_reg' -- If true, records in the column will
                    allow edit.

                'allows_input' -- If true, column will allow data input.

            Result:

                None
        """
        column = self.getColumnById( id )
        if column is None:
            if REQUEST is not None:
                self.redirect( REQUEST=REQUEST
                             , action='registry_view'
                             , message='Column with given id not found.')
            return

        column.edit(title, editable_after_reg,
                           allows_input,
                           visible,
                           width = REQUEST.get( 'width' ),
                           exportable = REQUEST.get( 'exportable', 0) )

        if column.Type() == 'lines':
            self._kw_list[id] = list(REQUEST.get('value_list'))
            self._p_changed = 1

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST
                         , action='registry_options_form'
                         , message='Column data changed.')

    def enumerateIndexes( self ):
        #   Return a list of ( index_name, type ) pairs for the initial
        #   index set.
        #   'Creator' indexremoved because it is created with the entry 'Creator'
        return ( ('ModificationDate', 'FieldIndex')
               , ('RecordId', 'FieldIndex')
               , ('allowedRolesAndUsers', 'KeywordIndex')
               )

    security.declareProtected( CMFCorePermissions.AddPortalContent, 'addColumn' )
    def addColumn( self, id=None, title='', type='', index_type=Missing, system_field=None, **kwargs ):
        """
            Creates new registry column.

            Arguments:

                'id' -- Id of the created column.

                'title' -- New columns's title.

                'typ' -- Type of the column. For now it may be one of the following:
                    'int', 'float', 'string', 'text', 'boolean', 'date', 'file'.

                'allows_input' -- If true, column will allows input. Otherwise
                    it will not be available for input.

                'mandatory' -- The mandatory column is not allowed for removal.

                'editable' -- If true, this column will allows data modification by
                    creator of the entry.

                'system_field' -- The system field calculates it's value by
                    requesting portal_catalog for given property of the
                    registered object.

                    Exclusions: 'category' and 'state'. They are calculated
                        using portal_category or portal_workflow.

                'index_type' -- String representing the type of index to be
                            used for the column data indexing in the
                            catalog. TextIndex is used by default for
                            'string' and 'text' columns; FieldIndex is used
                            for other column types.

                'factory' -- Class to be used for constructing the column
                         object. RegistryColumn class is used by default.

        """
        kwargs.setdefault( 'editable_after_reg', False )
        kwargs.setdefault( 'visible', True )
        kwargs.setdefault( 'width', 100 )
        kwargs.setdefault( 'exportable', True )
        kwargs.setdefault( 'sort_index', len(self.listColumns()) + 1 )

        if system_field:
            kwargs['_onCreateExpression'] = system_field
            kwargs['allows_input'] = 0
            kwargs['editable_after_reg'] = 0

        return GuardedTable.addColumn( self
                                     , id
                                     , title
                                     , type
                                     , factory=RegistryColumn
                                     , index_type=index_type
                                     , **kwargs)

    def getLastSequenceNumber(self):
        """
            Returns last sequence number.
        """
        return self.safe_sequence.getLastValue()

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'moveColumn' )
    def moveColumn(self, column_id=None, direction=1, REQUEST=None):
        """
            Moves column up or down (changes order of columns).

            Arguments:

                'column_id' -- Id of the column to move.

                'direction' -- Direction. Value 1 means move up, -1 - move down.
        """
        direction = int(direction)
        sorted_columns = self.listColumns()
        column = self.getColumnById( column_id )
        ckey = sorted_columns.index( column )

        while 1:
            if direction not in [1,-1] or \
               direction==1 and ckey <= 0 or \
               direction==-1 and ckey >= len(sorted_columns) - 1:
                break

            target_column = sorted_columns[ ckey - direction ]
            column.sort_index, target_column.sort_index = target_column.sort_index, column.sort_index
            break

        self.listColumns()

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST, action='registry_options_form' )

    def listColumns( self, wrapped=True ):
        """
            Returns a registry sorted columns list.

            Extends GuardedTable.listColumns() - adds columns sorting.
        """
        results = GuardedTable.listColumns( self )
        results.sort()
        return results

    def listVisibleColumns( self ):
        """
            Returns visible columns list.

            Extends listColumns()
        """
        return [ column for column in self.listColumns() if column.isVisible() ]

    security.declareProtected( CMFCorePermissions.View, 'listRegisteredDocumentsForEntry' )
    def listRegisteredDocumentsForEntry(self, entry):
        """
            Searches document(s) (brains) which are registered in the entry.

            Arguments:

                'entry' -- RegistryEntry which stores record about document(s)

            Result:

                List of mybrains.
        """
        registry_id = entry.get('ID')
        if registry_id is None:
            return []
        catalog = getToolByName(self, 'portal_catalog')
        documents = catalog.searchResults( registry_ids=registry_id,
                                           implements='isDocument')
        #leave documents registered only in this registry
        results = []
        for document_brain in documents:
            document = document_brain.getObject()
            registry_data = getattr(document, 'registry_data', {})
            registries = registry_data.get( registry_id, [] )
            if self.getUid() in registries:
                results.append( document_brain )
        return results

    def parseEntryForm(self, expected_columns=None, REQUEST=None):
        """
            Parses entry data from REQUEST.

            Extends GuardedTable.parseEntryForm() - adds computed columns
                processing.

            Arguments:

                'expected_columns' -- List of field ids that should be received
                from the form. This argument is essentially important for the
                processing of the boolean fields.
        """
        columns = self.listColumns()
        computed_columns = [x for x in columns if x.isComputed()]
        computed_columns_ids = [x.getId() for x in computed_columns]

        if expected_columns is None:
            expected_columns = [x.getId() for x in columns if not x.isComputed()]
        else:
            expected_columns = [x for x in expected_columns if x not in computed_columns_ids]

        entry_mapping = GuardedTable.parseEntryForm(self, expected_columns, REQUEST)
        for column in computed_columns:
            entry_mapping[ column.getId() ] = column.DefaultValue()
        return entry_mapping


    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setDepartment' )
    def setDepartment( self, department):
        """
          Sets up the department id.

          Used for the document registry id creation
        """
        self._updateProperty( 'department', department )

    security.declareProtected( CMFCorePermissions.View, 'getDepartment' )
    def getDepartment( self ):
        """
          Returns the department id.
        """
        return self.getProperty( 'department' )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setParentRegistry' )
    def setParentRegistry(self, parent_registry=''):
        """
            Sets up the parent registry.

            Arguments:

                'parent_registry' -- nd_uid of the parent registry.
        """
        self._updateProperty('parent_registry', '' )

        ob = getObjectByUid(self, parent_registry)
        if ob is not None:
            self._updateProperty( 'parent_registry', parent_registry )

    security.declareProtected( CMFCorePermissions.View, 'getParentRegistry' )
    def getParentRegistry( self ):
        """
            Returns uid of the parent registry.
        """
        return self.getProperty('parent_registry')

    security.declareProtected( CMFCorePermissions.View, 'releaseSelectedDocument' )
    def releaseSelectedDocument( self, redirect=1, REQUEST=None):
        """
            Resets the document preselected for registration.
        """
        session = REQUEST['SESSION']
        if session.has_key('came_from'):
            session.delete('came_from')
        if session.has_key('came_version_id'):
            session.delete('came_version_id')

        if redirect:
            self.redirect( REQUEST=REQUEST )

    security.declareProtected( CMFCorePermissions.AddPortalContent, 'assign' )
    def assign( self, registry_id, came_from, came_version_id, REQUEST=None):
        """
            Assigns document to the given entry ID.
        """
##        catalog = getToolByName(self, 'portal_catalog')
##        # Ensure that there is no document already assigned
##        res = catalog.searchResults( registry_id = registry_id )
##        if res:
##           return
#        ob = getObjectByUid(self, came_from)
        ob = self._getSourceObject(came_from, came_version_id, REQUEST)
        if ob is not None:
            #check if object is already registered
            if self.isObjectRegistered(ob):
                message = "Document is already registered"
                obj = ob or self
                return REQUEST[ 'RESPONSE' ].redirect( obj.absolute_url(message = message ) )
            if not hasattr(ob, 'registry_data'):
                ob.registry_data = {}

            s_reg_data = getattr(ob, 'registry_data', {})

            if registry_id in s_reg_data.keys():
                if not self.getUid() in s_reg_data[ registry_id ]:
                    s_reg_data[ registry_id ].append( self.getUid() )
            else:
                s_reg_data[ registry_id ] = [ self.getUid() ]

            ob._p_changed = 1
            ob.manage_permission(ZopePermissions.delete_objects, [Roles.Manager], 0)
            ob.reindexObject(idxs=['registry_ids',])

        if REQUEST['SESSION'].has_key('came_from'):
            REQUEST['SESSION'].delete('came_from')
        if REQUEST['SESSION'].has_key('came_version_id'):
            REQUEST['SESSION'].delete('came_version_id')


        self.redirect( message='Document assigned' )

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setInternalCounter')
    def setInternalCounter(self, new_counter=0):
        """
            Sets internal counter for registry ids value.
        """
        self.safe_sequence.setValue( new_counter )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setRegNumFormingRule' )
    def setRegNumFormingRule(self, reg_num_forming_rule):
        """
            Sets registry number forming rule.
        """
        self._updateProperty( 'reg_num_forming_rule', reg_num_forming_rule )

    security.declareProtected( CMFCorePermissions.View, 'exportToExcel' )
    def exportToExcel(self, REQUEST=None):
        """
            Generates html (with xml parts) presentation of the registry.

            Generated html is saved as *.xls file.

            Note:
                Partial support for Excel 97, full support for Excel 2000 and above.

            Result:
                HTML text.

        """
        lang = getToolByName( self, 'portal_membership' ).getLanguage( REQUEST=REQUEST )
        filename = self.title_or_id()

        # replace illegal characters
        #tr_filename = re.sub( r'[^\w\.\_\-\s~]+', '', tr_filename )
        filename = re.sub( r'[^\w\.\_\-\s~]+(?L)', '', filename )

        if not filename:
            filename = 'file'

        setHeader = REQUEST.RESPONSE.setHeader
        setHeader("Content-Type", "application/vnd.ms-excel; name='excel'");
        setHeader("Content-type", "application/octet-stream");
        setHeader("Content-Disposition", "attachment; filename=%s.xls" % filename);
        setHeader("Cache-Control", "must-revalidate, post-check=0, pre-check=0");
        setHeader("Pragma", "no-cache");
        setHeader("Expires", "0");

        self.excel_font_size = font_size = REQUEST.get('font_size')
        self.excel_landscape_view = landscape_view = REQUEST.get('landscape_view',0)
        columns = [x.getId() for x in self.listColumns() if REQUEST.get(x.getId())]
        widths = [ REQUEST.get('width_%s'%x) for x in columns ]
        include_changes_log = REQUEST.get('include_changes_log')

        result_text = self.export_excel_form(self
                                            , REQUEST=REQUEST
                                            , columns_ids=columns
                                            , widths=widths
                                            , include_log=include_changes_log
                                            , excel_font_size=font_size
                                            , excel_landscape_view=landscape_view
                                            )
        return result_text

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'importFromCSV' )
    def importFromCSV(self, csv_file=None, csv_columns=None, ignore_titles=None, use_internal_reg_numbers=None, REQUEST=None):
        """
            Imports data from CSV(comma separated values) file.

            Arguments:

                'csv_file'  -- FileUpload instance - file in MS Excel CSV format.

                'csv_columns'  -- Columns ids to be imported. Specifies order
                    of columns in the file.

                'ignore_titles' -- If true it is considered that the first row
                    in the file contains titles.

                'use_internal_reg_numbers' -- If true, registrative numbers for
                    entries will be generated according forming rule.

            Note:

                Tested only MS Excel format of CSV file.

            Result:

                None. Redirect with status message.
        """
        if not csv_file:
            message = 'Please choose file'
        if not csv_columns:
            message = 'Please choose column(s)'
        elif isinstance( csv_file, ListType):
            #this bug may take place in IE5.0, when interface language is
            # set to english, file name contains russian characters.
            message = 'Please use the same language as characters in the file name'
        else:
            data = csv_file.readlines()
            csv_file.close()
            if not data:
                message = "File is empty"
                if REQUEST is not None:
                    return self.redirect( REQUEST=REQUEST, message=message)

            #TODO: remove comments in data(#).
            raw_lines = map(strip, data)
            lines = []
            line = ''
            #long line may be splitted by '\\'
            for l in raw_lines:
                if not l:
                    continue
                if l.endswith('\\'):
                    line += l[:-1] + '\n'
                else:
                    lines.append(line + l)
                    line = ''

            if ignore_titles:
                lines = lines[1:]

            message = None
            for line in lines:
                flds = list(self._line_process(line, separator=';'))
                data = {}

                if use_internal_reg_numbers:
                    try:
                        csv_columns.remove('ID')
                    except ValueError:
                        pass
                columns = [self.getColumnById(x) for x in csv_columns]

                #columns = filter( lambda x: x.allowsInput(), self.listColumns())
                if len(flds) != len(columns):
                    raise IndexError, 'Number of columns in the file does not match.'

                #convert all fields to types in corresponding columns
                for i in range(0, len(flds)):
                    column = columns[i]
                    c_type = column.Type()

                    if c_type in ['string','text','lines']:
                        # do not use try/except here. Raise exception on error.
                        newObject = flds[i][:]
                    elif c_type == 'float':
                        newObject = float( flds[i].replace(',', '.') )
                    elif c_type == 'int':
                        newObject = int( flds[i] )
                    elif c_type == 'boolean':
                        newObject = not not int( flds[i] ) or None
                    elif c_type == 'date':
                        newObject = DateTime( flds[i] )
                    data[ column.getId() ] = newObject

                reg_num = None
                if data.has_key('ID'):
                    reg_num=data['ID']
                    del data['ID']

                message = self.addEntry(data=data, REQUEST=REQUEST, registry_id=reg_num )
                if message:
                    break
        if REQUEST is not None:
            return self.redirect( REQUEST=REQUEST, message=(message or "Entries added"))

    #this is adapted method from CSV 0.17  (8 June 1999) by Laurence Tratt
    #TODO: use python 2.3 CSV module instead.
    def _line_process(self, line, separator=';'):
        fields = []
        line_pos = 0

        while line_pos < len(line):
            # Skip any space at the beginning of the field (if there should be leading space,
            #   there should be a " character in the CSV file)
            while line_pos < len(line) and line[line_pos] == " ":
                line_pos += 1
            field = ""
            quotes_level = 0
            while line_pos < len(line):
                # Skip space at the end of a field (if there is trailing space, it should be
                #   encompassed by speech marks)
                if not quotes_level and line[line_pos] == " ":
                    line_pos_temp = line_pos
                    while line_pos_temp < len(line) and line[line_pos_temp] == " ":
                        line_pos_temp += 1
                    if line_pos_temp >= len(line):
                        break
                    elif line[line_pos_temp] == separator:
                        line_pos = line_pos_temp
                if not quotes_level and line[line_pos] == separator:
                    break
                elif line[line_pos] == "\"":
                    quotes_level = not quotes_level
                else:
                    field = field + line[line_pos]
                line_pos += 1
            line_pos += len(separator)
            fields.append(field)
        if line[-len(separator)] == separator:
            fields.append(field)

        return fields

    def _generate_registry_id(self, object):
        #Generates registry id for the given object according reg. number forming rule.
        folder_nomencl_num = object is not None and object.parent().getCategoryAttribute('nomenclative_number') or ''
        folder_postfix = object is not None and object.parent().getCategoryAttribute('postfix') or object is None and '-'
        category_postfix = object is None and '-' or ''
        if object is not None and hasattr(object, 'listCategoryMetadata'):
            for key, val in object.listCategoryMetadata():
                if key=='postfix':
                    category_postfix = val
                    break

        cmds = {'fnum': (folder_nomencl_num, "The 'nomenclative number' property in the folder not specified."),
                'fpfx': (folder_postfix,     "The 'postfix' property in the folder not specified."),
                'cpfx': (category_postfix,   "The 'postfix' property in the document's category not specified."),
                'rdpt': (self.getDepartment(), "The department not specified."),
               }

        now = DateTime()
        registry_id = ''
        pattern = self.reg_num_forming_rule
        if getattr(self, '_v_table_update', 0):
            pattern = pattern or '\Seq'
        if not pattern:
            raise SimpleError, "Registration number forming rule not specified"
        escaped = 0
        pos = 0
        while pos < len(pattern):
            if escaped:
                if pattern[pos] == '\\':
                    registry_id += '\\'
                else:
                    #dates:
                    command = pattern[pos]
                    if command in ('Y', 'y', 'm', 'd', 'H', 'M'):
                        registry_id += now.strftime( '%' + command )
                        escaped=0
                        pos += 1
                        continue

                    #commands:
                    m = re.match( r'seq(\:\d+#)?(?i)', pattern[pos:] )
                    if m:
                        width = m.group(1) and m.group(1)[1:-1] or '0'
                        registry_id += ("%" +".%s"%width + "d")%( self.getLastSequenceNumber() )

                        pos += m.end() - 1

                    m = re.match( r'sqd(\:\d+#)?(?i)', pattern[pos:] )
                    if m:
                        width = m.group(1) and m.group(1)[1:-1] or '0'

                        registry_id += ("%" +".%s"%width + "d")%( self.daily_counter.getLastValue() )
                        pos += m.end() - 1

                    for command in cmds.keys():
                        if pos + len(command) > len(pattern):
                            continue
                        if pattern[pos:pos+len(command)].lower() == command:
                            if not cmds[command][0]:
                                message = cmds[command][1]
                                raise SimpleError, message
                            registry_id += cmds[command][0]
                            pos += len(command) - 1
                            break
                escaped = 0
            else:
                if pattern[pos] == '\\':
                    escaped = 1
                else:
                    registry_id += pattern[pos]
            pos += 1
        return registry_id


    def _getSourceObject(self, came_from=None, came_version_id=None, REQUEST=None):
        #Searches the object user wants to register.
        #Arguments:
        #
        #   'came_from' -- nd_uid of the object.
        #
        #   'came_version_id' -- If user wants to register version instead of
        #   document, here is version id.
        #
        #   if both 'came_from' and 'came_version_id' are None,
        #       tries to get them form REQUEST.
        came_from = came_from or REQUEST is not None and REQUEST['SESSION'].get('came_from') or None
        came_version_id = came_version_id or REQUEST is not None and REQUEST['SESSION'].get('came_version_id') or None

        source = getObjectByUid(self, came_from)
        if came_version_id:
            source = source.getVersion(came_version_id)

        return source

    security.declareProtected(CMFCorePermissions.View, 'resolveErrors')
    def resolveErrors(self, data=None, REQUEST=None):
        """
            Helper function. Performs user's choice when error occured.
        """
        if data is None and REQUEST is not None:
            # Get entry info from REQUEST and place it into
            # the 'data' vocabulary
            data = self.parseEntryForm(self.listColumnIds(), REQUEST)
        #user's choice
        user_action = REQUEST and REQUEST.get('user_action', '')
        source = self._getSourceObject(REQUEST=REQUEST)

        if not user_action:
            #abandon registration
            self.releaseSelectedDocument(redirect=0, REQUEST=REQUEST)
            ob = source or self
            return REQUEST[ 'RESPONSE' ].redirect( ob.absolute_url() )
        elif user_action == 'both':
            #register in both registries
            pr = getObjectByUid(self, self.getParentRegistry())
            if pr is not None:
                return pr.addEntry( data, REQUEST, test_parent=0, childRegistry=self )
            else:
                #TODO: what to do if parent registry removed?
                raise "No parent registry object can be found."

        elif user_action == 'child':
            #register only in child registry (do not touch parent)
            return self.addEntry( data, REQUEST, test_parent=0 )

    security.declareProtected( CMFCorePermissions.AddPortalContent, 'addEntry' )
    def addEntry( self, data=None, REQUEST=None, test_parent=1, registry_id=None, childRegistry=None ):
        """
            Adds row to the report table

            Arguments:

                'data' -- Column id:value mapping.

                'test_parent' -- Indicates if it shoul be tested that the
                    document is registered in the parent registry.

                'registry_id' -- Value that will be stored in the 'ID' column.
                    If None, it will be generated according registry settings.

                'childRegistry' -- Child registry (Registry) where it is needed
                    to register given data too.
        """
        if data is None and REQUEST is not None:
            # Get entry info from REQUEST and place it into
            # the 'data' vocabulary
            data = self.parseEntryForm(self.listColumnIds(), REQUEST)

        source = self._getSourceObject(REQUEST=REQUEST)
        obj = source or self
        if self.isObjectRegistered(source):
            return obj.redirect( REQUEST=REQUEST, message='Document is already registered' )

        #test_parent: if 1, test if the document is registered in the parent registry
        if test_parent:
            pr = getObjectByUid(self, self.getParentRegistry())
            if pr is not None and not pr.isObjectRegistered( source ):
                message = "Document is not registered in parent registry"
                #store data we have got in REQUEST
                dt = {}
                for key, val in REQUEST.form.items():
                    dt[key] = val
                REQUEST.SESSION.set('data', dt)
                REQUEST[ 'RESPONSE' ].redirect( self.absolute_url(message = message, action='registry_error_resolution' ) )
                return message
            elif pr is not None:
                #registered in parent registry, get reg_id from there
                registry_id = pr.getObjectRegistryId( source )
                #XXX Here is problem: need to choose some way paper document.

        while 1:
            try:
                val1 = self.getLastSequenceNumber()
                val2 = self.daily_counter.getLastValue()

                if registry_id is None:
                    if data.get('ID'):
                        registry_id = data['ID']
                    else:
                        try:
                            registry_id = self._generate_registry_id( source )
                        except SimpleError, s:
                            if REQUEST is not None:
                                obj.redirect( REQUEST=REQUEST, message= str(s) )
                            return s

                # check for duplicate registry_id (only in this registry)
                # the lack of this is that we don't check global duplicatiton of reg_ids.
                # but may be it is not needed - like in case with parent registry
                if not getattr(self, '_v_table_update', 0):
                    for entry in self.listEntries():
                        if registry_id == entry.get('ID'):
                            get_transaction().abort()
                            if REQUEST is not None:
                                obj.redirect( REQUEST=REQUEST, message="Entry with id \"%s\" already exists." % registry_id )
                            return message

                # Apply document ID and increment id counter
                data['ID'] = registry_id
                if 'creation_date' in self.listColumnIds():
                    data['creation_date'] = DateTime()
                self._store(data, factory=RegistryEntry)

                if self.getLastSequenceNumber() != val1 or self.daily_counter.getLastValue() != val2:
                    raise ConflictError

                self.safe_sequence.getNextValue()
                self.daily_counter.getNextValue()
                get_transaction().commit()
                break

            except ConflictError:
                get_transaction().abort()
                time.sleep( random() * 1.0 )

        if REQUEST is not None:
            # Keep link to the source document
            if source is not None:

                if not hasattr(source, 'registry_data'):
                    source.registry_data = {}

                if source.registry_data.has_key( registry_id ):
                    if self.getUid() not in source.registry_data[ registry_id ]:
                        source.registry_data[ registry_id ].append( self.getUid() )
                else:
                    source.registry_data[ registry_id ] = [ self.getUid() ]

                source._p_changed = 1
                source.manage_permission(ZopePermissions.delete_objects, [Roles.Manager], 0)
                source.reindexObject(idxs=['registry_ids'])
                if childRegistry is None:
                    self.releaseSelectedDocument(redirect=0, REQUEST=REQUEST)

            obj.redirect( REQUEST=REQUEST, message='Document was registered' )

        if childRegistry is not None:
            childRegistry.addEntry( data=data, REQUEST=REQUEST, test_parent=0, registry_id=registry_id, childRegistry=None )


    security.declareProtected(CMFCorePermissions.View, 'isObjectRegistered')
    def isObjectRegistered(self, object):
        """
            Returns true if the object has already been registered in this registry.
        """
        return not not self.getObjectRegistryId( object )

    security.declareProtected(CMFCorePermissions.View, 'getObjectRegistryId')
    def getObjectRegistryId(self, object):
        """
            Returns registry id if the object has already been registered in this registry.
        """
        s_reg_data = getattr(object, 'registry_data', {})
        #two opportunities are possible to check:
        #check all s_reg_data keys in entries:
        #reg_ids = s_reg_data.keys()
        #for entry in self.objectValues():
        #    if entry.get('ID') in reg_ids:
        #        return entry.get('ID')

        #or check self.uid in s_reg_data. - less expensive approach.
        suid = self.getUid()
        for reg_id in s_reg_data.keys():
            if suid in s_reg_data[reg_id]:
                return reg_id

    security.declareProtected( CMFCorePermissions.AddPortalContent, 'editEntry' )
    def editEntry( self, record_id, data=None, comment='', REQUEST=None, redirect=1 ):
        """
           Edit row in the report table
        """

        entry = self.getEntryById(record_id)
        entry.validate()

        if REQUEST is not None:
            # Get entry info from REQUEST and place it into
            # the 'data' dictionary
            data = self.parseEntryForm(self.listColumnIds(), REQUEST)

        if _checkPermission(CMFCorePermissions.ModifyPortalContent, self) and \
            REQUEST.has_key('ID') and not data.has_key('ID'):
            data['ID'] = REQUEST.get( 'ID' )

        #do not allow to create entries with equal ID
        ids = [v.get('ID') for v in self.listEntries() if v.getId()!=record_id]
        if data.get('ID') in ids:
            if REQUEST is not None:
                self.redirect( message = "Entry with given id already exists.")
            return

        self._edit(data, record_id)

        if _checkPermission(CMFCorePermissions.ModifyPortalContent, self):
            user = _getAuthenticatedUser(self).getUserName()
            entry_creator = REQUEST.get('entry_creator', entry._data.get('Creator', user))
            entry._data['Creator'] = entry_creator

        entry.updateHistory(text=comment)
        entry.reindexObject()

        if redirect and REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry updated')

    def _edit( self, entry_data, index ):
        """
        """
        entry = self.getEntryById(index)
        catalog = getToolByName(self, 'portal_catalog')

        for key in entry_data.keys():
            if entry.isEditAllowed( key ):
                if key=='ID' and entry.get('ID')!=entry_data['ID']:
                    #find all documents with old regisrty_id
                    reg_id = entry.get('ID')
                    res = catalog.unrestrictedSearch( registry_ids = reg_id, implements='isDocument' )
                    for obj_brain in res:
                        obj = obj_brain.getObject()
                        if self.getUid() in obj.registry_data[ reg_id ]:
                            #update only documents registered in this registry
                            #first say that we do not register the document
                            obj.registry_data[ reg_id ].remove( self.getUid() )
                            if obj.registry_data[ reg_id ]==[]:
                                del obj.registry_data[ reg_id ]

                            #and then register it with new register_id
                            #obj.registry_data
                            registry_id = entry_data['ID']
                            if registry_id in obj.registry_data.keys():
                                if not self.getUid() in obj.registry_data[ registry_id ]:
                                    obj.registry_data[ registry_id ].append( self.getUid() )
                            else:
                                obj.registry_data[ registry_id ] = [ self.getUid() ]

                            obj._p_changed = 1
                            obj.reindexObject(idxs=['registry_ids',])
                entry.set(key, entry_data[key])

        self.catalog_object(entry, index)

    def delColumn( self, id ):
        """
          Removes entry key
        """
        GuardedTable.delColumn(self, id)

        #allow sort
        si = 0
        for column in self.listColumns():
            column._updateProperty( 'sort_index', si )
            si += 1

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setDelEntryAuthorAllowed')
    def setDelEntryAuthorAllowed(self, is_allowed=None):
        """
            Sets self._author_can_delete_entry.
        """
        self._updateProperty( '_author_can_delete_entry', is_allowed)

    security.declareProtected(CMFCorePermissions.View, 'isDelEntryAuthorAllowed')
    def isDelEntryAuthorAllowed( self ):
        """
            Returns true if entry author allowed to delete entry.
        """
        return self.getProperty('_author_can_delete_entry')

    security.declareProtected(CMFCorePermissions.View, 'isEntryDeleteAllowed')
    def isEntryDeleteAllowed(self, entry_id=None):
        """
          Defines whether the current user is allowed to remove an entry record with entry_id.
        """
        is_entry = isinstance(entry_id, GuardedEntry)

        try:
            entry = is_entry and entry_id or self.getEntryById( entry_id )
        except IndexError:
            return 0

        has_perm = _checkPermission(CMFCorePermissions.ModifyPortalContent, entry.parent() )
        is_owner = entry._data.get('Creator', None) == _getAuthenticatedUser(self).getUserName()

        if has_perm or (is_owner and self.isDelEntryAuthorAllowed() ):
            return 1

        return 0

    def delEntries( self, selected_entries=[], REQUEST=None ):
        """
            Removes rows from the report table
        """
        catalog = getToolByName(self, 'portal_catalog')

        for key in selected_entries:
            try:
                entry = self.getEntryById(key)
                if not self.isEntryDeleteAllowed( key ):
                    continue
                reg_id = entry.get('ID')
                res = catalog.unrestrictedSearch( registry_ids = reg_id, implements='isDocument' )
                for obj_brain in res:
                    obj = obj_brain.getObject()
                    if self.getUid() in obj.registry_data[ reg_id ]:
                        obj.registry_data[ reg_id ].remove( self.getUid() )
                        if obj.registry_data[ reg_id ]==[]:
                            del obj.registry_data[ reg_id ]

                        if not obj.registry_data:
                            obj.manage_permission(ZopePermissions.delete_objects, \
                                [Roles.Manager, Roles.Owner, Roles.Editor], 1)
                        obj._p_changed = 1
                        obj.reindexObject(idxs=['registry_ids',])
                self._remove(key)
            except (KeyError, IndexError):
                pass

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry deleted')

    def getListById( self, id ):
        """
            Returns elements of 'list' field

            Arguments:

                'id' -- id of requisite field

            Result:

                List. Value of _kw_list[id]
        """
        return self.getColumnById(id).getProperty('options')

InitializeClass(Registry)


def initialize( context ):
    # module initialization callback

    context.registerContent( Registry, addRegistry, RegistryType )
