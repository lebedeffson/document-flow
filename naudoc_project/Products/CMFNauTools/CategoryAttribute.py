"""
CategoryAttribute class.

$Editor: vpastukhov $
$Id: CategoryAttribute.py,v 1.32 2007/10/10 10:56:16 oevsegneev Exp $
"""
__version__ = '$Revision: 1.32 $'[11:-2]

from types import StringType

from AccessControl import ClassSecurityInfo
from Globals import HTMLFile

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser

import Exceptions
from Features import createFeature
from Monikers import MonikerBase
from Script import DefaultScriptNamespace
from SimpleObjects import ContainerBase, InstanceBase
from Utils import getObjectImplements, InitializeClass, isSequence, readLink, updateLink
from ValueTypes import getValueHandler, DerivedValueBase


_field_template_infos   = {}
_field_template_methods = {}

def registerFieldTemplate( name, method, **info ):
    global _field_template_infos, _field_template_methods
    if _field_template_infos.has_key( name ) or \
       _field_template_methods.has_key( name ):
        raise ValueError, name
    _field_template_methods[name] = method
    _field_template_infos[name] = info


class CategoryAttribute( InstanceBase ):
    """
        Category attribute descriptor.
    """
    _class_version = 1.40

    meta_type = 'Category Attribute'

    __implements__ = createFeature('isCategoryAttribute'), \
                     InstanceBase.__implements__

    security = ClassSecurityInfo()

    _properties = InstanceBase._properties + (
            { 'id':'multiple', 'type':'boolean', 'mode':'' },
            { 'id':'mandatory', 'type':'boolean', 'mode':'w' },
            { 'id':'read_only', 'type':'boolean', 'mode':'w' },
        )

    # default attribute values
    defvalue  = None
    multiple  = False
    mandatory = False
    read_only = False

    def __init__( self, id, title, type, multiple=Missing,
                  mandatory=Missing, read_only=Missing ):
        # instance constructor
        InstanceBase.__init__( self, id, title )

        # NB whenever self.handler is changed properties must be reset
        self.handler = type
        handler = self.getHandler()

        if handler.isDerived():
            type = None

        self.name = id
        self.type = type

        if multiple  is not Missing: self.multiple  = multiple
        if mandatory is not Missing: self.mandatory = mandatory
        if read_only is not Missing: self.read_only = read_only

        if self.multiple:
            self.defvalue = []

        elif self.type in ['string','text']:
            self.defvalue = ''

    def _initstate( self, mode ):
        # initialize attributes
        if not InstanceBase._initstate( self, mode ):
            return False

        if hasattr( self, 'typ' ): # < 1.34
            self.type = self.typ
            del self.typ
            if self.type == 'userlist':
                self.multiple = True

        if hasattr( self, '_mandatory' ): # < 1.34
            self.mandatory = self._mandatory
            del self._mandatory
        if hasattr( self, 'obligatory' ): # < 1.34
            self.mandatory = self.obligatory
            del self.obligatory

        if hasattr( self, '_isSubordinate' ): # < 1.37
            self.handler = 'subordinate'
            del self._isSubordinate

        if mode and not hasattr( self, 'handler' ): # < 1.37
            self.handler = self.type

        if mode and self.handler == 'lines' and not hasattr( self, 'options' ): # < 1.38
            self._updateProperty( 'options', self.defvalue or [] )
            if self.multiple:
                self.defvalue = []
            else:
                self.defvalue = None

        return True

    def _instance_onCreate( self ):
        self.getHandler().notifyPropertiesChanged( self )

        # fill attributes index only by request
        #self.registerAttribute()

    def _instance_onDestroy( self ):
        self.unregisterAttribute()

    def registerAttribute(self):
        category = self.getCategory()
        index = self.getAttributesIndex()
 
        # TODO as id use ResourceUid
        index.registerAttribute( "%s/%s" % ( category.getId(), self.getId() )
                               , self.Type() )

    def unregisterAttribute(self):
        category = self.getCategory()
        index = self.getAttributesIndex()

        # TODO as id use ResourceUid
        index.unregisterAttribute( "%s/%s" % ( category.getId(), self.getId() ) )

    security.declarePublic( 'getId' )
    def getId( self ):
        """
            Returns an attribute id.

            Result:

                String.
        """
        return self.name

    security.declarePublic( 'Type' )
    def Type( self ):
        """
            Returns an attribute type.

            Type value is allowed to be either a 'string', 'boolean', 'date',
            'text' or 'lines'.

            Result:

                String.
        """
        return self.type

    security.declarePublic( 'isMultiple' )
    def isMultiple( self ):
        """
            Checks whether the attribute is multi-valued.

            Result:

                Boolean.
        """
        return self.multiple

    security.declarePublic( 'isMandatory' )
    def isMandatory( self ):
        """
            Checks whether an attribute is mandatory.

            User must specify all values of mandatory attributes before submitting
            the form.

            Result:

                Boolean.
        """
        return self.mandatory

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setMandatory' )
    def setMandatory( self, mandatory=True ):
        """
            Marks an attribute as mandatory.

            Arguments:

                'mandatory' -- Boolean.
        """
        self.mandatory = mandatory

    security.declarePublic( 'isReadOnly' )
    def isReadOnly( self ):
        """
            Checks whether an attribute is read only.

            Result:

                Boolean.
        """
        return self.read_only or self.getHandler().isReadOnly()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setReadOnly' )
    def setReadOnly( self, read_only=True ):
        """
            Marks an attribute as read only.

            Arguments:

                'read_only' -- Boolean.
        """
        if self.getHandler().isReadOnly() and not read_only:
            # if attribute is inherited from primary category it should always be read only
            raise Exceptions.SimpleError( "Cannot make subordinate attribute writable." )
        self.read_only = read_only

    security.declarePublic( 'isDerived' )
    def isDerived( self ):
        """
            Checks whether the attribute's value is derived from external source.

            Result:

                Boolean.
        """
        return self.getHandler().isDerived()

    security.declarePublic( 'isSubordinate' )
    def isSubordinate( self ):
        """
            Checks whether the attribute is inherited from primary category.

            Result:

                Boolean.
        """
        return self.getHandlerId() == 'subordinate'

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setSubordinate' )
    def setSubordinate( self, subordinate=True, primary=Missing ):
        """
            Marks the attribute as subordinate. This means it was inherited from primary category and is _always_ read only.

            Arguments:

                'subordinate' -- Boolean.
        """
        handler = self.getHandler()

        if subordinate:
            htype = (primary is Missing) and 'subordinate' or 'derived'

            if htype != handler.getId():
                # cleanup links that may exist
                handler.notifyTypeChange( self, htype )
                # use new handler from here
                handler = getValueHandler( htype )
                self.handler = htype

            if primary is not Missing:
                handler.setPrimary( self, primary )

            self.setDefaultValue( None )
            self.setReadOnly()

        elif handler.isDerived():
            handler.notifyTypeChange( self, self.type )

            self.handler = self.type
            self.setReadOnly( False )

    security.declarePublic('isInCategory')
    def isInCategory( self, category, recursive=False ):
        """
            Checks whether an attribute belongs to a given category.

            Arguments:

                'category' -- CategoryDefinition instance.

                'recursive' -- Boolean. Check base categories recursively.

            Result:

                Boolean.
        """
        attr_category = self.parent().parent()

        if recursive:
            return category.hasBase(attr_category)

        return attr_category == category

    security.declareProtected( CMFCorePermissions.View, 'isEmpty' )
    def isEmpty( self, value=Missing ):
        """
            Checks whether the attribute value is empty.

            Arguments:

                'value' -- a value to check; if omitted, default value
                           of this attribute is checked

            Result:

                Boolean.
        """
        if value is Missing:
            value = self.getDefaultValue()

        if isSequence( value ):
            assert self.multiple, "list value passed to a non-list attribute"
            return not len( value )

        if type(value) is StringType:
            return not len( value.strip() )

        return value is None

    security.declarePrivate('getAttributesIndex')
    def getAttributesIndex( self):
        catalog = getToolByName( self, 'portal_catalog' )
        return catalog._catalog.getIndex( catalog._catalog_attr_key )

    security.declarePrivate('getCategory')
    def getCategory(self):
        return self.parent().parent()

    security.declarePublic( 'getDefaultValue' )
    def getDefaultValue( self, moniker=False ):
        """
            Returns an attribute default value.

            Result:

                Depends on the attribute type.
        """
        if self.isDerived():
            return self.getHandler().getDefaultValue( self, moniker=moniker )

        value = self.defvalue

        if self.type == 'link' and value is not None:
            value = readLink( self, 'property', 'default', value, moniker=moniker )

        return value

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setDefaultValue' )
    def setDefaultValue( self, value ):
        """
            Sets default attribute value.

            Arguments:

                'value' -- new default value for the attribute;
                           use 'None' to clear the old value
        """
        if self.multiple:
            if isSequence( value ):
                value = list( value )
            elif value is not None:
                value = [ value ]
            else:
                value = []
        else:
            assert not isSequence(value), "list value passed to a single-value attribute"
            if self.type == 'link':
                value = updateLink( self, 'property', 'default', value )

        self.defvalue = value

    security.declarePrivate( 'getValueFor' )
    def getValueFor( self, object, default=Missing, moniker=False ):
        """
        """
        assert object.implements('isCategorial')
        assert self.isInCategory(object.getCategory(), recursive = True)

        if self.isDerived():
            return self.getHandler().getDerivedValue( self, object, default, moniker=moniker )

        if default is Missing:
            default = self.getDefaultValue( moniker=moniker )

        sheet = object._getCategorySheet()
        value = sheet.getProperty( self.getId(), default )

        if self.Type() == 'link' and value is not None:
            if value is default:
                return default
            value = readLink( object, 'attribute', self.getId(), Missing, moniker=moniker )

        elif self.isMultiple() and not isSequence(value):
            value = (value is not None) and [value] or []

        return value

    def getViewFor(self, object, template_type='view'):
        """
            Returns HTML code piece for the given object and type.

            Arguments:

                'object' -- object, where attribute value located.

                'template_type' -- type of the template. Currently, there
                                   are two types: 'view' and 'edit'.

            Result:

                String with HTML code.
        """
        try:
            info   = _field_template_infos[template_type]
            method = _field_template_methods[template_type]
        except KeyError:
            raise ValueError( "'%s' -- unknown template type" % template_type )
        return getattr(self, method )(
                  object, None,
                  value = self.getValueFor(object, moniker=True),
                  **self.getFieldDescriptor( **info )
               )

    def _propertyMap( self ):
        # returns combined list of basic and type-specific properties
        return InstanceBase._propertyMap( self ) + self.getHandler()._propertyMap()

    def manage_changeProperties( self, REQUEST=None, **kwargs ):
        """
            Changes existing object properties.
        """
        previous = self.getProperties()
        result = InstanceBase.manage_changeProperties( self, REQUEST, **kwargs )
        self.getHandler().notifyPropertiesChanged( self, previous )
        return result

    security.declareProtected( CMFCorePermissions.View, 'getFieldDescriptor' )
    def getFieldDescriptor( self, view=True, modify=True, edit=False, **kwargs ):
        """
            Returns UI field descriptor corresponding to this attribute,
            for use in 'entry_field' templates.

            Result:

                Mapping object.
        """
        modify = modify and (not self.isReadOnly() or edit)
        desc = {
                'id'          : self.getId(),
                'name'        : self.getId(),
                'type'        : self.Type(),
                'multiple'    : self.isMultiple(),
                'mandatory'   : self.isMandatory() and not edit,
                'options'     : self.getProperty('options',[]),
                'properties'  : self.getProperties( uids=True ),
                'field_title' : self.Title(),
                'message'     : '',
                'comment'     : '',
                'view'        : view,
                'modify'      : view and modify,
                'external'    : False,
            }
        desc.update( kwargs )
        return desc

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getHandlerId' )
    def getHandlerId( self ):
        """
        """
        return self.handler

    security.declarePrivate( 'getHandler' )
    def getHandler( self ):
        """
        """
        return getValueHandler( self.handler )

    security.declareProtected( CMFCorePermissions.View, 'hasDerived' )
    def hasDerived( self ):
        """
        """
        return self.getHandler().hasDerived( self )

    security.declareProtected( CMFCorePermissions.View, 'listDerived' )
    def listDerived( self ):
        """
        """
        return self.getHandler().listDerived( self )

