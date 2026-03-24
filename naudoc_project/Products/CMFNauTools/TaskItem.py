"""Task Item base class.

$Editor: ikuleshov $
$Id: TaskItem.py,v 1.262 2007/10/19 12:36:01 oevsegneev Exp $
"""
__version__ = '$Revision: 1.262 $'[11:-2]

from types import StringType, ListType
from sets import Set

from Acquisition import aq_base, aq_parent
from AccessControl import ClassSecurityInfo, Permissions
from BTrees.IIBTree import IISet, IITreeSet, intersection, union
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from DateTime import DateTime
from Globals import DTMLFile, package_home
from OFS.ObjectManager import ObjectManager
from zExceptions import Unauthorized
from ZODB.PersistentMapping import PersistentMapping
from ZODB.POSException import ConflictError

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.FSPythonScript import FSPythonScript
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser, _checkPermission
from Products.PageTemplates.Expressions import getEngine
from Products.NauScheduler.TemporalExpressions import DateTimeTE, \
     UniformIntervalTE, MonthlyByDateTE, UnionTE

import Features
from CatalogSupport import IndexableMethod
from Config import Roles
from File import addFile
from SimpleObjects import ContentBase
from ResponseCollection import ResponseCollection
from TaskItemContainer import TaskItemContainer
from Utils import InitializeClass, cookId, setDefaultAttrs, parseTime, flattenString, \
         uniqueValues, isSequence, getObjectImplements, tuplify

class IndexableTaskMethod( IndexableMethod ):
    def getReindexMethod( self, context ):
        return context.updateIndexes


TASK_RESULT_SUCCESS = 'success'
TASK_RESULT_FAILED = 'failed'
TASK_RESULT_CANCELLED = 'cancelled'

class TaskItemBase( ContentBase, ObjectManager ):
    """ Task item base class."""
    _class_version = 1.0

    __implements__ = ( Features.isTaskItem,
                       ContentBase.__implements__,
                       ObjectManager.__implements__,
                     )

    __unimplements__ = ( Features.isPortalContent,
                       )
    meta_type = None

    allow_discussion = 1

    __resource_subkeys__ = [ 'uname', 'status', 'response_id' ]

    mail_notify_users = 'task.notify_users'
    mail_supervisor_notify = 'task.supervisor_notify'
    mail_supervisor_canceled = 'task.supervisor_cancelled'
    mail_alarm = 'task.alarm'
    mail_changes = 'task.inform_changes'
    mail_finalized = 'task.finalized'

    mail_user_reviewed = 'task.reviewed'
    mail_user_included = 'task.directive_user_included'
    mail_user_excluded = 'task.directive_user_excluded'

    dateperiod = FSPythonScript('dateperiod', '%s/skins/common/dateperiod.py' % package_home(globals()))

    security = ClassSecurityInfo()

    _expiration_schedule_id = None
    _effective_schedule_id = None
    _alarm_schedule_id = None
    temporal_expr = None
    duration = None
    plan_time = None
    bind_to = None
    enabled = False
    finalized = False
    result = None
    version_id = None
    finalization_mode = 'manual_creator'

    def __init__( self,
                  id,
                  title,
                  description='',
                  creator=None,
                  involved_users=[],
                  supervisor=None,
                  effective_date=None,
                  expiration_date=None,
                  duration=None,
                  alarm_settings=None,
                  task_template_id=None,
                  finalization_mode='manual_creator',
                ):
        ContentBase.__init__( self, id, title )

        self._container = PersistentMapping()

        self.description = description
        self.creator = creator or _getAuthenticatedUser(self).getUserName()
        self.supervisor = supervisor
        self.involved_users = involved_users

        if not effective_date:
            effective_date = DateTime()
        self.effective_date = effective_date

        if not expiration_date and duration:
            expiration_date = DateTime( float(effective_date.timeTime() + duration) )
        self.expiration_date = expiration_date

        self.alarm_settings = alarm_settings
        self.responses = ResponseCollection()
        self.task_template_id = task_template_id
        self.attachments = []
        self.notification_history = []
        self.followup_tasks = []
        self.finalization_mode = finalization_mode


    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not ContentBase._initstate( self, mode ):
            return False

        if getattr(self, 'notification_history', None) is None:
            self.notification_history = []

        if not hasattr(self, '_task_schedule_id'):
            default = getattr(self, 'schedule_id', None)
            self._task_schedule_id = default

        if not hasattr(self, 'followup_tasks'):
            self.followup_tasks = []

        if not hasattr(self, 'actual_times'):
            self.actual_times = PersistentMapping()

        if not hasattr(self, 'attachments'):
            self.attachments = []

        return True

    def _instance_onCreate( self ):
        REQUEST = getattr( self, 'REQUEST', None )
        if REQUEST:
            file = REQUEST.get( 'attachment', '' )
            if file:
                self.attachFile( file=file )

