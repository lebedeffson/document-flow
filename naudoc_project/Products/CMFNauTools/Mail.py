"""
E-mail related classes:

Charset -- national character set convertor class

MailMessage -- representation of the RFC-822 e-mail message class

MailServerBase -- abstract base class for all incoming and outgoing
                  mail servers

$Editor: vpastukhov $
$Id: Mail.py,v 1.67 2005/11/30 17:13:27 ikuleshov Exp $
"""
__version__ = '$Revision: 1.67 $'[11:-2]

import re
from copy import copy
from string import capitalize
from types import StringType, UnicodeType, TupleType, ListType, DictType
from sys import exc_info
from urllib import splittype, splithost

import email.base64MIME, email.quopriMIME
from email import __version__ as _email_version
from email.Charset import Charset as _Charset, \
        BASE64, QP, ALIASES, CODEC_MAP
from email.Encoders import _bencode
from email.Generator import _is8bitstring
from email.Header import Header as _Header, ecre as _header_ecre, \
        USASCII as _charset_USASCII, UTF8 as _charset_UTF8
#from email.Header import decode_header
from email.Message import Message as _Message, _formatparam
from email.Parser import Parser
from email.Utils import getaddresses, specialsre, escapesre
from email.base64MIME import body_encode as base64_encode
from email.quopriMIME import body_encode as quopri_encode

import Globals
from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from AccessControl.Role import RoleManager
from Acquisition import aq_parent, aq_base, aq_get
from BTrees.OOBTree import OOBTree
from Globals import DTMLFile
from zLOG import LOG, TRACE, ERROR

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Config, Exceptions
from Monikers import ContentMoniker
from SimpleObjects import InstanceBase
from Utils import InitializeClass, getLanguageInfo, cookId, \
        updateLink, isCharsetKnown, recode_string, joinpath


_meta_ctype_rec  = re.compile( r'<meta\b[^>]+\bhttp-equiv="?Content-Type"?[^>]*>', re.I )


class Charset( _Charset ):
    """
        National character set convertor.

        Attributes:

            'input_charset' -- name of the source encoding

            'input_changed' --  a flag used by the mail message parser

            'input_codec' -- name of the codec from input charset to Unicode

            'output_charset' -- name of the target encoding

            'output_codec' -- name of the codec from Unicode to output charset
    """

    input_changed = None

    def __init__( self, input_charset=None, output_charset=None ):
        """
            Initializes new 'Charset' instance.

            Arguments:

                'input_charset' -- optional source encoding name,
                        by default is set to the charset corresponding
                        to 'Config.DefaultLanguage' value

                'output_charset' -- optional target encoding name,
                        default value is selected from 'CHARSETS' mapping
                        (see 'email.Charset' module) using 'input_charset'
                        value as the lookup key
        """
        if input_charset is None:
            input_charset = Config.MailCharset

        _Charset.__init__( self, input_charset )

        if output_charset is not None:
            output_charset = output_charset.lower()
            master_charset = ALIASES.get( output_charset, output_charset )
            self.output_charset = output_charset
            self.output_codec   = CODEC_MAP.get( master_charset, self.input_codec )

    def change_input_charset( self, charset ):
        """
            Changes source encoding and input codec.

            Arguments:

                'charset' -- new source encoding name
        """
        master_charset = ALIASES.get( charset, charset )
        if master_charset != self.input_charset:
            self.input_changed = 1
            self.input_charset = charset
            self.input_codec   = CODEC_MAP.get( master_charset, self.input_codec )

    def convert( self, text ):
        """
            Converts a string from source to target encoding.

            Arguments:

                'text' -- the string to be converted

            Result:

                String in the target encoding.
        """
        if self.input_codec != self.output_codec:
            return unicode( text, self.input_codec, 'ignore' ).encode( self.output_codec, 'ignore' )
        else:
            return text

    def body_encode( self, text, convert=1 ):
        """
            Encodes a string using body encoding for the input charset.

            Available body encodings are *base64*, *quoted-printable*,
            *7bit* and *8bit*.  The actual encoding used is selected
            from 'CHARSETS' mapping (see 'email.Charset' module) depending
            on the source encoding.

            Arguments:

                'text' -- the string to be encoded

                'convert' -- boolean flag, indicating that the string
                             must be first converted to the target encoding;
                             true by default

            Result:

                Body-encoded string.
        """
        if convert:
            text = self.convert(text)
        # 7bit/8bit encodings return the string unchanged (module conversions)
        if self.body_encoding is BASE64:
            return base64_encode(text)
        elif self.body_encoding is QP:
            return quopri_encode(text)
        else:
            return text

    def clone( self ):
        """
            Returns a copy of this object.

            Result:

                New 'Charset' object with 'input_changed' attribute
                reset to 'None' and all other attribute values copied.
        """
        new = copy( self )
        try: del new.input_changed
        except AttributeError: pass
        return new


