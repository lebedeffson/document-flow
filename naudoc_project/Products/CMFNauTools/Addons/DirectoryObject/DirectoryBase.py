# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DirectoryObject/DirectoryBase.py
# Compiled at: 2008-03-26 18:00:53
"""
Directory implementation.

$Editor: vpastukhov $
$Id: DirectoryBase.py,v 1.23 2008/03/26 15:00:53 oevsegneev Exp $
"""
__version__ = '$Revision: 1.23 $'[11:-2]
import re
from types import IntType
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import Features, Exceptions
from Products.CMFNauTools.interfaces import IDirectory
from Products.CMFNauTools.interfaces.IJungleTree import IBasicTree
from Products.CMFNauTools.Explorer import ExplorerBase
from Products.CMFNauTools.PatternProcessor import Pattern
from Products.CMFNauTools.Utils import InitializeClass
DirectoryDerivedColumns = [{'column': 'fulltitle__', 'type': 'string', 'title': 'directories.full_title'}, {'column': 'fullcode__', 'type': 'string', 'title': 'directories.full_code'}, {'column': 'parent__', 'type': 'object', 'title': 'directories.parent_branch'}]

class DirectoryIteratorBase:
    __module__ = __name__
    __implements__ = IDirectory.IDirectoryIterator
    __allow_access_to_unprotected_subobjects__ = 1
    _last_idx = None
    _next_idx = None
    _limit = None

    def __init__(self, branch, items, include_branches=1, include_nested=1, order_by=None, reverse_order=0, hierarchy_order=0, start=None, size=None):
        self._branch = branch
        self._items = items
        self._include_branches = include_branches
        self._include_nested = include_nested
        self._order_by = order_by
        self._reverse_order = reverse_order
        self._hierarchy_order = hierarchy_order
        self._index = 0
        self._start = start or 0
        if size is not None:
            self._limit = self._start + size
        if order_by:
            if include_nested and not hierarchy_order:
                while 1:
                    try:
                        self.getNextItem()
                    except StopIteration:
                        break

            self._sortEntries()
        if start:
            self.skipItems(start)
        return

    def _sortEntries(self):
        return

    def __getitem__(self, index):
        assert index == self._index - self._start, 'Random access is not implemented'
        try:
            item = self.getNextItem()
        except StopIteration:
            raise IndexError(index)

        return item
        return

    def _getNextIndex(self):
        if self._next_idx is not None:
            return self._next_idx
        idx = last = self._last_idx
        items = self._items
        if last is None:
            idx = 0
        while idx < len(items):
            (id, subiter) = items[idx]
            if subiter is None:
                if idx != last:
                    break
            elif self._include_branches and idx != last:
                break
            elif self._include_nested:
                subiter = self._getSubIterator(idx)
                id = subiter.getNextId()
                if id is not None:
                    break
            idx += 1
        else:
            return None

        self._next_idx = idx
        return idx
        return

    def _getSubIterator(self, idx):
        (id, subiter) = self._items[idx]
        if subiter is None:
            return None
        if type(subiter) is IntType:
            entry = self._branch.getDirectory().getEntry(id)
            subiter = entry.listEntries(include_nested=1, include_branches=self._include_branches, order_by=self._order_by)
            self._items[idx] = (id, subiter)
        return subiter
        return

    def getNextItem(self, default=Missing):
        """
        """
        next = self._getNextIndex()
        if next is None or self._limit is not None and self._index == self._limit:
            if default is Missing:
                raise StopIteration
            return default
        (id, subiter) = self._items[next]
        last = self._last_idx
        if subiter is not None and (next == last or not self._include_branches):
            entry = subiter.getNextItem()
        else:
            entry = self._branch.getDirectory().getEntry(id)
        self._last_idx = next
        self._next_idx = None
        self._index += 1
        return entry
        return

    def skipItems(self, count=1):
        assert count > 0
        for idx in xrange(count):
            try:
                self.getNextItem()
            except StopIteration:
                return idx

        return count
        return

    def listItems(self):
        results = []
        while 1:
            try:
                results.append(self.getNextItem())
            except StopIteration:
                break

        return results
        return

    def listIds(self):
        return []
        return

    def getNextId(self):
        next = self._getNextIndex()
        if next is None:
            return None
        (id, subiter) = self._items[next]
        last = self._last_idx
        if subiter is not None and (next == last or not self._include_branches):
            id = subiter.getNextId()
        return id
        return

    def countItems(self):
        count = len(self._items)
        for idx in range(count):
            subiter = self._getSubIterator(idx)
            if subiter is not None:
                count += subiter.countItems()

        return count
        return

    def __len__(self):
        count = self.countItems()
        if self._start >= count:
            return 0
        if self._limit is not None and count > self._limit:
            count = self._limit
        return count - self._start
        return

    def __iter__(self):
        return self
        return

    next = getNextItem


InitializeClass(DirectoryIteratorBase)