InitializeClass( CategoryAttribute )


class CategoryAttributesContainer( ContainerBase ):
    """
        Contains category attribute definitions
        ('CategoryAttribute' instances)
    """
    _class_version = 1.3

    meta_type = 'Category Attributes Container'

    all_meta_types = [
            { 'name'   : CategoryAttribute.meta_type,
              'action' : ContainerBase.manage_options[0]['action'] },
        ]

    # why _containment_onDelete?
    def _containment_onDelete( self, item, container ):
        ids = []
        for adef in self.listAttributeDefinitions():
            if adef.isDerived():
                ids.append( adef.getId() )
        if ids:
            self.deleteAttributeDefinitions( ids )


InitializeClass( CategoryAttributesContainer )


class DerivedAttribute( DerivedValueBase ):
    """
        Attribute of the object designated by the named link attribute.
    """

    _template = 'attr_construction_derived'

    _properties = (
            {'id':'primary_attr', 'type':'link', 'feature':'isCategoryAttribute', 'mode':'w', 'title':"Primary attribute"},
            {'id':'derived_attr', 'type':'link', 'mode':'w', 'title':"Value of the derived attribute"},
        )

    def getPrimary( self, attr ):
        return attr.getProperty('primary_attr')

    def setPrimary( self, attr, primary ):
        assert primary.implements('isCategoryAttribute') # TODO allow Uid too
        assert primary.Type() == 'link'

        previous = self.getProperty('primary_attr')
        attr._updateProperty( 'primary_attr', primary )
        self.notifyPropertiesChanged( attr, {'primary_attr':previous} )

    def getDefaultValue( self, attr=Missing, moniker=False ):
        # use None for unspecified attribute
        if attr is Missing:
            return self._default
        # all work done by getDerivedValue below with object=Missing
        return self.getDerivedValue( attr, Missing, moniker=moniker )

    def getDerivedValue( self, attr, object, default=Missing, moniker=False ):
        # get attribute referenced by the primary link
        primary = self.getPrimary( attr )
        uid = attr.getProperty( 'derived_attr', uid=True )
        if not ( primary and uid ):
            if default is not Missing:
                return default
            return
      
        if object is Missing:
            # special case -- invoked by getDefaultValue above
            value = primary.getDefaultValue()
        else:
            value = primary.getValueFor( object, None )

        if value is None or uid is None:
            if default is not Missing:
                return default
            # primary link is empty -- return type's default value
            return DerivedValueBase.getDefaultValue( self, attr, real=True, moniker=moniker )

        provider = self._getProvider( attr )
        if provider is not None:
            # value belongs to the realm having its own attributes -- ask it for the value
            return provider.getAttributeValueFor( value, uid, default, moniker=moniker )

        # derived value is a category attribute of the value
        category = uid.uid
        subid = uid.attribute

        if not value.implements('isCategorial') or \
           not value.hasBase( category ):
            if default is not Missing:
                return default
            # value is not of the required categry -- return type's default value
            return DerivedValueBase.getDefaultValue( self, attr, real=True, moniker=moniker )

        return value.getCategoryAttribute( subid, default, moniker=moniker, restricted=Trust )

    def notifyPropertiesChanged( self, attr, previous=None ):
        DerivedValueBase.notifyPropertiesChanged( self, attr, previous )

        provider = self._getProvider( attr )
        if provider is None:
            derived = attr.getProperty( 'derived_attr' )
            if derived is not None:
                attr.type = derived.Type()
                attr.multiple = derived.isMultiple()

        else:
            uid = attr.getProperty( 'derived_attr', uid=True )
            # TODO provider.getAttributeDefinition( uid )
            for adef in provider.listAttributeDefinitions():
                if adef['uid'] == uid:
                    attr.type = adef['type']
                    attr.multiple = adef.get('multiple',False)
                    break

    def _getProvider( self, attr ):
        attr = self.getPrimary( attr )

        while attr and attr.hasDerived():
            if attr.Type() == 'link':
                break
            attr = attr.getHandler().getPrimary( attr )
        else:
            return None

        scope = attr.getProperty('scope')
        if scope is None or not scope.implements('isAttributesProvider'):
            return None

        return scope

