"""
Remote object synchronization support.

$Editor: vpastukhov $
$Id: SyncableContent.py,v 1.36 2005/08/21 12:07:28 vsafronovich Exp $
"""
__version__ = '$Revision: 1.36 $'[11:-2]

import errno, os
from cPickle import Pickler
from cStringIO import StringIO
from os import getpid
from string import join

from AccessControl.SecurityManagement import getSecurityManager, \
        newSecurityManager, setSecurityManager
from Acquisition import aq_base, aq_parent, aq_inner, aq_get
from ExtensionClass import Base
from zLOG import LOG, TRACE, INFO, PROBLEM

from ZODB import DB
from ZODB.ExportImport import export_end_marker
#from ZODB.coptimizations import new_persistent_id
from ZODB.utils import p64

from Products.CMFCore.utils import getToolByName

from Exceptions import SimpleError
import Features
from Utils import InitializeClass, \
        normpath, splitpath, joinpath, pathdelim


# ZEO may be missing
_HaveZEO = 0
try:
    from ZEO.ClientStorage import ClientStorage as _ClientStorage
    _HaveZEO = 1
except ImportError:
    class _ClientStorage: pass


class ClientStorage( _ClientStorage ):

    def _startup( self ):
        if not self._call.connect( not self._wait_for_server_on_startup ):
            LOG( 'ClientStorage', PROBLEM, "Failed to connect to storage" )
            raise OSError, ( errno.ENOTCONN, os.strerror(errno.ENOTCONN) )

    def notifyDisconnected( self, ignored ):
        LOG( 'ClientStorage', PROBLEM, "Disconnected from storage" )
        self._connected = 0
        self._transaction = None


