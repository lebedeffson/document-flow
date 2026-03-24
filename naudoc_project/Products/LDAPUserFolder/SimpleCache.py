#####################################################################
#
# SimpleCache     A simple non-persistent cache
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################

from copy import deepcopy
from time import time
from weakref import WeakValueDictionary

try:
    from thread import get_ident, allocate_lock
except ImportError:
    get_ident = lambda: 0
    allocate_lock = None


_caches = WeakValueDictionary()

def getSimpleCache( owner, name ):
    """ Returns specified cache for the owner """
    if getattr( owner, '_p_oid', '' ) is None:
        # got new persistent object -> assign _p_oid
        get_transaction().commit(1)

    oid = getattr( owner, '_p_oid', id(owner) )

    # NB __getitem__ is broken in python 2.1
    cache = _caches.get( (oid, name) )
    if cache is None:
        cache = _caches[ (oid, name) ] = SimpleCache()
    return cache

def deepCopyExtClass( self, memo ):
    """ Create a copy of extension class instance """
    if hasattr( self, '_p_oid' ):
        raise TypeError, "cannot copy persistent object"

    new = self.__class__.__basicnew__()
    new.__dict__.update( deepcopy( self.__dict__, memo ) )

    return new


class SimpleCache:
    """ A simple non-persistent thread-safe cache """

    def __init__( self ):
        """ Initialize a new instance """
        if allocate_lock:
            lock = allocate_lock()
            self.acquire = lock.acquire
            self.release = lock.release
        else:
            self.acquire = self.release = lambda: 0

        self.timeout = 600
        self.clear()

    def set( self, id, object ):
        """ Cache an object under the given id """
        id = str( id ).lower()

        self.acquire()
        try:

            self.cache[ id ] = object
            self.getLocalCache()[ id ] = object = deepcopy( object )
            return object

        finally:
            self.release()

    def get( self, id, password=None ):
        """ Retrieve a cached object if it is valid """
        id = str( id ).lower()

        self.acquire()
        try:

            local = self.getLocalCache()
            user = local.get( id, None )

            if user is None:
                user = self.cache.get( id, None )
                need_copy = 1
            else:
                need_copy = 0

            if ( password is not None and
                 user is not None and
                 password != user._getPassword() ):
                user = None

            if ( user and
                 (time() < user.getCreationTime().timeTime() + self.timeout) ):
                if need_copy:
                    local[ id ] = user = deepcopy( user )
                return user
            else:
                return None

        finally:
            self.release()

    def getCache( self ):
        """ Get valid cache records """
        valid = []
        cached = self.cache.values()
        now = time()

        for object in cached:
            created = object.getCreationTime().timeTime()
            if object and now < (created + self.timeout):
                valid.append(object)

        return valid

    def getLocalCache( self ):
        """ Return thread local cache """
        return self.local.setdefault( get_ident(), {} )

    def remove( self, id ):
        """ Purge a record out of the cache """
        id = str( id ).lower()

        self.acquire()
        try:

            if self.cache.has_key( id ):
                del self.cache[ id ]

            for local in self.local.values():
                if local.has_key( id ):
                    del local[ id ]

        finally:
            self.release()

    def clear( self ):
        """ Clear the internal caches in all threads """
        self.acquire()
        try:

            self.cache = {}
            self.local = {}

        finally:
            self.release()

    def setTimeout( self, timeout ):
        """ Set the timeout (in seconds) for cached entries """
        self.timeout = timeout
