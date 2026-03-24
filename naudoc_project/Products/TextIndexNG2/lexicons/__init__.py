# check for converter modules

import os
from Products.TextIndexNG2.Registry import LexiconRegistry

lexicons = os.listdir(__path__[0])
lexicons = [ x for x in lexicons  if x.endswith('.py') and x!='__init__.py' ]

for lex in lexicons:

    lex = lex [:-3]
    mod = __import__(lex, globals(), globals(), __path__)
    if not hasattr(mod,'Lexicon'): continue

    lexicon = mod.Lexicon
    if not LexiconRegistry.is_registered(lex):
        LexiconRegistry.register(lex, lexicon)

del lexicons
