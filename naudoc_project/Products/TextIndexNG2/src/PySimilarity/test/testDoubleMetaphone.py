###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import sys, os, unittest, re, gzip
import Similarity

__basedir__ = os.getcwd()

class TestDoubleMetaphone(unittest.TestCase):

    def testSimple(self):

        assert 'double_metaphone' in Similarity.availableAlgorithms()
        func = Similarity.double_metaphone
        self.assertEqual(func([]), [])

    def testComplex(self):

        regex = re.compile("'(.*)'\s+([\w]+)\s+([\w]+)")
        lines = gzip.GzipFile(os.path.join(__basedir__,'double_metaphone.txt.gz')).readlines()

        for l in lines:
            mo  = regex.match(l)
            s,c1,c2 =  mo.groups()
        
            res = Similarity.double_metaphone(s)
            self.assertEqual(res, (c1,c2))


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestDoubleMetaphone))
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

