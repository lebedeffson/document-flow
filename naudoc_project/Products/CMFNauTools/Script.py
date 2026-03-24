"""
Script class.

$Editor: mbernatski $
$Id: Script.py,v 1.67 2008/03/21 11:05:11 oevsegneev Exp $
"""
__version__ = '$Revision: 1.67 $'[11:-2]


import new, re, sys
from sys import exc_info
from traceback import format_exception_only, format_tb
from types import StringTypes, NoneType
from parser import ParserError

from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from AccessControl.SecurityManagement import getSecurityManager, \
       newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser
from BTrees.OOBTree import OOBTree
from Globals import package_home
from Shared.DC.Scripts.Signature import _setFuncSignature
from webdav.LockItem import LockItem
from ZODB.POSException import ConflictError
from zLOG import LOG, TRACE, ERROR

try:
    from RestrictedPython.compiler_2_1 import pycodegen, visitor
    from RestrictedPython.compiler_2_1.transformer import Transformer

    # backported from compiler module
    def parse(buf, mode="exec"):
        if mode == "exec" or mode == "single":
            return Transformer().parsesuite(buf)
        elif mode == "eval":
            return Transformer().parseexpr(buf)
        else:
            raise ValueError("compile() arg 3 must be"
                             " 'exec' or 'eval' or 'single'")

    misc = None
    ZOPE_IS_OLD = 1
except ImportError:
    from compiler import parse, misc, pycodegen, visitor
    ZOPE_IS_OLD = 0


from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.WorkflowCore import WorkflowException, \
        ObjectDeleted, ObjectMoved
from Products.CMFCore.utils import _checkPermission, getToolByName, _getAuthenticatedUser

import Config, Exceptions, Features
import DefaultScripts
from ActionInformation import ActionInformation as AI
from CatalogSupport import IndexableMethod
from Config import Permissions, ManagedRoles
from Features import createFeature
from Monikers import Moniker
from SimpleObjects import ContentBase
from Utils import InitializeClass, formatPlainText, parseDate, readLink


ScriptType = {
        'id'             : 'Script',
        'meta_type'      : 'Script',
        'title'          : "Script",
        'description'    : "Python script",
        'icon'           : 'pyscript.gif',
        'sort_order'     : 0.45,
        'product'        : 'CMFNauTools',
        'factory'        : 'addScript',
        'immediate_view' : 'script_edit_form',
        'permissions'    : (CMFCorePermissions.ManagePortal,),
        'actions'        : (
                            { 'id'            : 'view',
                              'name'          : 'Edit',
                              'action'        : 'script_edit_form',
                              'permissions'   : (CMFCorePermissions.View,),
                            },
                            { 'id'            : 'metadata',
                              'name'          : 'Metadata',
                              'action'        : 'script_metadata_edit_form',
                              'permissions'   : (CMFCorePermissions.ModifyPortalContent,),
                            },
                            { 'id'            : 'test',
                              'name'          : 'Test',
                              'action'        : 'script_test_form',
                              'permissions'   : (CMFCorePermissions.ModifyPortalContent,),
                            },
                         ),
     }


class DefaultScriptNamespace:
    """
        Default script namespace.
    """
    _class_version = 1.1

    security = ClassSecurityInfo()

    namespace_type = 'default_namespace'

    context = None
    user = None
    portal = None

    Product = None

    def __init__( self, object, user, portal ):
        self.user = user
        self.portal = portal
        self.context = object
        import Products.CMFNauTools as CMFNauToolsProduct
        self.Product = CMFNauToolsProduct
        del CMFNauToolsProduct

    security.declareProtected( CMFCorePermissions.View, 'listNamespaceItems' )
    def listNamespaceItems( self ):
        """
            Returns namespace's items.

            Result:

               Dictionary of attributes.

        """
        items = {}
        items = self.__dict__
        return items

    security.declareProtected( CMFCorePermissions.View, 'getType' )
    def getType( self ):
        """
            Returns namespace's type.
        """
        return self.namespace_type


