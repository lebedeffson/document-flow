"""Defines Schedule class

$Id: Scheduler.py,v 1.29 2006/04/17 13:26:02 ishabalin Exp $
$Editor: ikuleshov $
"""

__version__ = '$Revision: 1.29 $'[11:-2]

import Zope2

from mx.DateTime import now, DateTime
import string
from sys import exc_info
import threading
import time
import traceback
from types import ListType, TupleType
from whrandom import random

import transaction
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, Persistent
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from ZODB.POSException import ConflictError
from zLOG import LOG, TRACE, DEBUG, INFO, ERROR

from Products.CMFCore import CMFCorePermissions

from Schedule import Schedule
from ScheduleElement import ScheduleElement

from Products.CMFNauTools import Utils

import Config
from Logger import LOG as SLOG

createSchedulerForm = DTMLFile('dtml/createScheduler', globals())

def createScheduler( self, id='NauScheduler', REQUEST={} ):
    """
      add Schedule instance
    """
    ob = Scheduler( id )
    self._setObject( id, ob )

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


def initialize(context):
    context.registerClass(
        Scheduler,
        permission = 'Add Schedule',
        constructors = (createSchedulerForm, createScheduler), icon = 'www/Schedule.gif')

    context.registerHelpTitle( 'Scheduler Help' )
    context.registerHelp(directory='help')

_dispatchers = {}

