## Script (Python) "task_edit"
##parameters=title, alarm_type, finalization_mode=None, description=None, supervisor=None, involved_groups=[], involved_users=[], periodical=None, task_id=None, brains_type='directive'
##title=Add a task item
# $Id: task_edit.py,v 1.20 2008/09/23 11:54:09 oevsegneev Exp $
# $Revision: 1.20 $
# $Editor: ikuleshov $
from Products.CMFNauTools.SecureImports import parseDateTime, \
                                               DailyTE, WeeklyTE, MonthlyByDayTE, \
                                               MonthlyByDateTE, YearlyTE, \
                                               DateTimeTE, UnionTE

REQUEST = context.REQUEST

if not title:
    message = 'Please specify task title'
    return REQUEST['RESPONSE'].redirect(context.absolute_url(message=message))

duration = None
temporal_expr = None
alarm_settings = {}

effective_date = parseDateTime(REQUEST['effective_date'])
expiration_date = parseDateTime(REQUEST['expiration_date'])

plan_time = REQUEST['plan_time']

# parse alarm settings
if alarm_type == 'percents':
    alarm_settings['value'] = REQUEST['alarm_percents']
elif alarm_type == 'periodical':
    alarm_settings['value'] = REQUEST['alarm_period']
    alarm_settings['period_type'] = REQUEST['alarm_period_type']
elif alarm_type == 'custom':
    alarm_settings['value'] = map(parseDateTime,
                                  REQUEST.get('alarm_dates', ()))

if alarm_settings:
    alarm_settings['type'] = alarm_type
    alarm_settings['note'] = REQUEST['alarm_note']
    alarm_settings['include_descr'] = not not REQUEST.get('alarm_includes_descr')
else:
    alarm_settings = None

if periodical:
    duration = REQUEST['duration_time']
    repeat_type = REQUEST['repeat_type']

    if repeat_type == 'daily_repeat':
        temporal_expr = DailyTE( effective_date.hour(),
                                 effective_date.minute(),
                                 effective_date.second(),
                                 REQUEST['daily_repeat'],
                                 effective_date,
                                 expiration_date
                               )

    elif repeat_type == 'weekly_repeat':
        temporal_expr = WeeklyTE( REQUEST['weekly_repeat'],
                                  REQUEST['weekly_repeat_day'],
                                  effective_date,
                                  expiration_date
                                )

    elif repeat_type == 'monthly_repeat':
        if REQUEST['monthly_repeat_by'] == 'day':
            temporal_expr = MonthlyByDayTE( REQUEST['monthly_repeat'],
                                            [ REQUEST['monthly_repeat_week'] ],
                                            [ REQUEST['monthly_repeat_dow'] ],
                                            effective_date,
                                            expiration_date
                                          )

        else:
            temporal_expr = MonthlyByDateTE( REQUEST['monthly_repeat'],
                                             [ REQUEST['monthly_repeat_day'] ],
                                             effective_date,
                                             expiration_date
                                           )

    elif repeat_type == 'yearly_repeat':
        temporal_expr = YearlyTE( REQUEST['yearly_repeat'],
                                  REQUEST['yearly_repeat_month'],
                                  effective_date,
                                  expiration_date
                                )

    elif repeat_type == 'custom_repeat':
        temporal_expr = UnionTE([ DateTimeTE(parseDateTime(value))
                                  for value in REQUEST['custom_dates'] ])

    assert temporal_expr is not None, repeat_type

if not involved_users:
    message = 'Please specify involved users'
    REQUEST['RESPONSE'].redirect(context.absolute_url(message=message))
    return

params = { 'title': title,
           'description': description,
           'involved_users': involved_users,
           'supervisor': supervisor,
           'effective_date': effective_date,
           'expiration_date': expiration_date,
           'finalization_mode': finalization_mode,
           'alarm_settings': alarm_settings,
           'REQUEST': REQUEST,
         }

if periodical:
    params[ 'temporal_expr' ] = temporal_expr
    params[ 'duration' ] = duration
    if task_id is None: 
        params[ 'recurrent_type' ] = brains_type
        brains_type = 'recurrent'

elif effective_date.isFuture():
    params[ 'temporal_expr' ] = DateTimeTE(effective_date)
    params[ 'duration' ] = expiration_date - effective_date
    if task_id is None: 
        params[ 'recurrent_type' ] = brains_type
        brains_type = 'recurrent'

elif brains_type == 'directive':
    params[ 'plan_time' ] = plan_time


if task_id is None:
   context.createTask( type=brains_type,
                       **params
                     )
else:
   task = context.getTask( task_id )
   task.edit( **params )
   REQUEST['RESPONSE'].redirect( task.absolute_url() )
