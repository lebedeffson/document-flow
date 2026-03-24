## Script (Python) "undo_handler"
##title=Undo transactions
##parameters=transaction_info


from Products.CMFNauTools.SecureImports import SimpleError
from Products.CMFCore.utils import getToolByName

message="Transaction(s)+undone"

ut =getToolByName( context, 'portal_undo' )
try:
    ut.undo(context, transaction_info)
except SimpleError, err_mes:
    message=err_mes

return context.REQUEST.RESPONSE.redirect(
    context.portal_url()+'/undo_form?portal_status_message=' + str(message) )
