"""
Object monikers.

$Editor: vpastukhov $
$Id: Monikers.py,v 1.35 2006/07/06 11:02:17 oevsegneev Exp $
"""
__version__ = '$Revision: 1.35 $'[11:-2]

from cgi import escape
from sys import exc_info
from types import StringType, DictType

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from DocumentTemplate.DT_Util import TemplateDict
from ExtensionClass import Base
from Globals import HTMLFile
from zLOG import LOG, PROBLEM

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _checkPermission

import Config, Exceptions
from DTMLTags import MsgDict
from ResourceUid import ResourceUid, getResourceHandler
from Utils import InitializeClass, getObjectByUid, translate


def Moniker( object, md=None, **kwargs ):
    """
        Returns a moniker for the given object.
    """
    #print 'Moniker', `object`
    if isinstance( object, MonikerBase ):
        return object

    elif isinstance( object, ResourceUid ):
        handler = getResourceHandler( object.type )
        klass = _resource_monikers.get( handler.moniker )
        if klass is None:
            klass = _resource_monikers.get( None )

    elif callable(object) and hasattr( aq_base(object), 'im_self' ):
        klass = _resource_monikers.get( 'method' )

#    elif hasattr( object, '__class__' ) and \
#         hasattr( object.__class__, '__moniker__' ):
#        klass = getattr( object.__class__, '__moniker__', None )

    else:
        try:
            uid = ResourceUid( object )
        except TypeError:
            klass = None
        else:
            handler = getResourceHandler( uid.type )
            klass = _resource_monikers.get( handler.moniker or handler.id )

    if klass is None:
        return object

    #print 'Moniker', klass, `object`, md, kwargs
    return klass( object, md, **kwargs )


