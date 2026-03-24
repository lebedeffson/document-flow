"""
Helper functions and classes.

$Editor: vpastukhov $
$Id: Utils.py,v 1.187 2008/12/12 14:04:31 oevsegneev Exp $
"""
__version__ = '$Revision: 1.187 $'[11:-2]

import base64, marshal, os, os.path, re, string, sys
from cgi import escape as escapeHTML
from copy import deepcopy
from email.Charset import ALIASES, CHARSETS
#from os.path import abspath as os_abspath, normcase as os_normcase
from posixpath import normpath, split as splitpath
from types import ClassType, MethodType, DictType, \
        TupleType, ListType, UnicodeType, StringType, \
        IntType, FloatType, LongType, ComplexType, \
        InstanceType, BooleanType, StringTypes, FunctionType, \
        LambdaType, BuiltinFunctionType, BuiltinMethodType
from random import randrange
from urllib import quote, unquote, splittype
from UserDict import UserDict
from UserList import UserList
#from codecs import lookup

from Acquisition import aq_get, aq_inner, aq_parent, aq_base
from AccessControl.SecurityManagement import get_ident, \
        getSecurityManager, newSecurityManager, noSecurityManager
from App.Common import package_home
from BTrees.IIBTree import IISet, union, intersection
from BTrees.OIBTree import OISet 
from DateTime import DateTime
# _sorters sets by Patches.py
from DocumentTemplate.DT_In import _sorters as _DT_In_sorters, nocase
from DocumentTemplate.DT_String import String as _DT_String
from DocumentTemplate.DT_Var import special_formats as _DT_var_special_formats
from ExtensionClass import Base, ExtensionClass
from Globals import InitializeClass as _InitializeClass, get_request, DTMLFile
from Interface.Implements import visitImplements, getImplementsOfInstances
from ZPublisher.Converters import type_converters as _type_converters
from ZPublisher.HTTPRequest import record as _zpub_record
from zLOG import LOG, DEBUG, TRACE, WARNING

from OFS.CopySupport import _cb_decode
from OFS.Moniker import loadMoniker
from OFS.ObjectManager import checkValidId as _checkValidId, BadRequestException
from OFS.Uninstalled import BrokenClass

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.DirectoryView import registerMetaType, registerFileExtension
from Products.CMFCore.FSImage import FSImage
from Products.CMFCore.utils import getToolByName, _checkPermission, \
        minimalpath as _minimalpath, expandpath

from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter

import Config

pathdelim = '/'

ClassTypes    = (ClassType, ExtensionClass, type)
MethodTypes   = (MethodType, BuiltinMethodType)
FunctionTypes = (FunctionType, LambdaType, BuiltinFunctionType)
InstanceTypes = (InstanceType, Base, object)
SequenceTypes = (TupleType, ListType, UserList)
MappingTypes  = (DictType, UserDict, _zpub_record)
BooleanTypes  = (IntType is BooleanType) and (BooleanType,) or (BooleanType, IntType)
NumericTypes  = (IntType, LongType, FloatType, ComplexType)

def isMapping( ob ):
    """
        Checks for an object supporting the mapping interface.
    """
    if isinstance( ob, MappingTypes ):
        return True
    try:
        ob[ Missing ]
    except KeyError:
        return True
    except:
        pass
    return False

def isSequence( ob ):
    """
        Checks for an object supporting the sequence interface.
    """
    if isinstance( ob, SequenceTypes ):
        return True
    elif isinstance( ob, StringTypes ):
        return False
    try:
        ob[ len(ob) ]
    except IndexError:
        return True
    except:
        pass
    return False


def getLanguageInfo( context=None, default=Missing ):
    """
        Returns language information for the given language.

        The language information structure is looked up in the
        'Config.Languages' variable either by the given language code
        or by the default language of the portal if an object
        is passed as the first argument.

        Raises 'KeyError' if invalid language is specified and
        no default value given.

        Arguments:

            'context' -- language code, as indicated in the *Config* file,
                         or any object through which portal root can be acquired;
                         if not specified, 'Config.DefaultLanguage' is used

            'default' -- value to be returned if the requested language
                         is not valid

        Result:

            Dictionary as defined in the Config.
    """
    if context is None:
        lang = Config.DefaultLanguage
    elif aq_parent( context ) is not None:
        lang = getToolByName( context, 'msg' ).get_default_language()
    else:
        lang = str(context)

    try:
        return Config.Languages[ lang ]

    except KeyError:
        if default is Missing:
            raise
        return default


def isCharsetKnown( charset ):
    # checks whether the charset name is valid
    if not charset:
        return None
    charset = charset.lower()
    charset = ALIASES.get( charset, charset )
    return CHARSETS.has_key( charset ) and charset or None


def recode_string( text, charset=None, enc_from=None, enc_to=None, default=Missing ):
    """
        Recodes given string from one character set to another.

        Characters unsupported by the source or target encoding
        are removed from the result.  If neither encoding nor charset
        object is specified for input or output, character set
        corresponding to the 'Config.DefaultLanguage' value is used.

        If any of the encodings is not supported then all potentially
        unsafe characters are removed from the string (generally leaving
        only ASCII set in the result), unless default value is given,
        which is returned as the result.

        Arguments:

            'text' -- the string to be recoded

            'charset' -- optional 'Charset' object, used if encoding
                         arguments are omitted

            'enc_from' -- optional name of the source encoding;
                          if not specified, input encoding of the
                          'charset' object is used

            'enc_to' -- optional name of the target encoding;
                        if not specified, output encoding of the
                        'charset' object is used

            'default' -- optional default value that is returned
                         if any of the character sets is unknown

        Result:

            Recoded string or default value.
    """
    if charset:
        enc_from = enc_from or charset.input_charset
        enc_to   = enc_to   or charset.output_charset

    enc_from = ( enc_from or Config.DefaultCharset ).lower()
    enc_from = ALIASES.get( enc_from, enc_from )

    enc_to   = ( enc_to or Config.DefaultCharset ).lower()
    enc_to   = ALIASES.get( enc_to, enc_to )

    # 8bit is a pseudo-encoding used by email package
    if enc_from == enc_to or enc_from == '8bit':
        return text

    try:
        text = unicode( text, enc_from, 'ignore' ).encode( enc_to, 'ignore' )

    except ( LookupError, UnicodeError ):
        if default is Missing:
            text = secureString( text )
        else:
            text = default

    return text

_safe_re = re.compile( '[%s]' % re.escape( string.printable ) )
_eols_re = re.compile( '[%s]+' % string.whitespace.replace(' ','') )

def secureString( text ):
    """
        Removes potentially unsafe characters from the string.
    """
    return _safe_re.sub( '', text )

def flattenString( text ):
    """
        Unfolds multiline text into a single line string,
        removing End-Of-Line characters.
    """
    return _eols_re.sub( ' ', text )

def cutString( text, size, etc='...', flatten=True ):
    """
        Cuts a string, leaving not more than a specified number
        of leading characters.
    """
    text = text.strip()
    if flatten:
        text = _eols_re.sub( ' ', text )
    if len(text) <= size:
        return text
    text = text[:size]
    space = text.rfind(' ')
    if space > size/2:
        text = text[:space+1]
    return text + etc

_script_chars_re = re.compile( r'([\'\"\\])' )
_script_untag_re = re.compile( r'</(script[^>]*)>', re.I )

def escapeJScript( text ):
    """
        Escapes special JavaScript characters in a string.
    """
    text = _script_chars_re.sub( r'\\\1', str(text) )
    text = _script_untag_re.sub( r'<\\057\1>', text )
    return text.replace( '\n', '\\n\\\n' ).replace( '\r', '' )


# XXX move this to localizer
def translit_string( text, lang ):
    """
        Returns given string transliterated to the ASCII set.

        Uses mappings in 'Config.TransliterationMap'.

        Arguments:

            'text' -- the string to be transliterated

            'lang' -- language code of the source

        Result:

            Transliterated string.
    """
    if not text:
        return text

    charmap = Config.TransliterationMap.get( (lang,) )
    if not charmap:
        if type(text) is not UnicodeType:
            text = unicode( text, 'ascii', 'ignore' )
        return text.encode( 'ascii', 'ignore' )

    if type(text) is UnicodeType:
        text = text.encode( getLanguageInfo( lang )['python_charset'], 'ignore' )

    result = ''
    for c in text:
        result += charmap[c]

    return result

