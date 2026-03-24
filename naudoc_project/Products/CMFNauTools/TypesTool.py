"""
Portal object types tool.

$Editor: vpastukhov $
$Id: TypesTool.py,v 1.36 2005/10/19 05:01:43 vsafronovich Exp $
"""
__version__ = '$Revision: 1.36 $'[11:-2]

from types import StringType, DictType

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner
from BTrees.OOBTree import OOBTree
from Interface.Implements import instancesOfObjectImplements

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFCore.TypesTool import TypesTool as _TypesTool, typeClasses, \
        TypeInformation, FactoryTypeInformation as _FactoryTypeInformation

from ActionsTool import createExprContext
from SimpleObjects import InstanceBase, ToolBase
from Utils import InitializeClass, getClassByMetaType, getObjectImplements, getActionContext
from ValueTypes import listValueHandlers


class TypesTool( ToolBase, _TypesTool ):
    """
        Portal types tool
    """
    _class_version = 1.9

    meta_type = 'NauSite Types Tool'
    id = 'portal_types'
    isPrincipiaFolderish = _TypesTool.isPrincipiaFolderish

    security = ClassSecurityInfo()

    manage_options = _TypesTool.manage_options # + ToolBase.manage_options

    _actions = tuple(_TypesTool._actions)

    _default_factory_form = 'invoke_factory_form'

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not ToolBase._initstate( self, mode ):
            return 0

        if getattr( self, '_groups', None ) is None:
            self._groups = OOBTree()

        if mode > 1:
            for tname, tinfo in self.objectItems():
                if getattr( aq_base( tinfo ), '_isTypeInformation', None ):
                    self._upgrade( tname, FactoryTypeInformation )

        return 1

    ### Override TypesTool interface methods ###

#    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'listTypeInfo' )
#    def listTypeInfo( self, container=None, groups=0 ):
#       """ Return a sequence of TypeInformation instances
#       """
#       types = _TypesTool.listTypeInfo( self, container )
#
#       if groups:
#           types = filter( lambda ti: not ti.type_group, types )
#       else:
#           types = filter( lambda ti: ti.type_group is not None, types )
#
#       return types

    # TODO: this is a fixed version from CMF 1.3-release
    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'listContentTypes' )
    def listContentTypes( self, container=None, by_metatype=0 ):
        """
            Return list of content types.
        """
        typenames = {}
        for t in self.listTypeInfo( container ):

            if by_metatype:
                name = t.Metatype()
            else:
                name = t.getId()

            if name:
                typenames[ name ] = None

        result = typenames.keys()
        result.sort()
        return result

    # version from CMF 1.4.8
    security.declarePrivate( 'listActions' )
    def listActions( self, info=None ):
        """
            List type-related actions.
        """
        actions = list( self._actions )

        if info is not None:

            type_info = self.getTypeInfo( info.content )

            if type_info is not None:
                actions.extend( type_info.listActions( info ) )

        return actions


    ### New interface methods ###

    def addType( self, id, info ):
        """
        """
        if not getattr( aq_base(info), '_isTypeInformation', 0 ):

            if info.has_key('content_meta_type') or info.has_key('meta_type'):
                #XXX info must explain what type it using
                if info.has_key('responses'):
                    name = 'Task Type Information'
                else:
                    name = FactoryTypeInformation.meta_type
                group = info.get('type_group')

            else:
                name = TypeGroupInformation.meta_type
                group = None

            if group:
                group = self._getOb( group, None )

            factory = _type_factories[name]

            info = factory( group=group, **info )

        self._setObject( id, info )

        return self._getOb( id )

    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'listTypeGroups' )
    def listTypeGroups( self ):
        """ Return a sequence of TypeGroupInformation instances
        """
        return filter( lambda ob: getattr( aq_base(ob), '_isTypeGroup', 0 ), self.objectValues() )

    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'getDefaultFactoryForm' )
    def getDefaultFactoryForm( self ):
        """ Returns a default form used to create a new object instance
        """
        return self._default_factory_form

    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'listValueTypes' )
    def listValueTypes( self ):
        return [ item.id for item in listValueHandlers()
                         if not item.isDerived() ]

