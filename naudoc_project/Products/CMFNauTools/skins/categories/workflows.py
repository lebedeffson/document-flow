## Script (Python) "manage_workflows"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=
##
# $Id: workflows.py,v 1.19 2006/02/22 10:31:39 oevsegneev Exp $
# $Revision: 1.19 $
from Products.CMFNauTools.SecureImports import DuplicateIdError

REQUEST = context.REQUEST
wf = context.getWorkflow()
wf_id = wf.getId()

portal_workflow = context.portal_workflow

if REQUEST.has_key('save_properties'):
    #Saving workflow properties
    portal_workflow.setProperties(wf_id, REQUEST['title'])
    REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_properties',
                                                        message='Properties changed'
                                                      ))

if REQUEST.has_key('addState'):
    #Adding new state
    state_id = REQUEST.get('state_id')
    if state_id:
        try:
            portal_workflow.addState(wf_id, state_id)
        except DuplicateIdError, error:
            return apply( context.workflow_states, (context, REQUEST),
                          script.values( portal_status_message=str(error) ) )
    REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_states',
                                                        message='State added'
                                                      ))

if REQUEST.has_key('deleteStates'):
    #Deleting state(s)
    ids = REQUEST.get('ids') or []
    if ids:
        portal_workflow.deleteStates(wf_id, ids)

    REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_states',
                                                        message='State(s) removed'
                                                      ))

if REQUEST.has_key('save_state'):
    #Saving state properties
    transitions = REQUEST.get('transitions', [])
    state = REQUEST.get('state')
    title = REQUEST.get('title')

    # only one version can exist in state
    only_one_version_can_exists = REQUEST.get('only_one_version_can_exists', None)
    if only_one_version_can_exists:
        action='add'
        transition_for_exclude=REQUEST.get('transition_for_exclude')
    else:
        action='remove'
        transition_for_exclude=None

    context.manageAllowSingleStateForVersionArray( action, state, transition_for_exclude )

    portal_workflow.setStateProperties(wf_id, state, title, transitions)
    REQUEST['RESPONSE'].redirect( context.absolute_url( action='state_properties',
                                                        message='State properties changed',
                                                        params={ 'state': state }
                                                      ))
if REQUEST.has_key('set_permissions'):
    state = REQUEST.get('state')
    force_update_roles = REQUEST.get('force_update_roles')
    portal_workflow.setStatePermissions(wf_id, state, REQUEST, None, force_update_roles)

    REQUEST['RESPONSE'].redirect( context.absolute_url( action='state_properties',
                                                        message='State permissions changed',
                                                        params={ 'state': state }
                                                      ))

if REQUEST.has_key('set_attr_properties'):
    state = REQUEST.get('state')
    attribute_id = REQUEST.get('attribute_id')

    wf.setAttributePermissions(REQUEST)
    wf.states[state].setMandatoryAttribute(attribute_id, REQUEST.get('mandatory'))

    REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_attributes_permissions',
                                                        message='State permissions changed',
                                                        params={ 'state': state, 'attr': attribute_id }
                                                      ))

if REQUEST.has_key('setInitialState'):
   ids = REQUEST.get('ids')
   if ids:
       res = wf.states.setInitialState(ids[0])
       if res:
           message = 'Initial state selected'
           REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_states',
                                                               message=message
                                                             ))
       else:
           message = 'You must unset selected initial transition before'
           REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_states',
                                                               message=message
                                                             ))

if REQUEST.has_key( 'unsetInitialState' ):
   wf.states.unsetInitialState()
   REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_states',
                                                       message='Initial state removed'
                                                     ))                                                     

if REQUEST.has_key('setInitialTransition'):
   ids = REQUEST.get('ids')
   if ids:
       res = wf.transitions.setInitialTransition( ids[0] )

       if res:
           message = 'Initial transition selected'
           REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_transitions',
                                                               message=message
                                                             ))
       else:
           message = 'You must unset selected initial state before'
           REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_transitions',
                                                               message=message
                                                             ))
if REQUEST.has_key( 'unsetInitialTransition' ):
   wf.transitions.unsetInitialTransition()
   REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_transitions',
                                                       message='Initial transition removed'
                                                     ))                                                     
                                                     
if REQUEST.has_key('addTransition'):
    trans_id = REQUEST.get('trans_id')
    if trans_id:
        try:
            portal_workflow.addTransition(wf_id, trans_id)
        except DuplicateIdError, error:
            return apply( context.workflow_transitions, (context, REQUEST),
                          script.values( portal_status_message=str(error) ) )
    REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_transitions',
                                                        message='Transition added'
                                                      ))

if REQUEST.has_key('deleteTransitions'):
    ids = REQUEST.get('ids') or []
    if ids:
        portal_workflow.deleteTransitions(wf_id, ids)

    REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_transitions',
                                                        message='Transition(s) removed'
                                                      ))

if REQUEST.has_key('addManagedPermission'):
    p = REQUEST.get('p')
    wf.addManagedPermission(p)
    REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_permissions',
                                                        message='Permission added'
                                                      ))

if REQUEST.has_key('delManagedPermissions'):
    ids = REQUEST.get('ids')
    wf.delManagedPermissions(ids)
    REQUEST['RESPONSE'].redirect( context.absolute_url( action='workflow_permissions',
                                                        message='Permission(s) removed'
                                                      ))

if REQUEST.has_key('save_transition'):
    transition = REQUEST['transition']
    title = REQUEST['title']
    guard_roles = filter( None, REQUEST.get('guard_roles', []) )
    new_state_id = REQUEST['new_state_id']
    actbox_name = REQUEST['actbox_name']
    guard_permissions = REQUEST.get('guard_permissions', [])
    actions = filter( None, REQUEST.get('actions', []) )
    context.setAfterTransitionActions( transition, actions )

    trigger_workflow_method = REQUEST.get('trigger_workflow_method', '1' )
    portal_workflow.setTransitionProperties(wf_id, transition, title, actbox_name, new_state_id, trigger_workflow_method)
    portal_workflow.setTransitionGuardRoles(wf_id, transition, guard_roles)
    portal_workflow.setTransitionGuardPermissions(wf_id, transition, guard_permissions)
    REQUEST['RESPONSE'].redirect( context.absolute_url( action='transition_properties',
                                                        message='Transition properties changed',
                                                        params={'transition': transition}
                                                      ))
