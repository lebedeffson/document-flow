"""
$Id: FollowupActionsTool.py,v 1.127 2008/09/18 12:20:45 oevsegneev Exp $
"""
__version__ = '$Revision: 1.127 $'[11:-2]

from copy import deepcopy
from types import StringType, ListType

from Acquisition import Implicit, Explicit, aq_parent
from Globals import DTMLFile
from BTrees.OOBTree import OOBTree, OOTreeSet
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName, mergedLocalRoles
from Products.CMFCore.utils import _getAuthenticatedUser, _checkPermission, _dtmldir
from Products.PageTemplates.Expressions import getEngine
from Products.PluginIndexes.TextIndex.Vocabulary import Vocabulary
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import Catalog, CatalogError

import Config, Features
from interfaces.IJungleTree import IBasicTree
from TypesTool import TypeInformation, TypeGroupInformation
from CatalogSupport import SimpleQuery, IndexableObjectWrapper
from CatalogTool import CatalogTool
from HTMLCleanup import HTMLCleaner
from SimpleObjects import Persistent, InstanceBase, ToolBase, InterfacedBase
from TaskItemContainer import TaskItemContainer
from Utils import InitializeClass, cookId, refreshClientFrame, getObjectByUid, \
         get_param, joinpath, uniqueValues, getClassByMetaType

class SeenByLog(Persistent, Implicit):
    security = ClassSecurityInfo()

    _class_version = 1.00

    def __init__(self):
        self._pages_seen_by = OOBTree()

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not Persistent._initstate( self, mode ):
            return False

        if not mode:
            return True

        if not isinstance( self._pages_seen_by, OOBTree ):
            # upgrade to BTrees
            new_seen_by = OOBTree()
            for k, v in self._pages_seen_by.items():
                new_seen_by[k] = OOTreeSet(v)
            self._pages_seen_by = new_seen_by

        return True

    def __url(self, ob):
        return ob.physical_path()

    def getUserName(self, uname=None):
        if uname is None:
            return _getAuthenticatedUser(self).getUserName()
        else:
            return uname

    def addSeenByFor(self, task, uname=None):
        """
            Remembers that user has visited the given task item.

            Arguments:

                'ob' -- Task item.
        """
        uid = self.__url(task)
        uname = self.getUserName(uname)

        # seen_by = self._pages_seen_by.setdefault(uid, OOTreeSet() )
        if not self._pages_seen_by.has_key(uid):
            seen_by = self._pages_seen_by[uid] = OOTreeSet()
        else:
            seen_by = self._pages_seen_by[uid]
 
        if seen_by.insert( uname ):
             
            task.updateIndexes(idxs=['SeenBy',])
            # Request nav menu refresh
            refreshClientFrame( Config.FollowupMenu )

    def delSeenByFor(self, task, uname=None):
        """
            Removes seen by entry for the given user.

            Arguments:

                'ob' -- Task item.

                'uname' -- User id string.
        """
        uid = self.__url(task)

        try:
            if uname is None:
                del self._pages_seen_by[uid]
            else:
                self._pages_seen_by[uid].remove(uname)
        except KeyError:
            pass # notFound
        else:
            task.updateIndexes(idxs=['SeenBy',])
            # Request nav menu refresh
            refreshClientFrame( Config.FollowupMenu )

    def listSeenByFor(self, task):
        return self._pages_seen_by.get( self.__url(task), OOTreeSet() ).keys()

InitializeClass( SeenByLog )