def translate( context, text, lang=None ):
    """
        Translates a string to the current language.

        Arguments:

            'context' -- an object through which the portal message
                         catalog can be acquired

            'text' -- the string to be translated

            'lang' -- optional target language code, by default
                      the currently selected language is used

        Result:

            Translated string.
    """
    if not text:
        return ''
    return getToolByName( context, 'msg' ).gettext( text, lang=lang, add=0 )


def tuplify( value ):
    """
        Converts value to tuple.

        Arguments:

            'value' -- either tuple, list, or other object

        Result:

            Python tuple.
    """
    if type(value) is TupleType:
        return value
    elif type(value) is ListType:
        return tuple(value)
    else:
        return (value,)

def uniqueValues( sequence, key=Missing ):
    """
        Removes duplicates from the list, preserving order of the items.

        Arguments:

            'sequence' -- Python list.

            'key' -- TODO

        Result:

            Python list.
    """
    marked = OISet().insert

    append = [].append

    for item in sequence:
        if key is not Missing:
            item_key = item[key]
        else:
            item_key = item
        if marked(item_key):
            append(item)
        
    return append.__self__

def uniqueOptions( options ):
    """
        Removes duplicate (with the same label) options.

        TODO: remove this as redundant
    """
    return tuple(uniqueValues( options, 'label' ))

def sortByAttribute( items, name, reverse=False, mapping=False, stringify=None ):
    """
        Sorts a list of objects by named attribute.

        Arguments:

            'items' -- list of objects to sort

            'name' -- name of the attribute to sort by

        Keyword arguments:

            'reverse' -- sort in reverse order, boolean flag,
                    False by default

            'mapping' -- treat objects in the list as mappings,
                    boolean flag, False by default

            'stringify' -- set this to any true value to perform
                    stringification of attribute values before sorting;
                    if set to the string 'nocase', case-insensitive
                    comparison is taken; attribute values are compared
                    as-is by default

        Result:

            Sorted list of items.
    """
    pairs = []
    for item in items:
        if mapping:
            value = item.get( name )
        else:
            value = getattr( aq_base(item), name, None )

        if callable( value ):
            value = value()

        if stringify:
            if value is None:
                value = ''
            else:
                value = str( value )
                if stringify == 'nocase':
                    value = value.lower()

        pairs.append( (value, item) )

    pairs.sort()
    if reverse:
        pairs.reverse()

    return [ item[1] for item in pairs ]


# TODO
# * support all URL formats ( RFC1738, RFC2396, RFC2368 )
# * complete domains list
# * ftp.doma.in:/path/to/file
# * \\machine\path\to\file

_protos  = [ 'http', 'https', 'ftp', 'nntp' ]
_hostmap = { 'www':'http', 'ftp':'ftp', 'nntp':'nntp', 'news':'nntp' }
_domains = [ 'com', 'net', 'org', 'edu', 'gov', 'mil', 'biz', 'info', \
             'us', 'uk', 'ru', 'su', 'fr', 'de', 'nl', 'by', 'jp', 'tw' ]
_subst   = {
            'P' : '|'.join( _protos ),                  # protocol names
            'H' : '|'.join( _hostmap.keys() ),          # host prefixes
            'D' : '|'.join( _domains ),                 # top-level domains
            'C' : r'a-z0-9_\.\-\+\$\!\*\(\),\%\'',      # safe characters
            'N' : r'a-z0-9_\.\-',                       # hostname characters
            'A' : r'[a-z0-9_\.\-]+(?:\:\d+)?',          # host address
            'Q' : r'\?[^\s\[\]{}()]*',                  # query string
           }

_link_re = r'\b(%(P)s)://(?:[%(C)s]*(?:\:[%(C)s]*)?@)?%(A)s(?:/[%(C)s/~;]*)?(?:%(Q)s)?(?:#[%(C)s]*)?'
_host_re = r'\b(%(H)s)\d*\.%(A)s(?:/[%(C)s/~;]*)?\b'
_zone_re = r'\b[%(N)s]+\.(%(D)s)(?:\:\d+)?(?:/[%(C)s/~;]*)?\b'
_mail_re = r'\b(mailto):(?:(?:[%(C)s]+(?:@%(A)s)?,?)+(?:%(Q)s)?|%(Q)s)'
_addr_re = r'\b([%(C)s]+@%(A)s)\b'
_news_re = r'\b(news):(?:[%(C)s]+|\*)\b'

_url_res = [ _url_re % _subst for _url_re in _link_re, _host_re, _zone_re, _mail_re, _addr_re, _news_re ]
_url_rec = re.compile( '(?:' + '|'.join( _url_res ) + ')', re.I )
_eol_rec = re.compile( r'\r*\n' )

def formatPlainText( text, target=None ):
    """
        Converts plain text to HTML code, inserting hypertext links.

        Lines in the source text become separated with BR tags,
        tabulations and continuous whitespace are converted
        to the same amount of non-breaking spaces for the text
        to retain its formatting.  Special HTML characters are
        replaces with entity references.

        The function also extracts links to external resources
        from the text and replaces them with HTML tags.

        Arguments:

            'text' -- the source text

            'target' -- optional name of the target frame
                        for the links

        Result:

            String containing HTML text.
    """
    parts = []
    match = _url_rec.search( text )

    while match:
        href = link = escapeHTML( match.group(0) )

        if match.group(2): # _host_re
            href = '%s://%s' % ( _hostmap[ match.group(2).lower() ], href )

        elif match.group(3): # _zone_re
            href = 'http://%s' % href

        elif match.group(5): # _addr_re
            href = 'mailto:%s' % href

        if target and ( match.group(1) or match.group(2) or match.group(3) ):
            subst = '<a href="%s" target="%s">%s</a>' % ( href, target, link )
        else:
            subst = '<a href="%s">%s</a>' % ( href, link )

        parts.append( escapeHTML( text[ :match.start() ] ) )
        parts.append( subst )

        text  = text[ match.end(): ]
        match = _url_rec.search( text )

    parts.append( escapeHTML( text ) )
    text = ''.join( parts )

    text = text.expandtabs()
    text = text.replace( '  ', '&nbsp; ' ).replace( '  ', ' &nbsp;' )
    text = _eol_rec.sub( '<br />\n', text )

    return text


_body_start_re = re.compile( r'\A.*<body\b.*?>\s*',  re.I + re.S )
_body_end_re   = re.compile( r'\s*</body\b.*?>.*\Z', re.I + re.S )

def extractBody( text ):
    """
        Returns text inside BODY tag of HTML document.

        Arguments:

            'text' -- source string

        Result:

            String.
    """
    return _body_end_re.sub( '', _body_start_re.sub( '', text, 1 ), 1 )


def joinpath( *parts ):
    """
        Joins two or more pathname components, inserting path
        delimiters as needed.

        The components can be either strings or lists of strings.
        All 'None' values and empty strings are ignored, with a single
        exception: if the first component is an empty string the path
        is considered to be absolute and is prepended with a single
        delimiter.

        Arguments:

            '*parts' -- arbitrary amount of path components

        Result:

            Path string.
    """
    path = []
    for part in parts:
        if isinstance( part, SequenceTypes ):
            path.extend( part )
        elif part is not None:
            if not path and (not part or part.startswith('/')):
                path.append( '' )
            #part = part.strip('/') # python 2.2 only
            while part.startswith('/'): part = part[ 1: ]
            while part.endswith('/'):   part = part[ :-1 ]
            if part:
                path.append( part )
    return '/'.join( path ) or (path and '/' or '')

def makepath( *args ):
    return minimalpath( normpath( joinpath( package_home( globals() ), *args ) ) )

def minimalpath( path ):
    return _minimalpath( path ).replace( '\\', '/' )

#def abspath( path ):
#    return normpath( os_normcase( os_abspath( path ) ).replace( '\\', '/' ) )
#
#_norm_INSTANCE_HOME = abspath( INSTANCE_HOME )
#_norm_SOFTWARE_HOME = abspath( SOFTWARE_HOME )
#
#def minimalpath( path ):
#    # trims INSTANCE_HOME or SOFTWARE_HOME from a path
#    path = abspath( path )
#    plen = len( _norm_SOFTWARE_HOME )
#    if path[:plen] != _norm_SOFTWARE_HOME:
#        plen = len( _norm_INSTANCE_HOME )
#        if path[:plen] != _norm_INSTANCE_HOME:
#            # can't minimize
#            return path
#    path = path[ plen: ]
#    while path.startswith('/'): path = path[1:]
#    return path


_package_prefix = '.'.join( __name__.split('.')[:-1] )
_module_suffixes = ['py','pyc','pyo']

