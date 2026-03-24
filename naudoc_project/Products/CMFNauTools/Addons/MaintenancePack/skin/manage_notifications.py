## Script (Python) "reconfig_mail_subjects"
##title=Configure mail subjects
##parameters=
##
# $Id: manage_notifications.py,v 1.1 2009/02/17 15:04:22 oevsegneev Exp $

from Products.CMFNauTools.SecureImports import SimpleError

REQUEST = context.REQUEST
message = "Portal settings changed"

try:
    context.portal_notifications.editNotifications(REQUEST)
except SimpleError, message_error:
    message=message_error

context.redirect(action = 'manage_notifications_form', message = message)