class FollowupActionsTool( CatalogTool ):
    """
    Tasks indexing/search tool
    """
    _class_version = 1.31

    id              = 'portal_followup'
    meta_type       = 'NauSite Followup Actions Tool'

    _task_filters = {}

    security = ClassSecurityInfo()

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'dtml/explainFollowupTool', globals())

    IndexableObjectWrapper = IndexableObjectWrapper

    _catalog_indexes = [
            ('id', 'FieldIndex'),
            ('Title', 'TextIndexNG2'),
            ('Description', 'TextIndexNG2'),
            ('Creator', 'FieldIndex'),
            ('path', 'PathIndex'),
            ('created', 'DateIndex'),
            ('effective', 'DateIndex'),
            ('expires', 'DateIndex'),
            ('modified', 'DateIndex'),
            ('InvolvedUsers', 'KeywordIndex'),
            ('Supervisor', 'FieldIndex'),
            ('isFinalized', 'FieldIndex'),
            ('isEnabled', 'FieldIndex'),
            ('BrainsType', 'FieldIndex'),
            ('SeenBy', 'KeywordIndex'),
            ('StateKeys', 'KeywordIndex'),
            ('isStarted', 'FieldIndex'),
            ('isClosed', 'FieldIndex'),
            ('PendingUsers', 'KeywordIndex'),
            ('RespondedUsers', 'KeywordIndex'),
            ('DocumentCategory', 'FieldIndex'),
            ('DocumentFolder', 'FieldIndex'),
        ]

    _catalog_metadata = [
            'id',
            'Title',
            'Description',
            'Creator',
            'created',
            'effective',
            'expires',
            'InvolvedUsers',
            'Supervisor',
            'isFinalized',
            'BrainsType',
            'SeenBy',
            'StateKeys',
            'DocumentCategory',
            'DocumentFolder',
        ]

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not CatalogTool._initstate( self, mode ):
            return False

        if not hasattr(self, 'logger'):
            self.logger = SeenByLog()

        return True

    #
    #   'portal_catalog' interface methods
    #
    security.declarePrivate( 'searchResults' )

    security.declareProtected( CMFCorePermissions.View, 'searchTasks' )
    def searchTasks( self, restricted=True, do_autoexpand=True, REQUEST=None, **kw ):
        """
            Perfoms the portal-wide tasks search.

            Arguments:

                'REQUEST', '**kw' -- Extra arguments that limit the results to
                                     what the user is allowed to see.

        """
        membership = getToolByName( self, 'portal_membership' )
        username = membership.getAuthenticatedMember().getUserName()
        is_manager = _checkPermission( CMFCorePermissions.ManagePortal, self )
        if is_manager:
            restricted = False
        else:
            restricted = restricted is not Trust

        supervisor = get_param( 'Supervisor', REQUEST, kw, None )
        creator = get_param( 'Creator', REQUEST, kw, None )

        if kw.has_key('InvolvedUsers') and do_autoexpand:
            tokens = []
            involved_users = kw['InvolvedUsers']
            if isinstance( involved_users, StringType ):
                involved_users = kw['InvolvedUsers'] = [ involved_users ]
            for id in kw['InvolvedUsers']:
                if id.startswith( 'group:' ) or id.startswith( 'pos:' ) or id.startswith( 'div:' ):
                    continue
                member = membership.getMemberById( id )
                if member is None:
                    continue
                tokens.extend( member.listAccessTokens( include_userid=True,
                                                        include_positions=True,
                                                        include_divisions=True,
                                                        include_groups=True,
                                                        include_roles=False
                                                      ) )
            if tokens:
                kw['InvolvedUsers'].extend( uniqueValues( tokens ) )

        results = ZCatalog.searchResults( self, REQUEST, **kw )

        return results

    __call__ = searchTasks

    security.declareProtected( CMFCorePermissions.View, 'executeQuery' )
    def executeQuery(self, query, mode_name, REQUEST=None, **kwargs):
        """
           Lists tasks limited by 'query' and 'mode_name'

           Arguments:
                   'query' -- SearchQuery instance
                   'mode_name' -- viewing mode
                   'kwargs' - Extra arguments that pass to searchTasks.

           Result:

                List of catalog brains objects.

        """
        kwargs.update( getattr(query, 'filter_query', {}) )
        ### XXX
        if REQUEST and REQUEST.has_key('brains_type'):
            kwargs['BrainsType'] = REQUEST.get('brains_type')

        show_filter = self.getShowFilter( mode_name )

        if REQUEST and REQUEST.has_key('member_id'):
            kwargs = show_filter.setMainSearchKey( kwargs, member_id = REQUEST.get('member_id') )
        else:
            kwargs = show_filter.setMainSearchKey( kwargs )

        kwargs = show_filter.setFilteredOptions( kwargs )

        if type(kwargs) is ListType:
            results = []
            for kw in kwargs:
                results.extend(self.searchTasks( REQUEST=REQUEST, **kw ))
        else:
            results = self.searchTasks( REQUEST=REQUEST, **kwargs )

        return results # LazyCat

    security.declareProtected( CMFCorePermissions.View, 'executeQuery2' )
    def executeQuery2(self, mode_name, REQUEST, md=None):
        """
           TODO: removed md attribute
        """
        session = REQUEST['SESSION']
        uid = mode_name
        sort_on = REQUEST.get('sort_on', REQUEST.get('cookie_sort_on', 'created'))
        sort_order = REQUEST.get('sort_order', REQUEST.get('cookie_sort_order', ''))

        selected_columns = REQUEST.get('selected_columns', REQUEST.get('cookie_selected_columns', '').split(','))

        filter_id = 'followup'+ mode_name + '_' + (md.get('profile_id', ''))
        default_filter={ 'query': {}
                       , 'conditions':[]
                       , 'columns': self.getTableColumns()
                       }

        filter = session.get('%s_filter' % filter_id, default_filter)
        if not filter['columns']:
            filter['columns'] = self.getTableColumns()
        query = self.create_query( filter,
                                   mode_name=mode_name,
                                  )
        results = self.executeQuery( query=query,
                                     mode_name=mode_name,
                                     REQUEST=REQUEST,
                                     sort_on=None, # XXX support sort_on
                                   )

        # XXX remove this sorting, use catalog sorting instead
        results = md.sequence.sort(results, ((sort_on, 'cmp', sort_order),))
        results_count = len(results)
        total_count = len(self.executeQuery( None,
                                             mode_name=mode_name ,
                                             REQUEST=REQUEST,
                                           ))

        batch_size = int(getToolByName(self, 'portal_membership').getInterfacePreferences('viewing_document_number'))
        qs_new = int(REQUEST.get('qs', session.get('%s_qs' % uid, 1)))
        qs = qs_new / batch_size * batch_size + 1

        if session.get('%s_qs' % mode_name, qs ) != qs:
            session.set('%s_qs' % mode_name, qs)

        # XXX remove cookie
        REQUEST['RESPONSE'].setCookie('cookie_sort_on'
                                     , sort_on
                                     , path=REQUEST['BASEPATH1']
                                     , expires='Wed, 19 Feb 2020 14:28:00 GMT')
        REQUEST['RESPONSE'].setCookie('cookie_sort_order'
                                     , sort_order
                                     , path=REQUEST['BASEPATH1']
                                     , expires='Wed, 19 Feb 2020 14:28:00 GMT')
        REQUEST['RESPONSE'].setCookie('cookie_selected_columns'
                                     , ','.join(selected_columns)
                                     , path=REQUEST['BASEPATH1']
                                     , expires='Wed, 19 Feb 2020 14:28:00 GMT')

        return { 'results':results
               , 'results_count':results_count
               , 'total_count':total_count
               , 'batch_size':batch_size
               , 'qs':qs

               , 'sort_on':sort_on
               , 'sort_order':sort_order

               , 'filter':filter
               , 'filter_id':filter_id

               , 'table_columns':self.getTableColumns()
               , 'selected_columns':selected_columns
               }

    security.declarePrivate('registerTask')
    def registerTask(self, object):
        """
            Indexes task item in the catalog.

            Arguments:

                'object' -- Task item.
        """
        self.indexObject(object)

    security.declarePrivate('unregisterTask')
    def unregisterTask(self, object):
        """
            Removes task item reference from the catalog.

            Arguments:

                'object' -- Task item.
        """
        self.unindexObject(object)

    security.declareProtected( CMFCorePermissions.View, 'getStatistics' )
    def getStatistics(self, task_type, supervised=0, REQUEST=None, **kw):
        """
            Returns statistical data for the given task type.

            Arguments:

                'task_type' -- Task type string.

            Result:

                Mapping of the following structure:

                { <user_id>: [ <assigned_tasks_count>,
                               <expired_tasks_count>,
                               <pending_tasks_count>,
                               <processed_tasks_ratio>,
                               <list of user responses for each response type>,
                             ]
                }

            Finalized tasks are not included into the stat report.
        """
        results = {}

        mstool = getToolByName( self, 'portal_membership' )
        allowed = mstool.listSubordinateUsers( include_chief=1 )
        is_manager = _checkPermission( CMFCorePermissions.ManagePortal, self )

        tti = self.getTaskType( task_type )
        responses = {}
        for response in tti.listResponses():
            responses[ response['id'] ] = len(responses)

        tasks = self.searchTasks( BrainsType=task_type, REQUEST=REQUEST, **kw )
        for task in tasks:
            users = task['InvolvedUsers'][:]

            #support for 3.2 request tasks
            if not users:
                continue

            is_group_task = users[0].startswith( 'group:' )
            if supervised and task['Supervisor']:
                users.append(task['Supervisor'])

            for user in users:
                if not ( user in allowed or is_manager ):
                    continue

                record = results.get( user )
                if record is None:
                    record = results[ user ] = [ 0, 0, 0, 0, [0]*len(responses) ]

                record[0] += 1
                if task['expires'].isPast() and not task['isFinalized']:
                    record[1] += 1

                if user == task['Supervisor'] and ('review:%s' % user) not in task['StateKeys'] or\
                   ('pending:%s' % user) in task['StateKeys']:
                    record[2] += 1

            for response in task['StateKeys']:
                try:
                    code, user = response.split(':', 1)
                except ValueError:
                    pass
                else:
                    users = [user]
                    if is_group_task:
                        users = ['group:%s' % id for id in mstool.getMemberById(user).listGroupIds()]
                    for user in users:
                        if responses.has_key( code ) and results.has_key( user ):
                            results[ user ][4][ responses[code] ] += 1

        for counts in results.values():
            counts[3] = counts[0] and (counts[0] - counts[2])/(counts[0] + 0.0) * 100

        return results

    security.declareProtected( CMFCorePermissions.View, 'saveReport' )
    def saveReport(self, folder, title, description, report_generator, REQUEST):
        """
           Create an HTMLDocument containing a report
           previously generated with ReportWizard
        """
        html_text = report_generator(folder or self, REQUEST)

        # Find the folder where to place the overall report
        folder_uid=REQUEST.get('folder_uid')
        if folder_uid:
            folder = getObjectByUid(self, folder_uid)
        else:
            return ''

        if REQUEST.get('no_css', None) is not None:
            html_text = HTMLCleaner(html_text, None, 2, '', 'SCRIPT STYLE')

        #while( (not folder.implements('isPortalRoot')) and folder.meta_type != 'Heading' ):
        #   folder = aq_parent( aq_inner( self ) )

        if folder.implements('isPortalRoot'):
            folder = folder.storage

        id = cookId(folder, title=title, prefix='report')
        folder.invokeFactory(
            id = id,
            title = title,
            description = description,
            type_name = 'HTMLDocument',
            category = 'Document',
            text_format = 'text/html',
            text = html_text
        )

        return folder._getOb(id).absolute_url()

    security.declareProtected( CMFCorePermissions.View, 'listAllowedTaskTypes' )
    def listAllowedTaskTypes( self, context, manual=False ):
        """
            Returns the list of allowed task types in the given context.

            Arguments:

                'context' -- User context.

            Result:

                List of task type information mappings (see TaskBrains for
                details).
        """
        results = []
        types = self.listTaskTypes()
	uname = _getAuthenticatedUser( self ).getUserName()
        for tti in types:
             if manual and tti.getProperty( 'disallow_manual' ):
                 continue

             condition = tti.getProperty( 'condition' )
             if condition is not None:
                 if not condition( getEngine().getContext( {'here': context, 'member': uname } ) ):
                     continue

             permissions = tti.getProperty( 'permissions' )
             if permissions:
                  if isinstance( permissions, StringType ):
                      permissions = [ permissions, ]
                  for permission in permissions:
                       if _checkPermission( permission, context ):
                           break
                  else:
                      continue

             results.append( tti )

        return results

    security.declareProtected( CMFCorePermissions.View, 'listTaskTypes' )
    def listTaskTypes( self ):
        """
            Returns the list of portal task types.

            Result:

                List of task type information mappings (see TaskBrains for
                details).
        """
        result = []
        types = getToolByName( self, 'portal_types' )
        for info in task_type_information:
            type_info = types.getTypeInfo( info['id'] )
            if type_info is not None:
                result.append( type_info )
        return result

    security.declareProtected( CMFCorePermissions.View, 'getTaskType' )
    def getTaskType( self, task_type ):
        """
            Returns the task type information for the given task type.

            Arguments:

                'task_type' -- Task type name.

            Result:

                Task type information mapping.
        """
        types = getToolByName( self, 'portal_types' )
        return types.getTypeInfo( task_type )

    security.declarePublic( 'getTasksFor' )
    def getTasksFor(self, content):
        """
            Returns the tasks container for content, creating it if need be.

            Arguments:

                'content' -- Content object.

            Result:

                Reference to the TaskItemContainer class instance.
        """
        followup = getattr( content, 'followup', None )
        if not followup:
            followup = self._createFollowupFor( content )

        return followup

    def listFinalizationModes( self ):
        """
            Enumerates available task finalization modes.
        """
        return ( 'manual_creator',
#                'manual_creator_or_supervisor',
                 'auto_every_user',
                 'auto_any_user',
               )

    def getLogger( self ):
        """
            Returns the task logger instance used for tracking the user activity.

            Result:

                Reference to the logger object.
        """
        return self.logger
    #
    #   Utility methods
    #
    security.declarePrivate( '_createFollowupFor' )
    def _createFollowupFor( self, content ):
        """
            Creates the object that holds task items.

            Arguments:

                'content' -- Content object.

            Result:

                Reference to the TaskItemContainer class instance.
        """
        content.followup = TaskItemContainer()
        return content.followup

    security.declareProtected( CMFCorePermissions.View, 'getShowFilter' )
    def getShowFilter(self, mode_name):
        """
        """
        return getShowFilter( mode_name ).__of__( self )

    security.declareProtected( CMFCorePermissions.View, 'getTaskFilters' )
    def getTaskFilters(self):
        """
        """
        filters = deepcopy(self._task_filters)

        for k, v in filters.items():
            filters[k] = v.__of__(self)
        
        return filters

    security.declareProtected( CMFCorePermissions.View, 'getTaskFilterTree' )
    def getTaskFilterTree(self, root_item=Missing):
        """
        """
        tree = TaskFilterTree( self.getPortalObject() )

        if root_item is not Missing:
            tree.root_item = root_item

        return tree

    security.declareProtected( CMFCorePermissions.View, 'getTableColumns' )
    def getTableColumns(self):
        categories = getToolByName(self, 'portal_metadata').listCategories()
        return           [ { 'id'     : 'Title',
                             'title'  : 'Title',
                             'type'   : 'string',
                             'used_NG2' : 1,
                           },
                           { 'id'     : 'DocumentTitle',
                             'title'  : 'Document title',
                             'type'   : 'string',
                           },
                           { 'id'     : 'Creator',
                             'title'  : 'Assigned by',
                             'type'   : 'userlist',
                             'multiple' : 1,
                           },
                           { 'id'     : 'Supervisor',
                             'title'  : 'Supervisor',
                             'type'   : 'userlist',
                             'multiple' : 1,
                           },
                           { 'id'     : 'InvolvedUsers',
                             'title'  : 'Involved Users',
                             'type'   : 'userlist',
                             'multiple' : 1,
                           },
                           { 'id'     : 'created',
                             'title'  : 'Creation date',
                             'type'   : 'date',
                           },
                           { 'id'     : 'effective',
                             'title'  : 'Effective date',
                             'type'   : 'date',
                           },
                           { 'id'     : 'expires',
                             'title'  : 'Expiration date',
                             'type'   : 'date',
                           },
                           { 'id'     : 'BrainsType',
                             'title'  : 'Task type',
                             'type'   : 'list',
                             'multiple' : 1,
                             'options': [(t.getId(), t.Title()) for t in self.listTaskTypes()],
                           },
                           { 'id'     : 'DocumentCategory',
                             'title'  : 'Document category',
                             'type'   : 'list',
                             'multiple' : 1,
                             'options': [(c.getId(), c.Title()) for c in categories],
                           },
                           { 'id'     : 'DocumentFolder',
                             'title'  : 'Document folder',
                             'type'   : 'string',
                           },
                         ]

