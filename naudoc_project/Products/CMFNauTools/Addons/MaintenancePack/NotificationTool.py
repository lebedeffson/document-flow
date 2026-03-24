# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/MaintenancePack/NotificationTool.py
# Compiled at: 2009-03-10 16:38:45
"""
Notifications -- service class for mail notifications control

$Editor: oevsegneev $
$Id: NotificationTool.py,v 1.2 2009/03/10 13:38:45 oevsegneev Exp $
"""
__version__ = '$Revision: 1.2 $'[11:-2]
from AccessControl import ClassSecurityInfo
from cgi import escape
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.ActionInformation import ActionInformation as AI
from Products.CMFNauTools.Exceptions import SentinelError
from Products.CMFNauTools.SimpleObjects import ToolBase, Persistent
from Products.CMFNauTools.Utils import InitializeClass

class NotificationsTool(ToolBase):
    """
        Mail notifications service class.
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Notifications Tool'
    id = 'portal_notifications'
    security = ClassSecurityInfo()
    _actions = ToolBase._actions + (AI(id='manageNotifications', title='Manage Notifications', action=Expression(text='string: ${portal_url}/manage_notifications_form'), category='global', permissions=(CMFCorePermissions.ManagePortal,), visible=1),)

    def __init__(self):
        """
            Creates new instance and sets to default all properties.
            
            Arguments:
                
                'id' -- identifier
                'title' -- object's title
            
        """
        ToolBase.__init__(self)
        self.resetNotifications()
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'resetNotifications')

    def resetNotifications(self):
        self._notifications = {'task.alarm': {'subject': '', 'order': 0, 'active': 1}, 'task.directive_accepted': {'subject': '', 'order': 1, 'active': 1}, 'task.directive_committed': {'subject': '', 'order': 2, 'active': 1}, 'task.directive_failed': {'subject': '', 'order': 3, 'active': 1}, 'task.directive_rejected': {'subject': '', 'order': 4, 'active': 1}, 'task.directive_user_excluded': {'subject': '', 'order': 5, 'active': 1}, 'task.directive_user_included': {'subject': '', 'order': 6, 'active': 1}, 'task.finalized': {'subject': '', 'order': 7, 'active': 1}, 'task.info_user_informed': {'subject': '', 'order': 8, 'active': 1}, 'task.inform_changes': {'subject': '', 'order': 9, 'active': 1}, 'task.notify_users': {'subject': '', 'order': 10, 'active': 1}, 'task.reviewed': {'subject': '', 'order': 11, 'active': 1}, 'task.supervisor_cancelled': {'subject': '', 'order': 12, 'active': 1}, 'task.supervisor_notify': {'subject': '', 'order': 13, 'active': 1}}
        self._p_changed = 1
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'editNotifications')

    def editNotifications(self, REQUEST):
        """
        """
        msg = getToolByName(self, 'msg')
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('MaintenancePack'):
            raise SentinelError, msg('sentinel.trial_expired') % msg('Maintenance Pack Addon')
        for key in self._notifications.keys():
            if REQUEST.has_key(key):
                self._notifications[key]['subject'] = REQUEST.get(key)
            self._notifications[key]['active'] = REQUEST.get('%s_active' % key, 0)

        self._p_changed = 1
        return

    security.declareProtected(CMFCorePermissions.View, 'getSubject')

    def getSubject(self, id):
        """
        """
        return self._notifications.get(id)['subject']
        return

    security.declareProtected(CMFCorePermissions.View, 'isActive')

    def isActive(self, id):
        """
        """
        return self._notifications.get(id)['active']
        return

    security.declareProtected(CMFCorePermissions.View, 'hasNotification')

    def hasNotification(self, id):
        """
        """
        return self._notifications.has_key(id)
        return

    security.declareProtected(CMFCorePermissions.View, 'listNotifications')

    def listNotifications(self, sort=True):
        """
        """
        notifications = self._notifications.keys()
        if sort:
            notifications.sort((lambda x, y: cmp(self._notifications[x]['order'], self._notifications[y]['order'])))
        return notifications
        return


InitializeClass(NotificationsTool)

def initialize(context):
    context.registerTool(NotificationsTool)
    return
