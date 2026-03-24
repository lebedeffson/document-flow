"""
  TaskDefinitionFactory class

  Purpose of this class is to have all-in-one-class
  function to register new action templates (taskDefinition)

  To provide single interface to ask about title, handler types, supported types,
  form, controller implementation from instance of TaskDefintionRegistry
  (from which have to be inheritanced all other action template's registry classes)

$Editor: inemihin $
$Id: TaskDefinitionFactory.py,v 1.20 2006/02/09 11:57:27 vsafronovich Exp $
"""
__version__ = '$Revision: 1.20 $'[11:-2]

from Acquisition import Implicit, aq_base, aq_parent
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from SimpleObjects import Persistent
from Utils import InitializeClass


class TaskDefinitionFactory( Persistent, Implicit ):
    """
      This class have only one instance,
      in MetadataTool.

    """
    _class_version = 1.8

    security = ClassSecurityInfo()

    def _initstate( self, mode ):
        if not Persistent._initstate( self, mode ):
            return 0

        if hasattr( self, 'taskDefinitionRegistryList' ): # < 1.8
            del self.taskDefinitionRegistryList

        return 1

    security.declareProtected( CMFCorePermissions.ManagePortal, 'listActionTemplateTypes' )
    def listActionTemplateTypes( self ):
        """
          Returns list of registered action templates

        """

        results = []
        actions = getToolByName( self, 'portal_actions' )

        for id, registry in actions.listActionsByCategory( 'task_definition', tuples=True ):
            for item in registry.getTypeList():
                if item['id'] == id:
                    results.append( item )
                    break

        return results


    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskDefinitionTypeList' )
    def getTaskDefinitionTypeList( self, as='' ):
        """
          Returns list of registered action templates

        """
        import warnings
        warnings.warn('TaskDefinitionFactory.getTaskDefinitionTypeList'
                      ' deprecated and will be removed in ND 3.6,'
                      ' use listActionTemplateTypes instead', DeprecationWarning, stacklevel=3)

        return self.listActionTemplateTypes()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskDefinitionFormByTaskType' )
    def getTaskDefinitionFormByTaskType( self, task_definition_type, taskDefinitionArray=None, mode=None, template_id=None, parent_id=None, namespace=None ):
        """
          Returns form for specific task definition type

          Arguments:

            'task_definition_type' -- type of task definition

            'taskDefinitionArray' -- array of values (if form for 'change')

            'mode' -- mode of show ('add', 'change')

          Result:

            Return html-form for specific task definition

        """
        controller = self._getControllerImplementationByTaskDefinitionType( task_definition_type )
        form = self._getFormImplementationByTaskDefinitionType( task_definition_type )

        if taskDefinitionArray is None: # i.e. action add
            taskDefinitionArray = controller.getEmptyArray()
            taskDefinitionArray['type'] = task_definition_type

        # _mode, for analize in dtml (mode - 'add', 'change')
        taskDefinitionArray['_mode'] = mode

        if template_id:
            taskDefinitionArray['_template_id'] = template_id
        if parent_id:
            taskDefinitionArray['_parent_id'] = parent_id
        return form.getForm( taskDefinitionArray, namespace )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskDefinitionFormScriptOnSubmit' )
    def getTaskDefinitionFormScriptOnSubmit( self, task_definition_type ):
        """
          Returns java-script fragment for form's onSubmit, for specific task_definition_type

          Arguments:

            'task_definition_type' -- type of task definition

          Result:

            Java-script fragment for valid form onSubmit.

        """
        form = self._getFormImplementationByTaskDefinitionType( task_definition_type )
        return form.onSubmit()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskDefinitionFormScriptOnLoad' )
    def getTaskDefinitionFormScriptOnLoad( self, task_definition_type, task_definition=None ):
        """
          Returns java-script fragment for form's onLoad, for specific task_definition_type

          Arguments:

            'task_definition_type' -- task definition type

            'task_definition' -- array of values of task_definition, for initialize

        """
        form = self._getFormImplementationByTaskDefinitionType( task_definition_type )
        return form.onLoad()

    security.declarePublic( 'getTaskDefinitionTypeTitle' )
    def getTaskDefinitionTypeTitle( self, task_definition_type ):
        """
          Returns title of task definition type

          Arguments:

            'task_definition_type' -- type of task definition

        """
        registry = self._getTaskDefinitionRegistrySupportedTaskDefinitionType( task_definition_type )
        return registry.getTitleByType( task_definition_type )

    security.declarePublic( 'getDtmlNameForInfoByType' )
    def getDtmlNameForInfoByType( self, task_definition_type ):
        """
          Returns dtml name for show form for specific task_definition_type on page
          'change_state'

          Arguments:

            'task_definition_type' -- task definition type

        """
        registry = self._getTaskDefinitionRegistrySupportedTaskDefinitionType( task_definition_type )
        return registry.getDtmlNameForInfoByType( task_definition_type )

