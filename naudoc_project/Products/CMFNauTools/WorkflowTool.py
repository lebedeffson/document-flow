""" WorkflowTool class
$Id: WorkflowTool.py,v 1.101 2008/05/20 12:01:01 oevsegneev Exp $
"""
__version__ = '$Revision: 1.101 $'[11:-2]

import sys
from types import StringType, TupleType, DictType, StringTypes

from Acquisition import Implicit, aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo
from Globals import HTMLFile
from OFS.Folder import Folder
from ZODB.PersistentMapping import PersistentMapping
from ZODB.PersistentList import PersistentList

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.WorkflowCore import WorkflowException, \
        ObjectDeleted, ObjectMoved
from Products.CMFCore.WorkflowTool import WorkflowTool as _WorkflowTool, \
        addWorkflowFactory, _marker as workflow_marker
from Products.CMFCore.utils import getToolByName, _checkPermission

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Expression import Expression
from Products.DCWorkflow.ContainerTab import ContainerTab as _ContainerTab
from Products.DCWorkflow.Scripts import Scripts as _Scripts
from Products.DCWorkflow.States import States as _States, \
        StateDefinition as _StateDefinition
from Products.DCWorkflow.Transitions import Transitions as _Transitions, \
        TransitionDefinition
from Products.DCWorkflow.Variables import Variables
from Products.DCWorkflow.Worklists import Worklists
from Products.DCWorkflow.utils import modifyRolesForPermission

import Config, Features
from Exceptions import DuplicateIdError, ResourceLockedError, Unauthorized
from Config import Permissions
from MethodObject import Method
from Monikers import MonikerBase
from SimpleObjects import ToolBase, ContainerBase, InstanceBase, ExpressionWrapper, Persistent
from Utils import getObjectImplements, InitializeClass


