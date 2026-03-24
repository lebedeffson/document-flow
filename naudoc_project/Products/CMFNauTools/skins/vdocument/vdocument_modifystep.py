## Script (Python) "vdocument_modifystep"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, title, step_id, allowed_members=[], allowed_groups=[], writable_columns=[], readable_columns=[], rollback_steps=[]
##title=Configure the Business Procedure's step
# $Editor: ikuleshov $
# $Id: vdocument_modifystep.py,v 1.7 2005/11/16 17:49:14 vsafronovich Exp $
# $Revision: 1.7 $
step = context.getStepById(step_id)

step.setTitle(title)
step.setAllowedMembers(allowed_members)
step.setAllowedGroups(allowed_groups)

step.setWritableColumns(writable_columns)
step.setReadableColumns(readable_columns)

step.setRollbackSteps(rollback_steps)

step.setDuration(REQUEST['duration'])

options_form = context.getTypeInfo().getActionById( 'edit' )

message = "Step options changed"
context.redirect( action=options_form, message=message)
