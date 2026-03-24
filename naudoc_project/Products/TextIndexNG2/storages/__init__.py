# check for converter modules

import os
from Products.TextIndexNG2.Registry import StorageRegistry

storages = os.listdir(__path__[0])
storages = [ x for x in storages  if x.endswith('.py') and x!='__init__.py']

for st in storages:

    st = st[:-3]
    mod = __import__(st, globals(), globals(), __path__)
    if not hasattr(mod,'Storage'): continue

    storage = mod.Storage
    StorageRegistry.register(st, storage)

del storages
