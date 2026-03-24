"""
Action template for creating document.

$Editor: inemihin $
$Id: TaskDefinitionCreateDocument.py,v 1.14 2006/02/06 08:57:20 vsafronovich Exp $
"""

__version__ = '$Revision: 1.14 $'[11:-2]

from Globals import package_home
from Products.CMFCore.FSPythonScript import FSPythonScript

import Exceptions
from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import cookId, InitializeClass, getObjectByUid, getToolByName, parseDate


class TaskDefinitionCreateDocument(TaskDefinition):
    """
        Creating document of specified category.
    """

    _class_version = 1.00

    process_attributes = FSPythonScript('process_attributes', '%s/skins/common/process_attributes.py' % package_home(globals()))

    def __init__(self):
        """
            Creates new instance.
        """
        TaskDefinition.__init__( self )
        self.type = 'create_document'
        self.dest_category = None

    def changeTo( self, taskDefinition ):
        """
            Changes self data.

            Arguments:
                'taskDefinition' -- instance of TaskDefinition
        """
        TaskDefinition.changeTo( self, taskDefinition )

        # specific fields
        self.dest_category = taskDefinition.dest_category

    def toArray( self ):
        """
            Converts object's fields to dictionary

            Result:
                Dictionary as { 'field_name': 'field_value', ... }
        """
        arr = TaskDefinition.toArray( self )
        arr["dest_category"] = self.dest_category
        return arr

    def activate( self, object, context, transition ):
        """
            Activate taskDefinition (action template)

            Arguments:

                'object' -- object in context of which happened activation
                'context' -- common actions context

            Result:
                Also returns dictionary, which is passed to next (inner) taskDefinition's activate (if presented)
        """

        catalog = getToolByName(self, 'portal_catalog')
        mdtool = getToolByName(self, 'portal_metadata')
        REQUEST = self.REQUEST
        r = REQUEST.get

        # folder where document will be placed
        folder = object.parent()

        # information for creating document
        doc_title = r('title')
        if not doc_title:
            raise Exceptions.SimpleError, 'Title of document is not specified'

        doc_id = r('id') or cookId( folder, title=doc_title )

        category = mdtool.getCategoryById( self.dest_category )
        attrs = self.process_attributes( REQUEST, category=category, pattern='%s' )

        folder.manage_addProduct['CMFNauTools'].addHTMLDocument( id=doc_id
                                                               , title=doc_title
                                                               , description=r('description')
                                                               , category=self.dest_category
                                                               , category_attributes=attrs
                                                               )

        doc = folder._getOb(doc_id)
        if not doc:
            raise Exceptions.SimpleError, 'Failed to create document'

        context['new_doc_uid'] = doc.getUid()

InitializeClass(TaskDefinitionCreateDocument)

class TaskDefinitionFormCreateDocument(TaskDefinitionForm):
    """
      Class view (form)
    """
 
    _template = 'task_definition_create_document'

class TaskDefinitionControllerCreateDocument(TaskDefinitionController):
    """
      Class controller
    """
    def getEmptyArray(self):
        """
            Returns dictionary with empty values.
        """
        array = TaskDefinitionController.getEmptyArray( self )
        array['dest_category'] = None
        return array

    def getTaskDefinitionByRequest( self, request ):
        """
            Gets destination folder uid from request and stores it in
            TaskDefinitionCreateDocument() instance.
        """
        taskDefinition = TaskDefinitionCreateDocument()
        TaskDefinitionController.getTaskDefinitionByRequest(self, request, taskDefinition)

        if request.has_key('dest_category'):
            taskDefinition.dest_category = request['dest_category']

        return taskDefinition


class TaskDefinitionRegistryCreateDocument(TaskDefinitionRegistry):
    """
        Class that provides information for factory about class
    """
 
    type_list = ( { "id": "create_document"
                  , "title": "Creating document" 
                  }, 
                )

    Controller = TaskDefinitionControllerCreateDocument()
    Form = TaskDefinitionFormCreateDocument()

    dtml_token = 'create_document'


def initialize( context ):
    # module initialization callback
    context.registerAction( TaskDefinitionRegistryCreateDocument() )