InitializeClass( TypesTool )

# supports CMF 1.4.+
if not isinstance( TypeInformation, ActionProviderBase ):
    class ActionSupport( ActionProviderBase ):
        security = ClassSecurityInfo()

        # ported from CMF 1.4.8
        def __init__(self, id, **kw):
      
            self.id = id

            kw = kw.copy()  # Get a modifiable dict.
  
            if kw:
                if (not kw.has_key('content_meta_type')
                    and kw.has_key('meta_type')):
                    kw['content_meta_type'] = kw['meta_type']

                if (not kw.has_key('content_icon')
                    and kw.has_key('icon')):
                    kw['content_icon'] = kw['icon']

                self.manage_changeProperties(**kw)

            actions = kw.get( 'actions', () )
            # make sure we have a copy
            _actions = []
            for action in actions:
                _actions.append( action.copy() )
            # We don't know if actions need conversion, so we always add oldstyle
            # _actions and convert them.
            self._actions = tuple(_actions)
            self._convertActions()

        # ported from CMF 1.4.8
        security.declarePrivate( '_convertActions' )
        def _convertActions( self ):
            """ Upgrade dictionary-based actions.
            """
            aa, self._actions = self._actions, ()

            for action in aa:

                # Some backward compatibility stuff.
                if not action.has_key('id'):
                    action['id'] = cookString(action['name'])

                if not action.has_key('name'):
                    action['name'] = action['id'].capitalize()

                # historically, action['action'] is simple string
                actiontext = action.get('action').strip() or 'string:${object_url}'
                if actiontext[:7] not in ('python:', 'string:'):
                    actiontext = 'string:${object_url}/%s' % actiontext

                #print `self`, action['name'], action.get('visible', 1)
                self.addAction(
                     id=action['id']
                     , name=action['name']
                     , action=actiontext
                     , condition=action.get('condition')
                     , permission=action.get( 'permissions', () )
                     , category=action.get('category', 'object')
                     , visible=action.get('visible', 1)
                     )

        security.declarePublic('getActionById')
        def getActionById( self, id, default=Missing):
            """
                Return the URL of the action whose ID is id.
            """
            context = getActionContext( self )
            for action in self.listActions():

                if action.getId() == id:
                    target = action.action(context).strip()
                    if target.startswith('/'):
                        target = target[1:]
                    return target

            if default is Missing:
                raise ValueError, ('No action "%s" for type "%s"'
                                   % (id, self.getId()))
            else:
                return default

    InitializeClass( ActionSupport )

    class TypeInformation( ActionSupport, TypeInformation ):
        manage_options = TypeInformation.manage_options

    class _FactoryTypeInformation( ActionSupport
                                 , _FactoryTypeInformation ):
        manage_options = _FactoryTypeInformation.manage_options

class TypeGroupInformation( InstanceBase, TypeInformation ):
    """ Portal content factory """
    _class_version = 1.10

    meta_type = 'Types Group'

    _isTypeGroup = 1

    security = ClassSecurityInfo()

    manage_options = TypeInformation.manage_options + \
                     InstanceBase.manage_options

    _properties = _FactoryTypeInformation._properties + (
        {'id':'disallow_manual', 'type': 'boolean', 'mode':'w',
         'label':'Disallow manual creation?'},
        {'id':'sort_order', 'type': 'float', 'mode':'w',
         'label':'Sort order'},
        )

    ### Default attribute values ###

    disallow_manual = 0
    sort_order = 0.75

    # restore method overriden by ItemBase
    Title = TypeInformation.Title

    def __init__( self, id, factory_form=None, **kw ):
        """ Initialize class instance
        """
        InstanceBase.__init__( self )
        TypeInformation.__init__( self, id, **kw )

        if factory_form:
            self.factory_form = factory_form

    def _initstate( self, mode ):
        if not InstanceBase._initstate( self, mode ):
            return False

        if self._actions and isinstance( self._actions[0], DictType ):
            for action in self._actions:
                # XXX restore to simple strings
                if not isinstance(action.get('condition', ''), StringType ):
                    action['condition'] = action['condition'].text
            self._convertActions()

        return True

    security.declarePublic('getFactoryForm')
    def getFactoryForm( self ):
        """ Returns a form used to create a new object instance
        """
        factory_form = getattr(self, 'factory_form', None)
        if factory_form is None:
            types_tool = getToolByName(self, 'portal_types')
            factory_form = types_tool.getDefaultFactoryForm()

        return factory_form

    security.declarePublic( 'typeImplements' )
    def typeImplements( self, feature=() ):
        """
            Checks whether the type implements any of given interfaces or features.
        """
        raise NotImplementedError

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed( self, container ):
        """
        Does the current user have the permission required in
        order to construct an instance?
        """
        return 0

    security.declarePublic('disallowManual')
    def disallowManual( self ):
        """ Should manual creation of objects of this type be disallowed?
        """
        return 1

