## Script (Python) "reconfig_crypto"
##title=Configure cryptography options
##parameters=
##
# $Id: reconfig_signature.py,v 1.1.1.1 2007/03/23 13:46:13 oevsegneev Exp $

from Products.CMFNauTools.SecureImports import SimpleError

REQUEST = context.REQUEST
message = "Portal settings changed"

try:
    context.portal_signature.editProperties(REQUEST)
except SimpleError, message_error:
    message=message_error

context.redirect(action = 'manage_signature_form', message = message)
