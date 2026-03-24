## Script (Python) "voting_edit"
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=
##title=
##
# $Editor : ypetrov $
# $Id: voting_edit.py,v 1.5 2005/05/14 05:43:54 vsafronovich Exp $
# $Revision: 1.5 $
request = container.REQUEST
response = request.RESPONSE

r = request.get

action = 'voting_edit_form'
if r( 'apply_changes' ):
    context.configure( r( 'choice_titles', [] ), r( 'finish_voting' ), r( 'main_voting' ) )
    message = 'Changes saved'
    action = None

elif r( 'delete_choice' ):
    context.delChoices( r( 'del_choices', [] ) )
    message = 'Choices deleted'

elif r( 'add_choice' ):
    title = r( 'new_choice_title' )
    if title:
        context.addChoice( title )
        message = 'Choice added'
    message = 'Please specify title of choice'

return context.redirect( action=action, message=message )