InitializeClass( TypeGroupInformation )


class FactoryTypeInformation( InstanceBase, _FactoryTypeInformation ):
    """ Portal content factory """
    _class_version = 1.12

    meta_type = 'NauSite Factory-based Type Information'

    security = ClassSecurityInfo()

    manage_options = _FactoryTypeInformation.manage_options + \
                     InstanceBase.manage_options

    _properties = _FactoryTypeInformation._properties + (
            {'id':'disallow_manual', 'type':'boolean', 'mode':'w', 'label':'Disallow manual creation'},
            {'id':'sort_order', 'type':'float', 'mode':'w', 'label':'Sort order'},
            {'id':'type_group', 'type':'string', 'mode':'w', 'label':'Types group name'},
            {'id':'permissions', 'type':'lines', 'mode':'w', 'label':'Required permissions'},
            {'id':'condition', 'type':'string', 'mode':'w', 'label':'Required condition'},
            {'id':'allowed_categories', 'type':'multiple selection', 'select_variable':'manage_listCategoryIds', 'mode':'w', 'label':'Allowed Categories'},
            {'id':'inherit_categories', 'type':'boolean', 'mode':'w', 'label':'Inherit Categories'},
         )

    ### Default attribute values ###

    disallow_manual = 0
    sort_order = 0.75
    type_group = ''
    permissions = ()
    condition = ''
    allowed_categories = ()
    inherit_categories = 1

    # restore method overriden by ItemBase
    Title = _FactoryTypeInformation.Title

    def __init__( self, id, group=None, condition=None, factory_form=None, **kw ):
        """ Initialize class instance
        """
        if group:
            for prop, value in group.propertyItems():
                kw.setdefault( prop, value )

        if condition and type( condition ) == type( '' ):
            self.condition = Expression( condition )
        elif condition:
            self.condition = condition

        if factory_form:
            self.factory_form = factory_form

        InstanceBase.__init__( self )
        _FactoryTypeInformation.__init__( self, id, **kw )

    _initstate = TypeGroupInformation._initstate.im_func

    def __cmp__( self, other ):
        # compare type objects by identifier
        if other is None:
            return 1
        if isinstance( other, FactoryTypeInformation ):
            return cmp( self.getId(), other.getId() )
        if type(other) is StringType:
            return cmp( self.getId(), other )
        raise TypeError, other

    ### Override FactoryTypeInformation interface methods ###

    def _finishConstruction( self, ob ):
        # apply default object properties
        _FactoryTypeInformation._finishConstruction( self, ob )

        if ob.implements('isContentStorage'):
            ob.setAllowedCategories( self.getProperty('allowed_categories') )
            ob.setCategoryInheritance( self.getProperty('inherit_categories') )

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed( self, container ):
        """
        Does the current user have the permission required in
        order to construct an instance?
        """
        #LOG('FactoryTypeInformation', TRACE, 'title:'+`self.title`)
        if self.permissions:
            allowed = 0
            for perm in self.permissions:
                if _checkPermission( perm, container ):
                    allowed = 1
                    break
            if not allowed:
                return 0

        if self.condition:
            #LOG('FactoryTypeInformation', TRACE, 'condition: '+`self.condition`)
            if container is None or not hasattr(container, 'aq_base'):
                #we can not get portal and folder
                #so we can not test condition
                #FIX!!!
                #LOG('FactoryTypeInformation', TRACE, 'container is None: '+`container`)
                pass

            portal = self.getPortalObject()

            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            folder = container
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    folder = aq_parent(aq_inner(folder))

            container_url = container is not None and container.absolute_url() or ''
            #LOG('FactoryTypeInformation', TRACE, 'folder: '+`folder`)
            #LOG('FactoryTypeInformation', TRACE, 'portal: '+`portal`)
            #LOG('FactoryTypeInformation', TRACE, 'container: '+`container`)
            #LOG('FactoryTypeInformation', TRACE, 'container_url: '+`container_url`)
            ec = createExprContext( folder, portal, container, url=container_url )
            if self.condition and not self.condition(ec):
                #LOG('FactoryTypeInformation', TRACE, 'condition() is false')
                return 0
            #LOG('FactoryTypeInformation', TRACE, 'condition() is true')

        return _FactoryTypeInformation.isConstructionAllowed( self, container )

    security.declarePublic('allowType')
    def allowType( self, contentType, construction=True ):
        """ Can objects of 'contentType' be added to containers whose type object we are?
        """
        tinfo = self.getTypeInfo( contentType )
        if tinfo and tinfo.globalAllow():
            # disallow_manual flag takes sense for instance construction only
            if construction and tinfo.disallowManual():
                return False

        # workaround for the bug in the 'list' converter
        if type(self.allowed_content_types) is StringType:
            del self.allowed_content_types

        return _FactoryTypeInformation.allowType( self, contentType )

    ### New interface methods ###

    security.declarePublic('disallowManual')
    def disallowManual( self ):
        """ Should manual creation of objects of this type be disallowed?
        """
        return self.disallow_manual

    security.declarePublic('getFactoryForm')
    def getFactoryForm( self ):
        """ Returns a form used to create a new object instance
        """
        factory_form = getattr(self, 'factory_form', None)
        if factory_form is None:
            types_tool = getToolByName(self, 'portal_types')
            factory_form = types_tool.getDefaultFactoryForm()

        return factory_form

    security.declarePublic( 'typeImplements' )
    def typeImplements( self, feature=() ):
        """
            Checks whether the type implements any of the given interfaces or features.
        """
        klass = getClassByMetaType( self.Metatype() )
        return getObjectImplements( klass, feature )

    security.declarePublic( 'manage_listCategoryIds' )
    def manage_listCategoryIds( self ):
        # returns a list of category ids for the ZMI properties
        mdtool = getToolByName( self, 'portal_metadata', None )
        if mdtool is None:
            return []
        return [ c.getId() for c in mdtool.listCategories() ]

