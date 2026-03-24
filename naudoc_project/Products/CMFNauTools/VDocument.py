"""Business Procedure content class.

$Id: VDocument.py,v 1.72 2006/04/28 07:44:21 ynovokreschenov Exp $
"""
__version__ = '$Revision: 1.72 $'[11:-2]


import Globals

from Acquisition import aq_self, aq_base, aq_parent, aq_get
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from zExceptions import Unauthorized

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser, _checkPermission

import Config, Features
from Config import Roles
from GuardedTable import GuardedTable, GuardedEntry
from Features import createFeature
from File import addFile
from HTMLDocument import HTMLDocument
from SimpleObjects import Persistent
from TaskItem import TASK_RESULT_SUCCESS, TASK_RESULT_CANCELLED, TASK_RESULT_FAILED
from Utils import cookId, InitializeClass
from SecureImports import refreshClientFrame


VDocumentType = { 'id'             : 'Business Procedure'
                , 'meta_type'      : 'Business Procedure'
                , 'title'          : "Business Procedure"
                , 'description'    : "Business Procedure"
                , 'icon'           : 'virt_doc_icon.gif'
                , 'product'        : 'CMFNauTools'
                , 'factory'        : 'addVDocument'
                , 'immediate_view' : 'vdocument_options_form'
                , 'permissions'    : ( CMFCorePermissions.AddPortalContent, )
                , 'actions'        : ( { 'id'            : 'view'
                                       , 'name'          : "View"
                                       , 'action'        : 'vdocument_view'
                                       , 'permissions'   : (CMFCorePermissions.View,)
                                       },
                                       { 'id'            : 'edit'
                                       , 'name'          : "Properties"
                                       , 'action'        : 'vdocument_options_form'
                                       , 'permissions'   : (CMFCorePermissions.ModifyPortalContent,)
                                       },
                                     )
                }

ENTRY_ENABLED   = 'enabled'
ENTRY_FINALIZED = 'finalized'
ENTRY_ABANDONED = 'abandoned'
ENTRY_ROLLBACK  = 'rollback'

