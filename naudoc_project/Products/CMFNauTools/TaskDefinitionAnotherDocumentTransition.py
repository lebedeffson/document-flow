"""
Action template for :
    DocFlow action to make transition in documents linked with current document.

$Editor: kfirsov $
$Id: TaskDefinitionAnotherDocumentTransition.py,v 1.13 2005/08/23 11:36:21 vsafronovich Exp $
"""

__version__ = '$Revision: 1.13 $'[11:-2]

from AccessControl.SecurityManagement import getSecurityManager, \
       newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser
from Acquisition import aq_inner, aq_parent

from Config import ManagedRoles
from DocumentLinkTool import Link
from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import InitializeClass, getToolByName


#--------------------------------------------------------------
class TDAnotherDocumentTransition( TaskDefinition ):
    """
        DocFlow action to perform transition in objects linked with current one.
    """

    _class_version = 1.00


    _properties=({'id' : 'link_type', 'type': 'string', 'mode': ''},
                  {'id' : 'document_category', 'type': 'string', 'mode': 'w'},
                  {'id' : 'use_inheritance', 'type': 'string', 'mode': ''},
                  {'id' : 'state_id', 'type': 'string', 'mode': ''},
                  {'id' : 'transition_id', 'type': 'string', 'mode': ''},
                  {'id' : 'comment', 'type': 'text', 'mode': ''},
                 )


    def __init__( self ):
        """
            Creates new instance.
        """
        TaskDefinition.__init__( self )

        for prop in self._properties:
            setattr( self, prop['id'], '')
        self.type='another_document_transition'

    def changeTo( self, taskDefinition ):
        """
            Copies data from taskDefinition to self.

            Updates properties from taskDefinition.

            Arguments:

                'task_definition' -- instance of TaskDefinition
        """
        TaskDefinition.changeTo( self, taskDefinition )

        # specific fields
        for prop_id in self.propertyIds():
            self._updateProperty( prop_id, taskDefinition.getProperty( prop_id ) )

    def toArray( self ):
        """
          Converts object's fields to dictionary.

          Result:

            Dictionary as { 'field_name': 'field_value', ... }

        """
        arr = TaskDefinition.toArray( self )
        for prop_id in self.propertyIds():
            arr[ prop_id ] = self.getProperty( prop_id )
        return arr

    def listFilteredLinksFor(self, object):
        """
            Filters links created in object according to task settings

            Arguments:

                'object' -- object with links

            Result:

                List of Link instances.
        """
        brains = getToolByName(self, 'portal_links')\
                 .searchLinks( source=object
                             , source_internal=True
                             , relation=self.getProperty('link_type')
                             )
        return [x.getObject() for x in brains]

    def listPermittedCategories(self):
        """
            Lists permitted categories.

            If specified in task properties, also includes their descendants.

            Result:

                List of CategoryDefinition instances.
        """
        md_tool = getToolByName(self, 'portal_metadata')
        categories = [ md_tool.getCategoryById( self.getProperty('document_category')) ]

        if self.getProperty('use_inheritance'):
            heirs = {}
            for category in categories:
                heirs[ category.getId() ] = category
                heirs_categories = category.listDependentCategories()
                for heir_category in heirs_categories:
                    heirs[ heir_category.getId() ] = heir_category

            categories = [x for x in heirs.values()]
        return categories

    def filterDocuments(self, candidates, categories):
        """
            Filters objects according their categoty and state.

            Arguments:

                'candidates' -- list of objects-candidates

                'categories' -- permitted categories

            Result:

                List of filtered objects.
        """
        wf_tool = getToolByName(self, 'portal_workflow')

        documents = []
        for candidate in candidates:
            workflow_state = wf_tool.getStateFor(candidate) or candidate.state() # getStatus?

            if candidate.getCategory() in categories and \
               workflow_state == self.getProperty('state_id'):
                documents.append( candidate )
        return documents

    def listMatchedObjects(self, object):
        """
            Creates list of objects that matches task settings for given object.

            Arguments:

                'object' -- Object which has links pointed to another objects.

            Result:

                List of objects.
        """
        links = self.listFilteredLinksFor( object )
        candidates = map(Link.getTargetObject, links)
        categories = self.listPermittedCategories()
        return self.filterDocuments(candidates, categories)

    def activate( self, object, context, transition ):
        """
            Activate taskDefinition (action template)

            First filters links in object. Then filters objects to which
            point filtered links according their category and state.
            Then for residuary objects performs desired transition.

            Arguments:

                'object' -- object in context of which happened activation

                'context' -- common actions context

            Result:

                Also returns dictionary, which is passed to next (inner)
                taskDefinition's activate (if presented)

        """
        #TODO:
        # check heir categories..... passed
        # dtml document .... passed
        # Ckeck links to versions of documents ... passed
        # check transitions for several documents ... passed
        # check permissions (when it is not permitted to view document or make desired transition) ... passed

        # check transitions which need some extra data to enter ... TODO
        # check several documents and fail one of actions ... TODO
        # check one action causes another action that also calls different transitions in linked documents ... TODO

        documents = self.listMatchedObjects( object )
        wf_tool = getToolByName(self, 'portal_workflow')

        oldsm = getSecurityManager()
        system=UnrestrictedUser('System Processes', '', ManagedRoles, [])
        newSecurityManager(None, system)
        try:
            for document in documents:
                version = None
                if document.implements('isVersion'):
                    version = document
                    document = version.getVersionable()
                    version_id_to_return = version.makeCurrent()

                wf_tool.doActionFor( document, self.getProperty('transition_id'), comment=self.getProperty('comment') )

                if version is not None:
                    document.getVersion(version_id_to_return).makeCurrent()
        finally:
            setSecurityManager(oldsm)

InitializeClass( TDAnotherDocumentTransition )

#----------------------------------------------------------------
class TDAnotherDocumentTransitionForm( TaskDefinitionForm ):
    """
      Class view (form)

    """
    _template = 'task_definition_another_doc_transition'

#----------------------------------------------------------------
class TDControllerAnotherDocumentTransition( TaskDefinitionController ):
    """
      Class controller

    """
    def getEmptyArray( self ):
        """
          Returns dictionary with empty values.

          Arguments:

            'emptyArray' -- dictionary to fill

        """
        emptyArray = TaskDefinitionController.getEmptyArray( self )
        td = TDAnotherDocumentTransition()
        for prop_id in td.propertyIds():
            emptyArray[ prop_id ] = ''
        return emptyArray

    def getTaskDefinitionByRequest( self, request ):
        """
            Gets destination folder uid from request and srotes it in
            TaskDefinitionRouting() instance.

        """
        taskDefinition = TDAnotherDocumentTransition()

        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )

        for prop_id in taskDefinition.propertyIds():
            if request.has_key( prop_id ):
                taskDefinition._updateProperty( prop_id, request.get(prop_id) )

        return taskDefinition

#----------------------------------------------------------------
class TDRegistryAnotherDocumentTransition( TaskDefinitionRegistry ):
    """
        Class that provides information for factory about class
    """
    type_list = ( { "id": "another_document_transition"
                  , "title": "DocFlow action on another documents"
                  },
                )
   
    Controller = TDControllerAnotherDocumentTransition()
    Form = TDAnotherDocumentTransitionForm()

    dtml_token = 'another_doc_transition'

def initialize( context ):
    context.registerAction( TDRegistryAnotherDocumentTransition() )