class Header( _Header ):
    """
        Internet mail message header.
    """

    if _email_version >= '2.5':

        def __init__( self, s=None, charset=None, maxlinelen=None,
                      header_name=None, continuation_ws=' ', errors='ignore' ):
            # default error handling is changed from 'strict' to 'ignore'
            _Header.__init__( self, s, charset, maxlinelen, header_name, continuation_ws, errors )

    else:

        def append( self, s, charset=None, errors='ignore' ):
            """
                Appends a string to the MIME header.

                This method is entirely copied from 'email.Header' module,
                with error handling for character encoding set to 'ignore'.
            """
            if charset is None:
                charset = self._charset
            elif not isinstance(charset, _Charset):
                charset = _Charset(charset)
            if charset <> '8bit':
                if isinstance(s, StringType):
                    incodec = charset.input_codec or 'us-ascii'
                    ustr = unicode(s, incodec)
                    outcodec = charset.output_codec or 'us-ascii'
                    ustr.encode(outcodec, errors)
                elif isinstance(s, UnicodeType):
                    for charset in _charset_USASCII, charset, _charset_UTF8:
                        try:
                            outcodec = charset.output_codec or 'us-ascii'
                            s = s.encode(outcodec, errors)
                            break
                        except UnicodeError:
                            pass
                    else:
                        assert False, 'utf-8 conversion failed'
            self._chunks.append((s, charset))


class MailMessage( _Message ):
    """
        Internet mail message class (RFC 822, 2822).

        See 'email' package description for additional information.

        The most important difference of this implementation is advanced
        support for automatic text convertion between character sets used
        in electronic mail system and in Web portal documents.

        Another significant concept is an introduction of the *message
        body* which contains the main text of the message.  This is the
        message object itself for a simple message or the first part
        of the multipart message.
    """

    """
        Some details on the character set handling.

        Message._charset -- Charset of the message body.  Also, message
                parts have their own charsets for the bodies.

        Header._charset -- Charset of the individual header. More over,
                the header may have many chucks each having different charset.

        Message._hint_charset -- Default charset of the message; this is
                used in the case when charset of some header or body part
                is not specified explicitly.

        When parsing incoming message (with from_text method), source text
        is scanned till the first occurence of Content-Type header having
        valid charset parameter is found.  This charset is used as an input
        encoding for the hint charset, which is shared between top-level
        Message object and all the initial parts through the one the charset
        was found in.  Like that, default headers encoding (used when actual
        charset is not known) of the multipart message appears the same as
        encoding of the first textual part.

        During parsing, unencoded headers share hint charset of the part
        they are contained in.  Likewise, when adding headers to the message
        or part without specifying a charset, the relevant hint charset is
        shared between them by default.

        Hint charset is also used to recode headers and bodies in various
        get-like methods.
    """

    # default attribute values
    _in_parser    = None
    _hint_charset = None

    def __init__( self, ctype=None, multipart=None, source=None, charset=None, to_mail=None ):
        """
            Initializes new mail message.

            If the message is created as multipart, additional part for
            the main body is created with 'ctype' type and is attached
            to the multipart object.

            Positional arguments:

                'ctype' -- optional MIME content type for the body
                        of the message; may be changed later

            Keyword arguments:

                'multipart' -- if evaluated to truth, the message is created
                        as multipart with subtype set to the value of this
                        argument ('mixed' is used if it's not a string)

                'source' -- RFC 822 text (with headers and body) that
                        is parsed into the body of this message

                'charset' -- 'Charset' object used for character encoding
                        conversion
        """
        _Message.__init__( self )
        self._hint_charset = charset

        if multipart:
            multipart = type(multipart) is StringType and multipart.lower() or 'mixed'
            body = self.__class__( ctype, charset=charset )
            self.set_type( 'multipart/' + multipart )
            self.attach( body )
            self.epilogue = '' # ensure newline at EOF

        else:
            body = self
            if ctype:
                body.set_type( ctype )