def loadModules( package=None, names=Missing, skip=(),
                 packages=False, refresh=False, raise_exc=True ):
    """
        Loads modules from the specified sub-package.

        Arguments:

            'package' -- name of the package to import, relative
                         to the product location

            'names' -- list of module names to load; if not given,
                       all modules in the package are loaded

            'skip' -- list of module names that should not be loaded;
                      used only when loading all modules (i.e. no 'names')

            'packages' -- whether to load subpackages (directories)
                          instead of modules (files); 'False' by default

            'refresh' -- perform reloading of the modules; 'False'
                         by default

            'raise_exc' -- whether to propagate import errors to the caller,
                           otherwise just log warning; 'True' by default

        Result:

            Mapping from module names to module objects.
    """
    if package is None:
        package = _package_prefix
    else:
        package = _package_prefix + '.' + package

    modules = {}
    namespace = globals()

    if names is Missing:
        # first import the package itself
        module = sys.modules.get( package )
        if module is None:
            try:
                module = __import__( package, namespace, None, ['__name__'] )
            except:
                if raise_exc:
                    raise
                if not package.count('migration'):
                    LOG( Config.ProductName, WARNING, "Cannot import package '%s'" % package, error=sys.exc_info() )
                return modules

        # get directory path of the imported package
        namespace = vars( module )
        path = package_home( namespace )
        names = {}

        # filter out hidden and non-python files
        for name in os.listdir( path ):
            # skip illegal and reserved names
            if name.startswith('_') or name.startswith('.'):
                continue
            if name in skip:
                continue

            # check whether the path is valid package or module
            subpath = os.path.join( path, name )
            if packages:
                if not os.path.isdir( subpath ):
                    continue

            else:
                if not os.path.isfile( subpath ):
                    continue
                name, ext = os.path.splitext( name )
                if ext[1:].lower() not in _module_suffixes:
                    continue

            names[ name ] = 1

        # we need hash because there can exist both source
        # and compiled representation of the same module
        names = names.keys()

    for name in names:
        fullname = package + '.' + name
        module = sys.modules.get( fullname )

        try:
            if module is None:
                # the module is not loaded yet
                module = __import__( fullname, namespace, None, ['__name__'] )

            elif refresh:
                # the module is already loaded and must be refreshed
                module = reload( module )

        except:
            if raise_exc:
                raise
            LOG( Config.ProductName, WARNING,
                 "Cannot import module '%s'" % name, error=sys.exc_info() )

        else:
            modules[ name ] = module

    #print 'loadModules', package, modules.keys()
    return modules


_metatype_map   = {}
_reserved_attrs = ( '__doc__', '__ac_permissions__', 'security' )

def InitializeClass( klass, version=None ):
    """
        Superior replacement for the Zope class initialization method.

        This function does several additional things compared to regular
        class initialization:

          - builds '_class_tag' attribute from versions
            of current and base classes, needed by automated
            object update code

          - populates *meta_type* to class mapping used by
            'getClassByMetaType()' function

          - removes *unimplemented* interfaces or features
            from the list of supported by base classes ones

          - builds '__bases_recursive__' list of all the
            ancestor classes recursively in the order suitable
            for applyRecursive function

          - if 'Config.BindClassAttributes' variable is set,
            inherited attributes and methods are bound to this
            class's dictionary to improve performance

        Arguments:

            'klass' -- class object

            'version' -- optional version of the class; if omitted,
                         '_class_version' is used
    """
    global _metatype_map, _reserved_attrs
    if klass.__dict__.has_key('__initialized__'):
         return
    _InitializeClass( klass )

    # setup metatype-to-class mapping for getClassByMetaType
    if klass.__dict__.has_key('meta_type'):
        _metatype_map[ klass.meta_type ] = klass

    # get class version
    version = version or klass.__dict__.get('_class_version')
    if version:
        version = str( version )
    else:
        version = klass.__name__

    tags = [ version ]
    for base in klass.__bases__:
        if hasattr( base, '_class_tag' ):
            tags.append( base._class_tag )

    # set version tag on the class
    klass._class_version = version
    klass._class_tag = hash( tuple(tags) )

    # remove unimplemented interfaces and features from __implements__
    klass.__implements__ = listImplements( klass )

    # prepare inverted restrictions index
    ac_restrs = klass.__dict__.get('__ac_restrictions__', {})
    restricted_perms = {}
    if type( ac_restrs ) is DictType:
        for restr, perms in ac_restrs.items():
            if type( perms ) is StringType:
                perms = ( perms, )
            for p in perms:
                restricted_perms[ p ] = restr
        # gather restrictions recursively from the bases
        for base in klass.__bases__:
            if not getattr( base, '__ac_restricted_permissions__', None ):
                continue
            for k, v in base.__ac_restricted_permissions__.items():
                restricted_perms.setdefault( k, v )

        klass.__ac_restrictions__ = ac_restrs
        klass.__ac_restricted_permissions__ = restricted_perms

    # prepare recursively expanded base classes list for applyRecursive
    bases  = klass.__bases_recursive__ = list( klass.__bases__ )
    mark   = { klass:1 }
    marked = mark.has_key
    idx    = 0

    while idx < len(bases):
        kls = bases[ idx ]
        if marked( kls ):
            idx += 1
        else:
            mark[ kls ] = 1
            blist = [ base for base in kls.__bases__ if not marked( base ) ]
            if blist:
                bases[ idx:idx ] = blist
            else:
                idx += 1

    klass.__initialized__ = True

    if not Config.BindClassAttributes:
        return

    # bind inherited attributes and methods to the class dictionary
    bound = klass.__bound_attributes__ = {}
    kdict = klass.__dict__
    bases = list( klass.__bases__ )

    while bases:
        base  = bases.pop(0)
        bdict = base.__dict__

        for attr, value in bdict.items():
            if kdict.has_key( attr ) or attr in _reserved_attrs:
                continue
            real = getattr( klass, attr )
            if isinstance( real, MethodTypes ):
                real = real.im_func
            if value is real:
                kdict[ attr ] = value
                bound[ attr ] = 1
                #LOG( 'InitializeClass', TRACE, '[%s] inherited attribute %s from %s' % ( klass.__name__, attr, base.__name__ ) )

        bases.extend( base.__bases__ )


def listImplements( klass, append=(), remove=() ):
    """
        Returns interfaces supported by the klass, excluding unimplemented ones.

        Arguments:

            'klass' -- class object

            'append' -- optional list of additional supported features

            'remove' -- optional list of unsupported features

        Result:

            Tuple containing interface objects.
    """
    implements   = tuplify( getImplementsOfInstances( klass ) )
    unimplements = tuplify( getattr( klass, '__unimplements__', () ) )

    implements   += tuplify( append )
    unimplements += tuplify( remove )

    if not unimplements:
        return implements
    return _recurseUnimplement( implements, unimplements )

def _recurseUnimplement( implements, features ):
    # unimplement() helper
    if isinstance( implements, SequenceTypes ):
        implements = filter( lambda i, f=features: i not in f, implements )
        implements = tuple([ _recurseUnimplement( i, features ) for i in implements ])
    elif implements in features:
        implements = ()
    return implements

def getObjectImplements( object, feature=Missing, name=None ):
    """
        Checks whether an object implements given interface or feature.

        The class is considered to support an interface if that interface
        is enlisted by its '__implements__' attribute.  This list of
        supported interfaces and features may also include those from
        parent classes.  Additionally, integer attributes of the class
        are checked, such as 'isPrincipiaFolderish' (but only if 'name'
        argument is not given).

        Arguments:

            'object' -- instance or class to be checked

            'feature' -- optional interface or feature of interest,
                         can be either interface object or its name

            'name' -- optional name of the object's attribute containing
                      interfaces list, if other than the default one

        Result:

            If 'feature' is requested, boolean value indicating whether
            it is supported; otherwise list of names of all supported
            interfaces and features.
    """
    object = aq_base(object)
    if isinstance( object, ClassTypes ):
        klass = object
    else:
        klass = getattr( object, '__class__', None )

    interfaces = []
    implements = getattr( object, name or '__implements__', None )
    if not implements:
        if feature is Missing:
            return []
        return False

    # TODO execute this during class initialization
    # build a mapping names => interfaces
    visitImplements( implements, object, interfaces.append )
    mapping = {}
    for item in interfaces:
        mapping[ item.__name__ ] = item

    if feature is Missing:
        # removes duplicate entries from the list to avoid ZCatalog
        # unindexing error
        return mapping.keys()

    if not isinstance( feature, SequenceTypes ):
        feature = [feature]

    for item in feature:
        if type(item) is StringType:
            # leading underscore is not allowed
            if item[0] == '_':
                continue
            # check interface name
            if mapping.has_key( item ):
                return True
            # try integer property in class
            if not name:
                value = getattr( klass, item, 0 )
                if isinstance( value, BooleanTypes ) and value:
                    return True
        else:
            # check interface object
            if mapping.get( item.__name__ ) is item:
                return True

    # not found
    return False