InitializeClass( FollowupActionsTool )

class TaskTypeInformation( InstanceBase, TypeInformation ):
    """ Portal content factory """
    _class_version = 1.00

    meta_type = 'Task Type Information'

    security = ClassSecurityInfo()
 
    _properties = TypeInformation._basic_properties + (
            {'id':'factory_form', 'type':'string', 'mode':'w', 'label':'Factory form'},
            {'id':'permissions', 'type':'lines', 'mode':'w', 'label':'Required permissions'},
            {'id':'condition', 'type':'string', 'mode':'w', 'label':'Required condition'},
            {'id':'disallow_manual', 'type':'boolean', 'mode':'w', 'label':'Disallow manual creation'},
          )

    _responses = ()
    _results = ()
    _factory = None

    def __init__( self, id, condition=None, group=None, **kw ):
        """ Initialize class instance
        """
        InstanceBase.__init__( self )
        TypeInformation.__init__( self, id, **kw )

        if condition and isinstance( condition, StringType ):
            self.condition = Expression( condition )
        elif condition:
            self.condition = condition

        if kw.has_key( 'responses' ):
            responses = []
            for item in kw['responses']:
                responses.append( item.copy() )
            self._responses = responses

        if kw.has_key( 'results' ):
            results = []
            for item in kw['results']:
                results.append( item.copy() )
            self._results = results

