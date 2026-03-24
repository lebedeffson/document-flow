## Script (Python) "add_task"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,text=None,title=None,is_public=0,from_month=None,priority, state,plan_date,ready_proc
##title=Create content
##



if REQUEST.has_key('save_button'):
    context.changeTask(REQUEST['id'], title,text,plan_date.year(),plan_date.month(),plan_date.day(),priority,state, ready_proc,is_public)
    message='Task changed'

else:
    if not title and not text:
        message='specify title or text'
    else:
        context.addCalendarTask(title
                                ,text
                                ,plan_date.year()
                                ,plan_date.month()
                                ,plan_date.day()
                                ,priority
                                ,state
                                ,ready_proc
                                ,is_public
                                )
        message='Task added'

params={ 'year': plan_date.year(),
         'month': plan_date.month(),
         'show_tasks':1,
       }

context.redirect(action='calendar_view', message=message,params=params )