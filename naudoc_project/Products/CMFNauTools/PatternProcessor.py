"""
PatternProcessor

$Editor: oevsegneev $
$Id: PatternProcessor.py,v 1.12 2008/09/02 11:02:42 oevsegneev Exp $
"""
__version__ = '$Revision: 1.12 $'[11:-2]

import re

from types import DictType, ClassType
from ExtensionClass import Base
from Interface import Interface, Attribute
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Utils import translit_string
from DateTime import DateTime

class PatternProcessor:

    _patterns = {}

    def registerPattern( self, pattern_class ):
        assert isinstance( pattern_class, ClassType ), `pattern_class`

        if self._patterns.has_key( pattern_class.id ):
            raise ValueError( 'pattern <%s> already registered' % pattern_class.id )

        self._patterns[ pattern_class.id ] = pattern_class()

    registerPattern = classmethod( registerPattern )

    def getPatternById( self, id ):
        return self._patterns[ id ]

    def processString( self, string, fmt, **kw):
        return self.getPatternById( fmt ).process( string, **kw )

    def listExplanations( self, fmt ):
        details = []
        self.getPatternById( fmt ).explain( details )
        return details

PatternProcessor = PatternProcessor()

listExplanations = PatternProcessor.listExplanations

class IPattern( Interface ):
    id = Attribute('id', 'TODO')

    def search( string ):
        """ TODO """
   
    def process( string, **kw ):
        """ TODO """

    def explain( details ):
        """ TODO """

class IPatternGroup( Interface ):
    pass # TODO

class Pattern:
    id = NotImplemented

    _explanation = ''
    _pattern = ''

    __implements__ = IPattern

    def search( self, string ):
        """ See IPattern interface """
        raise NotImplementedError
 
    def process( self, string, **kw ):
        """ See IPattern interface """
        raise NotImplementedError
 
    def explain( self, details ):
        if not self._explanation:
            return

        if isinstance( self._explanation, DictType ):
            res = self._explanation
        else:
            res = { self._pattern : self._explanation }

        details.append( res )

class PatternGroup( Pattern ):

    # patterns is iterator of Patterns
    _patterns = ()

    __implements__ = Pattern.__implements__, IPatternGroup

    def process( self, string, **kw ):
        """ See IPatternGroup interface """
        for pattern in self._patterns:
             if isinstance( pattern, str ):
                 pattern = PatternProcessor.getPatternById( pattern )
                 
             string = pattern.process( string, **kw )
        return string

    def explain( self, details ):
        for pattern in self._patterns:
             if isinstance( pattern, str ):
                 pattern = PatternProcessor.getPatternById( pattern )
                 
             pattern.explain( details )

class SimpleReplacePattern( Pattern ):

    def search( self, string ):
        return string.count(self._pattern)

class ReplacePPattern( Pattern ):
    id = 'replace_point'
    _pattern = '.'
    _explanation = "Current folder"

    def search( self, string ):
        return string.startswith(self._pattern + '/')

    def process( self, string, **kw ):
        if self.search ( string ):
            parent = kw['doc'].parent( feature='isPrincipiaFolderish' )
            string = string.replace(self._pattern, parent.physical_path())
        return string

class ReplacePPPattern( Pattern ):
    id = 'replace_2point'
    _pattern = '..'
    _explanation = "Parent folder"

    def search( self, string ):
        s_parts = string.split('/')
        return self._pattern in s_parts

    def process( self, string, **kw ):
        if self.search ( string ):
            s_parts = string.split('/')
            s_parts.reverse()
            folder = kw['doc'].parent( feature='isPrincipiaFolderish' )
            for p in range(len(s_parts)):
                if s_parts[p] == self._pattern: 
                    folder = folder.parent( feature='isPrincipiaFolderish' )
                    if folder is None:
                        raise ValueError('Unexisting folder')
                    s_parts[p] = ''
            s_parts[-1] = folder.physical_path()
            s_parts = [p for p in s_parts if p]
            s_parts.reverse()
            string = '/'.join(s_parts)
        return string

class PathPrefixPattern( Pattern ):
    id = 'path_prefix'
    _explanation = ''

    def process( self, string, **kw ):
        if string.split('/')[0] not in ( '.', '..' ):
            if string.startswith('/'):
                string = '%s/storage%s' % ( kw['doc'].getPortalObject().physical_path(), string )
            else: 
                string = '%s/%s' % ( kw['doc'].aq_parent.physical_path(), string )

        return string

class ReplaceDatePattern( Pattern ):
    id = 'replace_date'
    _pattern = ''
    _explanation = { '\\y': "Year without century as a decimal number"
                    ,'\\Y': "Year with century as a decimal number"
                    ,'\\m': "Month as a decimal number"
                    ,'\\d': "Day of the month as a decimal number"
                    ,'\\H': "Hour as a decimal number"
                    ,'\\M': "Minute as a decimal number"
                   }

    def process( self, string, **kw ):
        now = DateTime()
        for c in 'YymdHM':
            string = string.replace( '\\'+c, now.strftime('%'+c) )
        return string

class ReplaceDPattern( SimpleReplacePattern ):
    id = 'replace_id'
    _pattern = '%D'
    _explanation = "Document Id"

    def process( self, string, **kw ):
        if self.search ( string ):
            string = string.replace(self._pattern, kw['doc'].getId())
        return string

class ReplaceTPattern( SimpleReplacePattern ):
    id = 'replace_title'
    _pattern = '%T'
    _explanation = "Document title"

    def process( self, string, **kw ):
        if self.search ( string ):
            string = string.replace(self._pattern, kw['doc'].Title())
        return string

