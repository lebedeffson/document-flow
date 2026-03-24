## Script (Python) "document_confirmation"
##parameters=comment='', involved_users=[], confirm_by_turn=0, brains_type=None, notification_level=0, finalization_mode=None
##title=Add a task item
#raise 'error'
from Products.CMFNauTools.SecureImports import parseDateTime
REQUEST = context.REQUEST

expiration_date = parseDateTime(REQUEST['expiration'])

if brains_type=='signature_request':
    cfm_msg = 'Signature request for the document'
    chain_msg = 'Chain signature request for the document'
elif brains_type=='publication_request':
    cfm_msg = 'Publication request for the document'
    chain_msg = 'Chain publication request for the document'
else:
    cfm_msg = 'Confirmation request of the document'
    chain_msg = 'Chain confirmation of the document'

# Do not allow stupid users to crash everything here
if not involved_users:
    return context.document_confirmation_form(context, REQUEST)

task_id = context.followup.createTask( title="%s '%s'" % ( context.msg(cfm_msg),
                                                           context.title_or_id(),
                                                         ),
                                       description=comment,
                                       involved_users=involved_users,
                                       expiration_date=expiration_date,
                                       type=brains_type,
                                       ordered=confirm_by_turn,
                                       notification_level=notification_level,
                                       finalization_mode=finalization_mode,
                                     )

REQUEST['RESPONSE'].redirect(context.absolute_url() + '/document_follow_up_form')
