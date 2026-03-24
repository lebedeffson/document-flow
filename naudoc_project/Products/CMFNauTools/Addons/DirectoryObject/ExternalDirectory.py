# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DirectoryObject/ExternalDirectory.py
# Compiled at: 2004-05-01 15:04:51
"""
Directory implementation.

$Editor: vpastukhov $
$Id: ExternalDirectory.py,v 1.13 2004/05/01 11:04:51 vpastukhov Exp $
"""
__version__ = '$Revision: 1.13 $'[11:-2]
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from Acquisition import aq_parent
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import Features
from Products.CMFNauTools.interfaces import IDirectory
from Products.CMFNauTools.ProxyObject import ProxyItemBase, ProxyMethod, initializeWrapperClass
from Products.CMFNauTools.SimpleObjects import ContentBase, ItemBase
from Products.CMFNauTools.Utils import InitializeClass
ExternalDirectoryType = {'id': 'External Directory', 'meta_type': 'External Directory', 'title': 'External Directory', 'description': 'External Directory', 'icon': 'directory_external.gif', 'product': 'CMFNauTools', 'factory': 'addExternalDirectory', 'permissions': (CMFCorePermissions.ManagePortal,), 'actions': ({'id': 'view', 'name': 'View', 'action': 'directory_view', 'permissions': (CMFCorePermissions.View,), 'condition': 'python: object.isActive()'}, {'id': 'metadata', 'name': 'Metadata', 'action': 'metadata_edit_form', 'permissions': (ZopePermissions.change_configuration,)})}

class ExternalDirectory(ContentBase, ProxyItemBase):
    """
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'External Directory'
    portal_type = 'External Directory'
    __implements__ = (
     IDirectory.IDirectoryRoot, IDirectory.IDirectoryNode, Features.isDirectory, Features.isPortalContent, ContentBase.__implements__, ProxyItemBase.__implements__)
    _properties = ContentBase._properties + ({'id': 'service_id', 'type': 'list', 'mode': 'w', 'title': 'External service', 'select_variable': 'listServices'},)
    _wrapper_methods = []
    __of__ = ProxyItemBase.__of__.im_func
    __getattr__ = ProxyItemBase.__getattr__.im_func

    def __init__(self, id, title, service_id='', **kw):
        ContentBase.__init__(self, id, title, **kw)
        self._setPropValue('service_id', service_id)
        return

    def __getitem__(self, name):
        try:
            return self.getEntry(name)
        except LookupError:
            raise KeyError, name

        return

    def listServices(self):
        connector = getToolByName(self, 'portal_connector')
        return [s[1] for s in connector.listServices('isDirectory')]
        return

    def isActive(self):
        connector = getToolByName(self, 'portal_connector')
        return connector.isServiceActive(self.service_id)
        return

    def openDirectory(self):
        if not self.service_id:
            return None
        if self._v_proxied_object is None:
            connector = getToolByName(self, 'portal_connector')
            self._v_proxied_object = connector.getService(self.service_id)
        return self._v_proxied_object
        return

    _proxy_connect = openDirectory

    def getDirectory(self):
        return self
        return

    def this(self):
        return self
        return

    def tpId(self):
        return ''
        return

    def tpURL(self):
        return self.getId()
        return

    def tpValues(self):
        return self.listEntries(include_entries=False, include_nested=False).listItems()
        return


initializeWrapperClass(ExternalDirectory)
InitializeClass(ExternalDirectory)

class ColumnWrapper(ProxyItemBase, ItemBase):
    __module__ = __name__
    __implements__ = (
     IDirectory.IDirectoryColumn, ProxyItemBase.__implements__, ItemBase.__implements__)
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)

    def __init__(self, *args):
        ProxyItemBase.__init__(self, *args)
        ItemBase.__init__(self)
        return

    def this(self):
        return self
        return


initializeWrapperClass(ColumnWrapper)
InitializeClass(ColumnWrapper)

class EntryWrapper(ProxyItemBase, ItemBase):
    __module__ = __name__
    __implements__ = (
     IDirectory.IDirectoryEntry, ProxyItemBase.__implements__, ItemBase.__implements__)
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)
    _wrapper_methods = []

    def __init__(self, *args):
        ProxyItemBase.__init__(self, *args)
        ItemBase.__init__(self)
        return

    def getDirectory(self):
        return self.parent()
        return

    def this(self):
        return self
        return


initializeWrapperClass(EntryWrapper)
InitializeClass(EntryWrapper)

class BranchWrapper(EntryWrapper):
    __module__ = __name__
    __implements__ = (
     IDirectory.IDirectoryBranch, IDirectory.IDirectoryNode, EntryWrapper.__implements__)
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)
    _wrapper_methods = ['getEntryByCode', 'getEntryByAttribute', 'listEntries', 'listEntriesByAttribute']

    def tpId(self):
        return self.id()
        return

    def tpURL(self):
        return self.id()
        return

    def tpValues(self):
        return self.listEntries(include_entries=False, include_nested=False).listItems()
        return


initializeWrapperClass(BranchWrapper)
InitializeClass(BranchWrapper)

class IteratorWrapper(ProxyItemBase):
    __module__ = __name__
    __implements__ = (
     IDirectory.IDirectoryIterator, ProxyItemBase.__implements__, ItemBase.__implements__)
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)
    _wrapper_methods = ['getNextItem', 'listItems', 'next']


initializeWrapperClass(IteratorWrapper)
InitializeClass(IteratorWrapper)
ExternalDirectory._wrapper_factories = [
 (
  IDirectory.IDirectoryRoot, NotImplementedError, 0), (IDirectory.IDirectoryBranch, BranchWrapper, 1), (IDirectory.IDirectoryEntry, EntryWrapper, 1), (IDirectory.IDirectoryIterator, IteratorWrapper, 1), (IDirectory.IDirectoryColumn, ColumnWrapper, 1)]

def addExternalDirectory(self, id, title='', REQUEST=None, **kwargs):
    """
        Adds an External Directory.
    """
    self._setObject(id, ExternalDirectory(id, title, **kwargs))
    if REQUEST is not None:
        return self[id].redirect(message='External directory added.', REQUEST=REQUEST)
    return


def initialize(context):
    context.registerContent(ExternalDirectory, addExternalDirectory, ExternalDirectoryType, activate=False)
    return