class MonikerBase:
    """
        Abstract base class for object monikers.
    """

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess( 1 )

    _id = None
    _ob = Missing
    _types = ()
    _mandatory_args = ( ('moniker_unauthorized', False) # pass Unauthorized error
                      , ('moniker_method', None ) # the object's method for URL
                      , ('moniker_frame', '_blank' ) # browser frame
                      )                      


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
        if isinstance( object, MonikerBase ):
            # copy constructor
            self._id = object._id
            self._ob = object._ob
            if md is None:
                md = object._md

        elif isinstance( object, ResourceUid ):
            # constructor from ResourceUid
            self._id = object

        elif isinstance( object, DictType ):
            # keys of ResourceUid as dictionary
            if object:
                self._id = ResourceUid( object )

        elif isinstance( object, StringType ):
            # string representation of ResourceUid
            if object:
                type_id = self._types and self._types[0] or None
                self._id = ResourceUid( object, type=type_id )
        else:
            self._moniker_bind( object )

        self._md = md
        self._args = kwargs

    def _moniker_bind( self, object ):
        """
            Connects the moniker to the given object.

            Arguments:

                'object' -- target object

            Note:

                To be implemented by the specific subclasses.
        """
        #print 'Moniker._bind', `object`
        self._id = ResourceUid( object )
        self._ob = object

    def _moniker_load( self, context=None ):
        """
            Loads the associated object.

            Arguments:

                'context' -- valid acquisition context

            Note:

                To be implemented by the specific subclasses.
        """
        if self._ob is not Missing or self._id is None:
            return
        #print 'Moniker._load', self._id.dict(), `self._md`
        if context is None:
            context = MsgDict( self._md )
        elif isinstance( context, TemplateDict ):
            context = MsgDict( context )
        try:
            self._ob = self._id.deref( context )
        except LookupError:
            self._ob = None
        #print 'Moniker._load =>', `self._ob`

    def _moniker_render( self, md=None, **kwargs ):
        """
            Returns rendered view of the associated object.

            Arguments:

                'md' -- DTML namespace dictionary

                'kwargs' -- custom rendering parameters

            Result:

                HTML string.

            Note:

                To be implemented by the specific subclasses.
        """
        raise NotImplementedError

    def _render( self, template, md, **kwargs ):
        """
            Returns rendered DTML template using the object
            and the DTML dictionary.
        """
        #print 'Moniker._render'
        try:
            if md is None:
                md = self._md

            ob = self._ob
            if ob is Missing:
                ob = None

            if isinstance( template, StringType ):
                if md is None:
                    raise ValueError

                # acquire page template from DTML namespace
                template = md.getitem( template, False )
                args = (ob, md)

            else:
                args = (template, ob, md)

            # setup template namespace
            for name, value in self._args.items():
                kwargs.setdefault( 'moniker_%s' % name, value )

            # defaults for obligatory arguments
            for name, def_value in self._mandatory_args:
                kwargs.setdefault( name, md.get(name, def_value) )

            # mandatory items
            kwargs['moniker_args']   = self._args  # dict of extra arguments
            kwargs['moniker_id']     = self._id    # the object Uid
            kwargs['moniker_object'] = ob          # the object itself

            if md is not None:
                saved_getattr = md.guarded_getattr
                saved_getitem = md.guarded_getitem
                md.guarded_getattr = None
                md.guarded_getitem = None

            try:
                text = apply( template, args, kwargs )

            finally:
                if md is not None:
                    md.guarded_getattr = saved_getattr
                    md.guarded_getitem = saved_getitem

        except:
            if exc_info()[0] == 'Unauthorized' and kwargs.get('moniker_unauthorized'):
                raise

            LOG( Config.ProductName, PROBLEM,
                 "Error rendering moniker for [%s]:" % str(self._id), error=exc_info() )
            # fallback to minimal rendering
            try:
                if self._ob is Missing:
                    raise ValueError
                text = escape(str( self._ob ))
            except:
                text = escape(str( self._id ))

        return text.strip()

    def __getattr__( self, name ):
        """
            Returns associated object's attribute value,
            or that value's moniker if possible.
        """
        #print 'Moniker.__getattr__', name
        if self._ob is Missing:
            self._moniker_load()
        if self._ob is None:
            raise AttributeError, name

        if hasattr( aq_base(self._ob), name ):
            value = getattr( self._ob, name )

        else:
            if name.startswith('_'):
                raise AttributeError, name
            raise AttributeError, name
            #return UnknownMoniker( name )

        #print 'Moniker.__getattr__ =>', `value`
        return Moniker( value, self._md )

    security.declarePublic( 'title' )
    def title( self, md=None ):
        if self._ob is Missing:
            self._moniker_load( md )
        if self._ob is None:
            return ''
        return self._ob.Title()

    security.declarePublic( 'uid' )
    def uid( self ):
        return self._id

    security.declarePublic( 'render' )
    def render( self, md, **kwargs ):
        #print 'Moniker.render', self._id, `self._ob`
        if self._ob is Missing:
            if md is None:
                raise ValueError
            self._moniker_load( md )
        elif self._ob is None and md is not None:
            del self._ob
            self._moniker_load( md )
        return self._moniker_render( md, **kwargs )

    __render_with_namespace__ = render

    # tells TemplateDict to invoke __call__ with namespace
    #isDocTemp = True

    def __call__( self, context=None, md=None ):
        #print 'Moniker._call', `context`, `md`
        if self._ob is Missing:
            self._moniker_load( context or md )
        #if md is not None:
        #    # called by TemplateDict.__getitem__
        #    return self
        return self._ob

    def __of__( self, context ):
        # used by MsgDict to load monikers
        self._moniker_load( context )
        return self

    def __eq__( self, other ):
        if isinstance( other, MonikerBase ):
            id = other._id
        elif isinstance( other, ResourceUid ):
            id = other
        else:
            try: id = ResourceUid( other )
            except TypeError: return False
        return id == self._id

    def __nonzero__( self ):
        return True

    def __str__( self ):
        #print 'Moniker.__str__'
        return str( self._id )

    def __repr__( self ):
        return '<%s instance at 0x%x, UID=\'%s\'>' % \
               (self.__class__.__name__, id(self), str(self._id))

