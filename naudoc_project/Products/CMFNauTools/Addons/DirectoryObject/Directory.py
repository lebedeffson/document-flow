# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DirectoryObject/Directory.py
# Compiled at: 2006-08-15 12:33:57
"""
Directory implementation.

$Editor: vpastukhov $
$Id: Directory.py,v 1.46 2006/08/15 08:33:57 oevsegneev Exp $
"""
__version__ = '$Revision: 1.46 $'[11:-2]
import re
from sys import exc_info
from time import time
from types import StringType
from marshal import loads, dumps
from urllib import quote, unquote
from zlib import compress, decompress
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from Acquisition import Explicit, aq_base, aq_parent, aq_inner
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from ExtensionClass import Base
from Persistence import PersistentMapping
from zLOG import LOG, ERROR
from Products.PageTemplates.Expressions import getEngine
from Products.PluginIndexes.common.PluggableIndex import PluggableIndexInterface
from Products.ZCatalog.Catalog import Catalog
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import Features, Config
from Products.CMFNauTools.interfaces import IDirectory
from Products.CMFNauTools.interfaces.IDirectory import DirectoryColumnScopes as Scopes
from Products.CMFNauTools.RegistrationBook import TotalSequence
from Products.CMFNauTools.Monikers import Moniker
from Products.CMFNauTools.SimpleObjects import ContentBase, ContainerBase, InstanceBase, ItemBase, SimpleRecord
from Products.CMFNauTools.Utils import InitializeClass, readLink, updateLink, cookId, getLanguageInfo, _getViewFor
from Products.CMFNauTools.ValueTypes import getValueHandler
from Products.CMFNauTools.PatternProcessor import PatternProcessor
from Products.CMFNauTools.ResourceUid import ResourceUid
from DirectoryBase import DirectoryDerivedColumns, DirectoryIteratorBase, DirectoryTree
from DirectoryError import DirectoryError
DirectoryType = {'id': 'Directory', 'meta_type': 'Directory', 'title': 'Directory', 'description': 'Directory', 'icon': 'directory_object.gif', 'product': 'CMFNauTools', 'factory': 'addDirectory', 'permissions': (CMFCorePermissions.ManagePortal,), 'actions': ({'id': 'view', 'name': 'View', 'action': 'directory_view', 'permissions': (CMFCorePermissions.View,)}, {'id': 'metadata', 'name': 'Metadata', 'action': 'metadata_edit_form', 'permissions': (ZopePermissions.change_configuration,)}, {'id': 'settings', 'name': 'Change settings', 'action': 'directory_settings_form', 'permissions': (ZopePermissions.change_configuration,)}, {'id': 'columns', 'name': 'Configure attributes', 'action': 'directory_columns_form', 'permissions': (ZopePermissions.change_configuration,)})}

