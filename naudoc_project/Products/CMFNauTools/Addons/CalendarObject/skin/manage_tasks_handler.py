## Script (Python) "manage_task_handler"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None, ids,selected_year,selected_month,selected_day
##


context.delTasks(ids)
message='Task deleted'

context.redirect(action='calendar_view', message=message,
                     params={ 'year': selected_year,
                              'month': selected_month,
                              'show_tasks':1
                            }
)
