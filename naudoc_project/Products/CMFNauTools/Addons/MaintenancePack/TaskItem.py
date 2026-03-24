# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/MaintenancePack/TaskItem.py
# Compiled at: 2009-03-10 17:19:28
""" 
$Id: TaskItem.py,v 1.3 2009/03/10 14:19:28 oevsegneev Exp $

$Editor: oevsegneev $

"""
__version__ = '$Revision: 1.3 $'[11:-2]
from types import StringType
from Products.CMFNauTools.TaskItem import TaskItemBase
from Products.CMFNauTools.Utils import flattenString
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from utils import class_patch

class TaskItemBase_patch(class_patch):
    """ 
        Patch of TaskItem.
    """
    __module__ = __name__

    def send_mail(self, members, template_name, **kwargs):
        msg = getToolByName(self, 'msg')
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        template = getattr(self, template_name)
        portal_notifications = None
        if hasattr(self, 'portal_notifications'):
            portal_notifications = getToolByName(self, 'portal_notifications')
        if portal_sentinel.checkAction('MaintenancePack') and portal_notifications and portal_notifications.hasNotification(template):
            default_subject = msg('%s.subject' % template)
            over_subject = None
            if self.BrainsType() in ('directive', 'information'):
                over_subject = portal_notifications.getSubject(template)
            kwargs['over_subject'] = (over_subject or default_subject) % {'task_title': (flattenString(self.Title()))}
        TaskItemBase.old_send_mail(self, members, template_name, **kwargs)
        return


def initialize(context):
    TaskItemBase_patch(TaskItemBase, backup=True)
    return
