"""
$Id: TaskDefinitionRegisterVersion.py,v 1.11 2006/06/22 11:27:15 oevsegneev Exp $
Action template for registering document version in a registry.
$Editor: ishabalin $
"""

__version__ = '$Revision: 1.11 $'[11:-2]

from Exceptions import SimpleError, LocatorError

from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import InitializeClass, getToolByName
from ResourceUid import ResourceUid


class TaskDefinitionRegisterVersion(TaskDefinition):
    """
        Registers document version in the specified registry.
    """

    _class_version = 1.00

    type = 'register_version'

    registry_uid = None

    def changeTo( self, taskDefinition ):
        """
            Changes self data.

            Arguments:
                'taskDefinition' -- instance of TaskDefinition
        """
        TaskDefinition.changeTo( self, taskDefinition )

        # specific fields
        self.registry_uid = taskDefinition.registry_uid

    def toArray( self ):
        """
            Converts object's fields to dictionary

            Result:
                Dictionary as { 'field_name': 'field_value', ... }
        """
        arr = TaskDefinition.toArray( self )
        arr["registry_uid"] = self.registry_uid
        return arr

    def activate(self, object, context, transition):
        """
            Activate taskDefinition (action template)

            Arguments:
                'object' -- object in context of which happened activation
                'ret_from_up' -- dictionary

            Result:
                Also returns dictionary, which is passed to next (inner) taskDefinition's activate (if presented)
        """

        try:
            registry = ResourceUid( self.registry_uid ).deref(object)
        except LocatorError:

            registry = None
        if not registry:
            raise SimpleError( "Task template '%(task)s' is not configured properly.", task=self )

        result = registry.register(object)

    def getResultCodes( self ):
        """
            Return result codes.
            There are no result codes for this task definition.

            Result:
                Return array of result codes.
        """

        return {}


InitializeClass (TaskDefinitionRegisterVersion)


class TaskDefinitionFormRegisterVersion(TaskDefinitionForm):
    """
      Class view (form)
    """
    _template = 'task_definition_register_version'

class TaskDefinitionControllerRegisterVersion(TaskDefinitionController):
    """
      Class controller
    """
    def getEmptyArray(self):
        """
            Returns dictionary with empty values.

            Arguments:
                'emptyArray' -- dictionary to fill
        """
        array = TaskDefinitionController.getEmptyArray(self)
        array['registry_uid'] = None
        return array


    def getTaskDefinitionByRequest( self, request ):
        """
            Gets destination folder uid from request and stores it in
            TaskDefinitionRegisterVersion () instance.
        """
        taskDefinition = TaskDefinitionRegisterVersion ()
        TaskDefinitionController.getTaskDefinitionByRequest (self, request, taskDefinition)

        if request.has_key('registry_uid'):
            taskDefinition.registry_uid = request['registry_uid']
        return taskDefinition


class TaskDefinitionRegistryRegisterVersion(TaskDefinitionRegistry):
    """
        Class that provides information for factory about class
    """
    type_list = ( { "id": "register_version"
                  , "title": "Register document version" 
                  },
                )

    Controller = TaskDefinitionControllerRegisterVersion()
    Form = TaskDefinitionFormRegisterVersion()

    dtml_token = "register_version"

def initialize( context ):
    # module initialization callback

    context.registerAction( TaskDefinitionRegistryRegisterVersion() )