#        if kw.has_key( 'factory' ):
#            self._factory = kw['factory']

    _initstate = TypeGroupInformation._initstate.im_func

    def __cmp__( self, other ):
        # compare type objects by identifier
        if other is None:
            return 1
        if isinstance( other, TaskTypeInformation ):
            return cmp( self.getId(), other.getId() )
        if type( other ) is StringType:
            return cmp( self.getId(), other )
        raise TypeError, other

    def getFactory( self ):
        return getClassByMetaType( self.content_meta_type )

    def listResults( self ):
        return self._results

    def listResponses( self ):
        return self._responses

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed( self, container ):
        """
            Does the current user have the permission required in
            order to construct an instance?
        """
        return 0

    security.declarePublic('disallowManual')
    def disallowManual( self ):
        """
            Should manual creation of objects of this type be disallowed?
        """
        return 1

InitializeClass( TaskTypeInformation )

task_type_information = []

def registerTaskType( klass, tti, activate=True ):
    global task_type_information
    tti['factory'] = klass
    tti['activate'] = activate
    type_id = tti['id']
    for item in task_type_information:
        if item['id'] == type_id:
            raise ValueError, type_id
    task_type_information.append( tti )

#XXXX use portal_followup.getShowFilter
def getShowFilter( id ):
    return FollowupActionsTool._task_filters[id] 

