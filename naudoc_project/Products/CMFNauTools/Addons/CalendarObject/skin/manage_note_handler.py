## Script (Python) "manage_note_handler"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None, ids,selected_year,selected_month,selected_day
##


context.delNote(ids)
message='Note deleted'

context.redirect(action='calendar_view', message=message,
                     params={ 'year': selected_year,
                              'month': selected_month,
                              'day':selected_day
                            }
)