class SyncableContent( Base ):
    """
        Mix-in class for objects that can be synchronized to another server.
    """
    _class_version = 1.24

    __implements__ = Features.isSyncableContent

    # attributes saved during remote object synchronization
    _sync_reserved = ( '_sync_status', '_sync_mtime' )

    # attributes which are syncable objects by their own
    _sync_subobjects = ()

    _sync_status = -1
    _sync_mtime = 0

    def updateRemoteCopy( self, *args, **kw ):
        """ Copy this document to remote server
        """
        #print 'SyncableContent.updateRemoteCopy: start %s [%s]' % ( repr(self), self.getId() )
        site = self.getSite()
        if site:
            site.updateRemoteCopy( self, *args, **kw )
        #print 'SyncableContent.updateRemoteCopy: done [%s]' % self.getId()

    def deleteRemoteCopy( self ):
        """ Delete remote copy of this document
        """
        site = self.getSite()
        if site:
            site.deleteRemoteCopy( self )

    def _containment_onDelete( self, item, container ):
        """ Delete remote copy of this object
        """
        if isinstance( item, SyncableContent ):
            status = item._sync_status
            if status < 0:
                self._sync_status = status
                return

        self.deleteRemoteCopy()

    def syncCompleted(self):
        """ Indicate the accomplishment of the synchronization state
        """
        if not hasattr(self, 'sync_completed'):
            self.sync_completed = 0
        return not not self.sync_completed

    def _remote_compare( self, other ):
        """ Compare this object with its remote copy
        """
        if other is None:
            return 2

        if type(other) is not type(self):
            return 3

        self_time  = self.bobobase_modification_time().timeTime()
        other_time = other._sync_mtime or other.bobobase_modification_time().timeTime()

        if self_time == other_time:
            return 0

        return self_time > other_time and 1 or -1

    def _remote_transfer( self, context=None, container=None, server=None, path=None, id=None, parents=None, recursive=None ):
        """
        """
        if id is None:
            id = self.getId()

        LOG( 'SyncableContent._remote_transfer', INFO, '[%s] => %s %s' % (id, path, repr(container)) )

        if container is None:
            path = normpath( path )
            container = server.restrictedTraverse( path, None )

            if container is not None:
                # ensure traverse has not accidentally acquired anything
                try: ppath = container.physical_path()
                except AttributeError: ppath = None
                if ppath != path:
                    container = None

            # try to create remote parents chain
            if container is None and parents:
                ppath  = splitpath( path )[0]
                parent = aq_parent( aq_inner( self ) )

                if ppath and parent is not None and isinstance( parent, SyncableContent ):
                    container = parent._remote_transfer( context, None, server, ppath, None, parents, 0 )

            if container is None:
                raise AttributeError, path

        old = container._getOb( id, None )
        if old is not None and self._remote_compare( old ) == 0:
            LOG( 'SyncableContent._remote_transfer', INFO, '[%s] is up to date' % id )
            return old

        # save the object
        trsn = get_transaction()
        conn = self._p_jar
        conn.tpc_begin( trsn, 1 )
        conn.commit( self, trsn )
        conn.tpc_finish( trsn )

        # export
        data = self._remote_export( context )

        LOG( 'SyncableContent._remote_transfer', INFO, '[%s] exported (%d bytes)' % ( id, len(data.getvalue()) ) )

        # import
        if old is None or not isinstance( old, SyncableContent ):
            remote = container._p_jar.importFile( data )
        else:
            remote = old._remote_import( data )

        if remote is None:
            raise ValueError, 'object transfer failed'

        LOG( 'SyncableContent._remote_transfer', INFO, '[%s] imported' % id )

        if old is None:
            # NB: _setObject executes manage_afterAdd automatically
            container._setObject( id, remote, set_owner=0 )
        else:
            container._setOb( id, remote )

        remote = container._getOb( id )

        if recursive:
            # transfer syncable subobjects
            rpath = joinpath( path, id )

            for sub_id in self._sync_subobjects:
                if hasattr( aq_base(self), sub_id ):
                    ob = getattr( self, sub_id )
                    if isinstance( ob, SyncableContent ):
                        ob._remote_transfer( context, remote, server, rpath, sub_id, 0, recursive )

        if not remote.implements('isPrincipiaFolderish'):
            remote.reindexObject()

        self._sync_status  = 1
        remote._sync_mtime = self.bobobase_modification_time().timeTime()

        LOG( 'SyncableContent._remote_transfer', INFO, '[%s] transferred' % id )

        return remote

    def _remote_delete( self, context=None, container=None, server=None, path=None, id=None ):
        """
        """
        if container is None:
            container = server.restrictedTraverse( path, None )
            if container is None:
                return

        if id is None:
            id = self.getId()

        if container._getOb( id, None ) is not None:
            container._delObject( id )

        self._sync_status = -2

    def _remote_export( self, context=None, file=None, skip_ids=None ):
        """
        """
        if not ( context and context.has('pickler') ):
            new_file = file is None
            saved_stack = None

            if new_file:
                file = StringIO()
                file.write('ZEXP')

            context = _SyncContext( context )

            context.file    = file
            context.stream  = stream  = StringIO()
            context.pickler = pickler = Pickler( stream, 1 )
            context.done    = done    = {}
            context.stack   = stack   = []

            conn = self._p_jar
            try: func = new_persistent_id( conn, conn._creating.append ) # Zope 2.5
            except TypeError: func = new_persistent_id( conn, conn._creating )
            pickler.persistent_id = lambda ob, ctx=context, fn=func: _persistent_id( ob, ctx, fn )

        else:
            new_file = 0
            saved_stack = context.stack

            file    = context.file
            stream  = context.stream
            pickler = context.pickler
            done    = context.done
            stack   = context.stack = []

        object = self.__class__.__basicnew__()

        for attr in ( '_p_jar', '_p_oid', '_p_mtime', '_p_serial' ):
            setattr( object, attr, getattr( self, attr ) )

        # NB: attributes in copy must be changed through __dict__
        # because setattr would register the copy in transaction
        object.__dict__.update( self.__dict__ )

        skip_ids = list( skip_ids or [] )
        skip_ids.extend( self._sync_reserved )
        skip_ids.extend( self._sync_subobjects )

        for id in skip_ids:
            try: del object.__dict__[ id ]
            except KeyError: pass

        stack.append( object )
        count = 0

        while stack:
            object = stack.pop( 0 )
            oid    = object._p_oid
            if oid and done.get( oid ):
                continue

            if count and isinstance( object, SyncableContent ):
                object._remote_export( context )

            else:
                klass = object.__class__
                # try to load ghost
                getattr( object, '_p_mtime', None )

                # XXX we dump only Persistent objects
                if hasattr( klass, '__getinitargs__' ):
                    args = object.__getinitargs__()
                    len(args)
                else:
                    args = None

                module = getattr( klass, '__module__', None )
                if module:
                    klass = module, klass.__name__

                stream.seek( 0 )
                pickler.clear_memo()
                pickler.dump( (klass, args) )
                pickler.dump( object.__getstate__() )

                data = stream.getvalue( 1 )
                oid  = object._p_oid

                #print repr(object), type(object), repr(oid)
                file.write( oid )
                file.write( p64( len(data) ) )
                file.write( data )

                done[ oid ] = 1

            count += 1

        if new_file:
            file.write( export_end_marker )
            file.seek( 0 )

        if saved_stack is not None:
            context.stack = saved_stack

        #dump = open( 'dump.zexp', 'w' )
        #dump.write( file.getvalue() )
        #dump.close()

        return file

    def _remote_import( self, file, save_ids=() ):
        """
        """
        new = self._p_jar.importFile( file )

        all_ids = {}
        for id in self._sync_reserved + self._sync_subobjects + tuple( save_ids ):
            all_ids[ id ] = 1

        for id in all_ids.keys():
            if self.__dict__.has_key( id ):
                setattr( new, id, getattr( self, id ) )

        return new

