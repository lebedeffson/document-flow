# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/LDAP/LDAPUserFolder.py
# Compiled at: 2008-12-05 14:22:33
"""
LDAPUserFolder class patch.

$Id: LDAPUserFolder.py,v 1.1 2008/12/05 11:22:33 oevsegneev Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import Config
if Config.UseLDAPUserFolder:
    from Products.LDAPUserFolder import LDAPUserFolder
from utils import class_patch

class LDAPUserFolder_patch(class_patch):
    """
        LDAPUserFolder patch
    """
    __module__ = __name__

    def getUserNames(self):
        """ 
        """
        now = time()
        if self._v_userlist_expire > now:
            return self._v_userlist
        msg = getToolByName(self, 'msg')
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('LDAP'):
            return []
        return self.old_getUserNames()
        return


def initialize(context):
    LDAPUserFolder_patch(LDAPUserFolder, backup=True)
    return
