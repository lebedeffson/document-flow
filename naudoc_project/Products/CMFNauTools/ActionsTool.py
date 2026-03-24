"""
Actions list tool.

$Editor: vpastukhov $
$Id: ActionsTool.py,v 1.29 2009/02/18 12:14:30 oevsegneev Exp $
"""
__version__ = '$Revision: 1.29 $'[11:-2]

from bisect import bisect_right
from types import DictType, InstanceType

from OFS.Uninstalled import BrokenClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent, aq_base

from Products.CMFCore.ActionsTool import ActionsTool as _ActionsTool
from Products.CMFCore.Expression import createExprContext as _createExprContext
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFCore.TypesTool import TypeInformation

import Config
from ActionInformation import ActionInformation, oai
from SimpleObjects import ToolBase
from Utils import InitializeClass, joinpath, getObjectImplements


class ActionsTool( ToolBase, _ActionsTool ):
    """ Portal actions """
    _class_version = 1.5

    meta_type = 'NauSite Actions Tool'

    security = ClassSecurityInfo()

    manage_options = _ActionsTool.manage_options # + ToolBase.manage_options

    # assign to muttable list, so if it changes, default action_providers also changed.
    action_providers = Config.ActionProviders

    # Method from CMF 1.3
    #   * changed to use relative object URL
    #   * uses custom createExprContext and oai
    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor( self, object=None, object_url=None):

        """
            Gets all actions available to the user and returns a mapping
            containing user actions, object actions, and global actions.
        """
        REQUEST = self.REQUEST

        if REQUEST.has_key('_filtered_actions_'):
            return REQUEST['_filtered_actions_']

        portal = self.getPortalObject()

        if object is None or not hasattr(object, 'aq_base'):
            folder = portal
        elif getObjectImplements( object, 'isPrincipiaFolderish' ):
            folder = object
        elif getObjectImplements( object, 'isItem' ):
            folder = object.parent( 'isPrincipiaFolderish' )
        else:
            folder = object
            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    folder = aq_parent(aq_inner(folder))

        if object_url is None:
            object_url = object is not None and object.absolute_url() or ''
        #ec = createExprContext(folder, portal, object)
        ec = createExprContext( folder, portal, object, url=object_url )
        actions = []
        append = actions.append
        #info = oai(self, folder, object)
        info = oai( self, folder, object, url=object_url )
        # Include actions from specific tools.
        for provider_name in self.listActionProviders():
            provider = getattr(self, provider_name, None)
            if provider and not isinstance( provider, BrokenClass ):
                self._listActions(append,provider,info,ec)

        # Include actions from object.
        if object is not None:
            base = aq_base( object )

            if getObjectImplements(base, 'ActionProvider'):
                self._listActions(append,object,info,ec)

        # Reorganize the actions by category,
        # filtering out disallowed actions.
        filtered_actions = {}

        for action in actions:
            a_get = action.get
            if not a_get('visible', True): continue

            category = action['category']
            permissions = a_get('permissions')

            verified = True
            if permissions:
                # This action requires no extra permissions.
                if (object is not None and
                    (category.startswith('object') or
                     category.startswith('workflow'))):
                    context = object

                elif (folder is not None and
                      category.startswith('folder')):
                    context = folder

                else:
                    context = portal

                for permission in permissions:
                    # The user must be able to match at least one of
                    # the listed permissions.
                    if _checkPermission(permission, context):
                        break
                else:
                    verified = False

            if verified:
                catlist = filtered_actions.setdefault( category, [] )

                # XXX compare dicts
                if action not in catlist:
                    catlist.append( action )

        REQUEST['_filtered_actions_'] = filtered_actions

        return filtered_actions

    # listFilteredActions() is an alias.
    security.declarePublic( 'listFilteredActions' )
    listFilteredActions = listFilteredActionsFor

    security.declarePublic( 'getAction' )
    def getAction( self, id, ignore_permissions=True ):
        object = aq_parent( self )
        folder = object.parent()
        info   = oai( self, folder, object )
        ec     = createExprContext( folder, self.parent(), object )
        action = None

        if getObjectImplements(object, 'ActionProvider'):
            action = self._getAction( id, object, info, ec )

        if action is None:
            for name in self.listActionProviders():
                provider = getToolByName( self, name, None )
                if provider and not isinstance( provider, BrokenClass ):
                    action = self._getAction( id, provider, info, ec )
                    if action is not None:
                        break

        if action is not None:

            if not ignore_permissions:
                # check action permissions
                permissions = action.get( 'permissions' )
                for perm in permissions:
                    if not _checkPermission( perm, object ):
                        return None

            action['url'] = action['url'].strip()
            return action

    def _getAction( self, id, provider, info, ec ):
        actions = provider.listActions( info )

        for action in actions:
            if type(action) is DictType:
                if action.get('id') == id:
                    return action.copy()

            elif action.getId() == id:
                if not action.testCondition( ec ):
                    return None
                return action.getAction( ec )

    def getActionInfo( self, id ):
        ai = _registered_actions[ id ]
        if hasattr( ai, '__of__' ):
            ai = ai.__of__( self )
        return ai

    def listActionsByCategory( self, category, object=None, tuples=False ):
        """
            Returns action descriptors for the given actions category
            and optional object.

            Arguments:

                'category' -- Id of the actions category

                'object' -- optional object to compute the actions for

                'tuples' -- boolean flag, default is false;
                            return tuples in the result if true

            Result:

                List of 'ActionInformation' instances, or list of pairs
                '(Id, ActionInformation)' if 'tuples' argument is given.
        """
        results = []
        ec = createExprContext( folder=self.parent()
                              , portal=self.parent()
                              , object=object )
        info = oai( self, self.getPortalObject(), object )

        for pname in self.listActionProviders():
            provider = getToolByName( self, pname, None )
            if provider and not isinstance( provider, BrokenClass ):
                for ai in provider.listActions( info ):
                    if type(ai) is DictType:
                        # XXX should use CMF 1.4+ to eliminate dicts
                        raise NotImplementedError
                    elif ai.getCategory() == category and ai.testCondition(ec):
                        results.append( ai.__of__( provider ) )

        if tuples:
            results = [ (ai.getId(), ai) for ai in results ]

        for id, ai in _registered_actions.items():
            if ai.getCategory() == category:
                if hasattr( ai, '__of__' ):
                    ai = ai.__of__( self )

                if not ai.testCondition(ec):
                    continue

                if tuples:
                    # XXX each TaskDefinitionRegistry can be registered
                    # under several Ids, thus we can't use getId
                    results.append( (id, ai) )
                else:
                    results.append( ai )

        return results

InitializeClass( ActionsTool )


def createExprContext( folder, portal, object, url=None ):
    context = _createExprContext( folder, portal, object )
    vars = context.global_vars

    if url is not None:
        vars['object_url'] = url

    elif object is not None:
        try: vars['object_url'] = object.relative_url()
        except AttributeError: pass

    return context

def registerAction( id, **kwargs ):
    """
        Registers a global action information.
    """
    global _registered_actions

    if type(id) is InstanceType:
        # got TaskDefinitionRegistry
        registry = id
        for taskdef in registry.getTypeList():
            id = taskdef['id']
            if _registered_actions.has_key( id ):
                raise ValueError, id
            _registered_actions[ id ] = registry

    else:
        if _registered_actions.has_key( id ):
            raise ValueError, id
        _registered_actions[ id ] = ActionInformation( id, **kwargs )

# mapping action_id => (ActionInformation or TaskDefinitionRegistry)
_registered_actions = {}

def initialize( context ):
    # module initialization callback
    context.registerTool( ActionsTool )

    context.register( registerAction )