class WorkflowTool( ToolBase, ContainerBase, _WorkflowTool ):
    """
        This tool accesses and changes the workflow state of content.
    """
    _class_version = 1.24

    meta_type = 'NauSite Workflow Tool'
    id = 'portal_workflow'
    isPrincipiaFolderish = 1

    __resource_type__ = 'item'

    meta_types = ({'name':'Workflow',
                   'permission':CMFCorePermissions.ManagePortal,
                   'action':''},
                 )

    security = ClassSecurityInfo()

    manage_options = _WorkflowTool.manage_options # + ToolBase.manage_options

    # CMF includes default_workflow, we do not
    _default_chain = ()

    # restore WorkflowTool methods overridden by ToolBase
    listActions = _WorkflowTool.listActions

    def setProperties(self, wf, title='dc_workflow', REQUEST=None):
        """
            Sets the workflow properties.

            Arguments:

                'wf' -- Workflow id string.

                'title' -- New workflow title.
        """
        workflow = self[wf]
        workflow.setProperties(title= title)
        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.portal_url() + '/workflow_properties?wf='+ wf\
                                            +'&portal_status_message=Properties+changed' )

    def addState(self, wf, state_id, REQUEST=None):
        """
            Adds new state to the specified workflow.

            Arguments:

                'wf' -- Workflow id string.

                'state_id' -- New state id string.
        """
        workflow = self[wf]
        workflow.states.addState(state_id)
        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.portal_url() + '/states?wf='+ wf\
                                            +'&portal_status_message=State+added' )

    def deleteStates(self, wf, ids, REQUEST=None):
        """
            Deletes states from the specified workflow.

            Arguments:

                'wf' -- Workflow id string.

                'ids' -- List of state id strings.

        """
        workflow = self[wf]
        states = workflow.states
        transitions = workflow.transitions

        for id in ids:
            state = states.get(id)
            if state and states.isPrivateItem(state):
                states.deleteStates([id])
                # fix transitions
                for transition in transitions.values():
                    if transition.new_state_id in ids and transitions.isPrivateItem(transition):
                        id = transition.id
                        title = transition.title
                        actbox_name = transition.actbox_name
                        new_state_id = ''
                        self.setTransitionProperties(wf, id, title, actbox_name, new_state_id)

        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.portal_url() + '/states?wf='+ wf\
                                            +'&portal_status_message=State(s)+removed' )

    def setStateProperties(self, wf, state_id, title, transitions, REQUEST=None):
        """
            Sets state properties.

            Arguments:

                'wf' -- Workflow id string.

                'state_id' -- State id string.

                'title' -- State title.

                'transitions' -- List of allowed transition ids.

            In case the specified state is acquired from the parent category, it
            should automatically become private before new state properties will
            be applied.

        """
        states = self[wf].states
        sdef = states[state_id]
        sdef = states.makePrivateItem(sdef)
        sdef.setProperties( title=title,
                            transitions=transitions
                          )

        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.portal_url() + '/state_properties?wf='+ wf\
                                            +'&state='+state_id\
                                            +'&portal_status_message=State+properties+changed' )

    def setStatePermissions(self, wf, state_id, REQUEST=None, redirect=1, force_update_roles=1):
        """
            Sets state permissions.

            Arguments:

                'wf' -- Workflow id string.

                'state_id' -- State id string.

                'REQUEST' -- REQUEST object containing the form with new state
                             permissions settings represented as the combination
                             of '<permission>|<role>' and 'acquire_<permission>'
                             input fields.

                'redirect' -- Boolean value indicating whether the user should
                              be redirected to the state properties management
                              form or not.
        """
        states = self[wf].states
        sdef = states[state_id]
        sdef = states.makePrivateItem(sdef)
        sdef.setPermissions(REQUEST)

        # XXX Add into the daily maintainance operations list.
        if force_update_roles:
            self.updateRoleMappings( wf, state_id )

        if REQUEST is not None and redirect:
            REQUEST[ 'RESPONSE' ].redirect( self.portal_url() + '/state_properties?wf='+ wf\
                                            +'&state='+state_id\
                                            +'&portal_status_message=State+properties+changed' )


    def updateRoleMappings(self, wf, state_id):
        # Update role mappings and recursively reindex objects of the same
        # category and state.
        catalog_tool = getToolByName( self, 'portal_catalog' )
        results = catalog_tool.unrestrictedSearch( state=state_id,
                                                   hasBase=self[wf].getCategoryDefinition().getId()
                                                 )
        if not results:
            return

        paths = []
        for r in results:
            ob = r.getObject()
            if ob is not None:
                wf = ob.getCategory().getWorkflow()
                if wf is not None and wf.updateRoleMappingsFor( ob ):
                    paths.append( r.getPath() )

        if not paths:
            return


        # While changing the object's permissions settings, we need to
        # update the allowedRolesAndUsers index for every subobject.
        # XXX Reindex only if 'View' permission settings were changed.
        results = catalog_tool.unrestrictedSearch( path=paths )
        for r in results:
            ob = r.getObject()
            if ob is not None:
                ob.reindexObject( idxs='allowedRolesAndUsers' )

    def getStateTitle(self, wf, state_id):
        """
            Returns the workflow state title.

            Arguments:

                'wf' -- Workflow id string.

                'state_id' -- State id string.

            Result:

                String, state title or id .
        """
        workflow = self[wf]
        state = workflow.states.get(state_id)
        if state:
            return state.title_or_id()

        return state_id # may be raise KeyError?

    security.declareProtected( CMFCorePermissions.View, 'getStateTitleFor' )
    def getStateTitleFor(self, obj):
        """
            Returns the workflow state title for given object.

            Arguments:

                'obj' -- Object reference.

            Result:

                String, state title or id .
        """
        wf_id = self._getCategoryWorkflowFor( obj
                                            , category=obj.getCategory().getId()
                                            )
        return self.getStateTitle( wf_id
                                 , self.getStateFor( obj, wf_id )
                                 )

    def addTransition(self, wf, trans_id, REQUEST=None):
        """
            Adds transition to the specified workflow.

            Arguments:

                'wf' -- Workflow id string.

                'trans_id' -- New transition id string.
        """
        workflow = self[wf]
        workflow.transitions.addTransition(trans_id)
        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.portal_url() + '/transitions?wf='+ wf\
                                            +'&portal_status_message=Transition+added' )

    def deleteTransitions(self, wf, ids, REQUEST=None):
        """
            Deletes transitions from the specified workflow.

            Arguments:

                'wf' -- Workflow id string.

                'ids' -- List of transition id strings.
        """
        workflow = self[wf]
        workflow.transitions.deleteTransitions(ids)

        # keep resultcodes2transition in actual state
        category = workflow.getCategoryDefinition()
        category.resultcodes2TransitionModel.onDeleteTransitions( ids )


        # delete transition ids from states
        states = workflow.states
        for state in states.values():
            if states.isPrivateItem(state):
                transitions = state.getTransitions()
                for transition_id in ids:
                    if transition_id in transitions:
                        transitions.remove( transition_id )
                self.setStateProperties(wf, state.getId(), state.title, transitions)

        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.portal_url() + '/transitions?wf='+ wf\
                                            +'&portal_status_message=Transition(s)+removed' )

    def setTransitionProperties(self, wf, transition, title, actbox_name, new_state_id, trigger_type=1):
        """
            Sets transition properties.

            Arguments:

                'wf' -- Workflow id string.

                'transition' -- Transition id string.

                'title' -- Transition title.

                'actbox_name' -- Transition name to be used in the action box.

                'new_state_id' -- State id string. Specifies the transition destination state.

                'trigger_type' -- Specifies the way transition is invoked by the workflow.
                Currently DCWorkflow defines the following trigger types: TRIGGER_AUTOMATIC,
                TRIGGER_USER_ACTION and TRIGGER_WORKFLOW_METHOD.

        """
        transitions = self[wf].transitions
        tdef = transitions[transition]
        tdef = transitions.makePrivateItem(tdef)

        trigger_type= int(trigger_type)
        script_name=''
        after_script_name=''
        actbox_url='%(content_url)s/change_state?transition='+transition
        tdef.setProperties(title, new_state_id,
                           trigger_type, script_name,
                           after_script_name,
                           actbox_name, actbox_url)

    def getTransitionInfo(self, wf, transition):
        """
            Returns transition properties.

            Arguments:

                'wf' -- Workflow id string.

                'transition' -- Transition id string.

            Result:

                Mapping with the following keys: 'title', 'new_state_id', 'actbox_name',
                'actbox_url'.

        """
        workflow=self[wf]
        transition = workflow.transitions[transition]
        ti = {        'title': transition.title,
               'new_state_id': transition.new_state_id,
                'actbox_name': transition.actbox_name,
                 'actbox_url': transition.actbox_url,
             }
        return ti

    def getTransitionTitle( self, wf, transition ):
        """
            Returns the workflow transition title.

            Arguments:

                'wf' -- Workflow id string.

                'transition' -- Transition id string.

            Result:

              String.
        """
        try: return self[ wf ].transitions[ transition ].title
        except KeyError: return ''

    def getTransitionGuard(self, wf, transition):
        """
            Returns the workflow transition guard.

            Arguments:

                'wf' -- Workflow id string.

                'transition' -- Transition id string.

            Result:

                Guard class instance.
        """
        workflow=self[wf]
        tr=workflow.transitions[transition]
        guard = tr.getGuard()
        return guard

    def getTransitionGuardRoles(self, wf, transition):
        """
            Lists the user roles required by the transition guard.

            Arguments:

                'wf' -- Workflow id string.

                'transition' -- Transition id string.

            Note:

                This method should become obsolete soon.

            Result:

              List of guard roles.

        """
        guard = self.getTransitionGuard(wf, transition)
        return guard.roles

    def setTransitionGuardRoles(self, wf, transition, roles):
        """
            Sets transition guard roles.

            Arguments:

                'wf' -- Workflow id string.

                'transition' -- Transition id string.

                'roles' -- List of guard roles.

            Note:

                This method should become obsolete soon.
        """
        guard = self.getTransitionGuard(wf, transition)
        guard.roles = roles
        workflow = self[wf]
        workflow.transitions[transition].guard = guard

        return

    def setTransitionGuardRules(self, wf, transition, rules_expr):
        """
            Sets the expression required by the transition guard.

            Arguments:

                'wf' -- Workflow id string.

                'transition' -- Transition id string.

                'rules_expr' -- Rule expression.

            Note:

                This method should become obsolete soon.
        """
        guard = self.getTransitionGuard(wf, transition)
        guard.expr = Expression(text=rules_expr)
        workflow = self[wf]
        workflow.transitions[transition].guard = guard

        return

    def setTransitionGuardPermissions(self, wf, transition, permissions):
        """
            Sets the permissions required by the transition guard.

            Arguments:

                'wf' -- Workflow id string.

                'transition' -- Transition id string.

                'permissions' -- List if required permissions.

            Note:

                This method should become obsolete soon.
        """
        guard = self.getTransitionGuard(wf, transition)
        guard.permissions = permissions
        workflow = self[wf]
        workflow.transitions[transition].guard = guard

        return

    def createWorkflow(self, id):
        """
            Creates new workflow.

            Arguments:

                'id' -- Workflow id string.

            New workflow object represents the WorkflowDefinition class instance.

        """
        ob = WorkflowDefinition(id)
        self._setObject(id, ob)

    def bindWorkflow(self, id, types=None):
        """
            Associates the specified workflow with the particular portal types.

            Arguments:

                'id' -- Workflow id string.

                'types' -- Portal types list.

            The given workflow is added to the workflows chain corresponding to the
            specified portal type.

        """
        if types is not None:
            for typ in types:
                if self._chains_by_type is None:
                    chain=[]
                else:
                    chain = self._chains_by_type.get(typ, [])
                chain = list(chain)
                chain.append(id)
                self.setChainForPortalTypes( ( typ, ), chain )
        else:
            # Add workflow to the default chain
            chain = self._default_chain or []
            if id not in chain:
                chain = list(chain)
                chain.append(id)
                self._default_chain = tuple(chain)

    def getChainFor( self, ob ):
        """
            Returns the chain that applies to the given object.

            Arguments:

                'ob' -- Either a portal object or a string representing the object's portal
                        type.

            Result:

                List of workflow ids.
        """
        if not isinstance( ob, StringType ):
            wf_id = self._getCategoryWorkflowFor( ob )
            if wf_id is not None:
                return [ wf_id ]
        return _WorkflowTool.getChainFor( self, ob )

    security.declarePublic('doActionFor')
    def doActionFor( self, ob, action, wf_id=None, wf_bycategory=1, *args, **kw ):
        """
            Allows the user to request a workflow action.

            Arguments:

                'ob' -- User context.

                'action' -- Workflow action id.

                'wf_id' -- Optional workflow specification.

                'wf_bycategory' -- Boolean. Indicates that workflow should be selected
                                   depending on the document's category.

                '*args', '**kw' -- Additional arguments to be passed to the action method.

            Result:

                Action result code.
        """
        if aq_parent( ob ) is None:
            #XXX fix me
            #try to take object again
            portal_catalog = getToolByName( self, 'portal_catalog' )
            ob = portal_catalog.getObjectByUid( uid = ob.nd_uid )

        if wf_id is None and wf_bycategory:
            wf_id = self._getCategoryWorkflowFor( ob )

        old_state = self.getStateFor(ob, wf_id)

        try:
            res = _WorkflowTool.doActionFor( self, ob, action, wf_id, *args, **kw )
        except ObjectMoved, err:
            ob = err.getNewObject()
            # XXX
            res = { 'ObjectMoved': ob }

        if self.getStateFor(ob, wf_id) != old_state:
            portal_metadata = getToolByName(self, 'portal_metadata')
            portal_metadata.docflowLogic.processAutomatedTransitionsFor( ob )

        # XXX test for its need
        ob.reindexObject()

        return res or {}

    security.declarePublic('getStateFor')
    def getStateFor( self, ob, wf_id=None, wf_bycategory=1, category=None ):
        """
            Returns workflow state of the object.

            Arguments:

                'ob' -- Object reference.

                'wf_id' -- Optional workflow specification.

                'wf_bycategory' -- Boolean. Indicates that workflow should be selected
                                   depending on the document's category.

                'category' -- Explicit document category specification.

            Result:

                State id.
        """
        if wf_id is None and wf_bycategory:
            wf_id = self._getCategoryWorkflowFor( ob, category=category )

        # TODO: use wf.state_var
        return _WorkflowTool.getInfoFor( self, ob, 'state', None, wf_id )

    security.declarePublic('getStateForContext')
    def getStateForContext( self, *args, **kw ):
        """
            Returns workflow state of the current context.

            Arguments:

                '*args', '**kw' -- Additional arguments to be passed to the getStateFor method.

            Result:

                State id.
        """
        return self.getStateFor( aq_parent( self ), *args, **kw )

    security.declarePublic('getInfoFor')
    def getInfoFor( self, ob, name, default=Missing, wf_id=None, wf_bycategory=1, *args, **kw ):
        """
            Returns information on the object provided by the workflow.

            Arguments:

                'ob' -- Object reference.

                'name' -- Workflow variable name.

                'default' -- Default variable value.

                'wf_id' -- Optional workflow specification.

                'wf_bycategory' -- Boolean. Indicates that workflow should be selected
                                   depending on the document's category.

                '*args', '**kw' -- Additional arguments to be passed to the workflow's
                                   getInforFor method.

            Result:

                Workflow variable value.
        """
        if wf_id is None and wf_bycategory:
            wf_id = self._getCategoryWorkflowFor( ob )

        if default is Missing:
            default = workflow_marker

        return _WorkflowTool.getInfoFor( self, ob, name, default, wf_id, *args, **kw )

    security.declarePublic('getInfoForContext')
    def getInfoForContext( self, *args, **kw ):
        """
            Returns information on the current context provided by the workflow.

            Arguments:

                '*args', '**kw' -- Additional arguments to be passed to the getInfoFor method.

            Result:

                Workflow variable value.
        """
        return self.getInfoFor( aq_parent( self ), *args, **kw )

    security.declarePrivate('getCatalogVariablesFor')
    def getCatalogVariablesFor( self, ob, wf_bycategory=1 ):
        """
            Returns a mapping containing the catalog variables that apply to the object.

            Arguments:

                'ob' -- Object reference.

                'wf_bycategory' -- Boolean. Indicates that workflow should be selected
                                   depending on the document's category.

            Result:

                Mapping containing the variables name/value pairs.

        """
        vars = _WorkflowTool.getCatalogVariablesFor( self, ob )

        if wf_bycategory:
            wf_id = self._getCategoryWorkflowFor( ob )
            if wf_id:
                wf = self.getWorkflowById( wf_id )
                if wf:
                    vars[ wf.state_var ] = wf.getInfoFor( ob, wf.state_var, None )

        return vars

    security.declarePrivate('wrapWorkflowMethod')
    def wrapWorkflowMethod(self, ob, method_id, func, args, kw):
        """
            Allows a workflow definition to wrap a WorkflowMethod.

            Arguments:

                'ob' -- Object reference.

                'method_id' -- Workflow method id.

                'func' -- Function reference.

                'args', 'kw' -- Additional arguments to be passed to the workflow method.

            To be invoked only by WorkflowCore.
        """
        wf = None
        wfs = self.getWorkflowsFor(ob)
        if wfs:
            for w in wfs:
                if (hasattr(w, 'isWorkflowMethodSupported')
                    and w.isWorkflowMethodSupported(ob, method_id)):
                    wf = w
                    break
        else:
            wfs = ()
        if wf is None:
            # No workflow wraps this method.
            # check permission
            if not isinstance( method_id, StringType ):
                if not _checkPermission( method_id.getPerm(), ob ):
                    raise Unauthorized
            return func( *args, **kw)
        return self._invokeWithNotification(
            wfs, ob, method_id, wf.wrapWorkflowMethod,
            (ob, method_id, func, args, kw), {})

    def _invokeWithNotification( self, wfs, ob, action, func, args, kw ):
        """
            Private utility method:  call 'func', and deal with exceptions
            indicating that the object has been deleted or moved.
        """
        reindex = 1
        for w in wfs:
            w.notifyBefore(ob, action)
        try:
            res = func( *args, **kw)
        except ObjectDeleted, ex:
            res = ex.getResult()
            reindex = 0
        except ObjectMoved, ex:
            res = ex.getResult()
            ob = ex.getNewObject()
        except:
            exc = sys.exc_info()
            try:
                for w in wfs:
                    w.notifyException(ob, action, exc)
                raise exc[0], exc[1], exc[2]
            finally:
                exc = None
        # the original tool performs reindex after notifySuccess
        if reindex:
            self._reindexWorkflowVariables(ob)
        for w in wfs:
            w.notifySuccess(ob, action, res)
        return res

    def _getCategoryWorkflowFor( self, ob, category=None ):
        """
            Returns the workflow corresponding to the document's category.

            Arguments:

                'ob' -- Object reference.

                'category' -- Explicit category specification.

            Result:

                Workflow definition object.
        """
        chain = _WorkflowTool.getChainFor( self, ob )
        wf_id = None

        if chain and ob.implements( 'isCategorial' ):
            metadata = getToolByName( self, 'portal_metadata' )
            category = metadata.getCategoryById( category or ob.Category() )

            if category:
                wf_id = category.Workflow()
                if wf_id and wf_id not in chain:
                    wf_id = None

        return wf_id

    def onFinalize( self, task ):
        """
            Task finalization handler.

            Arguments:

                'task' -- Task item.
        """
        portal_metadata = getToolByName(self, 'portal_metadata')
        portal_metadata.docflowLogic.processAutomatedTransitionsFor( task )

    def onRespond( self, task ):
        """
            Task respond handler.

            Arguments:

                'task' -- Task item.
        """
        portal_metadata = getToolByName(self, 'portal_metadata')
        portal_metadata.docflowLogic.processAutomatedTransitionsFor( task )

