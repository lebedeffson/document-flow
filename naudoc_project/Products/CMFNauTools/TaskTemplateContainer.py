"""

  TaskTemplateContainer and TaskTemplate classes

  TaskTemplate -- is container for TaskDefinition instances,
  there is only one TaskDefinition on top, other if is, are included
  it top (root) TaskDefintion.

  And possible to say that TaskTemplate are same that root TaskDefinition, and
  when takes title of TaskTemplate, it will be title of root TaskDefinition

  When creating first TaskDefinition, creates TaskTemplate.
  When delete root TaskDefinition, will be deleted TaskTemplate



$Editor: inemihin $
$Id: TaskTemplateContainer.py,v 1.27 2006/03/30 12:06:41 ikuleshov Exp $
"""
__version__ = '$Revision: 1.27 $'[11:-2]

from types import StringType

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.WorkflowCore import ObjectMoved, ObjectDeleted

from SimpleObjects import InstanceBase, ItemBase
from Utils import InitializeClass, applyRecursive


#-----------------------[ TaskTemplateContainer ]------------------------
class TaskTemplateContainer( InstanceBase ):
    """
      Class container for TaskTemplate

      Provide interface for modify contained TaskTemplates
      (add, change, remove)
    """
    _class_version = 1.2

    def _initstate( self, mode ):
        if not InstanceBase._initstate( self, mode ):
            return 0

        if not hasattr( self, 'taskTemplates' ):
            self.taskTemplates = {}

        if not getattr( self, 'id', None ): # < 1.2
            self.id = 'taskTemplateContainer'

        return 1

    def _containment_onDelete( self, item, container ):
        for ttem in self.getTaskTemplates():
            ttem.manage_beforeDelete( item, container )

    def _instance_onDestroy( self ):
        # XXX must inherit ContainerBase
        for ttem in self.getTaskTemplates():
            applyRecursive( ItemBase._instance_onDestroy, 1, ttem )

    #----[ modify ]----
    def modify( self, action, taskTemplate ):
        """
          Interface for modifying content

          Arguments:

            'action' -- action to perform ('add_template' | 'change_template' | 'del_template')

            'taskTemplate' -- instance which takes part of action

        """
        if action == 'add_template':
            self.taskTemplates[ taskTemplate.id ] = taskTemplate
            self._p_changed = 1

        elif action == 'del_template':
            applyRecursive( ItemBase._instance_onDestroy, 1, self.getTaskTemplate( taskTemplate.id ) )
            del self.taskTemplates[ taskTemplate.id ]
            self._p_changed = 1

        elif action == 'change_template':
            self.getTaskTemplate( taskTemplate.id ).changeTo( taskTemplate )

    #----[ activate ]----
    def activateTaskTemplate( self, template_id, object, transition, context ):
        """
          Are main function for activating specific action template (TaskTemplate)

          Arguments:

            'template_id' -- template id to activate

            'object' -- object for which will be maden action

        """
        self.getTaskTemplate( template_id ).activate( object, transition, context )

    __ac_permissions__=(
        ('View', ('getTaskTemplate',),),
        )
    def getTaskTemplate( self, template_id ):
        """
          Returns task template by id

          Arguments:

            'template_id' -- template id to take

          Result:

            Returns TaskTemplate instance

        """
        return self.taskTemplates[ template_id ].__of__(self)

    def getTaskTemplates( self, filter=None ):
        """
          Returns all task templates
        """
        templates = []
        if type( filter ) is StringType:
            filter = [ filter ]
        elif not filter:
            filter = []
        for template_id in self.taskTemplates.keys():
            template = self.getTaskTemplate(template_id)
            definition = template.getTaskDefinitionOnTop()
            if 'have_result_codes' in filter and not template.getResultCodes():
                continue
            if 'followup_only' in filter and not hasattr( definition, 'task_brains' ):
                continue
            templates.append( template )
        return templates

    def getTaskTemplateIds( self, filter=None ):
        """
          Returns ids of task templates

          Arguments:

            'filter' -- filtering for task templates, now supported only
                        'have_result_codes', this mean task templates which
                        have result codes

          Result:

            List of ids of action templates.

        """
        return [ x.id for x in self.getTaskTemplates( filter=filter ) ]

    def getTaskTemplatesAsArray( self, filter=None ):
        """
          Returns task templates as array

          Arguments:

            'filter' -- filter for action templates, now supported 'have_result_codes'
                        this mean task templates which have result codes.

          Result:

            Returns array:
            >>> return = [
            >>>   { "template_id": 'template_id1',
            >>>     "template_title": 'template_title1' },
            >>>    ...
            >>> ]
        """
        array = []
        for template in self.getTaskTemplates( filter=filter ):
            array.append( { "template_id": template.id, "template_title": template.getTitleRootTaskDefinition() } )
        return array

