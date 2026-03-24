"""
Module implementing story "ND.DocFlow_task.3"

Workflow for version.

Contain class:
  VersionWorkflowLogic

$Editor: inemihin $
$Id: VersionWorkflow.py,v 1.8 2005/05/14 05:43:49 vsafronovich Exp $

"""

__version__ = '$Revision: 1.8 $'[11:-2]


from copy import deepcopy
from types import StringType

from Acquisition import Implicit, aq_base
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.SecurityManagement import getSecurityManager
from DateTime import DateTime
from zExceptions import Unauthorized

from Products.CMFCore.utils import _checkPermission, getToolByName

from SimpleObjects import Persistent
from Config import Roles, Permissions
from Utils import InitializeClass

class VersionWorkflowLogic( Persistent, Implicit ):
    """
      Class implementing transition handler logic.

      Have one public method:
        -- onBeforeTransition( transition_id )

      Diagram:

        'version_workflow-activity_diagram.png'
    """

    _class_version = 1.0

    def __init__( self ):
        Persistent.__init__( self )

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not Persistent._initstate( self, mode ):
            return 0

        return 1

    def onBeforeTransition( self, obj, action ):
        """
          Handler-function, must be called before transition for document.
          The "main-logic" function.

          Arguments:

            'obj' -- object for which transition have to be performed

            'action' -- transition which have to be performed

        """
        self._log( function='onBeforeTransition', params=(obj, action) )

        if not self._isObjectValid( obj ):
            return

        if self._isActionWorkflowMethod( action ):
            transition_id = action.getAction()
            self._createNewVersionLogic( action, obj )
        else:
            transition_id = action

        self._logicForVersionExclusion( obj, transition_id )

    #--------------------------------------------------------------------
    def _logicForVersionExclusion( self, obj, transition_id=None, new_state_id=None ):
        """
        """

        if not new_state_id:
            new_state_id = self._getStateIdByTransition( self._getCategory(obj), transition_id )

        count_versions_in_state = self._getCountVersionsInState( obj, new_state_id )
        if self._areCountVersionsInStateValid( self._getCategory(obj), new_state_id, count_versions_in_state+1 ):
            # just return, i.e. execute transition
            #
            return
        else:
            # we have to exclude version from state, by
            # transition it to other state
            version_ids = self._getVersionsForExclusion( obj, new_state_id )
            transition_for_exclusion = self._getTransitionForExclusion( self._getCategory(obj), new_state_id )
            for ver_id in version_ids:
                self._makeTransitionForVersion( obj, ver_id, transition_for_exclusion )

    #--------------------------------------------------------------------------------------
    def _getCountVersionsInState( self, obj, state_id ):
        """
          Return count of version in state

          Arguments:

            'obj' -- object for which count are computed

            'state_id' -- state for counting

          Result:

            count of version in specified state (int)

        """

        self._log( function='_getCountVersionsInState', params=(obj, state_id) )

        return len( self._getVersionsInState( obj, state_id ) )

    def _areCountVersionsInStateValid( self, category_id, state_id, count_versions ):
        """
          Return true or false, in case if count of versions in specific state are valid or not.

          Arguments:

            'category_id' -- category id

            'state_id' -- state for check

            'count_versions' -- count of version in this state for check

          Result:

            Boolean

        """

        self._log( function='_areCountVersionsInStateValid', params=(category_id, state_id, count_versions) )

        # ask to configurations
        if state_id in self._getAllowOnlySingleVersionArray(category_id).keys() and count_versions>1:
            self._log( function='_areCountVersionsInStateValid', text='return false' )
            return 0
        self._log( function='_areCountVersionsInStateValid', text='return true' )
        return 1

    def _getVersionsForExclusion( self, obj, state_id ):
        """
          Returns version_id for exclusion from specific state

          Arguments:

            'obj' -- object for which are needed to exclude some version

            'state_id' -- state from which are needed to exclude version

          Result:

            A tuple.
        """

        self._log( function='_getVersionForExclusion', params=(obj, state_id) )

        versions_in_state = tuple(self._getVersionsInState( obj, state_id ))
        return versions_in_state

    def _getTransitionForExclusion( self, category_id, state_id ):
        """
          Return transition that are cofigured for state in category
          for exclusion version from state.

          Arguments:

            'category_id' -- category id

            'state_id' -- state from which are needed to exclude some version

          Result:

            transition id

        """

        self._log( function='_getTransitionForExclusion', params=(category_id, state_id) )

        # ask to configurations
        if state_id in self._getAllowOnlySingleVersionArray(category_id).keys():
            return self._getAllowOnlySingleVersionArray(category_id)[state_id]  # this is transition_id

        return None

    def _makeTransitionForVersion( self, obj, version_id, transition_id ):
        """
          Performs transition for version

          Arguments:

            'obj' -- object for which make transition

            'version_id' -- version for which needed make transition

            'transtion_id' -- trasnition for performs

          Algorithm:
            1. store to stack current document's version
            2. make 'version_id' as current document's version
            3. make transition (default Workflow's function)
            4. restore from stack stored document's version
            5. make restored version as current
        """

        self._log( function='_makeTransitionForVersion', params=(obj, version_id, transition_id) )

        # back current version
        back_version_id = obj.version[version_id].makeCurrent()

        # make transition
        self._secureBeforeTransition( self._getTransitionObject( obj, transition_id ) )
        try:
            self._portal_workflow().doActionFor( obj, transition_id )
        finally:
            self._secureAfterTransition( self._getTransitionObject( obj, transition_id ))

        # restore version
        obj.version[back_version_id].makeCurrent()

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
        return self._portal_workflow()[self._getWorkflowId(ob)].transitions[transition_id]

    def _getWorkflowId( self, ob ):
        """
          Return workflow id of object

          Arguments:

            'ob' -- object

          Result:

            return workflow id

        """
        return self._portal_metadata().getCategoryById( ob.Category() ).Workflow()

    def _isObjectValid( self, object ):
        """
          Check that object are handled.

          Arguments:

            'object' -- object for check

          Result:

            Boolean

        """

        self._log( function='_isObjectValid', params=(object) )

        # check that object are Document,
        # with versions

        return object.implements('isVersionable')

    def _getVersionsInState( self, object, state_id ):
        """
          Return versions in specific state

          Arguments:

            'object' -- object for which we see

            'state_id' -- state for which we see versions

          Result:

            return array of version's id in specific state of object

        """

        versions_in_state=[]
        for version_dict in object.listVersions():
            if version_dict['State'] == state_id:
                versions_in_state.append(version_dict['id'])
        return versions_in_state


    #---------------------------------------------------------------------------

    def _getStateIdByTransition( self, category_id, transition_id ):
        """
          Returns state_id where to transition_id lead.

          Arguments:

            'category_id' -- category of document

            'transition_id' -- transition

          Result:

            return state id

        """

        self._log( function='_getStateIdByTransition', params=(category_id, transition_id) )

        wf_id = self._portal_metadata().getCategoryById(category_id).Workflow()
        transition = self._portal_workflow()[wf_id].transitions[transition_id]

        return transition.new_state_id

    def _getCategory( self, object ):
        """
          Return category id of object

          Arguments:

            'object' -- object (generally HTMLDocument)

          Result:

            object's category id

        """

        return object.Category()


    def _portal_metadata( self ):
        return getToolByName( self, 'portal_metadata' )

    def _portal_workflow( self ):
        return getToolByName( self, 'portal_workflow' )

    #--------------------------------------------

    def _getAllowOnlySingleVersionArray( self, category_id ):
        """
          Returns 'allow_only_single_version' array, which keep configuration
          for what states can have only one version, and where to exclude version.

          Arguments:

            'category_id' -- category for which this information are asked

          Result:

            configuration array from category

        """
        return self._portal_metadata().getCategoryById( category_id ).allow_only_single_version

    #--------------------------------------------

    def _createNewVersionLogic( self, action, object ):
        """
          Logic for create or not new version

          Arguments:

            'action' -- wrapped method

            'object' -- object

        """
        if _checkPermission( action.getPerm(), object ):
            return

        if not _checkPermission( Permissions.CreateObjectVersions, object ):
            raise Unauthorized, 'You are not allowed to create new object versions in this context'

        roles = rolesForPermissionOn( action.getPerm(), object )
        if not Roles.VersionOwner in roles:
            raise Unauthorized, 'Version owner does not have modification rights within the current state'

        self._createNewVersion( object )

    #--------------------------------------------
    def _isActionWorkflowMethod( self, action ):
        """
        """
        return not isinstance( action, StringType )

    def _createNewVersion( self, object ):
        """
        """
        version = object.getVersion() # get version working with
        #document = version.aq_parent

        wf = object.getCategory().getWorkflow()
        wf_id = wf.getId()

        # state of 'base' version, with this state will be created new version
        state=self._portal_workflow().getStatusOf( wf_id, object )

        # check for exclusion from new state
        self._logicForVersionExclusion( object, new_state_id=state['state'] )

        state_for_new_version = deepcopy(state)
        state_for_new_version['actor'] = str( getSecurityManager().getUser() )
        state_for_new_version['time'] = DateTime()
        state_for_new_version['action'] = 'modify' # todo

        new_ver_id = object.createVersion(ver_id=version.id, title=version.title, description=version.description)
        object.getVersion(new_ver_id).makeCurrent()
        self._portal_workflow().setStatusOf( wf_id , object, state_for_new_version )
        wf.updateRoleMappingsFor(object)
        object.activateCurrentVersion()

    #--------------------------------------------

    def _log( self, function, text='', params='' ):
        return
        #print "\nClass VersionWorkflowLogic"
        print '\n'
        print " "+function
        if text=='return':
            print ' return: ',
            print params
            return
        if text:
            print " "+text
        if params:
            print " params: ",
            print params

InitializeClass( VersionWorkflowLogic )

from Products.DCWorkflow.Expression import StateChangeInfo, createExprContext

def check( self, sm, wf_def, ob ):
    expr = self.expr
    if expr is not None:
        econtext = createExprContext(StateChangeInfo(ob, wf_def))
        res = expr(econtext)
        if not res:
            return 0
    return 1