#        if charset:
#            body.set_charset( charset )

        if source:
            # TODO: set initial charset to '8bit' when converting from mail
            body.from_text( source.lstrip(), charset, to_mail=to_mail )

    def __setitem__( self, name, value ):
        """
            Adds a field to the message header.

            If the value contains 8bit characters, new 'Header' object
            is created with the same charset parameters as given in the
            constructor, thus enabling automatic charset converions for
            the field contents.

            Arguments:

                'name' -- the name of the field

                'value' -- contents of the field
        """
        name = '-'.join( map( capitalize, name.strip().split('-') ) )
        hint = self._hint_charset

        if type(value) is TupleType and type(value[1]) is DictType:
            value, params = value
        else:
            params = {}

        if type(value) is TupleType:
            # (name, address) pair
            value = formataddr( value, hint )

        is8bit = _is8bitstring( value )
        if is8bit or ( params and isinstance(value, StringType) ):
            value = Header( value, is8bit and hint or None )

        if isinstance( value, StringType ):
            self.add_header( name, value, **params )

        else:
            for k, v in params.items():
                value.append( '; ' )
                value.append( '%s="%s"' % (k.replace('_','-'), recode_string(v, hint)), '8bit' )

                # XXX the right way but not supported by Outlook
                #if _is8bitstring( v ):
                #    v = (hint.output_charset, None, recode_string(v, hint))
                #value.append( '; ' )
                #value.append( _formatparam( k.replace('_','-'), v ) )

            self._headers.append( (name, value) )

        # this is a workaround for charset problems
        # with badly formed cyrillic message headers
        if self._in_parser and self._hint_charset and not self._charset \
                           and name.lower() == 'content-type':
            charset = self.get_content_charset()
            if isCharsetKnown( charset ):
                self._hint_charset.change_input_charset( charset )

    def set_header( self, name, value, **params ):
        """
            Sets a header field value and parameters.

            This method basically works by removing existing headers
            with the same name and the calling '__setitem__' method.

            Positional arguments:

                'name' -- the name of the field

                'value' -- contents of the field

            Keyword arguments:

                '**params' -- additional field parameters

            Result:

                Value of the new header.
        """
        self.remove_header( name )
        self[ name ] = params and (value, params) or value
        return self._headers[-1][1]

    def remove_header( self, *names ):
        """
            Deletes all occurrences of the specified headers.

            Arguments:

                '*names' -- the list of the header names
        """
        for name in names:
            del self[ name.strip() ]

    def get( self, name, default=None, decode=None, maxlen=None ):
        """
            Returns a header field value.

            Positional arguments:

                'name' -- the name of the field

                'default' -- default value to return if the requested
                        field does not exist in the header; 'None' if
                        not given

            Keyword arguments:

                'decode' -- if true, the value is decoded and converted
                        to the target character set, otherwise (default)
                        the value is returned as-is

                'maxlen' -- currently not implemented

            Result:

                Value of the named field or default value.

            Note:

                See 'email' package for additional information.
        """
        header = _Message.get( self, name, default )

        # XXX a hack for _get_params_preserve - calls us with default=[]
        # always decode the field cause it does not support Header objects
        decode = decode or type(default) is ListType

        if header is default or not decode:
            return header

        # TODO implement maxlen
        return recode_header( header, self._hint_charset )

    def get_all( self, name, default=Missing, decode=None ):
        """
            Returns a list of all values for the named field, in case
            there are multiple fields with the same name in the message.

            Positional arguments:

                'name' -- the name of the field

                'default' -- default value to return if the requested
                        field does not exist in the header; empty list
                        if not given

            Keyword arguments:

                'decode' -- if true, the values are decoded and converted
                        to the target character set, otherwise (default)
                        the values are returned as-is

            Result:

                A list of values of the named field or default value.

            Note:

                See 'email' package for additional information.
        """
        headers = _Message.get_all( self, name, default )

        if headers is default or not decode:
            if default is Missing:
                return []
            return headers

        charset = self._hint_charset
        return [ recode_header( header, charset ) for header in headers ]

    def items( self, decode=None ):
        """
            Returns all the message headers as a list of name-value pairs.

            Keyword arguments:

                'decode' -- if true, the values are decoded and converted
                        to the target character set, otherwise (default)
                        the values are returned as-is

            Result:

                A list of header values.

            Note:

                See 'email' package for additional information.
        """
        items = _Message.items( self )
        if not decode:
            return items

        charset = self._hint_charset
        return [ (name, recode_header(value, charset)) for name, value in items ]

    def get_param( self, param, default=None, header='content-type', unquote=1, decode=None ):
        """
            Returns the parameter value of the header field.

            Positional arguments:

                'param' -- the name of the parameter

                'default' -- default value to return if the requested
                        parameter does not exist in the field; 'None'
                        if not given

                'header' -- the name of the field to search the parameter
                        in; by default 'Content-Type' field is searched

            Keyword arguments:

                'unquote' -- if true (default) the value is unquoted

                'decode' -- if true, the value is decoded and converted
                        to the target character set, otherwise (default)
                        the value is returned as-is

            Result:

                Value of the named parameter or default value.

            Note:

                See 'email' package for additional information.
        """
        param = _Message.get_param( self, param, default, header, unquote )

        if type(param) is TupleType:
            return '' # TODO

        #if param is default or not decode:
        #    return param

        # XXX why is this commented out???
        #return recode_header( param, self._hint_charset )

        # XXX _get_params_preserve does not support Header objects
        return param

    def get_filename( self, default=None, decode=None ):
        """
            Returns the filename associated with the payload if present.

            The filename is determined by first looking for parameter
            'filename' in the 'Content-Disposition' header and then
            for parameter 'name' in the 'Content-Type' header.

            Positional arguments:

                'default' -- default value to return if the filename
                        canot be determined; 'None' if not given

            Keyword arguments:

                'decode' -- if true, the filename is decoded and converted
                        to the target character set, otherwise (default)
                        the value is returned as-is

            Result:

                Filename string or default value.
        """
        return self.get_param( 'filename', None, 'content-disposition', decode=decode ) \
            or self.get_param( 'name', default, 'content-type', decode=decode )

    def set_payload( self, payload, charset=None ):
        """
            Sets message payload (message contents) to the given data.

            For 'text/html' content type, '<meta http-equiv="Content-Type">'
            tag in the HTML header is added or modified so that its 'charset'
            parameter corresponds to the 'output_charset' value of the
            associated 'Charset' object.

            Non-textual contents is encoded using 'base64' algorithm with
            'Content-transfer-encoding' header set accordingly.

            Arguments:

                'payload' -- message data

                'charset' -- optional character set of the data
                        for text messages

            Note:

                See 'email' package for additional information.
        """
        if self.is_text():
            if not ( charset or self.get_content_charset() ) and _is8bitstring( payload ):
                charset = self._hint_charset

            if isinstance( charset, StringType ):
                hint = self._hint_charset
                charset = Charset( charset, hint and hint.output_charset or None )

            if charset:
                # actual transfer encoding is determined by body_encoding of the Charset object
                self.remove_header( 'content-transfer-encoding' )

            if self.get_subtype() == 'html':
                # fix text/html with "meta http-equiv=Content-Type"
                if charset:
                    meta = '<meta http-equiv="Content-Type" content="text/html; charset=%s">' % charset.output_charset
                else:
                    meta = ''
                payload = _meta_ctype_rec.sub( meta, payload, 1 )

        elif not self._in_parser:
            self.set_header( 'content-transfer-encoding', 'base64' )
            payload = _bencode( payload )

        _Message.set_payload( self, payload, charset )

    def get_payload( self, index=None, decode=None ):
        """
            Returns the payload (contents) of the message.

            Positional arguments:

                'index' -- for multipart message this is a number
                        (starting from 0) of the part to return (optional)

            Keyword arguments:

                'decode' -- if true, the textual contents is decoded and
                        converted to the target character set, otherwise
                        (default) the contents is returned as-is

            Result:

                Message contents as a string, or list of parts if the message
                is multipart and 'index' is not given.

            Note:

                See 'email' package for additional information.
        """
        if self.is_multipart():
            return _Message.get_payload( self, index, 0 )

        text = _Message.get_payload( self, index, decode=decode )

        if decode:
            if text is None:
                text = ''
            elif self.is_text() and text:
                enc = self.get_content_charset()
                if enc:
                    text = recode_string( text, self._hint_charset, enc_from=enc )

        return text

    def attach( self, payload, inline=None, filename=None, cid=None, location=None ):
        """
            Adds an attachment to the current payload.

            Note:

                See 'email' package for additional information.
        """
        if payload._hint_charset is None:
            payload._hint_charset = self._hint_charset

        if not ( inline is None and filename is None ):
            inline = inline and 'inline' or 'attachment'

        if filename:
            payload.set_header( 'content-disposition', inline, filename=filename )

        elif inline:
            payload.set_header( 'content-disposition', inline )

        if cid:
            payload.set_header( 'content-id', '<%s>' % cid )

        if location:
            payload.set_header( 'content-location', location )

        _Message.attach( self, payload )

    def get_body( self ):
        """
            Return the main body of the message.

            The body object contains the main text of the message.
            This may be the message object itself for a simple message
            or the first part of the multipart message.

            Result:

                'MailMessage' object.
        """
        if not self.is_multipart():
            return self
        return self.get_payload(0)

    def is_text( self ):
        """
            Checks whether message content type is text.

            Result:

                Truth if the content type is 'text/*'.
        """
        return self.get_main_type() == 'text'

    def from_text( self, text, charset=None, to_mail=None ):
        """
            Parses RFC 822 text into the message.

            Positional arguments:

                'text' -- source RFC 822 text (with headers and body)

            Keyword arguments:

                'charset' -- 'Charset' object used for character encoding
                        conversion

            Result:

                This object.
        """
        self._in_parser = 1
        if charset is not None:
            self._hint_charset = charset