#-------------------------------------------

class ShowTaskFilter( Explicit, InterfacedBase ):
    id = NotImplemented
    title = ""
    header = ""
    is_visible = True

    __allow_access_to_unprotected_subobjects__ = 1

    def __class_init__(self):
        if self.id is not NotImplemented:
            FollowupActionsTool._task_filters[ self.id ] = self()

        #tree support
        parent = self.__bases__[0] 
        if getattr( parent, 'id', NotImplemented) is not NotImplemented:
            parent._children = parent.__dict__.get( '_children', () ) + ( self.id ,)

    def isVisible(self):
        return self.is_visible

    def setMainSearchKey(self, query):
        return query

    def setFilteredOptions(self, query):
        return query

    def getMemberName( self, member_id = None ):
        membership = getToolByName( self, 'portal_membership' )
        member = member_id and membership.getMemberById(member_id) or membership.getAuthenticatedMember()
        return member.getUserName()

    def getMemberTokens( self, member_id = None ):
        membership = getToolByName( self, 'portal_membership' )
        member = member_id and membership.getMemberById(member_id) or membership.getAuthenticatedMember()
        return member.listAccessTokens( include_userid=True,
                                        include_positions=True,
                                        include_divisions=True,
                                        include_groups=True
                                      )

    def getParentTitle( self ):
        return super(self.__class__, self).title

    def getIcon(self, opened=False):
        """
        """
        return ''

