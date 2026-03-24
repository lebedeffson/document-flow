"""
  Action template for creating version

  It have to be assigned to appropriate transition.


$Editor: oevsegneev $
$Id: TaskDefinitionCreateVersion.py,v 1.19 2008/08/13 10:29:32 oevsegneev Exp $

"""

from copy import deepcopy

from DateTime import DateTime

from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import getToolByName


#--------------------------------------------------------------
#
class TaskDefinitionCreateVersion( TaskDefinition ):
    """
      Create version
    """

    _class_version = 1.00

    def __init__( self ):
        TaskDefinition.__init__( self )
        self.type = 'create_version'
        self.version_state = None

    def _initstate( self, mode ):
        """
            Initialize attributes
        """
        if not TaskDefinition._initstate( self, mode ):
            return 0

        if not hasattr( self, 'version_state' ):
            self.version_state = None

        return 1

    def changeTo( self, taskDefinition ):
        TaskDefinition.changeTo( self, taskDefinition )
        self.version_state = taskDefinition.version_state

    def toArray( self ):
        arr = TaskDefinition.toArray( self )
        arr['version_state'] = self.version_state
        return arr

    def activate( self, object, context, transition ):
        version = object.getVersion()
        workflow_tool = getToolByName( self, 'portal_workflow' )
        membership = getToolByName(self, 'portal_membership')
        wf = object.getCategory().getWorkflow()
        wf_id = wf.getId()
        kw = {}
        if self.version_state == 'keep_state':
            kw['keep_state'] = True;
            state = workflow_tool.getStatusOf( wf_id, object )
            state_id = state.get('state')
        else:
            state_id = self.version_state

        # If new state id is the same as the initial state, just do nothing.
        if wf.initial_state != state_id:
            new_state = {   'comments'    : '',
                            'action'      : '',
                            'time'        : DateTime(),
                            'principal_version': object.getPrincipalVersionId(),
                            'actor'       : membership.getAuthenticatedMember().getId(),
                            'state'       : state_id
                            }
            kw['new_state'] = new_state

        new_ver_id = object.createVersion( ver_id=version.id,
                                           title=version.title,
                                           description=version.description,
                                           **kw
                                         )
        object.getVersion( new_ver_id ).makeCurrent()

#----------------------------------------------------------------
class TaskDefinitionFormCreateVersion( TaskDefinitionForm ):
    """
    """
    _template = 'task_definition_create_version'
    
#----------------------------------------------------------------
#
class TaskDefinitionControllerCreateVersion( TaskDefinitionController ):

    def getEmptyArray( self ):
        emptyArray = TaskDefinitionController.getEmptyArray( self )
        emptyArray['version_state'] = 0
        return emptyArray

    def getTaskDefinitionByRequest( self, request ):
        taskDefinition = TaskDefinitionCreateVersion()
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )
        if request.has_key('version_state'):
            taskDefinition.version_state = request.get('version_state')
        return taskDefinition

#----------------------------------------------------------------

class TaskDefinitionRegistryCreateVersion( TaskDefinitionRegistry ):
    type_list = ( { "id": "create_version"
                  , "title": "Create new version" 
                  },
                )

    Controller = TaskDefinitionControllerCreateVersion()
    Form = TaskDefinitionFormCreateVersion()


def initialize( context ):
    context.registerAction( TaskDefinitionRegistryCreateVersion() )
