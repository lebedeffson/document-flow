"""
CategoryDefinition class.

$Editor: vpastukhov $
$Id: CategoryDefinition.py,v 1.35 2007/05/24 12:46:24 oevsegneev Exp $
"""
__version__ = '$Revision: 1.35 $'[11:-2]

from types import NoneType, StringType, TupleType

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import Item
from ZODB.PersistentList import PersistentList

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Features, Exceptions
from CategoryAttribute import CategoryAttribute, CategoryAttributesContainer
from Features import createFeature
from Resultcodes2Transition import Resultcodes2TransitionModel
from TaskTemplateContainer import TaskTemplateContainer
from SimpleObjects import InstanceBase
from Utils import InitializeClass, getObjectByUid, uniqueValues, isBroken
from ValueTypes import DerivedValueBase


class CategoryDefinition( InstanceBase, Item ):
    """
        Content category definition.
    """
    _class_version = 1.54

    meta_type = 'Category'

    __resource_type__ = 'category'

    __implements__ = createFeature('isCategoryDefinition'), \
                     Features.isAttributesProvider, \
                     Features.isNavigable, \
                     Features.hasTabs, \
                     Features.hasHeadingInfo, \
                     InstanceBase.__implements__

    security = ClassSecurityInfo()
    security.declareProtected( CMFCorePermissions.ManagePortal, 'setTitle' )

    allowed_types = ()
    _subitems = ['attributes','taskTemplateContainer']

    _properties = InstanceBase._properties + (
            { 'id':'work_template', 'type':'string', 'mode':'w'
            },#, 'title':'Templates for the documents'},
            { 'id':'content_fixed', 'type':'boolean', 'mode':'w'
            , 'title':' User can edit only additional fields values' },
            { 'id':'lock_timeout', 'type':'time_period', 'mode':'w'
            , 'title': 'Lock timeout' },
            { 'id':'primary_category', 'type':'string', 'mode':'wn' },
            { 'id':'disallow_manual', 'type':'boolean', 'mode':'w'
            , 'title':'Category cannot be manually picked by users' },
            { 'id':'show_id', 'type':'boolean', 'mode':'w'
            , 'title': 'Show ID field' },
            { 'id':'templet_creation', 'type':'boolean', 'mode':'w'
            , 'title': 'Use template on document creation' }
        )

    # default property values
    work_template = ''
    content_fixed = False
    lock_timeout = 1800
    primary_category = None
    disallow_manual = False

    def __init__( self, id, title='' ):
        # instance constructor
        InstanceBase.__init__( self, id, title )

        self.attributes = CategoryAttributesContainer( 'attributes' )
        self.taskTemplateContainer = TaskTemplateContainer( 'taskTemplateContainer' )
        self.resultcodes2TransitionModel = Resultcodes2TransitionModel()

        # transition2TaskTemplate =
        #   { 'transition_id1':
        #     [ 'task_template_id1', 'task_template_id2', ... ],
        #     ...
        #   }
        self.transition2TaskTemplate = {}

        # state2TaskTemplateToDie =
        #   { 'state_id1':
        #     { 'task_template_id1': 'result_code1' , ... },
        #     ...
        #   }
        self.state2TaskTemplateToDie = {}

        # allow_only_single_version =
        #   { 'state_id1': 'transition_for_exclude1', 'state_id2', 'transition_for_exclude2', ... }
        self.allow_only_single_version = {}

        self._bases = []
        self._order = PersistentList()

    def _initstate( self, mode ):
        # initialize attributes
        if not InstanceBase._initstate( self, mode ):
            return False

        if hasattr( self, 'fields' ): # smth very old
            self.attributes = CategoryAttributesContainer( 'attributes' )
            for id, value in self.fields.items():
                self.attributes._setObject( id, value )
                self.attributes._upgrade( id, CategoryAttribute )
            del self.fields

        elif mode and isBroken( self.attributes ): # < 1.53
            attributes = self._upgrade( 'attributes', CategoryAttributesContainer )
            for id in attributes.objectIds():
                attributes._upgrade( id, CategoryAttribute )

        if mode:
            if not hasattr( self, '_bases' ):
                self._bases = []
            elif type( self._bases ) is TupleType: # < 1.54
                self._bases = list( self._bases )

            bases = []
            for base in self._bases:
                if type(base) is not StringType:
                    base = base.getId()
                bases.append( base )

            if bases != self._bases:
                self._bases = bases

        if hasattr( self, 'edit_template_fields_only' ): # < 1.45
            self.content_fixed = not not self.edit_template_fields_only
            del self.edit_template_fields_only

        if hasattr( self, '_lock_timeout' ): # < 1.45
            self.lock_timeout = self._lock_timeout
            del self._lock_timeout

        if hasattr( self, '_primaryCategory' ): # < 1.45
            self.primary_category = self._primaryCategory or None
            del self._primaryCategory

        if type(self.primary_category) not in [NoneType,StringType]: # < 1.48
            try:
                self.primary_category = self.primary_category.getId()
            except:
                self.primary_category = None

        if mode and not hasattr( self, 'taskTemplateContainer' ):
            self.taskTemplateContainer = TaskTemplateContainer( 'taskTemplateContainer' )

        if mode and not hasattr( self, 'resultcodes2TransitionModel' ):
            self.resultcodes2TransitionModel = Resultcodes2TransitionModel()

        if mode and not hasattr( self, 'transition2TaskTemplate' ):
            self.transition2TaskTemplate = {}

        if mode and not hasattr( self, 'state2TaskTemplateToDie' ):
            self.state2TaskTemplateToDie = {}

        if mode and not hasattr( self, 'allow_only_single_version' ):
            self.allow_only_single_version = {}

        if mode and not hasattr( self, '_order' ): # < 1.51
            self._order = PersistentList()

        return True

    def __cmp__( self, other ):
        # compare category objects by identifier
        if other is None:
            return 1
        if isinstance( other, CategoryDefinition ):
            return cmp( self.getId(), other.getId() )
        if type(other) is not StringType:
            raise TypeError, other
        return cmp( self.getId(), other )

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
        return self.main_category_form( self, REQUEST )

    def getCategory(self):
        return self

    security.declarePrivate( 'setWorkflow' )
    def setWorkflow( self, workflow ):
        """
            Sets the category workflow.

            Arguments:

                'workflow' -- workflow to bind
          """
        self.workflow = workflow

    security.declarePublic( 'disallowManual' )
    def disallowManual( self ):
        """
        """
        return self.getProperty( 'disallow_manual' )

    security.declareProtected( CMFCorePermissions.View, 'listTemplates' )
    def listTemplates(self, type_name=None):
        """
        """
        links_tool = getToolByName(self, 'portal_links')
        templates = [link.getObject()
                     for link in links_tool.searchLinks(source=self, relation='reference', target_removed=False)]

        results = []
        if type_name is not None:
            for t in templates:
                target = t.getTargetObject()
                if target.implements('isVersion') and target.getVersionable().meta_type == type_name or \
                   t.getTargetMetadata(name='meta_type') == type_name:
                    results.append(t)

            return results

        return templates

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setTemplate' )
    def setTemplate( self, template, template_version=None ):
        """
            Sets new category template.

            Arguments:

                'template'          --  Either Uid of the document (String) or
                                        the document instance.

                'template_version'  --  Version id of the document (String).
        """
        if type(template) is StringType:
            template = getObjectByUid( self, template)
        if not template:
            return
        if template.implements('isVersionable') and template_version:
            template = template.getVersion(template_version)
        links_tool = getToolByName( self, 'portal_links' )
        links_tool.restrictedLink( self, template, 'reference' )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'deleteTemplates' )
    def deleteTemplates( self, templates):
        """
            Deletes selected templates.

            Arguments:

                'templates' --  Template ids.
        """
        links_tool = getToolByName(self, 'portal_links')
        links_tool.removeLinks( ids=templates, restricted=Trust )
        if self.getWorkTemplateId() in templates:
            self.setWorkTemplate('')

    security.declareProtected( CMFCorePermissions.View, 'getWorkTemplateId' )
    def getWorkTemplateId( self ):
        """
            Returns the associated main template id.

            Result:

                Template id (String).
        """
        return self.getProperty( 'work_template' )

    security.declareProtected( CMFCorePermissions.View, 'getWorkTemplate' )
    def getWorkTemplate( self ):
        """
            Returns the associated main template object.

            Result:

                Template (Instance).
        """
        links_tool = getToolByName( self, 'portal_links' )
        work_template_id = self.getProperty( 'work_template' )
        template_brains = work_template_id and links_tool.searchLinks( source=self, id=work_template_id )

        return template_brains and template_brains[0].getObject().getTargetObject()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setWorkTemplate' )
    def setWorkTemplate(self, work_template):
        """
            Sets main template id.

            Arguments:

                'work_template' --  Template id (String).
        """
        self._updateProperty( 'work_template', work_template)

    security.declarePublic( CMFCorePermissions.View, 'isTempletCreation' )
    def isTempletCreation( self ):
        """
        """
        template = self.getWorkTemplate()
        if not template: 
            return None
        template_attrs = template.listBodyFields()
        category_attrs = self.listAttributeDefinitions()
        absent_attrs = [a for a in category_attrs if a.isMandatory() and a.getId() not in template_attrs]

        return self.getProperty( 'templet_creation' ) and template and not absent_attrs

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setCreationMode' )
    def setCreationMode( self, is_tc=None ):
        """
        """
        self._updateProperty( 'templet_creation', is_tc )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setEditMode' )
    def setEditMode( self, fixed=None ):
        """
            Sets the edit mode for documents of category.
            if "fixed" is true, user can edit only additional fields values

            Arguments:

                'fixed' - string to turn on/off editing only additional fields values
        """
        self._updateProperty( 'content_fixed', fixed )

    security.declarePublic( 'isContentFixed' )
    def isContentFixed( self ):
        """
            Returns the edit mode for documents of category.
            User can edit text of the document or only additional fields values

            Result:

                Boolean.
        """
        return self.getProperty('content_fixed')

    security.declareProtected( CMFCorePermissions.View, 'applyDocumentTemplate' )
    def applyDocumentTemplate( self, object, selected_template=None ):
        """
            Copies attaches from template document. Fills document with template document text.

            Arguments:

              'object' -- document to be filled with template text and attachments

        """
        links = getToolByName( self, 'portal_links' )

        if selected_template=='not use':return

        if not selected_template:
            selected_template = self.getProperty('work_template')
            if not selected_template:
                return

        link = links._getOb(selected_template, None)
        if not link or link.isTargetRemoved():
            return

        template = link.getTargetObject()
        if template.getPortalTypeName() != object.getPortalTypeName():
            if not object.implements( 'isHTMLDocument' ) and not template.implements( 'isHTMLDocument' ):
                return

        # Copy attachments from template document
        for attach in template.listAttachments():
            object.getVersion()._setObject(attach[0], attach[1]._getCopy(object))
            object.getVersion().attachments.append(attach[0])

        # Associate new document with attach if necessary
        if template.associated_with_attach:
            id = template.associated_with_attach
            object.associateWithAttach(id)

        # Fill new document with template document text
        text = template.text
        object.edit( 'html', text )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'addAttributeDefinition' )
    def addAttributeDefinition( self, name, type, title='', default=None, multiple=Missing,
                                mandatory=Missing, read_only=Missing, properties=None ):
        """
          Adds a new category attribute definition.

          Arguments:

              'name' -- attribute id.

              'type' -- attribute type.

              'title' -- attribute title.

              'default' -- attribute default value.

              'mandatory' -- Boolean. Indicates whether the attribute is mandatory.

              'read_only' -- Boolean. Indicates whether the attribute is read only.

          Exceptions:

              KeyError -- Raised if attribute with the given id already exists.

        """
        try:
            self.getAttributeDefinition( name )
        except KeyError:
            pass
        else:
            raise Exceptions.DuplicateIdError( "The attribute %(name)s already exists.", name=name )

        # TODO multi-values should be supported by all types
        if type in ('userlist', 'advanced_userlist'):
            multiple = True
        elif type != 'lines':
            multiple = False

        title = title or name

        adef = CategoryAttribute( name, title, type,
                                  multiple=multiple,
                                  mandatory=mandatory,
                                  read_only=read_only )

        adef = self.attributes.addObject( adef )

        # append new attribute's id to self and dependent categories' _order lists
        id = adef.getId()
        self._order.append( id )
        for cat in self.listDependentCategories():
            if id not in cat._order:
                cat._order.append( id )

        # set type-specific properties
        if properties:
            adef.setProperties( properties )

        # done unless default value is given
        if default is not None:
            adef.setDefaultValue( default )

        for cat in self.listSubordinateCategories():
            cat.setPrimaryCategory(self)

    security.declareProtected( CMFCorePermissions.ManagePortal, 'deleteAttributeDefinitions' )
    def deleteAttributeDefinitions( self, ids ):
        """
            Deletes specified attributes from the document category.

            Arguments:

                'ids' -- List of attribute ids to be removed.
        """
        catalog = getToolByName( self, 'portal_catalog' )
        results = catalog.searchResults( category=self.getId(),
                                         implements='isCategorial'
                                       )
        objects = filter( None, [ r.getObject() for r in results ] )
        for object in objects:
            object.deleteCategoryAttributes( ids )

        for id in ids:
            try:
                self._order.remove( id )
                for cat in self.listDependentCategories():
                    try:
                        attr = cat.getAttributeDefinition( id )
                        if not attr.isInCategory( cat ):
                            cat._order.remove( id )
                    except KeyError:
                        pass

            except ValueError:
                pass

        self.attributes.deleteObjects( ids )
        # Check for deleted attributes in base categories

        attr_ids = [ attr.getId() for attr in self._listAttributeDefinitions() ]
        for id in attr_ids:
            if id not in self._order:
                self._order.append( id )

        for cat in self.listSubordinateCategories():
            cat.setPrimaryCategory(self, remove_attrs=ids)

    security.declarePublic( 'listAttributeDefinitions' )
    def listAttributeDefinitions( self ):
        """
            Returns the sorted list of the document category attributes.

            Result:

              List of CategoryAttribute class instances.
        """

        order = self._order
        attributes = []
        for id in order[:]:
            try:
                attr = self.getAttributeDefinition( id )
                attributes.append( attr )
            except KeyError:
                order.remove( id )

        # uniqueValues for compatibility
        return uniqueValues(attributes)

    security.declarePrivate( '_listAttributeDefinitions' )
    def _listAttributeDefinitions( self ):
        """
            Returns the list of the local category attributes.

            Result:

              List of CategoryAttribute class instances.
        """

        attributes = self.attributes.objectValues()
        for base in self.listBases():
            attributes.extend(base.listAttributeDefinitions())

        # filtering by ID in order like in attributes
        # may be better sorting
        # early return attributes
        temp_dict = {}
        attr_uniq = []

        for atr in attributes:
            if not temp_dict.has_key(atr.getId()):
                attr_uniq.append(atr)
                temp_dict[atr.getId()] = 1

        return attr_uniq

    security.declarePublic( 'getAttributeDefinition' )
    def getAttributeDefinition( self, id, default=Missing ):
        """
            Returns an attribute definition given it's id.

            Arguments:

               'id' -- Attribute id string.

            Exceptions:

                KeyError -- Raised if specified attribute was not found in the
                            category definition.

            Result:

               Attribute definition object.
        """
        try:
            return self.attributes._getOb( id )
        except AttributeError:
            pass

        for base in self.listBases():
            try:
                return base.getAttributeDefinition( id )
            except KeyError:
                pass

        if default is not Missing:
            return default
        raise KeyError, id

    security.declarePublic( 'moveAttribute' )
    def moveAttribute( self, id=None, direction=1, REQUEST=None ):
        """
        """
        order = self._order
        direction = int(direction) < 0 and -1 or 1
        index = order.index( id ) # may raise IndexError

        # How about checking for border of the list
        order[ index ], order[ index - direction ] = order[ index - direction ], order[ index ]

        if REQUEST is not None:
            return self.redirect( REQUEST=REQUEST, action='category_metadata_form' )

    security.declarePublic( 'Workflow' )
    def Workflow( self ):
        """
            Returns the associated workflow id.

            Note:

                This method is obsolete, getWorkflow should be used instead.

            Result:

                String.
        """
        return self.workflow

    def getWorkflow( self ):
        """
            Returns the associated workflow object.

            Result:

                Workflow definition object.
        """
        workflow = getattr(self, 'workflow', None)
        if type(workflow) is StringType:
            wftool = getToolByName( self, 'portal_workflow' )
            workflow = wftool.getWorkflowById( workflow )

        return workflow

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setAllowedTypes' )
    def setAllowedTypes( self, type_ids ):
        """
            Sets up the list of the portal meta types supported by the category

            Arguments:

                'type_ids' -- list of meta types supported by category

        """
        self.allowed_types = type_ids

    security.declareProtected( CMFCorePermissions.View, 'listAllowedTypes' )
    def listAllowedTypes( self ):
        """
            Returns the list of the portal meta types supported by the category

            Result:

               List of strings.

        """
        return self.allowed_types

    security.declareProtected( CMFCorePermissions.View, 'isTypeAllowed' )
    def isTypeAllowed( self, type_id ):
        """
            Checks whether this category supports the given content type

            Arguments:

                'type_id' -- content type to check
        """
        if type(type_id) is not StringType:
            type_id = type_id.getId()
        return ( type_id in self.allowed_types )

    security.declareProtected( CMFCorePermissions.View, 'categoryImplements' )
    def categoryImplements( self, feature ):
        """
           Checks whether at least one one of allowed content types implements the given feature.
        """
        types_tool = getToolByName( self, 'portal_types' )
        for type_name in self.listAllowedTypes():
            type_info = types_tool.getTypeInfo(type_name)
            if type_info.typeImplements( feature ):
                return 1
        return None

    security.declareProtected( CMFCorePermissions.View, 'getLockTimeout' )
    def getLockTimeout(self):
        """
            Returns object lock timeout for this category

            Result:

                int, number of seconds
        """
        return self.lock_timeout

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setLockTimeout' )
    def setLockTimeout(self, lock_timeout):
        """
            Sets lock timeout for category objects

            Arguments:

                'lock_timeout' -- time in seconds

        """
        self.lock_timeout = lock_timeout


    security.declareProtected( CMFCorePermissions.ManagePortal, 'manageAllowSingleStateForVersionArray' )
    def manageAllowSingleStateForVersionArray( self, action, state, transition_for_exclude=None ):
        """
          Manage states where can exists only one version

          Arguments:

            'action' -- action to perform ('add' | 'remove')

            'state' -- state for which perform action

            'transition_for_exclude' -- for action 'add', this mean trasnition by which 'old' version
                                        will be excluded

          Note:

            Are called from workflow.py

        """
        if action=='add':
            self.allow_only_single_version[state]=transition_for_exclude
            self._p_changed = 1
        elif action=='remove' and state in self.allow_only_single_version.keys():
            del self.allow_only_single_version[state]
            self._p_changed = 1

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setBases' )
    def setBases(self, bases):
        """
            Sets up the list of the category ancestors.

            Arguments:

                'bases' -- List of the CategoryDefinition class instances
                           or ids. All categories already inheriting from the
                           current category are removed from the list.
        """
        old_attrs = self._listAttributeDefinitions()

        # Remove cross-references to avoid infinite recursion.
        valid_bases = []
        permissions = []
        dependent = self.listDependentCategories()

        for base in bases:
            if type( base ) is StringType:
                base = self.getCategoryById( base )

            if base not in dependent:
                valid_bases.append( base.getId() )
                # XXX: fix this
                permissions.extend( base.getWorkflow().permissions )

        self._bases = valid_bases

        for cdef in [self,] + self.listDependentCategories():
            wf = cdef.getWorkflow()
            for id in ['states', 'transitions']:
                wf[id].notifyChanged()

            # Remove nonexisting transitions from states properties.
            states = wf.states
            transitions = wf.transitions
            for state in states.values():
                if states.isPrivateItem( state ):
                    tr_ids = [ tr_id for tr_id in state.getTransitions() if hasattr( transitions, tr_id ) ]
                    state.setProperties( state.title, tr_ids )

        wf = self.getWorkflow()
        # Get initial state from the first ancestor category.
        initial_state = wf.initial_state
        if not (initial_state and wf.states.get( initial_state, None )) and bases:
            base = bases[0]
            if type( base ) is StringType:
                base = self.getCategoryById( base )
            wf.initial_state = base.getWorkflow().initial_state
        elif initial_state is not None and not wf.states.get( initial_state, None ):
            # Set inherited initial state to None when ancestor category was removed.
            wf.initial_state = None

        if wf:
            # Cleanup workflow data cache
            for id in ['states', 'transitions', 'scripts']:
                wf[id].notifyChanged()
            wf.permissions = tuple( uniqueValues(permissions) )

        new_attrs = self._listAttributeDefinitions()
        new_attrs_ids = [atr.getId() for atr in new_attrs]
        old_attrs_ids = [atr.getId() for atr in old_attrs]

        removed_attrs = filter( lambda x, new=new_attrs_ids: x.getId() not in new, old_attrs )
        added_attrs = filter( lambda x, old=old_attrs_ids: x.getId() not in old, new_attrs )

        #del removed attrs from order
        for attr in removed_attrs:
            self._order.remove(attr.getId())

        # Add ids of new attributes to _order list
        self._order += [ atr.getId() for atr in added_attrs if atr.getId() not in self._order ]

        catalog = getToolByName(self, 'portal_catalog')
        results = catalog.searchResults( category = self.getId(),
                                         implements='isCategorial'
                                       )

        objects = map( lambda x: x.getObject(), results)
        objects = filter( None, objects )
        for object in objects:
            for attr in added_attrs:
                object.setCategoryAttribute(attr)

            object.deleteCategoryAttributes(removed_attrs)

    security.declareProtected( CMFCorePermissions.View, 'listBases' )
    def listBases(self, recursive=False):
        """
            Returns the category ancestors.

            Arguments:

                'recursive' -- False value indicates that only first-level bases
                            should be returned, otherwise return the full list
                            of category ancestors.

            Result:

                List of CategoryDefinition class instances.
        """
        bases = map(self.parent().getCategory, self._bases)

        if not recursive:
            return bases

        results = []
        for base in bases:
            results.append(base)
            results.extend(base.listBases(recursive=True))

        return uniqueValues(results)

    security.declareProtected( CMFCorePermissions.View, 'listBaseIds' )
    def listBaseIds(self, recursive=True, include_self=True):
        """
            Returns the category ancestor ids.

            Arguments:

                'recursive' -- False value indicates that only first-level bases
                            should be returned, otherwise return the full list
                            of category ancestors.

                'include_self' -- True value indicates that context category id 
                            should be included into result list.

            Result:

                List of category ids.
        """
        base_ids = [c.getId() for c in self.listBases( recursive = recursive )]

        if include_self: 
            base_ids.append(self.getId())

        return base_ids

    def hasBase(self, base = None, recursive = True):
        """
            Checks whether the document's category inherits or equal to the given category.

            Result:

                Boolean value if base is not None, otherwise returns the list of
                base categories ids including the current document's category.
        """

        if base is None:
            # Catalog indexing support
            results = [self] + self.listBases(recursive = True)
            return [x.getId() for x in results]

        if type(base) is not StringType:
            base = base.getId()

        if base == self.getId() or base in self._bases:
            return True

        if recursive:
            for superbase in self._bases:
                if self.parent().getCategory(superbase).hasBase(base):
                    return True

        return False

    security.declareProtected( CMFCorePermissions.View, 'listDependentCategories' )
    def listDependentCategories(self):
        """
            Lists categories that inherit from the current category.

            Result:

                List of CategoryDefinition class instances.
        """
        result = []

        for category in self.listCategories():
            if category != aq_base(self) and \
               category.hasBase(self, recursive = False):
                result += [category] + category.listDependentCategories()

        return result

    def _listDependentCategoryIds(self, attribute_id):
        """
            Lists ids of categories wich inheriting given attribute.
        """
        # TODO skip dependent categories with inherited overriden definition

        return [category.getId()
                for category in self.listDependentCategories()
                # attribute definition is overriden
                if not category.attributes.hasObject(attribute_id)]


    security.declareProtected( CMFCorePermissions.ManagePortal, 'setPrimaryCategory' )
    def setPrimaryCategory( self, category=None, remove_attrs=[] ):
        """
            Sets primary category for documents of this category.

            Arguments:

                'category'  --  category id or CategoryDefinition instance.
        """
        sub_attribs = [ x.getId() for x in self.listAttributeDefinitions () if x.isSubordinate() and x.getId() in remove_attrs ]
        self.deleteAttributeDefinitions( sub_attribs )

        md_tool = getToolByName(self, 'portal_metadata')
        if type(category) is StringType:
            category = md_tool.getCategoryById(category)

        self.primary_category = category and category.getId() or None

        if not category:
            return

        cat_bases = self.listBases()
        self.setBases( [] )

        for attr in category.listAttributeDefinitions():
            try:
                self.addAttributeDefinition( attr.getId(), attr.Type(), title=attr.Title(), \
                                             multiple=attr.isMultiple(), mandatory=attr.isMandatory() )
                new_attr = self.getAttributeDefinition( attr.getId() )
                new_attr.setDefaultValue(attr.getDefaultValue())
                new_attr.setSubordinate()
            except Exceptions.DuplicateIdError:
                pass

        self.setBases( cat_bases )

    security.declareProtected( CMFCorePermissions.View, 'getPrimaryCategory' )
    def getPrimaryCategory( self ):
        """
            Returns primary category id.
        """
        return self.primary_category or None

    security.declareProtected( CMFCorePermissions.View, 'listSubordinateCategories' )
    def listSubordinateCategories( self ):
        """
          Returns list of subordinate categories ids.
        """
        result = []
        for cdef in self.listCategories():
            if self.getId() == cdef.getPrimaryCategory():
                result.append(cdef)
                result.extend(cdef.listSubordinateCategories())
        return result

    def hasInitialStateOrTransition( self ):
        """
            Indicates whether the category has initial state or transition.
            Returns True if it does, False otherwise.

            Note:   If the category has no states or transitions at all,
                    False is returned as well.
        """

        wf = self.getWorkflow()
        state_ids = wf.states.keys()
        initial_state_id = wf.states.initial_state

        transition_ids = wf.transitions.keys()
        initial_transition_id = wf.transitions.getInitialTransition()

        return (initial_state_id in state_ids or initial_transition_id in transition_ids)

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setAfterTransitionActions' )
    def setAfterTransitionActions( self, transition_id, action_ids ):
        """
            Binds the given docflow actions to the workflow transition.
        """
        # XXX Move this to the WorkflowDefinition
        self.transition2TaskTemplate[transition_id] = action_ids
        self._p_changed = 1

    # XXX Eventually rename this to listActions and rewrite ActionTool.
    security.declareProtected(CMFCorePermissions.View, 'listDFActions')
    def listDFActions( self ):
        """
            Returns the list of docflow actions created within the category definition.
        """
        return self.taskTemplateContainer.getTaskTemplates()

    def listTabs(self):
        """
            See Feature.hasTabs interface
        """
        REQUEST = self.REQUEST
        msg = getToolByName( self, 'msg' )
 
        tabs = []
        append_tab = tabs.append

        #type = self.getTypeInfo()
        link = REQUEST.get('link', '')

        append_tab( { 'url' : self.relative_url( action='main_category_form', frame='inFrame' )
                    , 'title' : msg('Information')
                    } )

        if link.find('view') >=0 or link.find('main_category_form') >=0:
            tabs[-1]['selected'] = True
            tabs[-1]['selected_color'] = '#ffffff'

        action = 'metadata_edit_form'
        append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                    , 'title' : msg('Metadata')
                    } )
        if link.find(action) >= 0:
            tabs[-1]['selected'] = True
            tabs[-1]['selected_color'] = '#ffffff'


        return tabs
        

