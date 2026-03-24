###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Logger wrapper

$Id: logger.py,v 1.1.1.1 2004/09/20 12:10:01 vpastukhov Exp $
"""

import os 
import logging1

from Products.TextIndexNG2 import __file__ as package_home

package_home = os.path.dirname(package_home)
logging1.fileConfig(os.path.join(package_home,"textindexng_log.ini"))


class logger:
    
    _debug = 0

    def __init__(self):
        self._log = logging1.getLogger("TextIndexNG")
        env = os.environ.get("TEXTINDEXNG_DEBUG",0)
        if str(env) in ("1","on"):
            self._debug = 1

    def debug(self, *args, **kw):
        if self._debug:
            self._log.debug(*args, **kw)

    def debug_on(self): self._debug = 1
    def debug_off(self): self._debug = 0

    def status(self): return self._debug

LOG = logger()        