class ComputedAttribute( DerivedValueBase ):
    """
        Attribute of the object computed by the linked script.
    """

    _template = 'attr_construction_computed'

    _properties = (
            {'id':'script_object', 'type':'link', 'feature':'isScript', 'mode':'w', 'title':"Script"},
        )

    def getDefaultValue( self, attr=Missing, moniker=False ):
        # use None for unspecified attribute
        if attr is Missing:
            return self._default
        # all work done by getDerivedValue below with object=Missing
        return self.getDerivedValue( attr, Missing, moniker=moniker )

    def getDerivedValue( self, attr, object, default=Missing, moniker=False ):
        # get script destined to compute the value
        script = attr.getProperty('script_object')

        if script is None:
            if default is not Missing:
                return default
            # no script defined -- return default value of the real type
            return DerivedValueBase.getDefaultValue( self, attr, real=True, moniker=moniker )

        # prepare script namespace
        user = _getAuthenticatedUser( attr ).getId()
        portal = getToolByName( attr, 'portal_url' ).getPortalObject()
        namespace = CategoryAttributeNamespace( object, user, portal, attr )

        # and finally run the script
        return script.evaluate( namespace )

    def notifyPropertiesChanged( self, attr, previous=None ):
        DerivedValueBase.notifyPropertiesChanged( self, attr, previous )

        script = attr.getProperty('script_object')
        if script is not None:
            if script.getNamespaceFactoryType() != CategoryAttributeNamespace.namespace_type:
                raise Exceptions.SimpleError( "The script %(script)s must use category attribute namespace.", script=script )
            attr.type = script.getResultType()
        else:
            attr.type = 'unknown_value'

        # TODO add support for multivalued computed attrs
        attr.multiple = False