class VGuardedEntry(GuardedEntry):

    _class_version = 1.38

    _properties = GuardedEntry._properties + (
                    { 'id':'step', 'type':'int', 'mode':'w', 'default':1 },
                    { 'id':'state', 'type':'string', 'mode':'w', 'default':ENTRY_ENABLED },
                    { 'id':'chief_user', 'type':'string', 'mode':'w', 'default':'' },
                  )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        GuardedEntry.__init__(self, id, title)
        self.passed_steps = []

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not GuardedEntry._initstate( self, mode ):
            return False

        if getattr(self, 'step', None) is None:
            self.step = 1

        if getattr(self, 'state', None) is None:
            self.state = ENTRY_ENABLED

        if getattr(self, 'passed_steps', None) is None:
            self.passed_steps = range(1, self.step)

        if not hasattr(self, 'chief_user'):
            self.chief_user = None

        return True

    #__getattr__ = GuardedEntry.__getattr__

    def index_html( self, REQUEST, RESPONSE ):
        """
            Returns the entry contents.
        """
        return self.vdocument_entry_form( self, REQUEST, RESPONSE )

    document_follow_up_form = index_html

    security.declareProtected(CMFCorePermissions.View, 'isEnabled')
    def isEnabled(self):
        """
            Checks whether this entry is enabled.

            Result:

                Boolean.
        """
        return self.getProperty('state') == ENTRY_ENABLED

    security.declareProtected(CMFCorePermissions.View, 'isFinalized')
    def isFinalized(self):
        """
            Checks whether this entry is finalized.

            Result:

                Boolean.
        """
        return self.getProperty('state') == ENTRY_FINALIZED

    security.declareProtected(CMFCorePermissions.View, 'isAbandoned')
    def isAbandoned(self):
        """
            Checks whether this entry is abandoned.

            Result:

                Boolean.
        """
        return self.getProperty('state') == ENTRY_ABANDONED

    def changeState(self, state, comment=''):
        """
          Switches entry state.

          Allowed 'state' values:
          'enabled' - entry processing is in progress
          'finalized' - entry processing complete
          'abandoned' - entry processing was interrupted
        """
        self._updateProperty( 'state', state )
        self.reindex( idxs=['State'] )
        self.updateHistory( action=state, text=comment )

    def isSetAllowed(self, name):
        step = self.getStep()
        return step and step.isUserAllowed() and name in step.listWritableColumnIds()

    def isGetAllowed(self, name):
        """
        """
        if name in self.getTable().listKeyColumns():
            return True

        if self.isSetAllowed(name):
            return True

        if _checkPermission(CMFCorePermissions.ManagePortal, self):
            return True

        if Roles.Editor in self.getTable().user_roles():
            return True

        for step_id in range(self.step):
            step = self.getStep(step_id + 1)
            if step.isUserAllowed() and (name in step.listReadableColumnIds() or \
                                         name in step.listWritableColumnIds()):
                return True

        return False

    def setChiefUser(self, chief_user):
        """
            Sets up the entry chief user.

            Arguments:

                'chief_user' -- Member id string.
        """
        self._updateProperty( 'chief_user', chief_user )

    def resetChiefUser(self):
        """
            Resets the entry chief user.
        """

        self._updateProperty('chief_user', '' )

    security.declareProtected(CMFCorePermissions.View, 'getChiefUser')
    def getChiefUser(self):
        """
            Returns the entry chief user.

            Result:

                Member id string.
        """
        return self.getProperty('chief_user')

    security.declareProtected(CMFCorePermissions.View, 'getStep')
    def getStep(self, step_id=Missing):
        """
            Returns the current entry's step. ? ? ? for what step_id
        """
        step_id = step_id or self.getStepId()
        return self.parent().getStepById(step_id)

    security.declareProtected(CMFCorePermissions.View, 'getStepId')
    def getStepId(self):
        """
        """
        return self.getProperty('step')

    security.declareProtected(CMFCorePermissions.View, 'getState')
    def getState(self):
        """
        """
        return self.getProperty('state')

    # Alias for catalog indexing
    StepId = getStepId
    State = getState

    security.declareProtected(CMFCorePermissions.View, 'PassedSteps')
    def PassedSteps(self):
        return self.passed_steps

    def switchStep(self, new_step_id, chief_user=None, comment=''):
        """
           Changes the current entry step and sets up the chief user.

           Arguments:

               'new_step_id' -- New entry step id. None value indicates that entry
                                should be switched to the next step.

               'chief_user' -- Entry chief user id.

               'comment' -- User comment.
        """
        new_step_id = int( new_step_id or self.getStepId() )
        new_step = self.getStep( new_step_id )

        if new_step_id != self.step and self.step not in self.passed_steps:
            self.passed_steps.append( self.step )
            self._p_changed = 1

        state = ENTRY_ENABLED

        if new_step is not None:
            self.step = new_step_id

            self.setChiefUser( chief_user )
            if chief_user:
                # Create task
                msgtool = getToolByName(self, 'msg' )
                expiration_date = DateTime( new_step.getDuration() + float(DateTime()) )
                self.followup.createTask( title="%s / %s %s" % (self.Title(), msgtool('Step'), new_step.Title()),
                                          involved_users=[chief_user],
                                          description=comment,
                                          expiration_date=expiration_date,
                                          brains_type='directive',
					  plan_time = 0
                                        )

                # Send a mail to the users involved into the next step
                host = getToolByName(self, 'MailHost' )
                host.sendTemplate( 'vdocument_chief_notify', [chief_user]
                                 , REQUEST=aq_get(self, 'REQUEST')
                                 , step_title = new_step.Title()
                                 , vdocument_title = self.parent().Title()
                                 , vdocument_url = self.absolute_url()
                                 )
        elif new_step_id in self.passed_steps:
            state = ENTRY_ROLLBACK

            for task in self.followup.objectValues():
                task.Finalize( TASK_RESULT_CANCELLED )
        else:
            for task in self.followup.objectValues():
                task.Finalize( TASK_RESULT_SUCCESS )

            self.resetChiefUser()
            state = ENTRY_FINALIZED

        self.changeState( state, comment )
        self.reindex( idxs=['State', 'StepId'] )

    def updateHistory( self, **kwargs ):
        """
            Adds record to the changes history.

            Arguments:

               'kwargs' -- keyword arguments, mapping
        """
        kwargs.setdefault( 'step', self.step )
        GuardedEntry.updateHistory( self, **kwargs )

    security.declarePublic('allowed')
    def allowed(self):
        """
          Checks whether the current user is able to manage
          this entry
        """
        return self.getStep().isUserAllowed() or\
               _checkPermission(CMFCorePermissions.ModifyPortalContent, self.parent() )

    def SearchableText( self ):
        return ' '.join( map( str, self.getData(self.listKeyColumns()).values() ) )

    def _containment_onDelete( self, item, container ):
        """
            Removes and uncatalogs all nested tasks.
        """
        self.followup.manage_beforeDelete( self.followup, self)


