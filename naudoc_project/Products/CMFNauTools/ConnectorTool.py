"""
Connector tool.

$Editor: vpastukhov $
$Id: ConnectorTool.py,v 1.14 2005/09/13 05:10:24 vsafronovich Exp $
"""
__version__ = '$Revision: 1.14 $'[11:-2]

from types import StringType

from Acquisition import aq_get
from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOSet

try:
    from Interface.Implements import visitImplements # Zope 2.6.x
except ImportError:
    from Interface.Util import visitImplements # Zope 2.5.x

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

from ActionInformation import ActionInformation as AI
from Exceptions import SimpleError
from Features import createFeature
from SimpleObjects import ToolBase, ContainerBase, InstanceBase, SimpleRecord
from Utils import InitializeClass, cookId


class ConnectorTool( ToolBase, ContainerBase ):
    """
    """
    _class_version = 1.0

    meta_type = 'NauSite Connector Tool'
    id = 'portal_connector'

    security = ClassSecurityInfo()

    manage_options = ContainerBase.manage_options + \
                     ToolBase.manage_options

    _actions = (
            AI( id='manageAdapters'
              , title='External adapters'
              , description='Manage external adapters'
              , action=Expression( text='string: ${portal_url}/manage_adapters_form' )
              , permissions=[ CMFCorePermissions.ManagePortal ]
              , category='global'
              , visible=True
              ),
        )

    all_meta_types = ()

    def __init__( self ):
        ToolBase.__init__( self )
        self._activated_adapters = OOSet()

    #
    # Adapters management
    #

    security.declareProtected( CMFCorePermissions.ManagePortal, 'createAdapter' )
    def createAdapter( self, factory_id ):
        """
        """
        id = cookId( self, prefix=factory_id )
        factory = _getAdapterFactory( factory_id )
        self._setObject( id, factory( id ), set_owner=None )
        return self[ id ]

    getAdapter = ContainerBase._getOb

    security.declareProtected( CMFCorePermissions.ManagePortal, 'listAdapters' )
    def listAdapters( self ):
        """
        """
        return self.objectValues( feature='isAdapter' )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'listAvailableAdapters' )
    def listAvailableAdapters( self ):
        """
        """
        results = []
        for id, factory, enable, kwargs in _listRegisteredAdapters():
            if enable or id in self._activated_adapters:
                rec = SimpleRecord( kwargs, id=id )
                rec.setdefault( 'title', id )
                results.append( rec )
        return results

    security.declareProtected( CMFCorePermissions.ManagePortal, 'isAdapterActive' )
    def isAdapterActive( self, id ):
        """
        """
        _getAdapterFactory( id ) # checks id
        return (id in self._activated_adapters)

    security.declarePrivate( 'activateAdapter' )
    def activateAdapter( self, id ):
        """
        """
        _getAdapterFactory( id ) # checks id
        if id not in self._activated_adapters:
            self._activated_adapters.insert( id )
            self.getAdapter( id ).notifyActivated() 

    security.declarePrivate( 'deactivateAdapter' )
    def deactivateAdapter( self, id ):
        """
        """
        _getAdapterFactory( id ) # checks id
        if id in self._activated_adapters:
            self.getAdapter( id ).notifyDeactivated() 
            self._activated_adapters.remove( id )

    #
    # Services management
    #

    security.declareProtected( CMFCorePermissions.ManagePortal, 'createService' )
    def createService( self, adapter_id, service_id ):
        """
        """
        # check for valid adapter
        adapter = self[ adapter_id ]
        if not adapter.implements( 'isAdapter' ):
            raise TypeError, adapter.meta_type

        # raises exception if service is not valid
        info = adapter.getServiceInfo( service_id )

        # check whether multiple service instance are allowed
        if not info.get('multiple'):
            for service in self.listServices():
                if service.getAdapter() == adapter and service.getType() == service_id:
                    raise SimpleError( message="Service already exists." )

        # create ServiceDefinition instance
        id = cookId( self, prefix='service' )
        self._setObject( id, ServiceDefinition( id ), set_owner=None )

        # bind service to the adapter
        service = self[ id ]
        service.manage_changeProperties( adapter_id=adapter_id, service_id=service_id )

        return service

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getService' )
    def getService( self, sdef ):
        """
        """
        if isinstance( sdef, StringType ):
            sdef = self[ sdef ]
        if not sdef.implements( 'isServiceDefinition' ):
            raise TypeError, sdef.meta_type

        adapter = sdef.getAdapter()
        if adapter.getType() not in self._activated_adapters:
            raise SimpleError( message="Adapter is disabled." )

        return adapter.getService( sdef )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'listServices' )
    def listServices( self, feature=() ):
        """
        """
        services = self.objectValues( feature='isServiceDefinition' )

        if not feature:
            return services
        if isinstance( feature, StringType ):
            feature = [feature]

        results = []
        for service in services:
            implements = service.getInfo().get('implements')
            if not implements:
                continue
            ifaces = []
            visitImplements( implements, None, ifaces.append )
            for iface in ifaces:
                if iface.__name__ in feature:
                    results.append( service )
                    break

        return results

    security.declareProtected( CMFCorePermissions.ManagePortal, 'isServiceActive' )
    def isServiceActive( self, id ):
        """
        """
        service = self._getOb( id, None )
        if service is None or not service.implements( 'isServiceDefinition' ):
            return False

        return service.getAdapter().isActive()

