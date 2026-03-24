###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
Module breaks out Zope specific methods and behavior.  In
addition, provides the Lexicon class which defines a word to integer
mapping.

$Id: StandardLexicon.py,v 1.2 2004/09/20 12:14:15 vpastukhov Exp $
"""

import re
from types import UnicodeType

from Persistence import Persistent
from Acquisition import Implicit
from BTrees.OIBTree import OIBTree
from BTrees.IOBTree import IOBTree
from BTrees.IIBTree import IISet
import BTrees.Length

from Products.TextIndexNG2.interfaces.ILexicon import LexiconInterface
from Products.TextIndexNG2.BaseParser import QueryParserError
from indexsupport import vocabBatchInsert
from Levenshtein import ratio

def reverse(s):
    """ reverse a string """
    l = list(s)
    l.reverse()
    return ''.join(l)

class Lexicon(Persistent, Implicit):
    """Maps words to word ids """

    __implements__ = LexiconInterface

    def __init__(self, truncate_left=0):
        self.truncate_left = truncate_left
        self.clear()

    def clear(self):
        self._nextid      = BTrees.Length.Length()
        self._forward_idx = OIBTree()
        self._inverse_idx = IOBTree()
        if self.truncate_left:
            self._lforward_idx = OIBTree()
        else:
            self._lforward_idx = None

    def getWordIdList(self, words):
        """ return a list a wordIds for a list of words """

        fwd_idx = self._forward_idx
        fwd_get = fwd_idx.get
        inv_idx = self._inverse_idx
        lfw_idx = self._lforward_idx
        nextid  = self._nextid
        trnleft = self.truncate_left

        wids = [None] * len(words)
        i = 0

        for word in words:
            wid = fwd_get(word)
            if wid is None:
                nextid.change(1)
                wid = nextid()
                fwd_idx[word] = wid
                inv_idx[wid] = word
                if trnleft:
                    lfw_idx[reverse(word)] = wid
            wids[i] = wid
            i += 1

        return wids

    def getWordId(self, word, default=None):
        """Return the matched word against the key."""

        return  self._forward_idx.get(word, default)

    def getWord(self, wid):
        """ return a word by its wid"""
        return self._inverse_idx[wid]

    def getWordsForRightTruncation(self, prefix):
        """ Return a list for wordIds that match against prefix.
            We use the BTrees range search to perform the search
        """

        assert isinstance(prefix, UnicodeType)
        return  self._forward_idx.keys(prefix, prefix + u'\uffff') 

    def getWordsForLeftTruncation(self, suffix):
        """ Return a sequence of word ids for a common suffix """

        suffix = reverse(suffix)
        assert isinstance(suffix, UnicodeType)
        return  [reverse(w) for w in  self._lforward_idx.keys(suffix, suffix + u'\uffff') ] 

    def createRegex(self, pattern):
        """Translate a PATTERN to a regular expression """
        
        pattern = pattern.replace( '*', '.*')
        pattern = pattern.replace( '?', '.')

        return "%s$" % pattern

    def getSimiliarWords(self, term, threshold=0.75): 
        """ return a list of similar words bases on the levenshtein distance """
        return [ (w, ratio(w,term)) for w in self._forward_idx.keys() if ratio(w, term) > threshold  ]

    def getWordsForPattern(self, pattern):
        """ perform full pattern matching """

        # search for prefix in word
        mo = re.search('([\?\*])', pattern)
        if mo is None:
            return [ pattern ] 

        pos = mo.start(1)
        if pos==0: raise QueryParserError, \
            'word "%s" should not start with a globbing character' % pattern

        prefix = pattern[:pos]

        words = self._forward_idx.keys(prefix, prefix + u'\uffff')
        regex = re.compile( self.createRegex(pattern) )

        return [ word  for word in words if regex.match(word) ] 

    def getWordsInRange(self, w1, w2):
        """ return all words within w1...w2 """
        
        words = self._forward_idx.keys(w1, w2)
        return words

    def getWordsForSubstring(self, sub):
        """ return all words that match *sub* """
        
        return [word for word in self._forward_idx.keys() if word.find(sub) > -1 ]


    def __len__(self):
        return self._nextid() 

if __name__ == '__main__':
    test()
