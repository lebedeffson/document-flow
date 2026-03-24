## Script (Python) "task_elaborate"
##parameters=REQUEST
##title=
# $Id: task_elaborate.py,v 1.8 2006/07/17 11:47:15 ypetrov Exp $
# $Revision: 1.8 $
from Products.CMFNauTools.SecureImports import parseDate
from random import randrange

def task_elaborate_form(REQUEST, message=''):
    wizard_data_id = REQUEST.get('wizard_data_id')
    return REQUEST['RESPONSE'].redirect(
               context.absolute_url( action='task_elaborate_form'
                                   , message=message
                                   , params={'wizard_data_id': wizard_data_id}
                                   ))

session = REQUEST['SESSION']

wizard_data_id = REQUEST.get('wizard_data_id')
while not wizard_data_id:
    # actually this loop is redundant cause each member's
    # session storage is isolated from the others
    wizard_data_id = 'elaboration_wizard_%s' % randrange(1000000000)
    if session.has_key(wizard_data_id):
        wizard_data_id = None

REQUEST.set('wizard_data_id', wizard_data_id)

if not session.has_key(wizard_data_id):
    default_data = { 'task_form': {}
                   , 'task_items': []
                   }
    session.set(wizard_data_id, default_data)


wizard_data = session.get(wizard_data_id)
task_items = REQUEST.get('task_items', wizard_data.get('task_items')) or []

message = ''

if REQUEST.get('add'):
    title = REQUEST.get('title')
    selected_members = REQUEST.get('selected_members')
    description = REQUEST.get('description')
    expiration_date = parseDate('expiration_date', REQUEST)

    if selected_members:
        default_subtask = { 'title': title
                          , 'involved_users': selected_members
                          , 'expiration_date': expiration_date
                          , 'description': description
                          }
        task_items.append(default_subtask)
        message = 'Task item added'
    else:
        message = 'No task members were selected'

elif REQUEST.get('delete'):
    items = []
    selected_keys = REQUEST.get('selected_keys') or []
    for key in range(len(task_items)):
        if key not in selected_keys:
            items.append(task_items[key])

    task_items = items
    message = 'Task item removed'

elif REQUEST.get('finish'):
    root = wizard_data['task_form']
    if not root:
        message = 'Session data was lost'
        return task_elaborate_form(REQUEST, message=message)

    idle_users = root.get('involved_users')
    for item in task_items:
        idle_users = filter( lambda x, m=item.get('involved_users'): x not in m
                           , idle_users)

#         # JScript should prevent this
#         if not item.get('involved_users'):
#            wizard_data['task_items'] = task_items
#            message = 'There are tasks with no users involved!'
#            return task_elaborate_form(REQUEST, message=message)

    if idle_users:
        message = 'There are idle users. Every user must have a task assigned.'
        return task_elaborate_form(REQUEST, message=message)

    # create the root task
    for k in root.keys():
        if k not in ('type', 'title', 'description', 'supervisor',
                     'effective_date', 'expiration_date',
                     'finalization_mode', 'plan_time'):
            del root[k]

    task_id = context.createTask(involved_users = [], **root) #enabled = 1, 
    root_task = context.followup.getTask(task_id)

    for i in range(len(task_items)):
        item = task_items[i]
        title = '%s (%s %d)' % (root.get('title'), context.msg('subtask'), i + 1)

        root_task.followup.createTask(
            title = title,
            description = item.get('description'),
            involved_users = item.get('involved_users'),
            expiration_date = item.get('expiration_date'),
            brains_type = root.get('brains_type', 'directive'),
            plan_time = root.get('plan_time')
        )
    session.delete(wizard_data_id)
    return REQUEST['RESPONSE'].redirect(root_task.absolute_url())

elif REQUEST.get('back'):
    wizard_data['task_items'] = task_items
    return context.task_add_form(context, REQUEST)

else:
    # start
    data = REQUEST.form.copy()
    for key, value in data.items():
        if key.endswith('_date'):
            data[key] = parseDate(key, REQUEST)

    task_form = wizard_data['task_form']
    if task_form and filter( lambda x, b=data.get('involved_users'): x not in b
                           , task_form.get('involved_users')):
        # filter out users that are not longer
        # involved into the root task
        available_users = data.get('involved_users')
        for i in range(len(task_items)):
            item = task_items[i].copy()
            item['involved_users'] = filter( lambda x, a=available_users: x in a
                                           , item['involved_users']
                                           )

            task_items[i] = item
        message = 'Involved users list was reduced at the previous stage!'
    # store the form data from the step 1
    wizard_data['task_form'] = data

wizard_data['task_items'] = task_items

return task_elaborate_form(REQUEST, message)
