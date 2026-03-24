"""
Unique object identifier class.

Each object class may define the following attributes which are
related to the resource uid system:

    '__resource_type__' -- the resource type Id of the object

    '__resource_subkeys__' -- list of

$Editor: vpastukhov $
$Id: ResourceUid.py,v 1.22 2006/03/06 16:15:45 ypetrov Exp $
"""
__version__ = '$Revision: 1.22 $'[11:-2]

from types import StringType, DictType

from AccessControl import ClassSecurityInfo
from Acquisition import aq_get
from DocumentTemplate.DT_Util import TemplateDict
from Products.CMFCore.utils import getToolByName

import Utils
from DTMLTags import MsgDict
from Utils import InitializeClass, getObjectByUid


class ResourceUid:
    """
        NB. This class cannot have '__call__' method because its instances
        are stored in the ZCatalog metadata.  ZCatalog always invokes '__call__'
        during metadata updates.
    """

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess( 1 )

    def __init__( self, object, type=None, service=None, context=None ):
        """
        """
        info = None
        if context is None:
            context = object

        #if service is None:
        #    service = aq_get( object, '__service__', None, 1 )

        if object is None or isinstance( object, DictType ):
            info = object

        elif isinstance( object, StringType ):
            try:
                info = self.parse( object, type=type )
            except ValueError:
                raise TypeError, object

        elif isinstance( object, ResourceUid ):
            info = object.__dict__

        elif service is None:
            if type is None:
                type = aq_get( object, '__resource_type__', Missing, 1 )
                if type is Missing:
                    raise TypeError, object

            identify = _resource_types[ type ].identify.im_func
            portal = getToolByName( context, 'portal_url' ).getPortalObject()
            info = apply( identify, (portal, object) )

        else:
            # external object
            connector = getToolByName( context, 'portal_connector' )
            info = connector.getService( service ).getResourceUid( object )

        dict = self.__dict__
        if isinstance( info, StringType ):
            dict['uid'] = info
        elif info:
            dict.update( info )

        type = dict.setdefault( 'type', type )
        dict.setdefault( 'service', service )

        for key in _resource_types[ type ].keys:
            dict.setdefault( key, None )

    def deref( self, context, **kwargs ):
        """
        """
        if isinstance( context, TemplateDict ):
            context = MsgDict( context )

        if self.service is not None:
            # external object
            connector = getToolByName( context, 'portal_connector' )
            return connector.getService( self.service ).getObjectByUid( self )

        portal = getToolByName( context, 'portal_url' ).getPortalObject()
        lookup = _resource_types[ self.type ].lookup.im_func

        info = self.__dict__.copy()
        info.update( kwargs )

        return apply( lookup, (portal,), info )

    def moniker( self, context=Missing ):
        if context is Missing:
            return Moniker( self )
        return Moniker( self ).__of__( context )

    def get( self, name, default=None ):
        return getattr( self, name, default )

    def dict( self ):
        return vars( self )

    def copy( self ):
        return self.__class__( self )

    def update( self, other ):
        """
            Copies UID keys from another one.
        """
        if not isinstance( other, ResourceUid ) or other.type != self.type:
            raise TypeError, other
        self.__dict__.update( other.dict() )

    def base( self ):
        """
            Returns UID of the base resource.
        """
        info = {}
        set  = info.setdefault
        get  = self.__dict__.get

        #keys = _resource_types[ self.type ].keys
        #for key in keys:

        for key in _mandatory_keys:
            set( key, get( key ) )

        return self.__class__( info )

    def __delattr__( self, key ):
        if not hasattr( self, key ):
            return
        if key in _resource_types[ self.type ].keys:
            raise ValueError, key
        del self.__dict__[ key ]

    def __eq__( self, other ):
        """
            Compares to another UID or object for equality.

            The UIDs are considered to be equal if both have
            the same set and values of the keys.
        """
        if not isinstance( other, ResourceUid ):
            try: other = ResourceUid( other )
            except TypeError: return False

        return self.__dict__ == other.dict()

    def __ne__( self, other ):
        return not self.__eq__( other )

    def __le__( self, other ):
        """
            Compares to another UID or object for precedence.

            The UID is considered to be less than another one
            if it has a narrower set of keys and values of the
            common keys match.
        """
        if not isinstance( other, ResourceUid ):
            try: other = ResourceUid( other )
            except TypeError: return False

        items = self.__dict__.items
        get = other.__dict__.get

        for k,v in items():
            if get(k) != v:
                return False

        return True

    def __nonzero__( self ):
        return not not (self.type or self.uid)

    def __str__( self ):
        """
            Returns string representation that can be parsed back later.
        """
        type = self.type
        desc = _resource_types[ type ]
        keys = desc.keys
        info = self.__dict__

        # default UID type without extra keys is represented as a simple string
        if desc.default and len(info) == len(keys) \
                        and len( filter(None, info.values()) ) <= 2:
            return str( self.uid )

        get = info.get
        parts = []

        # arrange mandatory keys sequentially
        for key in keys:
            value = get( key )
            parts.append( value is not None and str(value) or '' )

        # append additional keys as name=value pairs
        for key, value in info.items():
            if key not in keys:
                parts.append( '%s=%s' % (value is None and (key,'') or (key,value)) )

        # if type ID is empty it is default type
        if not parts[0]:
            parts[0] = _default_type

        return ':'.join( parts )

    def __hash__(self):
        return hash( str(self) )

    def parse( self, source, type=None ):
        """
            Parses string representation of the UID into mapping.
        """
        # UID of default type contains no delimiters
        if ':' not in source:
            if type is None:
                type = source.startswith('/') and _path_type or _default_type
            return { 'type':type, 'uid':source, 'service':None }

        info  = {}
        set   = info.setdefault
        parts = source.split(':')

        if type is None:
            type = parts[0]

        try:
            handler = getResourceHandler( type )
        except KeyError:
            raise ValueError, type

        # mandatory keys are arranged sequentially
        for key in handler.keys:
            value = parts.pop(0)
            if '=' in value:
                raise ValueError, value
            set( key, value or None )

        # additional keys follow as name=value pairs
        for part in parts:
            set( *part.split( '=', 1 ) )

        return info

