##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Scripts in a web-configurable workflow.

$Id: Scripts.py,v 1.3.20.2 2005/03/16 17:57:54 sidnei Exp $
"""

from OFS.Folder import Folder
import Globals
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal

from ContainerTab import ContainerTab


class Scripts (ContainerTab):

    meta_type = 'Workflow Scripts'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    def manage_main(self, client=None, REQUEST=None, **kw):
        '''
        '''
        kw['management_view'] = 'Scripts'
        return Folder.manage_main(self, client, REQUEST, **kw)

Globals.InitializeClass(Scripts)