#        self.setInvolvedUsers( self.involved_users )

        effective_date = self.effective_date
        if effective_date is None:
            effective_date = DateTime()
        self.setEffectiveDate( effective_date )

        expiration_date = self.expiration_date
        if not expiration_date:
            raise ValueError, 'Expiration date required. Infinite tasks are not allowed.'
        self.setExpirationDate( expiration_date )

        self.setAlarm( self.alarm_settings )

    def _containment_onAdd( self, item, container ):
        self.resetSchedule()
        followup = getToolByName( self, 'portal_followup', None )
        if followup is not None:
            followup.registerTask( self )

    def _containment_onDelete( self, item, container ):
        """
          Removes self from the catalog
        """
        #
        #   Are we going away?
        #
        if aq_base(container) is not aq_base(self):
            #self.stopSchedule()
            followup = getToolByName( self, 'portal_followup', None )
            if followup is not None:
                logger = followup.getLogger()
                logger.delSeenByFor(self)
                followup.unregisterTask( self )
                
    def _instance_onDestroy(self):
        self.stopSchedule()

    def __call__( self, REQUEST=None ):
        """
            Invokes the default view.
        """
        if not self.validate():
           raise Unauthorized, self.getId()

        # Check task as read by the current user
        portal_followup = getToolByName( self, 'portal_followup' )
        logger = portal_followup.getLogger()
        logger.addSeenByFor( self )

        return ContentBase.__call__(self, REQUEST)

    def _getVersionId( self ):
        try:
            # if this is a subtask then return parent's version_id
            parent = self.parent().getTask( self.bind_to )
            version_id = parent._getVersionId()
        except KeyError:
            # this task is not bound to any other task
            version_id = getattr( self, 'version_id', None )
        return version_id

    def getPhysicalPath( self ):
        """
            Returns physical path of the task.
            If the task is bind to a version the path is taken
            in context of the version.
        """
        ftool = getToolByName(self, 'portal_followup')
        task = self

        base = self.getBase()
        version_id = self._getVersionId()
        if base.implements('isVersionable') and version_id:
            base = base.getVersion( version_id )
            container = ftool.getTasksFor(base)
            envelope = aq_base(container).__of__(base)
            task = aq_base(self).__of__(envelope)

        return ContentBase.getPhysicalPath(task)

    def portal_type( self ):
        return self.meta_type

    security.declarePrivate( CMFCorePermissions.View, 'get_responses' )
    def get_responses( self ):
        """
            Returns the responses collection instance associated with the task object.

            Responses collection instance is created within every task item;
            it is responsible for storing and retrieving the user responses.

            Result:

                Reference to the ResponseCollection instance.
        """
        return self.responses

    listResponses = get_responses

    security.declarePublic( 'Creator' )
    def Creator( self ):
        """
            Returns the task author.

            Result:

                String.
        """
        try: creator = self.creator
        except: creator = ContentBase.Creator( self )

        return creator

    security.declareProtected( CMFCorePermissions.View, 'ResultCode' )
    def ResultCode( self ):
        """
            Returns the task finalization status.

            None value indicates that task is still in progress. Available
            task result codes are defined in the task brain information
            mapping.

            Result:

                String.
        """
        return self.result

    security.declareProtected( CMFCorePermissions.View, 'Supervisor' )
    def Supervisor( self ):
        """
            Returns the supervisor assigned with the task.

            Supervisor is able to track and review the task progress in order
            to share owner's duties.

            Note:

                None result value indicates that no supervisor was assigned.

            Result:

                User id string or None.
        """
        return self.supervisor

    security.declareProtected( CMFCorePermissions.View, 'isInvolved' )
    def isInvolved( self, user=None ):
        """
            Checks whether the member is involved into the task.

            Arguments:

                'user' -- User id string. None value indicates that current
                           authenticated member id has to be used.

            Result:

                Boolean.
        """
        if not user:
            user = _getAuthenticatedUser(self).getUserName()
        return user in self.listInvolvedUsers( flatten=True )

    security.declareProtected( CMFCorePermissions.View, 'isViewer' )
    def isViewer( self, user=None ):
        """
            Checks whether the member participates in the task.

            Arguments:

                'user' -- User id string. None value indicates that current
                authenticated member id has to be used.

            Result:

                Boolean.
        """
        if not user:
            user = _getAuthenticatedUser(self).getUserName()

        return self.isInvolved( user ) or self.isCreator( user ) or self.isSupervisor( user )

    security.declareProtected( CMFCorePermissions.View, 'isCreator' )
    def isCreator( self, user=None ):
        """
            Checks whether the member is a task author.

            Arguments:

                'user' -- User id string. None value indicates that current
                           authenticated member id has to be used.

            Result:

                Boolean.
        """
        if not user:
            user = _getAuthenticatedUser(self).getUserName()

        return user == self.Creator()

    security.declareProtected( CMFCorePermissions.View, 'isSupervisor' )
    def isSupervisor( self, user=None ):
        """
            Checks whether the member is a task supervisor.

            Arguments:

                'user' -- User id string. None value indicates that current
                           authenticated member id has to be used.

            Result:

                Boolean.
        """
        if not user:
            user = _getAuthenticatedUser(self).getUserName()

        return user == self.Supervisor()

    security.declarePublic( 'validate' )
    def validate( self ):
        """
            Checks whether the current user is allowed to access the given task
        """
        base = self.getBase()
        if base.implements(('isVersionable', 'isVersion',)):
            version_id = base.getCurrentVersionId()
            task_version = self._getVersionId()
            if task_version is not None and task_version != version_id:
                return None

        local_roles = _getAuthenticatedUser(self).getRolesInContext(self)

        is_viewer = self.isViewer()
        if not is_viewer:
            parents = self.parentsInThread()
            for item in parents:
                if not hasattr( item, 'isViewer' ):
                    continue
                is_viewer = item.isViewer()
                if is_viewer:
                    break

        return  _checkPermission(CMFCorePermissions.View, self) and \
                (   is_viewer or \
                    Roles.Manager in local_roles or \
                    Roles.Editor in local_roles)

    security.declareProtected( CMFCorePermissions.View, 'isFinalized' )
    def isFinalized( self ):
        """
            Checks whether this task is finalized.

            No further responds expected from the involved users since the
            task was finalized.

            Result:

                Boolean.
        """
        return self.finalized

    security.declarePublic( 'attachFile' )
    def attachFile( self, file, id=None, title=None ):
        fid = addFile( self, id=id, file=file, title=title )
        self.attachments.append(fid)
        self.reindexObject()
        return fid

    def objectIds( self, spec=None ):
        ids = ObjectManager.objectIds(self, spec)
     
        #XXXXXX how could TaskItemContainer be in TaskItem
        followup = ( hasattr( aq_base( self ), 'followup' ) and self.followup or None )
        if followup is not None:
            ids.append('followup')
        return ids

    # XXX inherit ContainerBase
    # restore overloaded methods by PortalContent
    objectValues = ObjectManager.objectValues
    objectItems = ObjectManager.objectItems
    tpValues = ObjectManager.tpValues

    security.declarePublic( 'listAttachedFiles' )
    def listAttachedFiles( self ):
        """
            Returns a list of the task's file attachments.

            Result:

                List of (id, attachment) pairs.
        """
        attaches = filter(lambda x: x[0] , ObjectManager.objectItems( self ))
        return filter( lambda x, ids=self.attachments: x[0] in ids, attaches)

    security.declarePublic( 'isEnabled' )
    def isEnabled( self ):
        """
            Checks whether this task is enabled.

            Result:

                Boolean.
        """
        return self.enabled

    def isStarted(self):
        """
            TODO:
        """
        return bool( not self.InvolvedUsers() or
                     self.listRespondedUsers() or
                     self.isFinalized()
                   )

    def isClosed(self):
        """
            TODO:
        """
        return bool( self.listUsersWithClosedReports() == self.InvolvedUsers() and
                     ( not self.supervisor or
                       self.searchResponses( status='review', member=self.supervisor )
                     )
                   )

    security.declareProtected( CMFCorePermissions.View, 'isEditable' )
    def isEditable(self):
        """
            Checks whether this task is editable.

            Note:

                Tasks that have been created in action
                template is not editable by default.

            Result:

                Boolean.


        """
        #XXX may be here check for isEnabled too???
        return self.isCreator() and not self.isFinalized() and not self.task_template_id

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setSupervisor' )
    def setSupervisor(self, supervisor):
        """
            Sets the task supervisor.

            Arguments:

                'supervisor' -- Superisor user id string.
        """
        if self.isEnabled():
            self._old_supervisor = self.supervisor
        self.supervisor = supervisor

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setInvolvedUsers' )
    def setInvolvedUsers( self, involved_users ):
        """
            Sets the task involved users.

            Involved users are responsible for perfoming the task.

            Arguments:

                'involved_users' -- List of the involved users id strings.
        """
        if not isSequence( involved_users ):
            involved_users = [ involved_users ]

        if self.isEnabled():
            self._old_involved_users = self.involved_users
        self.involved_users = involved_users

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setEffectiveDate' )
    def setEffectiveDate( self, effective_date ):
        """
            Sets the task effective date.

            Arguments:

                'effective_date' -- DateTime class instance.

            Note:

                In case the task expiration date is less then effective date,
                expiration date becomes equal to next day after the task
                effective date.
        """
        self.effective_date = self._datify( effective_date )

        is_future = self.effective().isFuture()

        if self.isEnabled() and is_future:
            self.Disable()

        if self.effective() > self.expires():
            self.setExpirationDate(self.effective() + 1.0)

        # schedule task start
        if is_future:
            scheduler = getToolByName( self, 'portal_scheduler', None )
            if scheduler is None:
                return

            element_id = self._effective_schedule_id
            if element_id:
                scheduler.delScheduleElement( schedule_id )

            temporal_expr = DateTimeTE( self.effective() )
            self._effective_schedule_id = scheduler.addScheduleElement( self.Enable,
                                                          temporal_expr=temporal_expr,
                                                          title="Enable [%s]" % self.Title()
                                                         )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent
                             , 'setExpirationDate' )
    def setExpirationDate( self, expiration_date ):
        """
            Sets the task expiration date.

            Arguments:

                'effective_date' -- DateTime class instance.
        """
        self.expiration_date = self._datify( expiration_date )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'Enable' )
    def Enable(self, no_mail=None):
        """
            Enables the task.

            Arguments:

                'no_mail' -- Disable mail notifications.

            Sends mail notifications and allows involved users to write their
            reports.
        """
        old_involved_users = getattr( self, '_old_involved_users', [] )
        involved_users = self.listInvolvedUsers()
        included_users = filter( lambda x, t=old_involved_users: x not in t, involved_users )
        excluded_users = filter( lambda x, t=involved_users: x not in t, old_involved_users)

        if not no_mail:
            # Notify included and excluded users via email
            if included_users:
                self.send_mail( flattenUsers( self, included_users ), 'mail_user_included' )

            if excluded_users:
                self.send_mail( flattenUsers( self, excluded_users ), 'mail_user_excluded' )

        restricted_users = list( excluded_users )
        granted_users = list( included_users )

        base = self.getBase()
        old_supervisor = getattr( self, '_old_supervisor', [] )
        supervisor = self.Supervisor()
        # Check whether the task supervisor have been changed since last Enable() call
        if supervisor != old_supervisor:
            if old_supervisor:
                restricted_users.append( old_supervisor )
                if not no_mail:
                    self.send_mail( [ old_supervisor ], 'mail_supervisor_canceled' )

            if supervisor:
                granted_users.append( supervisor )
                if not no_mail:
                    self.send_mail( [ supervisor ], 'mail_supervisor_notify' )

        if supervisor in restricted_users:
            restricted_users.remove( supervisor )

        if self.Creator() in restricted_users:
            restricted_users.remove( self.Creator() )

        if restricted_users:
            self.manage_delLocalGroupRoles( [ u[6:] for u in restricted_users if u.startswith('group:') ] )
            self.manage_delLocalRoles( [ u for u in restricted_users if not u.startswith('group:') ] )
            if not base.implements('isPortalRoot'):
                # Delete local roles from the document only for those users who are not participating
                # in any of the document's tasks.
                participants = []
                for task in self.followup.objectValues():
                    participants.extend( task.listInvolvedUsers() )
                    participants.append( task.Creator() )
                    participants.append( task.Supervisor() )

                restricted_users = filter( lambda u, p=participants: u not in p, restricted_users )
                if restricted_users:
                    base.manage_delLocalGroupRoles( [ u[6:] for u in restricted_users if u.startswith('group:') ] )
                    base.manage_delLocalRoles( [ u for u in restricted_users if not u.startswith('group:') ] )

        allowed = [ self ]
        if not base.implements('isPortalRoot'):
            allowed.append( base )

        for ob in allowed:
            for user in granted_users:
                if 'Owner' in ob.get_local_roles_for_userid( user ):
                    continue
                if user.startswith( 'group:' ):
                    setRoles =  ob.manage_setLocalGroupRoles
                    user = user[6:]
                else:
                    setRoles = ob.manage_setLocalRoles
                setRoles( user, ['Reader'] )

        self.reindexObject(idxs=['allowedRolesAndUsers'])
        base.reindexObject(idxs=['allowedRolesAndUsers'])

        self.enabled = True

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'Disable' )
    def Disable( self ):
        """
            Disables the task.
        """
        self.enabled = False

    def Finalize( self, result_code=None, safe=False ):
        """
            Checks whether given result_code is allowed and finalizes task.
        """
        allowed_result_codes = [ x.get('id') for x in self.listResultCodes( manual=not( safe is Trust ))]
        assert result_code in allowed_result_codes
        self._finalize( result_code )

    def _finalize(self, result_code=None):
        """
            Finalizes task.

            Arguments:

                'result_code' -- String. Task finalization code.

            Nobody is allowed to write reports after the task was finalized.
        """
        if self.isFinalized():
            return

        self.finalized = True
        self.result = result_code

        # event 'finalize task'
        portal_workflow = getToolByName(self, 'portal_workflow')
        portal_workflow.onFinalize(self)

        self.stopSchedule()
        # XXX Should always finalize subtasks.
        tasks = self.followup.getBoundTasks(recursive=1)
        for task in tasks:
            task.onFinalize( result_code = result_code )

    security.declareProtected( CMFCorePermissions.View, 'listInvolvedUsers' )
    def listInvolvedUsers(self, flatten = False):
        """
            Returns the list of involved members.

            Arguments:

                'flatten' -- list or boolean.

            Result:

                List of user id strings.
        """
        users = tuplify(self.involved_users)
        membership = getToolByName(self, 'portal_membership')

        if flatten:
            if not isSequence(flatten):
                # flatten everything
                return membership.listPlainUsers(users)

            results = []

            for u in users:
                parts = u.split(':', 1)
                if len(parts) == 1 or parts[0] not in flatten:
                    results.append(u)
                else:
                    results.extend(membership.listPlainUsers(u))

            return results

        return list(users)

    # alias for catalog
    InvolvedUsers = listInvolvedUsers

    security.declareProtected( CMFCorePermissions.View, 'listRespondedUsers' )
    def listRespondedUsers(self):
        """
            Returns the list of responded users.

            Result:

                List of user id strings.
        """
        return self.get_responses().getIndexKeys('member')

    # alias for catalog
    RespondedUsers = listRespondedUsers

    security.declareProtected( CMFCorePermissions.View, 'listPendingUsers' )
    def listPendingUsers(self):
        """
            Returns the list of users involved into the task who did not make any response.

            Result:

                List of the user id strings.
        """
        membership = getToolByName(self, 'portal_membership')

        tokens = []
        for name in self.listRespondedUsers():
            user = membership.getMemberById(name)
            if user is None:
                continue

            # pos:, username
            tokens += user.listAccessTokens(
                include_divisions = False,
                include_groups = False,
                include_roles = False
            )

        return list(
            Set(self.listInvolvedUsers(flatten = ('div', 'group'))) -
            Set(tokens)
        )

    # alias for catalog
    PendingUsers = listPendingUsers

    security.declareProtected( CMFCorePermissions.View, 'StateKeys' )
    def StateKeys( self ):
        """
            Indexing routine. Describes the current task state in a short string.

        """
        state = []

        for member in self.listUsersWithClosedReports():
            state.append("closed_report:%s" % member)

        for r in self.searchResponses():
            state.append("%s:%s" % (r['status'], r['member']))

        return state

    security.declareProtected( CMFCorePermissions.View, 'SeenBy' )
    def SeenBy( self ):
        """
            Indexing routine. Returns the list of users that have already viewed this object.

            Note:

                Should be obsolete in future releases.

            Result:

                List of user id strings.
        """
        portal_followup = getToolByName( self, 'portal_followup', None )
        if portal_followup is not None:
            logger = portal_followup.getLogger()
            seen_by = logger.listSeenByFor(self)
            return list(seen_by)

    security.declarePrivate( 'updateIndexes' )
    def updateIndexes( self, idxs=[] ):
        if idxs == []:
            # Update the modification date.
            if hasattr(aq_base(self), 'notifyModified'):
                self.notifyModified()
        portal_followup = getToolByName(self, 'portal_followup', None)
        if portal_followup is not None:
            portal_followup.reindexObject(self, idxs)

    #
    # Threading interface
    security.declareProtected( CMFCorePermissions.View, 'isBoundTo' )
    def isBoundTo( self, REQUEST=None ):
        """
            Returns the task parent.

            Result:

                Task item reference or None.
        """
        tool = getToolByName( self, 'portal_followup' )
        followup = tool.getTasksFor( self )
        return followup._getTaskParent( self.bind_to )

    security.declarePrivate( CMFCorePermissions.View, 'BindTo' )
    def BindTo( self, bind_to ):
        """
            Binds this task to the parent 'bind_to'

            Arguments:

                'bind_to' -- Parent object.
        """
        if getObjectImplements(bind_to, Features.isTaskItem):
            self.bind_to = bind_to.getId()
        else:
            self.bind_to = None

            if getObjectImplements(bind_to, Features.isVersionable):
                self.version_id = bind_to.getVersion().getId()
            else:
                self.version_id = None


    security.declareProtected( CMFCorePermissions.View, 'parentsInThread' )
    def parentsInThread( self, size=0 ):
        """
            Returns the list of items which are "above" this item in the task thread.

            Arguments:

                'size' -- Integer. If 'size' is not zero, only the closest
                          'size' parents will be returned.

            Result:

                List of parent task items.
        """
        parents = []
        current = self
        while not size or len( parents ) < size:
            parent = current.isBoundTo()
            assert not parent in parents  # sanity check
            parents.insert( 0, parent )
            if not ( hasattr( parent, 'implements' ) and parent.implements( Features.isTaskItem ) ):
                break
            current = parent
        return parents

    security.declareProtected( CMFCorePermissions.View, 'findRootTask' )
    def findRootTask( self ):
        """
            Finds the topmost task in a thread.

            Returns self if no parent tasks were found.

            Result:

                Reference to the Task item instance.
        """
        parents = self.parentsInThread()
        if len(parents)>=2:
            # The first parent is content object and the second
            # is a top level task item of the thread
            return parents[1]

        return self

    security.declareProtected( CMFCorePermissions.View, 'getBase' )
    def getBase( self ):
        return self.parent().getBase()

    security.declareProtected( CMFCorePermissions.View, 'deleteObject')
    def deleteObject( self, REQUEST=None ):
        """
           Selfdestruction method.
        """
        # 1. manager can delete tasks
        can_del = _checkPermission( CMFCorePermissions.ManagePortal, self )
        # 2. creator can delete tasks if task not started
        task_not_started=('task_not_started' in self.StateKeys())
        if task_not_started and self.isCreator():
            can_del=True

        if can_del:
            id = self.getId()
            self.deleteTask(id)
        # else: need any message ???
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( self.getBase().absolute_url(action="document_follow_up_form") )

    security.declareProtected( CMFCorePermissions.View, 'BrainsType' )
    def BrainsType( self ):
        """
            Returns the brains type id associated with the task.

            Result:

                String. Task brains type id.
        """
        return self.getTypeInfo().getId()

    security.declareProtected( CMFCorePermissions.View, 'DocumentCategory' )
    def DocumentCategory( self ):
        """
            Indexing routine: returns the category of the parent document.

            Result:

               String.
        """
        base = self.getBase()
        if base.implements('isCategorial'):
            return base.Category()

    security.declareProtected( CMFCorePermissions.View, 'DocumentFolder' )
    def DocumentFolder( self ):
        """
            Indexing routine: returns the folder title of the parent document.

            Result:

                String.
        """
        base = self.getBase()
        if not base.implements('isPortalRoot'):
            folder = aq_parent( base )
            return folder.Title()

    security.declareProtected( CMFCorePermissions.View, 'canRespond' )
    def canRespond( self, status ):
        """
            Checks whether the user is able to respond with the given status.

            Result:

                Boolean.
        """
        allowed_ids = [ rti['id'] for rti in self.listAllowedResponseTypes() ]
        return status in allowed_ids

    security.declareProtected( CMFCorePermissions.View, 'canSendNotifications' )
    def canSendNotifications( self ):
        """
            Checks whether the user can send notifications to the involved users.

            Result:

                Boolean.
        """
        result = not self.isFinalized() and self.listInvolvedUsers() and \
                 ( self.isCreator() or self.isSupervisor() )
        return result