InitializeClass( ResourceUid )

class Resourceable:
    """ Mix-in class for objects with resource uid"""

    getObjectByUid = getObjectByUid

def listResourceKeys( object=Missing ):
    """
        Returns all resource keys applicable to the given object.

        Arguments:

            'object' -- the object instance to examine; if not given,
                        mandatory resource keys are returned

        Result:

            List of strings.
    """
    if object is Missing:
        return _mandatory_keys[:]

    try:
        uid = ResourceUid( object )
    except TypeError:
        return []

    keys = uid.dict().keys()
    keys.extend( getattr( object, '__resource_subkeys__', [] ) )

    return keys


def registerResource( id, klass, features=(), moniker=None, default=False, path=False, catalog=None ):
    """
        Registers globally unique object type for use by the links subsystem.

        Arguments:

            'id' -- unique type identifier, string

            'klass' -- class implementing this resource type

            'default' -- boolean flag, true if this is the default type

            'path' -- boolean flag, true if resources of this type are
                      identified by their object paths

        Class attributes:

            'keys' -- list of additional mandatory keys

            'identify' -- a method used to find uid of the object

            'lookup' -- a method used to locate the object by uid

        Exceptions:

            'ValueError' -- the specified object type is already registered
    """
    global _resource_types, _default_type, _path_type
    if _resource_types.has_key( id ):
        raise ValueError, id

    _resource_types[ id ] = klass

    klass.id      = getattr( klass, 'id', id )
    klass.default = getattr( klass, 'default', default )
    klass.moniker = getattr( klass, 'moniker', moniker )
    klass.catalog = getattr( klass, 'catalog', catalog )
    klass.keys    = _mandatory_keys + klass.__dict__.get('keys', [])

    if default:
        if _default_type is not None:
            raise ValueError, id
        _default_type = id
        _resource_types[ None ] = klass

    if path:
        if _path_type is not None:
            raise ValueError, id
        _path_type = id

def getResourceHandler( id ):
    if isinstance( id, ResourceUid ):
        id = id.type
    return _resource_types[ id ]

def getDefaultResourceType():
    return _default_type

def getCatalogByType( context, id ):
    id = getResourceHandler( id ).catalog
    return id and getToolByName( context, id ) or None

# mapping type_id => class
_resource_types = {}

_default_type = None
_path_type = None
_mandatory_keys = ['type','uid','service']


# XXX for getObjectByUid (breaks circular dependencies)
Utils.ResourceUid = ResourceUid

def initialize( context ):
    # module initialization callback

    context.register( registerResource )