class DirectoryColumn(InstanceBase):
    """
        Directory column descriptor.
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Directory Column'
    __implements__ = (
     IDirectory.IDirectoryColumn, InstanceBase.__implements__)
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)
    _entries = True
    _branches = True
    _reserved = False
    _constant = False
    _readonly = False
    _scope = Scopes.SCOPE_NONE

    def __init__(self, name, type):
        InstanceBase.__init__(self, name)
        assert not getValueHandler(type).isDerived()
        self._name = name
        self._type = type
        self.setTitle(name)
        return

    def name(self):
        return self._name
        return

    def title(self):
        return self._title
        return

    def type(self):
        return self._type
        return

    def isEntryColumn(self):
        return self._entries
        return

    def isBranchColumn(self):
        return self._branches
        return

    def isConstant(self):
        return self._constant
        return

    def isUnique(self, scope=Missing):
        if scope is Missing:
            return self._scope
        if isinstance(scope, Base):
            if not scope.implements('IDirectoryNode'):
                raise TypeError, scope
            if scope.implements('IDirectoryRoot'):
                scope = Scopes.SCOPE_DIRECTORY
            else:
                scope = Scopes.SCOPE_PARENT
            return self._scope > scope
        return self._scope == scope
        return

    def isLoose(self):
        return False
        return

    def allowsInput(self):
        return not self._readonly
        return

    def isReserved(self):
        return self._reserved
        return

    def isImmutable(self):
        return False
        return

    def setTitle(self, title):
        self._title = str(title)
        return

    def setUsage(self, entries=False, branches=False):
        entries = not not entries
        branches = not not branches
        if entries == self._entries and branches == self._branches:
            return
        if self._reserved:
            raise TypeError
        if not (entries or branches):
            raise ValueError
        self._entries = entries
        self._branches = branches
        return

    def setConstant(self, value):
        value = not not value
        if value == self._constant:
            return
        self._constant = value
        self._readonly = value
        return

    def setUnique(self, scope):
        if scope == self._scope:
            return
        self._scope = scope
        return

    def disableInput(self, value):
        value = not not value
        if value == self._readonly:
            return
        if not value and self._constant:
            raise ValueError, value
        self._readonly = value
        return

    def _setReserved(self):
        self._reserved = True
        return

    def _getDirectory(self):
        return self.parent().parent()
        return

    def _checkValue(self, value, entry=Missing, parent=Missing, raise_exc=True):
        if entry is not Missing:
            if entry.isBranch():
                check = self._branches
            else:
                check = self._entries
            if not check:
                if raise_exc:
                    raise KeyError, self.name()
                return False
        if self._constant:
            if raise_exc:
                raise TypeError, self.name()
            return False
        if self._scope and value is not None and self._type != 'link':
            root = self._getDirectory()
            if not root._catalogCheckUnique(self, value, entry=entry, parent=parent):
                if raise_exc:
                    raise DirectoryError('column_value_exists', column=self, value=value)
                return False
        return True
        return

    def _instance_onCreate(self):
        self._getDirectory()._catalogAddIndex(self.name(), 'FieldIndex')
        return

    def _instance_onDestroy(self):
        self._getDirectory()._catalogDeleteIndex(self.name())
        return

    def _propertyMap(self):
        return InstanceBase._propertyMap(self) + getValueHandler(self._type)._propertyMap()
        return

    icon = 'directory_object.gif'
    Title = title
    security.declareProtected(ZopePermissions.change_configuration, 'setProperties')
    security.declareProtected(CMFCorePermissions.View, 'getFieldDescriptor')

    def getFieldDescriptor(self, view=True, modify=True, edit=False, **kwargs):
        """
            Returns UI field descriptor corresponding to this column,
            for use in 'entry_field' templates.

            Result:

                Mapping object.
        """
        modify = modify and (self.allowsInput() or edit)
        desc = {'id': (self.name()), 'name': (self.name()), 'type': (self.type()), 'multiple': False, 'mandatory': False, 'options': (self.getProperty('options', [])), 'properties': (self.getProperties(uids=True)), 'field_title': (self.title()), 'message': '', 'comment': '', 'view': view, 'modify': (view and modify)}
        desc.update(kwargs)
        return desc
        return


InitializeClass(DirectoryColumn)

class DirectoryNode(Base):
    __module__ = __name__
    __implements__ = IDirectory.IDirectoryNode
    security = ClassSecurityInfo()
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'addEntry')

    def addEntry(self, code=None):
        return self.getDirectory()._createEntry(self, False, code)
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'addBranch')

    def addBranch(self, code=None):
        return self.getDirectory()._createEntry(self, True, code)
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'deleteEntries')

    def deleteEntries(self, *entries):
        root = self.getDirectory()
        if self.implements('IDirectoryBranch'):
            pid = self.id()
            subids = root._catalogSearch(path__={'query': pid, 'level': (-1)})
            for id in entries:
                if id == pid or id not in subids:
                    raise ValueError, id

        root._deleteEntries(entries)
        return

    security.declareProtected(CMFCorePermissions.View, 'getEntryByCode')

    def getEntryByCode(self, code, default=Missing):
        column = self.getDirectory().getCodeColumn()
        if not column.isUnique(self):
            raise ValueError, code
        raise NotImplementedError
        return

    security.declareProtected(CMFCorePermissions.View, 'getEntryByAttribute')

    def getEntryByAttribute(self, name, value, default=Missing):
        column = self.getDirectory().getColumn(name)
        if not column.isUnique(self):
            raise ValueError, value
        raise NotImplementedError
        return

    security.declareProtected(CMFCorePermissions.View, 'listEntries')

    def listEntries(self, date=None, include_entries=True, include_branches=True, include_nested=True, **kw):
        if self.implements('IDirectoryBranch'):
            pid = self.id()
        else:
            pid = None
        root = self.getDirectory()
        query = {}
        iter_names = root._iterator_factory_args
        for (k, i) in kw.items():
            if k not in iter_names:
                query[k] = i
                del kw[k]

        if include_nested:
            if self.implements('IDirectoryBranch'):
                parts = [_[1] for x in self.listParentNodes()]
                parts.append(pid)
                parts.insert(0, '')
                query['id__'] = {'query': pid, 'operator': 'not'}
            else:
                parts = []
            query['path__'] = ('/').join(parts)
        else:
            query['parent__'] = pid
        if not (include_entries and include_branches):
            query['branch__'] = include_branches
        ids = root._catalogSearch(**query)
        items = [_[1] for id in ids]
        return root._iterator_factory(self, items, **kw)
        return

    security.declareProtected(CMFCorePermissions.View, 'listEntriesByAttribute')

    def listEntriesByAttribute(self, name, value, **kw):
        results = []
        iter = self.listEntries(**kw)
        for entry in self.listEntries(**kw):
            try:
                if entry.getEntryAttribute(name) == value:
                    results.append(entry)
            except KeyError:
                pass

        return results
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'cutObjects')

    def cutObjects(self, ids=None, REQUEST=None):
        """
            Put a reference to the objects named in ids in the clip board
        """
        if ids is None:
            return (
             ValueError, 'No items specified')
        if type(ids) is type(''):
            ids = [
             ids]
        cp = (
         1, ids)
        cp = _cb_encode(cp)
        if REQUEST is not None:
            REQUEST['RESPONSE'].setCookie('__cp', cp, path='%s' % cookie_path(REQUEST))
            REQUEST['__cp'] = cp
        return cp
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'pasteObjects')

    def pasteObjects(self, REQUEST=None):
        """
            Paste previously copied objects into the directory.
        """
        root = self.getDirectory()
        cp = None
        if REQUEST and REQUEST.has_key('__cp'):
            cp = REQUEST['__cp']
        if cp is None:
            raise CopyError, 'No Data'
        cp = _cb_decode(cp)
        op = cp[0]
        ids = cp[1]
        if op == 1:
            parent = self
            for id in ids:
                entry = root._getEntry(id)
                entry = entry.__of__(root)
                if entry.getParent() is parent:
                    break
                if parent is root:
                    parent = None
                root._setParent(entry, parent)

            if REQUEST is not None:
                REQUEST['RESPONSE'].setCookie('__cp', 'deleted', path='%s' % cookie_path(REQUEST), expires='Wed, 31-Dec-97 23:59:59 GMT')
                REQUEST['__cp'] = None
        return ids
        return

    security.declareProtected(CMFCorePermissions.View, 'cb_dataValid')

    def cb_dataValid(self):
        try:
            cp = _cb_decode(self.REQUEST['__cp'])
        except:
            return 0

        return 1
        return


InitializeClass(DirectoryNode)
_entry_titles_cache = {}
ENTRY_TITLES_CACHE_TIMEOUT = 30

class DirectoryEntry(ItemBase):
    """
        Directory entry.

        Uses external persistent data container.
        Wholly relies on the hierarchy support implementation
        in the directory root object.
    """
    __module__ = __name__
    meta_type = 'Directory Entry'
    __resource_type__ = 'directory'
    __implements__ = (
     IDirectory.IDirectoryEntry, ItemBase.__implements__)
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)

    def __init__(self, id, data):
        self._id = id
        self._data = data
        return

    security.declareProtected(CMFCorePermissions.View, 'id')

    def id(self):
        return self._id
        return

    def code(self):
        return self._data.get('code__', '')
        return

    def title(self):
        node_type = self.isBranch()
        pattern = self.getTitlePattern(node_type=node_type)
        if pattern is None:
            return self._data.get('title__', '')
        (result, expires) = _entry_titles_cache.get(self.physical_path(), (None, 0))
        if result is not None and expires > time():
            return result
        context = {}
        for column in self.listColumns():
            column_id = column.getId()
            value = self.getEntryAttribute(column_id)
            if hasattr(value, 'Title'):
                value = value.Title()
            if not value:
                value = ''
            context[column_id] = str(value)

        try:
            result = pattern(getEngine().getContext(context))
            _entry_titles_cache[self.physical_path()] = (result, time() + ENTRY_TITLES_CACHE_TIMEOUT)
        except:
            result = '?'
            LOG('DirectoryObject', ERROR, 'Error while evaluating entry title', error=exc_info())

        return result
        return

    def level(self):
        return self.getDirectory()._getLevel(self._id)
        return

    def getParent(self):
        return self.getDirectory()._getParent(self._id)
        return

    def getDirectory(self):
        return aq_parent(aq_inner(self))
        return

    def listParentNodes(self):
        nodes = []
        branch = self.getParent()
        while branch is not None:
            nodes.insert(0, branch)
            branch = branch.getParent()

        return nodes
        return

    def getOwner(self):
        return None
        return

    def setCode(self, code):
        root = self.getDirectory()
        root.getCodeColumn()._checkValue(code, entry=self)
        self._data['code__'] = code
        root._catalogIndexEntry(self, idxs=['code__', 'searchabletext__'])
        return

    def setTitle(self, title):
        root = self.getDirectory()
        root.getTitleColumn()._checkValue(title, entry=self)
        self._data['title__'] = title
        root._catalogIndexEntry(self, idxs=['title__', 'searchabletext__'])
        return

    def setParent(self, branch):
        root = self.getDirectory()
        if branch is not None:
            if not branch.implements('IDirectoryBranch'):
                raise ValueError, branch
            if branch.getDirectory() != root:
                raise ValueError, branch
        if self.getParent() == branch:
            return
        root._setParent(self, branch)
        return

    security.declareProtected(CMFCorePermissions.View, 'getEntryAttribute')

    def getEntryAttribute(self, name, default=Missing, moniker=False, uid=False):
        column = self.getDirectory().getColumn(name)
        check = self.isBranch() and column.isBranchColumn or column.isEntryColumn
        if not check():
            if default is not Missing:
                return default
            raise KeyError, name
        value = self._data.get(name, None)
        if column.type() == 'link' and value is not None:
            value = readLink(self, 'field', name, value, moniker=moniker, uid=uid)
        return value
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setEntryAttribute')

    def setEntryAttribute(self, name, value):
        root = self.getDirectory()
        column = root.getColumn(name)
        column._checkValue(value, entry=self)
        if column.type() == 'link':
            value = updateLink(self, 'field', name, value)
        if value is not None:
            self._data[name] = value
        elif self._data.has_key(name):
            del self._data[name]
        _entry_titles_cache[self.physical_path()] = (None, 0)
        root._catalogIndexEntry(self, idxs=[name, 'searchabletext__'])
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setEntryAttributes')

    def setEntryAttributes(self, **kwargs):
        for (name, value) in kwargs.items():
            self.setEntryAttribute(name, value)

        return

    def setType(self, name, type, length=None, precision=None):
        raise NotImplementedError
        return

    def isBranch(self):
        return False
        return

    def belongsToBranch(self, branch):
        if not branch.implements('IDirectoryBranch'):
            return False
        id = branch.id()
        for parent in self.listParentNodes():
            if parent.id() == id:
                return True
        else:
            return False

        return

    def listColumns(self):
        return [_[1] for c in self.getDirectory().listColumns() if c.isEntryColumn()]
        return

    def deleteEntry(self):
        self.getDirectory()._deleteEntries([self.id])
        return

    def __eq__(self, other):
        if not isinstance(other, DirectoryEntry):
            return False
        return self._id == other.id()
        return

    def _unsetAttributes(self):
        attrs = {}
        for column in self.listColumns():
            attrs[column.name()] = None

        self.setEntryAttributes(**attrs)
        return

    icon = 'directory_entry.gif'
    Title = title

    def this(self):
        return self
        return

    def getId(self):
        return self._id
        return

    security.declarePublic('getIcon')

    def getIcon(self):
        return self.icon
        return

    def __call__(self, REQUEST=None):
        view = _getViewFor(self.getDirectory(), 'entry')
        if getattr(aq_base(view), 'isDocTemp', None):
            return view(self, REQUEST or self.REQUEST)
        raise 'Not Found'
        return

    def searchableText(self):
        """
        """
        res = []
        res.append(self.getId())
        res.append(self.code())
        res.append(self.title())
        for col in self.listColumns():
            res.append(str(self.getEntryAttribute(col.getId(), uid=True)))

        return (' ').join(res)
        return


InitializeClass(DirectoryEntry)

class DirectoryBranch(DirectoryEntry, DirectoryNode):
    __module__ = __name__
    meta_type = 'Directory Branch'
    __implements__ = (
     IDirectory.IDirectoryBranch, DirectoryEntry.__implements__, DirectoryNode.__implements__)
    security = ClassSecurityInfo()

    def isBranch(self):
        return True
        return

    def listColumns(self):
        return [_[1] for c in self.getDirectory().listColumns() if c.isBranchColumn()]
        return

    icon = 'directory_branch.gif'
    icon_open = 'directory_branch_open.gif'

    def tpId(self):
        return self.id()
        return

    security.declarePublic('getIcon')

    def getIcon(self, open=False):
        return open and self.icon_open or self.icon
        return

    def tpURL(self):
        return self.id()
        return

    def tpValues(self):
        return self.listEntries(include_entries=False, include_nested=False).listItems()
        return


InitializeClass(DirectoryBranch)

class DirectoryIterator(DirectoryIteratorBase):
    __module__ = __name__

    def _sortEntries(self):
        return


class Directory(ContainerBase, ContentBase, DirectoryNode, ZCatalog):
    """
        Directory object with BTrees data container and simple
        ZCatalog-based indexing.

        Only root object is persistent, entries and branches are not.
    """
    __module__ = __name__
    _class_version = 1.2
    meta_type = 'Directory'
    portal_type = 'Directory'
    __resource_type__ = 'directory'
    __implements__ = (
     IDirectory.IDirectoryRoot, Features.isDirectory, Features.isPortalContent, Features.isItemsRealm, Features.isAttributesProvider, ContentBase.__implements__, ContainerBase.__implements__, DirectoryNode.__implements__)
    security = ClassSecurityInfo()
    security.setDefaultAccess(0)
    security.declareProtected(CMFCorePermissions.View, 'this', 'title_or_id', 'title_and_id')
    manage_options = ZCatalog.manage_options
    _entry_factory = DirectoryEntry
    _branch_factory = DirectoryBranch
    _column_factory = DirectoryColumn
    _iterator_factory = DirectoryIterator
    _iterator_factory_args = _iterator_factory.__init__.im_func.func_code.co_varnames[3:]
    _properties = ContentBase._properties + ({'id': 'sole_root', 'type': 'boolean', 'mode': 'w'}, {'id': 'max_level', 'type': 'int', 'mode': 'w'}, {'id': 'code_pattern', 'type': 'string', 'mode': 'nw'}, {'id': 'owner_object', 'type': 'link', 'mode': 'w'})
    sole_root = False
    max_level = 0
    code_pattern = '\\Seq'
    owner_object = None
    _v_cache = None
    icon = ContentBase.icon
    setTitle = ContentBase.setTitle
    _getCopy = ContentBase._getCopy

    def __init__(self, id=None, title=None, **kwargs):
        ContentBase.__init__(self, id, title, **kwargs)
        self._data = OOBTree()
        self._tree = OOBTree()
        return

    def _initstate(self, mode):
        """ Initialize attributes
        """
        if not ContentBase._initstate(self, mode):
            return False
        if getattr(self, 'branch_title_pattern', None) is None:
            self.branch_title_pattern = None
        if getattr(self, 'entry_title_pattern', None) is None:
            self.entry_title_pattern = None
        return

    def _instance_onCreate(self):
        self._catalog = DirectoryCatalog()
        self._catalogInit()
        seq_id = 'directory.entries.%s' % self.getUid()
        self.addObject(DirectorySequence('entries_seq', seq_id=seq_id))
        self.addObject(DirectoryColumnContainer())
        self._columnsInit()
        return

    security.declareProtected(CMFCorePermissions.View, 'getDirectory')

    def getDirectory(self):
        return self
        return

    security.declareProtected(CMFCorePermissions.View, 'getDirectoryTree')

    def getDirectoryTree(self, item):
        return DirectoryTree(item, self)
        return

    security.declareProtected(CMFCorePermissions.View, 'getEntry')

    def getEntry(self, id, default=Missing):
        try:
            return self._v_cache[id].__of__(self)
        except TypeError:
            self._v_cache = {}
        except KeyError:
            pass

        try:
            entry = self._getEntry(id)
        except KeyError:
            if default is not Missing:
                return default
            raise LookupError, id

        self._v_cache[id] = entry
        return entry.__of__(self)
        return

    security.declareProtected(CMFCorePermissions.View, 'isSoleRoot')

    def isSoleRoot(self):
        return self.sole_root
        return

    security.declareProtected(CMFCorePermissions.View, 'getMaxLevel')

    def getMaxLevel(self):
        return self.max_level
        return

    security.declareProtected(CMFCorePermissions.View, 'getCodePattern')

    def getCodePattern(self):
        return self.code_pattern
        return

    security.declareProtected(CMFCorePermissions.View, 'getTitlePattern')

    def getTitlePattern(self, text=False, node_type=1):
        if node_type:
            pattern = self.branch_title_pattern
        else:
            pattern = self.entry_title_pattern
        if text and pattern:
            return pattern.text
        return pattern
        return

    security.declareProtected(CMFCorePermissions.View, 'getOwnerObject')

    def getOwnerObject(self, moniker=False):
        return self.getProperty('owner_object', moniker=moniker)
        return

    security.declareProtected(ZopePermissions.change_configuration, 'setSoleRoot')

    def setSoleRoot(self, value):
        value = not not value
        if value == self.sole_root:
            return
        if value:
            ids = self._catalogSearch(level__=1)
            if len(ids) > 1:
                raise ValueError, len(ids)
        self.sole_root = value
        return

    security.declareProtected(ZopePermissions.change_configuration, 'setMaxLevel')

    def setMaxLevel(self, level):
        if level < 0:
            raise ValueError, level
        current = self.max_level
        if level == current:
            return
        if level and (not current or level < current):
            if self._catalogSearch(level__=level + 1):
                raise ValueError, level
        self.max_level = level
        return

    security.declareProtected(ZopePermissions.change_configuration, 'setCodePattern')

    def setCodePattern(self, pattern=None):
        if pattern is not None:
            if not pattern.strip():
                raise ValueError, pattern
            if len(_pattern_seq_re.findall(pattern)) > 1:
                raise ValueError, pattern
        self.code_pattern = pattern
        return

    security.declareProtected(ZopePermissions.change_configuration, 'setTitlePattern')

    def setTitlePattern(self, pattern=None, node_type=1):
        if not pattern:
            pattern = None
        elif isinstance(pattern, StringType):
            if not pattern.startswith('python:'):
                pattern = 'python:' + pattern
            pattern = Expression(pattern)
        elif not isinstance(pattern, StringType):
            raise ValueError, pattern
        if node_type:
            self.branch_title_pattern = pattern
        else:
            self.entry_title_pattern = pattern
        return

    security.declareProtected(ZopePermissions.change_configuration, 'setOwnerObject')

    def setOwnerObject(self, owner):
        self._updateProperty('owner_object', owner)
        return

    _reserved_columns = [
     (
      'code__', 'string', 'Code', Scopes.SCOPE_NONE), ('title__', 'string', 'Title', Scopes.SCOPE_NONE)]
    security.declareProtected(CMFCorePermissions.View, 'getCodeColumn')

    def getCodeColumn(self):
        return self.columns['code__']
        return

    security.declareProtected(CMFCorePermissions.View, 'getTitleColumn')

    def getTitleColumn(self):
        return self.columns['title__']
        return

    security.declareProtected(CMFCorePermissions.View, 'getColumn')

    def getColumn(self, name):
        return self.columns[name]
        return

    security.declareProtected(CMFCorePermissions.View, 'listColumns')

    def listColumns(self, entries=False, branches=False, builtins=False):
        columns = self.columns.objectValues()
        if not builtins:
            columns = [_[1] for c in columns if not c.name().endswith('__')]
        if entries:
            columns = [_[1] for c in columns if c.isEntryColumn()]
        if branches:
            columns = [_[1] for c in columns if c.isBranchColumn()]
        return columns
        return

    security.declareProtected(ZopePermissions.change_configuration, 'addColumn')

    def addColumn(self, name, type):
        if not name.strip() or name.startswith('_') or name.endswith('__'):
            raise ValueError, name
        if self.columns.hasObject(name):
            raise KeyError, name
        return self._createColumn(name, type)
        return

    security.declareProtected(ZopePermissions.change_configuration, 'deleteColumn')

    def deleteColumn(self, name):
        column = self.columns[name]
        if column.isReserved() or column.isImmutable():
            raise TypeError, name
        column.setConstant(False)
        column.setUnique(Scopes.SCOPE_NONE)
        clear_map = [
         column.isEntryColumn(), column.isBranchColumn()]
        for (id, item) in self._tree.items():
            if clear_map[item[1] and 1 or 0]:
                entry = self._getEntry(id).__of__(self)
                entry.setEntryAttribute(name, None)

        column.deleteObject()
        return

    security.declareProtected(CMFCorePermissions.View, 'allowedContentTypes')

    def allowedContentTypes(self, **kwargs):
        return []
        return

    security.declareProtected(ZopePermissions.change_configuration, 'hasMoreThanOneNode')

    def hasMoreThanOneNode(self):
        return len(self.getDirectory().listEntries()) > 1
        return

    security.declarePrivate('listAttributeDefinitions')

    def listAttributeDefinitions(self, id=None, types=None, categories=None):
        attrs = []
        uid = self.getResourceUid()
        for column in self.listColumns(builtins=True):
            item = {'uid': (uid.copy()), 'type': (column.type()), 'title': (column.title())}
            item['uid'].column = column.name()
            attrs.append(item)

        for column in DirectoryDerivedColumns:
            item = column.copy()
            item['uid'] = uid.copy()
            item['uid'].column = column['column']
            attrs.append(item)

        return attrs
        return

    security.declarePrivate('getAttributeValueFor')

    def getAttributeValueFor(self, object, uid, default=Missing, moniker=False):
        assert object.implements('IDirectoryEntry')
        column = uid.get('column')
        if column is None:
            raise KeyError, str(uid)
        if column == 'parent__':
            value = object.getParent()
            if value is None:
                if default is not Missing:
                    value = default
            elif moniker:
                value = Moniker(value)
            return value
        elif column == 'fullcode__':
            return (' / ').join([_[1] for e in object.listParentNodes() + [object]])
        elif column == 'fulltitle__':
            return (' / ').join([_[1] for e in object.listParentNodes() + [object]])
        return object.getEntryAttribute(column, default, moniker=moniker)
        return

    def _getEntry(self, id, data=None, is_branch=None):
        if data is None:
            data = self._data[id]
        if is_branch is None:
            is_branch = self._tree[id][1]
        if is_branch:
            entry = self._branch_factory(id, data)
        else:
            entry = self._entry_factory(id, data)
        return entry
        return

    def _getLevel(self, id):
        return self._catalogGetIndexData('path__', id).count('/')
        return

    def _getParent(self, id):
        pid = self._tree[id][0]
        if pid is None:
            return None
        return self.getEntry(pid)
        return

    def _setParent(self, entry, parent):
        id = entry.id()
        self._updateTree(entry, parent)
        self._catalogIndexEntry(entry, idxs=['parent__', 'path__', 'level__'])
        if entry.isBranch():
            for cid in self._catalogSearch(path__={'query': id, 'level': (-1)}):
                if cid == id:
                    continue
                child = self.getEntry(cid)
                self._catalogIndexEntry(child, idxs=['path__', 'level__'])

        return

    def _createEntry(self, parent, is_branch, code):
        if not parent.implements('IDirectoryBranch'):
            parent = None
        if parent is None and self.sole_root:
            ids = self._catalogSearch(level__=1)
            if ids:
                raise IndexError, len(ids)
        if parent is not None and self.max_level:
            level = self._getLevel(parent.id()) + 1
            if level > self.max_level:
                raise IndexError, level
        (id, code) = PatternProcessor.processString(code, fmt='code', obj=self, parent=parent)
        data = PersistentMapping()
        entry = self._getEntry(id, data, is_branch)
        if self._v_cache is None:
            self._v_cache = {}
        self._v_cache[id] = entry
        entry = entry.__of__(self)
        self._updateTree(entry, parent)
        self._data[id] = data
        self._catalogIndexEntry(entry)
        entry.setCode(code)
        entry.setTitle('')
        return entry
        return

    def _deleteEntries(self, ids):
        data = self._data
        tree = self._tree
        cache = self._v_cache
        for id in self._catalogSearch(path__={'query': ids, 'level': (-1)}):
            entry = self._getEntry(id).__of__(self)
            entry._unsetAttributes()
            self._catalogUnindexEntry(entry)
            entry = None
            if cache and cache.has_key(id):
                del cache[id]
            del data[id]
            del tree[id]

        return

    def _updateTree(self, entry, parent):
        pid = parent is not None and parent.id() or None
        self._tree[entry.id()] = (pid, entry.isBranch())
        return

    def _createColumn(self, name, type):
        column = self._column_factory(name, type)
        return self.columns.addObject(column)
        return

    def _columnsInit(self):
        msg = getToolByName(self, 'msg')
        for (name, type, title, scope) in self._reserved_columns:
            column = self._createColumn(name, type)
            column.setTitle(msg.gettext(title, add=False))
            column.setUnique(scope)
            column._setReserved()

        return

    def __getitem__(self, name):
        try:
            return self.getEntry(name)
        except LookupError:
            raise KeyError, name

        return

    security.declareProtected(CMFCorePermissions.View, 'tpId')

    def tpId(self):
        return ''
        return

    security.declareProtected(CMFCorePermissions.View, 'tpURL')

    def tpURL(self):
        return self.getId()
        return

    security.declareProtected(CMFCorePermissions.View, 'tpValues')

    def tpValues(self):
        return self.listEntries(include_entries=False, include_nested=False).listItems()
        return

    _catalog_indexes = [
     (
      'id__', 'FieldIndex'), ('parent__', 'FieldIndex'), ('branch__', 'FieldIndex'), ('level__', 'FieldIndex'), ('path__', 'PathIndex'), ('searchabletext__', 'TextIndexNG2')]
    _catalogAddIndex = ZCatalog.addIndex
    _catalogDeleteIndex = ZCatalog.delIndex

    def _catalogInit(self, check=False):
        count = 0
        indexes = self._catalog.indexes.keys()
        for (iname, itype) in self._catalog_indexes:
            if iname in indexes:
                continue
            count += 1
            if check:
                continue
            options = None
            if itype == 'TextIndexNG2':
                if Config.UseTextIndexNG2:
                    properties = getToolByName(self, 'portal_properties')
                    options = SimpleRecord(Config.TextIndexNG2Options)
                    options.use_stemmer = properties.getProperty('stemmer')
                    options.default_encoding = getLanguageInfo(self)['python_charset']
                else:
                    itype = 'FieldIndex'
            self._catalogAddIndex(iname, itype, options)

        return count
        return

    def _catalogIndexEntry(self, entry, idxs=()):
        wrapper = DirectoryCatalogWrapper(entry)
        uid = entry.id()
        self._catalog.catalogObject(wrapper, uid, None, idxs or [])
        return

    def _catalogUnindexEntry(self, entry):
        uid = entry.id()
        self._catalog.uncatalogObject(uid)
        return

    def _catalogGetIndexData(self, name, id):
        catalog = self._catalog
        rid = catalog.uids[id]
        return catalog.getIndex(name).getEntryForObject(rid)
        return

    def _catalogSearch(self, **query):
        text = query.get('searchabletext__')
        if text:
            res = []
            for word in text.split():
                word = word.strip()
                if word != '*':
                    res.append(word)

            query['searchabletext__'] = (' ').join(res)
        catalog = self._catalog
        paths = catalog.paths
        results = catalog.searchResults(REQUEST={}, **query)
        ids = [_[1] for r in results]
        return ids
        return

    def _catalogCheckUnique(self, column, value, entry=Missing, parent=Missing):
        scope = column.isUnique()
        if not scope:
            return True
        id = entry is not Missing and entry.id() or None
        query = {(column.name()): value}
        if scope == Scopes.SCOPE_PARENT:
            if parent is not Missing:
                pid = parent is not None and parent.id() or None
            elif id:
                pid = self._tree[id][0]
            else:
                raise RuntimeError
            query['parent__'] = pid
        elif scope == Scopes.SCOPE_DIRECTORY:
            pass
        elif scope == Scopes.SCOPE_OWNER:
            raise NotImplementedError
        results = self._catalogSearch(**query)
        if len(results) == 1 and id:
            return results[0] == id
        return not results
        return

    def _getWrappedEntry(self, id):
        try:
            entry = self.getEntry(id)
        except LookupError:
            return

        return DirectoryCatalogWrapper(entry)
        return

    resolve_path = _getWrappedEntry


InitializeClass(Directory)

class DirectoryColumnContainer(ContainerBase):
    """
        Container for directory column descriptors.
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Directory Columns Container'
    id = 'columns'
    title = meta_type
    all_meta_types = ()
    _reserved_names = (
     'code__', 'title__')


