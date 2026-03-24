"""
Exception classes and support functions.

$Editor: vpastukhov $
$Id: Exceptions.py,v 1.31 2008/10/15 12:26:55 oevsegneev Exp $
"""
__version__ = '$Revision: 1.31 $'[11:-2]

import re, sys
from cgi import escape
from linecache import getline
from locale import Error as LocaleError
from traceback import format_exception, tb_lineno
from types import NoneType, StringType, DictType, ListType, TupleType

from Acquisition import aq_base, aq_parent, aq_inner
from DocumentTemplate.DT_Util import TemplateDict
from OFS.CopySupport import CopyError
from OFS.ObjectManager import BeforeDeleteException, BadRequestException
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized

try:
    from webdav.Lockable import ResourceLockedError as _ResourceLockedError
except ImportError:
    class _ResourceLockedError( Exception ): pass

try:
    from zExceptions.ExceptionFormatter import TextExceptionFormatter
except ImportError:
    TextExceptionFormatter = None

from Products.CMFCore.FSPythonScript import FSPythonScript
from Products.CMFCore.FSDTMLMethod import FSDTMLMethod
from Products.CMFCore.utils import getToolByName

import Config, Utils
from DTMLTags import MsgDict
from Monikers import Moniker
from Utils import InstanceTypes


if TextExceptionFormatter:

    class ExceptionFormatter( TextExceptionFormatter ):

        show_revisions = 1

        def formatLine( self, tb ):
            result = TextExceptionFormatter.formatLine( self, tb )
            sep = self.line_sep

            level = 0
            tbn = tb.tb_next
            while tbn is not None:
                level += 1
                tbn = tbn.tb_next

            f = tb.tb_frame
            co = f.f_code
            filename = co.co_filename
            lineno = tb_lineno(tb)

            if co.co_argcount:
                obj = f.f_locals.get( co.co_varnames[0], None )
                if isinstance( obj, FSDTMLMethod ):
                    result += '%s    DTML method %s, rev. %s, at %s' % \
                            ( sep, obj.getId(), getDTMLVersion(obj), obj.getObjectFSPath() )

                elif isinstance( obj, FSPythonScript ):
                    result += '%s    Python script %s, rev. %s, at %s' % \
                            ( sep, obj.getId(), getScriptVersion(obj), obj.getObjectFSPath() )

            line = getline( filename, lineno )
            if line:
                result += '%s    Line %d of function %s:%s      %s' % \
                          ( sep, lineno - co.co_firstlineno, co.co_name, sep, line.strip() )

            maxlev = Config.MaxArgumentsDepth
            names = (not maxlev or level < maxlev) and co.co_varnames[ :co.co_argcount ]
            if names:
                result += sep + '    Function arguments:'
                for name, value in listVariables( f.f_locals, names ):
                    result += sep + '      ' + name + '=' + value

            maxlev = Config.MaxVariablesDepth
            names = (not maxlev or level < maxlev) and co.co_varnames[ co.co_argcount: ]
            if names:
                result += sep + '    Function variables:'
                for name, value in listVariables( f.f_locals, names ):
                    result += sep + '      ' + name + '=' + value

            return result

    _fmt = ExceptionFormatter( Config.MaxTracebackDepth )

    def formatException( *args ):
        t, v, tb = args or sys.exc_info()
        try:    return '\n'.join( _fmt.formatException( t, v, tb ) )
        except: return '\n'.join( format_exception( t, v, tb ) )

else:
    # Zope < 2.6
    class ExceptionFormatter: pass
    def formatException( *args ): pass


#_exc_names = [ 'Debug Error', 'NotFound', 'BadRequest', 'InternalError', 'Forbidden' ]
_exc_types = [ Unauthorized ]
_dlg_rec = re.compile( r'<html\b[^>]*>.*?(?:<title>(.*?)</title>.*?)?<body\b[^>]*>(.*?)</body>.*?</html>' , re.I + re.S )
_pub_rec = re.compile( r'<table\b[^>]*>.*?<p><strong>(.*?)</strong></p>(.*?)<hr\b[^>]*>.*?</table>' , re.I + re.S )
_tag_rec = re.compile( r'<[^>]*>' )
_spc_rec = re.compile( r'\s+' )

