# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/Sentinel/Sentinel.py
# Compiled at: 2009-02-18 13:04:19
""" 
AddonsTool customization.

$Id: Sentinel.py,v 1.8 2009/02/18 10:04:19 oevsegneev Exp $
$Editor: oevsegneev $

"""
__version__ = '$Revision: 1.8 $'[11:-2]
import md5
from types import TupleType
from AccessControl import ClassSecurityInfo
from Globals import PersistentMapping
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.SimpleObjects import ToolBase
from Products.CMFNauTools.Utils import InitializeClass
from Products.CMFNauTools.AddonsTool import _getAddon
addon_tab = [
 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

class SentinelTool(ToolBase):
    """ 
        Patch of AddonsTool class.
    """
    __module__ = __name__
    _class_version = 1.1
    meta_type = 'Sentinel Tool'
    id = 'portal_sentinel'
    security = ClassSecurityInfo()
    _spots = {}
    _key = ''
    _company = ''

    def __init__(self):
        """
        """
        ToolBase.__init__(self)
        self._spots = PersistentMapping()
        return

    def _initstate(self, mode):
        for k in self._spots.keys():
            if not isinstance(self._spots[k], TupleType) and self._spots[k] > 0:
                self._spots[k] = (
                 self._spots[k], self._spots[k] + 30)

        self._p_changed = 1
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'setActivationKey')

    def setActivationKey(self, REQUEST):
        """
        """
        portal_addons = getToolByName(self, 'portal_addons')
        portal = self.getPortalObject()
        key = REQUEST.get('key', '')
        company = REQUEST.get('company', '')
        if len(key) == 48 and company and self.gd(key, company):
            addon_idxs = self.parseAddons(key)
            spot_range = self.parseRange(key)
            self._key = key
            self._company = company
            for idx in addon_idxs:
                id = addon_tab[idx]
                self.refreshSpot(id, r=spot_range)
                if portal_addons.getAddonProperty(id, 'status') != 'active':
                    try:
                        _getAddon(id).activate(portal)
                        portal_addons._activated_addons[id]['status'] = 'active'
                        portal_addons._activated_addons._p_changed = 1
                    except:
                        pass

            for id in range(len(addon_tab)):
                if id not in addon_idxs and self._spots.has_key(addon_tab[id]) and self._spots[addon_tab[id]] < 0:
                    self.refreshSpot(addon_tab[id])

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_addons_form')
        return

    def gd(self, key, company):
        base = 1000
        vec = []
        for i in range(4):
            vec.append(self.hex_dec(key[i * 2:i * 2 + 2]))

        old = vec[0]
        for x in range(vec[1]):
            old = vec[3] * old % (vec[2] * base)

        hash = md5.new()
        hash.update('%s%s%s' % (key[:16], old, company))
        return hash.hexdigest() == key[16:]
        return

    def parseAddons(self, key):
        prefix = key[8:12]
        num = self.hex_dec(prefix)
        results = []
        for i in range(16):
            if num & 2 ** i:
                results.append(i)

        return results
        return

    def parseRange(self, key):
        prefix = key[12:16]
        value = self.hex_dec(prefix)
        return self.hex_dec(prefix)
        return

    def dec_hex(self, n):
        return '%X' % n
        return

    def hex_dec(self, s):
        return int(s, 16)
        return

    def hex_list(self, s):
        l = []
        for i in range(len(s) / 2):
            l.append(self.hex_dec(s[i * 2:i * 2 + 2]))

        return l
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'checkActivation')

    def checkActivation(self, addon_id):
        portal_addons = getToolByName(self, 'portal_addons')
        spot = self._spots.get(addon_id, None)
        if spot and not isinstance(spot, TupleType) and spot < 0:
            return True
        if not spot:
            self.refreshSpot(addon_id)
        elif spot[0] > self.ZopeTime() or spot[1] < self.ZopeTime() or portal_addons.getAddonProperty(addon_id, 'status') == 'active':
            return False
        return True
        return

    security.declareProtected(CMFCorePermissions.View, 'checkAction')

    def checkAction(self, addon_id):
        spot = self._spots.get(addon_id, None)
        if spot and not isinstance(spot, TupleType) and spot < 0:
            return True
        return not (spot and (spot[0] > self.ZopeTime() or spot[1] < self.ZopeTime()) or not spot)
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getTimeLeft')

    def getTimeLeft(self, addon_id):
        """
        """
        spot = self._spots.get(addon_id, None)
        if spot and isinstance(spot, TupleType):
            days = int(round(spot[1] - self.ZopeTime()))
            return days > 0 and days or 0
        return '--'
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'isLimited')

    def isLimited(self, addon_id):
        portal_addons = getToolByName(self, 'portal_addons')
        spot = self._spots.get(addon_id, None)
        return portal_addons.getAddonProperty(addon_id, 'is_paid') and spot and isinstance(spot, TupleType) and spot[1] - spot[0] > 30
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'isTrial')

    def isTrial(self, addon_id):
        portal_addons = getToolByName(self, 'portal_addons')
        spot = self._spots.get(addon_id, None)
        return portal_addons.getAddonProperty(addon_id, 'is_paid') and (spot and isinstance(spot, TupleType) and spot[1] - spot[0] <= 30 or not spot)
        return

    def refreshSpot(self, id, v=None, r=None, dummy=13):
        s = v or self.ZopeTime()
        r = r and r & 4095
        self._spots[id] = (r or r is None) and (s, s + (r or 17 + dummy)) or -1
        self._p_changed = 1
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getKey')

    def getKey(self):
        return self._key
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getCompany')

    def getCompany(self):
        return self._company
        return


InitializeClass(SentinelTool)

def initialize(context):
    context.registerTool(SentinelTool)
    return
