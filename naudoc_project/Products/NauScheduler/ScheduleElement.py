"""
$Id: ScheduleElement.py,v 1.17 2005/11/20 16:47:53 vsafronovich Exp $
$Editor: ikuleshov $
"""

from thread import get_ident

from Acquisition import aq_parent
from OFS.SimpleItem import SimpleItem
from ZPublisher import Publish
from ZPublisher.BaseRequest import BaseRequest

from Products.Localizer.AcceptLanguage import AcceptLanguage

from Products.CMFNauTools.Exceptions import LocatorError
from Products.CMFNauTools.ResourceUid import registerResource, ResourceUid

from Config import States
from TemporalExpressions import TemporalExpression

class ScheduleElement( SimpleItem ):
    """
        Recurrent event definition.
    """
    meta_type = 'Schedule Element'

    __resource_type__ = 'schedule'

    def __init__( self, id, title, method_name, target_object, temporal_expr, auto_remove=1,
                    args=(), kwargs={} ):
        """
           Constructor
        """
        self.id = id
        self.title = title

        self.setTemporalExpression(temporal_expr)

        self.setAction( method_name
                      , ResourceUid( target_object )
                      , *args
                      , **kwargs
                      )

        self.auto_remove = auto_remove
        self.state = States.Runnable

    def isAutoRemovable( self ):
        return getattr( self, 'auto_remove', False )

    def getNextOccurenceDate( self ):
        """
        """
        te = self.getTemporalExpression()
        return te and te.nextOccurence()

    def listOccurences( self, min_date_range, max_date_range, limit=None ):
        te = self.getTemporalExpression()
        if te:
            return te.listOccurences( min_date_range, max_date_range )
        return None

    def setTemporalExpression( self, temporal_expr ):
        """
            Sets up the task recurrence settings.

            Recurrent events are described with a temporal expression object
            assigned to the schedule element.

            Arguments:

               'te' -- TemporalExpression class instance.
        """
        if not isinstance( temporal_expr, TemporalExpression ):
            raise TypeError, 'Temporal expression object expected'

        self.temporal_expr = temporal_expr

    def getTemporalExpression( self ):
        """
         Returns the task recurrence settings.

         Result:

            TemporalExpression class instance.
        """
        return self.temporal_expr

    def setAction( self, method_name, uid, *args, **kwargs ):
        """
            Assigns the action to be executed when event starts.

            Action is determined by the target object referenced by it's
            physical path and method name to be called on the selected
            object. Additional arguments can be also passed to the method.

            Arguments:

              'method_name' -- string containing the callable method name.

              'uid' -- target object resource uid.

              '*args', '**kwargs' -- additional arguments that would be passed
                                     to the method being executed.
        """
        self.method_name = method_name
        self.target_uid = uid
        self.method_args = args
        self.method_kwargs = kwargs

    def getAction( self ):
        """
            Returns the action settings for the schedule element.

            Result:

                Dictionary containing the following keys: 'method_name',
                'physical_path', 'args', 'kwargs'.
        """
        return { 'method_name': self.method_name, 
                 'uid': self.target_uid,
                 'args': self.method_args, 
                 'kwargs': self.method_kwargs
               }

    def doAction( self ):
        ob = self.getTargetObject()
        if ob is None:
            raise 'NotFound', 'target object with uid %s does not found' % self.target_uid

        method = getattr( ob, self.method_name, None )
        if method is None:
            raise AttributeError, 'Object %s has no method %s' % ( repr(ob), self.method_name )

        if hasattr(Publish, '_requests'):
            # Provide Localizer.get_request method with fake request object.
            ident = get_ident()
            request = BaseRequest()
            request.other['USER_PREF_LANGUAGES'] = AcceptLanguage('')
            Publish._requests[ident] = request

        try:
            return apply( method, self.method_args, self.method_kwargs )
        finally:
            if hasattr(Publish, '_requests') and Publish._requests.has_key(ident):
                Publish._requests[ident].close()
                del Publish._requests[ident]

    def getTargetObject( self ):
        try:
            return self.target_uid.deref(self)
        except LocatorError:
            return None

    def getState( self ):
        """
         Returns the current state of the schedule element.

         Task can be either in a 'running', 'idle' or 'disabled' state:

            'running' -- task is being executed right now.

            'idle' -- task is enabled and waiting for it's time to start.

            'disabled' -- task was disabled and will never start.

         Result:

            string
        """
        if not self.getNextOccurenceDate():
            return States.Zombie

        return self.state

    def resume( self ):
        """
            Enables the task.
        """
        self.state = States.Runnable
        scheduler = aq_parent(self)
        scheduler.resetDispatcher()

    def suspend( self ):
        """
            Disables the task.
        """
        self.state = States.Suspended
        scheduler = aq_parent(self)
        scheduler.resetDispatcher()


class ScheduleResource:

    def identify( portal, object ):
        return { 'uid' : object.getId() }

    def lookup( portal, uid=None, **kwargs ):
        scheduler = getToolByName( portal, 'portal_scheduler' )

        object = scheduler.getScheduleElement( str(uid) )
        if object is None:
            raise Exceptions.LocatorError( 'schedule', uid )

        return object


def initialize( context ):
    # module initialization callback

    registerResource( 'schedule', ScheduleResource )
