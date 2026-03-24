## Script (Python) "manage_comments"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, ids=(), text=None, type=None
##title=Handler for resolution templates management form.
##
# $Editor: vpastukhov $
# $Id: manage_comments.py,v 1.4 2004/09/16 15:38:52 vpastukhov Exp $
# $Revision: 1.4 $

tool = context.portal_comments
message = None

if REQUEST.has_key('add'): # add new comment
    tool.addComment( text.strip(), type.strip() )
    message = "Entry added"

elif REQUEST.has_key('remove'): # remove comments
    if ids:
        for id in ids:
            tool.deleteComment( id )
        message = "Template(s) deleted"
    else:
        message = "Please select one or more items first."

elif REQUEST.has_key('save'): # edit comment
    context.setText( text.strip() )
    message = "Changes saved."

return tool.redirect( action='manageComments', message=message, REQUEST=REQUEST )
