###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Storage for wordIds/documentIds with forward and backup indexes 

$Id: StandardStorage.py,v 1.4 2006/04/05 13:23:30 ikuleshov Exp $
"""

from types import IntType

from Persistence import Persistent
from BTrees.IIBTree import IITreeSet, IISet, IIBTree, difference
from BTrees.IOBTree import IOBTree
import BTrees.Length

from Products.TextIndexNG2.interfaces.IStorage import StorageInterface
from Products.ZCTextIndex.WidCode import encode, decode

class Storage(Persistent):
    """ storage to keep the mapping wordId to sequence
        of document ids and vis-versa.
    """

    __implements__ = StorageInterface

    def __init__(self): 
        self.clear()

    def clear(self):
        self._forward_idx = IOBTree()
        self._reverse_idx = IOBTree()
        self._frequencies = IOBTree()
        self._length = BTrees.Length.Length()
    
    def __len__(self): return self._length()
    getNumDocuments = __len__
    
    def getDocIds(self): return self._reverse_idx.keys()

    def insert(self, wids, docid):
        """ insert entries: 
            wids is either an integer or a sequence of integers.
            docid is an integer.
        """

        if isinstance(wids, IntType): wids = [wids]
        idx = self._forward_idx

        # get rid of words removed by reindexing
        try:
            oldwids = decode(self._reverse_idx[docid])
        except KeyError:
            pass
        else:
            remwids = difference(IISet(oldwids), IISet(wids))
            for wid in remwids:
                try:
                    v = idx[wid]
                    if isinstance( v, IntType ):
                        idx[wid] = IITreeSet()
                        idx[wid].insert(v)
                    idx[wid].remove(docid)
                    if not len(idx[wid]):
                        del idx[wid]
                except KeyError:
                    pass

        # fill forward index
        for wid in wids:
            try:
                v = idx[wid]
                # Don't know the reason but it happens indeed
                if isinstance( v, IntType ):
                    idx[wid] = IITreeSet()
                    idx[wid].insert(v)
                idx[wid].insert(docid)
            except KeyError:
                idx[wid] = IITreeSet()
                idx[wid].insert(docid)

        if not self._reverse_idx.has_key(docid): self._length.change(1)
        self._reverse_idx[docid] = encode(wids)
        self._frequencies[docid] = self._get_frequencies(wids)

    def _get_frequencies(self, wids):
        """ determine the word frequencies for a sequence of wids.
            Return a mapping wid -> #occurences
        """

        f = IIBTree()
        fg = f.get
        for wid in wids:
            f[wid] = fg(wid, 0) + 1
        return f

    def getWordFrequency(self, docid, wid):
        if not self._forward_idx.has_key(wid): return 0
        try:
            return self._frequencies[docid].get(wid, 0)
        except KeyError:
            return 0

    def removeWordIdsForDocId(self, docid, wids):

        for wid in wids:
            try:
                self._forward_idx[wid].remove(docid)
                if len(self._forward_idx[wid])==0:
                    del self._forward_idx[wid]
            except KeyError: pass

        old_wids = decode(self._reverse_idx[docid])
        new_wids = [w for w in old_wids if w not in wids]
        self._reverse_idx[docid] = encode(new_wids)
        self._frequencies[docid] = self._get_frequencies(new_wids)
        

    def removeDocument(self, docid):
        """ remove a document and all its words from the storage """

        try:
            wids = decode(self._reverse_idx[docid])
        except KeyError: return

        del self._reverse_idx[docid]
        try:
            del self._frequencies[docid]
        except KeyError:
            pass

        for wid in wids:
            try:
                self._forward_idx[wid].remove(docid )
            except KeyError: pass
            
            try:
                if len(self._forward_idx[wid]) == 0:
                    del self._forward_idx[wid]
            except KeyError: pass

        self._length.change(-1)

    def getDocumentIdsForWordId(self, wid):
        """ return the sequence of document ids for a word id """

        if wid is None:
            return ()
        try:
            return self._forward_idx[wid].keys()
        except KeyError:
            return ()

    get = getDocumentIdsForWordId

    def getWordIdsForDocId(self, docid):
        """ return a sequence of words contained in the document with 
            ID 'docId'
        """
        return decode(self._reverse_idx[docid])

    def printStorage(self):
        for k,v in self._forward_idx.items():
            print k, list(v)

