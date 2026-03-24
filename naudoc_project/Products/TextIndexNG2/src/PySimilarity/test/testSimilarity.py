###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import sys, os, unittest, gzip
import Similarity

__basedir__ = os.getcwd()

class TestBase(unittest.TestCase):

    algorithm = 'foo'

    def testSimple(self):

        assert self.algorithm in Similarity.availableAlgorithms()
        func = getattr(Similarity, self.algorithm)
        self.assertEqual(func([]), [])

    def testComplex(self):

        lines = gzip.GzipFile(os.path.join(__basedir__,self.algorithm + '.txt.gz')).readlines()
        func = getattr(Similarity, self.algorithm)

        for l in lines:
            k,v = l.split()
            self.assertEqual(func(k), v)
            self.assertEqual(func([k]), [v])


class MetaphoneTests(TestBase):
    algorithm = 'soundex'

class SoundexTests(TestBase):
    algorithm = 'soundex'


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(MetaphoneTests))
    s.addTest(unittest.makeSuite(SoundexTests))
    return s

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

