"""
Additional DTML tags.

    'GetMsgTag' -- 'dtml-msg' tag implementation

    'GetMessageTag' -- 'dtml-msgtext' tag implementation

    'RevisionTag' -- 'dtml-revision' tag implementation

$Editor: vpastukhov $
$Id: DTMLTags.py,v 1.29 2006/07/03 12:43:20 ypetrov Exp $
"""
__version__ = '$Revision: 1.29 $'[11:-2]

import re
from cgi import escape as escapeHTML
from types import ListType, StringType, IntType, FloatType

import Globals
from Acquisition import aq_base
from DocumentTemplate.DT_Util import InstanceDict, Eval, ParseError, \
        parse_params, name_param, namespace, render_blocks, safe_callable
from zLOG import LOG, INFO, ERROR
from ZPublisher.Converters import type_converters

from Products.Localizer.GettextTag import GettextTag

from Utils import escapeJScript
from PatternProcessor import PatternProcessor

class GetPatternTag:
    """
        Simple DTML tag for output of the processed strings.

        Format::

            <dtml-pattern "string" ptype=value [doc=object ...]>

        Arguments:

            'string' -- string to were processed by PatternProcessor

            'ptype' -- pattern type

            'doc' -- HTMLDocument object which requred for some patterns

        Result:

            Processed string.

        Examples:

            <dtml-pattern "../F_%D" ptype="folder_routing" doc="this()">

    """
    name = 'pattern'

    string = None
    expr = None
    ptype = None
    kw = None

    def __init__( self, args ):
        args = _parse_params( args, tag=self.name, compile_values=True )

        if args.has_key(''):
            self.string = args['']
            del args['']

        if args.has_key('expr'):
            self.expr = args['expr']
            del args['expr']

        if args.has_key('ptype'):
            self.ptype = args['ptype']
            del args['ptype']

        self.kw = args

    def render( self, md ):
        # process string
        #
        expr = self.expr

        if expr:
            if safe_callable( expr ):
                value = expr( md )
            else:
                value = md.getitem( expr, False )

            if hasattr( value, '__render_with_namespace__' ):
                text = value.__render_with_namespace__( md )
            elif safe_callable( value ):
                text = value()
            else:
                text = value

            if text is None:
                text = ''
            else:
                text = str(text).strip()

            if not text and self.string:
                text = self.string

        else:
            text  = self.string

        kw={}
        for k in self.kw.keys():
            kw[k] = self.kw[k](md)
        text = PatternProcessor.processString( text, fmt=self.ptype, **kw )

        return text

    __call__ = render


_linesre = re.compile( r'\s*?\n\s*\n\s*?' )
_spacesre = re.compile( r'\s+' )
_tagre = re.compile( r'<[^>]*?>' )