InitializeClass( VGuardedEntry )


class VStep(Persistent, Implicit):
    _class_version = 1.38

    security = ClassSecurityInfo()
    security.setDefaultAccess(1)

    def __init__(self, table, title=''):
        Persistent.__init__( self )
        self.title = title
        self._table = table
        self.allowed_members = []
        self.allowed_groups = []

        self.writable_columns = []
        self.readable_columns = []

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not Persistent._initstate( self, mode ):
            return False

        if getattr(self, 'rollback_steps', None) is None:
            self.rollback_steps = []

        if getattr(self, 'duration', None) is None:
            self.duration = 0

        return True

    security.declareProtected(CMFCorePermissions.View, 'Title')
    def Title(self):
        return self.title

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setTitle')
    def setTitle(self, title):
        self.title = title

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setWritableColumns')
    def setWritableColumns(self, columns):
        """
            Specifies writable columns of the current step.

            Arguments:

                'columns' -- List of column id strings.
        """
        self.writable_columns = columns

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setReadableColumns')
    def setReadableColumns(self, columns):
        """
            Specifies readable columns of the current step.

            Arguments:

                'columns' -- List of column id strings.
        """
        self.readable_columns = columns

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setDuration')
    def setDuration(self, duration):
        """
            Sets up the step duration.

            Arguments:

                'duration' -- Integer. Step duration in seconds.
        """
        self.duration = duration

    security.declareProtected(CMFCorePermissions.View, 'getDuration')
    def getDuration(self):
        """
            Returns the step duration.

            Result:

                Integer. Step duration in seconds.
        """
        return self.duration

    security.declareProtected(CMFCorePermissions.View, 'listWritableColumnIds')
    def listWritableColumnIds(self):
        """
            Returns a list of step's writable columns.

            Result:

                List of column id strings.
        """
        return self.writable_columns

    security.declareProtected(CMFCorePermissions.View, 'listReadableColumnIds')
    def listReadableColumnIds(self):
        """
            Returns a list of step's readable columns.

            Result:

                List of column id strings.
        """
        return self.readable_columns

    security.declareProtected(CMFCorePermissions.View, 'listAllowedMembers')
    def listAllowedMembers(self):
        """
            Returns a list of users involved into the step.

            Result:

                List of member id strings.
        """
        membership = getToolByName(self._table, 'portal_membership')
        return membership.expandUserList(self.allowed_groups, self.allowed_members)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setRollbackSteps')
    def setRollbackSteps( self, rollback_steps ):
        """
            Sets up the list of the procedure steps which are allowed to be used for rollback.

            Arguments:

                'rollback_steps' -- List of step id strings.
        """
        self.rollback_steps = rollback_steps

    security.declareProtected(CMFCorePermissions.View, 'listRollbackSteps')
    def listRollbackSteps( self ):
        """
            Returns the list of the procedure steps which are allowed to be used for rollback.

            Result:

                List of step id strings.
        """
        return self.rollback_steps

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setAllowedMembers')
    def setAllowedMembers(self, members):
        """
            Sets up the list of members involved into the step.

            Arguments:

                'members' -- List of member id strings.

            Enumerated members are automatically granted with the Reader local
            role.
        """
        self.allowed_members = members

        # XXX: Use shortcuts instead

        # Grant access to all involved users and groups
        if self.allowed_members:
            for u_id in self.allowed_members:
                if 'Owner' not in self.get_local_roles_for_userid(u_id):
                    self.manage_setLocalRoles(u_id, ['Reader'])

        self.reindexObject(idxs=['allowedRolesAndUsers'])

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setAllowedGroups')
    def setAllowedGroups(self, groups):
        """
            Sets up the list of members involved into the step and grants local roles.

            Note:

                This method should be deprecated soon.
        """
        self.allowed_groups = groups

        if self.allowed_groups:
            for g_id in self.allowed_groups:
                self.manage_setLocalGroupRoles(g_id, ['Reader'])
        self.reindexObject()

    security.declareProtected(CMFCorePermissions.View, 'isUserAllowed')
    def isUserAllowed(self):
        """
            Checks whether the user is currently involved into the process.

            Result:

                Boolean.
        """
        uname = _getAuthenticatedUser(self).getUserName()
        return uname in self.listAllowedMembers()