InitializeClass( WorkflowTool )


class WorkflowDefinition( InstanceBase, DCWorkflowDefinition ):
    """
        NauSite Workflow Definition
    """
    _class_version = 1.27

    meta_type = 'Workflow'
    title = 'NauSite Workflow Definition'

    initial_transition = None

    manage_options = DCWorkflowDefinition.manage_options + \
                     InstanceBase.manage_options

    security = ClassSecurityInfo()
    security.declareObjectProtected( CMFCorePermissions.ManagePortal )

    isPrincipiaFolderish = DCWorkflowDefinition.isPrincipiaFolderish
    icon = DCWorkflowDefinition.icon

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setProperties' )
    setProperties = DCWorkflowDefinition.setProperties

    state_attr_permission_roles = None

    def __init__( self, id ):
        InstanceBase.__init__( self, id )
        self._addObject(States('states'))
        self._addObject(Transitions('transitions'))
        self._addObject(Variables('variables'))
        self._addObject(Worklists('worklists'))
        self._addObject(Scripts('scripts'))

    def _initstate( self, mode ):
        """
            Initialize attributes
        """
        if not InstanceBase._initstate( self, mode ):
            return False

        if hasattr(self, 'state_attr_mandatory'): # < 1.27
            del self.state_attr_mandatory

        self._upgrade('states', States)
        self._upgrade('scripts', Scripts)
        self._upgrade('transitions', Transitions)

        return True

    def setAttributePermission(self, state_id, attr_id, permission, acquired, roles):
        """
            Sets the permission-roles mapping for the category attribute
            in given state.

            Arguments:

                'state_id' -- A state id string.

                'attr_id' -- An attribute id string.

                'permission' -- Name of permission to set.

                'acquired' -- In this context set acquired to True means
                    "take security settings from state or superCategory`s
                    attribute settings".

                'roles' -- List of roles to set.
        """
        # in this context acquired means 'take all from state or superCategory`s attribute'
        # so if acquired - drop all roles for permission

        sapr = self.state_attr_permission_roles
        if sapr is None:
            self.state_attr_permission_roles = sapr = PersistentMapping()
        if acquired:
            roles = list(roles) #[]
        else:
            roles = tuple(roles)

        pr = sapr.get( (state_id, attr_id), {})
        pr[permission] = roles
        sapr[ (state_id, attr_id) ] = pr

    def setAttributePermissions(self, REQUEST):
        """
            Sets the permission-roles mapping for the category attribute
            in given state.

            Note: Only 'View attributes' and 'Modify attributes' permissions may
                be changed here.

            Arguments:

                'REQUEST' -- specifies Zope request object.
        """
        # in this context acquired means 'take all from state or superCategory`s attribute'
        # so if acquired - drop all roles for permission
        mdtool = getToolByName(self, 'portal_metadata')
        available_roles = mdtool.getManagedRoles_()

        state = REQUEST.get('state')
        attr_id = REQUEST.get('attribute_id')

        sapr = self.state_attr_permission_roles
        if sapr is None:
            self.state_attr_permission_roles = sapr = PersistentMapping()

        for p in ( Permissions.ViewAttributes, Permissions.ModifyAttributes ):
            roles = []
            acquired = REQUEST.get('acquire_' + p, 0)
            for r in available_roles:
                if REQUEST.get('%s|%s' % (p, r), 0):
                    roles.append(r)
            roles.sort()
            if not acquired:
                roles = tuple(roles)
            else:
                roles = list(roles) #[]


            pr = sapr.get( (state, attr_id), {})
            pr[p] = roles
            sapr[ (state, attr_id) ] = pr

    def getAttributePermissionInfo(self, state_id, attr_id, p):
        """
            Returns information about permission settings for
            category attribute in given state.

            Arguments:

                'state_id' -- A state id string.

                'attr_id' -- An attribute id string.

                'p' -- Permission name.


            Result:

                Dictionary with two keys: 'acquired' and 'roles'. 'acquired'
                is true if no permission-roles mapping for category attribue
                specified. Roles are list of roles managed by permission.
        """
        roles = None
        perm = None
        if self.state_attr_permission_roles:
            perm_def = self.state_attr_permission_roles.get( (state_id, attr_id), {} )
            roles = perm_def.get(p, None)
        if roles is None:
            return {'acquired':1, 'roles':[]}
        else:
            if type(roles) is TupleType:
                acq = 0
            else:
                acq = 1
            return {'acquired':acq, 'roles':list(roles)}

    def listObjectActions( self, info ):
        """
            Lists object actions provided by the workflow.

            Arguments:

                'info' -- Object action information. See CMFCore.ActionsTool for details.

            Allows this workflow to include actions to be displayed in the actions box.
            Called only when this workflow is applicable to info.content.

            Result:

                List of actions represented by mappings with the following keys: 'name',
                'url', 'permissions', 'category'.

        """

        try:
            ob = info.content
            if ob.implements('isLockable'):
                ob.failIfLocked()
        except ResourceLockedError:
            return []
        return DCWorkflowDefinition.listObjectActions( self, info )

    def notifyBefore(self, ob, action):
        """
            Before transition handler.

            Arguments:

                'ob' -- Object reference.

                'action' -- Workflow action id.

        """
        portal_metadata = getToolByName(self, 'portal_metadata')

        portal_metadata.versionWorkflowLogic.onBeforeTransition( ob, action )
        portal_metadata.docflowLogic.onBeforeTransition( ob, action )

    def notifySuccess(self, ob, action, result):
        """
            After transition handler.

            Arguments:

                'ob' -- Object reference.

                'action' -- Workflow action id.

        """
        portal_metadata = getToolByName(self, 'portal_metadata')
        portal_metadata.docflowLogic.onAfterTransition( ob, action )

    def _changeStateOf( self, ob, tdef=None, kwargs=None ):
        """
            Changes state.
            tdef set to None means the object was just created.
            If self.initial_state is None, try to make initial transition.

            Arguments:

                'ob' -- Object reference.

                'tdef' -- Transition definition.
        """
        old_sdef = self._getWorkflowStateOf( ob )
        if old_sdef is not None:
            old_state = old_sdef.getId()
        else:
            old_state = None

        is_to_none = 0
        if tdef is self.initial_state is None:
            try:
                tdef = self.transitions[self.initial_transition]
                # we need make this assignment to _executeTransition work properly.
                # initial_state will be set to None again.
                self.initial_state = tdef.new_state_id
                is_to_none = 1
            except KeyError:
                pass

        moved = 0
        while 1:
            try:
                sdef = self._executeTransition(ob, tdef, kwargs)
            except ObjectMoved, ex:
                moved = 1
                ob = ex.getNewObject()
                sdef = self._getWorkflowStateOf(ob)
            if sdef is None:
                break
            tdef = self._findAutomaticTransition(ob, sdef)
            if tdef is None:
                # No more automatic transitions.
                break
            # Else continue.
        if is_to_none:
            self.notifySuccess( ob, self.initial_transition, sdef )
            self.initial_state = None

        if moved:
            raise ObjectMoved(ob)

    security.declarePrivate('isWorkflowMethodSupported')
    def isWorkflowMethodSupported(self, ob, method):
        """
            Checks whether the given workflow method is supported in the current state.

            Arguments:

                'ob' -- Object reference.

                'method' -- Either a workflow method reference or method id string.

        """


        if not isinstance( method, StringType ):
            method_id = method.getAction()
        else:
            method_id = method

        sdef = self._getWorkflowStateOf(ob)

        if sdef is None:
            return 0
        if method_id in sdef.transitions:
            tdef = self.transitions.get(method_id, None)
            if (tdef is not None and
                tdef.trigger_type == 2 and # 2:=TRIGGER_WORKFLOW_METHOD
                self._checkTransitionGuard(tdef, ob)):
                return 1
        return 0

    security.declarePrivate('wrapWorkflowMethod')
    def wrapWorkflowMethod(self, ob, method, func, args, kw):
        """
            Allows the user to request a workflow action.

            Arguments:

                'ob' -- Object reference.

                'method_id' -- Workflow method id.

                'func' -- Function reference.

                'args', 'kw' -- Additional arguments to be passed to the workflow method.

            Note:

                Workflow method must perform its own security checks.
        """

        if not isinstance( method, StringType ):
            method_id = method.getAction()
            invoke_after = method.getInvokeAfter()
        else:
            method_id = method
            invoke_after = None

        sdef = self._getWorkflowStateOf(ob)
        if sdef is None:
            raise WorkflowException, 'Object is in an undefined state'
        if method_id not in sdef.transitions:
            raise Unauthorized
        tdef = self.transitions.get(method_id, None)
        if tdef is None or tdef.trigger_type != 2: # 2:=TRIGGER_WORKFLOW_METHOD
            raise WorkflowException, (
                'Transition %s is not triggered by a workflow method'
                % method_id)
        if not self._checkTransitionGuard(tdef, ob):
            raise Unauthorized
        if not invoke_after:
            res = apply(func, args, kw)
        try:
            self._changeStateOf(ob, tdef)
        except ObjectDeleted:
            # Re-raise with a different result.
            raise ObjectDeleted(res)
        except ObjectMoved, ex:
            # Re-raise with a different result.
            raise ObjectMoved(ex.getNewObject(), res)
        if invoke_after:
            res = apply(func, args, kw)
        return res

    security.declarePrivate('getCategoryDefinition')
    def getCategoryDefinition(self):
        """
            Returns the document category definition object applied to this workflow.

            Result:

                Category definition object.
        """
        metadata = getToolByName(self, 'portal_metadata')
        cat_id = self.getId().replace( metadata.WORKFLOW_PREFIX, '' )
        return metadata.getCategory( cat_id, None )

    security.declarePublic( 'getInitialTransition' )
    def getInitialTransition( self ):
        """
        Returns category's initial_transition
    """
        return getattr( self, 'initial_transition', None )