InitializeClass( MonikerBase )


class MethodMoniker( MonikerBase ):

    def _moniker_bind( self, object ):
        #print 'MethodMoniker._bind =>', `object`
        self._id = object.__name__
        self._m = object

    def _moniker_load( self, context=None ):
        if self._ob is not Missing:
            return
        #print 'MethodMoniker._load', `self._id`, `self._m`
        try:
            self._ob = Moniker( self._m() )
        except:
            self._ob = None
        #print 'MethodMoniker._load =>', `self._ob`

    def _moniker_render( self, md=None, **kwargs ):
        if isinstance( self._ob, MonikerBase ):
            return self._ob._moniker_render( md )
        return str( self._ob )

    def __call__( self, *args, **kwargs ):
        #print 'MethodMoniker.__call__ =>', args, kwargs
        if args or kwargs:
            return self._m( *args, **kwargs )
        if self._ob is Missing:
            self._moniker_load()
        return self._ob


class UnknownMoniker( MonikerBase ):
    """
        Moniker for unknown objects.
    """

    _ob = None
    _text = 'unknown'

    def _moniker_bind( self, object ):
        pass

    def _moniker_load( self, context=None ):
        pass

    def _moniker_render( self, md=None, **kwargs ):
        try:
            return md.getitem( 'msg', False ).gettext( self._text, add=0 )
        except:
            return self._text



class CategoryMoniker( MonikerBase ):
    """
        Moniker for generic objects (ItemBase).
    """

    _template = HTMLFile( 'skins/monikers/category_moniker', globals() )

    def _moniker_render( self, md=None, **kwargs ):
        margs = {}
        for name, value in kwargs.items():
            margs[ 'moniker_%s' % name ] = value

        obj = self._ob

        if obj.implements('isCategoryAttribute'):
            margs['moniker_is_attribute'] = True
            category = obj.parent().parent()

        elif obj.implements('isCategoryAction'):
            margs['moniker_is_action'] = True
            category = obj.parent().parent()

        else:
            category = self._ob

        margs['moniker_category'] = category
        margs['moniker_viewable'] = _checkPermission( 'View', category )

        return self._render( self._template, md, **margs )


class ContentMoniker( MonikerBase ):
    """
        Moniker for content objects (ContentBase).
    """

    _template = HTMLFile( 'skins/monikers/content_moniker', globals() )

    def _moniker_render( self, md=None, **kwargs ):
        #print 'ContentMoniker._render'
        if self._ob is not None:
            action = kwargs.get('action', self._args.get('action') )
            if action and not kwargs.has_key('method'):
                actions = getToolByName( self._ob, 'portal_actions' )
                kwargs['url'] = actions.getAction(action)['url']
            elif self._ob.implements('IDirectoryEntry'):
                kwargs['method'] = 'directory_entry_form'
        margs = {}
        for name, value in kwargs.items():
            margs[ 'moniker_%s' % name ] = value
        self._args.setdefault( 'url', None )
        return self._render( self._template, md, **margs )

    def getEditor( self ):
        if self._ob is None:
            return UnknownMoniker( None, self._md )
        editor = self._ob.getEditor()
        if editor is None:
            return UnknownMoniker( None, self._md )
        return UserMoniker( editor, self._md )