def formatErrorValue( etype, value ):
    """
        Strips HTML tags from Zope error messages.
    """
    if not ( type(etype) is StringType or etype in _exc_types ):
        return value

    if type(value) is StringType:
        message = value
    elif getattr( value, 'message', None ):
        message = str( value.message )
    else:
        return value

    match = _dlg_rec.search( message ) \
         or _pub_rec.search( message )

    if match:
        message = _tag_rec.sub( ' ', match.group(2) )
        message = _spc_rec.sub( ' ', message.strip() )
        if message.startswith( '! ' ):
            message = message[ 2: ]
        if not message:
            message = match.group(1)

    message = _tag_rec.sub( ' ', message )
    message = _spc_rec.sub( ' ', message.strip() )

    if type(value) is StringType:
        value = message
    else:
        value.message = message

    return value


def listVariables( namespace, names ):
    results = []

    for name in names:
        try:
            item = namespace[ name ]
        except KeyError:
            value = '<undefined>'
        else:
            value = getObjectRepr( item )
            path = getObjectPath( item, 0 )

            if path:
                context = getObjectPath( item, 1 )
                if context == path:
                    value += ' at %s' % path
                else:
                    value += ' at %s in context %s' % ( path, context )

            if isinstance( item, TemplateDict ):
                value += ' ' + formatTemplateDict( item )

        results.append( (name, value) )

    return results


def formatTemplateDict( md ):
    stack = []
    res   = []

    while 1:
        try: item = md._pop()
        except IndexError: break
        stack.insert( 0, item )

        try:    value = repr(item)
        except: value = '<unprintable %s object>' % type(item).__name__
        res.insert( 0, value )

    # restore dict
    for item in stack:
        md._push( item )

    return '[ ' + ', '.join(res) + ' ]'


_container_types = [ DictType, ListType, TupleType ]

def getObjectRepr( object ):
    """
        Returns simple *object* representation.
    """
    object = aq_base(object)
    info = ''

    if type(object) in _container_types and len(object) > Config.MaxObjectReprLength / 4:
        return '<large %s object: %d items>' % (type(object).__name__, len(object))

    try: info += repr(object)[ :Config.MaxObjectReprLength ]
    except:
        try: info += '<unprintable %s object>' % object.__class__.__name__
        except: info += '<unprintable %s object>' % type(object).__name__

    try: info += ' [%s]' % object.getId()  # item-like
    except:
        try: info += ' <%d>' % object.getRID()  # catalog brains
        except:
            try: info += ' [%s]' % object.__name__   # all else
            except: pass

    return info


def getObjectPath( object, use_context=None ):
    """
        Returns *object* path, either containment or context.
    """
    if aq_parent( object ) is None:
        return ''

    path = ['']

    while object is not None:
        base = aq_base( object )
        try:
            if base.isTopLevelPrincipiaApplicationObject:
                break
        except:
            pass

        # try hard to find object's ID
        try: id = base.getId()  # item-like
        except:
            try: id = '<%d>' % base.getRID()  # catalog brains
            except:
                try: id = base.__name__   # all else
                except: id = '<unknown>'  # no ID

        path.insert( 1, id )

        if use_context:
            object = aq_parent( object )
        else:
            object = aq_parent( aq_inner( object ) )

    try:    return '/'.join( map( str, path ) )
    except: return 'broken path'

def getDTMLVersion( doc ):
    """
        Returns version string of the DTML document.
    """
    try:
        blocks = doc._v_blocks
    except AttributeError:
        return None

    for block in blocks[:5]:
        if hasattr( block, 'isRevisionTag' ):
            return block.version

    return None

def getScriptVersion( script ):
    """
        Returns version string of the Python script.
    """
    count = sol = 0

    while count < 5:
        try:
            eol = script._body.index( '\n', sol )
        except ValueError:
            return None
        line = script._body[ sol:eol ]

        if line.startswith('#'):
            try:
                line = line[ line.index('$'): ]
                if line.startswith('$Revision:'):
                    line = line[ :line.index('$',1)+1 ]
                    return line[ 11:-2 ]
            except ValueError:
                pass

        sol = eol+1
        count += 1

    return None