#            self.set_charset( None )

        if Globals.DevelopmentMode:
            # debugging DTML comment tag inserts CVS Id
            text = re.sub( r'^<!--\s*(.*?)\s*-->\s*',
                           r'X-%s-Template-Id: \1\n' % Config.MailerName, text, 1 )

        Parser( self._factory ).parsestr( text )

        for part in self.walk():
            part._in_parser = 0

        if 'content-type' not in self:
            self.set_type( 'text/plain' )
            self.set_charset( self._hint_charset )

        if not self.get_charset() and to_mail:
            self.set_charset( self._hint_charset )

        return self

    def _factory( self ):
        # class factory hacked for the MIME parser.
        if self._in_parser == 1:
            new = self
        else:
            new = self.__class__()
            new._in_parser = 1

        charset = self._hint_charset
        if charset and charset.input_changed:
            charset = charset.clone()
        new._hint_charset = charset

        self._in_parser += 1

        return new


class MailServerBase( InstanceBase, RoleManager ):
    """
        Abstract base class for the mail services.
    """
    _class_version = 1.34

    security = ClassSecurityInfo()

    security.declareProtected( ZopePermissions.change_configuration, 'manage_changeProperties' )
    security.declareProtected( ZopePermissions.change_configuration, 'manage_editProperties' )
    security.declareProtected( ZopePermissions.change_configuration, 'manage_mailForm' )

    manage_options = (
                { 'label' : 'Mail', 'action' : 'manage_mailForm', },
            ) + \
            InstanceBase.manage_options + \
            RoleManager.manage_options

    manage_mailForm = DTMLFile( 'dtml/manageMailServer', globals() )

    _properties = InstanceBase._properties + (
            {'id':'host',         'type':'string', 'mode':'w'},
            {'id':'port',         'type':'int',    'mode':'w'},
            {'id':'min_interval', 'type':'int',    'mode':'w'},
        )

    index_html = None

    # default attribute values
    protocol = None
    default_host = ''
    default_port = None
    min_interval = 1

    _v_conn = None

    def __init__( self, id, title='', host=None, port=None ):
        """
            Initialize new instance.

            Arguments:

                'id' -- identifier of the new object

                'title' -- optional title of the new object, empty
                        string by default

                'host' -- address of the host where the server
                        is running

                'port' -- optional port number on which the server
                        is listening for connections

        """
        InstanceBase.__init__( self, id, title )
        self.host = (host is not None) and str(host) or self.default_host
        self.port = (port is not None) and int(port) or self.default_port
        self.catalog = OOBTree()

    def _p_deactivate( self ):
        # put persistent object into ghost state

        if self._v_conn:
            # ignore deactivate if connection is alive
            try:    self._v_conn.noop()
            except: pass
            else:   return None

            # close broken connection
            try:    self._disconnect()
            except: pass

        return InstanceBase._p_deactivate( aq_base(self) )

    security.declarePrivate( 'open' )
    def open( self ):
        """
            Opens mail session.
        """
        if self._v_conn:
            self.close()

        if not self.address():
            raise Exceptions.SimpleError( 'mail.server_not_configured' )

        try:
            self._connect()
        except:
            LOG( '%s.open' % self.__class__.__name__, ERROR,
                 '[%s] connection failed' % self.address(), error=exc_info() )
            raise

    security.declarePrivate( 'close' )
    def close( self ):
        """
            Closes mail session.
        """
        if not self._v_conn:
            return

        try:
            self._disconnect()
        except:
            LOG( '%s.close' % self.__class__.__name__, ERROR,
                 '[%s] disconnect error' % self.address(), error=exc_info() )

        self._v_conn = None

    security.declarePrivate( 'address' )
    def address( self, host=None, port=None ):
        """
            Returns or changes hostname and port of the server.

            Arguments:

                'host' -- address of the host where the server
                        is running

                'port' -- optional port number on which the server
                        is listening for connections

            Result:

                Server address string formatted as '"host:port"'.
        """
        if host is not None:
            parts = str( host ).split( ':', 1 )
            self.host = parts[0]
            if len(parts) > 1:
                self.port = int( parts[1] )

        if port is not None:
            self.port = int( port )

        if not self.host or self.port == self.default_port:
            return self.host

        return '%s:%s' % (self.host, self.port)

    def _connect( self ):
        """
            Opens connection to the server.

            To be implemented by the subclass.
        """
        raise NotImplementedError

    def _disconnect( self ):
        """
            Closes connection to the server.

            To be implemented by the subclass.
        """
        raise NotImplementedError

    security.declarePrivate( 'getInputCharset' )
    def getInputCharset( self, lang=None ):
        """
            Returns 'Charset' instance that can be used to decode
            incoming mail for this server.

            Arguments:

                'lang' -- optional language code used to determine target
                        character set; if not given, default language
                        of the portal is used

            Result:

                'Charset' object.
        """
        langinfo = getLanguageInfo( lang or self )
        return Charset( langinfo['mail_charset'], langinfo['python_charset'] )

    security.declarePrivate( 'getOutputCharset' )
    def getOutputCharset( self, lang=None ):
        """
            Returns 'Charset' instance that can be used to encode
            outgoing mail for this server.

            Arguments:

                'lang' -- optional language code used to determine source
                        character set; if not given, default language
                        of the portal is used

            Result:

                'Charset' object.
        """
        langinfo = getLanguageInfo( lang or self )
        return Charset( langinfo['python_charset'], langinfo['mail_charset'] )

    security.declarePrivate( 'createMessage' )
    def createMessage( self, *args, **kw ):
        """
            Creates a new mail message instance.

            Arguments:

                '*args', '**kw' -- arguments for the 'MailMessage'
                        constructor

            Result:

                'MailMessage' object.
        """
        return MailMessage( *args, **kw )

    security.declarePrivate( 'registerAccount' )
    def registerAccount( self, object, name, force=0 ):
        """
            Registers object's account name.
        """
        name = name and name.strip().lower()
        if not name:
            raise Exceptions.SimpleError( 'mail.empty_login_name' )

        try:
            uid = object.getUid()
        except AttributeError:
            uid = joinpath( object.getPhysicalPath() )

        old = self.catalog.get( name )
        if old is not None:
            if uid == old:
                return
            elif not force:
                raise Exceptions.SimpleError( 'mail.duplicate_account',
                                              name=name, folder=ContentMoniker(old) )

        self.catalog[ name ] = uid

    security.declarePrivate( 'unregisterAccount' )
    def unregisterAccount( self, object, name, force=0 ):
        """
            Unregisters object's account name.
        """
        name = name and name.strip().lower()
        if not name:
            return

        try:
            uid = object.getUid()
        except AttributeError:
            uid = joinpath( object.getPhysicalPath() )

        old = self.catalog.get( name )
        if old is None:
            return

        if uid == old or force:
            del self.catalog[ name ]
