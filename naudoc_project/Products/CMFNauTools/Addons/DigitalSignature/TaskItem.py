# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DigitalSignature/TaskItem.py
# Compiled at: 2008-10-22 13:21:33
""" 
$Id: TaskItem.py,v 1.2 2008/10/22 09:21:33 oevsegneev Exp $

$Editor: oevsegneev $

"""
__version__ = '$Revision: 1.2 $'[11:-2]
from Products.CMFNauTools.TaskItem import TaskItemBase
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from utils import class_patch
signable_types = (
 'signature_request',)

class TaskItemBase_patch(class_patch):
    """ 
        Patch of TaskItem.
    """
    __module__ = __name__
    security = ClassSecurityInfo()
    security.declareProtected(CMFCorePermissions.View, 'isSignable')

    def isSignable(self):
        return self.BrainsType() in signable_types
        return

    security.declareProtected(CMFCorePermissions.View, 'signAndRespond')

    def signAndRespond(self, status, text='', attachments=None, documents=None, close_report=None, sign_cont=None, REQUEST=None):
        """
        """
        self.Respond(status=status, text=text, attachments=attachments, documents=documents, close_report=close_report, REQUEST=REQUEST)
        base = self.getBase()
        base.addSignature(sign_cont, task=self, response_id=REQUEST.get('response_id'))
        return


def initialize(context):
    TaskItemBase_patch(TaskItemBase, backup=True)
    return