class DirectoryResource:
    __module__ = __name__
    keys = [
     'entry']

    def identify(portal, object):
        if object.implements('IDirectoryRoot'):
            root = object
        elif object.implements('IDirectoryEntry'):
            root = object.getDirectory()
        elif object.implements('IDirectoryColumn'):
            root = object.parent().parent()
        else:
            raise TypeError, object
        if not root.implements('isPortalContent'):
            raise TypeError, root
        uid = {'uid': (root.getUid())}
        if object.implements('IDirectoryEntry'):
            uid['entry'] = object.id()
        elif object.implements('IDirectoryColumn'):
            uid['column'] = object.getId()
        return uid
        return

    def lookup(portal, uid=None, entry=None, column=None, **kwargs):
        catalog = getToolByName(portal, 'portal_catalog')
        results = catalog.unrestrictedSearch(nd_uid=str(uid))
        if len(results) == 1:
            path = results[0].getPath()
            object = portal.unrestrictedTraverse(path)
            if object is None:
                raise Exceptions.LocatorError('content', uid)
        else:
            raise Exceptions.LocatorError('content', uid)
        if entry:
            object = object.getEntry(entry)
        if column:
            in_derived_columns = filter((lambda x, column=column: x['column'] == column), DirectoryDerivedColumns)
            if in_derived_columns:
                return column
            object = object.getColumn(column)
        return object
        return


class GenerateCodePattern(Pattern):
    """
        Generates code of for a new Direcory entry.
    """
    __module__ = __name__
    id = 'code'
    _pattern = re.compile('\\\\Seq\\b(?::(\\d*)#|#?)', re.I)
    _explanation = {'\\y': 'Year without century as a decimal number', '\\Y': 'Year with century as a decimal number', '\\m': 'Month as a decimal number', '\\d': 'Day of the month as a decimal number', '\\H': 'Hour as a decimal number', '\\M': 'Minute as a decimal number', '\\Seq[:nn#]': 'Counter value, where nn - optional parameter, number of digits of the counter'}

    def process(self, string, **kw):
        column = kw['obj'].getCodeColumn()
        sequence = kw['obj'].entries_seq
        seqnum = sequence.getNextValue()
        if string is None:
            pattern = kw['obj'].code_pattern
            if pattern is None:
                raise ValueError, string
            now = DateTime()
            for c in 'YymdHM':
                pattern = pattern.replace('\\' + c, now.strftime('%' + c))

            if not self._pattern.search(pattern):
                string = pattern
        else:
            string = string.strip()
        if string is not None:
            if not kw['obj']._catalogCheckUnique(column, string, parent=kw['parent']):
                raise DirectoryError('column_value_exists', column=column, value=string)
            return (
             str(seqnum), string)
        while 1:
            repl = lambda m, n=seqnum: '%%.%sd' % (m.group(1) or '0') % n
            string = self._pattern.sub(repl, pattern)
            if kw['obj']._catalogCheckUnique(column, string, parent=kw['parent']):
                break
            seqnum = sequence.getNextValue()

        return (str(seqnum), string)
        return


class DirectoryTree:
    __module__ = __name__
    __implements__ = IBasicTree

    def __init__(self, item, context):
        self.need_cleanup = not item
        self.root_item = item
        self.root = context
        self.root_url = '/' + context.absolute_url(1)
        self.info_dict = {'': context}
        return

    def get_items(self, item):
        info_dict = self.info_dict
        if item:
            node = info_dict.get(item)
            if node is None:
                node = self.root.getEntry(item)
                info_dict[item] = node
        else:
            node = self.root
        for entry in node.listEntries(include_nested=0, include_entries=0):
            id = entry.id()
            info_dict[id] = entry
            yield id

        return


class DirectoryExplorer(ExplorerBase):
    """
    """
    __module__ = __name__
    mode = 'directory'
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess(1)

    def tree_index(self, item):
        """
        """
        context = self._v_object
        REQUEST = context.REQUEST
        explorer_id = self.id
        REQUEST.set('item', item)
        return DirectoryTree(item or '', context)
        return

    def content_index(self, item):
        """
        """
        context = self._v_object
        REQUEST = context.REQUEST
        session = REQUEST['SESSION']
        if item:
            node = context.getEntry(item)
        else:
            node = context
        is_search = REQUEST.get('search_enable', 0)
        batch_size = int(context.portal_membership.getInterfacePreferences('viewing_document_number'))
        qs_old = is_search and 1 or session.get('explorer_directory_%s_qs' % node.getId(), 1)
        qs_new = int(REQUEST.get('qs', qs_old))
        qs = qs_new / batch_size * batch_size + 1
        if (qs > 1 or qs == 1 and qs_old > 1) and not is_search:
            session['explorer_directory_%s_qs' % node.getId()] = qs
        extra = {}
        include_nested = 0
        if is_search:
            if REQUEST.has_key('text'):
                session['explorer_directory_search_text'] = REQUEST['text']
                extra['searchabletext__'] = REQUEST['text']
            else:
                extra['searchabletext__'] = session.get('explorer_directory_search_text', '')
            include_nested = 1
        extra['size'] = batch_size
        extra['start'] = qs - 1
        results = []
        entries = node.listEntries(include_nested=include_nested, **extra)
        for entry in entries:
            results.append(((entry.id(), entry.getResourceUid()), entry))

        return {'results': results, 'results_count': (entries.countItems()), 'batch_size': batch_size, 'qs': qs, 'node': node, 'item': item}
        return


InitializeClass(DirectoryExplorer)

def initialize(context):
    context.registerPattern(GenerateCodePattern)
    context.registerResource('directory', DirectoryResource, moniker='content', features=['IDirectoryRoot', 'IDirectoryEntry', 'IDirectoryColumn'])
    context.registerExplorer('isDirectory', DirectoryExplorer)
    return
