"""
  ActionTimer classes

$Editor: mbernatski $
$Id: ActionTimer.py,v 1.11 2006/04/17 07:26:50 ishabalin Exp $
"""
__version__ = '$Revision: 1.11 $'[11:-2]

from Products.CMFCore.utils import getToolByName
from Products.NauScheduler.TemporalExpressions import DateTimeTE

from Utils import InitializeClass

from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry

#-------------------------------------------------------------------
class ActionSetTimer( TaskDefinition ):
    """
      Class-model.
    """

    _class_version = 1.1

    type = 'set_timer'

    transition = ''
    attribute_name = ''

    def toArray( self ):
        """
          Converting object's fields to dictionary

          Result:

            Dictionary as { 'field_name': 'field_value', ... }

        """
        arr = TaskDefinition.toArray( self )
        # specific fields
        arr['transition'] = self.transition
        arr['attribute_name'] = self.attribute_name
        return arr

    def changeTo( self, taskDefinition ):
        """
          Changes object's values to news

          Arguments:

            'taskDefinition' -- object to values of which need to change self

        """
        TaskDefinition.changeTo( self, taskDefinition )
        # specific fields
        self.transition = taskDefinition.transition
        self.attribute_name = taskDefinition.attribute_name

    def activate( self, object, ret_from_up, transition ):
        """
          Create new action in the planner which makes transition for the object
          in the fixed time

          Arguments:

            'object' -- object for which transition will be maden (generally HTMLDocument)

            'ret_from_up' -- dictionary from previous 'action', if this action template
                             are included, otherwise dictionary have key 'task_template_id'
                             which have id of task_template, this attribut are stored to task

        """

        planner = getToolByName( self, 'portal_scheduler', None )
        wftool = getToolByName( self, 'portal_workflow', None )

        if planner and wftool and getattr( object, 'docflow_timer_id', None ) is None:
            new_transition = self.transition
            title = 'Do transition ' + new_transition + ' for ' + object.id
            temporal_expr = DateTimeTE( self._getField( 'attribute_name', object ) )
            schedule_id = planner.addScheduleElement( wftool.doActionFor
                                                         , temporal_expr=temporal_expr
                                                         , title=title
                                                         , args=(object, new_transition)
                                                         )
            object.docflow_timer_id = schedule_id

        return {} # there is no passed-to-childs return codes

    def _getField( self, name, object ):
        """
          Return specific fields

          Arguments:

            'name' -- name of field

            'object' -- object for which transition will be maden (generally HTMLDocument)

          Purpose of this method, is to handle the case when action teamplate's
          fields are changed during 'change_state' page.

        """
        v = getattr( self, name, None )
        if v is not None and name == 'attribute_name':
            if hasattr( self, 'REQUEST') and self.REQUEST.has_key('date_value'):
                # take from request
                v = self.REQUEST.get( 'date_value' )
            else:
                v = object.getCategoryAttribute( attr=getattr( self, name ) , default=None )
        return v

InitializeClass( ActionSetTimer )


class ActionFormSetTimer( TaskDefinitionForm ):
    """
      Class-view.

      Showing form for edit action template's fields.

    """
    _template = 'task_definition_set_timer'

#----------------------------------------------------------------
class ActionControllerSetTimer( TaskDefinitionController ):
    """
      Class-controller.

    """
    def getEmptyArray( self ):
        """
          Return empty dictionary

        """
        emptyArray = TaskDefinitionController.getEmptyArray( self )
        emptyArray['transition'] = ''
        emptyArray['attribute_name'] = ''
        return emptyArray

    def getTaskDefinitionByRequest( self, request ):
        """
          Return task definition instance by request

          Arguments:

            'request' -- REQUEST

          Result:

            Filled by form 'ActionSetTimer' instance

        """
        taskDefinition = ActionSetTimer()
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )
        # fill specific fields from request
        #
        if request.has_key('transition'):
            taskDefinition.transition = request['transition']
        if request.has_key('attribute_name'):
            taskDefinition.attribute_name = request['attribute_name']

        return taskDefinition

#----------------------------------------------------------------

class ActionRegistrySetTimer( TaskDefinitionRegistry ):
    """
      Class-registry

      Register information to factory.

    """
    type_list = [ { "id": "set_timer"
                  , "title": "Set timer"
                  },
                ]

    Controller = ActionControllerSetTimer()
    Form = ActionFormSetTimer()

    dtml_token = 'set_timer'

#ClearTimer's part
#-------------------------------------------------------------------
class ActionClearTimer( TaskDefinition ):
    """
      Class-model.
    """

    _class_version = 1.0

    def __init__( self ):
        TaskDefinition.__init__( self )
        # specific fields
        self.type = 'clear_timer'

    def toArray( self ):
        """
          Converting object's fields to dictionary

          Result:

            Dictionary as { 'field_name': 'field_value', ... }

        """
        arr = TaskDefinition.toArray( self )
        return arr

    def activate( self, object, ret_from_up, transition ):
        """
          Deletes task from scheduler and 'docflow_timer_id' attribute for object

          Arguments:

            'object' -- object for which transition will be maden (generally HTMLDocument)

            'ret_from_up' -- dictionary from previous 'action', if this action template
                             are included, otherwise dictionary have key 'task_template_id'
                             which have id of task_template, this attribut are stored to task

        """
        planner = getToolByName( self, 'portal_scheduler', None )
        schedule_id = getattr(object, 'docflow_timer_id', None)
        if planner and schedule_id is not None:
            planner.delScheduleElement( schedule_id )
            delattr( object, 'docflow_timer_id' )


InitializeClass( ActionClearTimer )

class ActionFormClearTimer( TaskDefinitionForm ):
    """
      Class-view.

      Showing info form.

    """
    _template = 'task_definition_clear_timer'

#----------------------------------------------------------------
class ActionControllerClearTimer( TaskDefinitionController ):
    """
      Class-controller.

    """
    def getTaskDefinitionByRequest( self, request ):
        """
          Return task definition instance by request

          Arguments:

            'request' -- REQUEST

        """
        taskDefinition = ActionClearTimer()
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )

        return taskDefinition

#----------------------------------------------------------------

class ActionRegistryClearTimer( TaskDefinitionRegistry ):
    """
      Class-registry

      Register information to factory.

    """
    type_list = ( { "id": "clear_timer"
                       , "title": "Clear timer" 
                       },
                     )
    Controller = ActionControllerClearTimer()
    Form = ActionFormClearTimer()

    dtml_token =  'clear_timer'


def initialize( context ):
    context.registerAction( ActionRegistrySetTimer() )
    context.registerAction( ActionRegistryClearTimer() )