class ShowAll( ShowTaskFilter ):
    """
        Root Filter
    """
    id = 'all'
    title = 'All tasks'

    def setFilteredOptions(self, query ):
        involved_users = query.get( 'InvolvedUsers', [] )
        involved_users.extend( self.getMemberTokens() )

        query_in = query.copy()
        query_out = query.copy()
        query_supervised = query.copy()

        query_in['InvolvedUsers'] = involved_users
        query_out['Creator'] = self.getMemberName()
        query_supervised['Supervisor'] = query_out['Creator']

        return [query_in, query_out, query_supervised]

    def getIcon(self, opened=False):
        """
        """
        return 'taskfolder.gif'

    def countTasks(self):
        """
           XXX: remove from this class
           !!!For this method needed Acquisition
        """
        followup_tool = aq_parent( self )
        if followup_tool:
            return len( followup_tool.executeQuery( None, self.id ) )
        else:
            return 0

#------------------------------------------
class ShowIn( ShowAll ):
    id = 'incoming_tasks'
    title = "Incoming tasks"
    header = "You are involved into the following tasks:"

    def setMainSearchKey(self, query):
        involved_users = query.get( 'InvolvedUsers', [] )
        involved_users.extend( self.getMemberTokens() )

        query['isEnabled'] = True
        query['InvolvedUsers'] = involved_users

        return query

    def setFilteredOptions(self, query ):
        return query

    def getIcon(self, opened=False):
        return 'inc_task_%s.gif' % ( opened and 'op' or 'cl' )

