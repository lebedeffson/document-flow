"""
Defines Converter classes: TextConverter, MSWordConverter, RTFConverter,
PDFConverter, MSPowerPointConverter, MSExcelConverter, HTMLConverter

$Id: Converter.py,v 1.35 2006/06/13 12:40:19 oevsegneev Exp $

$Editor: kfirsov $
"""
__version__ = '$Revision: 1.35 $'[11:-2]

import os, re, sys, tempfile
import shutil
from cgi import escape
from htmlentitydefs import entitydefs
from sgmllib import SGMLParser
from types import StringType

try:
    import pywintypes 
    import win32pipe
except ImportError:
    win32pipe = None

from App.Common import package_home
from Globals import INSTANCE_HOME

from Exceptions import ConverterError
from Utils import checkCommand


ConverterFactories  = []
AvailableConverters = []


if sys.platform == 'win32':
    sys_err_stream = '2> nul'
else:
    sys_err_stream = '2> /dev/null'

# !!!!!!!!!!!!!!!! TODO:  content-types
#                         errout !!!


def convert(doc, contentType, format='text', charset='windows-1251'):
    """
      converts document, contained in 'doc', according content type, contained in 'contentType'
      format and charset, and return conveted text
    """
    for converter in ConverterFactories:
        if contentType in converter.content_types:
            return str(converter(doc, format, charset))
    raise ConverterError, 'content_type undefinied'


class BaseConverter:
    """
      BaseConverter class
    """
    enabled = 0
    _text = ''

    def __init__(self, doc, format='text', charset='windows-1251'):
        self.format = format
        self.charset = charset
        if not self.enabled:
            raise ConverterError, 'Appropriate converter is not installed'
        if doc:
            self.makeTempFile(doc)
            self._text = self.convert(format, charset)
            self.removeTempFile()

    def convert(self, format='text', charset='windows-1251'):
        """
          abstract method

          this method must convert file self._fname to text and return result
        """
        pass

    def __str__(self):
        """
          returns converted text
        """
        return self._text

    def makeTempFile(self, doc):
        """
          makes and open temp file
        """
        self._fname = tempfile.mktemp()
        self._tempFile = open(self._fname,'w+b').write(doc)

    def removeTempFile(self):
        """
          remove temp file
        """
        os.unlink(self._fname)

    def execute(self, com):
        """
          executes system command 'com' and returns output result
        """
        if win32pipe:
            fres = win32pipe.popen(com)
        else:
            fres = os.popen(com)
        res = fres.read()
        return res


class TextConverter:
    """
      Simple text converter class

      returns input text really
    """
    enabled = 0
    content_types = ('text/plain',)
    content_description = "Text"
    depends_on = None

    def __init__(self, doc, format='text', charset='windows-1251'):
        if format=='html':
            #escape <, > , &, ' and "
            doc = escape(str(doc), 1)
            #replace all \n\r to <br>
            if doc.find('\r') >= 0: doc = ''.join(doc.split('\r'))
            if doc.find('\n') >= 0: doc = '<br>\n'.join(doc.split('\n'))

        self._text = doc

    def __str__(self):
        return self._text

ConverterFactories.append( TextConverter )


class MSWordConverter(BaseConverter):
    """
      Microsoft Word document converter class
    """

    content_types = ('application/msword', 'application/ms-word', 'application/vnd.ms-word', 'application/vnd.msword')
    content_description = "MSWord"
    depends_on = 'wvWare'

    def convert(self, format='text', charset='windows-1251'):
        path = package_home( globals() )
        path = path.replace('\\', '/')
        config = 'wv%s.xml' % format.capitalize()
        if not os.path.isfile(os.path.join(path, config)):
            config = 'wvText.xml'
        return self.execute('wvWare --charset=%s --nographics -x \"%s\" %s %s' % (charset, os.path.join(path, config), self._fname.replace('\\', '/'), sys_err_stream))

ConverterFactories.append( MSWordConverter )


