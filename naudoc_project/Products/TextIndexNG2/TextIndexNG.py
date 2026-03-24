###########################################################################
#
# LICENSE.txt for the terms of this license.
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
TextIndexNG 
Written by Andreas Jung

E-Mail: andreas@andreas-jung.com

$Id: TextIndexNG.py,v 1.7 2006/05/26 11:20:27 ypetrov Exp $
"""

import sys, re, time, warnings, traceback
from cStringIO import StringIO
from types import IntType, StringType, UnicodeType, InstanceType, DictType, ListType, TupleType

from Globals import DTMLFile, InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from zLOG import LOG, ERROR
from OFS.SimpleItem import SimpleItem
from Products.PluginIndexes import PluggableIndex       
from Products.PluginIndexes.common.util import parseIndexRequest
from OFS.content_types import guess_content_type
from BTrees.IIBTree import IIBucket, IISet
from classVerify import verifyClass

from Products.TextIndexNG2.ResultSet import ResultSet
from Products.TextIndexNG2.Registry import ParserRegistry, ConverterRegistry, NormalizerRegistry, StorageRegistry
from Products.TextIndexNG2.Registry import LexiconRegistry, SplitterRegistry, StopwordsRegistry, RegistryException
from ParseTree import Evaluator

from interfaces.IStopwords import StopwordsInterface
from interfaces.INormalizer import NormalizerInterface

import parsers, converters, normalizers
import storages, lexicons, splitters, stopwords

import Stemmer 
import indexsupport
import PositionMap
#from Timer import Timer
from logger import LOG

from AccessControl.Permissions import  search_zcatalog
try:
    from AccessControl.Permissions import manage_zcatalog_indexes
except:
    manage_zcatalog_indexes = 'Manage ZCatalogIndex Entries' 


class TXNGError(Exception): pass


# Precalculate the term weight for terms derived by
# right truncation. The weight is calculated by the difference
# of the length of original term and the derived term.
# The weight is inverse proportional to difference
#
# weight = 1.0 / (a * difference + 1)
# a = (1 - p) / (p * d)
# p is the weight for terms with a difference of d  
#
# We use p=0.5 and  d=5


TRUNC_WEIGHT = {}
p = 0.5; d = 5
a = (1 - p) / (p * d)
for i in range(250): TRUNC_WEIGHT[i] = 1.0 / (a*i + 1)


class TextIndexNG(SimpleItem):
    """ TextIndexNG """

    meta_type = 'TextIndexNG2'
    __implements__ = PluggableIndex.PluggableIndexInterface

    security = ClassSecurityInfo()
    security.declareObjectProtected(manage_zcatalog_indexes)

    manage_options= (
        {'label': 'Settings',     
         'action': 'manage_workspace',
         'help': ('TextIndexNG','TextIndexNG_Settings.stx')},
        {'label': 'Stop words',     
         'action': 'manage_stopwords',
         'help': ('TextIndexNG','TextIndexNG_Stopwords.stx')},
        {'label': 'Normalizer',     
         'action': 'manage_normalizer',
         'help': ('TextIndex','TextIndexNG_Normalizer.stx')},
        {'label': 'Converters',     
         'action': 'manage_converters',
         'help': ('TextIndexNG','TextIndexNG_Converters.stx')},
        {'label': 'Vocabulary',     
         'action': 'manage_vocabulary',
         'help': ('TextIndexNG','TextIndexNG_Vocabulary.stx')},
        {'label': 'Test',     
         'action': 'manage_test',
         'help': ('TextIndexNG','TextIndexNG_Test.stx')},
        {'label': 'Statistics',     
         'action': 'manage_statistics',
         'help': ('TextIndexNG','TextIndexNG_Statistics.stx')},
    )

    _all_options = ('splitter_max_len', 'use_splitter', "splitter_separators",
         'splitter_single_chars', 'splitter_casefolding', 'use_stemmer', 
         'lexicon', 'near_distance', 'truncate_left', 'autoexpand',
         'autoexpand_limit', 'numhits',
         'use_stopwords', 'use_normalizer', 'use_converters',
         'use_parser', 'indexed_fields', 'default_encoding', 'sort_words_limit'
        )

    query_options = ("query", "operator", "parser", "encoding", 'near_distance', 'autoexpand',
                     'numhits')

    def __init__(self, id, extra=None, caller=None):
        
        self.id            = id

        # check parameters
        if extra:
            for k in extra.keys():
                if not k in self._all_options:
                    raise TXNGError,'unknown parameter "%s"' % k

        if caller is not None:
            self.catalog_path = '/'.join(caller.getPhysicalPath())
        else:
            self.catalog_path = None

        # indexed attributes
        self._indexed_fields = getattr(extra, 'indexed_fields', '').split(',')
        self._indexed_fields = [ attr.strip() for attr in  self._indexed_fields if attr ]
        if not self._indexed_fields:
            self._indexed_fields = [ self.id ]

        # splitter to be used
        self.use_splitter = getattr(extra, 'use_splitter', 'TXNGSplitter')

        # max len of splitted words
        self.splitter_max_len= getattr(extra,'splitter_max_len', 64)

        # allow single characters
        self.splitter_single_chars   = getattr(extra,'splitter_single_chars',0)

        # valid word separators
        self.splitter_separators = getattr(extra, 'splitter_separators','')

        # allow single characters
        self.splitter_casefolding   = getattr(extra,'splitter_casefolding',1) 

        # left truncation
        self.truncate_left = getattr(extra, 'truncate_left', 0)

        # Term autoexpansion
        self.autoexpand = getattr(extra, 'autoexpand', 0)
        self.autoexpand_limit = getattr(extra, 'autoexpand_limit', 4)

        # maximum number of hits
        self.numhits = getattr(extra, 'numhits', 999999999)

        # name of stemmer or None
        self.use_stemmer    = getattr(extra,'use_stemmer',    None) or None

        # default maximum distance for words with near search
        self.near_distance  = getattr(extra,'near_distance',  5)

        # Stopwords: either filename or StopWord object
        self.use_stopwords     = getattr(extra,'use_stopwords',    None) or None
        if self.use_stopwords:
            verifyClass(StopwordsInterface, self.use_stopwords.__class__)
     
        # Normalizer
        self.use_normalizer = getattr(extra,'use_normalizer', None) or None

        # use converters from the ConvertersRegistry
        self.use_converters = getattr(extra,'use_converters',0) 

        # encoding
        self.default_encoding = getattr(extra,'default_encoding', 'iso-8859-15') 

        # check Parser
        self.use_parser = getattr(extra, 'use_parser','PyQueryParser')

        # maximum number of words should be used for comparison
        self.sort_words_limit = getattr(extra, 'sort_words_limit', 30)

        self.use_storage = 'StandardStorage'
        self.use_lexicon = 'StandardLexicon'
        self.clear()


    def clear(self):

        self._storage = StorageRegistry.get(self.use_storage)() 
        self._lexicon = LexiconRegistry.get(self.use_lexicon)(truncate_left=self.truncate_left)


    def getId(self):   return self.id
    def __len__(self): return len(self._storage)
    def __nonzero__(self): return not not self._unindex
    def printIndex(self): self._storage.printStorage()
    def availableStemmers(self): return Stemmer.availableStemmers()    
    def getLexicon(self): return self._lexicon
    def getStorage(self): return self._storage

    def index_object(self, documentId, obj, threshold=None):
        """ wrapper to handle indexing of multiple attributes """

        # needed for backward compatibility
        try:
            fields = self._indexed_fields
        except:
            fields  = [ self.id ]

        res = 0
        for attr in fields:
            res += self._index_object(documentId, obj, threshold, attr) 
        return res > 0 
        
    def _index_object(self, documentId, obj, threshold=None, attr=''):
        
        # This is to support foreign file formats that
        # are stored as "File" objects when searching
        # through PrincipiaSearchSource

        if obj.meta_type in ('File', 'Portal File') and  \
           attr in ('PrincipiaSearchSource', 'SearchableText'):
            source = str(obj)
            mimetype = obj.content_type

        elif obj.meta_type in ('ZMSFile',):
            lang = attr[attr.rfind('_')+1:]
            req = {'lang' : lang}
            file = obj.getObjProperty('file', req)
            source = ''
            mimetype = None
            if file:
                source = file.getData()
                mimetype = file.getContentType()

   
        elif obj.meta_type in ('TTWObject',) and attr not in ('SearchableText', ): 
                field = obj.get(attr)
                source = str(field)
                if field.meta_type in ( 'ZMSFile', 'File' ):
                    mimetype = field.getContentType()
                else:
                    mimetype = None
        else:

            try:
                source = getattr(obj, attr)
                if callable(source): source = source()
                
                if not isinstance(source, UnicodeType):
                    source = str(source)

                mimetype = None

            except (AttributeError, TypeError):
                return 0
        
        # If enabled, we try to find a valid document converter
        # and convert the data to get a hopefully text only representation
        # of the data.

        if self.use_converters:
            mt, enc  = guess_content_type(obj.getId(), source)
            if mimetype is None: mimetype = mt

            try:
                converter = ConverterRegistry.get(mimetype)
            except RegistryException:
                return 0

            if converter:

                try:
                    source = converter(source)
                except:
                    return 0 

            if obj.meta_type == 'Portal File': 
                source += ' ' + obj.SearchableText()

        # Now we try to get a valid encoding. For unicode strings
        # we have to perform no action. For string objects we check
        # if the document has an attibute (not a method) '<index>_encoding'.
        # As fallback we also check for the presence of an attribute
        # 'document_encoding'. Checking for the two attributes allows
        # us to define different encodings for different attributes
        # on an object. This is useful when an object stores multiple texts
        # as attributes within the same instance (e.g. for multilingual
        # versions of a text but with different encodings). 
        # If no encoding is specified as object attribute, we will use
        # Python's default encoding.
        # After getting the encoding, we convert the data to unicode.

        try: # needed for backward compatibility
            encoding = self.default_encoding
        except:
            encoding = self.default_encoding = 'iso-8859-15'

        if isinstance(source, StringType):       

            for k in ['document_encoding', attr + '_encoding']:
                enc = getattr(obj, k, None)
                if enc:
                    encoding = enc  
            if encoding=='ascii': 
                encoding ='iso-8859-15'         

            source = unicode(source, encoding, 'ignore')
 
        elif isinstance(source, UnicodeType): 
            pass

        else:
            raise TXNGError,"unknown object type" 

        # Normalization: apply translation table to data
        if self.use_normalizer:
            source = NormalizerRegistry.get(self.use_normalizer).process(source)    
 
        # Split the text into a list of words
        SP = SplitterRegistry.get(self.use_splitter)

        _source = source
        words = SP( casefolding  = self.splitter_casefolding,
                    separator    = self.splitter_separators,
                    maxlen       = self.splitter_max_len,
                    singlechar   = self.splitter_single_chars
                    ).split(_source, encoding)

        #  remove stopwords from data
        if self.use_stopwords:
            words = self.use_stopwords.process( words ) 

        # We pass the list of words to the corresponding lexicon
        # and obtain a list of wordIds. The "old" TextIndex iterated
        # over every single words (overhead).
        wids = self._lexicon.getWordIdList(words)

        # Stem all words in one run
        if self.use_stemmer:
            stemmed = Stemmer.Stemmer( self.use_stemmer ).stem(words)
            # Filter out not-stemmed words for ranking accuracy.
            i = 0
            for word in words:
                if stemmed[i] == word:
                    stemmed[i] = None
                i += 1
            stemmed = filter( None, stemmed )
            # Append stemmed words to the list of wordIds.
            wids.extend( self._lexicon.getWordIdList(stemmed) )

        # insert forward entries 
        self._storage.insert(wids, documentId)

        return len(wids)

    def unindex_object(self, documentId): 
        """ carefully unindex document with Id 'documentId'
            index and do not fail if it does not exist 
        """
        self._storage.removeDocument(documentId)


    def _apply_index(self, request, cid=''): 
        """ Apply the index to query parameters given in the argument,
        request

        The argument should be a mapping object.

        If the request does not contain the needed parameters, then
        None is returned.
 
        Otherwise two objects are returned.  The first object is a
        ResultSet containing the record numbers of the matching
        records.  The second object is a tuple containing the names of
        all data fields used.  
        """

        record = parseIndexRequest(request,self.id,self.query_options)
        if record.keys==None: return None

        # extract some parameters from the request 

        query_operator = record.get('operator','dummy')
        if query_operator is None:
            raise TXNGError, ("Invalid operator '%s' "
                                            "for a TextIndex" % query_operator)

        query_parser = record.get('parser', self.use_parser)
        if not ParserRegistry.is_registered(query_parser): 
            raise TXNGError, "Unknown parser '%s'" %  query_parser

 
        query = record.keys[0]
        encoding = record.get('encoding', self.default_encoding)
        if isinstance(query, StringType): query = unicode(query, encoding, 'ignore')
        P = ParserRegistry.get( query_parser )
        parsed_query = P(query.strip(), operator=query_operator)
        if not parsed_query:
            raise TXNGError,"Bad query: '%s'" % q

        LOG.debug('parsed query: %s' % parsed_query)

        evaluator = Evaluator(self)
        evaluator.autoexpand = record.get('autoexpand', self.autoexpand)
        evaluator.near_distance = record.get('near_distance', self.near_distance)

        numhits = record.get('numhits', self.numhits)
        resultset = evaluator(parsed_query)
        resultset.cosine_ranking(self, numhits)

        return  resultset.result(), (self.id,) 


    ################################################################
    # callbacks for ParseTree.py
    ################################################################

    def _lookup(self, words, do_autoexpand=1, do_stem=1):
        """ search a word or a list of words in the lexicon and 
            return a ResultSet of found documents.
        """

        docids = IISet()
        used_words = {} 

        #  remove stopwords from data
        if self.use_stopwords:
            words = self.use_stopwords.process( words ) 

        for word in words:

            # perform casefolding if necessary
            if self.splitter_casefolding:
                word = word.lower()

            if self.use_normalizer:
                word = NormalizerRegistry.get(self.use_normalizer).process(word)    
 
            wlen = len(word)
            # Stem the word if necessary        
            if do_stem and self.use_stemmer:
                word  = Stemmer.Stemmer(self.use_stemmer).stem(word)
                wlen -= (wlen - len(word)) * 2

            used_words[word] = 1.0

            wid = self._lexicon.getWordId(word)

            # Retrieve list of docIds for this wordid
            if wid is not None:
                docids.update( self._storage.get(wid) )
            if do_autoexpand and self.autoexpand and len(word) >= self.autoexpand_limit:
                rs = self.lookupWordsByTruncation(word, right=1, do_stem=0)
                docids.update(rs.docIds())
                for w in rs.words().keys():
                    used_words[w] = TRUNC_WEIGHT[len(w)-wlen]

        return ResultSet(docids, used_words)

    
    def lookupWord(self, word, do_stem=1, do_autoexpand=1):
        """ search a word in the lexicon and return a ResultSet
            of found documents 
        """

        return self._lookup( [word], do_stem=do_stem, do_autoexpand=do_autoexpand )


    def lookupWordsByPattern(self, word, do_stem = 1):
        """ perform full pattern matching """

#        if self.use_stemmer:
#            raise TXNGError, \
#                "pattern matching not allowed with enabled stemming"

        if self.splitter_casefolding: word = word.lower()
        words = self._lexicon.getWordsForPattern(word)

        return self._lookup(words, do_autoexpand = 0, do_stem = do_stem)

    def lookupWordsByTruncation(self, word, left=0, right=0, do_stem=1):
        """ perform right truncation lookup"""

        if self.use_normalizer:
            word = NormalizerRegistry.get(self.use_normalizer).process(word)    

#       if self.use_stemmer:
#           raise TXNGError, \
#               "right truncation not allowed with enabled stemming"

        if self.splitter_casefolding: word = word.lower()
        if right:
            words = self._lexicon.getWordsForRightTruncation(word)
        if left:
            if  self.truncate_left:
                words = self._lexicon.getWordsForLeftTruncation(word)
            else: 
                raise TXNGError, "Left truncation not allowed"

        return self._lookup(words, do_autoexpand=0, do_stem=do_stem)


    def lookupRange(self, w1, w2):
        """ search all words between w1 and w2 """

        if self.splitter_casefolding: 
            w1 = w1.lower()
            w2 = w2.lower()

        words = self._lexicon.getWordsInRange(w1, w2)
        return self._lookup(words, do_autoexpand=0)


    def lookupWordsBySimilarity(self, word):       
        """ perform a similarity lookup """

        lst = self._lexicon.getSimiliarWords(word)

        docids = IISet()
        used_words = {} 

        getwid = self._lexicon.getWordId

        for word, threshold in lst:
            used_words[word] = threshold
            wid = getwid(word)

            docids.update( self._storage.get(wid) )

        return ResultSet(docids, used_words)


    def lookupWordsBySubstring(self, word):       
        """ perform a substring search """

        if self.splitter_casefolding: word = word.lower()
        words = self._lexicon.getWordsForSubstring(word)
        return self._lookup(words, do_autoexpand=0)
        

    ###################################################################
    # document lookup for near and phrase search 
    ###################################################################

    def positionsFromDocumentLookup(self,docId, words):
        """ search all positions for a list of words for
            a given document given by its documentId.
            positions() returns a mapping word to
            list of positions of the word inside the document.
        """

        # some query preprocessing  
        if self.splitter_casefolding:
            words = [word.lower() for word in words] 

        posMap = PositionMap.PositionMap() 

        # obtain wids from document
        wids = self._storage.getWordIdsForDocId(docId)
        for word in words:
            word = self._lexicon.getWordId( word )
            if word is None:
                continue
            posLst = indexsupport.listIndexes(wids, word)
            posMap.append(word, IISet(posLst) )

        return posMap

    ###################################################################
    # some helper functions 
    ###################################################################

    def numObjects(self):
        """ return number of index objects """
        return len(self._storage.getDocIds())

    def rebuild(self):
        """ rebuild the inverted index """
        self._storage.buildInvertedIndex()
        return "done"

    def info(self):
        """ return a list of TextIndexNG properties """

        lst = [ (k,str(getattr(self,k))) for k in dir(self) ] 
        lst.sort()
        return lst

    def getEntryForObject(self, docId, default=None, limit=None):
        """Get all information contained for a specific object.
           This takes the objects record ID as it's main argument.
        """

        try:
            wids = self._storage.getWordIdsForDocId(docId)
            if limit:
                wids = wids[:limit]
            return [self._lexicon.getWord(wid) for wid in wids]
        except:
            return []

    def getRegisteredObjectForObject(self, docId, default=None):
        """Get all information contained for a specific object.
           This takes the objects record ID as it's main argument.
        """

        return "%d distinct words" % \
            len(self._storage.getWordIdsForDocId( docId ))

    def uniqueValues(self, name=None, withLengths=0):
        """ we don't implement that ! """
        raise NotImplementedError

    ###################################################################
    # Catalog sort API
    ###################################################################
    
    def keyForDocument(self, docId):
        return self.getEntryForObject( docId, getattr( self, 'sort_words_limit', 30 ) )

    def items(self):
        res = []
        for docid, wids in self._storage._reverse_idx.items():
            res.append( ( self.keyForDocument( docid ), docid ) )
        return res

    ###################################################################
    # minor introspection API
    ###################################################################

    def allSettingOptions(self):
        return self._all_options


    def getSetting(self, key):
        if not key in self._all_options:
            raise TXNGError, "No such setting '%s'" % key

        return getattr(self, key, '')

    def getIndexSourceNames(self):
        """ return sequence of indexed attributes """
        
        try:
            return self._indexed_fields
        except:
            return [ self.id ]

    def getDebugMode(self):
        """ return debug mode """
        return LOG.status()


    ###################################################################
    # Stopword handling
    ###################################################################

    def getStopWords(self):     
        """ return a list of all stopwords (for ZMI) """

        if self.use_stopwords:
            return self.use_stopwords.getStopWords()
        else:
            return []

    ###################################################################
    # Normalizer handling
    ###################################################################

    def getNormalizerTable(self):     
        """ return the normalizer translation table """
        
        if self.use_normalizer:       
            return NormalizerRegistry.get(self.use_normalizer).getTable()
        else:
            return None

    ###################################################################
    # Converters
    ###################################################################

    def allConverters(self):
        """ return a list of all registered converters """
        lst = []
        used = []
        converters = ConverterRegistry.allRegisteredObjects()
        converters.sort( lambda x,y: cmp(x.getType(),y.getType()) )
        for c in converters:
            if not c in used:
                used.append(c)
                lst.append( (c.getType(), c.getDescription(), c.getDependency() ) )

        return lst

    ###################################################################
    # Testing 
    ###################################################################

    def testTextIndexNG(self, query, parser, operator=None):
        """ test the TextIndexNG """
        
        res = self._getCatalog().searchResults({self.id: {'query': query,
                                                          'parser': parser,
                                                          'operator': operator} })

        return [r.getURL(relative=1) for r in res]


    ###################################################################
    # Vocabulary browser 
    ###################################################################

    def _getCatalog(self):
        """ return the Catalog instance """

        try: 
            self._v_catalog = self.restrictedTraverse(self.catalog_path)
        except KeyError:
            self._v_catalog = self.aq_parent.aq_parent
        return self._v_catalog

    def getDocumentsForWord(self, word):
        """ return a sequence of document paths that contain 'word' """

        catalog = self._getCatalog()

        wid = self._lexicon.getWordId(word)
        docIds = self._storage.getDocumentIdsForWordId(wid)
        paths =  [ catalog.getpath(docId) for docId in docIds ]
        paths.sort()
        return paths

    ###################################################################
    # TextIndexNG preferences 
    ###################################################################

    def manage_setPreferences(self,extra, debug_mode,
                               REQUEST=None,RESPONSE=None,URL2=None):
        """ preferences of TextIndex """

        if debug_mode: LOG.debug_on()
        else: LOG.debug_off()

        for x in ('near_distance', ): 

            if hasattr(extra,x):

                oldval = getattr(self,x)
                newval = getattr(extra,x)
                setattr(self, x, newval)

        if RESPONSE:
            RESPONSE.redirect(URL2 + 
                '/manage_main?manage_tabs_message=Preferences%20saved')

    manage_workspace  = DTMLFile("dtml/manageTextIndexNG",globals())
    manage_stopwords  = DTMLFile("dtml/manageStopWords",globals())
    manage_normalizer = DTMLFile("dtml/manageNormalizer",globals())
    manage_converters = DTMLFile("dtml/showConverterRegistry",globals())
    manage_vocabulary = DTMLFile("dtml/vocabularyBrowser",globals())
    manage_statistics = DTMLFile("dtml/manageStatistics",globals())
    showDocuments     = DTMLFile("dtml/vocabularyShowDocuments",globals())
    manage_test       = DTMLFile("dtml/testTextIndexNG",globals())
    testResults       = DTMLFile("dtml/testResults",globals())

InitializeClass(TextIndexNG)


manage_addTextIndexNGForm = DTMLFile('dtml/addTextIndexNG', globals())

def manage_addTextIndexNG(self, id, extra, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a new TextIndexNG """

    from Registry import StopwordsRegistry

    # the ZMI passes the name of a registered Stopwords object (usually the
    # language abreviation like 'en', 'de'. 

    if extra.use_stopwords:
        sw = StopwordsRegistry.get(extra.use_stopwords)
        extra.use_stopwords = sw

    return self.manage_addIndex(id, 'TextIndexNG2', extra, REQUEST, RESPONSE, URL3)


