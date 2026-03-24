"""Defines Schedule class

$Id: Schedule.py,v 1.50 2006/04/06 08:06:11 ishabalin Exp $
$Editor: ikuleshov $
"""

__version__ = '$Revision: 1.50 $'[11:-2]

import Zope2

from bisect import insort
import sys
from threading import Thread, Event as ThreadingEvent
from time import time
from types import StringType

from mx.DateTime import RelativeDateTime, now

import transaction
from AccessControl import ClassSecurityInfo, SecurityManagement, User
from Acquisition import aq_parent
from Globals import InitializeClass
from OFS.ObjectManager import ObjectManager
from zLOG import LOG as ZOPELOG, TRACE, DEBUG, INFO, ERROR

from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.CMFCore import CMFCorePermissions

import Config
from Config import States
from Logger import LOG

class EventQueue:
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__( self, schedule, expires=None ):
        self.queue = []
        self.schedule = schedule
        self.expires = expires

    def isExpired( self ):
        return not self.expires or self.expires < now()

    def invalidate( self ):
        self.expires = None

    def refresh( self ):
        self.queue = []
        created = now()

        start_from = created
        if self.expires is not None and self.expires < created:
            start_from = self.expires

        expires = created + self.getExpirationInterval()

        need_commit = False
        for id, element in list(self.schedule.objectItems()):
            state = element.getState()
            if state == States.Zombie:
                if element.isAutoRemovable():
                    self.schedule._delObject( id )
                    need_commit = True
                continue
            elif state == States.Suspended:
                continue

            occurences = element.listOccurences( start_from, expires ) or []
            for datetime in occurences:
                insort( self.queue, (datetime, id) )

        self.created = created
        self.expires = expires
        if need_commit:
            transaction.commit()

        try:
            scheduler_name = self.schedule.getSchedulerName()
        except AttributeError:
            scheduler_name = None

        LOG( scheduler_name, TRACE,
             'Queue refresh (%s events)' % len( self.queue )
           )

    def getExpirationInterval( self ):
        return Config.QueueExpirationIterval

    def __len__( self ):
        return len( self.queue )

    def getNextEvent( self ):
        if not len( self ):
            return None

        start_date, element_id = self.queue[0]
        scheduler_path = '/'.join( self.schedule.getPhysicalPath() )
        return ScheduleEvent( start_date, element_id, scheduler_path )


_event_queues = {}

class ScheduleEvent( Thread ):
    def __init__( self, start_date, element, scheduler_path, semaphore=None ):
        if type( element ) is not StringType:
            element = element.getId()

        Thread.__init__( self, name=element )
        self.id = time()
        self.element_id = element
        self.start_date = start_date
        self.scheduler_path = scheduler_path
        self.semaphore = semaphore

    def run( self ):
        """
          Starts event action.

          This method is executed within the separate ZODB connection.
        """
        try:
            self._app = Zope2.bobo_application()
            try:
                try:
                    LOG( self.scheduler_path, INFO,
                         'Running action for element %s (%s)' % ( self.element_id, self.id ),
                       ) 

                    system = User.UnrestrictedUser( 'System Processes'
                                                  , ''
                                                  , ('manage', 'Member','Manager',)
                                                  , [])
                    SecurityManagement.newSecurityManager(None, system)
                    try:
                        result = self.getScheduleElement().doAction()
                    finally:
                        SecurityManagement.noSecurityManager()
         
                    transaction.commit()
                except:
                    transaction.abort()
                    LOG( self.scheduler_path, ERROR,
                         'Error while executing action for element %s (%s)' % ( self.element_id, self.id ),
                         error=sys.exc_info()
                       )
                else:
                    LOG( self.scheduler_path, INFO,
                         'Exiting action for element %s (%s) with result: %s' % ( self.element_id, self.id, result ),
                       )
                     
            finally:
                self._app._p_jar.close()
                del self._app

        finally:
            semaphore = self.getSemaphore()
            if semaphore:
                semaphore.release()

    def waitTillStart( self, threading_event=None ):
        if threading_event is None:
            threading_event = ThreadingEvent()

        threading_event.wait( self.getRemainingTime().seconds )

        return not threading_event.isSet()

    def getRemainingTime( self ):
        return self.start_date - now()

    def getScheduleElement( self ):
        scheduler = self._getScheduler()
        if scheduler:
            schedule = scheduler.getSchedule()
            return schedule._getOb( self.element_id, None )
        return None

    def setSemaphore( self, semaphore ):
        self.semaphore = semaphore

    def getSemaphore( self ):
        return self.semaphore

    def _getScheduler( self ):
        return self._app.unrestrictedTraverse( self.scheduler_path, None )

InitializeClass( ScheduleEvent )

class Schedule( BTreeFolder2 ):

    security = ClassSecurityInfo()
    security.setDefaultAccess( 1 )

    idx = 0
        
    #id = 'schedule'

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getEventQueue' )
    def getEventQueue( self, reset=False ):
        if reset:
            self.deleteEventQueue()

        try:
            queue = _event_queues[ self._p_oid ]
        except KeyError:
            queue = _event_queues[ self._p_oid ] = EventQueue( self )

        if queue.isExpired():
            queue.refresh()

        return queue

    security.declarePrivate( 'deleteEventQueue' )
    def deleteEventQueue( self ):
        try:
            del _event_queues[ self._p_oid ]
        except KeyError:
            pass

InitializeClass( Schedule )