class GetMsgTag:
    """
        Simple DTML tag for output of the internationalized text messages.

        This tag is a non-block tag usually having a single argument -
        message text to be translated to the user's currently selected language.
        Messages may accept additional parameters, which are inserted
        in the text using '%(name)s' syntax.

        Translation are being looked up in the message catalog, which is
        acquired by 'msg' name from DTML namespace.  Before that continuous
        whitespace in the text is replaced with a single space character,
        leading and trailing whitespace is removed.

        Special HTML characters in the translated message text are quoted
        using HTML character entities.  Values of the parameters are NOT quoted.

        Format::

            <dtml-msg "text" [expr=expression] [name=value ...]>

        Arguments:

            'text' -- default (not translated) message text, also used
                      as a key to lookup translation in the message catalog

            'expr' -- optional DTML or Python expression, used to obtain default
                      message text; if expression evaluates to 'None' or empty
                      string, default message 'text' is used if present, otherwise
                      empty string is returned

            'translate' -- TODO

            'newlines' -- TODO

            'jscript' -- TODO

            'name=value' -- additional keyword arguments used as
                            the parameters for the message

        Result:

            Translated string.

        Examples::

            <dtml-msg "Thank you for choosing NauDoc!">

            <dtml-msg expr=Title>

            <dtml-msg "Default text" expr="getProperty('text')">

            <dtml-msg "Path of %(id)s is %(path)s" id=getId path="'/'.join(getPhysicalPath())">
    """
    name = 'msg'

    catalog = 'msg'
    message = None
    expr = None
    params = None
    translate = True
    escape = True
    newlines = True
    jscript = False

    def __init__( self, args ):
        args = _parse_params( args, tag=self.name, compile_values=True,
                              translate=1, newlines=1, jscript=1 )

        if args.has_key(''):
            text = args['']
            del args['']

            # collapse continuous whitespace
            text = _spacesre.sub( ' ', text.strip() )
            self.message = text

        if args.has_key('expr'):
            self.expr = args['expr']
            del args['expr']

        if args.has_key('msgparams'):
            self.params = args['msgparams']
            del args['msgparams']

        if self.message is None and self.expr is None:
            raise ParseError, ( 'Message or expression must be specified', self.name )

        if args.has_key('translate'):
            self.translate = int( args['translate'] )
            del args['translate']

        if args.has_key('jscript'):
            self.jscript = int( args['jscript'] )
            if self.jscript:
                self.newlines = False

        if args.has_key('newlines'):
            self.newlines = int( args['newlines'] )

        # TODO: id, catalog, add, lang, html_quote arguments
        self.data = args

    def render( self, md ):
        # translate message
        #
        expr = self.expr
        translate = True

        if expr:
            if safe_callable( expr ):
                value = expr( md )
            else:
                value = md.getitem( expr, False )

            if hasattr( value, '__render_with_namespace__' ):
                text = value.__render_with_namespace__( md )
            elif safe_callable( value ):
                text = value()
            else:
                text = value

            if text is None:
                text = ''
            else:
                text = str(text).strip()

            if not text:
                text = self.message

            elif self.translate:
                # text obtained from context needs to be reformatted
                text = _linesre.sub( '\a', text )  # mark paragraph delimiters
                text = _spacesre.sub( ' ', text )  # collapse odd whitespace
                text = text.replace( '\a', '\\n' ) # restore delimiters

            else:
                translate = False
        else:
            text  = self.message
            value = None

        if not text:
            return ''

        # lookup translation
        if translate:
            text = self.getTranslation( text, md, add=not expr )

        # escape HTML control characters
        if self.escape:
            text = escapeHTML( text, 1 )
            if self.newlines:
                text = text.replace( '\\n', '<br />\n' )
            else:
                text = text.replace( '\\n', '\n' )

        # escape special JavaScript characters
        if self.jscript:
            text = escapeJScript( text )

        if hasattr( value, '__render_parameters__' ):
            data = value.__render_parameters__( md )
        elif safe_callable( self.params ):
            data = self.params( md )
        elif self.params:
            data = md[ self.params ]
        else:
            data = None

        data = MsgDict( md, data )

        if self.data:
            # evaluate message parameters
            for name, expr in self.data.items():
                if safe_callable( expr ):
                    data[ name ] = str( expr(md) )
                elif type(expr) is StringType:
                    data[ name ] = str( md[expr] )

        # substitute variables
        if len(data):
            #print 'GetMsgTag.render', text, `data`
            text = text % data

        return text

    __call__ = render

    def getTranslation( self, text, md, add=True ):
        """
            Tries to get message catalog, caches it in TemplateDict
            and translates text
        """
        cache_key = '_msgcat_%s' % self.catalog
        try:
            catalog = getattr( md, cache_key, None) or md.getitem( self.catalog, 0 )
        except KeyError:
            LOG( '%s.render' % self.__class__.__name__
               , ERROR
               , "Message catalog '%s' not found" % self.catalog )
        else:
            if not hasattr(md, cache_key):
                #print "caching catalog", md.get('URL', None)
                setattr( md, cache_key, aq_base(catalog) )
            text = catalog.gettext( text )

        return text


