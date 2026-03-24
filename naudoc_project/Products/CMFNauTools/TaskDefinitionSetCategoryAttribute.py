"""
  TaskDefinitionSetCategoryAttribute class

$Editor: inemihin $
$Id: TaskDefinitionSetCategoryAttribute.py,v 1.20 2008/03/06 09:47:01 oevsegneev Exp $
"""
from types import StringType
from DateTime import DateTime

from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry

from Utils import InitializeClass, getToolByName, readLink, updateLink
from ResourceUid import ResourceUid

#--------------------------------------------------------------
class TaskDefinition_SetCategoryAttribute( TaskDefinition ):
    """
        Class-model

        Action sets category attribute 'attribute_name' to 'attribute_value' value
    """

    _output_params = ( 'attribute_value', )

    def __init__( self ):
        """
            Initialize 'TaskDefinition_SetCategoryAttribute' instance
        """
        TaskDefinition.__init__( self )
        self.type = 'set_category_attribute'
        self.attribute_name = None
        self.attribute_value = None

    def changeTo( self, taskDefinition ):
        """
            Changes action parameters to new values

            Arguments:

              'taskDefinition' -- new instance on TaskDefinition_SetCategoryAttribute,
                                  to which values needed to change self
        """
        TaskDefinition.changeTo( self, taskDefinition )
        self._allow_edit = taskDefinition._allow_edit

        name  = taskDefinition.attribute_name
        value = taskDefinition.attribute_value

        if name is None:
            attr  = None
            value = None
        else:
            attr = self.parent().parent().getAttributeDefinition( name )
            if attr.Type() == 'link':
                # update link to the target value
                value = updateLink( self, 'property', 'value', value )
            else:
                # drop link to the old value just in case
                updateLink( self, 'property', 'value', None )

        # update link to the attribute definition
        updateLink( self, 'property', 'name', attr )

        # specific fields
        self.attribute_name  = name
        self.attribute_value = value

    def toArray( self ):
        """
            We convert action fields to array
        """
        arr = TaskDefinition.toArray( self )
        name  = self.attribute_name
        value = self.attribute_value

        if name is not None:
            attr = self.parent().parent().getAttributeDefinition( name )
            if attr.Type() == 'link':
                value = readLink( self, 'property', 'value', value, moniker=True )

        arr['attribute_name']  = name
        arr['attribute_value'] = value

        return arr

    def activate( self, object, context, transition ):
        """
            Setting attribute of document
        """
        self.loadParams( context, as_first = True )

        name = self._getField( 'attribute_name' )

        attr  = self.parent().parent().getAttributeDefinition( name )
        value = self._getField( 'attribute_value' )

        if attr.Type() == 'date' and not value:
            value = DateTime()
        elif attr.Type() == 'link' and not isinstance(value, ResourceUid):
            value = readLink( self, 'property', 'value', value )

        # check if there is passed from top 'new_doc_uid'
        if context.has_key( 'new_doc_uid' ):
            catalog = getToolByName( self, 'portal_catalog' )
            object = catalog.getObjectByUid( context['new_doc_uid'] )

        # set attribute without permission checking
        object._setCategoryAttribute( name, value )

        self.saveParams( context )

    def _getDateNow( self ):
        return DateTime(str(DateTime()).split(' ')[0])

    def _instance_onDestroy( self ):
        updateLink( self, 'property', 'name', None )
        updateLink( self, 'property', 'value', None )

InitializeClass( TaskDefinition_SetCategoryAttribute )


#----------------------------------------------------------------
class TaskDefinitionForm_SetCategoryAttribute( TaskDefinitionForm ):
    """
      Class-view, define form for editing model's content (field 'message')

    """
    _template = 'task_definition_set_category_attribute'

#----------------------------------------------------------------
class TaskDefinitionController_SetCategoryAttribute( TaskDefinitionController ):
    """
      Class-controller, handle fields from form, and store them to model
    """
    def getEmptyArray( self ):
        """
          Returns empty array (field 'message')
        """
        emptyArray = TaskDefinitionController.getEmptyArray( self )
        emptyArray['attribute_name']  = None
        emptyArray['attribute_value'] = None  # <-- default value
        return emptyArray

    def getTaskDefinitionByRequest( self, request ):
        """
          Parse request and return instance of model (class TaskDefinitionSetCategoryAttribute)
        """
        var_postfix='_var'
        taskDefinition = TaskDefinition_SetCategoryAttribute()
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )
        # fill specific fields from request
        if request.has_key( 'attribute_name' ):
            taskDefinition.attribute_name = request['attribute_name']

        if request.has_key( 'attribute_value' ):
            taskDefinition.attribute_value = request['attribute_value']

        if request.has_key('_allow_edit'):
            taskDefinition._allow_edit = request['_allow_edit']
        else:
            taskDefinition._allow_edit = []

        for param in taskDefinition._output_params:
            if request.has_key( param+var_postfix ):
                taskDefinition.vars[param] = request[param+var_postfix]


        return taskDefinition

#----------------------------------------------------------------
class TaskDefinitionRegistry_SetCategoryAttribute( TaskDefinitionRegistry ):
    """
      Class-registry, for registration this action template (task definition)
      in factory. Define supported types.
    """
    type_list = ( { "id": "set_category_attribute"
                  , "title": "Set category attribute" 
                  },
                )

    Controller = TaskDefinitionController_SetCategoryAttribute()
    Form = TaskDefinitionForm_SetCategoryAttribute()

    dtml_token = 'set_category_attribute'

def initialize( context ):
    context.registerAction( TaskDefinitionRegistry_SetCategoryAttribute() )
