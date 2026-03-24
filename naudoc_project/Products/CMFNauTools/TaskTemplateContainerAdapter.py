"""
TaskTemplateContainerAdapter class

  Purpose of this class is to provide access to inner classes structures
  (TaskTemplateContainer) from dtml pages (like interface to dtmls)

  Generally this class dont have self logic, but provide security access to logic.


$Editor: inemihin $
$Id: TaskTemplateContainerAdapter.py,v 1.29 2006/02/09 11:45:31 vsafronovich Exp $
"""
__version__ = '$Revision: 1.29 $'[11:-2]

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, Acquired

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import ManagePortal

from SimpleObjects import Persistent
from Exceptions import DuplicateIdError
from TaskTemplateContainer import TaskTemplate
from Utils import InitializeClass
from Products.CMFCore.utils import getToolByName

class TaskTemplateContainerAdapter( Persistent, Implicit ):
    _class_version = 1.3

    security = ClassSecurityInfo()

    taskDefinitionFactory = Acquired
    getCategoryById = Acquired

    def _initstate( self, mode ):
        if not Persistent._initstate( self, mode ):
            return False

        if hasattr( self, 'taskTemplateContainer' ): # < 1.2
            del self.taskTemplateContainer

        if self.__dict__.has_key( 'taskDefinitionFactory' ): # < 1.3
            del self.taskDefinitionFactory

        return True

    #========================[ task template work ]========================

    security.declareProtected( CMFCorePermissions.ManagePortal, 'makeActionByRequest' )
    def makeActionByRequest( self, category_id, action, request ):
        """
          Make action over task template by request

          Arguments:

            'category_id' -- id of category

            'action' -- action

            'request' -- REQUEST

        """
        taskTemplate = self.getTaskTemplateFromRequest( request )

        ttcontainer = self.getTaskTemplateContainerByCategoryId( category_id )
        ttcontainer.modify( action, taskTemplate )

        if action == 'del_template':
            self.deleteTemplateIdFromRelatedEntity( taskTemplate.id, category_id )
            ret = ''
        else:
            ret = taskTemplate.id

        return ret

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskTemplatesAsArray' )
    def getTaskTemplatesAsArray( self, category_id, filter=None ):
        """
          Returns list of task templates as array

          Arguments:

            'category_id' -- id of category

        """
        ttcontainer = self.getTaskTemplateContainerByCategoryId( category_id )
        return ttcontainer.getTaskTemplatesAsArray( filter=filter )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskTemplateById' )
    def getTaskTemplateById( self, category_id, template_id ):
        """
          Returns task template by id (as array)

          Arguments:

            'category_id' -- id of category

            'template_id' -- id of template

          Result:

            Dictionary of task templates fields

        """
        ttcontainer = self.getTaskTemplateContainerByCategoryId( category_id )
        return ttcontainer.getTaskTemplate( template_id ).toArray()

    def getTaskTemplateFromRequest( self, request ):
        """
          Returns TaskTemplate from request

          Arguments:

            'request' -- REQUEST

          Result:

            Instance of 'TaskTemplate'
        """
        template_id = request['template_id']
        title = 'deprecated'  # we dont have this param when action='del_template'
        return TaskTemplate( template_id, title )

    def getTaskTemplateContainerByCategoryId( self, category_id ):
        """
          Returns TaskTemplateContainer by specified category id

          Arguments:

            'category_id' -- id of category

          Result:

            TaskTemplateContaner of specified category id

        """
        return self.getCategoryById( category_id ).taskTemplateContainer

    def deleteTemplateIdFromRelatedEntity( self, template_id, category_id ):
        """
          Delete 'template_id' from relative entity

          Arguments:

            'template_id' -- id of action template

        """
        category = self.getCategoryById( category_id )

        # delete from category.transition2TaskTemplate
        for transition_id, tt_list in category.transition2TaskTemplate.items():
            try:
                tt_list.remove(template_id)
                category._p_changed = 1
            except:
                pass

        # detele from category.state2TaskTemplateToDie
        for state_id, state_dict in category.state2TaskTemplateToDie.items():
            try:
                del state_dict[template_id]
                category._p_changed = 1
            except:
                pass

    #========================[ task definition work ]========================

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskDefinitionTreeItems' )
    def getTaskDefinitionTreeItems( self, category_id, template_id, parent_id = '0' ):
        """
          Returns tree of task definition

          Arguments:

            'category_id' -- id of category

            'template_id' -- id of action template

            'parent_id' -- id of parent relative of which tree are showed

          Result:

            Array of dictionaries with keys: 'level', 'id_task_definition', 'name', 'task_definition_type_title'
        """
        tree = []
        ttcontainter = self.getTaskTemplateContainerByCategoryId( category_id )
        taskDefinitionTree = ttcontainter.getTaskTemplate( template_id ).getTaskDefinitionTree( parent_id )
        for taskDefinitionTreeItem in taskDefinitionTree:
            treeItem = {}
            treeItem['level'] = taskDefinitionTreeItem['level']
            treeItem['id_task_definition'] = taskDefinitionTreeItem['id']
            treeItem['name'] = taskDefinitionTreeItem['name']
            treeItem['task_definition_type_title'] = self.taskDefinitionFactory.\
                getTaskDefinitionTypeTitle( taskDefinitionTreeItem['type'] )
            tree.append( treeItem )
        return tree

    security.declareProtected( CMFCorePermissions.ManagePortal, 'makeTaskDefinitionActionByRequest' )
    def makeTaskDefinitionActionByRequest( self, category_id, action, request ):
        """
          Performs action over task definition by request

          Arguments:

            'category_id' -- id of category

            'action' -- action to perform ('change_task_definition', 'change_task_definition_title',
                        'delete_task_definition', 'add_task_definition', 'add_root_task_definition')

            'request' -- REQUEST

        """
        ttcontainter = self.getTaskTemplateContainerByCategoryId( category_id )

        template_id = request['template_id']
        parent_id = request.get('parent_id')  # is set if add included action template

        if not parent_id and action in ('add_task_definition', 'add_root_task_definition') \
                         and template_id in ttcontainter.getTaskTemplateIds():
            raise DuplicateIdError,'This identifier is already in use.'

        redirect_to_list = 0

        # get task definition type
        if action=='change_task_definition' or action == 'change_task_definition_title' or action == 'delete_task_definition':
            task_definition_type = self.getTaskDefinitionTypeById( category_id, template_id, request['id_task_definition'] )
        elif action=='add_task_definition':
            task_definition_type = request['task_definition_type']
        elif action=='add_root_task_definition':
            self.makeActionByRequest( category_id, 'add_template', request )
            request['parent_id']='0'
            task_definition_type = request['task_definition_type']
            action='add_task_definition'
            redirect_to_list = 1

        template = ttcontainter.getTaskTemplate( template_id )
        factory = self.taskDefinitionFactory

        if action == 'add_task_definition':
            new_id = factory.createTaskDefinition( task_definition_type, template, request.get('parent_id') )
            action = 'change_task_definition'
            request['id_task_definition'] = new_id

        taskDefinition = factory.getTaskDefinitionByRequest( task_definition_type, request )
        ret = template.modify( action, taskDefinition )

        if action=='delete_task_definition' and request['id_task_definition']=='1':
            # main task definition, we have to delete taskTempalte also
            self.makeActionByRequest( category_id, 'del_template', request )

        if redirect_to_list:
            return ''
        return ret

    security.declarePublic( 'getTaskDefinitionById' )
    def getTaskDefinitionById( self, category_id, template_id, id_task_definition ):
        """
          Returns task definition by id

          Arguments:

            'category_id' -- id of category

            'template_id' -- id of action template

            'id_task_definition' -- id of task definition

          Result:

            TaskDefinition instance

        """
        ttcontainer = self.getTaskTemplateContainerByCategoryId( category_id )
        return ttcontainer.getTaskTemplate(template_id).getTaskDefinitionById( id_task_definition ).toArray()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskDefinitionTypeById' )
    def getTaskDefinitionTypeById( self, category_id, template_id, id_task_definition ):
        """
          Returns type of task definition by id

          Arguments:

            'category_id' -- id of category

            'template_id' -- id of action template

            'id_task_definition' -- id of task definition

          Result:

            type of task definition (string)

        """
        ttcontainer = self.getTaskTemplateContainerByCategoryId( category_id )
        return ttcontainer.getTaskTemplate( template_id ).getTaskDefinitionById( id_task_definition ).type

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTaskDefinitionParents' )
    def getTaskDefinitionParents( self, category_id, template_id, id_task_definition ):
        """
          Returns parents of task definition

          Arguments:

            'category_id' -- id of category

            'template_id' -- id of action template

            'id_task_definition' -- id of task definition

          Result:

            Array of task definition in dictionary format, see
            TaskTemplate.getTaskDefinitionParents method.

        """
        ttcontainer = self.getTaskTemplateContainerByCategoryId( category_id )
        return ttcontainer.getTaskTemplate( template_id ).getTaskDefinitionParents( id_task_definition )

    #--------------[ dtml ]-------------#
    security.declareProtected( CMFCorePermissions.ManagePortal, 'getTransition2TaskTemplateArray' )
    def getTransition2TaskTemplateArray( self, category_id, transition_id ):
        """
          Returns array of action templates associated with transition

          Arguments:

            'category_id' -- id of category

            'transition_id' -- id of transition

          Result:

            Array of action templates's id

        """
        return \
          self.getCategoryById(category_id).transition2TaskTemplate.has_key(transition_id) \
          and self.getCategoryById(category_id).transition2TaskTemplate[transition_id] \
          or []

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getState2TaskTemplateToDieArray' )
    def getState2TaskTemplateToDieArray( self, category_id, state_id ):
        """
          Returns array of action templates which are needed to finalize in specified state

          Arguments:

            'category_id' -- id of category

            'state_id' -- id of state

          Result:

            Array of id of action templates and result code.
            See MetadataTool.CategoryDefinition.state2TaskTemplateToDie attribute.

        """
        return \
          self.getCategoryById(category_id).state2TaskTemplateToDie.has_key(state_id) \
          and self.getCategoryById(category_id).state2TaskTemplateToDie[state_id] \
          or []

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getState2TaskTemplateToDieMapped' )
    def getState2TaskTemplateToDieMapped( self, category_id, state_id, filter=None ):
        """
          Get array state2task_template_to_die in specific format

          Arguments:

            'category_id' -- id of category

            'state_id' -- id of state

          Result:

            Array of dictionary, with keys:
            'template_id', 'title', 'result_codes', 'finalize', 'result_code'

          Return all task_templates, with list of result codes,
          and with selected (if is) result_code when finalized
          task based on task_template
        """
        arr = []
        ttcontainer = self.getTaskTemplateContainerByCategoryId( category_id )
        taskTemplateToDie = self.getCategoryById(category_id).state2TaskTemplateToDie.get(state_id, {})
        # taskTemplateToDie = { 'task_template_id1': 'result_code1' , ... }

        for taskTemplate in ttcontainer.getTaskTemplates( filter=filter ):
            item = {
              "template_id": taskTemplate.id,
              "title": taskTemplate.getTitleRootTaskDefinition(),
              "result_codes": taskTemplate.getResultCodes(),
              "finalize": 0,
              "result_code": None,
            }
            if taskTemplate.id in taskTemplateToDie.keys():
                item['finalize'] = 1
                item['result_code'] = taskTemplateToDie[taskTemplate.id]
            arr.append(item)

        return arr

    security.declarePublic( 'getTaskTemplates' )
    def getTaskTemplates( self, category_id, transition_id ):
        """
          Returns array of task templates associated with transition

          Arguments:

            'category_id' -- id of category

            'transition_id' -- id of transition

          Result:

            Array of dictionaries, with keys: 'template_title', 'template_id'

        """
        category = self.getCategoryById( category_id )
        ttcontainer = category.taskTemplateContainer

        arr = []
        for task_template_id in category.transition2TaskTemplate.get(transition_id, []):
            item = ttcontainer.getTaskTemplate( task_template_id ).toArray()
            arr.append( item )

        return arr

    #--------------[ result code -> transition table ]-------------#
    security.declareProtected( CMFCorePermissions.ManagePortal, 'callModel' )
    def callModel( self, category_id, function_name, *params ):
        """
          Method to work with 'Resultcodes2TransitionModel' instance methods from dtml

          Arguments:

            'category_id' -- id of category

            'function_name' -- function name to call

            '*params' -- params to function

          Function-adapter for Resultcodes2TransitionModel
            called from dtml for access to specific model
        """
        function_impl = getattr( self.getCategoryById(category_id).resultcodes2TransitionModel, function_name )
        return function_impl( *params )

InitializeClass( TaskTemplateContainerAdapter )
