"""
$Id: TaskDefinitionCreateSubordinate.py,v 1.31 2006/08/15 13:14:34 oevsegneev Exp $

Action template for creating subordinate document.
"""

__version__ = '$Revision: 1.31 $'[11:-2]

from Globals import package_home
from Acquisition import aq_parent, aq_inner

from Products.CMFCore.FSPythonScript import FSPythonScript

import Exceptions
from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import cookId, InitializeClass, getObjectByUid, getToolByName, parseDate, getFolderAnyway
from PatternProcessor import PatternProcessor

class TaskDefinitionCreateSubordinate(TaskDefinition):
    """
        Creating subordinate document due to specified category and target folder.
    """

    _class_version = 1.00

    process_attributes = FSPythonScript('process_attributes', '%s/skins/common/process_attributes.py' % package_home(globals()))

    type = 'create_subordinate'

    dest_category = None
    dest_folder_uid = None
    dest_folder_title = ''
    dest_folder_template = '/'
    dest_folder_type = 'path'
    object_title_template = ''

    def changeTo( self, taskDefinition ):
        """
            Changes self data.

            Arguments:
                'taskDefinition' -- instance of TaskDefinition
        """
        TaskDefinition.changeTo( self, taskDefinition )

        # specific fields
        self.dest_category = taskDefinition.dest_category
        self.dest_folder_uid = taskDefinition.dest_folder_uid
        self.dest_folder_title = taskDefinition.dest_folder_title
        self.dest_folder_template = taskDefinition.dest_folder_template
        self.dest_folder_type = taskDefinition.dest_folder_type
        self.object_title_template = taskDefinition.object_title_template

    def toArray( self):
        """
            Converts object's fields to dictionary

            Result:
                Dictionary as { 'field_name': 'field_value', ... }
        """
        arr = TaskDefinition.toArray( self )
        arr["uid"] = self.parent().id + self.id
        arr["dest_category"] = self.dest_category
        arr["dest_folder_uid"] = self.dest_folder_uid
        arr["dest_folder_title"] = self.dest_folder_title
        arr["dest_folder_template"] = self.dest_folder_template
        arr["dest_folder_type"] = self.dest_folder_type
        arr["object_title_template"] = self.object_title_template
        return arr

    def activate(self, object, context, transition):
        """
            Activate taskDefinition (action template)

            Arguments:
                'object' -- object in context of which happened activation
                'context' -- common actions context

            Result:
                None
        """
        catalog = getToolByName(self, 'portal_catalog')

        if not ((self.dest_folder_type == 'path' and self.dest_folder_uid) or
                (self.dest_folder_type == 'template' and self.dest_folder_template)):
            raise Exceptions.SimpleError( "Task template '%(task)s' is not configured properly.", task=self )

        # locating destination folder

        if self.dest_folder_type == 'template':
            path = PatternProcessor.processString( self.dest_folder_template, fmt='folder_routing', doc=object )
            folder = getFolderAnyway( object, path=path )
        else:
            folder = getObjectByUid( self, self.dest_folder_uid )

        if folder is None:
            raise Exceptions.SimpleError( 'Folder not found' )

        # getting document metadata from REQUEST
        REQUEST = self.REQUEST
        uid = '_%s%s' % ( self.parent().id, self.id )
        doc_id = REQUEST.get('id%s' % uid, None)
        doc_title = REQUEST.get('title%s' % uid, None)

        if not doc_id:
            if not doc_title and self.object_title_template:
                doc_title = PatternProcessor.processString( self.object_title_template, fmt='title', doc=object )
            doc_id = cookId(folder, title=doc_title)

        # testing for not empty mandatory fields in primary document
        for attr, attr_value in object.listCategoryAttributes():
            if attr.isMandatory() and attr.isEmpty(attr_value):
                raise Exceptions.SimpleError( 'Mandatory attribute missing in primary document' )


        mdtool = getToolByName(self, 'portal_metadata')
        category = mdtool.getCategoryById( self.dest_category )
        attrs = self.process_attributes( REQUEST, category=category, pattern='%%s%s'%uid )

        # create document
        folder.invokeFactory( 'HTMLDocument'
                            , doc_id
                            , title=doc_title
                            , description=REQUEST.get('description%s' % uid, None)
                            , category=category.getId()
                            , category_primary=(object.getUid(), Trust)
                            , category_attributes=attrs
                            )

        doc = folder._getOb(doc_id)
        if not doc:
            raise Exceptions.SimpleError( 'Failed to create document' )

        if self.amIonTop():
            setattr( doc, 'task_template_id', context['task_template_id'] )

    def getResultCodes( self ):
        """
            Return result codes.
            The result codes for this task definition are available states of subordinate document.

            Result:
                Return array of result codes
        """

        if not self.dest_category:
            return {}

        mdtool = getToolByName (self, 'portal_metadata')
        wftool = getToolByName (self, 'portal_workflow')

        category = mdtool.getCategoryById( self.dest_category )
        if not category:
            return {}

        wf = category.getWorkflow()

        result = []

        for state in wf.states.objectIds():
            code = {}
            code ['id'] = state
            code ['title'] = wftool.getStateTitle (wf.getId(), state)
            result.append (code)

        return result

InitializeClass (TaskDefinitionCreateSubordinate)

class TaskDefinitionFormCreateSubordinate(TaskDefinitionForm):
    """
      Class view (form)
    """
    _template = 'task_definition_create_subordinate'

class TaskDefinitionControllerCreateSubordinate(TaskDefinitionController):
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
        array['dest_category'] = None
        array['dest_folder_title'] = ''
        array['dest_folder_template'] = '/'
        array['dest_folder_type'] = 'path'
        array['dest_folder_uid'] = None
        array['object_title_template'] = ''
        return array

    def getTaskDefinitionByRequest( self, request ):
        """
            Gets destination folder uid from request and stores it in
            TaskDefinitionCreateSubordinate () instance.
        """
        taskDefinition = TaskDefinitionCreateSubordinate ()
        TaskDefinitionController.getTaskDefinitionByRequest (self, request, taskDefinition)

        taskDefinition.dest_category = request.get('dest_category', taskDefinition.dest_category)
        taskDefinition.object_title_template = request.get('object_title_template', '')
        taskDefinition.dest_folder_uid = request.get('dest_folder_uid', None)
        taskDefinition.dest_folder_title = request.get('dest_folder_title', '')
        taskDefinition.dest_folder_template = request.get('dest_folder_template', None)
        taskDefinition.dest_folder_type = request.get('dest_folder_type', 'path')

        return taskDefinition


class TaskDefinitionRegistryCreateSubordinate(TaskDefinitionRegistry):
    """
        Class that provides information for factory about class
    """
    type_list = ( { "id": "create_subordinate"
                  , "title": "Create subordinate document" 
                  },
                )

    Controller = TaskDefinitionControllerCreateSubordinate()
    Form = TaskDefinitionFormCreateSubordinate()

    dtml_token = 'create_subordinate'

def initialize( context ):
    context.registerAction( TaskDefinitionRegistryCreateSubordinate() )