#        else:
#            raise Exceptions.SimpleError( 'mail.duplicate_account',
#                                          name=name, folder=ContentMoniker(old) )

    security.declarePrivate( 'isAccountRegistered' )
    def isAccountRegistered( self, name ):
        """
            Checks whether account is alreay registerred.
        """
        name = name and name.strip().lower()
        if not name:
            return None
        return self.catalog.has_key( name )

    security.declareProtected( ZopePermissions.change_configuration, 'listAccounts' )
    def listAccounts( self ):
        # returns a list of all registered accounts
        accounts = []
        tool = getToolByName( self, 'portal_catalog' )

        for name, uid in self.catalog.items():
            result = tool.searchResults( nd_uid=uid )
            result = result and result[0] or None
            accounts.append( (name, result) )

        return accounts

    security.declareProtected( ZopePermissions.change_configuration, 'manage_deleteAccounts' )
    def manage_deleteAccounts( self, items, REQUEST=None ):
        """
            Removes accounts.
        """
        # Delete registered accounts
        for item in items:
            try: del self.catalog[ item ]
            except KeyError: pass

        if REQUEST is not None:
            return self.redirect( action='manage_mailForm', REQUEST=REQUEST )

    def _instance_onClone( self, source, item ):
        # unregister all accounts
        self.catalog.clear()

