"""
$Id: testSchedule.py,v 1.1 2006/02/02 09:58:38 vsafronovich Exp $
$Editor: ikuleshov $
"""
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing.ZopeTestCase import ZopeTestCase

from Globals import Persistent
from OFS.Traversable import Traversable
from mx.DateTime import DateTimeFrom, now, RelativeDateTime

from Products.NauScheduler.Schedule import Schedule
from Products.NauScheduler.ScheduleElement import ScheduleElement
from Products.NauScheduler.TemporalExpressions import DateTimeTE


class DummyItem( Persistent, Traversable ):
  
    __resource_type__ = 'item'

    def __init__( self, id ):
        self.id = id

    def getId( self ):
        return self.id

    def say( self, text ):
        return text

start_time = now() + RelativeDateTime(minutes=4)

class ScheduleTests( ZopeTestCase ):
    items_count = 5

    def afterSetUp( self ):
        self.app._setOb('dummy', DummyItem(id='dummy') )
        dummy = self.app.dummy

        schedule = self.app.schedule = Schedule()
        get_transaction().commit(1)
        method = dummy.say

        for i in range( self.items_count ):
            temporal_expr = DateTimeTE( start_time + RelativeDateTime(seconds=i) )
            element = ScheduleElement( id='testelement%s' % i,
                                       title='Say hello %s' % i,
                                       method_name=method.im_func.func_name,
                                       target_object=method.im_self,
                                       temporal_expr=temporal_expr,
                                       kwargs={'text': 'hello %s' % i}
                                     )
            schedule._setObject( 'element%s' % i, element )

    def testEventQueue( self ):
        schedule = self.app.schedule
        queue = schedule.getEventQueue()
        expected_queue = schedule.getEventQueue()
        assert queue is expected_queue, 'Expected: %s, got: %s' % ( queue, expected_queue )

        queue_size = len(queue.queue)
        assert queue_size == items_count, 'Wrong queue size. Got: %s, expected: %s' % ( queue_size, items_count )
        assert queue.expires, 'Queue has no expiration date'

    def beforeTearDown( self ):
        del self.app.schedule
        del self.app.dummy
        get_transaction().commit()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    #suite.addTest(makeSuite(ScheduleTests))
    return suite

if __name__ == '__main__':
    framework()

