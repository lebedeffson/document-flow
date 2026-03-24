"""
  TaskDefinitionMessage class

  This is example class. It show example of creation simple action template.

  This action template have only one field: 'message'

  This action havent practical application.

  And simple action: print message to console

$Editor: inemihin $
$Id: TaskDefinitionMessage.py,v 1.17 2005/08/23 11:36:21 vsafronovich Exp $
"""

from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry


#--------------------------------------------------------------
class TaskDefinitionMessage( TaskDefinition ):
    """
      Class-model.

      Have field 'message',
      and action print message to console
    """
    def __init__( self ):
        """
          Define field 'message'
        """
        TaskDefinition.__init__( self )
        self.type = 'message'
        self.message = ''

    def changeTo( self, taskDefinition ):
        """
          Changes field message to new value

          Arguments:

            'taskDefinition' -- new instance on TaskDefinitionMessage,
                                to which values needed to change self
        """
        TaskDefinition.changeTo( self, taskDefinition )
        # specific fields
        self.message = taskDefinition.message

    def toArray( self ):
        """
            We convert field 'message' to array
        """
        arr = TaskDefinition.toArray( self )
        arr["message"] = self.message
        return arr

    def activate( self, object, action, transition ):
        """
            Print message to console
        """
        print 'message: ' + self.message

#----------------------------------------------------------------
class TaskDefinitionFormMessage( TaskDefinitionForm ):
    """
      Class-view, define form for editing model's content (field 'message')

    """
    _template = 'task_definition_message'

#----------------------------------------------------------------
class TaskDefinitionControllerMessage( TaskDefinitionController ):
    """
      Class-controller, handle fields from form, and store them to model
    """
    def getEmptyArray( self ):
        """
          Returns empty array (field 'message')
        """
        emptyArray = TaskDefinitionController.getEmptyArray( self )
        emptyArray['message'] = ''
        return emptyArray

    def getTaskDefinitionByRequest( self, request ):
        """
          Parse request and return instance of model (class TaskDefinitionMessage)
        """
        taskDefinition = TaskDefinitionMessage()
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )
        # fill specific fields from request
        if request.has_key('message'):
            taskDefinition.message = request['message']
        return taskDefinition

#----------------------------------------------------------------
class TaskDefinitionRegistryMessage( TaskDefinitionRegistry ):
    """
      Class-registry, for registration this action template (task definition)
      in factory. Define supported types.
    """
    type_list = [ { "id": "message"
                  , "title": "Print message to console" 
                  },
                ]

    Controller = TaskDefinitionControllerMessage()
    Form = TaskDefinitionFormMessage()

    dtml_token = 'message'


def initialize( context ):
    context.registerAction( TaskDefinitionRegistryMessage() )
