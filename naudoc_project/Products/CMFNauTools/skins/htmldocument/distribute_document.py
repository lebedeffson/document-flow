## Script (Python) "send_notification"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= subject
##title=
##
# $Editor: inemihin $
# $Id: distribute_document.py,v 1.4 2005/11/30 15:39:05 ikuleshov Exp $
# $Revision: 1.4 $

from Products.CMFNauTools.SecureImports import re_split

REQUEST = context.REQUEST

lang = REQUEST.get('LOCALIZER_LANGUAGE')

requested_users = REQUEST.get('requested_users', [])
comment = REQUEST.get('comment')
letter_parts = REQUEST.get('letter_parts', [])
letter_type = REQUEST.get('letter_type')
other_user_emails = REQUEST.get('other_user_emails')

if other_user_emails:
    requested_users.extend( re_split( '[;\s]\s*', other_user_emails ) )

message = 'The document is distributed'

sent = context.distributeDocument( template='distribute_document_template'
                          , mto=requested_users
                          , from_member=1
                          , lang=lang
                          , comment=comment
                          , subject=subject
                          , letter_type=letter_type
                          , letter_parts=letter_parts
                          )

if not sent:
    message="Error while sending message"

context.redirect(message=message)