InitializeClass( MailServerBase )


def getContentId( object, extra=None ):
    """
        Returns string suitable for MIME 'Content-Id' header.
    """
    url = getToolByName( object, 'portal_url' )( canonical=True )
    host, path = splithost( splittype(url)[1] )
    cid = host.replace(':','_') + path.replace('/','_') + '.' + object.getUid()
    if extra:
        cid += '.%s' * extra
    return cid

def formataddr( pair, charset=None ):
    """
        Formats name and e-mail address pair into string, properly
        encoding and converting characters if necessary.

        Arguments:

            'pair' -- tuple of strings (<real name>, <e-mail address>);
                    if name is empty, address is returned as-is

            'charset' -- optional 'Charset' object for character
                    set convertion

        Returns:

            String suitable for RFC 822 header.
    """
    name, address = pair
    name    = name    and name.strip()
    address = address and address.strip()

    if not name:
        return address

    if _is8bitstring( name ):
        header = Header( '"%s"' % name, charset )
        header.append( ' <%s>' % address, '8bit' )
        return header

    quotes = ''
    if specialsre.search( name ):
        quotes = '"'
    name = escapesre.sub( r'\\\g<0>', name )

    return '%s%s%s <%s>' % ( quotes, name, quotes, address )


def recode_header( header, charset=None ):
    # converts characters in the header
    if isinstance( header, _Header ):
        chunks = header._chunks
    else:
        chunks = decode_header( header )
    result = ''
    for value, enc in chunks:
        if isinstance( enc, _Charset ):
            enc = enc.input_charset
        result += recode_string( value, charset, enc_from=enc )
    return result


