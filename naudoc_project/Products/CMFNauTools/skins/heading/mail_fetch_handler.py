## Script (Python) "mail_fetch_handler"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None
##title=Handler for downloading new mail.
##
# $Editor: vpastukhov $
# $Id: mail_fetch_handler.py,v 1.5 2008/05/26 15:04:06 oevsegneev Exp $
# $Revision: 1.5 $

from Products.CMFNauTools.SecureImports import SimpleError

action = None
message = None
error = None
params = {}

action_success  = 'folder'
action_settings = 'folder_edit_form'
action_error    = 'mail_fetch'

try:
    action = action_success

    if REQUEST.has_key('cancel'):
        pass

    elif REQUEST.has_key('settings'):
        action = action_settings

    elif REQUEST.has_key('autorun') or REQUEST.has_key('retry'):
        count = context.fetchMail()
        if count:
            message = "New messages have been received: %(count)s"
            params['count:int'] = count
        else:
            message = "No new mail."

except SimpleError, error:
    error.abort()
    params['error'] = error
    params['portal_status_message'] = error
    return apply( getattr(context, action_error), (context, REQUEST), params )

return context.redirect( action=action, message=message, params=params )