# XXX remove this
    security.declarePrivate( 'OpenReportFor' )
    def OpenReportFor(self, uname):
        """
            Opens report for the selected user.

            Arguments:

                'uname' -- User id string.

            Opened reports can be modified in any time until the task is not
            finalized.
        """
        responses = self.searchResponses(member=uname, isclosed=1)
        for response in responses:
            layer = response['layer']
            status = response['status']
            text = response['text']
            member = response['member']
            self.get_responses().addResponse( layer=layer
                                            , status=status
                                            , text=text
                                            , member=member
                                            , isclosed=0
                                            )

    security.declareProtected( CMFCorePermissions.View, 'listUsersWithClosedReports' )
    def listUsersWithClosedReports( self ):
        """
            Returns the list of users who have closed their reports.

            Result:

                List of user id strings.
        """
        if not self.isEnabled():
            return []

        users = []
        for uname in self.listInvolvedUsers( flatten=True ):
            if not self.listAllowedResponseTypes( uname ):
                 users.append(uname)
        return users

    def _isResponseManuallyClosed( self, r ):
        """ return 1 if this response are manually closed
            (not automatically)
        """
        if r['isclosed'] != 1:
            return 0
        # if closed, test attribute of manually closed
        status = r['status']
        portal_followup = getToolByName(self, 'portal_followup')
        typeInfo = portal_followup.getResponseTypeById( status )
        return typeInfo.get('manual_report_close') is not None

    security.declareProtected( CMFCorePermissions.View, 'listFollowupTasks' )
    def listFollowupTasks(self):
        """
            Returns the followup tasks list.

            Result:

                List of user id strings.
        """
        return self.followup_tasks

    security.declareProtected( CMFCorePermissions.View, 'Respond' )
    def Respond(self, status, text = '', attachments = None, documents = None,
                close_report = None, REQUEST = None):
        """
            Adds user response to the collection.

            Arguments:

                'status' -- response type. This can one of the status values
                           defined in the task type info mapping

                'text' -- user comment

                'close_report' -- indicates whether this report is modifiable or not

                'REQUEST' -- additional parameters to be passed to the response handlers
        """
        if not self.canRespond(status):
            raise Unauthorized, 'unauthorized to respond'

        # mark task as new
        portal_followup = getToolByName( self, 'portal_followup', None )
        if portal_followup is not None:
            logger = portal_followup.getLogger()
            logger.delSeenByFor( self, uname = self.Creator() ) 

        rti = self.getResponseTypeById(status)
        if rti.get('manual_report_close', None):
            isclosed = close_report
        else:
            isclosed = 1

        # XXX wondering about situation when attachments and documents are lists

        file_ids = []
        for file in tuplify(attachments or ()):
            id = self.attachFile(file)
            if id:
                file_ids.append(id)
        file_ids = tuple(file_ids)

        uname = _getAuthenticatedUser(self).getUserName()
        layer = rti['layer']
        response_id = self.get_responses().addResponse( layer=layer
                                                      , status=status
                                                      , text=text
                                                      , member=uname
                                                      , isclosed=isclosed
                                                      , attachments=file_ids
                                                      )

        if rti.has_key('handler'):
            handler = rti['handler']
            handler_func = getattr( self, handler )
            assert callable(handler_func), 'Handler func is not callable!'

            # XXX: pass arguments to the handler function directly
            REQUEST.set( 'response_id' , response_id ) 

            handler_func(REQUEST)

        self.onRespond( REQUEST, close_report=close_report or not self.listAllowedResponseTypes(uname) )

        if documents:
            links_tool = getToolByName( self, 'portal_links' )
            for d in tuplify(documents):
                if not d.uid: continue

                links_tool.restrictedLink( self, d.uid,
                                           source_uname=uname,
                                           source_status=status,
                                           source_response_id=response_id,
                                           relation='reference' )

        self.updateIndexes( idxs=[ 'StateKeys', 'isStarted', 'isClosed'
                                 , 'PendingUsers','RespondedUsers']
                          )

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST, relative=False )

    security.declareProtected( CMFCorePermissions.View, 'KickUsers' )
    def KickUsers( self, selected_users, text, open_reports=None, REQUEST=None ):
        """
          Send and log notification to the users involved in to this task.
        """
        if not ( self.isCreator() or self.isSupervisor() ):
            raise Unauthorized, 'unauthorized to send notifications for this task'

        # Mark task as 'new' to selected users and reopen reports
        portal_followup = getToolByName( self, 'portal_followup' )
        logger = portal_followup.getLogger()
        for user in selected_users:
            logger.delSeenByFor( self, user )
            if open_reports:
                self.OpenReportFor( user )

        uname = _getAuthenticatedUser(self).getUserName()
        notification = { 'date' : DateTime()
                       , 'actor': uname
                       , 'rcpt' : selected_users
                       , 'text' : text
                       }

        self.notification_history.append( notification )
        self._p_changed = 1

        self.send_mail( selected_users, 'mail_notify_users',
                        actor=uname, message=text, open_reports=open_reports )

        if REQUEST is not None:
            message = "You have sent notification to the users"
            self.redirect( REQUEST=REQUEST, message=message )

    security.declareProtected( CMFCorePermissions.View, 'getTaskResponses' )
    def getTaskResponses(self):
        """
            Returns the ResponseCollection object
        """
        return self.get_responses()

    security.declareProtected( CMFCorePermissions.View, 'listResultCodes' )
    def listResultCodes( self, manual=0 ):
        """
            Returns information about the possible task results codes.

            Result:

                List of result code information mappings.
        """
        results = self.getTypeInfo().listResults()
        if manual:
            results = filter( lambda x: not x.get( 'disallow_manual', 0 ), results )
        return results

    security.declareProtected( CMFCorePermissions.View, 'listResponseTypes' )
    def listResponseTypes(self):
        """
          Returns a list of the user response types found in the task responses collection.

          Note:

              Should become obsolete soon.

          Result:

              List of task response type information mappings.
        """
        return [ self.getResponseTypeById(id) for id in self.get_responses().getIndexKeys('status') ]

    security.declarePrivate( 'resetSchedule' )
    def resetSchedule(self):
        """
            Restarts all schedule events associated with the task.
        """
        # NB: invoke stopSchedule is not needed, because each of three
        # method below stop own schedule event
        #self.stopSchedule()
        #self.setEffectiveDate( self.effective_date )
        #self.setExpirationDate( self.expiration_date )
        #self.setAlarm( self.alarm_settings )
        #Interface method for any type of tasks
        pass

    security.declarePrivate( 'stopSchedule' )
    def stopSchedule(self):
        """
            Disables all recurrent events associated with the task.

            Result:

                Boolean. Returns True in case every schedule element was
                successfully stopped or False otherwise.
        """
        planner = getToolByName( self, 'portal_scheduler', False )
        element_ids = filter( None, [ self._task_schedule_id
                                    , self._expiration_schedule_id
                                    , self._effective_schedule_id
                                    , self._alarm_schedule_id
                                    ] )

        planner.delScheduleElement( element_ids )
        for name in ( '_task_schedule_id'
                    , '_expiration_schedule_id'
                    , '_effective_schedule_id'
	            , '_alarm_schedule_id'):
            setattr( self, name, None)
                   
        return True

    security.declareProtected( CMFCorePermissions.View, 'listAllowedResponseTypes' )
    def listAllowedResponseTypes( self, uname=None ):
        """
            Returns a list of response types allowed to the user.

            Arguments:

                'uname' -- User id string.

            Result:

                 List of task response type information mappings.
        """
        results = []
        membership = getToolByName( self, 'portal_membership' )
        if not uname:
            user = membership.getAuthenticatedMember()
            uname = user.getUserName()
        else:
            user = membership.getMemberById( uname )
            if user is None:
                return results


        if self.isFinalized() or not self.isEnabled():
            return results

        involved_members = self.listInvolvedUsers(flatten=True)

        mates = user.listMates()
        mates.append(uname)
        for rti in self.getTypeInfo().listResponses():
           available = 1
           closed_responses = self.searchResponses( layer=rti['layer'], isclosed=1 )
           responded_members = [r['member'] for r in closed_responses]
           if uname in Set(involved_members)&Set(responded_members):
               continue
           if rti.has_key( 'condition' ):
               condition = rti['condition']
               if isinstance( condition, StringType ):
                   condition = Expression( condition )
               # XXX: FIX THIS
               if not condition( getEngine().getContext( {'here': self, 'member': uname, 'roles': mates, 'mates': mates } ) ):
                   available = 0
           if available:
               results.append( rti )
        return results

    security.declareProtected( CMFCorePermissions.View, 'getResponseTypeById' )
    def getResponseTypeById( self, id ):
        """
            Returns a response type information, given it's id.

            Arguments:

                'id' -- Id string.

            Result:

                 Response type information mapping.
        """
        for rti in self.getTypeInfo().listResponses():
            if rti['id'] == id:
                return rti
        return

    security.declareProtected( CMFCorePermissions.View, 'getResultById' )
    def getResultById( self, id ):
        """
            Returns a task result code information, given it's id.

            Task brains component defines the available task result codes.

            Arguments:

                'id' -- Code id string.

            Result:

                Result code information mapping.

        """
        for result in self.listResultCodes():
            if result['id'] == id:
                return result
        raise KeyError, id

    security.declareProtected( CMFCorePermissions.View, 'searchResponses' )
    def searchResponses( self, **kw ):
        """
            Returns user responses list according to the given query.

            See CollectionResponse.searchResponses for details.
        """
        return self.get_responses().searchResponses( **kw )

    security.declareProtected( CMFCorePermissions.View, 'getHistory' )
    def getHistory( self ):
        """
            Returns the notifications history.
        """
        return self.notification_history

    security.declareProtected( CMFCorePermissions.View, 'getSourceAction' )
    def getSourceAction( self ):
        return self.task_template_id

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setSourceAction' )
    def setSourceAction( self, action ):
        self.task_template_id = action

    security.declareProtected( CMFCorePermissions.View, 'getFinalizationMode' )
    def getFinalizationMode( self ):
        return getattr( self, 'finalization_mode', None ) or 'manual_creator'


    security.declareProtected( CMFCorePermissions.View, 'edit' )
    def edit( self, REQUEST=None, **kw ):
        changes = self._edit( **kw )
        self.updateIndexes()

        if len( changes ) and self.isEnabled():
            self.Enable()
            # Notify the involved users via email
            notify_list = self.listInvolvedUsers( flatten=True )
            supervisor = self.Supervisor()
            if supervisor and supervisor not in notify_list:
               notify_list.append( supervisor )

            self.send_mail( notify_list, 'mail_changes', **changes )

    def _edit( self,
               title=None,
               involved_users=None,
               description=None,
               supervisor=None,
               effective_date=None,
               expiration_date=None,
               alarm_settings=None,
               finalization_mode=None,
            ):
        """
            Changes task properties and sends mail notfications.
        """
        portal_followup = getToolByName( self, 'portal_followup' )
        logger = portal_followup.getLogger()
        logger.delSeenByFor( self )

        changes = {}

        if title is not None and self.Title() != title:
            self.setTitle(title)
            changes['task_title'] = self.Title()

        if description is not None and self.Description() != description:
            self.setDescription( description )
            changes['task_description'] = self.Description()

        if alarm_settings != self.alarm_settings:
            self.setAlarm( alarm_settings )
            changes['task_alarm'] = alarm_settings

        if involved_users is not None:
            flatten_users = flattenUsers( self, involved_users )
            old_flatten_users = self.listInvolvedUsers( flatten=True )
            excluded_users = filter( lambda x, t=flatten_users: x not in t, old_flatten_users )
            included_users = filter( lambda x, t=old_flatten_users: x not in t, flatten_users )

            self.setInvolvedUsers( involved_users )

            if excluded_users or included_users:
                changes.update( {'task_included_users': included_users,
                                 'task_excluded_users': excluded_users,
                                } )

        if supervisor is not None:
            if  self.Supervisor() != supervisor:
                changes['task_supervisor'] = supervisor

            self.setSupervisor( supervisor )

        if expiration_date is not None and self.expires() != expiration_date:
            self.setExpirationDate( expiration_date )
            changes['task_expiration_date'] = self.expires()

        if effective_date is not None and self.effective() != effective_date:
            self.setEffectiveDate( effective_date )
            changes['task_effective_date'] = self.effective()

        if finalization_mode:
            self.finalization_mode = finalization_mode

        return changes

    def send_mail( self, members, template_name, **kwargs ):
        """
            Sends e-mail notification to the selected users.

            Arguments:

                'members' -- List of user id strings.

                'template_name' --  DTML mail template id string. Mail templates
                                    objects are defined within the task brains
                                    component.

                '**kwargs' -- Additional keyword parameters to be passed to the
                              mail template.
        """
        template = getattr( self, template_name )
        if isinstance( template, StringType ):
            template = getattr( self, template )

        links = getToolByName( self, 'portal_links' )
        task_url = links.absolute_url( action='locate', params={'uid':self.getUid()}, canonical=1 )

        task_links = []
        task_attachments = []
        if kwargs.has_key( 'response' ):
            response = kwargs['response']
            slinks = links.searchLinks( source=self,
                                        source_uname=response['member'],
                                        source_status=response['status'],
                                        source_response_id=response['response_id'],
                                      )
            for link in slinks:
                obj = link.getObject().getTargetObject()
                if obj:
                    url = links.absolute_url( action='locate', params={'uid':obj.getUid()}, canonical=1 )
                    task_links.append( url )

            if response['attachments']:
                for file_id in response['attachments']:
                    task_attachments.append( self.absolute_url( action=file_id ) )

        membership = getToolByName( self, 'portal_membership' )
        
        kwargs.setdefault( 'task_url', task_url )
        kwargs.setdefault( 'task_title', flattenString( self.Title() ) )
        kwargs.setdefault( 'task_links', task_links )
        kwargs.setdefault( 'task_attachments', task_attachments )
        kwargs.setdefault( 'creator', membership.getMemberName(self.Creator()) )


        members = [ user for user in members if user and not membership.isUserLocked( user ) ]

        mail = getToolByName( self, 'MailHost' )
        mail.sendTemplate( template, members, restricted=Trust,
                           raise_exc=False, **kwargs )

    def onFinalize(self, REQUEST=None, result_code=None):
        self._finalize(result_code or REQUEST.get('result_code'))

    def onRespond( self, REQUEST=None, **kw ):
        # TODO: Implement task result code determination rules, 'success' code is not always eligible.
        if not self.isFinalized() and kw['close_report'] and \
           ( self.getFinalizationMode() == 'auto_any_user' or \
             self.getFinalizationMode() == 'auto_every_user' and self.isClosed()
           ):
            self.Finalize(TASK_RESULT_SUCCESS, Trust)

    security.declarePrivate( 'Alarm' )
    def Alarm( self ):
        """
            Reminders users about task.

            The method is called automatically by the portal scheduling
            service.
        """
        if self.isFinalized() or not self.isEnabled():
            return

        exclude_list = self.listUsersWithClosedReports()
        notify_list = [ user for user in self.InvolvedUsers()
                        if user not in exclude_list ]
        notify_list.append( self.Creator() )
        if self.Supervisor():
            notify_list.append( self.Supervisor() )
        host = getToolByName( self, 'MailHost' )
        host.sendTemplate( self.mail_alarm, uniqueValues( notify_list ),
                           raise_exc = False )

    security.declarePrivate( 'setAlarm' )
    def setAlarm( self, settings ):
        self.alarm_settings = settings
        if settings is None:
            return

        # build TE from alarm settings
        type, value = settings['type'], settings['value']
        if type == 'percents':
            date = self.expiration_date - (self.expiration_date - self.effective_date) * value / 100
            te = DateTimeTE( date )

        elif type == 'periodical':
            period_type = settings['period_type']
            if period_type == 'hours':
                te = UniformIntervalTE( value * 3600, self.effective_date )
            elif period_type == 'days':
                # XXX UniformIntervalTE easier than DailyTE
                te = UniformIntervalTE( value * 3600 * 24, self.effective_date )
            elif period_type == 'months':
                te = MonthlyByDateTE(value,
                                     [self.effective_date.day()],
                                     self.effective_date)

        elif type == 'custom':
            te = UnionTE( map( DateTimeTE, value ))

        scheduler = getToolByName( self, 'portal_scheduler', None )
        if scheduler is not None and self._alarm_schedule_id:
            scheduler.delScheduleElement( self._alarm_schedule_id )

        self._alarm_schedule_id = scheduler.addScheduleElement \
                                      ( self.Alarm,
                                        temporal_expr = te,
                                        title = "[Alarm] '%s" % self.Title(),
                                      )

    security.declareProtected( CMFCorePermissions.View, 'getLeveledTaskTree' )
    def getLeveledTaskTree( self, root=0, level=0 ):
        """
        """
        current_task = root and self.findRootTask() or self
        lev_list = [current_task]
        bound_tasks = current_task.followup.getBoundTasks()
        for t in bound_tasks:
            deep_tasks = t.getLeveledTaskTree(level=level+1)
            lev_list += deep_tasks
        return lev_list

    security.declareProtected( CMFCorePermissions.View, 'getLevel' )
    def getLevel( self ):
        """
        """
        root_id = self.findRootTask().getId()
        task = self
        level = 0
        while task.getId() != root_id:
            task = task.aq_parent
            level+=1
        return level

    #redefines TaskItem methods, why?
    setEffectiveDate  = IndexableMethod( ContentBase.setEffectiveDate
                                       , effective_date=['effective'] )
    setExpirationDate = IndexableMethod( ContentBase.setExpirationDate
                                       , expiration_date=['expires'] )

    setSupervisor = IndexableTaskMethod( setSupervisor, supervisor=['Supervisor', 'isClosed'] ) 
    setInvolvedUsers = IndexableTaskMethod( setInvolvedUsers, involved_users=['InvolvedUsers','isStarted', 'isClosed'] ) 
    Enable = IndexableTaskMethod( Enable, enabled=['isEnabled'] ) 
    Disable = IndexableTaskMethod( Disable, enabled=['isEnabled'] ) 
    _finalize = IndexableTaskMethod( _finalize, finalized=['isFinalized', 'isStarted'] ) 

    #Respond = IndexableTaskMethod( Enable, finalized=['isFinalized'] ) 

InitializeClass( TaskItemBase )

def flattenUsers( self, *args, **kw ):
    membership = getToolByName( self, 'portal_membership' )
    return membership.listPlainUsers( *args, **kw )