class Script( ContentBase ):
    """
        Script class.
    """

    _class_version = 1.2

    meta_type = 'Script'
    portal_type = 'Script'

    __implements__ = ( createFeature('isScript'),
                       Features.isExternallyEditable,
                       Features.isPortalContent,
                       Features.isPrintable,
                       Features.hasHeadingInfo,
                       Features.hasTabs,
                       ContentBase.__implements__,
                     )

    security = ClassSecurityInfo()

    manage_options = ContentBase.manage_options

    _actions = (
            AI(
                id          = 'external_edit',
                title       = "External editor",
                description = "Edit using external editor",
                icon        = 'external_editor.gif',
                action      = Expression('string: ${object_url}/externalEdit'),
                permissions = ( CMFCorePermissions.ModifyPortalContent, ),
                condition   = Expression(
                                "python: portal.portal_properties.getConfig('UseExternalEditor') "
                                    "and not object.isLocked()"
                              ),
                visible     = Config.UseExternalEditor,
            ),
        )

    _properties = ContentBase._properties + (
            {'id':'result_type', 'type':'string', 'mode':'w'},
        )

    _v_ft = None

    func_defaults = ()
    func_code = None

    result_type = None
    namespace_factory = DefaultScriptNamespace

    _setFuncSignature = _setFuncSignature

    def __init__( self, id, title=None, text='', **kwargs ):
        """
            Initialize class instance
        """
        ContentBase.__init__( self, id, title, **kwargs )
        self._body = text
        self._parameters = OOBTree()
        self._allowed_types = []

    security.declareProtected( CMFCorePermissions.View, '__call__' )
    def __call__( self, REQUEST=None ):
        """
            Invokes the test form allowed to execute script.
        """
        REQUEST = REQUEST or self.REQUEST
        return self.checkScriptPerm() and self.script_test_form( self, REQUEST ) or self.script_edit_form( self, REQUEST )

    def test( self, REQUEST=None, *args, **kw ):
        """
           Evaluate script in context with arguments and returns error report
           if it exists.
        """
        text = self.body()
        st = 0
        body = False
        while 1:
            # Find the next non-empty line
            m = _nonempty_line.search(text, st)
            if m is None:
                # There were no non-empty body lines
                break
            line = m.group(0).strip()
            if line[:1] != '#':
                # We have found the first line of the body
                body = True
                break

            st = m.end(0)
            # Parse this header line
            if len(line) == 2 or line[2] == ' ' or '=' not in line:
                # Null header line
                continue
        if body:
            self.evaluate( *args, **kw )
        else:
            self._setFuncSignature((), (), 0)
            REQUEST = REQUEST or self.REQUEST
            return self.script_test_form( self, REQUEST )

        return self.script_test_result( self, REQUEST, errors=self.errors )

    def _compile(self):
        """
        """
        code, errors = compile_function(self._params, self._body or 'pass',
                           self.id, self.meta_type)
        if errors:
            self._code = None
            self._v_f = None
            self._setFuncSignature((), (), 0)
            # Fix up syntax errors.
            filestring = '  File "<string>",'
            for i in range(len(errors)):
                line = errors[i]
                if line.startswith(filestring):
                    errors[i] = line.replace(filestring, '  Script', 1)
            self.errors = errors
            return

        self.errors = ()
        f = self._newfun(code)
        fc = f.func_code
        self._setFuncSignature(f.func_defaults or (), fc.co_varnames,
                               fc.co_argcount)

    def _newfun( self, code ):
        """
        """
        g = {'__debug__': __debug__,
             '__name__' : Config.PackagePrefix,
             '__path__' : [ package_home( globals() ) ],
            }
        l = {}
        exec code in g, l
        self._v_f = f = l.values()[0]
        self._v_ft = (f.func_code, g, f.func_defaults or ())
        return f

    def evaluate( self, namespace, raise_exc=False, REQUEST=None, *args, **kw ):
        """
           Evaluate script in context with arguments.
        """
        expr = self.body()
        if expr:
            error = None
            lines = []
            args = []
            global_scope = {}
            global_scope = namespace.listNamespaceItems()
            if kw.has_key( 'parameters' ):
                local_scope = kw['parameters']
                local_names = local_scope.keys()
                for name in local_names:
                    args.append(local_scope[name])
            self.errors = ()
            param_names = self.listParameterNames()
            self._params = param_names

            self._compile()

            ft = self._v_ft
            if ft is None:
                LOG( 'Script.evaluate.',
                     ERROR,
                     'Error was occured while compilation of "%s" script' % (self.id),
                     error=exc_info() )
                return None

            fcode, g, fadefs = ft
            global_scope.update(g)
            f = new.function(fcode, global_scope, None, ())

            oldsm = getSecurityManager()

            system = UnrestrictedUser( 'System Processes', '', ManagedRoles, [] )
            newSecurityManager( None, system )
            try:

                # Execute the function in a new security context.
                getSecurityManager().addContext( self )
                try:
                    try:
                        try:
                            result = f( *args )
                        finally:
                            #XXXX why this needed?
                            self._setFuncSignature((), (), 0)
                        return result
                    except (ObjectDeleted, ObjectMoved):
                        raise
                    except ConflictError:
                        raise
                    except:
                        if raise_exc:
                            raise
                        error = exc_info()
                        try:
                            if error is not None:
                                lines += [ ''.join( format_exception_only(error[0], error[1]) ),
                                           ''.join( format_tb(error[2])[1:] ),
                                           '' ]
                                self.errors = lines
                            LOG( 'Script.evaluate.',
                                 ERROR,
                                 'Error was occured while execution of "%s" script:' % (self.id),
                                 error=error )
                        finally:
                            error = None
                finally:
                    getSecurityManager().removeContext( self )
            finally:
                setSecurityManager( oldsm )


    def setBody( self, text ):
        """
           Writes the Script body
        """
        try:
            body = text.rstrip()
            if body:
                body = body + '\n'
            if body != self._body:
                self._body = body
        except:
            LOG( self.meta_type, ERROR, 'write failed', error=sys.exc_info() )
            raise

    security.declareProtected( CMFCorePermissions.ManageProperties, 'edit' )
    def edit( self, data=None, title=None, REQUEST=None ):
        """
            Edits the script's body
        """
        if data is not None:
            self.write( data )
        if title:
            self.setTitle( title )
        if REQUEST:
            message="Content changed."
            return self.view(self,REQUEST,portal_status_message=message)

    security.declareProtected( CMFCorePermissions.View, 'body' )
    def body( self ):
        """
           Return the body of the script
        """
        return self._body

    security.declareProtected( CMFCorePermissions.View, 'FormattedBody' )
    def FormattedBody( self ):
        """
            Converts plain script's text to HTML code

            Result:

                HTML code
        """
        text = self.body()
        return formatPlainText( text=text )

    def manage_FTPget( self ):
        """
           Get source for FTP download
        """
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')
        return self.body()

    def upload( self, file='' ):
        """
            Replace the body of the script with the text in file.
        """
        if self.wl_isLocked():
            raise Exceptions.ResourceLockedError, "The script is locked via WebDAV."

        if not file:
            raise ValueError, 'File not specified'

        headers = getattr( file, 'headers', {} )
        ctype = headers and headers.get('content-type') or 'unknown'
        ctype = ctype.lower()

        if type(file) not in StringTypes:
            if ctype != 'text/plain':
                raise Exceptions.SimpleError( "Unsupported content type \"%(type)s\" for the script text.", type=ctype )
            file = file.read()

        self.write( file )

    security.declareProtected( CMFCorePermissions.View, 'checkScriptPerm' )
    def checkScriptPerm( self ):
        """
        """
        # portal manager and editor can do any action with script
        return _checkPermission( CMFCorePermissions.ModifyPortalContent, self )

    security.declareProtected( CMFCorePermissions.View, 'getResultType' )
    def getResultType( self ):
        """
            Returns return value type of the script.

            Result:

                Value type Id, or 'None' for unspecified type.
        """
        return self.getProperty( 'result_type' )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setResultType' )
    def setResultType( self, type ):
        """
            Changes return value type of the script.

            Arguments:

                'type' -- new value type Id, or 'None' for unspecified type
        """
        assert isinstance( type, (StringTypes,NoneType) )
        self._updateProperty( 'result_type', type )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setNamespaceFactory' )
    def setNamespaceFactory( self, namespace_type ):
        """
            Sets up the namespace for the script

            Arguments:

                'namespace_type' -- type of the namespace
        """
        self.namespace_factory = getNamespace( namespace_type )

    security.declareProtected( CMFCorePermissions.View, 'getNamespaceFactoryType' )
    def getNamespaceFactoryType( self ):
        """
            Return script's namespace factory type

            Result:

                Type of the namespace
        """
        return self.namespace_factory.namespace_type

    security.declareProtected( CMFCorePermissions.View, 'getNamespaceFactory' )
    def getNamespaceFactory( self ):
        """
            Return script's namespace factory

            Result:

                Namespace class for this script.

        """
        return self.namespace_factory

    security.declarePublic('listParameters' )
    def listParameters( self ):
        """
            Returns the list of the script's parameters.

            Result:

              List of parameters.
        """
        parameters = self._parameters.values()
        return list( parameters )

    security.declarePublic('listParameterNames' )
    def listParameterNames( self ):
        """
            Returns the list of the script's parameters names.

            Result:

              List of parameters names.
        """
        names = self._parameters.keys()
        return ( ",".join( list( names ) ) ).strip()

    security.declareProtected( CMFCorePermissions.View, 'getParameterDefaultValue' )
    def getParameterDefaultValue( self, id, moniker=False ):
        """
            Returns script's parameter default value.

            Result:

                Default parameter value.

        """
        if self._parameters.has_key(id):
            param = self._parameters[id]
        else:
            return None

        value = param['default_value']

        if param['data_type'] == 'link' and value is not None:
            value = readLink( self, 'property', param['id'], value, moniker=moniker )

        return value

    security.declareProtected( CMFCorePermissions.View, 'getParameterById' )
    def getParameterById( self, id ):
        """
            Returns an information about script's parameter.

            Result:

                Dictionary.
        """
        if self._parameters.has_key(id):
            return self._parameters[id]

        return None

    security.declareProtected( CMFCorePermissions.ManageProperties, 'editParameter' )
    def editParameter( self, id, title, value ):
        """
            Edit the parameter's title and default value.
        """
        if self.getParameterById( id ) is None:
            raise KeyError, '%s parameter does not exist' % id
        else:
            data_type = self._parameters[id]['data_type']
            self._parameters.__setitem__( id, { 'id'            :  id
                                              , 'data_type'     :  data_type
                                              , 'title'         :  title
                                              , 'default_value' :  value
                                              })

    security.declareProtected( CMFCorePermissions.ManageProperties, 'addParameter' )
    def addParameter( self, id, data_type, title, value ):
        """
            Sets the parameter to the script.
        """
        if self.getParameterById( id ) is None:
            self._parameters.insert( id, { 'id'            :  id
                                         , 'data_type'     :  data_type
                                         , 'title'         :  title
                                         , 'default_value' :  value
                                         })
        else:
            raise KeyError, '%s parameter already exists' % id

    security.declareProtected( CMFCorePermissions.ManageProperties, 'deleteParameters' )
    def deleteParameters( self, ids ):
        """
            Deletes specified parameters from the script.

            Arguments:

                'ids' -- List of parameter ids to be removed.
        """
        links_tool = getToolByName( self, 'portal_links', None )
        for id in ids:
            try:
                param = self._parameters[id]
                if param['data_type'] == 'link' and param['default_value'] and links_tool:
                    links_tool.removeLink( param['default_value'], restricted=Trust )
                del self._parameters[id]
            except KeyError:
                pass

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setAllowedTypes' )
    def setAllowedTypes( self, type_names ):
        """
            Sets up the list of the portal meta types supported by the script

            Arguments:

                'type_ids' -- list of meta types supported by the script

        """
        self._allowed_types = type_names

    security.declareProtected( CMFCorePermissions.View, 'listAllowedTypes' )
    def listAllowedTypes( self ):
        """
            Returns the list of the supported objects.

            Result:

              List of object type names.
        """
        allowed = self._allowed_types
        return allowed

    security.declareProtected( CMFCorePermissions.View, 'isAllowedForCategoryAndAction' )
    def isAllowedForCategoryAndAction( self, category ):
        """
            Checks is script available for category or not.

            Result:

              True or false.
        """
        allowed = self._allowed_types
        category_allowed = category.listAllowedTypes()
        for typ in allowed:
            if typ in category_allowed and self.getNamespaceFactoryType() == 'action_script_namespace':
                return True
        return False


    security.declareProtected( CMFCorePermissions.View, 'listAllowedNamespacesTypes' )
    def listAllowedNamespacesTypes( self ):
        """
           Returns the list of the existing contexts.

           Result:

             List of allowed namespace types.
        """
        allowed_namespaces = listNamespaceTypes()
        return allowed_namespaces

    def SearchableText(self):
        """
        """
        return '%s %s %s' % ( self.getId(), self.Title(), self.body() )

    def listTabs(self):
        """
            See Feature.hasTabs interface
        """
        REQUEST = self.REQUEST
        msg = getToolByName( self, 'msg' )
 
        tabs = []
        append_tab = tabs.append

        type = self.getTypeInfo()
        link = REQUEST.get('link', '')

        append_tab( { 'url' : self.relative_url( action='script_edit_form', frame='inFrame' )
                    , 'title' : msg('Edit')
                    } )

        if link.find('view') >=0 or link.find('script_edit_form') >=0:
            tabs[-1]['selected'] = True

        if not self.checkScriptPerm():
            return tabs
      
        append_tab( { 'url' : self.relative_url( action='script_metadata_edit_form', frame='inFrame' )
                    , 'title' : msg('Configure')
                    } )
        if link.find('script_metadata_edit_form') >= 0:
            tabs[-1]['selected'] = True

        append_tab( { 'url' : self.relative_url( action='script_parameters_form', frame='inFrame' )
                    , 'title' : msg('Attributes')
                    } )
        if link.find('script_parameters_form') >= 0:
            tabs[-1]['selected'] = True
        
        append_tab( { 'url' : self.relative_url( action='script_test_form', frame='inFrame' )
                    , 'title' : msg('Test')
                    } )
        if link.find('script_test_form')>=0 or link == self.absolute_url():
            tabs[-1]['selected'] = True

        return tabs

    # write is alias to setBody, remove it in future
    write = IndexableMethod( setBody, body=['SearchableText'] )

