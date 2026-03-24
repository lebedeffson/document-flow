"""
$Id: update_backup.py,v 1.3 2006/09/27 10:03:45 oevsegneev Exp $
$Editor: ypetrov $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

title = 'Update backup tool'
version = '3.2.1.4'
# must be run before update_scheduler2
before_script = 1
order = 3

from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.NauScheduler.TemporalExpressions import UniformIntervalTE

def migrate(context, object):

    physical_root = object.getPhysicalRoot()
    backup_root = physical_root.NauBackupFSRoot
    context.fixBrokenState(backup_root)
    backup_tool = getToolByName(context.portal, 'portal_backup')
    scheduler = getToolByName(context.portal, 'portal_scheduler')
    today = DateTime().earliestTime()

    backup_tool._notified_members = backup_root._notified_members

    for prefix in ('pack', 'backup'):
        old_options = getattr(backup_root, '_%sOptions' % prefix)
        new_options = getattr(backup_tool, '_%sOptions' % prefix)

        # converting old options to interval object
        seconds = (
            old_options['%s_days' % prefix]*86400 +
            old_options['%s_hours' % prefix]*3600 +
            old_options['%s_minutes' % prefix]*60
        )
        if seconds:
            new_options.interval = \
                UniformIntervalTE(seconds = seconds, start_date = today)
            new_options.interval_seconds = seconds

        # moving specific options
        if prefix is 'pack':
            new_options.days_older = old_options['pack_older']
        else:
            new_options.copies = old_options['backup_copies']
            new_options.path = old_options['backup_path']

        # processing scheduler tasks
        task_id = getattr(backup_root, '%s_db_task_id' % prefix)
        if task_id is None:
            # no task to process
            continue

        scheduler.delScheduleElement(task_id)

        # XXX following code hangs up migration in 'Committing transaction'
        #     state. reason is undiscovered.

##        if not new_options.interval:
##            # XXX shouldn't happen, but just in case
##            continue
##
##        setattr(
##            backup_tool,
##            '_%s_task_id' % prefix,
##            scheduler.addScheduleElement(
##                getattr(backup_tool, prefix),
##                temporal_expr = new_options.interval,
##                title = "%s Database" % prefix.capitalize()
##            )
##        )


    # deleting NauBackupFSRoot only if it was configured for current
    # portal or not configured at all
    stupid_property = backup_root.nausite_with_sceduler_URL
    if stupid_property is None or stupid_property == context.portal.absolute_url(1):
        physical_root.manage_delObjects('NauBackupFSRoot')

##    except:
##        from traceback import print_exc
##        print_exc()
##        raise
