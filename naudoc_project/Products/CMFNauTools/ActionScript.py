"""
$Id: ActionScript.py,v 1.18 2006/04/17 12:33:16 ikuleshov Exp $
Action template for execution script.
$Editor: mbernatski $
"""

__version__ = '$Revision: 1.18 $'[11:-2]

from BTrees.OOBTree import OOBTree
from Products.CMFCore.utils import _getAuthenticatedUser

from Monikers import Moniker
from Script import DefaultScriptNamespace, registerNamespace
from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import InitializeClass, getToolByName, updateLink
from ResourceUid import ResourceUid


class ActionScript( TaskDefinition ):
    """
       Evaluate the existing script in the system.
    """
    _class_version = 1.01

    def __init__( self ):
        """
            Creates new instance.
        """
        TaskDefinition.__init__( self )
        self.script_ruid = None
        self.parameters = OOBTree()
        self.type = 'script'

    def toArray( self ):
        """
          Converts object's fields to dictionary

          Result:

            Dictionary as { 'field_name': 'field_value', ... }

        """
        arr = TaskDefinition.toArray( self )
        arr['script'] = self.getScript( mode = 2 )
        arr['parameters'] = self.getParameters( moniker=1 )
        return arr

    def changeTo( self, taskDefinition ):
        """
          Changes object's values to news

          Arguments:

            'taskDefinition' -- new instance on ActionScript,
                                to which values needed to change self
        """
        TaskDefinition.changeTo( self, taskDefinition )
        # specific fields
        self.script_ruid = taskDefinition.getScript( mode = 1 )
        parameters = taskDefinition.listParameters()
        for param in parameters:
            if param['data_type'] == 'link':
                link_id = updateLink( self, 'property', param['id'], value=param['value'] )
                taskDefinition.editParameter( param['id'], link_id )
        self.parameters = taskDefinition.parameters

    def activate( self, object, context, transition ):
        """
            Call the script's method 'evaluate'
        """
        user = _getAuthenticatedUser( self ).getId()
        portal = self.getPortalObject()
        namespace = ActionScriptNamespace( object, user, portal, transition, context=context )
        self.getScript( mode = 2, portal = portal ).evaluate( namespace=namespace, parameters=self.getParameters(), raise_exc=True )

    def getScript( self, mode = None, portal = None ):
        """
           Returns the Resource Uid of the script if mode = 1.
           Returns the script as object if mode = 2.

           Result:

               Resource Uid of the script object or script as object.
        """

        if mode == 1:
            return self.script_ruid
        elif mode == 2:
            return self.script_ruid \
                   and self.script_ruid.deref( portal or self ) or None
    	
    def setScript( self, script, portal = None ):
        """
           Sets Resource Uid of script.
        """
        if script:
            self.script_ruid = ResourceUid( script, context = portal )

    def addParameter( self, id, data_type, title, value ):
        """
            Sets the parameter to the script template.
        """
        self.parameters.insert( id, { 'id'          :  id
                                     , 'data_type'  :  data_type
                                     , 'title'      :  title
                                     , 'value'      :  value
                                     })

    def editParameter( self, id, value ):
        """
            Edit the parameter's value.
        """
        data_type = self.parameters[id]['data_type']
        title = self.parameters[id]['title']
        self.parameters.__setitem__( id, { 'id'         :  id
                                         , 'data_type'  :  data_type
                                         , 'title'      :  title
                                         , 'value'      :  value
                                          })

    def listParameters( self ):
        """
            Returns the list of the template parameters.

            Result:

              List of parameters.
        """
        parameters = self.parameters.values()
        return list( parameters )

    def getParameters( self, moniker=False ):
        """
           Returns dictionary of the script's parameters for this action.

           Result:

               Dictionary as { 'parameter_name': 'parameter_value', ... }
        """
        result = {}
        links_tool = getToolByName( self, 'portal_links' )
        parameters = self.listParameters()
        for param in parameters:
            if param['data_type'] == 'link':
                value = param['value'] is not None and links_tool[ param['value'] ] or None
                if value is None:
                    result[param['id']] = None
                elif moniker:
                    result[param['id']] = Moniker( value )
                else:
                    result[param['id']] = value.getTargetObject()
            else:
                result[param['id']] = param['value']

        return result

#----------------------------------------------------------------
class ActionFormScript( TaskDefinitionForm ):
    """
      Class-view, define form for editing model's content.

    """
    _template = 'task_definition_script'

#----------------------------------------------------------------
class ActionControllerScript( TaskDefinitionController ):
    """
      Class-controller, handle fields from form, and store them to model
    """
    def getEmptyArray( self ):
        """
          Returns empty array
        """
        emptyArray = TaskDefinitionController.getEmptyArray( self )
        emptyArray['script'] = None
        emptyArray['parameters'] = {}
        return emptyArray

    def getTaskDefinitionByRequest( self, request ):
        """
          Parse request and return instance of model (class ActionScript)
        """
        action = ActionScript()
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, action )
        portal = request.get('context', None) or request.get('portal', None)
        portal = portal.getPortalObject()
        # fill specific fields from request
        if request.has_key('script'):
            action.setScript( request['script'], portal = portal )

        if request.has_key('parameters'):
            r = request.get
            for param in action.getScript( mode = 2, portal = portal ).listParameters():
                cid = param['id']
                title = param['title']
                typ = param['data_type']
                if typ == 'date':
                    value = parseDate('value_%s' % cid, request, default=None )
                    if value:
                        value = str(value)
                elif typ == 'lines':
                    value = list(r('value_%s' % cid))
                    if len(value) == 1 and not len(value[0]):
                        # empty textarea gets parsed by Zope into
                        # a single-element list containing an empty string
                        value.pop(0)
                else:
                    value = r('value_%s' % cid)
                action.addParameter( cid, typ, title, value )

        return action

#----------------------------------------------------------------
class ActionRegistryScript( TaskDefinitionRegistry ):
    """
      Class-registry, for registration this action template
      in factory. Define supported types.
    """
    type_list = ( { "id": "script"
                  , "title": "Execute system script" 
                  },
                )

    Controller = ActionControllerScript()
    Form = ActionFormScript()

    dtml_token = 'script'

class ActionScriptNamespace( DefaultScriptNamespace ):
    """
        Action script namespace.
    """

    _class_version = 1.0

    namespace_type = 'action_script_namespace'

    def __init__( self, object, user, portal, transition='', **kw  ):
        DefaultScriptNamespace.__init__( self, object, user, portal )
        self.object = object
        self.transition = transition
        if kw.has_key( 'context' ):
            self.context = kw['context']

def initialize( context ):
    # module initialization callback
    context.registerAction( ActionRegistryScript() )
    context.registerNamespace( ActionScriptNamespace )
