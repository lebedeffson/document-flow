"""
RegistrationBook class.
$Id: RegistrationBook.py,v 1.92 2007/07/04 08:06:51 oevsegneev Exp $
$Editor: ishabalin $
"""

__version__ = '$Revision: 1.92 $'[11:-2]

import re
from types import StringType, ListType, TupleType

from AccessControl import ClassSecurityInfo, getSecurityManager, Permissions as ZopePermissions

from Products.CMFCore import CMFCorePermissions
from Products.ZCatalog.Lazy import Lazy


import Features, Exceptions
from CatalogSupport import ZCatalogIter, QueryContext
from Exceptions import SimpleError
from DateTime import DateTime
from Utils import cookId, InitializeClass, getToolByName, parseDate, _checkPermission
from ResourceUid import ResourceUid
from SimpleObjects import InstanceBase
from ReferenceTable import ReferenceTable
from Monikers import ContentMoniker

from PatternProcessor import PatternProcessor

RegistrationBookType = \
            { 'id'              : 'RegistrationBook'
            , 'meta_type'       : 'RegistrationBook'
            , 'title'           : "Registration book"
            , 'description'     : "Registration book"
            , 'icon'            : 'registry_icon.gif'
            , 'product'         : 'CMFNauTools'
            , 'factory'         : 'addRegistrationBook'
            , 'factory_form'    : 'registration_book_factory_form'
            , 'immediate_view'  : 'registration_book_edit_form'
            , 'permissions'     : ( CMFCorePermissions.ModifyPortalContent, )
            , 'actions'         :
              (
                { 'id'          : 'view'
                , 'name'        : "View"
                , 'action'      : 'registration_book_view_form'
                , 'permissions' : ( CMFCorePermissions.View, )
                },
                { 'id'          : 'edit'
                , 'name'        : "Settings"
                , 'action'      : 'registration_book_edit_form'
                , 'permissions' : ( ZopePermissions.change_configuration, )
                },
                { 'id'          : 'migrate'
                , 'name'        : "Migration"
                , 'action'      : 'registration_book_migration_form'
                , 'permissions' : ( CMFCorePermissions.ManagePortal, )
                },
                { 'id'          : 'register_paper'
                , 'name'        : "Register paper document"
                , 'action'      : 'paper_document_registration'
                , 'condition'   : 'python: object.canAdd()'
                , 'permissions' : ( CMFCorePermissions.View, )
                },
              )
            }


def addRegistrationBook( self, id, REQUEST=None, **kwargs ):
    """
        Adds RegistrationBook
    """
    obj = RegistrationBook( id, **kwargs )
    self._setObject( id, obj )


class TotalSequence( InstanceBase ):
    """
        TotalSequence implementation.
    """
    _class_version = 1.0

    meta_type = 'Total Sequence'

    security = ClassSecurityInfo()

    _properties = InstanceBase._properties + (
            { 'id':'seq_id',     'type':'string', 'mode':'w' },
            { 'id':'last_value', 'type':'int',    'mode':'w' },
        )

    def __init__( self, seq_id, start_value=0 ):
        """
            Constructor.
        """
        InstanceBase.__init__( self, seq_id, self.meta_type )
        self.seq_id = seq_id
        self.last_value = start_value

    def getNextValue( self ):
        """
            Increments the sequence counter and returns its new value.
        """
        self.last_value += 1
        return self.last_value

    def getLastValue( self ):
        """
            Returns the last sequence value,
            but does not modify it as getNextValue() does.
        """
        return self.last_value

    def setValue( self, new_value ):
        """
            Sets internal sequence value to new_value.
        """
        self.last_value = new_value

InitializeClass( TotalSequence )


class DailySequence( TotalSequence ):
    """
        DailySequence implementation.
    """
    _class_version = 1.0

    meta_type = 'Daily Sequence'

    security = ClassSecurityInfo()

    def __init__( self, seq_id, start_value=0 ):
        """
            Constructor.
        """
        TotalSequence.__init__( self, seq_id, start_value )
        self.today = DateTime()

    def _resetSequence( self ):
        """
            Resets the sequence.
        """
        self.setValue( 1 )

    def getNextValue( self ):
        """
            Overrides TotalSequence.getNextValue.
            Resets the sequence every next day.
        """
        if not self.today.isCurrentDay():
            self.today = DateTime()
            self._resetSequence()
        return TotalSequence.getNextValue( self )

    def getLastValue( self ):
        """
            Overrides TotalSequence.getLastValue.
            Resets the sequence every next day.
        """
        if not self.today.isCurrentDay():
            self.today = DateTime()
            self._resetSequence()
        return TotalSequence.getLastValue( self )

