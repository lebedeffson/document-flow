# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DirectoryObject/DirectoryError.py
# Compiled at: 2004-09-03 19:16:03
"""
Directory exception class.

$Editor: vpastukhov $
$Id: DirectoryError.py,v 1.1 2004/09/03 15:16:03 vpastukhov Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
from Products.CMFNauTools.Exceptions import SimpleError

class DirectoryError(SimpleError):
    __module__ = __name__
    code_prefix = 'directories'