InitializeClass( WorkflowDefinition )

addWorkflowFactory(WorkflowDefinition, id='nausite_workflow',
                   title='NauSite workflow')


class WorkflowMethod( Method ):

    """ Wrap a method to workflow-enable it.
    """
    _need__name__ = 1

    def __init__( self, method, id=None, reindex=1, security=None, invoke_after=None, method_permission=None ):
        name = (type(method) is StringType) and method or method.__name__
        self._id = id or name
        self._m = method
        self._invoke_after = invoke_after
        self._method_permission = method_permission
        security.declarePublic( name )
        # reindex ignored since workflows now perform the reindexing.

    def __call__( self, instance, *args, **kwargs ):
        """ Invoke the wrapped method, and deal with the results.
        """
        method = self.__dict__['_m']
        if type(method) is StringType:
            method = getattr( instance, method )
        else:
            args = (instance,) + args
        workflow = getToolByName( instance, 'portal_workflow' )
        return workflow.wrapWorkflowMethod( instance, self, method, args, kwargs )

    def getAction( self ):
        return self._id

    def getInvokeAfter( self ):
        return self._invoke_after

    def getPerm( self ):
        return self._method_permission


class StateDefinition(InstanceBase, _StateDefinition):

    __resource_type__ = 'item'

    __implements__ = Features.createFeature('isState')

    meta_type = _StateDefinition.meta_type
    manage_options = _StateDefinition.manage_options
    setProperties = _StateDefinition.setProperties

    security = ClassSecurityInfo()

    def _getManatoryAttributeLink(self, attr):
        links = getToolByName(self, 'portal_links')
        attr = self.getAttributeDefinition(attr)

        res = links.searchLinks(
            source = self,
            target = attr,
            relation = 'reference'
        )

        if res:
            return res[0].getObject()

    # TODO add permission
    def setMandatoryAttribute(self, attr, mandatory):
        """
            Sets mandatory property of attribute in given state.

            Arguments:

                'attr' -- String. Attribute identifier.

                'mandatory' -- Boolean.

        """
        links = getToolByName(self, 'portal_links')
        link = self._getManatoryAttributeLink(attr)

        if mandatory:
            if link: return

            links.createLink(
                self,
                self.getAttributeDefinition(attr),
                'reference'
            )

        else:
            if not link: return

            links.removeLink(link, self)

    # TODO add permission
    def isAttributeMandatory(self, attr):
        """
            Checks that attribute is mandatory in given state.

            Arguments:

                'attr' -- String. Attribute identifier.

            Result:

                Boolean.

        """
        return (self._getManatoryAttributeLink(attr) is not None)