#----------------

    # from TaskTemplateContainerAdapter makeTaskDefinitionActionByRequest()
    def getTaskDefinitionByRequest( self, task_definition_type, request ):
        """
          Returns specific task definition instance from request

          Arguments:

            'task_definition_type' -- type of task definition to get

            'request' -- REQUEST


          Result:

            Inherit from 'TaskDefinition' class

          Get specific controller, and from it get instance of model

        """
        controller = self._getControllerImplementationByTaskDefinitionType( task_definition_type )
        return controller.getTaskDefinitionByRequest( request )

    def createTaskDefinition( self, type, template, parent=None ):
        controller = self._getControllerImplementationByTaskDefinitionType( type )

        if hasattr( controller, 'createTaskDefinition' ):
            tdef = controller.createTaskDefinition()
        else:
            tdef = controller.getTaskDefinitionByRequest( {'context':self} )

        if parent is not None:
            tdef.parent_id = parent

        return template.addTaskDefinition( tdef )

    def _getControllerImplementationByTaskDefinitionType( self, task_definition_type ):
        """
          Returns class-controller implementation by task definition type

          Arguments:

            'task_definition_type' -- type of task definition

          Result:

            Inherit from 'TaskDefinitionController' class

        """
        registry = self._getTaskDefinitionRegistrySupportedTaskDefinitionType( task_definition_type )
        if registry is not None:
            return registry.getControllerImplementation( task_definition_type )
        raise ValueError( task_definition_type )

    def _getFormImplementationByTaskDefinitionType( self, task_definition_type ):
        """
          Returns class-form implementation by task defintion type

          Arguments:

            'task_definition_type' -- task of task defintion

          Result:

            Inherit from 'TaskDefinitionForm' class

        """
        registry = self._getTaskDefinitionRegistrySupportedTaskDefinitionType( task_definition_type )
        if registry is not None:
            form = registry.getFormImplementation( task_definition_type ).__of__( self )
            return form
        raise ValueError( task_definition_type )

    def _getTaskDefinitionRegistrySupportedTaskDefinitionType( self, task_definition_type ):
        """
          Returns task definition registry class which support specific task_definition_type

          Arguments:

            'task_definition_type' -- type of task definition

          Result:

            Inherit from 'TaskDefinitionRegistry' class

        """
        actions = getToolByName( self, 'portal_actions' )
        try:
            return actions.getActionInfo( task_definition_type )
        except KeyError:
            return None

    # used by *Form classes
    # TODO: move to other place
    def getDtml( self, template_name, namespace, **kw ):
        """
          Returns parsed dtml-template

          Arguments:

            'template_name' -- name of dtml to return

            'namespace' -- DTML namespace object

            '**kw' -- additional parameters to dtml

          Result:

            Parsed dtml

        """
        # TODO move to skins tool
        skins = getToolByName( self, 'portal_skins' )
        skin  = skins.getSkinByName( skins.getDefaultSkin() )
        template = getattr( skin, template_name, None )
        if template is None:
            raise KeyError, template_name
        template = aq_base( template ).__of__( skins.parent() )

        return template( aq_parent(self), namespace, **kw )

InitializeClass( TaskDefinitionFactory )
