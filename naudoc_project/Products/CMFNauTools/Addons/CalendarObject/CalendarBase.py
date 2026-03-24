# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/CalendarObject/CalendarBase.py
# Compiled at: 2005-09-01 11:34:32
"""
Calendar implementation.

$Editor: vpastukhov $
$Id: CalendarBase.py,v 1.2 2005/09/01 07:34:32 vsafronovich Exp $
"""
__version__ = '$Revision: 1.2 $'[11:-2]
from types import IntType
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import Features, Exceptions
from Products.CMFNauTools.interfaces import IDirectory
from Products.CMFNauTools.Utils import InitializeClass

class CalendarResource:
    __module__ = __name__
    keys = [
     'calendar']

    def identify(portal, object):
        if object.implements('isCalendar'):
            root = object
        else:
            raise TypeError, object
        if not root.implements('isPortalContent'):
            raise TypeError, root
        uid = {'uid': (root.getUid())}
        return uid
        return

    def lookup(portal, uid=None, entry=None, **kwargs):
        catalog = getToolByName(portal, 'portal_catalog')
        results = catalog.unrestrictedSearch(nd_uid=str(uid))
        if len(results) == 1:
            object = results[0].getObject()
            if object is None:
                raise Exceptions.LocatorError('content', uid)
        else:
            raise Exceptions.LocatorError('content', uid)
        if entry:
            object = object.getEntry(entry)
        return object
        return


def initialize(context):
    context.registerResource('calendar', CalendarResource, moniker='content', features=['isCalendar'])
    return