InitializeClass(StateDefinition)

class StateMoniker( MonikerBase ):
    """
        Moniker for state definition.
    """
    _types = (StateDefinition.__resource_type__,)
    _template = HTMLFile( 'skins/monikers/state_moniker', globals() )
    _mandatory_args = MonikerBase._mandatory_args[:-1] + (('moniker_frame', 'workspace' ),)

    def __init__( self, object, md=None, **kwargs ):
        """
            Associates new moniker with the target object.

            Arguments:

                'object' -- the object or its identifier (string)

                'md' -- optional DTML dictionary, used to load
                        the object by identifier

                '**kwargs' -- additional keyword arguments to pass
                              to DTML template
        """
        if hasattr( object, 'implements' ) and object.implements( 'isCategorial' ):
            category = object.getCategory()
            state = category.getWorkflow()._getWorkflowStateOf( object )
        elif isinstance( object, StringTypes ):
            # object is a string 'wf_id:state_id'
            # XXX add new resource type
            wf_id, state_id = object.split(':',1)

            wf_tool = md.getitem('portal_workflow', 0 )
            workflow = wf_tool.getWorkflowById(wf_id)
            state = workflow.states[ state_id ]
            category = workflow.getCategoryDefinition()
        else: # object is StateDefinition
            state = object
            category = state.getWorkflow().getCategoryDefinition()

        # set right default url for state
        kwargs['url'] = category.relative_url( action='state_properties'
                                             , params={'state':state.getId()}
                                             )

        assert( isinstance(state, StateDefinition ) ), 'expected StateDefinition instance'
        MonikerBase.__init__(self, state, md=md, **kwargs)

    def _moniker_render( self, md=None, **kwargs ):
        return self._render( self._template, md, **kwargs )

