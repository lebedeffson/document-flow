"""

Docflowlogic class

Implement docflow, i.e. actions over document on when transition (or other) events
happened.

$Editor: inemihin $
$Id: DocflowLogic.py,v 1.40 2008/05/20 12:01:01 oevsegneev Exp $
"""
__version__ = '$Revision: 1.40 $'[11:-2]

from types import StringType

from Acquisition import Implicit, aq_base

from Products.CMFCore.WorkflowCore import ObjectMoved, ObjectDeleted
from Products.CMFCore.utils import getToolByName

import Features
from Exceptions import SimpleError
from TaskDefinitionAbstract import ActionContext
from SimpleObjects import Persistent
from Utils import InitializeClass, getObjectImplements
from WorkflowTool import WorkflowMethod

class DocflowLogic( Persistent, Implicit ):
    """
        DocflowLogic class

        Handled events:

            - onBeforeTransition
            - onAfterTransition
            - onFinalizeTask

        Logic:

           - onBeforeTransition:
               1. take listTaskTemplateForDie for new state
               2. if doc have task from that list, off flag 'automated_task' (i.e. task_template_id),
                  finalize that task, and set result code (if not finalized)

           - onAfterTransition:
               1. take task templates needed for activate for transition,
               2. activate all them

           - onFinalizeTask:
               1. are finalized task automated? if no - exit
               2. take list of result codes of finalized automated-task of document
               3. take transition from matrix "result-codes -> transition"
                  if exists - make this transition

         Diagrams:

             'docflow-class_diagram.png' -- UML diagram of docflow classes

    """
    #-----[ ON BEFORE TRANSITION ]-----
    def onBeforeTransition( self, ob, action ):
        """
            handler-function are called before transition

            Arguments:

                'ob' -- object in context of which happened transition (generally HTMLDocument)

                'action' -- transition id

            Performs DocFlow action for transition.

                1. check object (_isObjectValid)
                1.5 validate state mandatory attributes
                2. take list of task for finalize in new state
                3. for each automated task of document,
                   3.1  if task are included in list:
                     - make flag 'not automated'
                     - finalize task (if not)

        """
        # 1. check object
        if not self._isObjectValid( ob ):
            return

        if isinstance( action, WorkflowMethod ):
            action = action.getAction()

        # 1.5 validate state mandatory attributes
        state_def = ob.getCategory().getWorkflow()._getWorkflowStateOf( ob )
        for attr, value in ob.listCategoryAttributes():
            if state_def.isAttributeMandatory(attr.getId()) and attr.isEmpty(value):
                raise SimpleError("Value of '%(attr_title)s' attribute is empty. Transition not permitted.",
                                  attr_title = attr.Title())

        # Heading support
        if not getObjectImplements( ob, 'isHTMLDocument' ):
            return

        # 2. take listTaskTemplateForDie for new state
        category_id = self._getCategoryOfObject( ob )
        state = self._stateWhereDocumentGo( ob, action )
        listTaskForDie = self._getListTaskForDieForState( category_id, state )    # list of template's id, with result code
        self._log( function='onBeforeTransition', text='listTaskForDie:', params=listTaskForDie )

        # 3. if doc have task from that list, off flag 'automated_task' (i.e. task_template_id)
        #    finalize that task, and set result code
        for task in self._getTaskAutomatedOfDocument( ob ):
            template_id = self._getTaskTemplateId( task )
            if template_id in listTaskForDie.keys():
                self._log( function='onBeforeTransition', text='make this task not automated:', params=task.id )
                self._makeTaskNotAutomated( task )
                if not task.isFinalized():
                    self._log( function='onBeforeTransition', text='finalize this task:', params=task.id )
                    self._finalizeTask( task, listTaskForDie[template_id] ) # result_code

    #-----[ ON AFTER TRANSITION ]-----
    def onAfterTransition( self, ob, action ):
        """
            handler-function are called after transition.

            Arguments:

                'ob' -- object in context of which transition happened (generally HTMLDocument)

                'action' -- transition id

            Performs:

                1. get action templates for activating in new state
                2. for each action template - activate it
        """
        if not self._isObjectValid( ob ):
            return

        if isinstance( action, WorkflowMethod ):
            action = action.getAction()

        # 1. take task templates needed for activations for transition
        #    activate all them
        transition = action

        category = ob.getCategory()
        actionContainer = category.taskTemplateContainer
        context = ActionContext()

        moved = False
        for template_id in category.transition2TaskTemplate.get( transition, [] ):
            try:
                actionContainer.activateTaskTemplate( template_id, ob, transition, context )
            except ObjectMoved, err:
                ob = err.getNewObject()
                moved = True
            except ObjectDeleted:
                break
      
        if moved:
            # re-raise
            raise ObjectMoved( ob )

    def processAutomatedTransitionsFor( self, obj ):
        """
            Event-handler function for any state changes of an object.

            Arguments:

                'obj'           --  an object instance.

                'version_id'    --  (optional) object version id string.
        """
        tt_id = self._getTaskTemplateId( obj )
        if not tt_id: return

        if hasattr( obj, 'implements' ) and obj.implements( 'isTaskItem' ):
            # suppose 'obj' is a finalized task
            target = obj.getBase()
            target_version_id = getattr( obj, 'version_id', None )
            result_code = obj.ResultCode()

        elif obj.implements( 'isCategorial' ):
            # suppose 'obj' is a subordinate document
            links_tool = getToolByName( self, 'portal_links' )
            links = links_tool.searchLinks( source=obj, internal=0, relation='subordination' )
            target = links and links[0].getObject().getTargetObject() or None
            target_version_id = links and links[0].getObject().getTargetUid('ver_id') or None
            result_code = self._getStateOfObject( obj )

        else: return

        if not target: return

        state_id = self._getStateOfObject( target )
        category_id = target.getCategory().getId()
        result_codes = self._getResultCodesFor( target, target_version_id )
        if result_code:
            result_codes[ tt_id ] = result_code

        transition_id = self._getTransitionByResultCodes( category_id, result_codes, state_id )
        if transition_id:
            self._makeTransitionForVersion( target, transition_id, target_version_id )

    #------------[ LOGIC IMPLEMENTATION ]---------------------------------------

    def _isObjectValid( self, object ):
        """
            Check is object valid for performs docflow logic

            Arguments:

                'object' -- object in context of which events happened
                            (generally HTMLDocument and Heading)

            Result:

                Boolean
        """
        return getObjectImplements( object, 'isCategorial' )


    #---------------[ on_finalizeTask ]---------------
    def _isTaskAutomated( self, task ):
        """
            Check is task automated

            Arguments:

                'task' -- object task (TaskItem)

            Result:

                Boolean

            Task on document may be 'automated' if they was maded automated,
            or 'not automated'

        """
        return self._getTaskTemplateId( task ) is not None

    def _getTaskTemplateId( self, obj ):
        """
            Returns id of the task template the object was created within.
        """
        return getattr( obj , 'task_template_id', None)

    def _getResultCodesFor( self, obj, version_id ):
        """
            Returns result codes mapping for task templates employed upon the object.

            Arguments:

                'obj'       --  target object.

                'version_id' -- object version id string.

            Result:

                A mapping of template id strings to result code values.

            Comments:

                Result codes for non-finalized followup tasks
                are set to '__running__'.

                Result codes for task templates which are not employed yet
                are set to '__notexists__'.
        """
        result_codes = {}

        try:
            followup = obj.followup
        except AttributeError:
            followup = None
        if followup is not None:
            tasks = followup.getBoundTasks( version_id )
            tasks.sort(lambda x, y: cmp( x.effective_date, y.effective_date ))

            for task in tasks:
                tt_id = self._getTaskTemplateId( task )
                if self._isTaskAutomated( task ):
                    if task.isFinalized():
                        result_codes[ tt_id ] = task.ResultCode()
                    else:
                        # mark running action templates
                        result_codes[ tt_id ] = '__running__'

        links_tool = getToolByName( self, 'portal_links' )
        query = { 'target': obj, 'relation': 'subordination' }
        version_id and query.setdefault( 'target_ver_id', version_id )
        links = links_tool.searchLinks( internal=0, **query )
        for link in links:
            subordinate = link.getObject().getSourceObject()
            if subordinate:
                tt_id = self._getTaskTemplateId( subordinate )
                if tt_id:
                    result_codes[ tt_id ] = self._getStateOfObject( subordinate )

        # mark not existing action templates
        tt_ids = obj.getCategory().taskTemplateContainer.getTaskTemplateIds( filter = 'have_result_codes' )
        for template_id in tt_ids:
            result_codes.setdefault( template_id, '__notexists__' )

        return result_codes

    def _getTransitionByResultCodes( self, category_id, result_codes, state ):
        """
            Takes transition by result codes, if is.

            Arguments:

                'category_id' -- category id

                'result_codes' -- array of result codes

                'state' -- state id for additions conditions

            Result:

                transition id or None

        """
        return self._portal_metadata().getCategoryById(category_id).resultcodes2TransitionModel.getTransitionByResultCodes( result_codes, state )

    def _makeTransitionForVersion( self, ob, transition, version ):
        """
            Perform transition for version of object

            Arguments:

                'ob' -- object for which performs transition

                'transition' -- transition id to perform

                'version' -- version of object

        """
        self._log( function='_makeTransition', text='transition:', params=transition )
        ob = ob.implements('isVersion') and ob.getVersionable() or ob
        self._secureBeforeTransition( self._getTransitionObject( ob, transition ) )
        # enter to version
        if version:
            back_version_id = ob.version[version].makeCurrent()
        try:
            result = self._portal_workflow().doActionFor( ob, transition )
            if result and result.has_key('ObjectMoved'):
                ob._setAcquisition(result['ObjectMoved'])
        finally:
            self._secureAfterTransition( self._getTransitionObject( ob, transition ))
            # leave version
            if version:
                ob.version[back_version_id].makeCurrent()

    def _secureBeforeTransition( self, transition_object ):
        self._log( function='_secureBeforeTransition', text='transition_object:', params=transition_object )
        guard_object = transition_object.guard
        guard_object.__class__._check = check
        guard_object.__dict__['check'] = guard_object._check

    def _secureAfterTransition( self, transition_object ):
        self._log( function='_secureAfterTransition', text='transition_object:', params=transition_object )
        guard_object = transition_object.guard
        try:
            del guard_object.__dict__['check']
        except:
            pass
        try:
            del guard_object.__class__._check
        except:
            pass

    def _getTransitionObject( self, ob, transition_id ):
        """
            Returns transiton object by id

            Arguments:

                'ob' -- object

                'transition_id' -- transition id

            Result:

                return transition object

        """

        self._log( function='_getTransitionObject', text='ob, transition:', params=(ob,transition_id) )
        return self._portal_workflow()[self._getWorkflowId(ob)].transitions[transition_id]

    #---------------[ onBeforeTransition ]---------------

    def _stateWhereDocumentGo( self, ob, transition_id ):
        """
            Return state where document will go by transition

            Arguments:

                'ob' -- object

                'transition_id' -- transition which will be perform

            Result:

                return state id where transition id lead

        """
        transitionInfo = self._portal_workflow().getTransitionInfo( self._getWorkflowId( ob ), transition_id )
        return transitionInfo["new_state_id"]

    def _getWorkflowId( self, ob ):
        """
            Return workflow id of object

            Arguments:

                'ob' -- object

            Result:

                return workflow id

        """
        return ob.getCategory().getWorkflow().getId()

    def _getListTaskForDieForState( self, category_id, state_id ):
        """
            Gets templates id which needed to finalize

            Arguments:

                'category_id' -- category id

                'state_id' -- state id

            Result:

                Returns array:
                >>  taskTemplateToDie = {
                >>     'task_template_id1': 'result_code1',
                >>     ...,
                >>  }
        """
        try:
            taskTemplateToDie = self._portal_metadata().getCategoryById(category_id).state2TaskTemplateToDie[state_id]
        except:
            taskTemplateToDie = {}
        return taskTemplateToDie

    def _getTaskAutomatedOfDocument( self, ob ):
        """
            Return automated task of document

            Arguments:

                'ob' -- object

            Result:

                Returns array of task objects (TaskItem) which was automated maden

        """
        automatedTasks = []
        # we take tasks only object's version
        for task in ob.followup.getBoundTasks( version_id=self._getObjectVersion( ob ) ):
            if self._isTaskAutomated( task ):
                automatedTasks.append( task )
        self._log( function='_getTaskAutomatedOfDocument', text='automatedTasks:', params=automatedTasks )
        return automatedTasks

    def _getObjectVersion( self, object ):
        """
            Returns object's version

            Arguments:

                'object' -- object version of which we want to know

            Result:

                current version id of document

        """
        return object.getVersion().id

    def _makeTaskNotAutomated( self, task ):
        """
            Make task not automated

            Arguments:

                'task' -- task object (TaskItem)

            TaskItem have attribute 'task_template_id', which are not None, if task
            are automated (i.e. was maden automated based on task template with id
            'task_template_id')

        """
        self._log( function='_makeTaskNotAutomated', text='task:', params=task )
        task.task_template_id = None

    def _finalizeTask( self, task, result_code ):
        """
            Finalize task with result code

            Arguments:

                'task' -- task which neede to finalize (TaskItem)

                'result_code' -- result code by which needed to finalize task

        """
        self._log( function='_finalizeTask', text='task, result_code', params=( task, result_code ) )
        task.onFinalize( result_code=result_code )

    #---------------[ onAfterTransition ]---------------
    def _getCategoryOfObject( self, ob ):
        """
            Returns category of object

            Arguments:

                'ob' -- object

            Result:

                category id of object

        """
        return ob.Category()

    def _getStateOfObject( self, ob ):
        """
             Returns state of object

             Arguments:

                 'ob' -- object to get state

            Result:

                State id of the object
        """
        return ob.getCategory().getWorkflow()._getWorkflowStateOf( ob ).getId()

    #--------------------------------------------------
    def _portal_metadata( self ):
        return getToolByName(self, 'portal_metadata')

    def _portal_workflow( self ):
        return getToolByName(self, 'portal_workflow')

    #--------------------------------------------------
    def _log( self, function='', text='', params='' ):
        return
        className = 'DocflowLogic'
        print "%s %s %s " % ( className, function, text ),
        print params


from Products.DCWorkflow.Expression import StateChangeInfo, createExprContext

def check( self, sm, wf_def, ob ):
    expr = self.expr
    if expr is not None:
        econtext = createExprContext(StateChangeInfo(ob, wf_def))
        res = expr(econtext)
        if not res:
            return 0
    return 1

InitializeClass( DocflowLogic, __version__ )