InitializeClass(DirectoryColumnContainer)

class DirectorySequence(TotalSequence):
    """
        Sequence number generator for entry codes.
    """
    __module__ = __name__
    _class_version = 1.0
    meta_type = 'Directory Sequence'

    def __init__(self, id=None, title=None, seq_id=None):
        TotalSequence.__init__(self, seq_id)
        InstanceBase.__init__(self, id, title)
        return


InitializeClass(DirectorySequence)

class DirectoryCatalogBrains(Explicit):
    __module__ = __name__

    def __init__(self, data):
        return


class DirectoryCatalog(Catalog):
    __module__ = __name__
    _v_brains = DirectoryCatalogBrains


InitializeClass(DirectoryCatalog)

class DirectoryCatalogWrapper:
    __module__ = __name__
    meta_type = 'unspecified'

    def __init__(self, ob):
        self.__ob = ob
        return

    def id__(self):
        return self.__ob.id()
        return

    def code__(self):
        return self.__ob.code()
        return

    def title__(self):
        return self.__ob.title()
        return

    def branch__(self):
        return self.__ob.isBranch()
        return

    def parent__(self):
        parent = self.__ob.getParent()
        if parent is None:
            return None
        return parent.id()
        return

    def level__(self):
        return len(self.__ob.listParentNodes()) + 1
        return

    def path__(self):
        path = [_[1] for p in self.__ob.listParentNodes()]
        path.append(self.__ob.id())
        path.insert(0, '')
        return tuple(path)
        return

    def __getattr__(self, name):
        try:
            value = self.__ob.getEntryAttribute(name, uid=True)
        except KeyError:
            raise AttributeError, name

        if isinstance(value, ResourceUid):
            return str(value)
        return value
        return

    def searchabletext__(self):
        return self.__ob.searchableText()
        return


_pattern_seq_re = re.compile('\\\\Seq\\b(?::(\\d*)#|#?)', re.I)

def addDirectory(self, id, title='', REQUEST=None, **kwargs):
    """
        Add a Directory
    """
    self._setObject(id, Directory(id, title, **kwargs))
    if REQUEST is not None:
        return self[id].redirect(message='Directory added.', REQUEST=REQUEST)
    return


def _cb_encode(d):
    return quote(compress(dumps(d), 9))
    return


def _cb_decode(s):
    return loads(decompress(unquote(s)))
    return


def cookie_path(request):
    return request['BASEPATH1'] or '/'
    return


def initialize(context):
    context.registerContent(Directory, addDirectory, DirectoryType, activate=False)
    return