class ReplaceTTranslitPattern( SimpleReplacePattern ):
    id = 'replace_title_translit'
    _pattern = '%T'
    _explanation = "Document title"

    def process( self, string, **kw ):
        if self.search ( string ):
            if aq_parent( kw['doc'] ) is not None:
                lang = getToolByName( kw['doc'], 'msg' ).get_default_language()
            else:
                lang = 'en'
            string = string.replace(self._pattern, translit_string( kw['doc'].Title(), lang ))
        return string

class ReplaceVPattern( SimpleReplacePattern ):
    id = 'replace_version'
    _pattern = '%V'
    _explanation = "Document version"

    def process( self, string, **kw ):
        if self.search ( string ):
            string = string.replace(self._pattern, kw['doc'].getCurrentVersionId().replace('.', '_'))
        return string

class ReplaceVTranslatePattern( SimpleReplacePattern ):
    id = 'replace_version_translate'
    _pattern = '%V'
    _explanation = "Document version"

    def process( self, string, **kw ):
        if self.search ( string ):
            msg = getToolByName( kw['doc'], 'msg' )
            lang = msg.get_default_language()
            string = string.replace('%V', '%s %s' % ( msg.gettext( 'Version', lang = lang ), kw['doc'].getVersion().getVersionNumber()))
        return string

class ReplaceFnumPattern( SimpleReplacePattern ):
    id = 'replace_Fnum'
    _pattern = '\\Fnum'
    _explanation = "Nomenclative number of the folder that contains the document. It may be specified in the folder's properties"

    def process( self, string, **kw ):
        if self.search ( string ):
            string = string.replace(self._pattern, kw['doc'].parent( feature='isPrincipiaFolderish' ).getCategoryAttribute('nomenclative_number', ''))
        return string

class ReplaceFpfxPattern( SimpleReplacePattern ):
    id = 'replace_Fpfx'
    _pattern = '\\Fpfx'
    _explanation = "Postfix of the folder that contains the document. It may be specified in the folder's properties"

    def process( self, string, **kw ):
        if self.search ( string ):
            string = string.replace(self._pattern, kw['doc'].parent( feature='isPrincipiaFolderish' ).getCategoryAttribute('postfix', ''))
        return string

class ReplaceCpfxPattern( SimpleReplacePattern ):
    id = 'replace_Cpfx'
    _pattern = '\\Cpfx'
    _explanation = "Postfix of the category the document belongs to. It may be stated by creating in the document's category property with 'postfix' id"

    def process( self, string, **kw ):
        if self.search ( string ):
            string = string.replace(self._pattern, kw['doc'].CategoryAttributes().get('postfix', ''))
        return string

class ReplaceRdptPattern( SimpleReplacePattern ):
    id = 'replace_Rdpt'
    _pattern = '\\Rdpt'
    _explanation = "Current registry 'department' property"

    def process( self, string, **kw ):
        if self.search ( string ):
            string = string.replace(self._pattern, kw['obj'].getDepartment())
        return string

class ReplaceSeqPattern( Pattern ):
    id = 'replace_Seq'
    _pattern = r'(\\Seq(\:\d*#)?(?i))'
    _explanation = {'\\Seq[:nn#]': "Counter value, where nn - optional parameter, number of digits of the counter"}

    def search( self, string ):
        return re.search( self._pattern, string)

    def process( self, string, **kw ):
        matches = self.search( string )
        if matches:
            width = matches.group(2) and matches.group(2)[1:-1] or '0'
            seq =   ("%" + ".%s" % (width) + "d") % \
                    (kw['obj'].safe_sequence.getLastValue())
            string = string.replace(matches.group(1), seq)
        return string

class ReplaceSqdPattern( Pattern ):
    id = 'replace_Sqd'
    _pattern = r'(\\Sqd(\:\d*#)?(?i))'
    _explanation = {'\\Sqd[:nn#]': "Special counter value, where nn - optional parameter, number of digits of the counter. This counter starts from 1 each new day"}

    def search( self, string ):
        return re.search( self._pattern, string)

    def process( self, string, **kw ):
        matches = self.search( string )
        if matches:
            width = matches.group(2) and matches.group(2)[1:-1] or '0'
            seq =   ("%" + ".%s" % (width) + "d") % \
                    (kw['obj'].daily_sequence.getLastValue())
            string = string.replace(matches.group(1), seq)
        return string

class PathPatternGroup( PatternGroup ):
    id = 'path'

    _patterns = 'path_prefix', 'replace_point', 'replace_2point'

class IdPatternGroup( PatternGroup ):
    id = 'id'
   
    _patterns = 'replace_title_translit', 'replace_version', 'replace_id'

class TitlePatternGroup( PatternGroup ):
    id = 'title'

    _patterns = 'replace_title', 'replace_version_translate', 'replace_id'

class RegBookPatternGroup( PatternGroup ):
    id = 'reg_book'

    _patterns = 'replace_Fnum', 'replace_Fpfx', 'replace_Cpfx', 'replace_Rdpt', 'replace_Seq', 'replace_Sqd'

class DatePatternGroup( PatternGroup ):
    id = 'date'

    _patterns = ('replace_date',)


class FolderRoutingPatternGroup( PatternGroup ):
    id = 'folder_routing'

    _patterns = 'path', 'title'

class RegBookDatePatternGroup( PatternGroup ):
    id = 'reg_book_date'

    _patterns = 'reg_book', 'date'

def initialize( context ):
    context.register( PatternProcessor.registerPattern ) 

    for item in globals().values():
        if not isinstance( item, ClassType ):
            continue

        if issubclass(item, Pattern) and not item in [Pattern, PatternGroup]:
            context.registerPattern( item )