InitializeClass( VStep )

def addVDocument(self, id, title='', description=''):
    """ Adds vdocument """
    self._setObject(id, VDocument( id, title=title, description=description))

class VDocument(GuardedTable):
    """ Business Procedure type """
    _class_version = 1.228

    meta_type = 'Business Procedure'
    portal_type = 'Business Procedure'

    security = ClassSecurityInfo()

    __implements__ = ( createFeature('isBusinessProcedure')
                     , Features.isPortalContent
                     , GuardedTable.__implements__
                     )

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not GuardedTable._initstate( self, mode ):
            return False

        if getattr(self, 'portal_type', 'Virtual Document') == 'Virtual Document':
            self.portal_type = self.meta_type

        if getattr(self, 'doc_templates', None) is None:
            self.doc_templates={}

        if getattr(self, 'key_columns', None) is None:
            self.key_columns=[]

        if getattr(self, 'steps', None) is None:
            self.steps = []

        for step in self.steps:
            if getattr(step, '_table', None) is None:
                step._table = self

        if hasattr( self, '_kw_list'):
            delattr( self, '_kw_list')

        return True

    security.declarePublic( 'enumerateIndexes' )
    def enumerateIndexes( self ):
        """
          Returns the catalog indexes list.

          Result:

            A list of ( index_name, type ) pairs for the initial index set.
        """
        return GuardedTable.enumerateIndexes(self) + \
               ( ('StepId', 'FieldIndex')
               , ('State', 'FieldIndex')
               )

    def executeQuery( self, REQUEST=None, **kwargs ):
        """
        """
        REQUEST = REQUEST or aq_get(self, 'REQUEST') or Globals.get_request()

        uid = self.getUid()
        session = REQUEST['SESSION']

        if REQUEST.has_key('apply_filter'):
            filter_editable = REQUEST.get('filter_editable', False)
            show_finalized = REQUEST.get('show_finalized', False)
        else:
            filter_editable = session.get( (uid, 'filter_editable'), False )
            show_finalized = session.get( (uid, 'show_finalized'), False )

        kwargs.setdefault( 'State', ['enabled', 'rollback'] + (show_finalized and ['abandoned', 'finalized'] or []) )
        kwargs.setdefault( 'StepId', filter_editable and self.listAllowedStepKeys() or [])
        results = GuardedTable.executeQuery( self, REQUEST, **kwargs)

        for name in 'filter_editable', 'show_finalized':
            # to use in next visit
            session.set((uid, name), locals()[name])
            # to use in dtml
            REQUEST.set(name, locals()[name])

        return results

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setKeyColumn' )
    def setKeyColumn( self, id ):
        """
            Sets up the key column, given it's id.

            Arguments:

                'id' -- Column id string.

            Key columns are displayed in the summary table and help user
            to identify entry.
        """
        if id not in self.key_columns:
            self.key_columns.append(id)
            self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'resetKeyColumn' )
    def resetKeyColumn( self, id ):
        """
            Removes the key column, given it's id.

            Arguments:

                'id' -- Column id string.
        """
        if id in self.key_columns:
            self.key_columns.remove(id)
            self._p_changed = 1

    security.declareProtected( CMFCorePermissions.View, 'listKeyColumns' )
    def listKeyColumns( self ):
        """
            Returns a list of key column ids.

            Result:

                List of column id strings.
        """
        return self.key_columns

    def listColumnsMetadata( self):
        """
        """
        columns = [ self.getColumnById( key, False) for key in self.listKeyColumns()]
        return [ col.getColumnDescriptor() for col in columns ]

    security.declareProtected( CMFCorePermissions.View, 'addEntry' )
    def addEntry( self, data=None, REQUEST=None ):
        """
            Adds a new entry to the table.

            Arguments:

              'data' -- Dictionary representing entry contents.

              'REQUEST' -- REQUEST object containing the form data to be
                           used as the entry contents. This argument is
                           effective only if the 'data' parameter is None.

             User is able to set only those entry fields that are marked as
             writable in a given step.
        """
        if not self.getStepById(1).isUserAllowed():
            raise Unauthorized

        if data is None and REQUEST is not None:
            # Get entry info from REQUEST and place it into
            # the 'data' vocabulary
            expected_columns = self.getStepById(1).listWritableColumnIds()
            data = self.parseEntryForm(expected_columns, REQUEST)

        entry = self._store(data, VGuardedEntry)
        followup = getToolByName(self, 'portal_followup')
        followup._createFollowupFor(entry)

        uname = _getAuthenticatedUser(self).getUserName()
        entry.switchStep(1, uname)

        if REQUEST is not None:
            refreshClientFrame( 'followup_menu' )
            self.redirect( REQUEST=REQUEST, message='Entry added' )

    security.declareProtected( CMFCorePermissions.View, 'editEntry' )
    def editEntry( self, record_id, data=None, comment='', REQUEST=None, redirect=1 ):
        """
           Changes the procedure entry.

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

             User is able to change only those entry fields that are marked as
             writable in a given step.
        """
        entry = self.getEntryById(record_id)
        entry.validate()

        if data is None and REQUEST is not None:
            # Get entry info from REQUEST and place it into
            # the 'data' vocabulary
            step_id = entry.getStepId()
            expected_columns = self.getStepById(step_id).listWritableColumnIds()
            data = self.parseEntryForm(expected_columns, REQUEST)

        self._edit(data, record_id)

        entry.updateHistory(text=comment)
        entry.reindexObject()

        if redirect and REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry updated')

    security.declareProtected( CMFCorePermissions.View, 'nextEntryStep' )
    def nextEntryStep( self, entry_id, comment='', chief_user=None, REQUEST=None):
        """
            Switches entry to the next step.

            Arguments:

                'record_id' -- Entry id string.

                'comment' -- User comment.

                'chief_user' -- Step chief user member id.

        """
        entry = self.getEntryById( entry_id )
        entry.validate()

        entry.switchStep( entry.getStepId() + 1, chief_user, comment )

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry step changed' )

    security.declareProtected( CMFCorePermissions.View, 'entryRollback' )
    def entryRollback( self, record_id, rollback_step, comment='', chief_user=None, REQUEST=None):
        """
            Rollbacks entry by switching it to the given step.

            Arguments:

                'record_id' -- Entry id.

                'rollback_step' -- An id of the step to rollback. Only steps
                                   previously defined as rollback steps are
                                   accepted.

                'comment' -- User comment.

                'chief_user' -- Step chief user member id.
        """
        entry = self.getEntryById(record_id)
        entry.validate()

        entry.switchStep(rollback_step, chief_user, comment)

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry step changed' )

    security.declareProtected( CMFCorePermissions.View, 'abandonEntry' )
    def abandonEntry( self, entry_id, comment='', REQUEST=None ):
        """
          Interrupts entry processing
        """
        entry = self.getEntryById( entry_id)
        entry.validate()

        entry.changeState(ENTRY_ABANDONED, comment)

        for task in entry.followup.objectValues():
            task.Finalize( TASK_RESULT_FAILED )

        if REQUEST is not None:
            self.redirect( REQUEST=REQUEST, message='Entry abandoned' )

    def delColumn( self, id ):
        """
          Removes entry keys
        """
        if id in self.listKeyColumns():
            self.resetKeyColumn(id)

        GuardedTable.delColumn(self, id)

    def getStepById(self, id):
        """
            Returns the step, given it's id.

            Arguments:

                'id' -- Step id.

            Result:

                Step class instance.
        """
        steps = self.listStepValues()
        id = int(id) - 1
        try:
            return steps[id]
        except IndexError:
            pass

    def addStep(self, title):
        """
            Adds step to the process queue.

            Arguments:

                'title' -- Step title.
        """
        self.steps.append( VStep( self, title ) )
        self._p_changed = 1

    def delStep(self, id):
        """
            Removes step from the process queue.

            Arguments:

                'id' -- Step id.
        """
        id = int(id) - 1
        try:
            del self.steps[id]
            self._p_changed = 1
        except IndexError:
            pass # why pass?
        #XXX what about entries ???

    def swapSteps(self, id1, id2):
        """
        """
        steps = self.steps
        steps_count = len(steps)
        id1 = id1 - 1
        id2 = id2 - 1

        if id2 >= steps_count:
            id2 = id2 - steps_count

        steps[id1], steps[id2] = steps[id2], steps[id1]
        self._p_changed = 1

    def moveStepUp(self, id):
        """
            Moves step up in the process queue.

            Arguments:

                'id' -- Step id.
        """
        id = int(id)
        return self.swapSteps(id, id-1)

    def moveStepDown(self, id):
        """
            Moves step down in the process queue.

            Arguments:

                'id' -- Step id.
        """
        id = int(id)
        return self.swapSteps(id, id+1)

    def listStepValues(self, wrapped=True):
        """
          Returns a list of step objects
        """
        return [ wrapped and step.__of__(self) or step for step in self.steps ]

    def listAllowedStepKeys(self):
        """
            Returns a list of a step ids allowed for the current user.
        """
        steps = self.listStepValues()
        return [ step_id+1 for step_id in range( len(steps) ) if steps[step_id].isUserAllowed() ]

    def listWritableColumnIds( self, step_id=1 ):
        """
            Returns a list of writable columns.

            Result:

                List of column id strings.
        """
        step = self.getStepById(step_id)
        return step and step.isUserAllowed() and step.listWritableColumnIds() or []

    def listReadableColumnIds( self, step_id=1 ):
        """
            Returns a list of readable columns.

            Result:

                List of column id strings.
        """
        step = self.getStepById(step_id)
        return step and step.isUserAllowed() and step.listReadableColumnIds() or []

    security.declareProtected( CMFCorePermissions.View, 'saveAs' )
    def saveAs(self, title, description, report_generator, record_id, REQUEST):
        """
            Creates an HTMLDocument containing a report generated with report wizard.

            Arguments:

                'title' -- Report document title.

                'description' -- Report document description.

                'report_generator' -- DTML method that is used to generate a
                                      report using the entry data.


                'record_id' -- Entry id string.

        """
        folder = self.parent()

        id = cookId( folder, title=title, prefix='report')
        html_text = apply(report_generator, (self, REQUEST), self.getEntryById(record_id).getData())
        o = HTMLDocument(id, title, 'html', html_text, description=description)

        folder._setObject( id, o)

        return folder._getOb( id).absolute_url()

    security.declareProtected( CMFCorePermissions.View, 'listAttachments' )
    def listAttachments( self ):
        """
            Lists file attachments contained in the procedure object.

            Note:

                This method should be deprecated soon.

        """
        return [ attach for attach in self.objectItems()
                 if attach[0] not in ['followup',] and self.doc_templates.has_key( attach[0])
               ]

    security.declareProtected( CMFCorePermissions.View, 'removeFile' )
    def removeFile( self, id ):
        """
            Removes file attach with the given id

            Note:

                This method should be deprecated soon.

        """
        if self.doc_templates.has_key(id):
            if hasattr( aq_base( self), id):
                self.manage_delObjects( id )
            del self.doc_templates[id]
            self._p_changed = 1

    security.declareProtected( CMFCorePermissions.View, 'addDocTemplate')
    def addDocTemplate( self, file=None, title=None, **kw ):
        """
            Attaches a file to the document

            Note:

                This method should be deprecated soon.
        """
        fileid = addFile( self, None, file, title, **kw )
        if fileid:
            self.doc_templates[fileid] = 1
            self._p_changed = 1
        return fileid

InitializeClass(VDocument)


def initialize( context ):
    # module initialization callback

    context.registerContent( VDocument, addVDocument, VDocumentType )