InitializeClass( Script )


_nonempty_line = re.compile('(?m)^(.*\S.*)$')
_default_script_text = """
"""

def addScript( self, id, title=None, file=None, REQUEST=None, **kwargs ):
    """
        Adds a new Script object.
    """
    obj = Script( id, title, text=_default_script_text, **kwargs )

    self._setObject( id, obj )
    obj = self._getOb( id )

    if file:
        obj.upload( file )


def compile_function( p, body, name, filename ):
    """
        Compile a code object for a function.

        The function can be reconstituted using the 'new' module:

        new.function(<code>, <globals>)
    """
    # Parse the parameters and body, then combine them.
    try:
        tree = parse('def f(%s): pass' % p, 'exec')
    except ParserError, err:
        error = exc_info()
        try:
            res = format_exception_only(error[0], error[1])
        finally:
            error = None
        if len(res)>1:
            res[0] = 'parameters: %s\n' % res[1][10:-8]
            res[1] = '  ' + res[1]

        return None, res

    f = tree.node.nodes[0]
    try:
        btree = parse( body, 'exec' )
    except ParserError, err:
        error = exc_info()
        try:
            res = format_exception_only(error[0], error[1])
        finally:
            error = None

        return None, res

    f.code.nodes = btree.node.nodes
    f.name = name

    if ZOPE_IS_OLD:
        gen = pycodegen.NestedScopeModuleCodeGenerator( filename )
    else:
        misc.set_filename(filename, tree)
        gen = pycodegen.ModuleCodeGenerator( tree )

    visitor.walk(tree, gen)

    return gen.getCode(), ()