InitializeClass( DailySequence )

class TargetsWrapper:
    def __init__(self, targets, entries ):
        self.targets = targets
        self.entires = entries
  
    def __getitem__(self, i):
        item = self.targets[i]
        if not self.entires[ item['nd_uid'] ].has_key('target'):
             self.entires[ item['nd_uid'] ]['target'] = item
        return item

class Optimizer(Lazy):

    def __init__( self, links, targets, entries, **kw ):
        # N.B. all links are bind by LazyMap to this time, so convert to list is not expensive
        self.links = list(links)
        self.targets = TargetsWrapper( targets, entries )
 
        self.entries = entries

        #self.total_count = #getTotalCount()
        links_len = len( links )
        self.results_count = min( len(targets) , links_len )

        self.reorder_links = self.results_count < links_len
        self.iter_on = kw.get('sort_on') and 'target' or 'link'

    def __len__( self ):
        return self.results_count

    # TODO write __iter__
    def __getitem__(self, i):
        #print 'requested target ==>', i
        if i>= len(self):
            raise IndexError(i)
        iter_on = self.iter_on
        entries = self.entries

        item = getattr(self, iter_on + 's')[i]
        if iter_on == 'target':
            res = entries[ item['nd_uid'] ]
        else: # link
            uid = str( item['target_uid'] )
            res = entries[uid]
            if not self.findTarget(uid):
                if self.reorder_links:
                    # reorder links for recursive call
                    del self.links[i]
                    # recursive call
                    return self[i]
                else:
                    raise ValueError(uid)
        return res
                
    def findTarget(self, uid):
        if self.entries[uid].has_key('target'):
            return True
        for target in self.targets:
            target_uid = target['nd_uid']

            if target_uid == uid:
                 result = True
                 break
        else:
            result = False
        return result
               

