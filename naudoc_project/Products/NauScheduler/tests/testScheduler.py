"""
$Id: testScheduler.py,v 1.1 2006/02/02 09:58:38 vsafronovich Exp $
$Editor: ikuleshov $
"""
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing.ZopeTestCase import ZopeTestCase

from time import sleep

from Globals import Persistent
from OFS.Traversable import Traversable
from mx.DateTime import DateTimeFrom, now, RelativeDateTime, cmp

from Products.NauScheduler.Scheduler import Scheduler
from Products.NauScheduler.TemporalExpressions import DateTimeTE
from Products.NauScheduler import Config

events_log = []

class DummyItem( Persistent, Traversable ):

    __resource_type__ = 'item'

    def __init__( self, id ):
        self.id = id

    def getId( self ):
        return self.id

    def run( self, element_index ):
        events_log.append( ( element_index, now() ) )

# Each list item represents delay (in seconds) required before starting the event
# corresponding to the item's index.
schedule = [ 6, 9, 5, 10, 6, 7, 7, 11 ]

class SchedulerTests( ZopeTestCase ):
    def afterSetUp( self ):
        Config.QueueExpirationIterval = RelativeDateTime( seconds=7 )

        self.app.dummy = DummyItem(id='dummy')
        self.app._setObject( 'test_scheduler', Scheduler('test_scheduler') )

    def testScheduler( self ):
        scheduler = self.app.test_scheduler
        dummy = self.app.dummy
        self.start_time = now()

        for i in range( len(schedule) ):
            temporal_expr = DateTimeTE( self.start_time + RelativeDateTime( seconds=schedule[i] ) )
            element_id = scheduler.addScheduleElement(
                                       title='Schedule element %s' % i,
                                       method=dummy.run,
                                       temporal_expr=temporal_expr,
                                       args=(i, )
                                     )

        # Wait all events to occure.
        sleep( max(schedule) + 5 )

        self.assertEqual( len(events_log), len(schedule),
                          'Some scheduled events were not executed (events log: %s).' % events_log
                        )

        for event_idx, actual_time in events_log:
            expected_time = self.start_time + RelativeDateTime( seconds=schedule[event_idx] )

            # Here we compare actual and expected start times considering the 1.5 second precision
            # because queue refresh procedure and accidental server perfomance degradation may
            # lead to some delays in events execution.
            self.assertEqual( cmp( actual_time, expected_time, 1.5 ), 0,
                              'Event #%s has wrong start time (expected: %s, got: %s)' % (event_idx, actual_time, expected_time)
                            )

    def beforeTearDown( self ):
        self.app._delObject('test_scheduler')
        self.app._delObject('dummy')
        get_transaction().commit()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    #suite.addTest(makeSuite(SchedulerTests))
    return suite

if __name__ == '__main__':
    framework()