class SimpleError( Exception ):
    """
        Basic exception class.

        Attributes:

            'code' -- error code, string, maybe 'None'

            'message' -- error message, string, maybe 'None'

            'precedent' -- preceding exception, or 'None'

            'args' -- positional arguments, list

            'kwargs' -- keyword arguments, mapping
    """

    code_prefix = None

    def __init__( self, *args, **kwargs ):
        """
            Initializes new error instance.

            Positional arguments:

                'code' -- the first argument should an error code

                Additionally, all positional arguments are saved
                into the 'args' list.

            Keyword arguments:

                'exc' -- preceding exception value

                'message' -- error message string

                Additionally, all keyword arguments are saved
                into the 'kwargs' mapping.
        """
        if args:
            # the first argument should be the code string
            code = args[0]
            assert type(code) in [NoneType,StringType]
            if code:
                prefix = self.code_prefix
                if prefix and not code.startswith( prefix+'.' ):
                    code = prefix+'.'+code
        else:
            code = None

        exc = kwargs.get('exc')
        if exc is not None:
            # initialized with another exception, reuse its parameters

            # copy positional arguments
            if isinstance( exc, Exception ) and len(args) <= 1:
                try: args = exc.args[:]
                except: pass

            # reuse error code and keyword arguments
            if isinstance( exc, SimpleError ):
                if code is None:
                    code = exc.code
                    assert type(code) in [NoneType,StringType]

                merged = exc.kwargs.copy()
                merged.update( kwargs )
                kwargs = merged

        elif kwargs:
            for key, value in kwargs.items():
                if isinstance( value, InstanceTypes ) and not isinstance( value, StringType ):
                    kwargs[ key ] = Moniker( value )

        self.code = code
        self.message = kwargs.get('message')
        self.precedent = exc
        self.args = args
        self.kwargs = kwargs

    def abort( self ):
        """
            Aborts the current transaction.
        """
        get_transaction().abort()

    def __getitem__( self, key ):
        """
            Returns keyword argument received by the constructor.
        """
        # MsgDict can fetch keys like 'name.subitem'
        if not hasattr( self, '_msgdict' ):
            self._msgdict = MsgDict( None, self.kwargs )
        return self._msgdict[ key ]

    def __str__( self ):
        """
            Returns string identifying the error.
        """
        if self.message is not None:
            return self.message % self
        if self.code is not None:
            return self.code
        if self.args:
            try: return str( self.args[0] )
            except: pass
        return ''

    def __repr__( self ):
        # internal representation for debugging
        klass = self.__class__.__name__
        if self.code:
            res = '%s [%s] exception at 0x%x' % (klass, self.code, id(self))
        else:
            res = '%s exception at 0x%x' % (klass, id(self))
        for k, v in self.kwargs.items():
            res += ', %s=%s' % (k, repr(v))
        return '<' + res + '>'

    def __render_parameters__( self, md ):
        # used by dtml-msg tag for arguments interpolation
        return self.kwargs


class InvalidIdError   ( SimpleError    ): pass
class ReservedIdError  ( InvalidIdError ): pass
class DuplicateIdError ( InvalidIdError ): pass

class DuplicateValueError ( SimpleError    ): pass

class ConverterError   ( SimpleError    ): pass


class BeforeDeleteError( SimpleError, BeforeDeleteException ): pass
class ResourceLockedError( SimpleError, _ResourceLockedError ): pass

# TODO make this SimpleError
class LocatorError( LookupError ): pass

class LicensingError( SimpleError ): pass

class SentinelError( SimpleError ): pass

# XXX a hack to prevent circular import
Utils.Unauthorized     = Unauthorized
Utils.InvalidIdError   = InvalidIdError
Utils.ReservedIdError  = ReservedIdError
Utils.DuplicateIdError = DuplicateIdError
