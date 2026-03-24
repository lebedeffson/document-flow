## Script (Python) "manage_workflows"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=
##

REQUEST = context.REQUEST
rget = REQUEST.get
c_id = context.getId()
wf = context.getWorkflow()
states = wf.states

if REQUEST.has_key('save_state2tasktemplatedie'):
    for state_id in states.objectIds():
        task_templates_array = {}  # { 'task_template_id1': 'result_code1', ... }
        task_templates = REQUEST.get( state_id+'_task_templates', [])
        for template_id in task_templates:
            select_name = '%s_result_code_%s' % ( state_id, template_id )
            result_code = REQUEST.get(select_name)
            if result_code == '':
                result_code=None
            task_templates_array[template_id] = result_code
        context.portal_metadata.setState2TaskTemplateToDie( c_id, state_id, task_templates_array )
    fragment='state2tasktemplatedie'

elif REQUEST.has_key('save_state2transition'):
    for state_id, state in states.objectItems():
        state.setProperties( title=state.title
                           , transitions=rget( state_id+'_transitions', [])
                           )
    fragment = 'state2transition'

context.redirect( action='task_template_summary', fragment=fragment )