class ContainerMapping( PersistentMapping, Implicit ):
    """
        Dictionary-like class that allows attributes to be dynamically inherited
        from base categories.
    """
    def isPrivateKey( self, key ):
        """
            Checks whether the attribute with the given key is private.

            Arguments:

                'key' -- Attribute name.

            Result:

                Boolean. Returns True value for private attribute and False
                value for attribute inherited from another category.
        """
        return self.data.has_key(key)

    def has_key( self, key ):
        return key in self.keys()

    def keys( self ):
        return self._getData().keys()

    def get( self, name, default=None ):
        try:
            return self[ name ]
        except KeyError:
            return default

    def __getitem__( self, name ):
        return self._getData()[ name ]

    def __setitem__( self, name, value ):
        PersistentMapping.__setitem__( self, name, value )
        self.invalidateCache()

    def __delitem__( self, name ):
        PersistentMapping.__delitem__( self, name )
        self.invalidateCache()

    def clear(self):
        self.invalidateCache()
        PersistentMapping.clear( self )

    def update(self, b):
        self.invalidateCache()
        PersistentMapping.update( self, b )

    def setdefault(self, key, failobj=None):
        self.invalidateCache()
        return PersistentMapping.setdefault( self, key, failobj )

    def pop(self, key, *args):
        self.invalidateCache()
        PersistentMapping.pop(self, key, *args)

    def popitem(self):
        self.invalidateCache()
        PersistentMapping.popitem()

    def _getData( self ):
        """
            Returns the mapping representing dictionary data.

            Dynamically inherited attributes are included into mapping
            as well as private attributes.

            Inherited dictionary data are being automatically cached.
            The cache is invalidated every time an item is modified
            or deleted from this mapping.
        """
        cache = getattr( self, '_v_data_cache', None )
        if cache is not None:
            return cache

        parent = aq_parent(aq_inner( self ))
        workflow = aq_parent(aq_inner( parent ))
        if workflow is None:
            # happens in process of lifting the parent from DB
            return self.data

        category = workflow.getCategoryDefinition()
        if category is None:
            # workflow is not bound to any category
            return self.data

        cache = {}
        id = parent.getId()
        bases = list( category.listBases() )
        bases.reverse()

        # walk through first-level base categories
        # and collect all the inherited items
        # XXX the whole stuff is damn slow
        for base in bases:
            container = base.getWorkflow()._getOb( id, None )
            if container is not None:
                # NB _getData induces listBases recursively
                cache.update( container._mapping._getData() )

        cache.update( self.data )

        self._v_data_cache = cache
        return cache

    def invalidateCache( self ):
        """
            Forces data cache to be updated.
        """
        if hasattr( self, '_v_data_cache' ):
            del self._v_data_cache

    def __getstate__(self):
        state = PersistentMapping.__getstate__(self)

        for key in state.keys():
            if key.startswith('_v_'):
                del state[key]

        return state


