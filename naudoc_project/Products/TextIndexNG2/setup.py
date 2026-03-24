#!/usr/bin/env python

###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

from distutils.core import setup,Extension


setup(name = "TextIndexNGExtensions",
      version = "1.09",
      author = "Andreas Jung",
      author_email = "andreas@andreas-jung.com",
	  ext_modules=[

            Extension("normalizer",
                [ "src/normalizer/normalizer.c" ],
            ),

            Extension("TXNGSplitter",
                [ "src/TXNGSplitter/TXNGSplitter.c",
                  "src/TXNGSplitter/hashtable.c",
                  "src/TXNGSplitter/dict.c" 
                ],
            ),


            Extension("indexsupport",
                [ "src/indexsupport.c" ],
            ),

            Extension("Similarity",
                [ "src/PySimilarity/src/Similarity.c",
                  "src/PySimilarity/src/metaphone.c",
                  "src/PySimilarity/src/double_metaphone.c",
                  "src/PySimilarity/src/soundex.c",
                  "src/PySimilarity/src/levenshtein.c", ],
            ),

            Extension("Stemmer",
                [ "src/PyStemmer/src/Stemmer.c",
                  "src/PyStemmer/q/french.c",
                  "src/PyStemmer/q/porter.c",
                  "src/PyStemmer/q/german.c",
                  "src/PyStemmer/q/dutch.c",
                  "src/PyStemmer/q/finnish.c",
                  "src/PyStemmer/q/english.c",
                  "src/PyStemmer/q/spanish.c",
                  "src/PyStemmer/q/italian.c",
                  "src/PyStemmer/q/swedish.c",
                  "src/PyStemmer/q/portuguese.c",
                  "src/PyStemmer/q/russian.c",
                  "src/PyStemmer/q/danish.c",
                  "src/PyStemmer/q/norwegian.c",
                  "src/PyStemmer/q/api.c",
                  "src/PyStemmer/q/utilities.c" ],
                  include_dirs=['src/PyStemmer/q','.','src/PyStemmer']
            ),
        ]
	)


extLevensthein = Extension('Levenshtein',
                           sources = ['src/python-Levenshtein-0.7/Levenshtein.c'],
                           extra_compile_args = ['-Wall']) #['-ggdb', '-O0'])

setup (name = 'python-Levenshtein',
       version = '0.7',
       description = 'Python extension computing string distances and similarities.',
       author = 'David Necas (Yeti)',
       author_email = 'yeti@physics.muni.cz',
       license = 'GNU GPL',
       url = 'http://trific.ath.cx/python/levenshtein/',
       long_description = '''
Levenshtein computes Levenshtein distances, similarity ratios, generalized
medians and set medians of Strings and Unicodes.  Becuase it's implemented
in C, it's much faster than corresponding Python library functions and
methods.
''',
       ext_modules = [extLevensthein])