class GetMessageTag( GettextTag ):
    """
        Block DTML tag for output of the internationalized text messages.

        This tag is a block tag usually used without arguments.
        The contents of the tag, which may also include other DTML tags,
        form a message text to be translated to the user's currently
        selected language.  Messages may accept additional parameters,
        which are inserted in the text using '%(name)s' syntax.  These
        parameters may be specified with 'data' argument or using
        'dtml-msgparam' subtags.

        Translation are being looked up in the message catalog, which is
        acquired by 'msg' name from DTML namespace.  Before that continuous
        whitespace in the text is replaced with a single space character,
        leading and trailing whitespace is removed.  If the text contains
        HTML tags, they are replaces with '%(n)s' substrings, where 'n'
        is a sequential number.  These substrings are then replaced back
        in the translated text.

        Special HTML characters in the translated message text are quoted
        using HTML character entities.  Values of the parameters are NOT quoted.

        Format::

            <dtml-msgtext [data=expression] [catalog="msg"]>
            text
            <dtml-msgparam name>
            value
            </dtml-msgtext>

        Arguments:

            'text' -- default (not translated) message text, also used
                      as a key to lookup translation in the message catalog

            'data' -- optional DTML or Python expression, must evaluate
                      to a dictionary containing parameters for the message

            'catalog' -- optional identifier of the message catalog;
                         'msg' is the default

            'name' -- name of additional parameter for the message

            'value' -- value of additional parameter for the message

        Result:

            Translated string.

        Examples::

            <dtml-msgtext>
            Please specify global parameters in
            <a href="&dtml-portal_url;/reconfig_form">
            the portal configuration</a>.
            </dtml-msgtext>

            msgid "Please specify global parameters in %(1)s
            the portal configuration%(2)s."

            <dtml-msgtext data="{'baz':'value of baz'}">
            foo is %(foo)s, bar is %(bar)s, baz is %(baz)s
            <dtml-msgparam foo>
            value of foo
            <dtml-msgparam bar>
            value of bar
            </dtml-msgtext>
    """
    name = 'msgtext'
    blockContinuations = ['msgparam']

    escape = 1
    newlines = 1
    jscript = 0

    def __init__( self, blocks ):
        GettextTag.__init__( self, blocks )

        if self.catalog is None: self.catalog = 'msg'
        self.blocks = data = []

        # reset data to overcome Localizer's expansion
        self.mdata = self.data
        self.data  = None

        for tname, args, section in blocks[1:]:
            args = parse_params( args, name='' )
            name = name_param( args,'msgparam' )
            data.append( (name, section.blocks) )

    def render( self, md ):
        ns = namespace(md)[0]
        md._push( InstanceDict(ns, md) )
        text = render_blocks( self.section, md )
        md._pop(1)

        data = {}
        match = _tagre.search( text )
        while match:
            data[ str( len(data)+1 ) ] = match.group()
            text  = text[ :match.start() ] + ( '%%(%d)s' % len(data) ) + text[ match.end(): ]
            match = _tagre.search( text, match.start() )

        # mark empty lines as paragraph delimiters
        text = _linesre.sub( '\a', text.strip() )
        # collapse continuous whitespace
        text = _spacesre.sub( ' ', text )
        # restore empty lines between paragraphs
        text = text.replace( '\a', '\\n' )

        # lookup translation
        text = self.getTranslation( text, md )

        if self.mdata is not None:
            # simple variables
            mdata = self.mdata.eval( md )
            try:
                data.update( mdata )
            except TypeError: # python < 2.2
                for key in mdata.keys():
                    data[ key ] = mdata[ key ]

        # escape HTML control characters
        if self.escape:
            text = escapeHTML( text, 1 )
            if self.newlines:
                text = text.replace( '\\n', '<br />\n' )
            else:
                text = text.replace( '\\n', '\n' )

        # TODO escape special JavaScript characters
        #if self.jscript:
        #    text = escapeJScript( text )

        # block variables
        for name, section in self.blocks:
            data[ name ] = render_blocks( section, md ).strip()

        # substitute variables
        if len(data):
            #print 'GetMessageTag.render', `data`
            text = text % data

        return text

    __call__ = render

    getTranslation = GetMsgTag.getTranslation.im_func


class RevisionTag:
    """
        DTML revision tag is used to specify DTML file version
        using CVS keyword expansion.

        The contents if the tag is a single CVS Revision keyword.
        The tag must be placed near the beginning of the file.

        Example::

            <dtml-revision $Revision: 1.29 $>
    """
    name = 'revision'
    isRevisionTag = 1

    def __init__( self, args ):
        self.revision = args = args.strip()

        if args.startswith('$Revision:'):
            self.version = args[ 11:-2 ]
        else:
            self.version = args

    def __call__( self, md ):
        return ''

# take care that Id in pattern is not expanded by CVS
_rcs_id_keyword = re.compile( r'\$(?:Id):([^$]+?)\$' )

class DebugCommentTag:
    """
        DTML comment tag replacement that extracts CVS Id tag from
        the comment text and outputs it (for debugging purposes).
    """
    name = 'comment'
    blockContinuations = ()
    text = ''

    def __init__( self, blocks, rcs_id_keyword=_rcs_id_keyword  ):
        blocks = blocks[0][2].blocks
        if not ( blocks and type(blocks[0]) is StringType ):
            return

        match = rcs_id_keyword.search( blocks[0] )
        if match:
            self.text = '<!-- %s -->\n' % match.group(1).strip()

    def __call__( self, md ):
        return self.text


_unparmre  = re.compile( r'([^\s="]+)\s*' )
_qunparmre = re.compile( r'"([^"]*)"\s*' )
_parmre    = re.compile( r'([^\s="]+)=([^\s="]+)\s*' )
_qparmre   = re.compile( r'([^\s="]+)="([^"]*)"\s*' )


