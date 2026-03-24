"""
NauDoc add-ons management tool.

$Editor: vpastukhov $
$Id: AddonsTool.py,v 1.30 2008/10/15 12:26:54 oevsegneev Exp $
"""
__version__ = '$Revision: 1.30 $'[11:-2]

import os, sys
from sys import exc_info
from types import DictType

from AccessControl import ClassSecurityInfo
from App.ProductContext import ProductContext
from Globals import package_home
from ZODB.PersistentMapping import PersistentMapping
from zLOG import LOG, ERROR, INFO, TRACE

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

import Config, Exceptions
from ActionInformation import ActionInformation as AI
from SimpleObjects import ToolBase
from Utils import InitializeClass, loadModules, isSequence


class AddonsTool( ToolBase ):
    """
        Add-ons Manager Tool
    """
    _class_version = 1.4

    id = 'portal_addons'
    meta_type = 'NauSite Addons Tool'

    _actions = (
            AI( id='manageAddons'
              , title='Add-ons'
              , description='Manage add-on modules'
              , action=Expression( text='string: ${portal_url}/manage_addons_form')
              , permissions=(CMFCorePermissions.ManagePortal,)
              , category='global'
              , condition=None
              , visible=1
            ),
        )

    security = ClassSecurityInfo()

    def __init__( self ):
        ToolBase.__init__( self )
        self._activated_addons = PersistentMapping()

    def _initstate( self, mode ):
        # updates instance attributes

        if not ToolBase._initstate( self, mode ):
            return False

        if mode:
            activated = self._activated_addons
            for id, item in activated.items():
                if not item.has_key('status'): # < 1.4
                    item['status']  = _available_addons.has_key(id) and 'active' or 'broken'
                    item['version'] = None
                    activated._p_changed = 1

        return True

    security.declareProtected( CMFCorePermissions.ManagePortal, 'listAddons' )
    def listAddons( self ):
        """
            Returns list of descriptors for known addons.

            Status codes:

                'active' -- enabled in this portal

                'inactive' -- waiting to be activated

                'disabled' -- manually turned off

                'broken' -- not available
        """
        global _available_addons
        activated = self._activated_addons
        result = []

        for id, info in _available_addons.items():
            item = activated.get( id )
            if not item:
                item = activated[ id ] = { 'status':'inactive' }

            # update cached data, or fill new item
            if not item.has_key('version') or \
                   item['version'] != info['version']:
                item['title'] = info['title']
                item['version'] = info['version']
                activated._p_changed = 1

            # check if broken add-on has been repaired
            if item['status'] == 'broken':
                item['status'] = 'active'
                activated._p_changed = 1

            item = item.copy()
            item.update( info )
            result.append( item )

        for id, item in activated.items():
            if _available_addons.has_key( id ):
                continue

            if item['status'] == 'active':
                item['status'] = 'broken'
                activated._p_changed = 1

            if item['status'] == 'broken':
                result.append( item.copy() )

        return result

    security.declareProtected( CMFCorePermissions.ManagePortal, 'listActiveAddons' )
    def listActiveAddons( self ):
        """
            Returns Ids of all active add-ons.
        """
        global _available_addons

        activated = self._activated_addons.items()
        activated = [ id for id, item in activated if item['status'] == 'active' ]

        return filter( _available_addons.has_key, activated )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'hasActiveAddon' )
    def hasActiveAddon( self, id ):
        """
            Checks whether the indicated add-on is active.
        """
        global _available_addons

        item = self._activated_addons.get( id )
        if not ( item and _available_addons.has_key(id) ):
            return False

        return item['status'] == 'active'

    security.declareProtected( CMFCorePermissions.ManagePortal, 'manage_changeActivatedAddons' )
    def manage_changeActivatedAddons( self, ids=(), REQUEST=None ):
        """
            Installs/uninstalls add-ons into the current portal.
        """
        global _available_addons
        portal = self.getPortalObject()
        activated = self._activated_addons

        addons = self.listAddons()
        addons.sort( lambda x, y: cmp( x.get( 'order', 0 ), y.get( 'order', 0 ) ) )

        for item in addons:
            id = item.get( 'id' )
            if not id:
                continue
            if id in ids:
                if item['status'] == 'active' and not item.get( 'unlocked', 0 ):
                    # already activated
                    continue

                # activate inactive add-on
                result = _getAddon( id ).activate( portal )
                
                if result is None or result:
                    activated[ id ]['status'] = 'active'
                    activated._p_changed = 1

            else:
                if item['status'] != 'active':
                    # already deactivated
                    continue

                # deactivate active add-on
                addon = _getAddon( id, raise_exc=False )
                if addon is not None:
                    addon.deactivate( portal )

                activated[ id ]['status'] = 'disabled'
                activated._p_changed = 1

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect( self.absolute_url() + '/manage_addons_form' )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getAddonProperty' )
    def getAddonProperty( self, id, name ):
        result = None
        if _available_addons.has_key( id ):
            result = _available_addons[id].get( name, None )

        if result is None and self._activated_addons.has_key( id ):
            return self._activated_addons[id].get( name, None )

        return result

    security.declareProtected( CMFCorePermissions.ManagePortal, 'activateAddons' )
    def activateAddons( self, ids, activate=True ):
        """
            Installs/uninstalls particular add-ons into the current portal.
        """
        if not isSequence( ids ):
            ids = [ ids ]

        addons = self.listActiveAddons()
        if activate:
            addons.extend( ids )
        else:
            addons = [ id for id in addons if id not in ids ]

        self.manage_changeActivatedAddons( addons )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'manage_refreshAddons' )
    def manage_refreshAddons( self, REQUEST ):
        """
            Refreshes add-ons registry.
        """
        app = self.getPhysicalRoot()
        object  = app.manage_addProduct[ Config.ProductName ]
        product = __import__( Config.PackagePrefix, None, None, ['__name__'] )

        context = ProductContext( object, app, product )
        initializeAddons( context, app )

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect( self.absolute_url() + '/manage_addons_form' )