class LinkMoniker( MonikerBase ):
    """
        Moniker for link objects (Link).
    """

    _template = HTMLFile( 'skins/monikers/link_moniker', globals() )

    def _moniker_render( self, md=None, **kwargs ):
        margs = self._args.copy()
        margs.update( kwargs )
        uid = margs.get('uid')
        src = dst = False
        if margs.get('source'):
            if uid:
                return str( self._ob.getSourceUid() )
            src = True
        elif margs.get('target'):
            if uid:
                return str( self._ob.getTargetUid() )
            dst = True
        else:
            src = dst = True

        kwargs['id'] = self._id and self._id.uid or None
        kwargs['moniker_source'] = src
        kwargs['moniker_target'] = dst
        kwargs['moniker_both'] = src and dst

        return self._render( self._template, md, **kwargs )

    def relation( self, md=None ):
        if self._ob is Missing:
            self._moniker_load( md )
        if self._ob is None:
            return UnknownMoniker( 'link relation' )
        return translate( self._ob, self._ob.getRelationInfo('title') ) \
            or self._ob.getRelation()

    def source( self, md=None ):
        if self._ob is Missing:
            self._moniker_load( md )
        if self._ob is None:
            return UnknownMoniker( 'link source' )
        return Moniker( self._ob.getSourceUid(), self._md )

    def target( self, md=None ):
        if self._ob is Missing:
            self._moniker_load( md )
        if self._ob is None:
            return UnknownMoniker( 'link target' )
        return Moniker( self._ob.getTargetUid(), self._md )


class TaskMoniker( MonikerBase ):
    """
        Moniker for task objects (TaskItem).
    """

    _template = HTMLFile( 'skins/monikers/task_moniker', globals() )

    def _moniker_render( self, md=None, **kwargs ):
        margs = {}
        for name, value in kwargs.items():
            margs[ 'moniker_%s' % name ] = value
        return self._render( self._template, md, **margs )


class UserMoniker( MonikerBase ):
    """
        Moniker for member objects (MemberData).
    """

    _template = HTMLFile( 'skins/monikers/member_moniker', globals() )

    def _moniker_render( self, md=None, **kwargs ):
        self._args.setdefault( 'brief', False )
        kwargs['name'] = self._id and self._id.uid or None
        return self._render( self._template, md, **kwargs )

class GroupMoniker( MonikerBase ):
    """
        Moniker for group objects.
    """

    _template = HTMLFile( 'skins/monikers/group_moniker', globals() )

    def __init__( self, object, md=None, **kwargs ):
        if isinstance( object, StringType ) and object.startswith('group:'):
            object = object[6:]
        MonikerBase.__init__( self, object, md=None, **kwargs )

    def _moniker_render( self, md=None, **kwargs ):
        kwargs['name'] = self._id and self._id.uid or None
        return self._render( self._template, md, **kwargs )

class RoleMoniker( MonikerBase ):
    """
        Moniker for role objects.
    """

    _template = HTMLFile( 'skins/monikers/role_moniker', globals() )

    def __init__( self, object, md=None, **kwargs ):
        if isinstance( object, StringType ) and object.startswith('role:'):
            object = object[5:]
        MonikerBase.__init__( self, object, md=None, **kwargs )

    def _moniker_render( self, md=None, **kwargs ):
        kwargs['name'] = self._id and self._id.uid or None
        return self._render( self._template, md, **kwargs )

class PositionMoniker( MonikerBase ):
    """
        Moniker for user position.
    """

    _template = HTMLFile( 'skins/monikers/position_moniker', globals() )

    def __init__( self, object, md=None, **kwargs ):
        if isinstance( object, StringType ) and object.startswith('pos:'):
            object = object[4:]
        MonikerBase.__init__( self, object, md=None, **kwargs )

    def _moniker_render( self, md=None, **kwargs ):
        kwargs['name'] = self._id and self._id.uid or None
        return self._render( self._template, md, **kwargs )

class DivisionMoniker( MonikerBase ):
    """
        Moniker for user position.
    """

    _template = HTMLFile( 'skins/monikers/division_moniker', globals() )

    def __init__( self, object, md=None, **kwargs ):
        if isinstance( object, StringType ) and object.startswith('div:'):
            object = object[4:]
        MonikerBase.__init__( self, object, md=None, **kwargs )

    def _moniker_render( self, md=None, **kwargs ):
        kwargs['name'] = self._id and self._id.uid or None
        return self._render( self._template, md, **kwargs )