class RTFConverter(BaseConverter):
    """
      Rich Text Format document converter class
    """
    content_types = ('application/rtf', 'text/richtext')
    content_description = "RTF"
    depends_on = 'rtf2html'

    def convert(self, format='text', charset='windows-1251'):
        #ToDo: use format and charset
        output_file = tempfile.mktemp()

        #TODO: there is possibility to store images from rtf file.
        img_dir = tempfile.mktemp()

        #TODO: need to show rtf2html license somewhere (author's page: http://sageshome.net)
        params = [ self.depends_on ]
        params.append( self._fname ) #original
        params.append( output_file ) #html
        params.append( os.path.split( img_dir )[-1] ) #images

        self.execute(' '.join(params)) #convert

        try:
            out = open(output_file)
            text = out.read()
            out.close()
        except IOError:
            raise ConverterError, "RTF converter is not installed"

        os.unlink(output_file)

        #remove images
        if os.path.exists( img_dir ):
            shutil.rmtree( path=img_dir, ignore_errors=1 )

        if format=='html':
            return str(text)

        p = StripTagParser()
        p.feed(text)
        p.close()
        text = str(p)

        return text

ConverterFactories.append( RTFConverter )


class PDFConverter(BaseConverter):
    """
      Adobe PDF document converter class
    """
    content_types = ('application/pdf',)
    content_description = "PDF"
    depends_on = ('pdftotext', 'iconv')

    def convert(self, format='text', charset='windows-1251'):
        #ToDo: use format
        return self.execute('pdftotext -enc UTF-8 %s - | iconv -f UTF-8 -t %s' % (self._fname, charset))

ConverterFactories.append( PDFConverter )


class MSPowerPointConverter(BaseConverter):
    """
      Microsoft Power Point document Converter class
    """
    content_types = ('application/mspowerpoint', 'application/ms-powerpoint', 'application/vnd.ms-powerpoint')
    content_description = "MSPowerPoint"
    depends_on = ('ppthtml', 'iconv')

    def convert(self, format='text', charset='windows-1251'):
        #TODO: use format
        text = self.execute('ppthtml %s | iconv -f UTF-8 -t %s' % (self._fname, charset))
        if format=='html':
            return str(text)

        p = StripTagParser()
        p.feed(text)
        p.close()
        text = str(p)
        return text

ConverterFactories.append( MSPowerPointConverter )


class MSExcelConverter(BaseConverter):
    """
      Microsoft Excel document converter class
    """
    content_types = ('application/vnd.ms-excel', 'application/msexcell', 'application/excel',)
    content_description = "MSExcel"
    depends_on = ('xlhtml', 'iconv')

    def convert(self, format='text', charset='windows-1251'):
        text = self.execute('xlhtml -nh -a %s | iconv -c -f UTF-8 -t %s' % (self._fname, charset))
        if format=='html':
            return str(text)

        p = StripTagParser()
        p.feed(text)
        p.close()
        text = str(p)
        return text

ConverterFactories.append( MSExcelConverter )


class HTMLConverter:
    """
      HTML document converter class
    """
    enabled = 0
    content_types = ('text/html',)
    content_description = "HTML"
    depends_on = None

    def __init__(self, doc, format='text', charset='windows-1251'):
        if format=='html':
            self._text = str(doc)
        else:
            p = StripTagParser()
            p.feed(doc)
            p.close()
            self._text = str(p)

    def __str__(self):
        return self._text

ConverterFactories.append( HTMLConverter )

_mso_macro_rec = re.compile(r'<!\[([^>]*)\][\s\-]*>')

class StripTagParser( SGMLParser ):
    """
      SGML Parser removing any tags and translating HTML entities.
    """
    data = None

    def handle_entityref( self, name ):
        table = self.entitydefs
        if table.has_key( name ):
            if self.data is None:
                self.data = []
            self.data.append( table[name] )
        else:
            self.unknown_entityref( name )

    def parse_declaration( self, i ):
        # Treat MSOffice 2000 generated macros like <![ ]> as comments
        # avoiding SGMLParseError.
        match = _mso_macro_rec.match( self.rawdata, i )
        if match:
            self.handle_comment( match.group(1) )
            return match.end()
        return SGMLParser.parse_declaration( self, i )

    def handle_data( self, data ):
        if self.data is None:
            self.data = []
        self.data.append( chr(160) )
        self.data.append( data )

    def __str__( self ):
        if self.data is None:
            return ''
        return ''.join( self.data )

def isConvertible( content_type ):
    for converter in ConverterFactories:
        if converter.enabled and content_type in converter.content_types:
            return 1
    return 0


def initialize( context ):

    for converter in ConverterFactories:
        enable = 0

        if not converter.depends_on:
            enable = 1
        elif type(converter.depends_on) is StringType:
            enable = checkCommand( converter.depends_on )
        else:
            for cmd in converter.depends_on:
                if not checkCommand( cmd ):
                    break
            else:
                enable = 1

        if enable:
            converter.enabled = 1
            AvailableConverters.append( converter.content_description )
