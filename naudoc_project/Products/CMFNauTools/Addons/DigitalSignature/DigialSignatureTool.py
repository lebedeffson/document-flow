# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DigitalSignature/DigialSignatureTool.py
# Compiled at: 2008-05-13 12:49:14
"""
DigitalSignature -- service class for digital signature

$Editor: oevsegneev $
$Id: DigialSignatureTool.py,v 1.2 2008/05/13 08:49:14 oevsegneev Exp $
"""
__version__ = '$Revision: 1.2 $'[11:-2]
from AccessControl import ClassSecurityInfo
from Globals import PersistentMapping
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFNauTools.ActionInformation import ActionInformation as AI
from Products.CMFNauTools.SimpleObjects import ToolBase
from Products.CMFNauTools.Utils import InitializeClass
from Products.CMFNauTools.SimpleObjects import Persistent

class DigitalSignatureTool(ToolBase):
    """
        Digital signature service class.
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Digital Signature Tool'
    id = 'portal_signature'
    security = ClassSecurityInfo()
    _actions = ToolBase._actions + (AI(id='manageDigitalSignature', title='Manage Digital Signature', action=Expression(text='string: ${portal_url}/manage_signature_form'), category='global', permissions=(CMFCorePermissions.ManagePortal,), visible=1),)

    def __init__(self):
        """
            Creates new instance and sets to default all properties.
            
            Arguments:
                
                'id' -- identifier
                'title' -- object's title
            
        """
        ToolBase.__init__(self)
        self._properties = PersistentMapping()
        self._properties.update({'csp_type': 0, 'csp_name': '', 'sign_alg_id': '', 'hash_alg_id': '', 'key_length': 0, 'include_attachments': 0})
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'editProperties')

    def editProperties(self, REQUEST):
        """
        """
        for key in self._properties.keys():
            if REQUEST.has_key(key):
                self._properties[key] = REQUEST.get(key)

        return

    security.declareProtected(CMFCorePermissions.View, 'getProperties')

    def getProperty(self, id):
        """
        """
        return self._properties.get(id)
        return


InitializeClass(DigitalSignatureTool)

def initialize(context):
    context.registerTool(DigitalSignatureTool)
    return