def registerMoniker( klass, *types ):
    """
    """
    global _resource_monikers

    if types:
        if not klass._types:
            klass._types = list( types )

        for type_id in types:
            _resource_monikers[ type_id ] = klass

    #name = klass.__name__
    #globals()[ '_%s_class' % name ] = klass
    #globals()[ name ] = lambda object, md=None, klass=klass, **kwargs: \
    #                           apply( _wrapObject, (klass, object, md), kwargs )

_resource_monikers = {}

def _wrapObject( klass, object, md, **kwargs ):
    # wraps an object with moniker
    # TODO this method will cache moniker instances
    #print 'Moniker', klass.__name__, `object`, `md`
    return apply( klass, (object, md), kwargs )

# XXX needed by 'moniker' converter and formatForRequest
import Utils as _Utils_module
_Utils_module.Moniker = Moniker
_Utils_module.MonikerBase = MonikerBase

import ResourceUid as _ResourceUid_module
_ResourceUid_module.Moniker = Moniker


def initialize( context ):
    # module initialization callback
    context.register( registerMoniker )

    context.registerMoniker( UnknownMoniker, None )
    context.registerMoniker( MethodMoniker, 'method' )
    context.registerMoniker( ContentMoniker, 'content', 'item', 'portal' )
    context.registerMoniker( CategoryMoniker, 'category' )
    context.registerMoniker( LinkMoniker, 'link' )
    context.registerMoniker( UserMoniker, 'user' )
    context.registerMoniker( GroupMoniker, 'group' )
    context.registerMoniker( RoleMoniker, 'role' )
    context.registerMoniker( PositionMoniker, 'position' )
    context.registerMoniker( DivisionMoniker, 'division' )
    context.registerMoniker( TaskMoniker, 'task' )

    context.registerVarFormat( 'uid', lambda v, n, md: str(Moniker(v)) )
    context.registerVarFormat( 'object', lambda v, n, md: Moniker(v).render(md) )
    context.registerVarFormat( 'object.title', lambda v, n, md: Moniker(v).title(md) )
    context.registerVarFormat( 'content', lambda v, n, md: ContentMoniker(v).render(md) )
    # TODO: replate with CategoryMoniker
    context.registerVarFormat( 'category', lambda v, n, md: ContentMoniker(v).render(md) )
    context.registerVarFormat( 'link', lambda v, n, md: LinkMoniker(v).render(md) )
    context.registerVarFormat( 'user', lambda v, n, md: UserMoniker(v).render(md) )

    mf = lambda v: v.startswith('pos:') and \
                               PositionMoniker or \
                   v.startswith('div:') and \
                               DivisionMoniker or \
                   v.startswith('group:') and \
                               GroupMoniker or \
                   v.startswith('role:') and \
                               RoleMoniker or UserMoniker
    context.registerVarFormat( 'member', lambda v, n, md, mf=mf: mf(v)(v).render(md) )
    context.registerVarFormat( 'group', lambda v, n, md: GroupMoniker(v).render(md) )
    context.registerVarFormat( 'position', lambda v, n, md: PositionMoniker(v).render(md) )
    context.registerVarFormat( 'division', lambda v, n, md: DivisionMoniker(v).render(md) )
    context.registerVarFormat( 'task.instruct', lambda v, n, md: TaskMoniker(v, instruct=1).render(md) )
    context.registerVarFormat( 'task.simple', lambda v, n, md: TaskMoniker(v, simple=1).render(md) )

    context.registerVarFormat( 'link.source', lambda v, n, md: LinkMoniker(v, source=1).render(md) )
    context.registerVarFormat( 'link.target', lambda v, n, md: LinkMoniker(v, target=1).render(md) )
    context.registerVarFormat( 'user.brief', lambda v, n, md: UserMoniker(v, brief=1).render(md) )
    context.registerVarFormat( 'member.brief', lambda v, n, md: UserMoniker(v, brief=1).render(md) )
