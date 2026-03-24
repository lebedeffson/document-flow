# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/SiteObject/SiteImage.py
# Compiled at: 2008-10-15 16:48:07
"""
SiteImage class.

$Id: SiteImage.py,v 1.1 2008/10/15 12:48:07 oevsegneev Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
from AccessControl import ClassSecurityInfo
from OFS.Image import Image as OFSImage, cookId
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFDefault.Image import Image
from Products.CMFNauTools import Config, Features
from Products.CMFNauTools.ActionInformation import ActionInformation as AI
from Products.CMFNauTools.Features import createFeature
from Products.CMFNauTools.SimpleNauItem import SimpleNauItem
from Products.CMFNauTools.SyncableContent import SyncableContent
from Products.CMFNauTools.Utils import InitializeClass
SiteImageType = {'id': 'Site Image', 'meta_type': 'Site Image', 'title': 'Image', 'description': 'Image objects can be embedded in Portal documents and added to the external sites.', 'icon': 'image_icon.gif', 'sort_order': 0.8, 'product': 'CMFNauTools', 'factory': 'addSiteImage', 'immediate_view': 'image_edit_form', 'condition': 'python: object.getSite() is not None', 'actions': ({'id': 'view', 'name': 'View', 'action': 'image_view', 'permissions': (CMFCorePermissions.View,)}, {'id': 'edit', 'name': 'Edit', 'action': 'image_edit_form', 'permissions': (CMFCorePermissions.ModifyPortalContent,)}, {'id': 'metadata', 'name': 'Metadata', 'action': 'metadata_edit_form', 'permissions': (CMFCorePermissions.ModifyPortalContent,)})}

def addSiteImage(self, id, title='', file='', content_type='', REQUEST=None, **kwargs):
    """
        Add a Site Image (based on Image.addImage)
    """
    (id, title) = cookId(id, title, file)
    obj = SiteImage(id, title, file='', content_type=content_type, **kwargs)
    self._setObject(id, obj)
    obj = self._getOb(id)
    if file:
        obj.edit(file=file)
    return


class SiteImage(SimpleNauItem, Image, SyncableContent):
    """
        Site Image class
    """
    __module__ = __name__
    _class_version = 1.22
    meta_type = 'Site Image'
    portal_type = 'Site Image'
    security = ClassSecurityInfo()
    __implements__ = (
     createFeature('isSiteImage'), Features.isImage, Features.isExternallyEditable, SimpleNauItem.__implements__, Image.__implements__, SyncableContent.__implements__)
    if Config.UseExternalEditor:
        _actions = (
         AI(id='external_edit', title='Edit using external editor', icon='external_editor.gif', action=Expression('string: ${object_url}/externalEdit'), permissions=(CMFCorePermissions.ModifyPortalContent,), condition=Expression('python: not object.isLocked()'), visible=0),)
    manage_options = SimpleNauItem.manage_options + Image.manage_options
    security.declareProtected(CMFCorePermissions.View, 'index_html')
    index_html = Image.index_html

    def __init__(self, id, title=None, file='', content_type='', **kwargs):
        """
            Initializes class instance.
        """
        SimpleNauItem.__init__(self, id, title, **kwargs)
        Image.__init__(self, id, self.title, description=self.description, file=file, content_type=content_type)
        return

    def _initstate(self, mode):
        if not SimpleNauItem._initstate(self, mode):
            return 0
        if not getattr(self, 'id', None):
            self.id = self.__name__
        return 1
        return

    def _containment_onAdd(self, item, container):
        OFSImage.manage_afterAdd(self, item, container)
        return

    def _instance_onClone(self, source, item):
        OFSImage.manage_afterClone(self, item)
        return

    def _containment_onDelete(self, item, container):
        OFSImage.manage_beforeDelete(self, item, container)
        return


InitializeClass(SiteImage)

def initialize(context):
    context.registerContent(SiteImage, addSiteImage, SiteImageType)
    return