class Scheduler( SimpleItem ):
    """
      Scheduler
    """
    meta_type = 'NauScheduler'

    title = 'Scheduled Event Catalog'

    manage_options = (
            {'label':'Daemon', 'action':'manageSchedulerForm'},
            {'label':'Events queue', 'action':'manageEventsQueueForm'},
            {'label':'Schedule', 'action':'manageScheduleForm'},
            {'label':'Security', 'action':'manage_access'},
            {'label':'Undo', 'action':'manage_UndoForm'},
        )

    security = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manageSchedulerForm')
    manageSchedulerForm = DTMLFile('dtml/manageScheduler', globals())

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manageScheduleForm')
    manageScheduleForm = DTMLFile('dtml/manageSchedule', globals())

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manageEventsQueueForm')
    manageEventsQueueForm = DTMLFile('dtml/manageEventsQueueForm', globals())

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manageTaskForm')
    manageTaskForm = DTMLFile('dtml/manageTask', globals())

    def __init__(self, id):
        self.id = id
        self._schedule = Schedule()

    security.declareProtected(CMFCorePermissions.ManagePortal, 'addScheduleElement')
    def addScheduleElement(self, method, temporal_expr, title='', args=(), kwargs={}):
        """
           Adds task to schedule and returns task id
        """
        schedule = self.getSchedule()
        idx = schedule.idx = schedule.idx + 1
        id = Utils.cookId( schedule, prefix='element', idx=idx )
        element = ScheduleElement( id = id,
                                   title = title,
                                   method_name = method.im_func.func_name,
                                   target_object =  method.im_self,
                                   temporal_expr = temporal_expr,
                                   args = args,
                                   kwargs = kwargs
                                 )

        schedule._setObject( id, element )
        SLOG( Config.ProductName,
             TRACE,
             'added element %s' % id
            )

        #self.resetDispatcher( temporal_expr )
        # postpone event queue refreshing until the end of a transaction
        InvokeAfterTransaction( self.resetDispatcher, (temporal_expr,) )
        return id

    security.declareProtected(CMFCorePermissions.ManagePortal, 'editScheduleElement')
    def editScheduleElement(self, id, temporal_expr):
        element = self.getScheduleElement(id)
        if element is not None:
            element.setTemporalExpression( temporal_expr )

            self.resetDispatcher( temporal_expr )

    security.declareProtected(CMFCorePermissions.View, 'getScheduleElement')
    def getScheduleElement(self, id):
        return self.getSchedule()._getOb( id, None )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'delScheduleElement')
    def delScheduleElement(self, ids, force=1):
        """
            Removes schedule elements.

            Arguments:

                'ids' -- Schedule elements ids list.

                'force' -- Whether to swallow AttributeError while trying to
                           remove the nonexistent object.
        """
        if type( ids ) not in [ ListType, TupleType ]:
            ids = [ ids ]

        schedule = self.getSchedule()
        for id in ids:
            try:
                # set element's state to Zombie
                # so it will be deleted by event queue
                element = schedule._getOb( id )
                element.state = Config.States.Zombie
                #schedule._delObject( id )
                SLOG( Config.ProductName,
                     TRACE,
                     'deleted element %s' % id
                   )

            except (KeyError, AttributeError):
                if not force:
                    raise

        # TODO check queue interval

        #self.resetDispatcher()
        # postpone event queue refreshing until the end of a transaction
        InvokeAfterTransaction( self.resetDispatcher )

    security.declareProtected(CMFCorePermissions.View, 'getSchedule')
    def getSchedule( self ):
        """
            Returns schedule instance.
        """
        return self._schedule

    security.declareProtected(CMFCorePermissions.View, 'getSchedulerName')
    def getSchedulerName(self):
        return '/'.join( self.getPhysicalPath() )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'checkDaemon')
    def checkDaemon(self):
        """
          returns 1 if corresponding thread has started else 0
        """
        name = self.getSchedulerName()
        for thread in threading.enumerate():
            if thread.getName() == 'NauScheduler_%s' % name:
                return 1
        return 0

    security.declareProtected(CMFCorePermissions.ManagePortal, 'startDaemon')
    def startDaemon( self, postpone=None ):
        """
           Start scheduler thread in case it is not running already.
        """
        if Config.DisableScheduler or self.checkDaemon():
            return None

        dispatcher = EventDispatcher( self )
        dispatcher.setDaemon(1)

        _dispatchers[ self._p_oid ] = dispatcher
        if postpone:
            return dispatcher

        dispatcher.start()
        time.sleep( random() )
        return dispatcher

    security.declareProtected(CMFCorePermissions.ManagePortal, 'stopDaemon')
    def stopDaemon( self ):
        dispatcher = _dispatchers.get( self._p_oid )
        if dispatcher:
            dispatcher.terminate()
            return 1

        LOG( Config.ProductName,
             ERROR,
             'No dispatcher thread for scheduler %s' % self.getSchedulerName(),
            )

        return 0

    security.declareProtected(CMFCorePermissions.ManagePortal, 'resetDispatcher')
    def resetDispatcher( self, reason=None ):
        dispatcher = _dispatchers.get( self._p_oid )
        if dispatcher:
            dispatcher.reset( reason )

    def manage_afterAdd(self, item, container):
        """
            Please note that this method commits a transaction in order to
            start scheduling thread.
        """
        self.register()

        if Config.AutoStartDaemonThreads:
            self.REQUEST._hold( DeferredStarter(self) )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'isRegistered')
    def isRegistered(self):
        root = self.getPhysicalRoot()
        schedulers_list = root._getOb( 'SchedulersList', None )
        if not schedulers_list:
            return None

        return schedulers_list.isRegistered( self )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'register')
    def register(self):
        root = self.getPhysicalRoot()
        schedulers_list = root._getOb( 'SchedulersList', None )
        if schedulers_list is None:
            root.manage_addProduct['NauScheduler'].createSchedulersList()
            schedulers_list = root._getOb( 'SchedulersList', None )

        schedulers_list.registerScheduler( self )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'unregister')
    def unregister(self):
        root = self.getPhysicalRoot()
        schedulers_list = root._getOb( 'SchedulersList', None )
        if schedulers_list:
            schedulers_list.unregisterScheduler( self )

    def manage_beforeDelete(self, item, container):
        self.stopDaemon()
        self.unregister()

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_scheduler')
    def manage_scheduler(self, REQUEST):
        """
            ZMI support.
        """
        r = REQUEST.has_key
        if r('start'):
            self.startDaemon()
        elif r('stop'):
            self.stopDaemon()
        elif r('restart'):
            self.stopDaemon()
            self.startDaemon()
        elif r('register'):
            self.register()
        elif r('unregister'):
            self.unregister()

        REQUEST['RESPONSE'].redirect( self.absolute_url() + '/manageSchedulerForm' )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_queue')
    def manage_queue(self, REQUEST):
        """
            ZMI support.
        """
        queue = self.getSchedule().getEventQueue()
        r = REQUEST.has_key
        if r('refresh'):
            self.resetDispatcher()

        REQUEST['RESPONSE'].redirect( self.absolute_url() + '/manageEventsQueueForm' )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_schedule')
    def manage_schedule(self, REQUEST):
        """
            ZMI support.
        """
        schedule = self.getSchedule()
        r = REQUEST.has_key
        if r('remove'):
            self.stopDaemon()
            ids = REQUEST.get('ids') or []
            for id in ids:
                schedule._delObject( id )
            self.startDaemon()

        elif r('suspend'):
            ids = REQUEST.get('ids') or []
            for id in ids:
                ob = schedule._getOb( id )
                ob.suspend()

        elif r('resume'):
            ids = REQUEST.get('ids') or []
            for id in ids:
                ob = schedule._getOb( id )
                ob.resume()

        REQUEST['RESPONSE'].redirect( self.absolute_url() + '/manageScheduleForm' )

