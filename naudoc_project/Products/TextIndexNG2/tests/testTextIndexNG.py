###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import sys, os, unittest
import ZODB
from Products.TextIndexNG2 import TextIndexNG
from Products.PluginIndexes.common.PluggableIndex import PluggableIndexInterface
from Products.TextIndexNG2.classVerify import verifyClass

class TO:
    
    def __init__(self,txt,id):
        self.text = txt
        self.id   = id
        self.meta_type = 'dummy'

class arguments: 

    def __init__(self, *args, **kw):
        self._keys = []

        for k,v in kw.items():
            setattr(self,k,v)
            self._keys.append(k)

    def keys(self): return self._keys


class Tests(unittest.TestCase):

    _testdata = (
        (1, 'this text is a simple text'),
        (2, 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG'),
        (3, 'auf einen alle Flugplätze der Gegner zerstört worden'),
        (4, 'alle Flugplätze Gegner lazy'),
        (5, 'extension comparisons flyers genes daemons monkeys'),
    )

    def _init(self, arguments):

        self._index  = TextIndexNG.TextIndexNG(
                            id='text', 
                            extra=arguments
                        )

        for id,text in self._testdata:
            obj = TO (text,id)
            self._index.index_object(id, obj)

    def search(self,query, expected):

        result, id = self._index._apply_index({'text':{'query': query}})
        lst = list(result.keys())
        lst.sort()
                                                                                                                                                 
        expected_lst = list(expected)
        expected_lst.sort()

        self.assertEqual( lst, expected_lst , \
            'Query: "%s", got: %s, expected: %s' % (query, lst, expected))

        return lst

    def testInterface(self):
        self._init(arguments(splitter_casefolding=1))
        verifyClass(PluggableIndexInterface, self._index.__class__)


    def testCaseFoldingOn(self):

        self._init(arguments(
                splitter_casefolding = 1              
                ))

        self.search('text',   [1] )
        self.search('simple', [1] )
        self.search('quick',  [2] )
        self.search('brown',  [2] )
        self.search('QUICK',  [2] )
        self.search('BROWN',  [2] )

    def testCaseFoldingOff(self):

        self._init(arguments(
                splitter_casefolding = 0              
                ))

        self.search('text',   [1] )
        self.search('simple', [1] )
        self.search('quick',  []  )
        self.search('brown',  []  )
        self.search('QUICK',  [2] )
        self.search('BROWN',  [2] )


    def testRightTruncation(self):

        self._init(arguments(
                splitter_casefolding = 1
                ))

        self.search('te*',  [1] )
        self.search('sim*', [1] )
        self.search('qu*',  [2] )
        self.search('br*',  [2] )
        self.search('QU*',  [2] )
        self.search('BR*',  [2] )

    def testLeftTruncation(self):

        self._init(arguments(
                splitter_casefolding = 1,
                truncate_left=1
                ))

        self.search('*ple',  [1] )
        self.search('*en', [3] )
        self.search('*s', [1,2,5] )

    def testStopWords(self):
        from Products.TextIndexNG2.Stopwords import Stopwords

        self._init(arguments(
                splitter_casefolding = 1,
                use_stopwords = Stopwords('dummy',('quick','brown','fox'))
                ))
        
        self.search('QUICK',  []  )
        self.search('quick',  []  )
        self.search('dog',    [2] )
        

    def testCombinedQueriesGlobbingOff(self):

        self._init(arguments(
                splitter_casefolding = 1,
                ))

        self.search('simple and text',  [1] )
        self.search('lazy or alle',     [2,3,4] )
        self.search('alle and sucks',   [] )

    def testCombinedQueriesGlobbingOn(self):

        self._init(arguments(
                splitter_casefolding = 1,
                ))

        self.search('simple and t*',    [1] )
        self.search('lazy or alle',     [2,3,4] )
        self.search('alle and sucks',   [] )
        self.search('brow* or all*',    [2,3,4] )



def test_suite():
   return unittest.makeSuite(Tests)

def main():
   unittest.TextTestRunner().run(test_suite())

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')
   
if __name__=='__main__':
   if len(sys.argv) > 1:
      globals()[sys.argv[1]]()
   else:
      main()