class ShowSeenNewIn( ShowIn ):
    id = 'showSeenNew'
    title = "tasks.tabs.new"
    is_visible = False

    def setFilteredOptions(self, query ):
        # not task_finalized and\
        # (task_pending and user_involved or \
        # is_supervisor and not task_review):
        query['isFinalized'] = False

        query['PendingUsers'] = SimpleQuery(self.getMemberTokens())

        query['SeenBy'] = SimpleQuery(self.getMemberName())

        return query

class ShowNewIn( ShowIn ):
    id = 'showNew'
    title = "tasks.tabs.new"

    def setFilteredOptions(self, query ):
        # not task_finalized and\
        # (task_pending and user_involved or \
        # is_supervisor and not task_review):
        query['isFinalized'] = False

        query['PendingUsers'] = SimpleQuery(self.getMemberTokens())

        return query

class ShowCurrentIn( ShowIn ):
    id = 'showCurrent'
    title = "tasks.tabs.current"

    def setFilteredOptions(self, query ):
        # not task_finalized and \
        #   not task_pending and user_involved and not report_closed:
        query['isFinalized'] = False

        username = self.getMemberName()
        PU_query = SimpleQuery(self.getMemberTokens())
        PU_query.setOption( 'operator', 'not' )
        query['PendingUsers'] = PU_query
        query['StateKeys'] = {'query': 'closed_report:%s' % username, 'operator':'not'}

        return query

class ShowWithClosedReportIn( ShowIn ):
    id = 'showWithClosedReport'
    title =  "tasks.tabs.closed"

    def setFilteredOptions(self, query ):
        # and not task_finalized and \
        # (task_seen and user_involved and report_closed):
        query['isFinalized'] = False

        username = self.getMemberName()
#       query['SeenBy'] = username
        query['StateKeys'] = 'closed_report:%s' % username

        return query

class ShowFinalizedIn( ShowIn ):
    id = 'showFinalized'
    title = "tasks.tabs.finalized"

    def setFilteredOptions(self, query ):
        # and task_finalized and \
        #           (user_involved or is_supervisor):
        query['isFinalized'] = True

        return query

#-------------------------------------------
class ShowOut( ShowAll ):
    id = 'outgoing_tasks'
    title = "Outgoing tasks"

    __implements__ = Features.canCreateTasks

    def setMainSearchKey(self, query):
        query['Creator'] = self.getMemberName()

        return query

    def setFilteredOptions(self, query ):
        return query

    def getIcon(self, opened=False):
        return 'out_task_%s.gif' % ( opened and 'op' or 'cl' )

class ShowSeenNewOut( ShowOut ):
    id = 'showSeenNew_out'
    title = "tasks.tabs.new"
    is_visible = False

    def setFilteredOptions(self, query ):
        #not task_started
        query['isStarted'] = False

        query['SeenBy'] = SimpleQuery(self.getMemberName())

        return query

class ShowNewOut( ShowOut ):
    id = 'showNew_out'
    title = "tasks.tabs.new"

    def setFilteredOptions(self, query ):
        #not task_started
        query['isStarted'] = False

        return query

class ShowCurrentOut( ShowOut ):
    id = 'showCurrent_out'
    title = "tasks.tabs.current"

    def setFilteredOptions(self, query ):
        #task_started and not task_closed and not task_finalized:
        query['isStarted'] = True
        query['isClosed'] = False
        query['isFinalized'] = False

        return query

