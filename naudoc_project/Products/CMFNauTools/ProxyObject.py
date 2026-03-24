"""
Proxy object mix-in class and helpers.

$Editor: vpastukhov $
$Id: ProxyObject.py,v 1.3 2004/09/23 09:20:54 vpastukhov Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, Explicit, \
        aq_inner, aq_parent, aq_base, aq_self
from ExtensionClass import Base

import Exceptions
from Features import createFeature
from Utils import InitializeClass, getObjectImplements, SequenceTypes


class ProxyItemBase( Implicit ):

    __implements__ = createFeature('isProxyObject')

    _v_proxied_object = None
    _v_wrapper_child = False
    _wrapper_factories = ()
    _wrapper_methods = ()

    def __init__( self, object, child=False ):
        self._v_proxied_object = object
        self._v_wrapper_child = child

    def _proxy_connect( self ):
        raise NotImplementedError

    def _proxy_getObject( self ):
        return aq_self( self._v_proxied_object )

    def __of__( self, parent ):
        wrapped = Implicit.__of__( aq_base(self), parent )
        if self._v_proxied_object is None and aq_parent(parent) is not None:
            wrapped._proxy_connect()
        return wrapped

    def __getattr__( self, name ):
        if self._v_proxied_object is None:
            raise AttributeError, name
        value = getattr( aq_base(self._v_proxied_object), name )
        if name.startswith('_'):
            raise Exceptions.Unauthorized( name )
        return ProxyAttribute( name )

    def _wrapper_wrap( self, object ):
        if object is None:
            return object
        if object is self._v_proxied_object:
            return self
        for iface, factory, child in self._wrapper_factories:
            if getObjectImplements( object, iface ):
                break
        else:
            return object
        if issubclass( factory, Exception ):
            raise factory
        return factory( object, child ).__of__( self )

    def _wrapper_unwrap( self, object ):
        if not isinstance( object, ProxyItemBase ):
            return object
        return object._proxy_getObject()

    def _wrapper_rewrap( self, name, *args, **kw ):
        # this raises AttributeError appropriately
        method = getattr( self._v_proxied_object, name )

        # arrange wrapper and unwrapper
        if self._v_wrapper_child:
            context = aq_parent(aq_inner( self ))
        else:
            context = self
        wrap   = context._wrapper_wrap
        unwrap = context._wrapper_unwrap

        # unwrap all arguments
        unargs = map( unwrap, args )
        unkw = {}
        map( unkw.setdefault, kw.keys(), map(unwrap, kw.values()) )

        # call method and wrap its result
        result = method( *unargs, **unkw )
        if type(result) in SequenceTypes:
            return map( wrap, result )
        else:
            return wrap( result )


class ProxyAttribute( Base ):

    def __init__( self, name ):
        self.__name__ = name

    def __of__( self, parent ):
        return getattr( parent._v_proxied_object, self.__name__ )


class ProxyMethod( Explicit ):

    def __init__( self, name ):
        self.__name__ = name

    def __call__( self, *args, **kw ):
        return aq_parent(aq_inner( self ))._wrapper_rewrap( self.__name__, *args, **kw )


def initializeWrapperClass( klass ):
    for name in klass._wrapper_methods:
        setattr( klass, name, ProxyMethod(name) )
