"""
$Id: fix_root_tasks.py,v 1.2 2008/03/04 11:05:28 oevsegneev Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = 'Fix root tasks'
version = '3.2.1.4'
after_script = 1
order = 3

from Products.CMFNauTools.Config import Roles
from Products.CMFNauTools import Features
from Products.CMFCore import CMFCorePermissions

def check( context, object ):
    for task in context.portal.followup.getBoundTasks( recursive=1 ):
        if hasattr(task, '_View_Permission') and Roles.Member not in task._View_Permission:
            return True
    return False

def migrate( context, object ):
    for task in context.portal.followup.getBoundTasks( recursive=1 ):
        if hasattr(task, '_View_Permission') and Roles.Member not in task._View_Permission:
            task.manage_permission( CMFCorePermissions.View, ( Roles.Reader, Roles.Owner, Roles.Manager, Roles.Editor, Roles.Member), 0 )
