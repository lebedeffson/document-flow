"""

  TaskDefinition abstract classes

  It consist of:
    -- model (TaskDefinition)
    -- controller (TaskDefinitionController)
    -- view (TaskDefinitionForm)
    -- register (TaskDefinitionRegistry)

  Them provide bases functions.

  Model - store fields, and have function for activate
  Controller - takes information from form and change model
  View - showing model
  Register - registration of action template (task definition) in
    factory (TaskDefinitionFactory)

$Editor: inemihin $
$Id: TaskDefinitionAbstract.py,v 1.26 2009/01/12 14:42:37 oevsegneev Exp $
"""
__version__ = '$Revision: 1.26 $'[11:-2]

from UserDict import UserDict

from AccessControl import ClassSecurityInfo
from Acquisition import Explicit, Acquired
from DateTime import DateTime
from ZODB.PersistentMapping import PersistentMapping

from Products.CMFCore.utils import _getAuthenticatedUser

from ActionInformation import ActionInformation
from Features import createFeature
from SimpleObjects import InstanceBase
from Utils import InitializeClass

#--------------------------------------------------------------
# abstract class
class TaskDefinition( InstanceBase ):
    """
      Abstract class-model.
    """
    _class_version = 1.01

    __implements__ = ( createFeature('isAction'),
                       createFeature('isCategoryAction'),
                       InstanceBase.__implements__ )

    type = ''

    parent_id = ''
    name = ''

    def __init__( self ):
        InstanceBase.__init__( self )

    def _initstate( self, mode ):
        """
            Initialize attributes
        """
        if not InstanceBase._initstate( self, mode ):
            return 0

        if getattr( self, 'vars', None ) is None:
            self.vars = PersistentMapping()

        if getattr( self, '_allow_edit', None ) is None:
            self._allow_edit = []

        return 1

    def Title( self ):
        return self.name

    def changeTo( self, task_definition ):
        """
          Changes self values to new

          Arguments:

            'task_definition' -- instance of TaskDefinition, to which
                                 needed to change

        """
        self.name = task_definition.name

        # XXX why needed clear
        self.vars.clear()
        self.vars.update( task_definition.vars )

    def toArray( self ):
        """
          Returns self values as array

          Arguments:

            'arr' -- array to which added new values

        """
        arr = {}
        arr["id"] = self.id
        arr["parent_id"] = self.parent_id
        arr["name"] = self.name
        arr["type"] = self.type
        arr['vars'] = dict(self.vars)
        # XXX
        if getattr( self, '_allow_edit', None ) is None:
            self._allow_edit = []
        arr['_allow_edit'] = self._allow_edit

        return arr

    def loadParams( self, context, object = None, as_first = False ):
        """
            Loads parameters for action. If parameter is bound up with variable
            from context, tries get it's value from that one, otherwise gets it from
            action's settings.

            Arguments:

              'as_first' -- flag to ignore parameters which are stored in the context
               (exclude the spec params)

            Result:

               Dictionary:
               >>  params = {
               >>     'param_name' : value,
               >>     ...,
               >>   }
        """
        param_names = self.toArray().keys()
        params = {}
        for name in param_names:
            if self.vars.has_key( name ):
                attr_id = self.vars[name]
                if not as_first and ( context.has_key( attr_id ) or object ):
                    params[name] = context.get( attr_id, object.getCategoryAttribute( attr_id ) )
                else:
                    params[name] = getattr( self, name, None )
            else:
                params[name] = getattr( self, name, None )

        spec_params = ['task_template_id', 'task_id']
        for sparam in spec_params:
            if context.has_key( sparam ):
                params[sparam] = context.get( sparam )

        self._v_params = params

    def saveParams( self, context ):
        """
        """
        output_params = getattr( self, '_output_params', [] )
        params_dict = self._v_params or {}
        for name in params_dict.keys():
            if self.vars.has_key( name ) and name not in output_params:
                context[name] = params_dict[name]

        for param in output_params:
            if self.vars.has_key( param ):
                context[self.vars[param]] = params_dict[param]

    def _getField( self, name ):
        """
            Return specific fields

            Arguments:

              'name' -- name of field

            Purpose of this method, is to handle the case when action teamplate's
            fields are changed during 'change_state' page. In this case we takes field's
            value from REQUEST, but not from 'self'.

        """
        form_name = "%s_%s" % ( self._v_params['task_template_id'], name )
        if self.allowEdit( name ) and self.amIonTop() and self.REQUEST.has_key( form_name ):
            # take from request
            # the last contition handle case when action template started automated,
            # in this case there is not any form
            value = self.REQUEST.get( form_name )
            if self.vars.has_key( name ):
                self._v_params[name] = value
            return value

        # otherwise return not changed value
        return self._v_params[name]

    def allowEdit( self, name ):
        return name in self._allow_edit

    def amIonTop( self ):
        """
          Checks whether taskDefinition are on top.

          Result:

            Boolean

        """
        return self.parent_id == '0'

    def activate( self, object, ret_from_up, transition ):
        """
          Activate taskDefinition (action template)

          Arguments:

            'object' -- object in context of which happened activation

            'ret_from_up' -- dictionary

          Result:

            Also return dictionary, which pass to next (inner)
            taskDefinition's activate (if is)

        """
        pass

    def getResultCodes( self ):
        """
          Return result codes

          Result:

            Return array of result codes
        """
        return []