def _parse_params( text, result=None, tag_name='', compile_values=False,
                   unparmre=_unparmre, qunparmre=_qunparmre,
                   parmre=_parmre, qparmre=_qparmre, **params ):

    text = text.strip()
    if result is None:
        result = {}

    while text:
        match = None

        while not match:
            match = parmre.match( text ) # name=expr
            if match:
                name = match.group(1)
                expr = match.group(2)
                conv = type_converters.get( type( params.get(name) ).__name__ )
                if conv:
                    expr = conv( expr )
                break

            match = qparmre.match( text ) # name="expr"
            if match:
                name, expr = match.group(1), match.group(2)
                if compile_values:
                    expr = _compile_expr( expr, tag_name )
                break

            match = unparmre.match( text ) # name
            if match:
                name = match.group(1)
                if result:
                    expr = params.get( name )
                else:
                    name, expr = '', name
                break

            match = qunparmre.match( text ) # "text"
            if match:
                name, expr = '', match.group(1)
                if result:
                    raise ParseError, ( 'Invalid attribute value, "%s"' % expr, tag_name )
                break

            raise ParseError, ( 'Invalid parameter: "%s"' % text, tag_name )

        if result.has_key( name ):
            p = params[ name ]
            if type(p) is not ListType or p:
                raise ParseError, ( 'Duplicate values for attribute "%s"' % name, tag_name )

        result[ name ] = expr
        text = text[ match.end(): ]

    return result

def _compile_expr( text, tag ):
    try:
        return Eval( text ).eval
    except SyntaxError, exc:
        raise ParseError, ( 'Syntax error:\n%s\n' % exc[0], tag )


class MsgDict:
    """
        Smart DTML TemplateDict and DictInstance replacement
        for rendering parametric messages and object monikers.
    """

    # for TemplateDict emulation
    guarded_getattr = None
    guarded_getitem = None

    def __init__( self, md=None, source=None ):
        self.__md = md
        self.__source = source
        self.__data = {}

    def __getitem__( self, key, subcall=None ):
        # returns requested item
        # used for parameter interpolation in tag's render method
        #print 'MsgDict.getitem', id(self), key, subcall
        try:
            # first try cached value, then ask source mapping
            try:
                value = self.__data[ key ]
            except KeyError:
                if self.__source is None:
                    raise
                value = self.__data[ key ] = self.__source[ key ]

        except KeyError:
            # check whether subitem is requested (key="object.subObject")
            i = key.rfind('.')
            if i < 0:
                raise # not subitem

            # get subitem from its parent object and cache it
            parent, child = key[:i], key[i+1:]
            value = getattr( self.__getitem__( parent, 1 ), child )
            if safe_callable( value ):
                value = value()
            self.__data[ key ] = value

        # the item is found and is in cache at this time
        if hasattr( value, '__of__' ):
            try:
                value = value.__of__( self ) # loads moniker
            except TypeError:
                pass

        if subcall:
            # in call for subitem - no need to render
            return value

        # in top-level call - return rendered object
        if hasattr( value, '__render_with_namespace__' ):
            return value.__render_with_namespace__( self.__md or self )

        #elif safe_callable( value ):
        #    if getattr( aq_base(value), 'isDocTemp', False ):
        #        return value( None, self.__md or self )
        #    return str( value() )

        elif type(value) in [IntType,FloatType]:
            return value

        elif value is None:
            return ''
        else:
            return escapeHTML( str(value), 1 )

    def __setitem__( self, key, value ):
        # used to add message parameters
        #print 'MsgDict.setitem', id(self), key, `value`
        self.__data[ key ] = value

    def __getattr__( self, name ):
        # emulates DictInstance behaviour but does not call objects
        #print 'MsgDict.getattr', id(self), name
        if self.__md is None:
            raise AttributeError, name
        try:
            return self.__md.getitem( name, 0 )
        except KeyError:
            raise AttributeError, name

    def __nonzero__( self ):
        return self.__md is not None or self.__source is not None

    def __len__( self ):
        if self.__source is not None:
            return len( self.__source )
        else:
            return len( self.__data )

    def __repr__( self ):
        return repr( self.__data )

    __str__ = __repr__


def initialize( context ):
    context.registerDTCommand( GetPatternTag.name, GetPatternTag )
    context.registerDTCommand( GetMsgTag.name, GetMsgTag )
    context.registerDTCommand( GetMessageTag.name, GetMessageTag )
    context.registerDTCommand( RevisionTag.name, RevisionTag )

    if __debug__ and Globals.DevelopmentMode:
        context.registerDTCommand( DebugCommentTag.name, DebugCommentTag )