InitializeClass( ContainerMapping )


class ContainerTab( Persistent, _ContainerTab ):
    _class_version = 1.5

    def __init__( self, id ):
        self.id = id
        self._mapping = ContainerMapping()
        Persistent.__init__( self )

    def _initstate( self, mode ):
        # initialize attributes
        if not Persistent._initstate( self, mode ):
            return 0

        mapping = self._mapping

        if type(mapping) is DictType:
            self._mapping = ContainerMapping( mapping )

        elif mode and mapping._p_oid \
             and hasattr(mapping, '_v_data_cache'): # < 1.5
            del mapping._v_data_cache
            mapping._p_changed = 1

        return 1

    def __getattr__(self, name):
        if hasattr(self, '_mapping'):
            ob = self._mapping.get(name, None)
            if ob is not None:
                return ob
        raise AttributeError, name

    def _setOb(self, name, value):
        # NB invalidateCache is called twice but it won't hurt
        _ContainerTab._setOb(self, name, value)
        self.notifyChanged()

    def _delOb(self, name):
        _ContainerTab._delOb(self, name)
        self.notifyChanged()

    def isPrivateItem(self, item):
        """
            Checks whether the container's item is private.

            Arguments:

                'item' -- Either a container's object reference or an attribute
                          id string.

            Result:

                Boolean. Returns True value for private attribute and False
                value for attribute inherited from another category.
        """
        if item is StringType:
            item = self[item]

        return self._mapping.isPrivateKey(item.getId())

    def makePrivateItem(self, item):
        """
            Makes the container's item private.

            Arguments:

                'item' -- Either a container's object reference or an attribute
                          id string.

            Result:

                Item instance.

            Ensures that the given item is private or copies it to the current
            object in case it is inherited from another category.
        """
        if item is StringType:
            item = self[item]

        id = item.getId()
        if not self.isPrivateItem(item):
            self._setObject(id, item._getCopy(self))

        return self[id]

    def _checkId(self, id, allow_dup=0):
        if not allow_dup:
            if self._mapping.isPrivateKey(id):
                raise DuplicateIdError, "This identifier is already in use."

    def notifyChanged( self, dependent=True ):
        """
            Handler for the container contents changes.

            Note:

                Handler is _not_ invoked on changing the contained
                itemsm properies; it's only purpose is to track the items
                creation and deletion operations in order to update the data
                cache.
        """
        self._mapping.invalidateCache()
        if not dependent:
            return

        workflow = aq_parent(aq_inner( self ))
        category = workflow.getCategoryDefinition()

        if category is None:
            return

        id = self.getId()
        for cdef in category.listDependentCategories():
            container = cdef.getWorkflow()._getOb( id, None )
            if container is not None:
                container.notifyChanged( dependent=False )

