"""
Actions-related classes.

$Id: ActionInformation.py,v 1.6 2006/03/24 06:17:22 ikuleshov Exp $
$Editor: vpastukhov $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.ActionInformation import \
        ActionInformation as _ActionInformation, oai as _oai
from Products.CMFCore.utils import getToolByName

import Exceptions
from Features import createFeature
from SimpleObjects import InstanceBase
from Utils import InitializeClass


class ActionInformation( _ActionInformation ):
    """
        Represents a single selectable action.

        See CMF Core documentation.
    """
    security = ClassSecurityInfo()

    def __init__( self, id, icon=None, parameters=None, handler=None, **kwargs ):
        _ActionInformation.__init__( self, id, **kwargs )
        self.icon = icon
        self.params = parameters or []
        self.handler = handler

    def getAction( self, ec ):
        info = _ActionInformation.getAction( self, ec )
        info['icon'] = self.icon
        return info

    def getParameters( self ):
        return self.params

    def getHandler( self, adef=None ):
        return self.handler( adef )

InitializeClass( ActionInformation )


class ActionDefinition( InstanceBase ):
    """
        A persistent container for action parameters.
    """
    _class_version = 1.0

    __implements__ = ( createFeature('isActionDefinition'),
                       InstanceBase.__implements__ )

    __resource_type__ = 'item'

    security = ClassSecurityInfo()

    _properties = InstanceBase._properties
    _basic_properties = [ prop['id'] for prop in _properties ]

    action_id = None

    security.declareProtected( CMFCorePermissions.View, 'getActionId' )
    def getActionId( self ):
        return self.action_id

    security.declareProtected( CMFCorePermissions.View, 'getActionTitle' )
    def getActionTitle( self ):
        actions = getToolByName( self, 'portal_actions' )
        return actions.getActionInfo( self.action_id ).Title()

    def getActionHandler( self ):
        actions = getToolByName( self, 'portal_actions' )
        return actions.getActionInfo( self.action_id ).getHandler( self )

    def setActionId( self, id ):
        if self.action_id == id:
            return

        actions = getToolByName( self, 'portal_actions' )
        info = actions.getActionInfo( id )

        self.action_id = id
        self.clearProperties( all=False )
        self._setupProperties( info )

    def _setupProperties( self, info=Missing ):
        if info is Missing:
            actions = getToolByName( self, 'portal_actions' )
            info = actions.getActionInfo( self.action_id )

        for param in info.getParameters():
            if not self.hasProperty( param['id'] ):
                self._properties += (param,) # XXX should improve _setProperty
                self._setPropValue( param['id'], param.get('default') )

    def setProperties( self, **kwargs ):
        self.manage_changeProperties( None, **kwargs )

    def clearProperties( self, all=True ):
        props = self._propertyMap()
        ignore = not all and self._basic_properties or []
        for prop in props:
            if prop['id'] not in ignore:
                self._delProperty( prop['id'] )

InitializeClass( ActionDefinition )


class oai( _oai ):

    def __init__( self, tool, folder, object=None, url=None ):
        _oai.__init__( self, tool, folder, object )

        if url is not None:
            self.content_url = url

        elif object is not None:
            try: self.content_url = object.relative_url()
            except AttributeError: pass