InitializeClass( ConnectorTool )


class AdapterBase( InstanceBase ):
    """
    """
    _class_version = 1.0

    meta_type = 'Adapter Definition'

    __implements__ = InstanceBase.__implements__, \
                     createFeature('isAdapter')

    security = ClassSecurityInfo()

    adapter_type = None
    services = ()

    security.declareProtected( CMFCorePermissions.View, 'getType' )
    def getType( self ):
        return self.adapter_type

    security.declareProtected( CMFCorePermissions.View, 'location' )
    def location( self ):
        raise NotImplementedError

    security.declareProtected( CMFCorePermissions.View, 'isActive' )
    def isActive( self ):
        return self.parent().isAdapterActive( self.getType() )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'testConnection' )
    def testConnection( self ):
        return self.isActive()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getServiceInfo' )
    def getServiceInfo( self, id, default=Missing ):
        for item in self.services:
            if item['id'] == id:
                rec = item.copy()
                rec['adapter'] = self.adapter_type
                return rec
        if default is Missing:
            raise KeyError, id
        return default

    security.declareProtected( CMFCorePermissions.ManagePortal, 'listAvailableServices' )
    def listAvailableServices( self ):
        return self.services # XXX copy?

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getService' )
    def getService( self, service ):
        raise NotImplementedError

    def notifyActivated( self ):
        pass
 
    def notifyDeactivated( self ):
        pass

InitializeClass( AdapterBase )


class ServiceDefinition( InstanceBase ):
    """
    """
    _class_version = 1.0

    meta_type = 'Service Definition'

    __resource_type__ = 'service'

    __implements__ = InstanceBase.__implements__, \
                     createFeature('isServiceDefinition')

    security = ClassSecurityInfo()

    _properties = InstanceBase._properties + (
            {'id':'adapter_id', 'type':'string', 'mode':'w'},
            {'id':'service_id', 'type':'string', 'mode':'w'},
        )

    adapter_id = ''
    service_id = ''

    security.declareProtected( CMFCorePermissions.View, 'index_html' )
    def index_html( self, REQUEST, RESPONSE ):
        """
            Publishes the object.
        """
        return aq_get( self, 'edit_service_form' )( self, REQUEST )

    security.declareProtected( CMFCorePermissions.View, 'getType' )
    def getType( self ):
        """
            Returns service type identifier.
        """
        return self.service_id

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getAdapter' )
    def getAdapter( self ):
        """
            Returns adapter instance for this service.
        """
        adapter = self.parent()[ self.adapter_id ]
        if not adapter.implements( 'isAdapter' ):
            raise TypeError, adapter.meta_type
        return adapter

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getInfo' )
    def getInfo( self, name=None, default=None ):
        """
        """
        if not self.adapter_id or not self.service_id:
            return default
        info = self.getAdapter().getServiceInfo( self.service_id )
        if not name:
            return info
        return info.get( name, default )

    def _propertyMap( self ):
        # returns combined _properties of service definition and implementation
        # TODO cache resulting prop list
        pmap = InstanceBase._propertyMap( self )
        info = self.getInfo()
        if info and info.has_key('properties'):
            pmap += tuple( info['properties'] )
        return pmap

InitializeClass( ServiceDefinition )


def registerAdapter( id, factory, enable=None, **kwargs ):
    """
        Registers adapter for the external system.

        Exceptions:

            'ValueError' -- the adapter is already registered
    """
    global _registered_adapters
    if _registered_adapters.has_key( id ):
        raise ValueError, id

    # add to the adapters registry
    _registered_adapters[ id ] = (id, factory, enable, kwargs)

# mapping adapter_id => adapter_info structure
_registered_adapters = {}


def _getAdapterFactory( id, default=Missing ):
    """
        Returns a callable factory for the specified adapter.

        Arguments:

            'id' -- adapter type ID string

            'default' -- arbitrary value to return in case the requested
                         adapter is not available

        Result:

            An object that creates and returns a new adapter instance
            when called (should be 'AdapterBase'-derived class).

        Exceptions:

            'KeyError' -- the requested adapter is not available
    """
    try:
        return _registered_adapters[ id ][1]
    except KeyError:
        if default is Missing:
            raise
    return default

def _listRegisteredAdapters():
    """
        Returns all registered adapter types.

        Result:

            A list of tuples (id, factory, enable, kwargs) for each
            registered adapter.
    """
    return _registered_adapters.values()


class ServiceResource:

    def identify( portal, object ):
        return { 'uid':object.getId() }

    def lookup( portal, uid=None, **kwargs ):
        try:
            object = getToolByName( portal, 'portal_connector' )[ uid ]
        except KeyError:
            raise LocatorError( 'service', uid )
        if not object.implements('isServiceDefinition'):
            raise LocatorError( 'service', uid )
        return object


def initialize( context ):
    # module initialization callback

    context.registerTool( ConnectorTool )

    context.register( registerAdapter )

    context.registerResource( 'service', ServiceResource, moniker='content' )