def registerNamespace( namespace ):
    name = namespace.namespace_type
    _registered_namespaces[name] = namespace

def listNamespace():
    return _registered_namespaces.values()

def listNamespaceTypes():
    return _registered_namespaces.keys()

def getNamespace( name ):
    return _registered_namespaces[name]

_registered_namespaces = {}

class ScriptInstaller:
    after = True
    priority = 75 # depends on CatPhaseOne and Workflow and Folders installers

    def install(self,p):
        msgcat = getToolByName( p, 'msg' )
        lang = msgcat.get_default_language()

        folder = p.getProperty( 'scripts_folder' )

        for script in DefaultScripts.Scripts.values():
            title = script['title']
            id = script['id']
            obj = Script( id, title=msgcat.gettext( title, lang=lang ) )
            folder._setObject( id, obj )
            obj = folder._getOb( id )
            obj.write( script['data'] )
            obj.namespace_factory = getNamespace( script['namespace_factory'] )
            obj._allowed_types = script['_allowed_types']
            obj.setResultType( script.get( 'result_type' ) )

def initialize( context ):
    # module initialization callback

    context.register( registerNamespace )

    context.registerContent( Script, addScript, ScriptType )
    context.registerNamespace( DefaultScriptNamespace )

    context.registerInstaller( ScriptInstaller )