def getClassName( klass ):
    """
        Returns full name of the klass (with module name).

        Arguments:

            'klass' -- class object of interest, or an instance
    """
    if not isinstance( klass, ClassTypes ):
        klass = klass.__class__

    return klass.__module__ + '.' + klass.__name__


def getClassByMetaType( meta_type, default=Missing ):
    """
        Returns class object by its *meta_type* name.

        The class must be initialized with 'InitializeClass()' first.
        If no class with given *meta_type* is found 'KeyError' is raised
        unless default value is given.

        Arguments:

            'meta_type' -- *meta_type* name

            'default' -- optional value to be returned if not class is found

        Result:

            Class object.
    """
    try:
        return _metatype_map[ meta_type ]
    except KeyError:
        if default is Missing:
            raise
        return default


def listClassBases( klass, recursive=True ):
    """
        Returns class ancestors.

        Arguments:

            'klass' -- class or instance object

            'recursive' -- optional boolean flag, indicating whether
                           base classes should be listed recursively

        Result:

            A list of class objects.
    """
    if type(klass) is StringType:
        # XXX Convert from string.
        raise NotImplementedError

    elif not isinstance( klass, ClassTypes ):
        klass = klass.__class__

    bases = list( klass.__bases__ )
    if not recursive:
        return bases

    seen = {}
    while bases:
        base = bases.pop(0)
        bases.extend( base.__bases__ )
        seen[ base ] = 1

    return seen.keys()

class StopApplyRecursive( Exception ): pass

def applyRecursive( method, reverse, object, *args, **kwargs ):
    """
        Recursively invokes the callback method for each class
        in the object's inheritance hierarchy.

        Arguments:

            'method' -- reference to the unbound method

            'reverse' -- invoke the methods chain in reverse order

            'object' -- target instance for the method

            '*args', '**kwargs' -- additional arguments to be passed to
                                   the invoked method

        Note:

            Methods are invoked only for classes inherited
            from the method's containing class.  The order of
            processing base classes is left-to-right, depth-first.
    """
    if reverse:
        applyForSubitems( method, reverse, object, *args, **kwargs )

    name  = method.__name__
    klass = method.im_class
    args2 = (object,) + args

    bases = [ object.__class__ ]
    bases[:-1] = getattr( object.__class__, '__bases_recursive__', [] )
    if reverse:
        bases.reverse()

    # cycle through all the inherited classes
    for base in bases:
        if not issubclass( base, klass ):
            continue

        # skip methods bound by InitializeClass
        bound = getattr( base, '__bound_attributes__', None )
        if bound and bound.has_key( name ):
            continue

        # call method from the base class if exists
        if base.__dict__.has_key( name ):
            #print 'apply', name, `object`, base.__name__
            try:
                getattr( base, name )( *args2, **kwargs )
            except StopApplyRecursive:
                break

    if not reverse:
        applyForSubitems( method, reverse, object, *args, **kwargs )


def applyForSubitems( method, reverse, object, *args, **kwargs ):
    """
        Invokes the callback method for each subitem of the object.

        Arguments:

            See 'applyRecursive' description.
    """
    subids  = getattr( object, '_subitems', [] )
    if reverse:
        subids.reverse()

    subargs = getattr( object, '%s_subargs' % method.__name__, ((), {}) )

    for id in subids:
        # this check is needed to evade acquisition
        if not hasattr( aq_base(object), id ):
            continue

        # get the subobject; silently skip missing ones
        subobj = getattr( object, id, None )
        if subobj is None:
            continue

        # prepare the arguments list for the method
        if callable(subargs):
            args2, kwargs2 = subargs( id, *args, **kwargs  )
        else:
            args2, kwargs2 = subargs

        # invoke the method on the subobject
        applyRecursive( method, reverse, subobj, *args2, **kwargs2 )


def installPermission( klass, perm ):
    """
        Installs custom permission in the given *klass*.

        Inserts given permission into '__ac_permissions__' structure
        in the class.  This is needed for the permission to appear on
        the *Security* tab of ZMI.

        Arguments:

            'klass' -- class object

            'perm' -- permission name, string
    """
    ac_perms = getattr( klass, '__ac_permissions__', () )
    if perm not in filter( lambda p: p[0], ac_perms ):
        klass.__ac_permissions__ = ac_perms + ( (perm, ()), )

def isBroken( object, class_name=None ):
    """
        Checks whether existing persistent object is of broken
        (renamed or removed) class.

        Arguments:

            'object' -- any instance

            'class_name' -- original class name (optional), the object should
                            have previously been an instance of this class

        Result:

            Truth if the object is broken.
    """
    return isinstance( object, BrokenClass ) \
           and ( class_name is None or object.__class__.__name__ == class_name \
              or object.__class__.__module__.__name__ + '.' + object.__class__.__name__ == class_name )


def inheritFTIItems( fti, section, *ids ):
    """
        Extracts and copies section items from a given factory
        type information structure.

        Arguments:

            'fti' -- factory type information structure

            'ids' -- identifiers of actions to copy

            'section' -- section name, e.g. 'actions'

        Result:

            Tuple of dictionaries in the same order as IDs.
    """
    items = fti[ section ]
    result = []

    if not ids:
        for item in items:
            result.append( item.copy() )

    else:
        for id in ids:
            for item in items:
                if item['id'] == id:
                    result.append( item.copy() )
                    break
            else:
                raise KeyError, id

    return tuple( result )

def inheritActions( fti, *ids ):
    """
        Extracts and copies action definitions from a given factory
        type information structure.

        Arguments:

            'fti' -- factory type information structure

            'ids' -- identifiers of actions to copy

        Result:

            Tuple of dictionaries in the same order as IDs.
    """
    return inheritFTIItems( fti, 'actions', *ids )

def getActionContext( self ):
    data = { 'object_url'   : ''
           , 'folder_url'   : ''
           , 'portal_url'   : ''
           , 'object'       : None
           , 'folder'       : None
           , 'portal'       : None
           , 'nothing'      : None
           , 'request'      : getattr( self, 'REQUEST', None )
           , 'modules'      : SecureModuleImporter
           , 'member'       : None
           }
    return getEngine().getContext( data )

def _verifyActionPermissions(obj, action):
    res = True
    pp = action.getPermissions()
    if pp:
        for p in pp:
            if _checkPermission(p, obj):
                break
        else:
            res = False
    return res

def _getViewFor(obj, view='view'):
    ti = obj.getTypeInfo()
    if ti is not None:
        context = getActionContext( obj )
        actions = ti.listActions()

        for action in actions:
            if action.getId() == view:
                if _verifyActionPermissions( obj, action ):
                    target = action.action(context).strip()
                    if target.startswith('/'):
                        target = target[1:]
                    return obj.restrictedTraverse( target )

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        for action in actions:
            if _verifyActionPermissions(obj, action):
                target = action.action(context).strip()
                if target.startswith('/'):
                    target = target[1:]
                return obj.restrictedTraverse( target )

        raise Unauthorized, ('No accessible views available for %s' %
                               obj.physical_path())
    else:
        raise 'Not Found', ('Cannot find default view for "%s"' %
                               obj.physical_path())

_num_rec = re.compile( r'\s*\[(\d+)\]\s*$' )

def getNextTitle( title, items=() ):
    """
        Returns title with sequental number appended.

        The purposes of this function is to generate unique titles
        when several objects with the same title are added to the container.
        The returned title has a sequential number in square brackets
        appended to it.  If the title already contains a number it is
        incremented.

        Arguments:

            'title' -- the title string

            'items' -- optional list of already existing titles;
                    they are parsed to find the highest number

        Result:

            Title string with the number in brackets appended.
    """
    idx = len( items )
    match = _num_rec.search( title )
    if match:
        title = title[ :match.start() ]
        if int( match.group(1) ) > idx:
            idx = int( match.group(1) )

    for item in items:
        match = _num_rec.search( item )
        if match and int( match.group(1) ) > idx:
            idx = int( match.group(1) )

    return '%s [%d]' % ( title, idx + 1 )