InitializeClass( SyncableContent )


class SyncableRoot( SyncableContent ):
    """
        Mix-in class for the root of the syncable objects subtree.
    """
    _class_version = 1.25

    isSyncableRoot = 1

    _properties = (
            {'id':'sync_addr',          'type':'string',        'mode':'w'},
            {'id':'sync_path',          'type':'string',        'mode':'w'},
        )

    _sync_reserved = SyncableContent._sync_reserved + \
                     ( 'id', 'sync_addr', 'sync_path' )

    ### default attribute values ###

    sync_addr = ''
    sync_path = ''

    def setSyncProperties( self, addr, path ):
        """
        """
        if addr and path and not self.checkRemoteParams( addr, path ):
            raise SimpleError, 'Parameters for the remote ZEO server are invalid.'

        self.sync_addr = addr
        self.sync_path = path

    def checkRemoteParams( self, addr=None, path=None ):
        """
        """
        if addr is None: addr = self.sync_addr
        if path is None: path = self.sync_path

        try:
            addr = addr.split(':')
            if not ( len(addr) == 2 and len(addr[0]) and int(addr[1]) > 0 ): raise ''
            path = normpath( path ).split( pathdelim )
            if not ( len(path) > 3 and len(path[0]) == 0 ): raise ''
        except:
            return 0

        return 1

    def updateRemoteCopy( self, object=None, recursive=1, REQUEST=None ):
        """ Copy the *object* to remote server
        """
        if object is None:
            object = self
        if not isinstance( object, SyncableContent ):
            return

        server = self._connectRemote()
        if server is None:
            return

        # check whether remote site object exists
        remote_site = self._getRemoteSite( server )
        if remote_site is None:
            server._p_jar.close()
            return

        dest_path, dest_id = self._getRemotePath( object, remote_site, server=server )
        if dest_path is None:
            server._p_jar.close()
            return

        LOG( 'SyncableRoot.updateRemoteCopy', INFO, 'pid %d: transfer [%s] %s' % (getpid(), object.getId(), repr(object)) )

        context = _SyncContext( self )

        try:
            self._setRemoteUser( remote_site )
            object._remote_transfer( context, server=server, path=dest_path, id=dest_id, parents=1, recursive=recursive )

        finally:
            self._resetUser( invalidate=1 )
            get_transaction().commit()
            server._p_jar.close()

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(
                    self.absolute_url( action='folder', message="Remote copy has been updated." ),
                    status=303 )

    def deleteRemoteCopy( self, object=None, REQUEST=None ):
        """ Delete remote copy of the *object*
        """
        if object is None:
            object = self
        if not isinstance( object, SyncableContent ):
            return

        server = self._connectRemote()
        if server is None:
            return

        dest_path, dest_id = self._getRemotePath( object, server=server )
        if dest_path is None:
            return

        #print 'deleteRemoteCopy', object.getId()
        context = _SyncContext( self )
        object._remote_delete( context, server=server, path=dest_path, id=dest_id )

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(
                    self.absolute_url( action='folder', message="Remote copy has been deleted." ),
                    status=303 )

    def _connectRemote( self ):
        """ Establish connection to the remote storage
        """
        if not ( _HaveZEO and self.checkRemoteParams() ):
            return None

        addr = self.sync_addr.split(':')

        storage = ClientStorage( (addr[0], int(addr[1]) ), wait_for_server_on_startup=0 )
        db = DB( storage )
        conn = db.open()
        root = conn.root()

        return root['Application']

    def _getRemoteSite( self, server=None ):
        """
        """
        server = server or self._connectRemote()
        if server is None:
            return None

        return server.unrestrictedTraverse( self.sync_path, None )

    def _getRemotePath( self, object, site=None, server=None ):
        """ Build path of the remote object's container
        """
        site = site or self._getRemoteSite( server )
        if site is None:
            return None, None

        site_path = list( site.getPhysicalPath() )

        base = aq_base( self )
        path = []

        while aq_base( object ) is not base:
            path.insert( 0, object.getId() )
            object = aq_parent( aq_inner( object ) )
            if object is None:
                raise AttributeError

        if path:
            path, id = ( site_path + path[:-1], path[-1] )
        else:
            path, id = ( site_path[:-1], site_path[-1] )

        return ( joinpath( path ), id )

    def _setRemoteUser( self, object ):
        """
        """
        if getattr( self, '_v_remote_users', None ) is None:
            self._v_remote_users = {}

        smgr  = getSecurityManager()
        uname = smgr.getUser().getUserName()

        if self._v_remote_users.has_key( uname ):
            user = self._v_remote_users[ uname ]

        else:
            mstool = getToolByName( object, 'portal_membership' )
            member = mstool.getMemberById( uname, containment=1 )
            user   = member and member.getUser() or None

            self._v_remote_users[ uname ] = user

        if user:
            if getattr( self, '_v_saved_manager', None ) is None:
                self._v_saved_manager = smgr

            newSecurityManager( None, user )

        return user

    def _resetUser( self, invalidate=None ):
        """
        """
        smgr = getattr( self, '_v_saved_manager', None )

        if smgr is not None:
            setSecurityManager( smgr )
            del self._v_saved_manager

        if invalidate:
            try:    del self._v_remote_users
            except: pass

InitializeClass( SyncableRoot )


class _SyncContext:

    def __init__( self, parent=None ):
        if isinstance( parent, _SyncContext ):
            self.__dict__.update( parent.__dict__ )
        else:
            setattr( self, 'root', parent )

    def __getattr__( self, name ):
        if self.__dict__.has_key( name ):
            return self.__dict__[ name ]

        value = aq_get( self.__dict__['root'], name, None, 1 )
        setattr( self, name, value )

        return value

    def has( self, name ):
        return self.__dict__.has_key( name )

    def __len__( self ):
        return len( self.__dict__ )

    def __nonzero__( self ):
        return len( self ) > 0

    def __repr__( self ):
        return repr( self.__dict__ )

    __str__ = __repr__


def _persistent_id( object, context, func ):
    #print '    ', repr(object), type(object), getattr(object,'_p_jar',None)
    if hasattr( object, '_p_oid' ):
        context.stack.append( object )
    return func( object )
