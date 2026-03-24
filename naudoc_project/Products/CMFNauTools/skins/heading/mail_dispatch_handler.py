## Script (Python) "mail_dispatch_handler"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None
##title=Handler for sending outgoing mail.
##
# $Editor: vpastukhov $
# $Id: mail_dispatch_handler.py,v 1.1 2004/07/06 14:33:58 vpastukhov Exp $
# $Revision: 1.1 $

from Products.CMFNauTools.SecureImports import SimpleError

action = 'folder'
message = None

if REQUEST.has_key('send'):
    count, errors = context.sendMail( uids=REQUEST.get('uids') )

    if errors:
        message = count and "Some messages were not sent due to errors." \
                         or "Nothing was sent due to errors."
    else:
        message = count and "Messages have been sent." \
                         or "Nothing to send."

return context.redirect( action=action, message=message )
