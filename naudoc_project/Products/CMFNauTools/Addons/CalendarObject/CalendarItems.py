# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/CalendarObject/CalendarItems.py
# Compiled at: 2005-04-07 14:35:57
from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from DateTime import DateTime
from Products.ZCatalog.Catalog import Catalog
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.CMFNauTools import Features
from Products.CMFNauTools.SimpleObjects import ContentBase, ContainerBase, InstanceBase
from Products.CMFNauTools.Utils import InitializeClass, cookId
from Products.CMFNauTools.Config import Permissions

class CalendarCatalogBase:
    __module__ = __name__

    def state(self):
        return ''
        return

    def priority(self):
        return ''
        return

    def ready_proc(self):
        return ''
        return

    def date(self):
        return self._date
        return

    def creator(self):
        return self._creator
        return

    def topic(self):
        return self._topic
        return


class CalendarNote(InstanceBase, CalendarCatalogBase):
    __module__ = __name__
    meta_type = 'Calendar Note'
    __resource_type__ = 'calendar'
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)
    _class_version = 1.0

    def __init__(self, id, title, text, date, public=0, topic=None):
        InstanceBase.__init__(self, id)
        self._title = title
        self._text = text
        self._date = date
        self.__public = public
        self._creator = _getAuthenticatedUser(self).getUserName()
        self._topic = topic
        return

    def title(self):
        return self._title
        return

    def getNoteText(self):
        return self._text
        return

    def isPublic(self):
        return self.__public
        return

    def _setPublic(self, public):
        self.__public = public
        return

    def isNote__(self):
        return True
        return


InitializeClass(CalendarNote)

class CalendarTask(CalendarNote):
    __module__ = __name__
    meta_type = 'Calendar Task'
    __resource_type__ = 'calendar'
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)
    _class_version = 1.0

    def __init__(self, id, title, text, date, priority, state, ready_proc, public=0):
        CalendarNote.__init__(self, id, title, text, date, public, '')
        self._priority = priority
        self._state = state
        self._ready_proc = ready_proc
        return

    def title(self):
        return self._title
        return

    def isNote__(self):
        return False
        return

    def state(self):
        return self._state
        return

    def setState(self, state):
        cal = aq_parent(aq_inner(self))
        if state in cal.listCalendarTaskStates():
            self._state = state
        return

    def priority(self):
        return self._priority
        return

    def setPriority(self, pr):
        if int(pr) in (1, 2, 3):
            self._priority = int(pr)
        return

    def getTaskText(self):
        return self._text
        return

    def getTaskPlanDate(self, to_str=False):
        """
           return DateTime object or string in Russian format dd.mm.yyyy hh:mm   (!)
        """
        return self.date()
        date_str_rus = '%s.%s.%s' % (self._d, self._m, self._y)
        date_str = '%s.%s.%s' % (self._y, self._m, self._d)
        if to_str:
            return date_str_rus
        else:
            return DateTime(date_str)
        return

    def ready_proc(self):
        return self._ready_proc
        return

    def setReadyProc(self, proc):
        if int(proc) >= 0 and int(proc) <= 100:
            self._ready_proc = proc
        return

    def __str__(self):
        return 'str str  str str str str'
        return


InitializeClass(CalendarTask)