InitializeClass( CategoryDefinition )


class SubordinateAttribute( DerivedValueBase ):
    """
        Attribute of the primary object having the same Id.
    """

    _type = 'object'

    def getPrimary( self, attr ):
        cat_id = attr.parent().parent().getPrimaryCategory()
        if cat_id is None:
            return None
        metadata = getToolByName( attr, 'portal_metadata' )
        category = metadata.getCategoryById( cat_id )
        return category.getAttributeDefinition( attr.getId(), None )

    def setPrimary( self, attr, primary ):
        assert primary is None

    def getDefaultValue( self, attr=Missing, moniker=False ):
        # use None for unspecified attribute
        if attr is Missing:
            return self._default

        # obtain default value from the primary category
        primary = self.getPrimary( attr )
        if primary is None:
            # no primary attribute -- return default value of the real type
            return DerivedValueBase.getDefaultValue( self, attr, real=True, moniker=moniker )

        return primary.getDefaultValue( moniker=moniker )

    def getDerivedValue( self, attr, object, default=Missing, moniker=False ):
        # obtain value from the primary object
        primary = object.getPrimaryDocument()

        if primary is None:
            if default is not Missing:
                return default
            # no primary document -- return default value of the real type
            return DerivedValueBase.getDefaultValue( self, attr, real=True, moniker=moniker )

        return primary.getCategoryAttribute( attr.getId(), default,
                                             moniker=moniker, restricted=Trust )

    def notifyPropertiesChanged( self, attr, previous=None ):
        DerivedValueBase.notifyPropertiesChanged( self, attr, previous )

        primary = self.getPrimary( attr )
        if primary is not None:
            attr.type = primary.Type()
            attr.multiple = primary.isMultiple()

        elif not attr.Type():
            attr.type = self._type
            attr.multiple = False


