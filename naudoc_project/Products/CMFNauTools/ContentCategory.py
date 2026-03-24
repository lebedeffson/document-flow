""" ContentCategory class
$Id: ContentCategory.py,v 1.104 2007/03/02 15:38:06 oevsegneev Exp $
"""
__version__ = '$Revision: 1.104 $'[11:-2]

from types import StringType
from Acquisition import aq_base, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFCore import CMFCorePermissions
from Config import Permissions

import Features, Exceptions
from SimpleObjects import ItemBase
from SyncableContent import SyncableContent
from Utils import InitializeClass, parseDate, readLink, updateLink, \
     isSequence, tuplify


class ContentCategory( ItemBase ):
    """
        Content category type
    """
    _class_version = 1.14

    __implements__ = Features.isCategorial

    security = ClassSecurityInfo()

    # default attribute values
    category = None

    def __init__( self, category, category_template=None,
                        category_primary=None, category_attributes=None ):
        """
            Initializes category-related instance attributes.
        """
        if category is not None:
            if type(category) is not StringType:
                category = category.getId()
            self.category = category

        if category_template:   self._v_category_template   = category_template
        if category_primary:    self._v_category_primary    = category_primary
        if category_attributes: self._v_category_attributes = category_attributes

    def _instance_onCreate( self ):
        self._setupCategory()

    def _setupCategory( self ):
        if not self.implements('isCategorial'):
            return

        try:
            category = self.getCategory()
            assert category is not None

            if self.isContentEmpty():
                template = getattr( self, '_v_category_template', None )
                category.applyDocumentTemplate( self, template )

            if hasattr( self, '_v_category_primary' ):
                self.setPrimaryDocument( *self._v_category_primary )

            attrs = {}
            if hasattr( self, '_v_category_attributes' ):
                attrs.update( self._v_category_attributes )

            for attr in category.listAttributeDefinitions():
                if not attrs.has_key( attr.getId() ):
                    attrs[ attr.getId() ] = attr.getDefaultValue()

            self.setCategoryAttributes( attrs, restricted=Trust )

        finally:
            for name in ['_v_category_template','_v_category_primary','_v_category_attributes']:
                if hasattr( self, name ):
                    delattr( self, name )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setCategory' )
    def setCategory( self, category, manual=False ):
        """
            Associates the document with a given category.

            Note:

                This method is obsolete and left for compatibility purposes only.
                It's strongly recommended to specify the content's category upon
                the creation time using constructor's 'category' argument.

            Arguments:

                'category' -- Either a category definition object or a category
                              id string.

                'manual' -- boolean flag, true if the category is being changed
                            manually by the end-user; default is false
        """
        if type(category) is StringType:
            metadata = getToolByName(self, 'portal_metadata')
            category = metadata.getCategoryById(category)

        if manual and category.disallowManual():
            # TODO implement moniker
            raise Exceptions.SimpleError( 'categories.category_disallowed',
                                          category=category.Title() )

        self.category = category.getId()
        self._setupCategory()

        if hasattr( aq_base(self), 'reindexObject' ):
            self.reindexObject( idxs=['category','hasBase','CategoryAttributes'] )

    def Category(self):
        """
            Returns the document's category id.

            Note:

                This method is obsolete, getCategory should be used instead.
        """
        category = self.category
        if not category:
            category = self._getDefaultCategory()
            return category and category.getId()

        return category

    def getCategory(self):
        """
            Returns the document's category.

            Result:

                Category definition object.
        """
        category = self.category
        if type(category) is StringType:
            metadata = getToolByName(self, 'portal_metadata')
            category = metadata.getCategoryById(category)

        if not category:
            category = self._getDefaultCategory()

        return category

    def _getDefaultCategory(self):
        """
            Returns the object's default category.
        """
        metadata = getToolByName(self, 'portal_metadata')
        categories = metadata.listCategories(self)
        if categories:
            return categories[0]
        return None

    security.declareProtected( CMFCorePermissions.View, 'isInCategory' )
    def isInCategory( self, category, strict=1 ):
        """
            Checks whether the document belongs to a given category.

            Arguments:

                'category' -- Either category definition object or category
                              identifier to check against.  Alternatively,
                              a list of definition objects or identifiers
                              may be given.

                'strict' -- Boolean flag, true by default. If false,
                            the category inheritance hierarchy is checked
                            additionally.

            Result:

                Boolean.
        """
        if isSequence( category ):
            categories = category
        else:
            categories = [category]

        mine = self.getCategory()

        for category in categories:
            if mine == category:
                return 1
            if not strict and category in mine.listBases( recursive=True ):
                return 1

        return 0

    def setCategoryAttributes( self, attrs=None, restricted=True, REQUEST=None ):
        """
            Sets the document category attributes.

            Arguments:

              'attrs' -- dictionary, where
                         key - attribute name,
                         value - attribute value to set

            Note: perform reindex of object

        """
        restricted = restricted is not Trust
        category = self.getCategory()
        if not category:
            return

        if REQUEST:
            attributes = category.listAttributeDefinitions()
            attrs = {}
            for attribute in attributes:
                if attribute.isReadOnly():
                    continue

                name = attribute.getId()
                value = REQUEST.get( name )
                if (value is None or value == '') and attribute.isMandatory():
                    raise Exceptions.SimpleError, 'Mandatory attribute missing'

                if REQUEST.has_key( name ):
                    attrs[name] = REQUEST.get( name )

        for name, value in attrs.items():
            attr = category.getAttributeDefinition( name )
            if attr is None:
                raise KeyError, 'Invalid category attribute specified'

            if not restricted or self.checkAttributePermissionModify(attr):
                self._setCategoryAttribute( attr, value, reindex=False )

        if hasattr( aq_base(self), 'reindexObject' ):
            self.reindexObject( idxs=['CategoryAttributes'] )

    def setCategoryAttribute(self, attr, value=Missing):
        """
            Sets the value of the document category attribute.

            Arguments:

                'attr' -- Either a CategoryAttribute class instance or an
                          attribute id string.

                'value' -- Attribute value. If no value given, attribute's
                           default value will be used.

            Result:

                Boolean. Result value is True in case the attribute were
                successfully added to the object or False otherwise.
        """
        category = self.getCategory()
        if not category:
            return None

        if type(attr) is StringType:
            attr = category.getAttributeDefinition( attr )

        if attr is None:
            raise KeyError, 'Invalid category attribute specified'

        if not self.checkAttributePermissionModify(attr):
            return False

        return self._setCategoryAttribute( attr, value )

    def _setCategoryAttribute( self, attr, value=Missing, reindex=True ):
        """
            Set the value of the document category attribute
            without checking of permission for write access to attribute.
            Mainly is used from within action template SetCategoryAttribute

            Arguments:

                'attr' -- Either a CategoryAttribute class instance or an
                          attribute id string.

                'value' -- Attribute value. If no value given, attribute's
                           default value will be used.

            Result:

                Boolean. Result value is True in case the attribute were
                successfully added to the object or False otherwise.
        """
        if type(attr) is StringType:
            category = self.getCategory()
            if not category:
                raise KeyError, "Invalid category"
            attr = category.getAttributeDefinition( attr )
        if attr is None:
            raise KeyError, "Invalid category attribute specified"

        name = attr.getId()
        typ  = attr.Type()
        sheet = self._getCategorySheet()

        # TODO: move this shit to ValueTypes

        if attr.isMultiple():
            if value is Missing:
                pass
            elif value is None:
                value = []
            elif isSequence( value ):
                value = list( value )
            else:
                value = [ value ]

        if typ == 'link':
            # TODO support multivalued links
            if attr.isMultiple():
                raise NotImplementedError, "Multivalued links not implemented."
            if value is not Missing:
                value = updateLink( self, 'attribute', name, value )
            else:
                updateLink( self, 'attribute', name, None )

        elif typ == 'date' and value is None:
            # XXX workaround for manage_addProperty
            value = Missing

        handler = attr.getHandler()
        if hasattr(handler, 'convertValue'):
            value = handler.convertValue(attr, value, self)

        if value is Missing:
            # omitted value means default will be used
            if not sheet.hasProperty( name ):
                return False
            sheet._delProperty( name )

        elif sheet.hasProperty( name ):
            sheet._updateProperty( name, value  )

        else:
            if typ == 'lines':
                typ = attr.isMultiple() and 'lines' or 'string'
            sheet._setProperty( name, value, typ )

        if reindex and hasattr( aq_base(self), 'reindexObject' ):
            self.reindexObject( idxs=['CategoryAttributes'] )

        self._category_onChangeAttribute( name, value )

        return True

    def listCategoryAttributes( self, monikers=False, restricted=True ):
        """
            Lists the document category attributes.

            Result:

                List of the attribute definition, attribute value pairs.
        """
        result = []
        category = self.getCategory()
        if not category:
            return result
        for attr in category.listAttributeDefinitions():
            result.append( (attr, self.getCategoryAttribute( attr, moniker=monikers, restricted=restricted )) )
        return result

    def CategoryAttributes(self):
        """
            Indexing routine. Returns the document category attributes list.

            Result:

                Dictionary (attribute id -> attribute value).
        """
        r = {}

        category = self.getCategory()
        for attr in category.listAttributeDefinitions():
            type = attr.Type()
            handler = attr.getHandler().getId()
            # XXX definitely should have attr.isIndexable
            if type in ['link','object'] or handler in ['computed']:
                continue
            value = self._getCategoryAttribute( attr, None )
            # XXX should fix attributes index instead
            if type in ['lines','userlist'] and value is None:
                value = []
            r[ attr.getId() ] = value

        return r

    def checkAttributePermissionView( self, attr ):
        return self.checkAttributePermission( attr, Permissions.ViewAttributes )

    def checkAttributePermissionModify( self, attr ):
        return self.checkAttributePermission( attr, Permissions.ModifyAttributes )

    def checkAttributePermission(self, attr, perm):
        """
            Checks whether the user has given permission given on category
            attribute in current object state.

            Arguments:

                'attr' -- Either a CategoryAttribute class instance or an
                          attribute id string.

                'perm' -- Permission to test. Only two permissions have sense
                          here - 'View attributes' and 'Modify attributes'

            Note: This is not the 'real' Zope security check. There is no
                'acquired' roles for permissions while check.

            Result:

                Boolean. Result value is True in case the user has given
                permission on given category attribute or False otherwise.
        """
        #It should work as follows (numbers denotes the order of roles search):
        #
        #for each attribute in each state may be set:
        #   list of roles who can view attr and
        #   list of roles who can change attr in current state
        #1. If roles are set (changed) for attribute in the state:
        #   all users having one of listed roles can access to the attribute value.
        #
        #2. If roles are not yet set (changed) for attribute, try to acquire roles from state:
        #   for viewing - permission 'View',
        #   for editing - permission 'Modify portal content'
        #
        #3. If there is category inheritance and in the parent category there is
        #   same state and same attribute, try to do as 1,2 but in parent category
        #
        #4. And so forth.

        category = self.getCategory()

        if not category:
            return None

        if type(attr) is StringType:
            attr = category.getAttributeDefinition(attr)

        if attr is None:
            return None

        attribute_id = attr.getId()

        membership = getToolByName(self, 'portal_membership')
        user = membership.getAuthenticatedMember()
        user_roles = user.getRolesInContext(self)

        wftool = getToolByName( self, 'portal_workflow' )
        state  = wftool.getStateFor( self )
        if state is None:
            #Most likely - no default states in category settings.
            return 0

        bases = [category]
        bases.extend( category.listBases(recursive=True) )

        for category in bases:
            wf = category.__of__(self).getWorkflow()
            result = wf.getAttributePermissionInfo(state, attribute_id, perm)

            #first test roles that were explicitly set
            for u_role in user_roles:
                if u_role in result['roles']:
                    return 1

            if result['acquired']:
                #test parent's props
                sd = wf.states.get(state)
                if sd is None:
                    continue

                if wf.states.isPrivateItem( sd ):
                    #simply check permission
                    #...hm, is it correct?
                    return _checkPermission(perm, self)
        return 0

    security.declareProtected( CMFCorePermissions.View, 'getCategoryAttribute' )
    def getCategoryAttribute( self, attr, default=Missing, moniker=False, restricted=True ):
        """
            Returns the value of the document category attribute.

            Arguments:

                'attr' -- Either a CategoryAttribute class instance or an
                          attribute id string.

                'default' -- Default attribute value to be used in case it was
                             not found in the document.

            Exceptions:

                KeyError -- Raised if 'attr' argument is a string and specified
                            attribute was not found in the category definition.

            Result:

                Attribute value.
        """
        restricted = restricted is not Trust

        if type(attr) is StringType:
            try:
                attr = self.getCategory().getAttributeDefinition( attr )
            except KeyError:
                if default is Missing:
                    raise
                return default

        if restricted and not self.checkAttributePermissionView(attr):
            return attr.getDefaultValue()

        return self._getCategoryAttribute( attr, default, moniker=moniker )

    def _getCategoryAttribute( self, attr, default=Missing, moniker=False ):
        """
            Unrestricted getCategoryAttribute.
        """
        if type(attr) is StringType:
            try:
                attr = self.getCategory().getAttributeDefinition( attr )
            except KeyError:
                if default is Missing:
                    raise
                return default

        return attr.getValueFor( self, default, moniker=moniker )

    def deleteCategoryAttributes(self, attrs):
        """
            Deletes the specified attributes from the document.

            Arguments:

                'attrs' -- List of either a CategoryAttribute class instance or
                           an attribute id strings.

            Result:

                Boolean. Result value is True in case all attributes were
                successfully removed from the object or False otherwise.
        """
        sheet = self._getCategorySheet()
        names = [type(x) is StringType and x or x.getId() for x in attrs]
        try:
            sheet.manage_delProperties(names)
            return 1
        except:
            return None

    def hasBase(self, base=None):
        """
            Checks whether the document's category inherits or equal to the given category.

            Result:

                Boolean value if base is not None, otherwise returns the list of
                base categories ids including the current document's category.
        """
        return self.getCategory().hasBase( base )

    def _getCategorySheet(self):
        """
            Returns category propertysheet
            Adds new one if no sheet found
        """
        category_id = self.Category()
        sheet_id = 'category_metadata_%s' % category_id
        sheet = self.propertysheets.get(sheet_id)
        if sheet is None:
            self.propertysheets.manage_addPropertySheet(sheet_id, sheet_id)
            sheet = self.propertysheets.get(sheet_id)
        return sheet

    def _remote_transfer( self, context=None, container=None, server=None, path=None, id=None, parents=None, recursive=None ):
        """
        """
        workflow = None

        if self.implements( 'isCategorial' ):
            tptool = getToolByName( context, 'portal_types'    )
            mdtool = getToolByName( context, 'portal_metadata' )

            tinfo    = tptool.getTypeInfo( self )
            category = mdtool.getCategoryById( 'Publication' )
            workflow = category and category.Workflow()

            if not ( workflow and tinfo and category.isTypeAllowed( tinfo ) ):
                return None

            wftool = getToolByName( context, 'portal_workflow' )
            state  = wftool.getStateFor( self, wf_id=workflow )

            if state != 'published':
                self._remote_delete( context, container, server, path )
                return None

        remote = SyncableContent._remote_transfer( self, context, container, server, path, id, parents, recursive )

        if workflow and remote is not None:
            if not context.has( 'remote_workflow' ):
                context.remote_workflow = getToolByName( remote, 'portal_workflow', None )

            wfremote = context.remote_workflow
            if wfremote:
                state = wfremote.getStateFor( remote, wf_id=workflow )
                if state != 'published':
                    wfremote.doActionFor( remote, 'publish', comment='Automatically published' )

        return remote

    def _remote_delete( self, context=None, container=None, server=None, path=None, id=None ):
        """
        """
        if self.implements( 'isCategorial' ):
            tptool = getToolByName( context, 'portal_types'    )
            mdtool = getToolByName( context, 'portal_metadata' )

            tinfo    = tptool.getTypeInfo( self )
            category = mdtool.getCategoryById( 'Publication' )
            workflow = category and category.Workflow()

            if not ( workflow and tinfo and category.isTypeAllowed( tinfo ) ):
                return

            wftool = getToolByName( context, 'portal_workflow' )
            state  = wftool.getStateFor( self, wf_id=workflow )

            if not ( state == 'published' or \
                     wftool.getInfoFor( self, 'published', 0, wf_id=workflow ) ):
                return

        SyncableContent._remote_delete( self, context, container, server, path, id )


    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setPrimaryDocument' )
    def setPrimaryDocument( self, doc_uid, restricted=True ):
        """
            Sets primary document for this document.

            Arguments:

                'doc_uid' -- primary document's uid

                'restricted' -- verify current user's permission to set primary document
                                (ModifyAttributes)
        """
        restricted = restricted is not Trust
        links   = getToolByName( self, 'portal_links' )
        catalog = getToolByName( self, 'portal_catalog' )

        # remove old links to primary document(s)
        for link in links.searchLinks( source=self, relation='subordination' ):
            links.removeLink( link.getObject(), restricted=Trust )

        doc = catalog.getObjectByUid( doc_uid )
        if not doc:
            return

        # XXX should have restricted and unrestricted versions of this method
        if restricted and not _checkPermission( Permissions.ModifyAttributes, doc ):
            raise Exceptions.Unauthorized( "You are not permitted to establish subordination to the document." )

        my_category = self.getCategory().getPrimaryCategory()
        doc_category = doc.getCategory().getId()
        if my_category != doc_category:
            raise Exceptions.SimpleError \
                  ( "Category of the primary document does not match the specified primary category" )

        source = self.implements([ 'isVersionable', 'isVersion' ]) and self.getVersion() or self
        doc = doc.implements([ 'isVersionable', 'isVersion' ]) and doc.getVersion() or doc

        links.createLink( source, doc, 'subordination')

    security.declareProtected( CMFCorePermissions.View, 'getPrimaryDocument' )
    def getPrimaryDocument( self ):
        """
            Returns primary document uid.
        """

        links = getToolByName( self, 'portal_links' )

        source_ver_id = self.implements([ 'isVersionable', 'isVersion' ]) and self.getCurrentVersionId() or None
        res = links.searchLinks( source=self,
                                 source_ver_id=source_ver_id,
                                 relation='subordination' )

        if not res:
            return None
        assert len(res) == 1, "More than one primary document found."

        return res[0].getObject().getTargetObject()

    security.declareProtected( CMFCorePermissions.View, 'listSubordinateDocuments' )
    def listSubordinateDocuments( self, recursive=None,
                                  version_dependent=None, category_id=None, state_id=None ):
        """
            Returns list of subordinate documents' uids for this document.

            Arguments:

                'recursive'         --  if true, recurses through the
                                        subordination tree, which top is the
                                        current document; otherwise considers
                                        documents which are subordinate for
                                        current document only.

                'version_dependent' --  if true, considers documents which are
                                        subodinate for current version only;
                                        otherwise - subordinate documents for
                                        all versions of current document.

                'category_id'        --  category id of subordinate documents to filter

                'state_id'           --  state id of subordinate documents to filter

            Result:

                List of documents' uids.
        """
        uid = self.getUid()
        links_tool = getToolByName(self, 'portal_links')
        catalog_tool = getToolByName(self, 'portal_catalog')
        kw = { 'internal': 0
              ,'relation': 'subordination' 
              ,'target': version_dependent and self.implements([ 'isVersionable', 'isVersion' ]) and self.getVersion() or self
             }
  
        if not version_dependent:
            kw['target_inclusive'] = True

        docs = links_tool.searchLinks( **kw )
        if not docs:
            return []

        docs = [ str( x['source_uid'].base() ) for x in docs ]

        query = {'nd_uid': docs}

        # filtering for category
        if category_id:
            query['category'] = category_id

        # filtering for state
        if state_id:
            query['state'] = state_id

        docs = catalog_tool.searchResults( **query )
        docs = [ x['nd_uid'] for x in docs ]

        if recursive and docs:
            last = docs
            while 1:
                current = []

                for doc_uid in last:
                    doc = catalog_tool.getObjectByUid( doc_uid )
                    if doc:
                        current.extend( doc.listSubordinateDocuments( version_dependent=version_dependent ) )

                if not current:
                    break

                docs.extend( current )
                last = current

        return docs

    # callback function, is called from within ContentCategory,
    # from method setCategoryAttribute
    def _category_onChangeAttribute( self, name, value ):
        md_tool = getToolByName(self, 'portal_metadata')
        cat_id = self.getCategory().getPrimaryCategory()
        primary_category = cat_id and md_tool.getCategoryById(cat_id)
        # checking for 'Normative' nature
        if self.getCategory().hasBase( 'NormativeDocument' ) or primary_category and primary_category.hasBase( 'NormativeDocument' ):
            # perform on-change attribute logic
            if name=='OriginalHolder':
                if value:
                    value = list(tuplify(value))
                    version_owners = self.getVersion().getVersionOwners()
                    version_creator = str(self.getVersion().getOwner())
                    self.getVersion().addLocalRoleVersionOwner( value )
                    # remove old copy_holder
                    arr = [version_creator] + value
                    remove_user_id = []
                    for user_id in version_owners:
                        if user_id not in arr:
                            remove_user_id.append(user_id)
                    if remove_user_id:
                        self.getVersion().delLocalRoleVersionOwner( remove_user_id )


InitializeClass( ContentCategory )
