"""
Data types registry and handlers of basic types.

$Editor: vpastukhov $
$Id: ValueTypes.py,v 1.17 2006/05/11 13:52:29 adolgushin Exp $
"""
__version__ = '$Revision: 1.17 $'[11:-2]

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName

from Features import createFeature
from ResourceUid import ResourceUid
from SimpleObjects import ItemBase
from Utils import InitializeClass, joinpath, uniqueValues


def registerValueType( klass, *ids ):
    global _value_types
    for id in ids:
        if _value_types.has_key( id ):
            raise ValueError, id
        _value_types[ id ] = klass( id )

def getValueHandler( id ):
    if not id:
        id = 'unknown_value'
    global _value_types
    return _value_types[ id ]

def listValueHandlers():
    global _value_types
    return _value_types.values()

_value_types = {}


class SimpleValue:

    __allow_access_to_unprotected_subobjects__ = 1

    _default = None
    _template = None
    _properties = ()

    def __init__( self, id ):
        self.id = id

    def getId( self ):
        return self.id

    def getDefaultValue( self, attr=Missing, moniker=False ):
        if attr is not Missing and attr.isMultiple():
            return []
        return self._default

    def getTemplate( self, type ):
        return self._template

    def isEmpty( self, value ):
        return value is None

    def isInternal( self ):
        return False

    def isDerived( self ):
        return False

    def getPrimary( self, attr ):
        return None

    def setPrimary( self, attr, primary ):
        raise TypeError

    def getDerivedValue( self, attr, object, default=Missing, moniker=False ):
        """
            Returns value of the derived attribute for the given object.
        """
        raise TypeError

    def hasDerived( self, attr ):
        return False

    def listDerived( self, attr ):
        return []

    def notifyPropertiesChanged( self, attr, previous=None ):
        pass

    def notifyTypeChange( self, attr, new ):
        for prop in self._propertyMap():
            try: attr._delProperty( prop['id'] )
            except (KeyError, AttributeError, ValueError): pass

    def _propertyMap( self ):
        return tuple( self._properties )

    def __cmp__( self, other ):
        return cmp( self.id, other.id )

    def isReadOnly(self):
        return self.isDerived()

class UnknownValue( SimpleValue ):

    def isInternal( self ):
        return True

class StringValue( SimpleValue ):

    _template = 'attr_construction_string'

    _properties = (
            { 'id':'input_length', 'type':'int', 'default':65, 'mode':'w', 'title':"Input field length in characters" },
        )

class DateValue( SimpleValue ):

    _template = 'attr_construction_date'

    _properties = (
            { 'id':'show_time', 'type':'boolean', 'default':False, 'mode':'w', 'title':"Show time" },
        )

class TextValue( SimpleValue ):

    _template = 'attr_construction_text'

    _properties = (
            { 'id':'input_columns', 'type':'int', 'default':65, 'mode':'w', 'title':"Input field width in characters" },
            { 'id':'input_rows', 'type':'int', 'default':6, 'mode':'w', 'title':"Input field height in lines" },
        )

class TimePeriodValue( SimpleValue ):

    _default = 86400


class LinesValue( SimpleValue ):

    _template = 'attr_construction_lines'

    _properties = (
            { 'id':'options', 'type':'lines', 'mode':'w', 'title':"List of possible values" },
            { 'id':'input_rows', 'type':'int', 'default':6, 'mode':'w', 'title':"Number of rows in selection box" },
        )


class LinkValue( SimpleValue ):

    _template = 'attr_construction_link'

    _properties = (
            { 'id':'scope', 'type':'link', 'feature':'isItemsRealm', 'mode':'w', 'title':"Objects selection realm" },
            { 'id':'allowed_types', 'type':'list', 'mode':'w', 'title':"Allowed content types" },
            { 'id':'allowed_categories', 'type':'list', 'mode':'w', 'title':"Allowed categories" },
        )

    def hasDerived( self, attr ):
        return True

    def listDerived( self, attr ):
        scope = attr.getProperty('scope')
        if scope is None:
            scope = getToolByName( attr, 'portal_metadata' )

        if not scope.implements('isAttributesProvider'):
            return scope.listAttributeDefinitions()

        return scope.listAttributeDefinitions(
                    types=(attr.getProperty('allowed_types') or None),
                    categories=(attr.getProperty('allowed_categories') or None) )

    def notifyPropertiesChanged( self, attr, previous=None ):
        SimpleValue.notifyPropertiesChanged( self, attr, previous )

        id = attr.getId()
        category = attr.parent().parent()

        realm = previous and previous.get('scope')
        if not realm or realm == attr.getProperty('scope'):
            return

        catalog = getToolByName( attr, 'portal_catalog' )
        results = catalog.searchResults( category=category.getId(),
                                         implements='isCategorial',
                                         restricted=Trust )
        for item in results:
            item.getObject().setCategoryAttribute( id )