class RegistrationBook( ReferenceTable ):
    """
        RegistrationBook class
    """
    _class_version = 1.6

    meta_type = 'RegistrationBook'
    portal_type = 'RegistrationBook'

    __implements__ = (  ReferenceTable.__implements__,
                        Features.createFeature( 'isRegistrationBook' ),
                        Features.hasTabs,
                        Features.hasHeadingInfo
                        )
    category_id = None
    reg_no_attr_id = None
    reg_no_forming_rule = '\Seq'
    department = ''
    papers_folder_uid = None
    safe_sequence = None
    daily_sequence = None

    security = ClassSecurityInfo()

    _meta_columns = ('Description', 'Owner', 'State', 'Followup', 'Attachments')

    def __init__( self, id, **kwargs ):
        """
            Initialize Class Instance
        """
        ReferenceTable.__init__( self, id, **kwargs )

    def _initstate(self, mode):
        """
            Initialize attributes
        """
        if not ReferenceTable._initstate( self, mode ):
            return False
        if hasattr(self, 'mutex'):
            # class version < 1.5
            del self.mutex
        if not hasattr(self, 'hide_registration_date'):
            # class version < 1.4
            self.hide_registration_date = False
        if not hasattr(self, 'hide_creator'):
            # class version < 1.4
            self.hide_creator = False
        if not hasattr(self, 'hide_version'):
            # class version < 1.4
            self.hide_version = False
        if not hasattr( self, 'recency_period' ):
            # class version < 1.6
            self.recency_period = 0
        return True

    def _instance_onCreate( self ):
        # create callback
        self.safe_sequence = TotalSequence( 'total_%s' % ( self.getUid() ), 1 )
        self.daily_sequence = DailySequence( 'daily_%s' % ( self.getUid() ), 1 )

    def _instance_onClone( self, source, item ):
        # copy callback
        if hasattr( self, 'safe_sequence' ):
            try:
                del self.safe_sequence
            except:
                pass
        self.safe_sequence = TotalSequence( 'total_%s' % ( self.getUid() ), 1)

        if hasattr( self, 'daily_sequence' ):
            try:
                del self.daily_sequence
            except:
                pass
        self.daily_sequence = DailySequence( 'daily_%s' % ( self.getUid() ), 1 )

    security.declareProtected( CMFCorePermissions.View, 'isDocumentAllowedToRegister' )
    def isDocumentAllowedToRegister( self, doc ):
        """
            Checks whether given document's category matches or is inherited
            from category for registered documents.

            Arguments:

                'doc'       --  document object instance.

            Results:

                Returns 1 (true) or 0 (false).
        """
        if not doc:
            return False
        return doc.getCategory().hasBase( self.getRegisteredCategory() )

    security.declareProtected( ZopePermissions.change_configuration, 'setRegisteredCategory' )
    def setRegisteredCategory( self, category_id ):
        """
            Sets the category of registered documents.

            Arguments:

                'category_id'   --  category id.
        """
        links_tool = getToolByName(self, 'portal_links')
        metadata_tool = getToolByName(self, 'portal_metadata')

        old_category_id = self.category_id
        self.category_id = category_id

        if old_category_id != category_id:

            # removing invalid columns
            category = metadata_tool.getCategoryById(category_id)
            attrs = category.listAttributeDefinitions()
            attr_ids = [x.getId() for x in attrs]
            if self.reg_no_attr_id not in attr_ids:
                self.reg_no_attr_id = None

            # unregistering invalid documents
            res = links_tool.searchLinks( source=self, relation='reference' )
            for item in res:
                link = item.getObject()
                dst_obj = link.getTargetObject()
                if not self.isDocumentAllowedToRegister(dst_obj):
                    self.unregister( link.getTargetObject() )

    security.declareProtected( CMFCorePermissions.View, 'getRegisteredCategory' )
    def getRegisteredCategory( self ):
        """
            Returns id of the category of registered documents.

            Result:

                Category id.
        """
        return self.category_id

    security.declareProtected( ZopePermissions.change_configuration, 'setRegistrationNumberAttributeId' )
    def setRegistrationNumberAttributeId( self, attr_id ):
        """
            Stores id of the attribute which registration number is written to.

            Arguments:

                'attr_id'   --  attribute id.
        """
        self.reg_no_attr_id = attr_id

    security.declareProtected( CMFCorePermissions.View, 'getRegistrationNumberAttributeId' )
    def getRegistrationNumberAttributeId( self ):
        """
            Returns id of the attribute which registration number is written to.

            Result:

                Attribute id.
        """
        return self.reg_no_attr_id

    security.declareProtected( ZopePermissions.change_configuration, 'setDepartment' )
    def setDepartment( self, dept='' ):
        """
            Sets the 'department' attribute.

            Arguments:

                'dept'      --  String.
        """
        self.department = dept

    security.declareProtected( CMFCorePermissions.View, 'getDepartment' )
    def getDepartment( self ):
        """
            Returns the 'department' attribute value.

            Result:

                String.
        """
        return self.department

    security.declareProtected( ZopePermissions.change_configuration, 'setRegistrationNumberTemplate' )
    def setRegistrationNumberTemplate( self, rule='' ):
        """
            Sets the 'reg_no_forming_rule' attribute which is a pattern
            for registration number generation.

            Arguments:

                'rule'      --  String.
        """
        self.reg_no_forming_rule = rule

    security.declareProtected( CMFCorePermissions.View, 'getRegistrationNumberTemplate' )
    def getRegistrationNumberTemplate( self ):
        """
            Returns the 'reg_no_forming_rule' attribute value.

            Result:

                String.
        """
        return self.reg_no_forming_rule

    security.declareProtected( CMFCorePermissions.View, 'getLastSequenceNumber' )
    def getLastSequenceNumber( self ):
        """
            Returns last sequence number.
        """
        return self.safe_sequence.getLastValue()

    security.declareProtected( ZopePermissions.change_configuration, 'setInternalCounter' )
    def setInternalCounter( self, new_counter=0 ):
        """
            Sets internal counter for registry ids value.
        """
        self.safe_sequence.setValue( new_counter )

    security.declarePublic( 'register' )
    def register(   self, doc,
                    creation_date=None,     # these arguments are supported
                    creator=None            # within the migration period only,
                    ):                      # and then should be removed
        """
            Registers document.
            Creates link (via portal_links) from self to the document.

            Arguments:

                'doc'           --  either document object or
                                    document uid string.

            Results:

                Returns 1 (true) if registration was successful
                or 0 (false) if failed.
        """
        links_tool = getToolByName( self, 'portal_links' )

        if type(doc) is StringType:
            doc = ResourceUid( doc ).deref( self )

        if doc.implements( 'isVersionable' ):
            doc = doc.getVersion()

        if not self.isDocumentAllowedToRegister(doc):
            return False

        try:
            link = links_tool.restrictedLink( self, doc, 'reference' )
        except SimpleError:
            return False

        #-----------------------------------------------------------------------
        # supported within the migration period only
        # the purpose is to copy registration date and user correctly
        # otherwise current date and user are set

        if creation_date or creator:
            mstool = getToolByName( self, 'portal_membership' )
            link = links_tool._getOb( link )
            if creation_date:
                link.creation_date = creation_date
            if creator:
                member = mstool.getMemberById( creator )
                user = member and member.getUser() or None
                if user:
                    link.changeOwnership( user )
            links_tool.reindexObject( link, idxs=['Creator','created'] )
        #-----------------------------------------------------------------------

        attr_id = self.getRegistrationNumberAttributeId()
        if attr_id:
            reg_no = PatternProcessor.processString(self.reg_no_forming_rule, fmt='reg_book_date', doc=doc, obj=self)
            doc._setCategoryAttribute( attr_id, value=reg_no, reindex=True )

        self.safe_sequence.getNextValue()
        self.daily_sequence.getNextValue()

        return True

    security.declareProtected( CMFCorePermissions.ManagePortal, 'unregister' )
    def unregister( self, docs=[], REQUEST=None ):
        """
            Unregisters document.
            Removes link from self to the document.

            Arguments:

                'docs'  --  either document object or document uid string.

            Results:

                Returns True if link was successfuly removed
                or False if there was not such link.
        """

        if type( docs ) is ListType or type( docs ) is TupleType:
            result = docs and True or False
            for item in docs:
                result = self.unregister( item ) and result
        else:
            result = False
            if type( docs ) is StringType:
                docs = ResourceUid( docs ).deref( self )

            if docs:
                if docs.implements( 'isVersionable' ):
                    docs = docs.getVersion( docs.getCurrentVersionId() )

                links_tool = getToolByName( self, 'portal_links' )
                res = links_tool.searchLinks(   source=self,
                                                target=docs,
                                                relation='reference' )
                if res:
                    links_tool.removeLinks( [x.id for x in res], restricted=Trust )
                    result = True

        message = result and 'Documents were successfully unregistered' or ''
        if REQUEST is not None:
            return self.redirect( action='view', message=message )

        return result

    security.declareProtected( CMFCorePermissions.View, 'searchEntries' )
    def searchEntries( self, REQUEST=None, **kw ):
        """

        """
        catalog_tool = getToolByName( self, 'portal_catalog' )
        links_tool = getToolByName( self, 'portal_links' )

        # Divide arguments between portal_links and portal_catalog
        links_kw = {}
        link_indexes = ['created', 'Creator']
        usage_keys = ['%s_usage' % x for x in link_indexes]

        for key in link_indexes + usage_keys:
            if kw.has_key( key ):
                links_kw[key] = kw[key]
                del kw[key]
            if REQUEST and REQUEST.has_key( key ):
                links_kw[key] = REQUEST[key]
                REQUEST[key] = None

        if kw.has_key( 'sort_on' ) and kw[ 'sort_on' ] in link_indexes:
            links_kw[ 'sort_on' ] = kw[ 'sort_on' ]
            del kw[ 'sort_on' ]

            if kw.has_key( 'sort_order' ):
                links_kw['sort_order'] = kw['sort_order']
                del kw['sort_order']

            #if kw.has_key( 'sort_limit' ) and kw['sort_limit'] in link_indexes:
            #    links_kw['sort_limit'] = kw['sort_limit']
            #    del kw['sort_limit']

        if REQUEST and REQUEST.has_key( 'sort_on' ):
            if REQUEST[ 'sort_on' ] in link_indexes:
                links_kw[ 'sort_on' ] = REQUEST[ 'sort_on' ]
            else:
                kw[ 'sort_on' ] = REQUEST[ 'sort_on' ]
            REQUEST[ 'sort_on' ] = None
            if REQUEST.has_key( 'sort_attr' ):
                kw[ 'sort_attr' ] = REQUEST[ 'sort_attr' ]
                REQUEST[ 'sort_attr' ] = None

        # sort entries on registration date by default
        if not ( kw.get( 'sort_on' ) or links_kw.get( 'sort_on' ) ):
            links_kw['sort_on'] = 'created'
            links_kw['sort_order'] = 'reverse'

        recency_period = self.getRecencyPeriod()
        if recency_period and 'created' not in links_kw.keys():
            if not kw.get( 'disable_recency_filter', 0 ):
                links_kw['created'] = { 'query': DateTime() - recency_period,
                                        'range': 'min' }

        links = links_tool.searchLinks( source=self,
                                        relation='reference',
                                        target_removed=False,
                                        **links_kw )

        #if uncomment think about call Optimizer with empty args here
        #if not links:
        #    return []
        entries = {}
        def get_uid_hook(link, entries=entries):
            uid = str(link['target_uid'])
            entries[uid] = {'link':link}
            return uid
        it = ZCatalogIter(links, get_uid_hook)

        targets = catalog_tool.unrestrictedSearch( nd_uid=QueryContext(it),
                                                   REQUEST=REQUEST,
                                                   **kw
                                                 )

        return Optimizer( links
                        , targets
                        , entries
                        , **kw
                        )

    security.declareProtected( CMFCorePermissions.View, 'executeQuery' )
    def executeQuery(self, REQUEST, md=None ):
        """
            TODO:
            md is needed only for copy code from dtml
            then this method checked on bugs remove it
        """
        catalog_tool = getToolByName(self, 'portal_catalog')
        SESSION = REQUEST['SESSION']
        r = REQUEST.get
        s = SESSION.get
        uid = self.getUid()

        sort_on =    r( 'sort_on',    s( '%s_sort_params' % uid, {} ).get( 'sort_on' ) )
        sort_attr =  r( 'sort_attr',  s( '%s_sort_params' % uid, {} ).get( 'sort_attr' ) )
        sort_order = r( 'sort_order', s( '%s_sort_order' % uid ) )
        sort_params = { 'sort_on': sort_on, 'sort_attr': sort_attr }

        table_columns = self.getFilterColumns()
        default_filter = { 'query'     : {},
                           'columns'   : table_columns
                         }

        filter_id = uid
        profile_id = r('profile_id', None)

        profile_filter = None
        if profile_id and s('load_filter', None):
            # remove flag
            SESSION.delete('load_filter')

            profile = catalog_tool.getObjectByUid(profile_id, feature = 'containsQuery')

            if profile:
                # load profile filter from filter object
                profile_query = profile.getQuery().copy()
                profile_filter = { 'query': profile_query.filter_query
                                 , 'columns': table_columns
                                 , 'profile_id': profile_id
                                 , 'profile_title': profile.Title() }

        filter = profile_filter or s( '%s_filter' % filter_id, default_filter )

        # If 'recency period' is set to non-zero value give an abilty to
        # temporarily disable recency filter.
        disable_recency_filter = False
        if self.getRecencyPeriod():
            if REQUEST.has_key( 'disable_recency_filter' ):
                disable_recency_filter = not not r( 'disable_recency_filter' )
            else:
                disable_recency_filter = not not s( '%s_disable_recency_filter' % uid, 0 )

        results = self.searchEntries( REQUEST=REQUEST
                                    , sort_on=sort_on
                                    , sort_attr=sort_attr
                                    , sort_order=sort_order
                                    , disable_recency_filter=disable_recency_filter
                                    , **filter['query'] )

        # 'table_pages_list' related stuff
        batch_size = int( r( 'batch_size', s( '%s_batch_size' % uid, 10 ) ) )
        qs_new     = int( r( 'qs', s( '%s_qs' % uid, 1 ) ) )
        qs_0       = qs_new / batch_size * batch_size + 1

        results_count = len( results )

        # Counting links instead of extra call to searchEntries is
        # less resource expensive.
        total_count = len( self.portal_links.searchLinks( source=self
                                                        , relation='reference'
                                                        , target_removed=False )
                          )
        total_pages = ( results_count / batch_size ) + ( results_count % batch_size and 1 ) or 1
        current_page = ( qs_0 / batch_size ) + ( qs_0 % batch_size and 1 )
        qs = current_page > total_pages and ( ( total_pages - 1 ) * batch_size + 1 ) or qs_0

        def session_set( k, v ):
            if SESSION.get( k ) != v: SESSION.set( k, v )

        session_set( '%s_qs' % uid, qs )
        session_set( '%s_batch_size' % uid, batch_size )
        session_set( '%s_sort_params' % uid, sort_params )
        session_set( '%s_sort_order' % uid, sort_order )
        session_set( '%s_disable_recency_filter' % uid, disable_recency_filter )

        return { 'results'               : results
               , 'results_count'         : results_count
               , 'total_count'           : total_count

               , 'qs'                    : qs
               , 'batch_size'            : batch_size

               , 'sort_on'               : sort_on
               , 'sort_order'            : sort_order
               , 'sort_attr'             : sort_attr
               , 'sort_params'           : sort_params

               , 'disable_recency_filter': disable_recency_filter

               , 'filter_id'             : filter_id
               , 'filter'                : filter
               }

    security.declareProtected( CMFCorePermissions.View, 'getFilterColumns' )
    def getFilterColumns( self ):
        """
            Returns a list of columns for catalog_filter_form.
        """
        cols = [    {   'id': 'Title',
                        'title': 'Document',
                        'type': 'string',
                        },
                    {   'id': 'Creator',
                        'title': 'User',
                        'type': 'userlist',
                        'multiple': 1,
                        },
                    {   'id': 'created',
                        'title': 'Registration date',
                        'type': 'date',
                        'show_time': 1,
                        },
                    ]

        metadata = getToolByName( self, 'portal_metadata' )
        workflow = getToolByName( self, 'portal_workflow' )
        category = metadata.getCategoryById( self.getRegisteredCategory() )
        if category:
            wf = category.getWorkflow()
            states = wf.states.objectIds()
            cols.append(    {   'id':       'state',
                                'title':    'State',
                                'type':     'list',
                                'multiple': 1,
                                'options':  [   ( x, workflow.getStateTitle( wf.getId(), x ) )
                                                for x in states
                                                ],
                                } )
            attributes = category.listAttributeDefinitions()
            for attr in attributes:
                if attr.Type() != 'link':
                    cols.append(    {   'id':       '%s/%s' % ( category.getId(), attr.getId() ),
                                        'title':    attr.Title(),
                                        'type':     attr.Type(),
                                        'multiple': attr.isMultiple(),
                                        'options':  attr.getProperty( 'options', [] ),
                                        'attributes_index' : 1,
                                        'show_time':attr.getProperty( 'show_time', None )
                                        } )
        return cols

    security.declareProtected( CMFCorePermissions.ManagePortal, 'migrate' )
    def migrate( self, registry, col2attr, skip_mismatches=1 ):
        """
            Migrates data from old version registry (class Registry).
            Re-registers documents which are registered in an old version
            registry then copies corresponding registry fields to selected
            (via 'col2attr') document attributes.

            Arguments:

                'registry'          --  old version registry;
                                        could be either object instance or uid.

                'col2attr'          --  a dictionary specifying migration scheme;
                                        the key is the registry field id and
                                        the value is the document category
                                        attribute id.

                'skip_mismatches'    --  a flag;
                                        if true, documents whose category
                                        doesn't match registration book settings
                                        are skipped;
                                        if false, those documents' categories
                                        are changed according to registration
                                        book settings.

            Result:

                Integer. The count of re-registered documents.
        """
        catalog_tool = getToolByName(self, 'portal_catalog')
        rb_category = self.getRegisteredCategory()
        cnt = 0

        if type(registry) is StringType:
            registry = catalog_tool.getObjectByUid(registry)
        if not registry:
            return 0
        entries = [x.getObject() for x in registry.searchEntries()]
        for entry in entries:
            reg_id = entry.get('ID', '')
            doc_br = catalog_tool.searchResults(    registry_ids=reg_id,
                                                    implements='isDocument')
            doc = doc_br and doc_br[0].getObject()

            ver_id = None
            if doc.implements('isVersion'):
                doc_obj = doc.getVersionable()
            elif doc.implements('isVersionable'):
                doc_obj = doc
                doc = doc.getVersion(doc.getCurrentVersionId())
            else:
                continue

            if not self.isDocumentAllowedToRegister(doc):
                if skip_mismatches:
                    continue
                doc_obj.setCategory(rb_category)

            creation_date = entry.get('creation_date', None)
            creator = entry.get('Creator', None)
            result = self.register( doc,
                                    creation_date=creation_date,
                                    creator=creator,
                                    )
            if not result:
                continue

            for col in registry.listColumns():
                fid = col.getId()
                fval = entry.get(fid, None)
                if col2attr.has_key(fid) and fval:
                    try:
                        doc.setCategoryAttribute(col2attr[fid], fval)
                    except:
                        pass
            doc_obj.reindexObject()
            cnt = cnt + 1

        return cnt

    security.declareProtected( ZopePermissions.change_configuration, 'setPapersFolder' )
    def setPapersFolder( self, folder_uid ):
        """
            Sets folder to store 'paper' documents.

            Arguments:

                'folder_uid'    --  destination folder uid.
        """
        self.papers_folder_uid = folder_uid

    security.declareProtected( CMFCorePermissions.View, 'getPapersFolder' )
    def getPapersFolder( self ):
        """
            Returns (uid, title) pair of the folder storing 'paper' documents.

            Result:

                Tuple (uid, title) or None.
        """
        catalog_tool = getToolByName( self, 'portal_catalog' )
        folder_br = self.papers_folder_uid and \
                    catalog_tool.searchResults( nd_uid=self.papers_folder_uid,
                                                meta_type='Heading'
                                                )
        folder_br = folder_br and folder_br[0] or None
        return folder_br and ( folder_br.nd_uid, folder_br.Title )

    security.declareProtected( CMFCorePermissions.View, 'getPapersFolder' )
    def registerPaperDocument( self, REQUEST=None ):
        """
            Creates and registers documents according to data passed from
            'paper_document_registration' form via REQUEST.

            Arguments:

                'REQUEST'   --  REQUEST object.
        """
        if not REQUEST:
            return

        r = REQUEST.get

        metadata_tool = getToolByName(self, 'portal_metadata')
        catalog_tool = getToolByName(self, 'portal_catalog')

        try:
            folder = catalog_tool.getObjectByUid( self.papers_folder_uid )
            if not folder:
                raise SimpleError, 'Please specify the folder to store paper documents'

            id      = r('id')
            title   = r('title')
            cat_id  = self.getRegisteredCategory()

            if not id:
                id = cookId( folder, id=id, title=title )

            type_args = { 'category': cat_id
                        , 'title' : title
                        , 'description': r('description')
                        }

            category = metadata_tool.getCategoryById( cat_id )
            attrs = self.process_attributes( category=category, pattern='attr/%s', REQUEST=REQUEST )
            if attrs:
                type_args['category_attributes'] = attrs

            primary_category = category.getPrimaryCategory()
            if primary_category:
                doc_uid     = REQUEST.get( 'doc_uid', None )
                if not doc_uid:
                    raise SimpleError, 'Select primary document'
                type_args['category_primary'] = (doc_uid,)

            folder.invokeFactory( 'HTMLDocument', id, **type_args )
            object = folder._getOb( id )

        except SimpleError, error:
            error.abort()
            return self.paper_document_registration( self, REQUEST
                                                   , use_default_values=1
                                                   , portal_status_message=str(error)
                                                   )

        params = {'object': ContentMoniker(object)}
        if self.register(object):
            reg_id = self.getRegistrationNumberAttributeId()
            if reg_id:
                params['reg_num'] = object._getCategoryAttribute(reg_id)
                message = 'Document %(object)s was registered with number %(reg_num)s.'
            else:
                message = 'Document %(object)s was registered.'
        else:
            message = 'Failed to register document %(object)s.'

        return self.redirect(action = 'paper_document_registration',
                             message = message,
                             params = params)

    def canAdd(self):
        """
            Checks whether current user has AddPortalContent permission
            on papers folder.
        """
        metadata_tool = getToolByName(self, 'portal_metadata')
        category = metadata_tool.getCategoryById( self.getRegisteredCategory() )
        if not (category and 'HTMLDocument' in category.listAllowedTypes() ):
            return False

        catalog_tool = getToolByName(self, 'portal_catalog')
        folder = catalog_tool.getObjectByUid(self.papers_folder_uid)
        return folder and _checkPermission(CMFCorePermissions.AddPortalContent, folder) or False

    security.declareProtected( ZopePermissions.change_configuration, 'setHideRegistrationDate' )
    def setHideRegistrationDate(self, value):
        """
        """
        self.hide_registration_date = bool(value)

    security.declareProtected( ZopePermissions.change_configuration, 'setHideCreator' )
    def setHideCreator(self, value):
        """
        """
        self.hide_creator = bool(value)

    security.declareProtected( ZopePermissions.change_configuration, 'setHideVersion' )
    def setHideVersion(self, value):
        """
        """
        self.hide_version = bool(value)

    def listTabs(self):
        """
        """
        REQUEST = self.REQUEST
        msg = getToolByName( self, 'msg' )
 
        tabs = []
        append_tab = tabs.append

        type = self.getTypeInfo()
        link = REQUEST.get('link', '')

        action = type.getActionById( 'view' )
        append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                    , 'title' : msg('View')
                    } )

        if link.find('view') >=0 or link.find(action) >=0:
            tabs[-1]['selected'] = True
            tabs[-1]['selected_color'] = '#ffffff'

        if _checkPermission( 'Change configuration', self ):
            action = type.getActionById( 'edit' )
            append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                        , 'title' : msg('Settings')
                        } )
            if link.find(action) >=0:
                tabs[-1]['selected'] = True
                tabs[-1]['selected_color'] = '#ffffff'

        if self.canAdd():
            action = type.getActionById( 'register_paper' )
            append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                        , 'title' : msg('Register')
                        } )
            if link.find(action) >=0:
                tabs[-1]['selected'] = True
                tabs[-1]['selected_color'] = '#ffffff'
 
        return tabs

    security.declareProtected( ZopePermissions.change_configuration, 'setRecencyPeriod' )
    def setRecencyPeriod( self, value ):
        """
            Sets recency period value (in days).
            When recency period is set to non-zero, records older than recency
            period are not displayed by default.
        """
        self.recency_period = int( value )

    security.declareProtected( CMFCorePermissions.View, 'getRecencyPeriod' )
    def getRecencyPeriod( self ):
        """
            Returns recency period in days.
            See 'setRecencyPeriod' desc. for details.
        """
        return getattr( self, 'recency_period', 0 )

