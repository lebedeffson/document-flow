"""
  Action template for activating version ('Make version principal')

  It have to be assigned to appropriate transition.


$Id: TaskDefinitionActivateVersion.py,v 1.9 2005/08/23 11:36:21 vsafronovich Exp $

"""

from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry

#--------------------------------------------------------------
#
class TaskDefinitionActivateVersion( TaskDefinition ):
    """
      Activate version
    """
    type = 'activate_version'

    def activate( self, object, context, transition ):
        object.activateCurrentVersion()

#----------------------------------------------------------------
class TaskDefinitionFormActivateVersion( TaskDefinitionForm ):
    _template = 'task_definition_none'

#----------------------------------------------------------------
#
class TaskDefinitionControllerActivateVersion( TaskDefinitionController ):

    def getTaskDefinitionByRequest( self, request ):
        taskDefinition = TaskDefinitionActivateVersion()
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )
        return taskDefinition

#----------------------------------------------------------------

class TaskDefinitionRegistryActivateVersion( TaskDefinitionRegistry ):

    type_list = ( { "id": "activate_version"
                  , "title": "Make the version principal" 
                  },
                )
   
    Controller = TaskDefinitionControllerActivateVersion()
    Form = TaskDefinitionFormActivateVersion()

def initialize( context ):
    context.registerAction( TaskDefinitionRegistryActivateVersion() )