InitializeClass( TaskTemplateContainer )

#-----------------------[ TaskTemplate ]------------------------
class TaskTemplate( InstanceBase ):
    """
      Class containing TaskDefinitions (i.e. container)

      Provide interface for modify and activate them
    """
    _class_version = 1.1

    security = ClassSecurityInfo()

    def _initstate( self, mode ):
        if not InstanceBase._initstate( self, mode ):
            return 0

        if getattr( self, 'taskDefinitions', None ) is None:
            self.taskDefinitions = []
        return 1

    def _containment_onDelete( self, item, container ):
        for tdef in self.taskDefinitions:
            tdef.__of__(self).manage_beforeDelete( item, container )

    def _instance_onDestroy( self ):
        # XXX must inherit ContainerBase
        for tdef in self.taskDefinitions:
            applyRecursive( ItemBase._instance_onDestroy, 1, tdef.__of__( self ) )

    def changeTo( self, taskTemplate ):
        self.title = taskTemplate.title

    def toArray( self ):
        """
          Return self values (title, id) as array

          Result:

            Dictionary:
            >>> return = { "template_title": "template_title1", "template_id": "template_id1" }
            >>>

        """
        array = {}
        array["template_title"] = self.getTitleRootTaskDefinition()
        array["template_id"] = self.id
        return array


    #----[ modify TaskDefinition ]----
    def modify( self, action, taskDefinition ):
        """
          Interface for modifying taskDefintions

          Arguments:

            'action' -- action to perform ('add_task_definition' | 'change_task_definition' |
                        'delete_task_definition' | 'change_task_definition_title')

            'taskDefinition' -- TaskDefinition instance take part in action

        """
        if action == 'add_task_definition':
            return self.addTaskDefinition( taskDefinition )
        elif action == 'change_task_definition':
            return self.changeTaskDefinition( taskDefinition )
        elif action == 'delete_task_definition':
            return self.deleteTaskDefinition( taskDefinition.id )
        elif action == 'change_task_definition_title':
            return self.changeTaskDefinitionTitle( taskDefinition )
        else:
            print 'unknown action for TaskDefinition modify'
            return ''


    #----[ add TaskDefinition ]----
    def addTaskDefinition( self, taskDefinition ):
        """
          Adds task definition

          Arguments:

            'taskDefinition' -- TaskDefinition to add

        """
        taskDefinition.id = self.getUniqueTaskDefinitionId()
        self.taskDefinitions.append(taskDefinition)
        self._p_changed = 1
        self.changeTaskDefinition( taskDefinition )
        return taskDefinition.id

    #----[ change TaskDefinition ]----
    def changeTaskDefinition( self, taskDefinitionNew ):
        """
          Changes task definition

          Arguments:

            'taskDefinitionNew' -- new TaskDefinition, have id of existing taskDefinition

        """

        taskDefinitionOld = self.getTaskDefinitionById( taskDefinitionNew.id )
        taskDefinitionOld.changeTo( taskDefinitionNew )
        return taskDefinitionNew.id

    #----[ change TaskDefinition title ]----
    def changeTaskDefinitionTitle( self, taskDefinitionNew ):
        """
          Changes task definition's title

          Arguments:

            'taskDefinitionNew' -- contain new title

        """
        taskDefinitionOld = self.getTaskDefinitionById( taskDefinitionNew.id )
        taskDefinitionOld.name = taskDefinitionNew.name
        return taskDefinitionNew.id

    #----[ delete TaskDefinition ]----
    def deleteTaskDefinition( self, id_task_definition ):
        """
          Deletes task definition

          Arguments:

            'id_task_definition' -- id task defintion to delete

          Note:

            Also will be deleted all childs (included) task definitions

        """
        # we have to delete all childs also
        taskDefinitionsIdToDel = [ id_task_definition ]
        childs = self.getTaskDefinitionTree( id_task_definition )
        for item in childs:
            taskDefinitionsIdToDel.append( item['id'] )
        taskDefinitionsIdToDel.reverse() # we will be delete from end

        for itemIdToDel in taskDefinitionsIdToDel:
            self.deleteTaskDefinitionItem( itemIdToDel )

        return ''

    def getResultCodes( self ):
        """
          Return result codes of task template

          Result:

            Returns array of result codes, which asking from top TaskDefinition.

            >>> result_codes = (
            >>>    { 'id': 'result_code1', 'title': 'title_result_code1' },
            >>>     ...
            >>> )
        """
        # 1. take top task definition
        taskDefinitionOnTop = self.getTaskDefinitionOnTop()
        if taskDefinitionOnTop is None:
            return None
        # 2. ask task definition for its result codes
        return taskDefinitionOnTop.__of__(self).getResultCodes()

    def deleteTaskDefinitionItem( self, id_task_definition ):
        """
          Delete task definition

          Arguments:

            'id_task_definition' -- id task definition to delete

        """
        applyRecursive( ItemBase._instance_onDestroy, 1, self.getTaskDefinitionById( id_task_definition ) )
        del self.taskDefinitions[ self.getTaskDefinitionPositionById( id_task_definition ) ]
        self._p_changed = 1

    def getUniqueTaskDefinitionId( self ):
        """
          Gets unique id for task definition

          Result:

            Returns unique id for task definition

        """
        ids = []
        for taskDefinition in self.taskDefinitions:
            ids.append( int( taskDefinition.id ) )
        try:
            max_id = max(ids)
        except:
            max_id = 0
        return str( max_id+1 ) # use string as taskDefinition id

    def getTaskDefinitionsOfParent( self, parent_id ):
        """
          Gets included task definition to parent task defintion

          Arguments:

            'parent_id' -- id of parent's task definition

          Result:

            Array of task definitin which are included to parent's task definition

        """
        tasks = []
        for taskDefinition in self.taskDefinitions:
            if taskDefinition.parent_id == parent_id:
                tasks.append( taskDefinition.__of__( self ) )
        return tasks


    security.declareProtected( CMFCorePermissions.View, 'getTaskDefinitionArrayById' )
    def getTaskDefinitionArrayById( self, id_task_definition ):
        if self.getTaskDefinitionById(id_task_definition):
            return self.getTaskDefinitionById(id_task_definition).toArray()
        return None

    def getTaskDefinitionById( self, id_task_definition ):
        """
          Gets task definition by id

          Arguments:

            'id_task_definition' -- id task definition to take

          Result:

            Returns TaskDefinition

        """
        for taskDefinition in self.taskDefinitions:
            if taskDefinition.id == id_task_definition:
                return taskDefinition.__of__( self )
        return None

    def getTaskDefinitionPositionById( self, id_task_definition ):
        """
          Gets position of TaskDefinition in array

          Arguments:

            'id_task_definition' -- id task definition

        """
        pos = 0
        for taskDefinition in self.taskDefinitions:
            if taskDefinition.id == id_task_definition:
                return pos
            pos=pos+1
        return None


    def getTaskDefinitionOnTop( self ):
        """
          Gets task definition on top
        """
        taskDefinitions = self.getTaskDefinitionsOfParent( '0' )
        if len( taskDefinitions ) > 1:
            print 'something wrong'
            return None
        elif len( taskDefinitions ) == 1:
            return taskDefinitions[0]
        return None

    # getTaskDefinitionParents
    # returns: parents as array { "id":, "name": }
    def getTaskDefinitionParents( self, id_task_definition ):
        """
          Returns all parents of specified task definition

          Arguments:

            'id_task_definition' -- id of task definition

          Result:

            Array of task definition which are parents of specified task definition
            >>> return = [
            >>>   { "id": "id1", "name": "name1" },
            >>>   ...
            >>> ]
        """
        parents = []
        parent_id = id_task_definition
        while parent_id != '0':
            if parent_id != id_task_definition:
                taskDefinition = self.getTaskDefinitionById( parent_id ).toArray()
                parent = {}
                parent["id"] = taskDefinition["id"]
                parent["name"] = taskDefinition["name"]
                parents.append( parent )
            # get parent of current taskDefinition
            parent_id = self.getTaskDefinitionById( parent_id ).parent_id
        parents.reverse()
        return parents

    #----[ activate ]----
    #----[ activate ]----
    def activate( self, object, transition, context ):
        """
          Activate task template

          Arguments:

            'object' -- object for which action will be maden

          Activation mean making action, i.e. TaskTemplate may contains
          more that one TaskDefinition - each task definition will be
          activated
        """
        # needed for top-task-definition for 'task_definition_id' attribute
        context['task_template_id'] = self.id
        try:
            taskDefinitionOnTop = self.getTaskDefinitionOnTop()
            if taskDefinitionOnTop is None:
                del context['task_template_id']
            self.activateTaskDefinition( taskDefinitionOnTop, object, transition, context )
        finally:
            del context['task_template_id']
            if context.has_key( 'task_id' ):
                del context['task_id']

    # recursive function
    def activateTaskDefinition( self, taskDefinition, object, transition, context ):
        """
          Activating task definition

          Arguments:

            'taskDefinition' -- TaskDefinition for activate

            'object' -- object for which action will be performed

            'context' -- common context for actions on transition

          Note:

            recurse function

          TaskDefinition may have included TaskDefinition - we have to
          activate them aslo.

        """
        moved = False
        try:
            taskDefinition.__of__(self).activate( object, context, transition )
        except ObjectMoved, err:
            object = err.getNewObject()
            moved = True
        except ObjectDeleted:
            return

        # may by add handler here? f.e.
        # if ret['message_to_task_template'] == 'exit':
        #   return
        # i.e. TaskDefinition's "activate" method can pass 'events' to self container - TaskTemplate,
        # by 'ret' array
        # f.e. dinamically creation task definition...
        # or making actions on TaskTemplate level, and pass result to 'ret' array, and
        #    handle them in child's TaskDefinition (where needed)
        # or making logical condition - pass to self.activateTaskDefinition only [0] or [1] child
        # accordingly condition
        #

        for childTaskDefinition in self.getTaskDefinitionsOfParent( taskDefinition.id ):
            try:
                self.activateTaskDefinition( childTaskDefinition, object, transition, context )
            except ObjectMoved, err:
                object = err.getNewObject()
                moved = True
            except ObjectDeleted:
                break

        if moved:
             # re-raise
             raise ObjectMoved( object )

    def getTaskDefinitionTree( self, parent_id = '0' ):
        """
          Returns all TaskDefinition as tree

          Arguments:

            'parent_id' -- parents for tree (default '0')

          Result:

            >>> return = [
            >>>  { 'id': 'task_definition_id1', 'level': 'level', 'name': 'name1', 'type': 'type1' }
            >>>  ...
            >>> ]
        """
        taskDefinitionTree = []
        level = 0
        for taskDefinition in self.getTaskDefinitionsOfParent( parent_id ):
            self.getTreeBranch( taskDefinitionTree, level, taskDefinition.id )
        return taskDefinitionTree

    # recursive function
    def getTreeBranch( self, tree, level, parent_id ):
        """
          Return tree branch, for specific parent

          Arguments:

            'tree' -- tree array which are filled

            'level' -- current level

            'parent_id' -- parent from which needed to take leaves

          Note:

            recursion function

        """
        taskDefinition = self.getTaskDefinitionById( parent_id )
        treeItem = {}
        treeItem["id"] = taskDefinition.id
        treeItem["level"] = level
        treeItem["name"] = taskDefinition.name
        treeItem["type"] = taskDefinition.type
        tree.append( treeItem )
        for taskDefinition in self.getTaskDefinitionsOfParent( parent_id ):
            self.getTreeBranch( tree, level+1, taskDefinition.id )

    security.declareProtected( CMFCorePermissions.View, 'getTitleRootTaskDefinition' )
    def getTitleRootTaskDefinition( self ):
        """
          Returns title of root task definitin
        """
        if len( self.getTaskDefinitionsOfParent('0') ) == 1:
            return self.getTaskDefinitionsOfParent('0')[0].name
        return 'n/a'


InitializeClass( TaskTemplate )
