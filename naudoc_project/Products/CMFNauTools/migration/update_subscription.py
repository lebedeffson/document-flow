"""
Migration script -- Update Subscription from version prior 2.0.

$Editor: kfirsov $
$Id: update_subscription.py,v 1.3 2005/05/14 05:43:46 vsafronovich Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

from Products.CMFCore.utils import getToolByName
from Products.NauScheduler.TemporalExpressions import DailyTE


title = 'Update Subscription'
#classes = ['Products.CMFNauTools.SubscriptionFolder.SubscriptionFolder',
classes = ['Products.CMFNauTools.SubscriptionFolder.Subscription']

version = '3.1.2.53'

def check(context, object):
    return object._class_version < 2.0

def migrate(context, object):
    hour = None
    if hasattr(object.__class__, 'send_hour'):
        hour = object.__class__.send_hour
        del object.__class__.send_hour
    if hasattr(object, 'send_hour'):
        hour = object.send_hour
        del object.send_hour

    minute = None
    if hasattr(object.__class__, 'send_minute'):
        minute = object.__class__.send_minute
        del object.__class__.send_minute
    if hasattr(object, 'send_minute'):
        minute = object.send_minute
        del object.send_minute

    interval = None
    if hasattr(object.__class__, 'send_interval'):
        interval = object.__class__.send_interval
        del object.__class__.send_interval
    if hasattr(object, 'send_interval'):
        interval = object.send_interval
        del object.send_interval

    for attr in ['check_hour', 'check_minute', 'check_interval']:
        if hasattr(object.__class__, attr):
            delattr( object.__class__, attr)
        if hasattr(object, attr):
            delattr( object, attr)

    scheduler = getToolByName(object, 'portal_scheduler')

    #remove old tasks
    for task in ['deliveryTask', 'sendMailTask']:
        if hasattr(object, task):
            scheduler.delScheduleElement( getattr(object, task), force=1)
            delattr(object, task)

    new_taskTE = None
    if hour is not None and minute is not None and interval is not None:
        new_taskTE = DailyTE( hour=hour % 24,
                              minute=minute % 60,
                              second=0,
                              days= int(interval / 24)
                             )
    if hasattr(object, 'send_TempExpr'):
        if new_taskTE is None:
            new_taskTE = object.send_TempExpr
        del object.send_TempExpr

    if hasattr(object, 'check_TempExpr'):
        del object.check_TempExpr

    object.sendMailTempExpr = new_taskTE

    if object.sendMailTempExpr is not None:
        object.sendMailTaskID = scheduler.addScheduleElement( \
            object.sendMail, \
            object.sendMailTempExpr, \
            title='Check and dispatch queued documents task (subscription)')