# decode_header() from email package eats whitespace between
# encoded and non-encoded words. Thus we use this fixed version.

def decode_header( header ):
    # If no encoding, just return the header
    header = str(header)
    if not _header_ecre.search(header):
        return [(header, None)]
    decoded = []
    dec = ''
    for line in header.splitlines():
        # This line might not have an encoding in it
        if not _header_ecre.search(line):
            decoded.append((line, None))
            continue
        parts = _header_ecre.split(line)
        while parts:
            unenc = parts.pop(0)
            if not unenc.strip():
                unenc = ''
            if unenc:
                # Should we continue a long line?
                if decoded and decoded[-1][1] is None:
                    decoded[-1] = (decoded[-1][0] + unenc, None)
                else:
                    decoded.append((unenc, None))
            if parts:
                charset, encoding = [s.lower() for s in parts[0:2]]
                encoded = parts[2]
                dec = ''
                if encoding == 'q':
                    dec = email.quopriMIME.header_decode(encoded)
                elif encoding == 'b':
                    dec = email.base64MIME.decode(encoded)
                else:
                    dec = encoded

                if decoded and decoded[-1][1] == charset:
                    decoded[-1] = (decoded[-1][0] + dec, decoded[-1][1])
                else:
                    decoded.append((dec, charset))
            del parts[0:3]
    return decoded