class ShowWithClosedReportOut( ShowOut ):
    id = 'showWithClosedReport_out'
    title =  "tasks.tabs.closed"

    def setFilteredOptions(self, query ):
        #task_closed and not task_finalized:
        query['isClosed'] = True
        query['isFinalized'] = False

        return query

class ShowFinalizedOut( ShowOut ):
    id = 'showFinalized_out'
    title = "tasks.tabs.finalized"

    def setFilteredOptions(self, query ):
        #task_started and task_finalized:
        query['isStarted'] = True
        query['isFinalized'] = True

        return query
#--------------------------------------------
class ShowSupervised( ShowAll ):
    id = 'supervised_tasks'
    title = "Supervised tasks"
    header = "You are a supervisor of the following tasks:"

    def setMainSearchKey(self, query):
        query['isEnabled'] = True
        query['Supervisor'] = self.getMemberName()

        return query

    def setFilteredOptions(self, query ):
        return query

    def getIcon(self, opened=False):
        """
        """
        return 'inc_task_%s.gif' % ( opened and 'op' or 'cl' )

class ShowSeenSupervised( ShowSupervised ):
    id = 'showSeenNew_supervised'
    title = "tasks.tabs.new"
    is_visible = False

    def setFilteredOptions(self, query ):
        # is_supervisor and not task_review):
        query['isFinalized'] = False

        username = self.getMemberName()
        query['StateKeys'] = {'query': 'review:%s' % username, 'operator':'not'}

        query['SeenBy'] = SimpleQuery(self.getMemberName())

        return query

class ShowNewSupervised( ShowSupervised ):
    id = 'showNew_supervised'
    title = "tasks.tabs.new"

    def setFilteredOptions(self, query ):
        # is_supervisor and not task_review):
        query['isFinalized'] = False

        username = self.getMemberName()
        query['StateKeys'] = {'query': 'review:%s' % username, 'operator':'not'}

        return query

class ShowWithClosedReportSupervised( ShowSupervised ):
    id = 'showWithClosedReport_supervised'
    title =  "tasks.tabs.closed"

    def setFilteredOptions(self, query ):
        # and not task_finalized and \
        # (is_supervisor and task_review):
        query['isFinalized'] = False

        username = self.getMemberName()
        query['StateKeys'] = 'review:%s' % username

        return query

class ShowFinalizedSupervised( ShowSupervised ):
    id = 'showFinalized_supervised'
    title = "tasks.tabs.finalized"

    def setFilteredOptions(self, query ):
        # and task_finalized and \
        #           is_supervisor:
        query['isFinalized'] = True

        return query

#----------------------------------------------
class ShowMemberIn( ShowIn ):
    id = 'incoming_member_tasks'
    title = "Incoming tasks"
    header = "You are involved into the following tasks:"
    is_visible = False

    def setMainSearchKey(self, query, member_id=None):
        involved_users = query.get( 'InvolvedUsers', [] )

        if member_id:
            involved_users.extend( self.getMemberTokens( member_id = member_id ))
        else:
            involved_users.extend( self.getMemberTokens() )

        query['isEnabled'] = True

        query_in = query.copy()
        query_supervised = query.copy()

        query_in['InvolvedUsers'] = involved_users
        query_supervised['Supervisor'] = self.getMemberName( member_id )

        return [query_in, query_supervised]

#----------------------------------------------
class TaskFilterTree(object):

    root_item = 'all'

    __implements__ = IBasicTree

    def __init__(self, context):
        self.need_cleanup = False
        self.root_url = context.portal_url()

        self.get_items = TaskFilterTreeWalker()
        self.info_dict = context.portal_followup.getTaskFilters()

class TaskFilterTreeWalker:
 
    def __call__(self, item ):
         show_filter = getShowFilter( item )
         
         for child in show_filter.__class__.__dict__.get( '_children', () ):
             if getShowFilter( child ).isVisible():
                 yield child

def initialize( context ):
    # module initialization callback

    context.registerTool( FollowupActionsTool )

    context.register( registerTaskType )    
    context.registerTypeFactory( TaskTypeInformation, 'manage_addFactoryTIForm' )

    context.registerFtis( task_type_information )