InitializeClass(RegistrationBook)

#
# XXX: RegistrationBookColumn class is needed to migrate properly.
#

class RegistrationBookColumn(InstanceBase):
    """
        RegistrationBookColumn class.
    """
    _class_version = 1.0
    security = ClassSecurityInfo()

    def __init__(self, id, type, title='', attr_id=None, sort_index=0, multiple=0):
        InstanceBase.__init__(self, id, title)
        self.type = type
        self.attr_id = attr_id
        self.sort_index = sort_index
        self.multiple = multiple

    def __cmp__(self, other):
        assert isinstance( other, self.__class__ )
        return cmp(self.sort_index, other.sort_index)

    security.declarePublic('Type')
    def Type(self):
        """
            Returns the type the attribute, pointed by 'attr_id'.
        """
        return self.type

    security.declarePublic('getSortIndex')
    def getSortIndex(self):
        """
            Returns sort_index of the column.
        """
        return self.sort_index

    security.declarePublic('setSortIndex')
    def setSortIndex(self, si):
        """
            Sets sort_index for the column.
        """
        try:
            self.sort_index = int(si)
        except:
            pass

    security.declarePublic('getAttributeId')
    def getAttributeId(self):
        """
            Returns attribute id for the column.
        """
        return self.attr_id

    security.declarePublic('isMultiple')
    def isMultiple(self):
        """
            Indicates whether the field is multivalued.
            Results:
                Boolean.
        """
        return self.multiple

InitializeClass(RegistrationBookColumn)

def initialize( context ):
    # module initialization callback

    context.registerContent( RegistrationBook, addRegistrationBook, RegistrationBookType )
