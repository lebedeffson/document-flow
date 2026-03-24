## Script (Python) "add_note"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,text=None,title=None,selected_year,selected_month,selected_day,selected_month_number,is_public=0,topic=None,from_month=None
##title=Add note
##

params={ 'year': selected_year,
         'month': selected_month,
       }

if not from_month:
    params['day']=selected_day

if not title and not text:
    message='Specify title or text'
else:
    if REQUEST.has_key('save_button'):
        context.changeNote(REQUEST['id'], title, text, is_public, topic)
        message='Note changed'
    else:
        context.addNote(title,text,selected_year,selected_month,selected_day,is_public,topic)
        message='Note added'


context.redirect(action='calendar_view', message=message,params=params )