class EventDispatcher( threading.Thread ):

    running = False

    min_timestamp = DateTime(1970)
    max_timestamp = DateTime(9999)

    def __init__( self, scheduler ):
        self.scheduler_path = scheduler.getPhysicalPath()

        self.CheckEvent = threading.Event()
        self.TaskSemaphore = threading.Semaphore( Config.MaxThreadsCount )

        threading.Thread.__init__( self, name='NauScheduler_%s' % scheduler.getSchedulerName() )

    def reset(self, reason=None):
        if reason is not None:
            if not reason.listOccurences( self.min_timestamp, self.max_timestamp ):
                return
            
        self.CheckEvent.set()

    def run( self ):
        """
            Start as main schedule thread.
        """
        LOG( Config.ProductName,
             TRACE,
             'Started dispatcher thread for scheduler %s' % '/'.join( self.scheduler_path ),
            )

        app = Zope2.bobo_application()
        schedule = None
        try:
            scheduler = app.unrestrictedTraverse( self.scheduler_path, None )
            if scheduler is None:
                LOG( Config.ProductName,
                     ERROR,
                     'Error traversing scheduler %s' % '/'.join( self.scheduler_path ) )
                return

            schedule = scheduler.getSchedule()
            queue = schedule.getEventQueue( reset=True )

            CheckEvent = self.CheckEvent
            self.running = True
            while self.running:
                if 1: # only for indent
                    if CheckEvent.isSet():
                        CheckEvent.clear()
                        app._p_jar.sync()
                        try:
                            queue.refresh() # commit transaction here
                        except ConflictError:
                            time.sleep( random() )
                            CheckEvent.set()
                            continue
                        else:
                            self.min_timestamp = queue.created
                            self.max_timestamp = queue.expires

                    event = queue.getNextEvent()
                    if event and event.waitTillStart( CheckEvent ):
                        self.TaskSemaphore.acquire()
                        event.setDaemon(1)
                        event.setSemaphore( self.TaskSemaphore )
                        event.start()

                        del event
                        del queue.queue[0]
                    elif not CheckEvent.isSet():
                        # No events left in the queue.
                        # Just waiting for the queue to expire.
                        delay = queue.expires - now()
                        CheckEvent.wait( delay.seconds )
                        CheckEvent.set()

        finally:
            if schedule is not None:
                schedule.deleteEventQueue()
            if app is not None:
                app._p_jar.close()

            LOG( Config.ProductName,
                 TRACE,
                 'Terminating dispatcher thread for scheduler %s' % '/'.join( self.scheduler_path ),
                )

    def terminate( self ):
        self.running = False
        self.CheckEvent.set()
        time.sleep(1)

class DeferredStarter:
    def __init__( self, scheduler ):
        self.scheduler = scheduler

    def __del__( self):
        # N.B.: if naudoc installation failed dispatcher thread exits immediately with error.
        self.scheduler.startDaemon()
        del self.scheduler


class InvokeAfterTransaction:
    """
        Invokes specified method at the end of a successful transaction.
    """
    _transaction_done = False
    subtransaction = False

    def __init__(self, method, args=(), kwargs={} ):
        self.target_method = method
        self.target_args = args
        self.target_kwargs = kwargs
        transaction.get().register( self )

    #######################################################
    # ZODB Transaction hooks
    #######################################################

    def commit(self, reallyme, t): 
        """ Called for every (sub-)transaction commit """
        pass

    def tpc_begin(self, transaction, subtransaction=False): 
        """ Called at the beginning of a transaction
            N.B. subtransaction argument is removed in ZODB 3.4
        """
        self.subtransaction = bool(subtransaction)

    def tpc_abort(self, transaction): 
        """ Called on abort - but not always :( """
        pass

    def abort(self, reallyme, t): 
        """ Called if the transaction has been aborted """
        self.target_method  = None
        self.target_args    = None
        self.target_kwargs  = None

    def tpc_vote(self, transaction):
        """ Only called for real transactions, not subtransactions """
        self._transaction_done = True

    def tpc_finish(self, transaction):
        """ Called at the end of a successful transaction """
        if self.subtransaction or not self._transaction_done:
            # finished the subtransaction
            # or transaction finished without tpc_vote (this shouldn't happen)
            # do nothing in this case
            return
        if self.target_method is not None:
            apply( self.target_method, self.target_args, self.target_kwargs )

        self._transaction_done = False

    def sortKey(self, *ignored):
        """ The sortKey method is used for recent ZODB compatibility which
            needs to have a known commit order for lock acquisition.
            I don't care about commit order, so return the constant 1
        """
        return 1