# characters from ObjectManager.bad_id
_bad_id_re = re.compile( r'[^a-zA-Z0-9-_~,.$\(\)# ]+' )
_invalid_ids = ['.','..']
_words_sep_re = re.compile( r'[\s|_]+' )

def checkValidId( container, id, allow_dup=False ):
    """
        Checks candidate identifier for validity.

        Arguments:

            'container' -- either 'ContainerBase' instance or 'None'

            'id' -- the id string to check

            'allow_dup' -- if true then skip check for an existing subobject
                           with the same id; false by default

        Exceptions:

            'InvalidIdError' -- id contains illegal characters

            'ReservedIdError' -- id conflicts with an object or a method
                                 name that cannot be overridden

            'DuplicateIdError' -- a subobject with the given id already
                                  exists in the 'container'
    """
    names = getattr( container, '_reserved_names', [] )
    if id in names:
        return

    #TIP27 BadRequestException is now real Exception
    try:
        if container is None:
            _checkValidId( None, id, True )

        elif hasattr( container, '_super_checkId' ):
            container._super_checkId( id, allow_dup )

        elif hasattr( container, '_checkId' ):
            container._checkId( id, allow_dup )

        else:
            _checkValidId( container, id, allow_dup )

    except BadRequestException, error:
        #Convert to our exceptions
        if str(error).find('in use') >= 0:
            raise DuplicateIdError( "This identifier is already in use.", id=id )

        if str(error).find('reserved') >= 0:
            raise ReservedIdError( "This identifier is reserved.", id=id )

        raise InvalidIdError( "This identifier is not valid.", id=id )

    if id.strip() in _invalid_ids:
        raise InvalidIdError( "This identifier is not valid.", id=id )

def cookId( container, id=None, prefix='', suffix='', idx=0, title=None, size=20, context=Missing ):
    """
        Generates a new object identifier, the best of all possible.

        New identifier is created from either denoted value,
        title of the object, or prefix with a sequetial number added.
        Generated identifier is checked against existing subobjects
        of the container to prevent duplication.  If the identifier
        is occupied, the number is incremented and the check is repeated.

        If neither 'id' nor 'prefix' nor 'title' is given,
        the returned value is a random '"objXXXXXXXXXX"' string.

        Arguments:

            'container' -- the target where new object will be placed

            'id' -- desired identifier, optional

            'prefix' -- prefix for the sequential identifier, optional

            'suffix' -- suffix for the sequential identifier, optional

            'idx' -- starting index for the sequential identifier, optional

            'title' -- optional title of the new object; not used if 'id' is given

            'size' -- the maximium length of the identifier in characters,
                    20 by default

            'context' -- wrapped object; used to get tool, when 'id' is not given
                                         and container is a simple instance

        Result:

            New identifier string.
    """
    if context is Missing:
        context = container

    if id:
        id = _bad_id_re.sub( '_', id )

    elif title:
        lang = getToolByName( context, 'portal_membership' ).getLanguage()
        # XXX spaces are replaced with underscores here, but it's not always necessary
        id = translit_string( title.strip(), lang )
        id = _words_sep_re.sub( '_', id )

        if len(id) > size:
            # cut and split title into words, then drop clipped last word
            words = id[ :size+1 ].split('_')
            id = len(words) == 1 and words[0] or '_'.join( words[:-1] )

        id = _bad_id_re.sub( '_', id )
        while id.startswith('_'): id = id[1:]
        while id.endswith('_'):   id = id[:-1]

    check_id = _getIdChecker( container )

    if id:
        try:
            check_id( id )
        except DuplicateIdError:
            if not prefix:
                prefix = id
            id = None
        except InvalidIdError:
            id = None
        except BadRequestException, error:
            if error.find('in use') >= 0 and not prefix:
                prefix = id
            id = None
        else:
            if not prefix:
                prefix = id

    elif prefix:
        prefix = _bad_id_re.sub( '_', prefix )

    while not id:
        if prefix:
            idx += 1
            id = '%s_%03d%s' % (prefix, idx, suffix)
        else:
            id = 'obj%010u' % randrange(1000000000)

        try: check_id( id )
        except ( DuplicateIdError, BadRequestException ): id = None

    return id

def _getIdChecker( container ):
    # helper for cookId - returns a callable for id checks
    # container can be either an object, a mapping or a sequence
    if hasattr( container, '_checkId' ):
        return container._checkId

    if isMapping( container ):
        mapping = container

    elif isSequence( container ):
        mapping = {}

        # find ids of all the items and put them into the mapping
        for item in container:
            if type(item) is StringType:
                id = item
            elif hasattr( aq_base(item), 'getId' ):
                id = item.getId()
            elif hasattr( aq_base(item), 'id' ):
                id = item.id
                if callable(id): id = id()
            elif isMapping(item):
                id = item['id']
            else:
                raise TypeError, item
            mapping[ id ] = 1

    else:
        raise TypeError, container

    return lambda id, mapping=mapping: _checkId( id, mapping )

def _checkId( id, mapping=None ):
    # helper for cookId - carries out the real check against the id
    checkValidId( None, id )
    if mapping is not None:
        try: mapping[ id ]
        except KeyError: pass
        else: raise DuplicateIdError( "This identifier is already in use.", id=id )

def listClipboardObjects( context, permission=None, feature=(), cb_copy_data=None, REQUEST=None ):
    """
        Return a list of objects in the clipboard for which current user
        has required permission.

        Positional arguments:

            'context' -- an object inside the portal; needed to acquire
                    application root

            'permission' -- optional permission name (*View* by default)
                    the current user must have on the objects, inaccessible
                    objects are not included in the result

        Keyword arguments:

            'cb_copy_data' -- clipboard data; if not given, 'REQUEST'
                    or 'context' is used to obtain the data

            'REQUEST' -- Zope request object

        Result:

            The list of objects, may be empty.
    """
    oblist = []
    if type(feature) is StringType:
        feature = [feature]

    if cb_copy_data is None:
        if REQUEST is None:
            REQUEST = aq_get( context, 'REQUEST', None )
        cb_copy_data = REQUEST and REQUEST.get('__cp')
        if cb_copy_data is None:
            return oblist

    try:    decoded = _cb_decode( cb_copy_data )
    except: return oblist

    op  = decoded[0]
    app = context.getPhysicalRoot()

    if permission is None:
        permission = CMFCorePermissions.View

    for mdata in decoded[1]:
        m = loadMoniker( mdata )

        try: ob = m.bind( app )
        except: continue

        if feature:
            for name in feature:
                if ob.implements( name ):
                    break
            else:
                continue

        if _checkPermission( permission, ob ):
            oblist.append( ob )

    return oblist

def get_param( name, REQUEST, kw, default=Missing ):
    """
        Retrieves the parameter from either request or dictionary.

        Arguments:

            'name' -- the name of the parameter

            'REQUEST' -- Zope request object

            'kw' -- dictionary for additional 'name' lookup
                    if the parameter is absent from the 'REQUEST'

            'default' -- optional default value to be returned
                    if the parameter is not found

        Result:

            The list of objects, may be empty.

        Exceptions:

            'KeyError' -- the requested parameter is not found
            and default value is not given.
    """
    if REQUEST:
        try: return REQUEST[ name ]
        except KeyError: pass
    if kw:
        try: return kw[ name ]
        except KeyError: pass
    if default is Missing:
        raise KeyError, name
    return default

def extractParams( mapping, request, *names ):
    # returns values from the form
    values = []

    for name, value in request.form.items():
        mapping.setdefault( name, value )

    for name in names:
        if mapping.has_key( name ):
            values.append( mapping[ name ] )
            del mapping[ name ]
        else:
            values.append( None )

    if len(names) == 1:
        return values[0]
    return values