class CategoryResource:

    def identify( portal, object ):
        if object.implements('isCategoryAttribute'):
            category = object.parent().parent()
            return { 'uid'       : category.getId(),
                     'attribute' : object.getId() }

        if object.implements('isCategoryAction'):
            template = object.parent()
            category = template.parent().parent()
            return { 'uid'     : category.getId(),
                     'action'  : template.getId(),
                     'subitem' : object.getId() }

        return { 'uid': object.getId() }

    def lookup( portal, uid=None, action=None, subitem=None, attribute=None, **kwargs ):
        metadata = getToolByName( portal, 'portal_metadata' )

        object = metadata.getCategoryById( str(uid) )
        if object is None:
            raise Exceptions.LocatorError( 'category', uid )

        if attribute is not None:
            try:
                return object.getAttributeDefinition( attribute )
            except KeyError:
                raise Exceptions.LocatorError( 'category.attribute', attribute )

        if action is None and subitem is None:
            return object

        try:
            object = object.taskTemplateContainer.getTaskTemplate( action )
        except KeyError:
            raise Exceptions.LocatorError( 'category.action', action )

        object = object.getTaskDefinitionById( subitem )
        if object is None:
            raise Exceptions.LocatorError( 'category.action.subitem', subitem )

        return object


def initialize( context ):
    # module initialization callback

    context.registerResource( 'category', CategoryResource, moniker='content' )

    context.registerValueType( SubordinateAttribute, 'subordinate' )
