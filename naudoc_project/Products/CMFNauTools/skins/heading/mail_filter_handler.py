## Script (Python) "mail_filter_handler"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None, id=None, title=None, before=None, action=None, selected=None, test=None, operation=None, header=None, patterns=None, patternrec=None
##title=Handler for mail filter management forms.
##
# $Editor: vpastukhov $
# $Id: mail_filter_handler.py,v 1.7 2004/07/02 14:26:43 vpastukhov Exp $
# $Revision: 1.7 $

redir = 'mail_filters_form'
form = ''
params = {}
message = None

if REQUEST.has_key('cancel_form'):
    pass

elif REQUEST.has_key('add_filter'):
    id = context.addFilter( title=title )
    if before:
        context.moveFilter( id, before=before )

    form = 'mail_filter_form'
    params['id'] = id
    message = "New message filter has been added."

elif REQUEST.has_key('save_filter'):
    filter = context.getFilter( id )
    filter.setTitle( title )

    if action:
        ai = context.getActionInfo( action )
        props = {}
        for param in ai.getParameters():
            name = param['id']
            if REQUEST.has_key( 'param/%s' % name ):
                props[ name ] = REQUEST[ 'param/%s' % name ]
        filter.setAction( action, **props )
    else:
        filter.setAction( None )

    if patternrec:
        for idx, value in patternrec.items():
            filter.edit( index=int(idx), patterns=value )

    message = "Message filter saved."

elif REQUEST.has_key('add_test'):
    if test != 'header':
        header = None

    filter = context.getFilter( id )
    filter.append( test, op=operation, header=header, patterns=patterns )

    form = 'mail_filter_form'
    params['id'] = id
    message = "New filter condition has been added."

elif REQUEST.has_key('delete_tests'):
    if selected:
        filter = context.getFilter( id )

        # start deletion from tail
        selected.sort()
        selected.reverse()

        for idx in selected:
            filter.remove( index=idx )

        message = "Filter condition has been deleted."

    else:
        message = "Please select one or more items first."

    form = 'mail_filter_form'
    params['id'] = id

elif not selected:
    message = "Please select one or more items first."

elif REQUEST.has_key('delete_filters'):
    for id in selected:
        context.deleteFilter( id )
    message = "Message filter has been deleted."

elif REQUEST.has_key('enable_filters'):
    for id in selected:
        context.getFilter( id ).enableFilter()
    message = "Message filter has been enabled."

elif REQUEST.has_key('disable_filters'):
    for id in selected:
        context.getFilter( id ).enableFilter( enable=False )
    message = "Message filter has been disabled."


if form:
    params['portal_status_message'] = message
    return apply( getattr(context, form), (context, REQUEST), params )
else:
    return context.redirect( action=redir, params=params, message=message )