def addQueryString( _url='', _params=None, _fragment=None, **kw ):
    """
        Adds query parameters to the URL string.

        The parameters are taken from three sources in the following
        priority order:  keyword arguments first, then dictionary, and
        existing parameters in the URL in the last place.

        List of tuple values are converted to a *tokens* Zope type.
        'None' values are never included in the result.

        Positional arguments (optional):

            'url=""' -- the URL, may itself contain parameters;
                        empty string is used by default

            'params' -- dictionary mapping parameter names to values

            'fragment' -- URL fragment name, which is added to the result
                          along with the "#" character

        Keyword arguments (optional):

            '**kw' -- additional parameters as name=value pairs

        Result:

            URL string with embedded parameters.
    """
    if _params:
        for name, value in _params.items():
            kw.setdefault( name, value )

    if _url:
        parts  = _url.split( '?', 1 )
        result = parts.pop(0)
        if parts:
            # parse query params from url to override with kw params
            for part in parts[0].split('&'):
                name, value = part.split( '=', 1 )
                kw.setdefault( unquote(name), unquote(value) )
    else:
        result = _url

    parts = [quote(name, '') + '=' + quote(str(value), '')
             for name, value in formatForRequest(kw.items())]

    if parts:
        result += '?' + '&'.join( parts )

    if _fragment is not None:
        result += '#' + _fragment

    return result


def buildUrl( url, action=None, params=None, fragment=None, message=None, \
              frame=None, popup=None, redirect=None, REQUEST=None ):
    # helper function for 'absolute_url' and 'relative_url'
    if REQUEST is None and redirect:
        redirect = False # no sense to redirect without client
    if params is None:
        params = {}

    relative = not ( url.startswith('/') or splittype(url)[0] )

    if frame is not None:
        if relative:
            # use dot to keep number of levels in the path
            frame = frame or '.'
            res = action or '.'
        else:
            res = joinpath(url, action) or url
        params = { 'link' : addQueryString( res, params, fragment ) }
        action = frame
        fragment = None

    res = joinpath( url or None, action ) or '.'

    if message is not None:
        params['portal_status_message'] = message

    if popup:
        params = { 'frame' : 'workspace',
                   'link'  : addQueryString( res, params, fragment ) }
        res = joinpath( url, 'reload_frame' )
        fragment = None

    elif redirect:
        for param in ['noWYSIWYG']:
            params[ param ] = REQUEST.get( param )

        if REQUEST.get('_UpdateWorkspace'):
            params = { 'frame' : 'workspace',
                       'link'  : addQueryString( res, params, fragment ) }
            res = joinpath( relative and '.' or url, 'reload_frame' )
            fragment = None

        params['_UpdateSections'] = REQUEST.get('_UpdateSections')

    if params:
        res = addQueryString( res, params, fragment )

    return res

def getPublishedInfo( context, REQUEST ):
    # returns extended information about what was published

    # first try to return cached result
    try: return REQUEST['PUBLISHED_INFO']
    except KeyError: pass

    # processInputs stores modified PATH_INFO in 'other', thus use environ
    path_info = REQUEST.environ.get('PATH_INFO','').strip()
    has_slash = path_info.endswith('/')
    path_id   = splitpath( normpath(path_info) )[1]

    published = REQUEST.get('PUBLISHED')
    assert published is not None, 'no PUBLISHED in REQUEST'

    is_method = isinstance( aq_base(published), MethodTypes )
    if is_method:
        object = published.im_self
    else:
        if hasattr( aq_base(published), 'implements' ):
            # TODO: need fix for DTMLDocument; exclude publisher
            is_method = False #not published.implements('isItem')
        elif getattr( aq_base(published), 'isDocTemp', False ):
            is_method = True
        elif hasattr( aq_base(published), 'func_code' ):
            is_method = True
        if is_method:
            object = aq_parent( published )
        else:
            object = published

    if is_method and REQUEST._hacked_path:
        is_method = False

    url_tool = getToolByName( context, 'portal_url' )
    #print `published`, `object`, published is object
    rel_path = url_tool.getRelativeContentPath( object )

    if not (has_slash or is_method):
        #real object doesn`t has slash, so real base url is the parent url
        rel_path = rel_path[:-1]
    elif has_slash and is_method:
        #method has slash, so real base url is the method url
        rel_path += ( path_id,)

    #print `published`, `object`, is_method, path_id, has_slash, rel_path
    info = (aq_base(published), aq_base(object), 
            is_method, path_id, has_slash, rel_path)
    REQUEST.set( 'PUBLISHED_INFO', info )

    return info


def refreshClientFrame( section, REQUEST=None ):
    """
        Sets an indicator in the request object that named section
        of the user interface needs to be refreshed.

        The real update is initiated by a JavaScript variable
        'updateSections' which is set to the list of section names
        in the page header.

        The list of sections that need to be refreshed is saved
        during external redirection as an '_UpdateSections' query
        parameter.  If *workspace* needs to be refreshed then the
        issued redirection points to a *reload_frame* page which
        loads requested link into the *workspace* frame.

        Arguments:

            'section' -- the section name such as '"workspace"'
                         or those defined in the *menu.dtml*

            'REQUEST' -- Zope request object; retrieved with
                         'get_request()' if not specified
    """
    if REQUEST is None:
        REQUEST = get_request()
        if REQUEST is None:
            return
    if section == 'workspace':
        REQUEST.set( '_UpdateWorkspace', 1 )
    else:
        updated = REQUEST.get( '_UpdateSections' )
        if not updated:
            REQUEST.set( '_UpdateSections', [ section ] )
        elif section not in updated:
            updated.append( section )


def checkCommand( command ):
    """
        Checks whether a given system command can be found
        in 'PATH' and is executable.

        Arguments:

            'command' -- system command name without path
                         and '".exe"' extension

        Result:

            Truth value if command is found and is executable.
    """
    path = os.environ.get('PATH') or os.defpath

    for prefix in path.split( os.pathsep ):
        if os.access( prefix + os.sep + command, os.X_OK ) or \
           os.access( prefix + os.sep + command + '.exe', os.X_OK ):
            return 1

    return 0


def encodeMapping( mapping ):
    # encodes mapping to a base64 string
    encoded = base64.encodestring( marshal.dumps( mapping ) )
    return encoded.strip().replace( '\n', '' )

def decodeMapping( encoded ):
    # decodes a base64 string to a mapping
    mapping = {}
    if encoded:
        mapping.update( marshal.loads( base64.decodestring( encoded ) ) )
    return mapping


def parseDate( value, mapping=Missing, default=Missing ):
    """
        Returns a date value from the submitted HTML form.

        The form may contain either a single field for date string
        or three separate fields for year, month and day. In the latter
        case the field names should have '"_year"', '"_month"' and '"_day"'
        suffixes respectively.

        The entered values are extracted from the request and converted
        to a 'DateTime' object.

        Positional arguments:

            'value' -- either string, record, or name of the date field;
                       in the latter case 'mapping' argument must present

            'mapping' -- optional mapping or Zope request object

            'default' -- optional value that is returned if valid
                         date cannot be returned

        Result:

            'DateTime' object of default value.

        Exceptions:

            See 'parseDateTime' function.
    """
    if type(value) is StringType and mapping is not Missing:
        name = value
        try:
            if mapping.has_key( name ):
                value = mapping[ name ]
                if not value:
                    raise KeyError, name
            else:
                value = { 'year'  : mapping[ '%s_year'  % name ],
                          'month' : mapping[ '%s_month' % name ],
                          'day'   : mapping[ '%s_day'   % name ] }
        except KeyError:
            if default is not Missing:
                return default
            raise KeyError, name

    # XXX needed for type converter
    if type(value) is StringType and not len(value.strip()):
        if default is not Missing:
            return default
        return None

    return parseDateTime( value, default, time=False )

_month_day_re = re.compile( r'\A(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})' )
_date_items = ['year','month','day']
_time_items = ['hour','minute']
_extra_items = ['second']

def parseDateTime( value, default=Missing, time=True ):
    """
        Returns a date value parsed from the passed value.

        Positional arguments:

            'value' -- value, from which date will be parsed. Can be
                       a string or mapping with 'year', 'month' and 'day' keys

            'default' -- optional value that is returned if valid date cannot
                         be returned

            'time' -- if true (default), parse both date and time, otherwise
                      time components are stripped from the result

        Result:

            'DateTime' object, or default value.

        Exceptions:

            'TypeError' -- value type is not valid

            'KeyError' -- mapping object does not have all required keys

            'DateTime.SyntaxError' -- the date string cannot be parsed and no
                                      default value is given

            'DateTime.DateTimeError' -- the date value is not valid and no
                                        default value is given

    """
    if value is None and default is not Missing:
        return default

    # XXX needed for type converter
    if type(value) is StringType and not len(value.strip()):
        if default is not Missing:
            return default
        return None

    if isinstance( value, DateTime ):
        return time and value or value.earliestTime()

    if type(value) is StringType:
        args = [ _month_day_re.sub( r'\3/\2/\1', value ) ] # YYYY/MM/DD

    else:
        try:
            # may raise KeyError if key does not exist
            args = [ value[i] for i in _date_items ]
        except ( AttributeError, TypeError ):
            raise TypeError, 'string or mapping required'

        if time:
            # may raise KeyError if some key does not exist
            args.extend( [ value[i] for i in _time_items ] )

        for i in _extra_items:
            try: args.append( value[i] )
            except KeyError: pass

        try:
            # parse strings into integers
            args = map( int, args )
        except ValueError:
            pass # try DateTime conversion anyway

    try:
        value = DateTime( *args )
    except (DateTime.SyntaxError, DateTime.DateTimeError):
        if default is not Missing:
            return default
        raise

    return time and value or value.earliestTime()

