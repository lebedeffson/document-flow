"""
$Id: update_scheduler.py,v 1.6 2006/09/27 10:03:45 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

title = 'Update scheduler service'
version = '3.2.1.4'
before_script = 1
order = 1

from DateTime import DateTime
from OFS.Uninstalled import BrokenClass

from Products.NauScheduler.TemporalExpressions import UniformIntervalTE, DailyTE, DateTimeTE
from Products.NauScheduler.ScheduleElement import ScheduleElement
from Products.NauScheduler.Schedule import Schedule

def check( context, object ):
    if hasattr( object, 'ScheduleList' ):
        return 1
    if isinstance( object.portal_scheduler, BrokenClass ) or \
       isinstance( object.portal_scheduler, Schedule ):
        return 1
    return 0

def migrate( context, object ):
    root = object.getPhysicalRoot()
    if hasattr( root, 'ScheduleList' ):
        root._delObject( 'ScheduleList' )

    if not (isinstance( object.portal_scheduler, BrokenClass ) or \
       isinstance( object.portal_scheduler, Schedule ) ):
        return

    old_scheduler = object.portal_scheduler
    getattr( old_scheduler, '_p_mtime', None )
    getattr( old_scheduler._data, '_p_mtime', None )
    old_data = object.portal_scheduler._data._tasks.items()
    object._delObject( 'portal_scheduler' )

    object.manage_addProduct['CMFNauTools'].manage_addTool( 'NauSite Scheduler Tool', None )
    schedule =  object.portal_scheduler.getSchedule()

    for id, props in old_data:
        ob = object.unrestrictedTraverse( props['physicalPath'], None )
        if ob is None:
            continue

        start = props['timeNext']
        if not start or start > DateTime('2007/01/01'):
            continue

        end = props['timeEnd']
        if end and end > DateTime('2010/01/01'):
            end = None

        if end and ( end.isPast() or start > end ):
            continue


        frequency = props['frequency']
        if not frequency and start.isPast():
            continue

        if frequency and frequency % 86400 == 0:
            temporal_expr = DailyTE( hour=start.hour(),
                                     minute=start.minute(),
                                     second=start.second(),
                                     days=frequency / 86400,
                                     start_date=start,
                                     end_date=end
                                   )
        elif frequency:
            temporal_expr = UniformIntervalTE( seconds=frequency,
                                               start_date=start,
                                               end_date=end
                                             )
        else:
            temporal_expr = DateTimeTE( start )

        element = ScheduleElement( id = id,
                                   title = props['title'],
                                   method_name = props['methodName'],
                                   target_object =  ob,
                                   temporal_expr = temporal_expr,
                                   args = props['args'],
                                   kwargs = props['kwargs']
                                 )
        schedule._setObject( id, element )
        if props['status'] == 'paused':
            schedule._getOb( id ).suspend()