InitializeClass( TaskDefinition )


class TaskDefinitionForm( Explicit ):
    """
      Class view (form)

    """
    _template = None

    getDtml = Acquired

    def getForm( self, taskDefinitionArray, namespace ):
        """
          Returns form (html)

          Arguments:

            'taskDefinitionArray' -- dictionary with values, which will be showed on form

            'namespace' -- DTML namespace object
        """
        form = self.getDtml( 'task_definition', namespace, taskDefinitionArray=taskDefinitionArray )
        if self._template:
            form += self.getDtml( self._template
                                 , namespace
                                 , taskDefinitionArray=taskDefinitionArray
                                 )
        return form

    def onSubmit(self, script='' ):
        """
          Returns javascript-fragment for validation form on submit

          Arguments:

            'script' -- initial value to add

        """
        return ''
        """
          if (! window.document.getElementsByName('name')[0].value) {
            alert('Please specify task definition name');
            return false;
          }
        """

    def onLoad(self):
        return ''

    # deprecated alias
    getTaskDefinitionFormScriptOnSubmit = onSubmit


class TaskDefinitionController:
    """
      Class controller

    """
    def getTaskDefinitionByRequest( self, request, taskDefinition ):
        """
          Returns taskDefinition instance (model) by request

          Arguments:

            'request' -- REQUEST

            'taskDefiniton' -- instance from upper instance of TaskDefinitionController

        """

        if request.has_key('name'): # action del
            taskDefinition.name = request['name']

        if request.has_key('parent_id'): # action add or del
            taskDefinition.parent_id = request['parent_id']

        if request.has_key('id_task_definition'): # action change or del
            taskDefinition.id = request['id_task_definition']

    def getEmptyArray( self ):
        """
          Returns array with empty values

          Arguments:

            'empty_array' -- array to fill

        """
        empty_array = {}
        empty_array['name'] = ''
        empty_array['vars'] = {}
        empty_array['_allow_edit'] = []
        return empty_array


class TaskDefinitionRegistry:
    """
      class provided information for factory about class
    """
    type_list = ()

    Controller = NotImplemented
    Form = NotImplemented

    dtml_token = None

    # XXX inherit this class from ActionInformation
    condition = None
    testCondition = ActionInformation.testCondition.im_func

    def getCategory( self ):
        return 'task_definition'

    def getTypeList( self ):
        """
          Returns list of handled action-types

          Return [{ "id": "id1", "title": "title1" }, ... ]
          "id" have to be unique for all task definitions
        """
        return self.type_list

    def getTitleByType( self, type ):
        """
          Returns title of action definition by type

          Arguments:

            'type' -- type of action

        """

        for type_item in self.type_list:
            if type_item['id']==type:
                return type_item['title']
        return ''

    def areSupportTaskDefinitionType( self, task_definition_type ):
        """
          Checks whether this taskDefinition (action template)
          support specific type

          Arguments:

            'task_definition_type' -- type to check

          Result:

            Boolan, true if supported, fasle - not

        """

        supported_ids = self._getTypeListAsIds()
        return ( task_definition_type in supported_ids )

    def getDtmlNameForInfoByType( self, task_definition_type ):
        """
          Returns dtml name, for showing of page 'change_state'

          Arguments:

            'task_definition_type' -- showing type

          Result:

            Dtml-file name

          On page 'change_state' user can see action templates which
          will be activated, and also user can change some fields of them.

          The dtml file name are: 'task_definition_%s_info_emb.dtml' % self.getDtmlTokenForInfoByType

        """
        template = self.getDtmlTokenForInfoByType( task_definition_type )
        if template:
            return 'task_definition_%s_info_emb' % template

    def getDtmlTokenForInfoByType( self, task_definition_type ):
        """
          Get 'token' for making full dtml-file-name,
          by mehod 'getDtmlNameForInfoByType'

          Arguments:

            'task_definition_type' -- action type

          Note:

            Overwrites in classes for have dtml
            for info on page 'change_state'
        """
        return self.dtml_token

    def getControllerImplementation( self, task_definition_type ):
        """
          Returns controller implementation

          Arguments:

            'task_definition_type' -- type of action

        """
        return self.Controller

    def getFormImplementation( self, task_definition_type ):
        """
          Returns form implementation

          Arguments:

            'task_defintioin_type' -- type of action

        """
        return self.Form

    def _getTypeListAsIds( self ):
        ids = []
        for item in self.type_list:
            ids.append( item['id'] )
        return ids

class ActionContext( UserDict ):
    """
        Common actions context class
    """
    def __init__( self ):
        """
            Initializes new 'ActionContext' instance.
        """
        UserDict.__init__( self )
        self['active_user'] = _getAuthenticatedUser( self ).getId()
        self['current_date'] = DateTime().earliestTime()