def parseTimePeriod( value ):
    days, hours, minutes = [ int(part) for part in value.split(':') ]
    return days*86400 + hours*3600 + minutes*60

def parseTime( name, REQUEST, default=Missing ):
    """
        Returns a time interval value from the submitted HTML form.

        The form may have up to three fields (for number of days,
        hours, and minutes) combined into *record* type.  The fields
        should be named with the base record name and '"days"', '"hours"'
        and '"minutes"' suffixes respectively.

        The entered values are extracted from the request and converted
        to a single number of seconds.

        Arguments:

            'name' -- base name of the record fields

            'REQUEST' -- Zope request object

            'default' -- optional value that is returned if specified
                         record is not found in the request

        Result:

            Number of seconds or default value.

        Exceptions:

            'KeyError' -- the request does not contain required fields
            and default value is not specified
    """
    record = REQUEST.get( name )
    if not record:
        if default is Missing:
            raise KeyError, name
        return default

    days    = record.get( 'days',    0 )
    hours   = record.get( 'hours',   0 )
    minutes = record.get( 'minutes', 0 )

    return days*86400 + hours*3600 + minutes*60

def parseUid( value, default=Missing ):
    # uid converter for ZPublisher
    if type(value) is StringType:
        value = value.strip() or None

    elif isinstance( value, _zpub_record ):
        # a 'record' object from HTML form
        link = value.get('value') or None
        if link is not None:
            raise NotImplementedError
        try:
            # if uid is an empty string, use None
            value = value['uid'] or None
        except KeyError:
            if default is Missing:
                raise
            return default

    if value is not None:
        try:
            value = ResourceUid( value )
        except TypeError:
            if default is Missing:
                raise
            return default

    return value

def parseMoniker( value, default=Missing ):
    # moniker converter for ZPublisher
    uid = parseUid( value, default )
    return Moniker( uid )

def readLink( *args, **kwargs ):
    # for implementation by the DocumentLinkTool
    return _readLink( *args, **kwargs )

def updateLink( *args, **kwargs ):
    # for implementation by the DocumentLinkTool
    return _updateLink( *args, **kwargs )


def getObjectByUid( context, uid, feature=(), restricted=False ):
    """
        Returns an object inside the portal, given it's UID
        and bypassing access rights.

        Arguments:

            'context' -- any object through which portal catalog
                         can be acquired

            'uid' -- required object UID

            'feature' -- optional list if interface or feature names,
                         any of which the object must support

            'restricted' -- optional boolean flag, restricting
                            the search to accessible to the current
                            user objects only; False by default

        Result:

            The object or None if not found.
    """
    if not uid:
        return None
    if not isinstance( uid, ResourceUid ):
        uid = ResourceUid( uid )

    try:
        ob = uid.deref( context )
    except LookupError:
        return None

    if feature:
        # TODO move loop to implements method
        if type(feature) is StringType:
            feature = [feature]
        for name in feature:
            if ob.implements(name):
                break
        else:
            return None

    if restricted and not _checkPermission( CMFCorePermissions.View, ob ):
        return None

    return ob

class File( FSImage ):
    """
        Filesystem File
    """
    meta_type = 'Filesystem File'

    def _readProperties(self):

        props_name = expandpath(self._filepath + '.properties')
        props = {}

        try:
            f = open(props_name, 'rt')
        except IOError:
            pass
        else:
            for line in f.readlines():
                try: key, value = line.split('=', 1)
                except: pass
                else:
                    props[key.strip()] = value.strip()
            f.close()

        return props

    #security = ClassSecurityInfo()
    #security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = DTMLFile( 'dtml/custfile', globals() )

    def _readFile( self, reparse ):
        data = FSImage._readFile( self, 0 )

        # XXX workaround for CMF-1.3-beta bug (doesn't read .properties)
        props = self._readProperties()
        if props:
            self.__dict__.update(props)

        if self.content_type == 'unknown/unknown':
            ext = os.path.splitext( self._filepath )[1]
            ext = ext[1:].lower() # remove dot

            ctype = Config.FileExtensionMap.get( ext, Config.DefaultAttachmentType )
            self.setContentType( ctype )

        return data

    def read(self):
        self._updateFromFS()
        return self._data
    __str__ = read

    def setContentType( self, ctype ):
        self.content_type = ctype

registerMetaType( 'File', File )
#for _ext in Config.FileExtensionMap.keys():
#    registerFileExtension( _ext, File )


try:
    from BTrees.IIBTree import multiunion
except ImportError: # Zope < 2.6
    multiunion = None

def multiintersection( seq ):
    return reduce( intersection, seq, None )

if multiunion is None:
    def multiunion( seq ):
        return reduce( union, seq, None )

def setDefaultAttrs(object, names, value):
    """
        Initializes object attributes which names is taken from list with
        default value (made for usage in _initstate method).

        Positional arguments:

            'object' -- any object.

            'names' -- list of attribute names.

            'value' -- default value. Used to initialize attributes that not
                       present in object.

        Result:

            Number of attributes that have been initialized.
    """
    changed = 0
    object  = aq_base(object)
    value   = deepcopy(value)

    for name in names:
        if hasattr(object, name): continue

        setattr(object, name, value)
        changed += 1

    return changed

def formatForRequest(pairs, ignore=()):
    """
        Converts list of (name, value) pairs to similar list that can be
        passed through request (via url or <input type="hidden"...>).
        However it have some limitations: None values are ignored, nested lists
        flatten to one level.

        Roughly speaking - it does reverse operation relative to
        HTTPRequest.processInputs and the same as ZTUtils.Zope.complex_marshal.

        Arguments:

            'pairs' -- list of (name, value) pairs that will be marshaled.

            'ignore' -- list of names or single name that will be ignored.

        Result:

            List of (name, value) pairs ready to pass through request.
    """
    ignore = tuplify(ignore)

    result = []
    for name, value in pairs:
        if name in ignore or value is None:
            continue

        ftype = None
        subresult = []

        if isinstance(value, BooleanType):
            ftype = 'boolean'

        elif isinstance(value, IntType):
            ftype = 'int'

        elif isinstance(value, FloatType):
            ftype = 'float'

        elif isinstance(value, DateTime):
            ftype = 'date'

        elif isinstance(value, UnicodeType):
            ftype = 'ustring'

        elif isinstance(value, ResourceUid):
            ftype = 'uid'

        elif isinstance(value, MonikerBase):
            ftype = 'moniker'

        elif isinstance(value, MappingTypes):
            for k, v in value.items():
                subresult.append(('%s.%s:record' % (name, k), v))

        elif isinstance(value, SequenceTypes):
            if len(value):
                for v in value:
                    if isinstance(v, MappingTypes):
                        for k, v in v.items():
                            subresult.append(('%s.%s:records' % (name, k), v))
                    else:
                        subresult.append(('%s:list' % name, v))
            else:
                ftype = 'tokens'
                value = ''

        if ftype and name.find(':%s' % ftype) < 0:
            result.append(('%s:%s' % (name, ftype), value))
        elif subresult:
            result.extend(formatForRequest(subresult, ignore))
        else:
            result.append((name, value))

    return result

def registerVarFormat(id, format):
    assert isinstance(id, StringTypes), `id`
    assert callable(format), `format`

    _DT_var_special_formats[id] = format

