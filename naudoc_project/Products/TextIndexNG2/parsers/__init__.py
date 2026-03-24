###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################


# check for parser modules

from Products.TextIndexNG2.Registry import ParserRegistry

import os
_oldcwd = os.getcwd()

os.chdir(__path__[0])
parsers = os.listdir('.')
parsers = [ p   for p in parsers if os.path.isdir(p) and not p in ['CVS'] ]

for p  in parsers:

    mod = __import__(p, globals(), globals(), __path__)

    try: ParserRegistry.register( p, mod.Parser() )
    except: pass

del parsers
os.chdir(_oldcwd)

