"""
Portal metadata tool -- contains category definitions.

$Editor: vpastukhov $
$Id: MetadataTool.py,v 1.162 2006/04/10 10:07:33 oevsegneev Exp $
"""
__version__ = '$Revision: 1.162 $'[11:-2]

from types import StringType, ListType

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.MetadataTool import DEFAULT_ELEMENT_SPECS, \
                                      MetadataTool as _MetadataTool

import Config, Features
from ActionInformation import ActionInformation as AI
from CategoryDefinition import CategoryDefinition
from DocflowLogic import DocflowLogic
from DefaultWorkflows import setupWorkflowVars
from ResourceUid import ResourceUid
from Resultcodes2Transition import Resultcodes2Transition
from TaskDefinitionFactory import TaskDefinitionFactory
from TaskDefinitionNotification import TaskDefinitionNotification
from TaskTemplateContainerAdapter import TaskTemplateContainerAdapter
from SimpleObjects import ToolBase, ContainerBase
from Utils import InitializeClass
from ValueTypes import getValueHandler, listValueHandlers
from VersionWorkflow import VersionWorkflowLogic


class MetadataTool( ToolBase, ContainerBase, _MetadataTool ):
    """
        Portal metadata tool.
    """
    _class_version = 1.44

    meta_type = 'NauSite Metadata Tool'
    id        = 'portal_metadata'
    title     = 'Document categories management'
    isPrincipiaFolderish = True

    __implements__ = Features.isAttributesProvider, \
                     Features.isNavigable, \
                     ToolBase.__implements__, \
                     ContainerBase.__implements__

    security = ClassSecurityInfo()

    manage_options = ContainerBase.manage_options[:-1] + \
                     _MetadataTool.manage_options # exclude 'Properties'
                     # + ToolBase.manage_options
    WORKFLOW_PREFIX = 'category_'

    _actions = (
            AI( id='manageSubjects'
              , title='Document types'
              , description='Manage valid document types'
              , action=Expression( text='string: ${portal_url}/metadata_subjects_form' )
              , permissions=(CMFCorePermissions.ManagePortal,)
              , category='global'
              , condition=None
              , visible=False
              ),
            AI( id='manageCategories'
              , title='Document categories'
              , action=Expression( text='string: ${portal_url}/manage_categories_form' )
              , permissions=(CMFCorePermissions.ManagePortal,)
              , category='global'
              , condition=None
              , visible=True
              ),
        )

    meta_types = ({'name':'Category',
                   'permission':CMFCorePermissions.ManagePortal,
                   'action':''},
                 )

    def __init__( self, publisher=None, element_specs=DEFAULT_ELEMENT_SPECS ):
        # instance constructor
        ToolBase.__init__( self )
        _MetadataTool.__init__( self, publisher, element_specs )

        self.taskDefinitionFactory = TaskDefinitionFactory()
        self.taskTemplateContainerAdapter = TaskTemplateContainerAdapter()

        self.docflowLogic = DocflowLogic()
        self.versionWorkflowLogic = VersionWorkflowLogic()
        self.resultcodes2Transition = Resultcodes2Transition()

    def _initstate( self, mode ):
        # update attributes
        if not ToolBase._initstate( self, mode ):
            return False

        if hasattr( self, 'categories' ):
            for category in self.categories.values():
                self._setObject( category.getId(), category, set_owner=0 )
            del self.categories

        for category_id in self.objectIds():
            self._upgrade( category_id, CategoryDefinition )

        if mode and not hasattr( self, 'taskDefinitionFactory' ):
            self.taskDefinitionFactory = TaskDefinitionFactory()

        if mode and not hasattr( self, 'taskTemplateContainerAdapter' ):
            self.taskTemplateContainerAdapter = TaskTemplateContainerAdapter()

        if mode and not hasattr( self, 'docflowLogic' ):
            if hasattr( self, 'docflowLogic1' ):
                del self.docflowLogic1
            self.docflowLogic = DocflowLogic()

        if mode and not hasattr( self, 'versionWorkflowLogic' ):
            self.versionWorkflowLogic = VersionWorkflowLogic()

        if mode and not hasattr( self, 'resultcodes2Transition' ):
            self.resultcodes2Transition = Resultcodes2Transition()

        return True

    def addCategory( self, cat_id, title='', default_workflow=1, wf_id=None, allowed_types=None, **kw ):
        """
            Adds a new document category - creates new instance of
            DocumentCategory class and adds it to the self.categories hash

            Arguments:

                'cat_id' -- New category id string.

                'title' -- Category title.

                'default_workflow' -- Determines whether the category should be
                                      bound to the default workflow.

                'wf_id' -- Category workflow id. The workflow with a given id
                           will be associated with the category.

                'allowed_types' -- List of allowed objects types that are
                                   allowed to be in the category.

                '**kw' -- additional category properties as name-value pairs

            Result:

                Reference to the created category object.
         """
        cat_id = str( cat_id ).strip()
        category = self.addObject( CategoryDefinition( cat_id, title ) )

        category.manage_changeProperties( kw )

        if allowed_types:
            category.setAllowedTypes( allowed_types )

        if not wf_id:
            wf_id = self.WORKFLOW_PREFIX + cat_id
            wftool = getToolByName( self, 'portal_workflow' )
            wftool.createWorkflow(wf_id)
            wftool.bindWorkflow(wf_id)
            if default_workflow:
                wf = wftool[wf_id]
                setupWorkflowVars(wf)

        category.setWorkflow( wf_id )

        return category

    def deleteCategories( self, ids ):
        """
          Deletes selected categories from "categories" hash.

          Arguments:

            'ids' -- list of categories ids to be deleted

          Notes:

            Category will not be deleted if at least one object with this
            category exists in the portal.

        """
        catalog  = getToolByName( self, 'portal_catalog' )
        workflow = getToolByName( self, 'portal_workflow' )

        ct_ids = []
        wf_ids = []
        errors = {'deps':0, 'docs':0}

        for id in ids:
            category = self.getCategory( id, None )
            if category is None:
                continue
            has_deps = category.listDependentCategories()
            has_docs = len( catalog.searchResults( category=category.getId(),
                                                   implements='isCategorial'
                                                 ))
            errors['deps'] = errors['deps'] or has_deps
            errors['docs'] = errors['docs'] or has_docs

            if not (has_deps or has_docs):
                ct_ids.append( id )
                wf_ids.append( category.Workflow() )

        if ct_ids:
            workflow.deleteObjects( wf_ids )
            self.deleteObjects( ct_ids )

        return errors

    security.declareProtected( CMFCorePermissions.View, 'getCategory' )
    def getCategory( self, id, default=Missing ):
        """
            Returns category object by category Id.

            Arguments:

                'id' -- category Id string

                'default' -- value to return if no category having
                             the specified Id exist; if not given,
                             an exception is raised in such case

            Result:

                'CategoryDefinition' instance.

            Exceptions:

                'KeyError' -- specified category does not exist
        """
        try:
            return self._getOb( id )
        except AttributeError:
            if default is Missing:
                raise KeyError, id
            return default

    security.declareProtected( CMFCorePermissions.View, 'getCategoryById' )
    def getCategoryById( self, id, default=None ):
        """
            DEPRECATED. Returns category object by category Id.

            Arguments:

                'id' -- category Id string

                'default' -- value to return if no category having
                             the specified Id exist; if not given,
                             'None' is returned by default

            Result:

                'CategoryDefinition' instance.
        """
        if not id:
            return default
        return self._getOb( id, default )

    security.declareProtected( CMFCorePermissions.View, 'listCategories' )
    def listCategories( self, type=None ):
        """
            Returns the list of allowed document categories.

            Arguments:

               'type' -- optional, either portal type Id or an object;
                         if given, only categories allowed for this type
                         (or for the type of the object) are returned

            Result:

                List of 'CategoryDefinition' objects.
        """
        categories = self.objectValues()

        if type:
            if not isinstance( type, StringType ):
                assert type.implements('Contentish')
                type = type.getPortalTypeName()
            categories = [ c for c in categories if c.isTypeAllowed(type) ]

        return categories

    security.declareProtected( CMFCorePermissions.ManagePortal, 'actionOverTable' )
    def actionOverTable( self, REQUEST ):
        """ make action on table """
        c_id = REQUEST.get('c_id', '')
        if c_id=='':
            return 'c_id not specified'
        self.resultcodes2Transition.setModel( self.getCategory(c_id).resultcodes2TransitionModel )

        urlString = ''
        ret = self.resultcodes2Transition.controller.makeActionByRequest( REQUEST )
        if ret != '': urlString = '?ret='+ret
        REQUEST.RESPONSE.redirect( 'task_template_summary' + urlString + '#resultcode2transition')

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setTransitionTaskTemplate' )
    def setTransitionTaskTemplate( self, c_id, transition, task_templates ):
        """ are called from skins/categories/workflows.py
            task_templates = [ 'template_id1', ... ]
        """
        self.getCategory(c_id).transition2TaskTemplate[transition] = task_templates
        self.getCategory(c_id)._p_changed = 1

    security.declareProtected( CMFCorePermissions.View, 'listTransitionsIdsWithNotification' )
    def listTransitionsIdsWithNotification(self, category_id):
        """
            Returns list of transitions ids in which object(s) of
            TaskDefinitionNotification is placed.

            Arguments:

                'category_id' -- id of the category
        """
        result = {}
        category = self.getCategory(category_id)
        ttcontainer = category.taskTemplateContainer
        for transition, templates in category.transition2TaskTemplate.items():
            for template in templates:
                for td in ttcontainer.getTaskTemplate( template ).taskDefinitions:
                    if isinstance(td, TaskDefinitionNotification):
                        result[ transition ] = 1
                        break
        return result.keys()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setState2TaskTemplateToDie' )
    def setState2TaskTemplateToDie( self, c_id, state, task_templates ):
        """ are called from skins/categories/workflows.py
            task_templates = { 'template_id1': 'result_code1', ... }
        """
        self.getCategory(c_id).state2TaskTemplateToDie[state] = task_templates
        self.getCategory(c_id)._p_changed = 1

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getGuardPermissions' )
    def getGuardPermissions( self, guard ):
        return guard.permissions

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getManagedPermissions_' )
    def getManagedPermissions_( self ):
        return Config.ManagedPermissions

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getManagedRoles_' )
    def getManagedRoles_( self ):
        return Config.ManagedRoles

    security.declareProtected( CMFCorePermissions.ManagePortal, 'importFromXML' )
    def importFromXML(self, xml ):
        #
        #
        # Category <-- cat_id, title( may not translated ), default_workflow, allowed-types
        # may be default or not
        #
        # attr <-- attr_id, attr_title( may not translated ), multiple, mandatory, read_only
        #
        # bases <-- bases cats
        #
        # subordinates <-- subordinate cats
        #
        #
        # Move next items to workflow tool
        # state <-- state_id, state_title( may not translated ), transitions, permissions
        #
        # transition <-- tr_id, tr_title( may not translated ), actbox-name( may not translated ), new state id, guard
        #
        # XXX state_attr_permission_roles <-- state, attr, permission, roles XXX
        from xmllib import XMLParser
        raise NotImplementedError

    security.declareProtected( CMFCorePermissions.ManagePortal, 'exportAsXML' )
    def exportAsXML(self, REQUEST ):
        """
            For use
            TODO split it into exportCategoryAsXML,
                               exportAttrAsXML,
                               exportStateAsXML,
                               exportTransitionAsXML,
        """
        from cStringIO import StringIO
        from xml.sax.saxutils import XMLGenerator
        stream = StringIO()
        #stream = open( 'res.xml', 'w+' )
        gen = XMLGenerator( stream, encoding="windows-1251" )
        gen.startDocument()
        gen.startElement( 'categories', {} )

        c_ids = REQUEST.get( 'selected_categories' )
        if c_ids:
            cat_defs = [ self.getCategory(c_id) for c_id in c_ids ]
        else:
            cat_defs = self.listCategories()

        for category in cat_defs:
            gen.startElement( 'category' , { 'id': category.getId()
                                           , 'title': category.Title()
                                           }
                            )

            gen.startElement( 'base-categories', {} )
            for base in category.listBases():
                gen.startElement( 'base-category', { 'id': base.getId() } )
                gen.endElement( 'base-category' )
            gen.endElement( 'base-categories' )

            gen.startElement( 'allowed-types', {} )
            for at in category.listAllowedTypes():
                gen.startElement( 'type', {'id' : at } )
                gen.endElement( 'type' )
            gen.endElement( 'allowed-types' )

            gen.startElement( 'attributes', {} )
            for attr in category.listAttributeDefinitions():
                if attr.isInCategory( category ):
                    gen.startElement( 'attribute', { 'id': attr.getId()
                                                   , 'type': attr.Type()
                                                   , 'title': attr.Title()
                                                   , 'default': str( attr.getDefaultValue() )
                                                   , 'multiple': str( attr.isMultiple() )
                                                   , 'mandatory': str( attr.isMandatory() )
                                                   , 'read_only': str( attr.isReadOnly() )
                                                   }
                                    )
                    gen.endElement( 'attribute' )
            gen.endElement( 'attributes' )

            workflow = category.getWorkflow()
            gen.startElement( 'workflow', {} )

            states = workflow.states
            gen.startElement( 'states', {} )
            for state in states.values():
                if not states.isPrivateItem(state):
                    continue

                gen.startElement( 'state', { 'id': state.getId()
                                           , 'title': state.title
                                           }
                                )
                gen.startElement( 'transitions', {} )
                for t_id in state.transitions:
                    gen.startElement( 'transition', {'id': t_id } )
                    gen.endElement( 'transition' )
                gen.endElement( 'transitions' )

                gen.startElement( 'permissions', {} )
                if state.permission_roles:
                    for perm_id, roles in state.permission_roles.items():
                        gen.startElement( 'permission', { 'id': perm_id
                                                        , 'acquire': str(type(roles) is type([]))
                                                        } )
                        for role in roles:
                            gen.startElement( 'role', {'id': role} )
                            gen.endElement( 'role' )
                        gen.endElement( 'permission' )
                gen.endElement( 'permissions' )

                gen.endElement( 'state' )
            gen.endElement( 'states' )

            transitions = workflow.transitions
            gen.startElement( 'transitions', {} )
            for transition in transitions.values():
                if not transitions.isPrivateItem( transition ):
                    continue

                gen.startElement( 'transition', { 'id': transition.getId()
                                                , 'title': transition.title
                                                , 'actbox-name': transition.actbox_name
                                                , 'new-state': transition.new_state_id
                                                }
                                )

                guard = transition.guard
                if guard:
                    gen.startElement( 'guard-roles', {} )
                    for role in guard.roles:
                        gen.startElement( 'role', {'id': role} )
                        gen.endElement( 'role' )
                    gen.endElement( 'guard-roles' )

                    gen.startElement( 'guard-permissions', {} )
                    for permission in guard.permissions:
                        gen.startElement( 'permission', { 'id': permission } )
                        gen.endElement( 'permission' )
                    gen.endElement( 'guard-permissions' )

                gen.startElement( 'trigger_type', { 'id': str(transition.trigger_type) }  )
                gen.endElement( 'trigger_type' )

                gen.endElement( 'transition' )
            gen.endElement( 'transitions' )

            state_attr_permission_roles = workflow.state_attr_permission_roles
            if state_attr_permission_roles:
                gen.startElement( 'state-attr-perm', {} )
                for (state, attr), perms in state_attr_permission_roles.items():
                    gen.startElement( 'item', {'state':state, 'attr' : attr} )

                    for perm, roles in perms.items():
                        gen.startElement( 'permission', { 'id': perm
                                                        , 'acquire': str(type( roles ) is type([]))
                                                        } )
                        for role in roles:
                            gen.startElement( 'role', {'id': role} )
                            gen.endElement( 'role' )
                        gen.endElement( 'permission' )

                    gen.endElement( 'item' )
                gen.endElement( 'state-attr-perm' )

            gen.endElement( 'workflow' )

            gen.endElement( 'category')

        gen.endElement( 'categories' )
        gen.endDocument()

        setHeader = REQUEST.RESPONSE.setHeader
        setHeader("Content-type", "text/xml");

        try:
            return stream.getvalue()
        finally:
            stream.close()

    security.declareProtected( CMFCorePermissions.View, 'listAttributeTypes' )
    def listAttributeTypes( self, construction=False ):
        types = listValueHandlers()
        if construction:
            # filter out internal (non-addable) types
            types = [ t for t in types if not t.isInternal() ]
        return types

    security.declareProtected( CMFCorePermissions.View, 'getAttributeType' )
    def getAttributeType( self, id ):
        return getValueHandler( id )

    security.declarePrivate( 'listAttributeDefinitions' )
    def listAttributeDefinitions( self, types=None, categories=None ):
        attrs = []

        if categories is None:
            categories = self.listCategories()

        for category in categories:
            if isinstance( category, StringType ):
                category = self.getCategory( category )

            ctitle = category.Title()

            for attr in category.listAttributeDefinitions():
                #if not attr.isInCategory( category ):
                #    continue
                atitle = attr.Title()
                attrs.append( {
                    'uid'   : attr.getResourceUid(),
                    'type'  : attr.Type(),
                    'title' : ctitle+' / '+atitle,
                } )

        return attrs

    security.declarePrivate( 'getAttributeValueFor' )
    def getAttributeValueFor( self, object, uid, default=Missing, moniker=False ):
        assert object.implements('isCategorial')

        category, subid = id.split('/')
        if not object.hasBase( category ):
            if default is not Missing:
                return default
            raise KeyError, id

        return object.getCategoryAttribute( subid, default,
                                            moniker=moniker, restricted=Trust )

    security.declareProtected( CMFCorePermissions.View, 'view' )
    def view( self, REQUEST=None ):
        """
          The default view of the entry contents
        """
        REQUEST = REQUEST or self.REQUEST
        return self.index_html( REQUEST, REQUEST.RESPONSE )

    security.declareProtected( CMFCorePermissions.View, 'index_html' )
    def index_html( self, REQUEST, RESPONSE ):
        """
          Returns the entry contents
        """
        return self.manage_categories_form( self, REQUEST )

InitializeClass( MetadataTool )


def initialize( context ):
    # module initialization callback

    context.registerTool( MetadataTool )
