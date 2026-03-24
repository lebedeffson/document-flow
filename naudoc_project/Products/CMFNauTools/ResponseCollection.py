"""Task responses collection class.

$Editor: ikuleshov $
$Id: ResponseCollection.py,v 1.7 2005/12/13 09:48:47 ikuleshov Exp $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

from types import IntType

from AccessControl import ClassSecurityInfo, Permissions
from Acquisition import Implicit
from BTrees.IIBTree import IISet, IITreeSet, intersection, union
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from DateTime import DateTime

from Products.CMFCore import CMFCorePermissions

from SimpleObjects import Persistent
from Utils import InitializeClass, isSequence

class ResponseCollection( Persistent, Implicit ):
    """
        Lightweight user responses storage. It is not aware of the
        task type brains and treats responses as a dict data.
    """
    _class_version = 1.02

    security = ClassSecurityInfo()
    idx_names = ('status', 'member', 'layer', 'isclosed')

    def __init__( self ):
        Persistent.__init__( self )
        self.collection = IOBTree()
        self._next_id = 1

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not Persistent._initstate( self, mode ):
            return 0

        if not getattr(self, 'indexes', None):
            self.indexes = OOBTree()

        for idx_name in self.idx_names:
            if not self.indexes.has_key(idx_name):
                self.indexes[idx_name] = OOBTree()

        if self.indexes['status'].has_key('fast_commit'):
            del self.indexes['status']['fast_commit']

        if hasattr(self, 'collection'):
            for id, response in self.collection.items():
                reindex = False
                if not response.has_key('response_id'):
                    reindex = True
                    response['response_id'] = id
                    
                if response.has_key('attachment') and response['attachment']:
                    response['attachments'] = ( response['attachment'], )
                    del response['attachment']
                    reindex = True
                else:
                    response['attachments'] = ()

                if response['status'] == 'fast_commit':
                    response['status'] = 'commit'
                    response['layer'] = 'involved_users'
                    reindex = True

                if reindex:
                    self.unindexResponse( id )
                    self.indexResponse( id, response )

    def addResponse( self, **kwargs ):
        """
            Adds a new user response

            Append a new user response in case there is no response
            with the given member, layer, status already stored in the
            collection or replace it otherwise.

            Arguments:

                'layer' -- Layer id string. There can be only *one* response on
                           each layer per user.

                'status' -- Response status id string.

                'text' -- User report text.

                'member' -- User id string.

                'isclosed' -- Boolean. Indicates whether the response can be
                              changed later or not.

                'attachments' -- list of ids of the file attachment associated
                                 with the response.

        """
        # Check for mandatory arguments
        assert ( not [ name for name in [ 'layer', 'status', 'member' ]
                      if not kwargs.has_key(name) ] 
               )

        id = self._next_id
        self._next_id += 1

        kwargs['response_id'] = id
        kwargs.setdefault( 'date', DateTime() )
        kwargs.setdefault( 'attachments', () )
        kwargs.setdefault( 'isclosed', 0 )
        kwargs.setdefault( 'text', '' )

        response = kwargs

        self.indexResponse(id, response)
        self.collection[id] = response
        return id

    security.declareProtected( CMFCorePermissions.View, 'getIndexKeys' )
    def getIndexKeys( self, idx):
        """
            Returns the keys of a given index.

            Arguments:

                'idx' -- Index id string.

            For example getIndexKeys('member') will return a list of
            responded users ids.
        """
        return list(self.indexes[idx].keys())

    security.declareProtected( CMFCorePermissions.View, 'searchResponses' )
    def searchResponses( self, **kw):
        """
            Returns a set of responses according to the search query.

            Arguments:

                '**kw' -- Search query. Each argument defines the value of the
                          particular index.

            Example:

                The following query will return the list of user responses with
                the given status and layer within the current task.

                >>> searchResponses(layer='involved_users', status='commit')

        """
        ids = self._searchResponsesIds( **kw )
        responses = [self.collection[id] for id in ids]

        return responses

    def _searchResponsesIds( self, **kw):
        """
            Returns a set of responses ids according to the search query.
        """
        # filter out parameters with no index
        valid_keys = list( self.indexes.keys() ) + ['response_id']
        items = [ (key, value) for (key, value) in kw.items() if key in valid_keys]
        if not items:
            # return all
            return self.collection.keys()

        results = None # provide intersection with valid args
        for key, value in items:
            if not isSequence(value):
                value = [ value ]

            if key == 'response_id':
                ids = IISet(value)
            else:
                idx = self.indexes[key]
                ids = None
                for item in value:
                    ids = union( ids, idx.get(item) )

            # if find nothing return empty result
            if not ids:
                return IISet()

            results = intersection(results, ids)

        if results is None:
            results = IISet()

        return results

    security.declarePrivate( 'indexResponse' )
    def indexResponse( self, id, response ):
        """
            Indexes the user response in the catalog.

            Arguments:

                'id' -- Index record id string. This is the object's name in
                        the catalog.

                'response' -- Dictionary containing the user response.
        """
        #
        # Sequentially update every index
        #
        for key, idx in self.indexes.items():
            value = response[key]
            # create inverted index
            idx.insert( value, IITreeSet() )

            # add reference to the current response
            idx[value].insert(id)

    security.declarePrivate( 'unindexResponse' )
    def unindexResponse( self, id ):
        """
            Removes response record from the catalog.

            Arguments:

                'id' -- Index record id string.
        """
        #
        # Remove reference to the given response id from every index
        #
        for idx_name, idx in self.indexes.items():
            for ids in idx.values():
                try:
                    ids.remove(id)
                except KeyError:
                    pass
                else: # only one id in one idx
                    break

    security.declarePrivate( CMFCorePermissions.View , 'getNextId' )
    def getNextId(self):
        """
            Returns id of new response.
        """
        return self._next_id

InitializeClass( ResponseCollection )