class MailInstaller:
    def install(self, p):
        """ Create mail objects
        """
        p.manage_addProduct['CMFNauTools'].manage_addMailSMTP( 'MailHost', host='' )
        p.manage_addProduct['CMFNauTools'].manage_addMailPOP( 'MailPOP', host='' )
        p.manage_addProduct['CMFNauTools'].manage_addMailIMAP( 'MailIMAP', host='' )

def mailFromDocument( doc, factory=MailMessage, **headers ):
    """ Convert document item to a new MailMessage object
    """
    fmt   = doc.Format()
    files = doc.listAttachments()

    msg   = factory( fmt, multipart=len(files) )
    body  = msg.get_body()

    formatFromAddress( doc, msg )
    msg.set_header( 'subject', doc.Title() )

    for name, value in headers.items():
        msg.set_header( name, value )

    # TODO set document charset
    body.set_payload( doc.FormattedBody( html=False, width=76, canonical=True ) )

    # XXX fix url tool (and portal and site objects) to use server_url
    REQUEST = aq_get( doc, 'REQUEST', None )
    if REQUEST is not None:
        urltool    = getToolByName( doc, 'portal_url' )
        portal_url = urltool()
    else:
        portal_url = aq_get( doc, 'server_url', None, 1 )

    content_id = getContentId( doc, extra=1 )

    for id, file in files:
        ctype = file.getContentType()
        fname = file.getProperty('filename') or file.getId()

        item = factory( ctype or Config.DefaultAttachmentType )
        msg.attach( item, filename=fname, cid=(content_id % id) )

        item.set_payload( file.RawBody() )

    return msg

def formatFromAddress( doc=None, message=None, name=None, email=None ):
    """ Set From header from either folder properties or document owner
    """
    if not (name and email) and doc:
        mstool = getToolByName( doc, 'portal_membership' )
        owner = mstool.getMemberById( doc.Creator() )
        if owner:
            name  = name  or owner.getMemberName()
            email = email or owner.getMemberEmail()

    if not email:
        return None

    if message:
        return message.set_header( 'from', (name, email) )

    # XXX set charset
    return formataddr( (name, email) )

def initialize( context ):
    # module initialization callback
    context.registerInstaller( MailInstaller )