class CategoryAttributeNamespace( DefaultScriptNamespace ):
    """
        Namespace for the computed attribute script.
    """
    namespace_type = 'category_attribute'

    def __init__( self, object, user, portal, attribute ):
        DefaultScriptNamespace.__init__( self, object, user, portal )
        self.attribute = attribute

class AttributeMoniker( MonikerBase ):
    """
        Moniker for attribute definition.
    """
    _types = ('category',)
    _template = HTMLFile( 'skins/monikers/state_moniker', globals() )
    _mandatory_args = MonikerBase._mandatory_args[:-1] + (('moniker_frame', 'workspace' ),)

    def __init__( self, object, md=None, **kwargs ):
        """
            Associates new moniker with the target object.

            Arguments:

                'object' -- the object or its identifier (string)

                'md' -- optional DTML dictionary, used to load
                        the object by identifier

                '**kwargs' -- additional keyword arguments to pass
                              to DTML template
        """
        if getObjectImplements( object, 'isCategoryAttribute'):
            pass
        else:
            raise TypeError(object)

        # set right default url for state
        category = object.parent().parent()
        kwargs['url'] = category.relative_url( action='category_attr_edit',
                                               params={'id':object.getId()} )

        MonikerBase.__init__(self, object, md=md, **kwargs)

    def _moniker_render( self, md=None, **kwargs ):
        return self._render( self._template, md, **kwargs )


def initialize( context ):
    # module initialization callback
    context.register( registerFieldTemplate )
    context.registerFieldTemplate( 'view',          'entry_field_view', view=True, modify=False )
    context.registerFieldTemplate( 'edit',          'entry_field_edit', view=True, modify=True )
    context.registerFieldTemplate( 'external_view', 'entry_field_view', view=True, modify=False, external=True )

    context.registerValueType( DerivedAttribute, 'derived' )
    context.registerValueType( ComputedAttribute, 'computed' )
    context.registerNamespace( CategoryAttributeNamespace )

    context.registerMoniker( AttributeMoniker, 'attribute' )
    context.registerVarFormat( 'attribute', lambda v, n, md: AttributeMoniker(v).render(md) )
