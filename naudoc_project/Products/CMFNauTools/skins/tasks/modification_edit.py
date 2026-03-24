## Script (Python) "modification_edit"
##parameters=title, description=None, task_id=None, brains_type='directive', consideration_time=None, attachment=None
##title=Add a modification request
from DateTime import DateTime

REQUEST = context.REQUEST

document =  context.implements( 'isCategorial' ) and context \
            or context.parent( feature='isCategorial' )
supervisor = document.getCategoryAttribute( 'OriginalHolder', default=[] )
supervisor = len( supervisor ) > 0 and supervisor[0] or None
involved_users = document.getCategoryAttribute( 'ResponsAuthor', default=[] )

if not title:
    message = 'Please specify task title'
    REQUEST['RESPONSE'].redirect(context.absolute_url(message=message))

    return

effective_date = DateTime()
expiration_date = effective_date + consideration_time

if not involved_users:
    message = 'Please specify involved users'
    REQUEST['RESPONSE'].redirect(context.absolute_url(message=message))
    return

if task_id is None:
    context.createTask( title=title
                      , description=description
                      , involved_users=involved_users
                      , supervisor=supervisor
                      , effective_date=effective_date
                      , expiration_date=expiration_date
                      , brains_type=brains_type
                      , REQUEST=REQUEST
                      )
    return
else:
    task = context.getTask(task_id)
    task.edit( title=title
             , description=description
             , involved_users=involved_users
             , supervisor=supervisor
             , effective_date=effective_date
             , expiration_date=expiration_date
             )
    REQUEST['RESPONSE'].redirect( task.absolute_url() )
