# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/CalendarObject/Calendar.py
# Compiled at: 2008-10-15 16:35:59
from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from DateTime import DateTime
from Products.ZCatalog.Catalog import Catalog
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.CMFNauTools import Features
from Products.CMFNauTools.Features import createFeature
from Products.CMFNauTools.SimpleObjects import ContentBase, ContainerBase, ItemBase
from Products.CMFNauTools.Utils import InitializeClass, cookId
from Products.CMFNauTools.Config import Permissions
from CalendarItems import CalendarNote, CalendarTask
import CalendarTool
CalendarType = {'id': 'Calendar', 'meta_type': 'Calendar', 'title': 'Calendar', 'description': 'Calendar', 'icon': 'calendar_object.gif', 'product': 'CMFNauTools', 'factory': 'addCalendar', 'permissions': (CMFCorePermissions.ManagePortal,), 'actions': ({'id': 'view', 'name': 'View', 'action': 'calendar_view', 'permissions': (CMFCorePermissions.View,)}, {'id': 'settings', 'name': 'Change settings', 'action': 'calendar_setting', 'permissions': (ZopePermissions.change_configuration,)})}

class Calendar(ContainerBase, ContentBase, ZCatalog):
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Calendar'
    portal_type = 'Calendar'
    __resource_type__ = 'calendar'
    __implements__ = (
     createFeature('isCalendar'), Features.isPortalContent, Features.isItemsRealm, Features.isAttributesProvider, ContentBase.__implements__, ContainerBase.__implements__)
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)
    security.declareProtected(CMFCorePermissions.View, 'this', 'title_or_id', 'title_and_id')
    manage_options = ZCatalog.manage_options
    _properties = ContentBase._properties
    _catalogAddIndex = ZCatalog.addIndex
    _catalogDeleteIndex = ZCatalog.delIndex
    _catalog_indexes = [('id', 'FieldIndex'), ('date', 'FieldIndex'), ('title', 'FieldIndex'), ('creator', 'FieldIndex'), ('isPublic', 'FieldIndex'), ('topic', 'FieldIndex'), ('isNote__', 'FieldIndex'), ('priority', 'FieldIndex'), ('state', 'FieldIndex'), ('ready_proc', 'FieldIndex')]
    _catalog_metadata = [
     9, 11, 12, 13, 14, 15]
    _entry_factory = CalendarNote
    _default_setting = {'view_month_select': 1, 'view_month_list': 1, 'week_mode': 'short', 'len_of_text': 55, 'popup_full_text': 1, 'week_table_mode_only_title': 1, 'show_holidays_together': 1, 'show_tasks_month_view': 1, 'public_default_check': 0, 'calendar_skin_version': '1.0'}
    _task_states = [
     34, 35, 36, 37, 38]
    manage_catalogView = ZCatalog.manage_catalogView

    def __init__(self, id, title, **kwargs):
        ContentBase.__init__(self, id, title, **kwargs)
        self.topics = []
        return

    def _instance_onCreate(self):
        self._catalog = Catalog()
        self._catalogInit()
        self._setting = self._default_setting
        return

    def __call__(self, REQUEST=None):
        """
            Invokes the default view.
        """
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('CalendarObject'):
            msg = getToolByName(self, 'msg')
            return msg('sentinel.trial_expired') % msg('"Calendar" object type')
        else:
            return ContentBase.__call__(self, REQUEST)
        return

    def getSetting(self):
        """
            return all current calendar settings
        """
        return self._setting
        return

    def getSettingById(self, id):
        """
            return specify setting
        """
        return self._setting.get(id, None)
        return

    def getDefaultSetting(self):
        """
            return default calendar setting
        """
        return self._default_setting
        return

    def setSetting(self, **kwargs):
        """
            Set setting for calendar
            Arguments:
                kwargs in format: <setting id>=<setting value>,...
        """
        old_setting = self.getSetting()
        for (setting_id, setting_value) in kwargs.items():
            if old_setting.has_key(setting_id) and old_setting[setting_id] != setting_value:
                self._setting[setting_id] = setting_value

        self._p_changed = 1
        return

    def listTopics(self):
        """
            return list of topics
        """
        return self.topics
        return

    def listCalendarTaskStates(self):
        return self._task_states
        return

    def addTopic(self, topic):
        """
            add topic. (Will be added new topic only)
        """
        topics_old = self.listTopics()
        if topic not in topics_old and topic is not None and topic != '':
            topics_old.append(topic)
            self.topics = topics_old
        return

    def getNote(self, id):
        try:
            note = self._getOb(id)
        except:
            note = None

        if not note.isNote__():
            note = None
        return note
        return

    security.declareProtected(Permissions.CreateObjectVersions, 'addNote')

    def addNote(self, title, text, y, m, d, public=0, topic=None):
        """
            add item (note) to calendar.
            Parameters:
                title      -    item title (string)
                text       -    item text  (string)
                y          -    year from item assigned date (integer)
                m          -    month number from item assigned date (integer)
                d          -    day from item assigned date (integer)                
                public     -    is note public (bool)
                topic      -    note topic
        """
        id = cookId(self, title=title)
        if topic not in self.listTopics():
            self.addTopic(topic)
        date = DateTime('%s/%s/%s' % (y, m, d))
        item = self._entry_factory(id, title, text, date, public, topic)
        self.addObject(item)
        self._catalog.catalogObject(item, item.getId())
        return

    security.declareProtected(Permissions.CreateObjectVersions, 'delNote')

    def delNote(self, ids):
        """
            Delete item with specify ids
            Parameters:
                ids - string or list with note id(s)
        """
        ids = list(ids)
        self.deleteObjects(ids)
        for id in ids:
            self._catalog.uncatalogObject(id)

        return

    security.declareProtected(Permissions.CreateObjectVersions, 'changeNote')

    def changeNote(self, id, title, text, is_public, topic):
        note = self._getOb(id)
        note._title = title
        note._text = text
        note._setPublic(is_public)
        if topic not in self.listTopics():
            self.addTopic(topic)
        note._topic = topic
        self._catalog.catalogObject(note, note.getId())
        return

    def listItemsForDate(self, y, m, d=None, filter_topic=''):
        """
            Return list of allowed items (catalog objects) for specify date
            if day is not specify than return all items for month.            
            
            Arguments:
                'y' - year (int)
                'm' - month number (int)
                'd' - day (int)
                'filter_topic' - notes with it topic are returned, if topic is empty string - all
                                 find notes will be returned
            Result:
                list of calendar items (catalog objects)
        """
        result = []
        mstool = getToolByName(self, 'portal_membership')
        username = mstool.getAuthenticatedMember().getUserName()
        if d:
            str_date = '%s/%s/%s' % (y, m, d)
            begin_date = DateTime(str_date).earliestTime()
            end_date = DateTime(str_date).latestTime()
        else:
            str_date_begin = '%s/%s/%s' % (y, m, 1)
            str_date_end = '%s/%s/%s' % (y, m, self.monthLength(y, m))
            begin_date = DateTime(str_date_begin).earliestTime()
            end_date = DateTime(str_date_end).latestTime()
        kw = {}
        kw['date'] = [begin_date, end_date]
        kw['date_usage'] = 'range:min:max'
        kw['isNote__'] = True
        if filter_topic:
            kw['topic'] = filter_topic
        result = self._catalog.searchResults(**kw)
        return [_[1] for res in result if res['creator'] == username or res['isPublic']]
        return

    def listNotesForDate(self, y, m, d=None, filter_topic=''):
        """
            return list of notes information dicts for specify date,
            if day is not specify than return all notes for month.            
            Arguments:
                'y' - year (int)
                'm' - month number (int)
                'd' - day (int)
                'filter_topic' - notes with it topic are returned, if topic is empty string - all
                                 find notes will be returned

            Result:
                list of items information dicts, in format:
                    {id:    <note id>,
                     title: <note title>,
                     text:  <note text>  }

        """
        items = self.listItemsForDate(y, m, d=d, filter_topic=filter_topic)
        returned = []
        for item in items:
            returned.append({'id': (item['id']), 'title': (item['title']), 'text': (item.getObject().getNoteText()), 'topic': (item['topic']), 'creator': (item['creator']), 'isPublic': (item['isPublic'])})

        return returned
        return

    def listDayWithNotes(self, y, m):
        """
            return list with days which has one or more notes for specify year and month.
            Arguments:
                'y'  -  year (int)
                'm'  -  month number (int)
        
        """
        res = self.listItemsForDate(y=y, m=m)
        returned = {}
        for r in res:
            returned[r['date'].day()] = 1

        return returned.keys()
        return

    def listTasksForDate(self, y, m, d=None):
        """
            return catalog task brains, assigned to current user and actuality for specify date
            Arguments:
                y   -  year (integer or string)
                m   -  month number (integer or string)
                d   -  day (integer or string)

        """
        fup_tool = getToolByName(self, 'portal_followup')
        mstool = getToolByName(self, 'portal_membership')
        username = mstool.getAuthenticatedMember().getUserName()
        tasks = [_[1] for t in fup_tool.searchTasks() if username in t['InvolvedUsers']]
        cur_date_str = '%s/%s/%s' % (y, m, d)
        cur_date = DateTime(cur_date_str)
        results = []
        for task in tasks:
            begin_date = task['effective'].earliestTime()
            end_date = task['expires'].latestTime()
            if cur_date <= end_date and cur_date >= begin_date:
                results.append(task)

        return results
        return

    def listTasksForWeek(self, y, m, w):
        """
            return info about tasks actuality in specify week,
            assigned to current user and actuality for specify week
            Arguments:
                y   -  year (integer or string)
                m   -  month number (integer or string)
                w   -  number of the week of the month (integer or string)
            return:
                [{'task':<catalog task brain>,
                  'task_days': DateTime objects list 
                 },
                 ...
                ]
        """
        info = []
        week_info = self.getWeekInfo(y, m, w)
        fup_tool = getToolByName(self, 'portal_followup')
        mstool = getToolByName(self, 'portal_membership')
        username = mstool.getAuthenticatedMember().getUserName()
        tasks = [_[1] for t in fup_tool.searchTasks() if username in t['InvolvedUsers']]
        for task in tasks:
            begin_date = task['effective'].earliestTime()
            end_date = task['expires'].latestTime()
            task_days = []
            for day in week_info:
                if day <= end_date and day >= begin_date:
                    task_days.append(day)

            if task_days:
                info.append({'task': task, 'task_days': task_days})

        return info
        return

    security.declareProtected(Permissions.CreateObjectVersions, 'addCalendarTask')

    def addCalendarTask(self, title, text, y, m, d, priority, status, ready_proc, public=0):
        id = cookId(self, title=title)
        item = CalendarTask(id, title, text, DateTime('%s/%s/%s' % (y, m, d)), priority, status, ready_proc, public)
        self.addObject(item)
        self._catalog.catalogObject(item, item.getId())
        return

    def listCalendarTasks(self, **kw):
        mstool = getToolByName(self, 'portal_membership')
        username = mstool.getAuthenticatedMember().getUserName()
        result = self._catalog.searchResults(isNote__=False, **kw)
        return [_[1] for res in result if res['creator'] == username or res['isPublic']]
        return

    security.declareProtected(Permissions.CreateObjectVersions, 'changeTask')

    def changeTask(self, id, title, text, y, m, d, priority, state, ready_proc, is_public=0):
        task = self._getOb(id)
        task._title = title
        task._text = text
        task._date = DateTime('%s/%s/%s' % (y, m, d))
        if int(priority) in (1, 2, 3):
            task._priority = priority
        if state in self.listCalendarTaskStates():
            task._state = state
        task._setPublic(is_public)
        task._ready_proc = ready_proc
        self._catalog.catalogObject(task, task.getId())
        return

    def getTask(self, id):
        try:
            task = self._getOb(id)
        except:
            task = None

        if task.isNote__():
            task = None
        return task
        return

    security.declareProtected(Permissions.CreateObjectVersions, 'delTasks')

    def delTasks(self, ids):
        """
            Delete item with specify ids
            Parameters:
                ids - string or list with note id(s)
        """
        ids = list(ids)
        self.deleteObjects(ids)
        for id in ids:
            self._catalog.uncatalogObject(id)

        return

    def _catalogInit(self):
        for (iname, itype) in self._catalog_indexes:
            self._catalogAddIndex(iname, itype)

        for iname in self._catalog_metadata:
            self._catalog.addColumn(iname)

        return

    firstDayOfMonth = CalendarTool.firstDayOfMonth
    lastDayOfMonth = CalendarTool.lastDayOfMonth
    isYearLeap = CalendarTool.isYearLeap
    monthLength = CalendarTool.monthLength
    getShortWeekInfo = CalendarTool.getShortWeekInfo
    getWeekInfo = CalendarTool.getWeekInfo
    firstDayNumberOfWeek = CalendarTool.firstDayNumberOfWeek
    getMonthInfo = CalendarTool.getMonthInfo


InitializeClass(Calendar)

def addCalendar(self, id, title='', REQUEST=None, **kwargs):
    """
        Add a Calendar
    """
    self._setObject(id, Calendar(id, title, **kwargs))
    if REQUEST is not None:
        return self[id].redirect(message='Calendar added.', REQUEST=REQUEST)
    return


def initialize(context):
    context.registerContent(Calendar, addCalendar, CalendarType, activate=False)
    return