InitializeClass( FactoryTypeInformation )

_type_factories = {}

def registerTypeFactory( klass, action ):
    global _type_factories
    name = klass.meta_type

    for item in typeClasses[:]:
        if item['name'] == name:
            typeClasses.remove( item )

    typeClasses.append( {
            'class'      : klass,
            'name'       : name,
            'action'     : action,
            'permission' : CMFCorePermissions.ManagePortal,
        } )
 
    _type_factories[name] = klass

class TypesInstaller:
 
    _ftiss = []

    def install(self, p):
        for ftis in self._ftiss:
           self.setupTypes(p, ftis )

    def setupTypes(self, portal, ftis):
        types = getToolByName( portal, 'portal_types' )
        for tp in ftis:
            if tp.get( 'activate', True ) and not types.getTypeInfo( tp['id'] ):
                types.addType( tp['id'], tp )
 
    def registerFtis(self, ftis):
        self._ftiss.append( ftis )

    registerFtis = classmethod( registerFtis )

def initialize( context ):
    # module initialization callback
    context.register( registerTypeFactory )
    context.register( TypesInstaller.registerFtis )

    context.registerTool( TypesTool )

    context.registerTypeFactory( FactoryTypeInformation, 'manage_addFactoryTIForm' )
    context.registerTypeFactory( TypeGroupInformation,   'manage_addFactoryTIForm' )

    context.registerInstaller( TypesInstaller )