class VarFormatters:

    def untaint(v, name='(Unknown name)', md=None):
        """
            'untaint' -- unquotes user-submitted values secured by ZPublisher
        """
        return str(v)

    def checked(v, name='(Unknown name)', md=None):
        """
            'checked' -- renders specific html attributes
        """
        return v and 'checked="checked"' or ''

    def selected(v, name='(Unknown name)', md=None):
        """
            'selected' -- renders specific html attributes
        """
        return v and 'selected="selected"' or ''

    def disabled(v, name='(Unknown name)', md=None):
        """
            'disabled' -- renders specific html attributes
        """
        return v and 'disabled="disabled"' or ''

    def readonly(v, name='(Unknown name)', md=None):
        """
            'readonly' -- renders specific html attributes
        """
        return v and 'readonly="readonly"' or ''

    def multiple(v, name='(Unknown name)', md=None):
        """
            'multiple' -- renders specific html attributes
        """
        return v and 'multiple="multiple"' or ''

    def jscript(v, name='(Unknown name)', md=None):
        """
            'jscript' -- escapes string values for use in JavaScript
        """
        return escapeJScript(v)

    def jscript_bool(v, name='(Unknown name)', md=None):
        """
            'jscript-bool' -- renders JavaScript boolean value
        """
        return v and 'true' or 'false'

    def strip(v, name='(Unknown name)', md=None):
        """
            'strip' -- removes surrounding whitespace in the value
        """
        return str(v).strip()

    def Class(v, name='(Unknown name)', md=None):
        """
            'class' -- outputs class atribute if value is a non-empty string
        """
        return v and ('class="%s"' % escapeHTML(v, True)) or ''

    def percent(v, name='(Unknown name)', md=None):
        """
            'percent' -- represents value in percent style
        """
        return '%d%%' % (float(v)*100)

    def rdate(v, name='(Unknown name)', md=None):
        """
            'rdate' -- represents date time value
        """
        if not isinstance(v, DateTime):
            v = DateTime(v)

        res = ''
        if not v.isCurrentDay():
           res += v.dd() + '&nbsp;'
           msg = md.get('msg',lambda s:s)
           res += msg(v.Mon()) + '&nbsp;'

        if not v.isCurrentYear():
           res += str(v.year()) + '&nbsp;'
        
        return res + v.TimeMinutes()

    def date(v, name='(Unknown name)', md=None):
        """
            'date' -- represents date value
        """
        if not isinstance(v, DateTime):
            v = DateTime(v)

        return v.strftime(getLanguageInfo(md['this'])['date_format'])

    def datetime(v, name='(Unknown name)', md=None):
        """
            'datetime' -- represents date value with time
        """
        if not isinstance(v, DateTime):
            v = DateTime(v)

        return v.strftime(getLanguageInfo(md['this'])['datetime_format'])

    def register(klass, context):
        for name, func in klass.__dict__.items():
            if name.startswith('_') or name is 'register':
                continue

            id = name.lower().replace('_', '-')
            context.registerVarFormat(id, func)

    register = classmethod(register)

def registerDTCommand( name, klass ):
    assert isinstance( name, StringTypes ), `name`
    assert isinstance( klass, ClassTypes ), `klass`

    global _DT_String
    _DT_String.commands[ name ] = klass

def registerDTInSorter( names, sorter ):
    if not isSequence( names ):
        names = [ names ]

    assert isinstance( sorter, (FunctionTypes, ClassTypes) ), `sorter`

    global _DT_In_sorters
    for name in names: 
       assert isinstance( name, StringTypes ), `name`
       _DT_In_sorters[ name ] = sorter

class MsgSorter:
    sorter = cmp

    def __init__(self, md):
        self.__msg = md.getitem('msg', 0)

    def __call__(self, str1, str2):
        msg = self.__msg
        return self.sorter( msg(str1), msg(str2) )

class MsgNoCaseSorter(MsgSorter):
    sorter = nocase

def registerConverter(id, converter):
    assert isinstance(id, StringTypes), `id`
    assert callable(converter), `converter`
    global _type_converters

    _type_converters[ id ] = converter

class currency: # (float): python 2.2
    """
    TODO: document this
          add currency type
          use Decimal here from python 2.4

    """
    def __init__(self, value, name=''):
        self.value = float(value) # may be here use abs function too???
        self.name = name # may be '$', 'rub'

    def __coerce__(self, other):
        return (self.value, other)

    def __float__(self):
        return self.value

    __hash__ = __float__

    def __cmp__(self, other):
        #if isinstance(other, currency):
        #    return cmp(self.value, other.value)
        coer = coerce(self.value, other)
        if coer is not None:
            res = cmp( *coer )
        else:
            res = -1
        #print '%s %s %s' %(`self`, ['==','>','<'][res], `other`)
        return res

    def __str__(self):
        return '%.2f%s%s' % (self.value, self.name and ' ' or '', self.name or '')

    def __repr__(self):
        return 'currency(%r, %r)' % (self.value, self.name)
        #return '<%s value="%s" at 0x%08X>' % (self.__class__.__name__, self.value, id(self))

    #def __call__(self):
    #    return float(self)

class RequestConverters:

    def __getattr__(self, name):
        global _type_converters

        if not _type_converters.has_key(name):
            raise AttributeError(name)

        return _type_converters[name]

    def currency(self, v):
        if isinstance(v, SequenceTypes):
            return map(self.currency, v)

        v = self.string(v).replace(',', '.', 1)

        if v:
            try: return currency(v)
            except ValueError:
                raise ValueError, (
                    "A currency-point number was expected in the value '%s'" %
                    escapeHTML(v)
                    )

        return currency(0)

    def float(self, v):
        if isinstance(v, SequenceTypes):
            return map(self.float, v)

        v = self.string(v).replace(',', '.', 1)

        if v:
            try: return float(v)
            except ValueError:
                raise ValueError, (
                    "A floating-point number was expected in the value '%s'" %
                    escapeHTML(v)
                    )

        return 0.

    def int(self, v):
        if isinstance(v, SequenceTypes):
            return map(self.int, v)

        if v:
            try: return int(float(v))
            except ValueError:
                raise ValueError, (
                    "A integer-point number was expected in the value '%s'" %
                    escapeHTML(v)
                    )

        return 0

    def sentences(self, v):
        v = self.string(v)
        return filter(None, map(str.strip, v.split(',')))

    def lines(self, v):
        if isinstance(v, SequenceTypes):
            return map(str, v)
        return self.text(v).splitlines()

    def boolean(self, v):
        if v == 'False': # support python 2.3
            return False

        return bool(v)

    def none(self, v):
        return v or None

##    def members(self, v):
##        return MembersSelection( tuplify(v) )

    # aliases:
    date_ = staticmethod(parseDate)
    datetime_ = staticmethod(parseDateTime)
    uid = staticmethod(parseUid)
    moniker = staticmethod(parseMoniker)
    time_period = staticmethod(parseTimePeriod)

    def register(self, context):
        for name in dir(self):
            if name.startswith('_') or name is 'register':
                continue

            context.registerConverter(name, getattr(self, name))

RequestConverters = RequestConverters()

def getFolderAnyway(context, path):
    """
        Gets folder located by path or creates it if it doesn't yet exist.
    """

    catalog = getToolByName(context, 'portal_catalog')
    lang = getToolByName(context, 'portal_membership').getLanguage()

    titles = path.split('/')
    path_array = [translit_string(title.strip(), lang) for title in titles]

    for i in range(len(path_array), 0, -1):
        results = catalog.unrestrictedSearch(
            id = path_array[i - 1],
            path = joinpath(path_array[:i]),
            implements = 'isContentStorage'
        )
        if results: break
    else:
        return None
 
    folder = results[0].getObject()

    for j in range(i, len(path_array)):
        id = path_array[j]
        folder.invokeFactory(
            type_name = 'Heading',
            category = 'Folder',
            id = id,
            title = titles[j]
        )
        folder = folder._getOb(id)

    return folder

def initialize( context ):

    context.register( registerVarFormat )
    context.register( registerDTCommand )
    context.register( registerDTInSorter ) 
    context.register( registerConverter )

    # default dtml-var formats
    VarFormatters.register(context)

    # default dtml-in sorters
    context.registerDTInSorter( 'cmp', cmp )
    context.registerDTInSorter( 'nocase', nocase )
    try: 
        from DocumentTemplate.DT_In import strcoll, strcoll_nocase
    except ImportError:
        pass
    else:
        context.registerDTInSorter( ['locale','strcoll'], strcoll )
        context.registerDTInSorter( ['locale_nocase','strcoll_nocase']
                                  , strcoll_nocase )
    context.registerDTInSorter( 'msg', MsgSorter )
    context.registerDTInSorter( 'msg_nocase', MsgNoCaseSorter )

    # 1. Registers new publisher's field type converters:
    #   'currency' -- money type
    #   'sentences' -- tokens separated by comma
    #
    # 2. Changes existing type converters:
    #   'float' -- accepts comma-separated float values
    #   'int' -- accepts float values

    RequestConverters.register(context)