class ObjectValue( SimpleValue ):

    _properties = (
            { 'id':'object_type', 'type':'string', 'title':"Object type" },
        )

    def isInternal( self ):
        return True

    def hasDerived( self, attr ):
        return True

    def listDerived( self, attr ):
        if attr.getProperty('object_type'):
            raise NotImplementedError # TODO

        scope = self._getScope( attr )
        if scope is None:
            return []

        return scope.listAttributeDefinitions( attr.getId() )

    def _getScope( self, attr ):
        # traverse primary values in search for link attribute
        while attr and attr.hasDerived():
            if attr.Type() == 'link':
                break
            attr = attr.getHandler().getPrimary( attr )
        else:
            return None

        # extract scope from the link
        scope = attr.getProperty('scope')
        if scope is None or not scope.implements('isAttributesProvider'):
            return None

        return scope


class DerivedValueBase( SimpleValue ):

    def isDerived( self ):
        return True

    def hasDerived( self, attr ):
        return getValueHandler( attr.Type() ).hasDerived( attr )

    def listDerived( self, attr ):
        return getValueHandler( attr.Type() ).listDerived( attr )

    def getDefaultValue( self, attr=Missing, moniker=False, real=False ):
        """
            Return default value of the real type
        """
        if real and attr is not Missing:
            if not attr.Type():
                raise KeyError, attr.getId()
            return getValueHandler( attr.Type() ).getDefaultValue( attr, moniker=moniker )
        return SimpleValue.getDefaultValue( self, attr, moniker=moniker )


class MembersSelection:
    """
        Container type of member source uids.

        Can return source uids with *getSelection* method or
        members with *listMembers*.
    """

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, uids):
        self._uids = uids

    def listMembers(self, context):
        resolve = getToolByName(context, 'portal_membership').resolveSource
        result = []

        for uid in self._uids:
            object = uid.deref(context)
            result.extend( resolve(uid.type, context, object) )

        return uniqueValues(result)

    def getSelection(self, context):
        sources = getToolByName(context, 'portal_membership').listSourceIds()
        result = {}

        for uid in self._uids:
            if uid.type not in sources:
                raise ValueError('Invalid type of user source: \'%s\'' % uid.type)

            result.setdefault(uid.type, []).append(uid)

        return result

class AdvancedUsersValue(SimpleValue):

    _template = 'attr_construction_advanced_userlist'
    _properties = (
            { 'id':'store_members', 'type':'boolean', 'title':"Store members" },
        )

    def isDerived(self):
        return True

    def isReadOnly(self):
        return False

    def notifyPropertiesChanged(self, attr, previous = None):
        SimpleValue.notifyPropertiesChanged(self, attr, previous)

        # XXX
        if attr.type is None:
            attr.type = attr.handler

    def convertValue(self, attr, value, context):
        """
            Returns value converted for storage.

            Value could be list of ResourceUid's or MembersSelection object.
        """
        selection_value = value and isinstance(value[0], MembersSelection) or False
        if selection_value:
            # XXX setCategoryAttribute always wraps value in list because
            #     this type is multiple
            value = value[0]

        if attr.getProperty('store_members'):
            if not selection_value:
                value = MembersSelection(value)

            return map(ResourceUid, value.listMembers(context))

        if selection_value:
            return value._uids

        return value

    def getDefaultValue(self, attr, moniker = False, real = False):
        uids = attr.defvalue

        if uids is not None:
            return MembersSelection(uids)

    def getDerivedValue(self, attr, object, default = Missing, moniker = False):
        sheet = object._getCategorySheet()
        uids = sheet.getProperty(attr.getId(), None)

        if uids is not None:
            return MembersSelection(uids)

def initialize( context ):
    # module initialization callback

    context.register( registerValueType )

    context.registerValueType( SimpleValue, 'boolean', 'userlist',
                                            'int', 'float', 'currency',
                                            'splitter' )

    context.registerValueType( AdvancedUsersValue, 'advanced_userlist' )

    context.registerValueType( StringValue, 'string' )

    context.registerValueType( DateValue, 'date')

    context.registerValueType( TextValue, 'text' )

    context.registerValueType( TimePeriodValue, 'time_period')

    context.registerValueType( LinesValue, 'lines' )

    context.registerValueType( LinkValue, 'link' )

    context.registerValueType( ObjectValue, 'object' )

    context.registerValueType( UnknownValue, 'unknown_value' )
