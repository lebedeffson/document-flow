"""
$Id: update_scheduler2.py,v 1.7 2007/06/19 11:21:09 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

title = 'Update scheduler service 2'
version = '3.2.1.4'
before_script = 1
order = 2 # after update_scheduler1 script

from OFS.Folder import Folder
from Products.NauScheduler.Schedule import Schedule
from Products.CMFNauTools.ResourceUid import ResourceUid
from OFS.Uninstalled import BrokenClass

def check( context, object ):
    scheduler = object.portal_scheduler
    # pass if scheduler is broken
    if isinstance( scheduler, BrokenClass ):
        return True
    schedule = scheduler.getSchedule()

    # check for BTreeFolder nature
    if getattr(schedule, '_tree', None) is None\
       or getattr( schedule, '_mt_index', None) is None:
        return True

    # check for wrong place of 'idx' attribute
    if hasattr( scheduler, 'idx' ):
        return True

    # check for using target path instead of target uid
    for element in scheduler.getSchedule().objectValues():
        if getattr( element, 'target_path', None) is not None:
            return True

    return False

def migrate( context, object ):
    scheduler = object.portal_scheduler

    # disable dispatcher 
    scheduler.stopDaemon()
    try:
        schedule = scheduler.getSchedule()
 

        # migrate schedule to BTreeFolder
        if getattr(schedule, '_tree', None) is None\
           or getattr( schedule, '_mt_index', None) is None:
            new_schedule = Schedule()
            scheduler._schedule = new_schedule
            fake_folder = Folder()
            fake_folder.__dict__ = schedule.__dict__
            scheduler.getSchedule()._populateFromFolder( fake_folder )
            schedule = scheduler.getSchedule()
        
        # migrate 'idx' attribute to schedule
        if hasattr( scheduler, 'idx'):
            schedule.idx = scheduler.idx
            del scheduler.idx
 
        # migrate target path to target uid
        bad_elements = []
        for element in schedule.objectValues():
            if hasattr(element, 'target_path'):
                try:
                    target = object.unrestrictedTraverse( element.target_path )
                    element.target_uid = ResourceUid(target)
                    del element.target_path
                except:
                    bad_elements.append( element.getId() )
        if len( bad_elements ) > 0:
            schedule.delScheduleElement( bad_elements )
 
    finally:
        scheduler.startDaemon()
           