InitializeClass( ContainerTab )


class Scripts(ContainerTab, _Scripts):
    """
        Workflow scripts container.
    """

    manage_main = _Scripts.manage_main

InitializeClass(Scripts)

class States(ContainerTab, _States):
    """
        Workflow states container.
    """
    _class_version = 1.00

    all_meta_types = ({'name':_StateDefinition.meta_type,
                       'action':'addState',
                       },)

    def _initstate( self, mode ):
        # initialize attributes
        if not ContainerTab._initstate( self, mode ):
            return 0

        for key in self._mapping.keys():
            self._upgrade(key, StateDefinition, self._mapping)

        return 1

    def addState(self, id, REQUEST=None):
        self._setObject(id, StateDefinition(id))

    def _delObject(self, id, *args, **kwargs):
        self._getOb(id)._ItemBase__instance_destroyed = True
        return ContainerTab._delObject(self, id, *args, **kwargs)

    manage_main = _States.manage_main

    def setInitialState(self, id=None, ids=None, REQUEST=None):
        """
        """
        if not id:
            if len( ids ) != 1:
                raise ValueError, 'One and only one state must be selected'
            id = ids[0]
        id = str( id )
        wf = aq_parent(aq_inner(self))
        if wf.initial_transition is None:
            wf.initial_state = id
            return True
        else:
            return False

    def unsetInitialState( self ):
        """
            Unset initial state for workflow.
        """
        wf = aq_parent(aq_inner( self ))
        initial_state = wf.initial_state
        if initial_state is not None:
            wf.initial_state = None

InitializeClass(States)

class Transitions(ContainerTab, _Transitions):
    """
        Workflow transitions container.
    """
    all_meta_types = ({'name':TransitionDefinition.meta_type,
                       'action':'addTransition',
                       },)

    manage_main = _Transitions.manage_main

    def setInitialTransition( self, id=None ):
        """
            Set initial transition for workflow.
        """
        id = str( id )
        wf = aq_parent( aq_inner( self ) )
        if wf.initial_state is None:
            wf.initial_transition = id
            return True
        else:
            return False

    def unsetInitialTransition( self ):
        """
            Unset initial transition for workflow.
        """
        wf = aq_parent(aq_inner( self ))
        initial_transition = wf.initial_transition
        if initial_transition is not None:
            wf.initial_transition = None

InitializeClass(Transitions)

class WorkflowInstaller:
    after = True
    name = 'setupWorkflow'
    priority = 55
    def install(self, p, check=False ):
        wftool = getToolByName( p, 'portal_workflow' )
        tptool = getToolByName( p, 'portal_types' )
        cbt = wftool._chains_by_type

        count = 0
        seen = []
        for chain, types in Config.WorkflowChains.items():
            seen.extend( types )
            for pt in types:
                if not cbt or cbt.get( pt, '__default__' ) != chain:
                    count += 1
            if check:
                continue

            if chain != '__default__':
                wftool.setChainForPortalTypes( types, chain )
            else:
                for pt in types:
                    if cbt and cbt.has_key( pt ):
                        del cbt[ pt ]

        types = []
        for tinfo in tptool.listTypeInfo():
            pt = tinfo.getId()
            if pt not in seen:
                if not cbt or cbt.get( pt, None ) not in ([], ()):
                    count += 1
                if check:
                    continue
                types.append( pt )

        orphans = []
        for wf in wftool.objectValues():
            id = wf.getId()
            if id.startswith('category_') and wf.getCategoryDefinition() is None:
                count += 1
                orphans.append( id )

        if not check:
            wftool.setChainForPortalTypes( types, [] )
            wftool.deleteObjects( orphans )

        return count

    __call__ = install

def initialize( context ):
    # module initialization callback

    context.registerTool( WorkflowTool )

    context.registerMoniker( StateMoniker, 'state' )
    #XXX
    context.registerVarFormat( 'workflow_state', lambda v, n, md: StateMoniker(v, md).render(md) )

    context.registerInstaller( WorkflowInstaller )
