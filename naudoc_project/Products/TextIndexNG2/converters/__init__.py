# check for converter modules

import os
from Products.TextIndexNG2.Registry import ConverterRegistry

converters = os.listdir(__path__[0])
converters = [ c for c in converters if c.endswith('.py') and c!='__init__.py' ]

for cv in converters:

    cv = cv[:-3]
    mod = __import__(cv, globals(), globals(), __path__)
    if not hasattr(mod,'Converter'): continue

    converter = mod.Converter()
    for t in converter.getType():
        ConverterRegistry.register(t, converter)

del converters