InitializeClass( AddonsTool )


# subdirs inside Addons subdirectory that should be skipped
_reserved_subdirs = ['CVS']

# mapping addon_id => addon_info structure
_available_addons = {}

def _getAddon( id, raise_exc=True ):
    if not _available_addons.has_key( id ):
        if raise_exc:
            raise KeyError, "No available addon '%s'" % id
        return None

    addons = loadModules( Config.AddonsPackageName, [id], packages=True, raise_exc=raise_exc )
    addon = addons.get( id )

    if addon is None and raise_exc:
        raise RuntimeError, "Importing error with addon '%s'" % id

    return addon


def initializeAddons( context, app=None ):
    """
        Loads and initializes add-on packages.

        Arguments:

            'context' -- Zope 'ProductContext' object

            'app' -- Zope 'Application' object, if not given
                     is extracted from the context
    """
    # XXX cannot handle removed add-ons yet
    global _available_addons

    if app is None:
        app = context._ProductContext__app

    addons_dir = os.path.join( package_home(globals()), Config.AddonsPackageName )
    if not os.path.exists( addons_dir ):
        return

    addons = loadModules( Config.AddonsPackageName, \
                          skip=_reserved_subdirs, packages=True, raise_exc=False )

    sorted_addons = []
    for name, addon in addons.items():
      sorted_addons.append((name,addon))

    sorted_addons.sort( lambda x, y: cmp( getattr(x[1], 'order', 0), getattr(y[1], 'order', 0) ))

    for name, addon in sorted_addons:
        name = name.split('.')[-1]
        if _available_addons.has_key( name ):
            continue
        try:
            addon.initialize( context, app )
        except:
            LOG( Config.ProductName, ERROR,
                 "Cannot initialize add-on %s" % name, error=exc_info() )
            if _available_addons.has_key( name ):
                _available_addons[ name ]['status'] = 'broken'
        else:
            LOG( Config.ProductName, TRACE, "%s add-on initialized" % name )
            #if _available_addons.has_key( name ):
            #    _available_addons[ name ]['status'] = 'safe'



def registerAddon( id, title=None, version=None, **kwargs ):
    """
        Registers an add-on package.

        Arguments:

            'id' -- unique add-on identifier, string

            'title' -- title of the add-on, string

            'version' -- add-on version, string

            'activate' -- should the add-on be activated in the
                          new portals; boolean, false by default

        Exceptions:

            'ValueError' -- the add-on is already registered
    """
    global _available_addons
    if _available_addons.has_key( id ):
        raise ValueError, id

    kwargs['id'] = id
    kwargs['title'] = title or id
    kwargs['version'] = version and str(version) or None

    kwargs.setdefault( 'order', 50 )
    kwargs.setdefault( 'activate', False )

    _available_addons[ id ] = kwargs


class AddonError( Exceptions.SimpleError ):
    pass

class AddonDeactivateError( AddonError ):

    def __init__( self, *args, **kwargs ):
        AddonError.__init__( self, *args, **kwargs )
        kwargs = self.kwargs

        kwargs.setdefault( 'name', kwargs.get('id','(no name)') )

        if kwargs.has_key('objects'):
            if not self.code:
                self.code = 'addons.used_by_objects'
            kwargs.setdefault( 'count', len(kwargs['objects']) )

Exceptions.AddonError = AddonError
Exceptions.AddonDeactivateError = AddonDeactivateError

class AddonsInstaller:
    after = True
    priority = 100
    def install(self, portal):
        addons = getToolByName( portal, 'portal_addons' )
        active = []

        for info in addons.listAddons():
            if info['status'] == 'active' or \
             ( info['status'] == 'inactive' and info.get('activate') ):
                active.append( info['id'] )

        if active:
            addons.manage_changeActivatedAddons( active )

def initialize( context ):
    # module initialization callback

    context.registerTool( AddonsTool )

    context.register( registerAddon )

    context.registerInstaller( AddonsInstaller )
