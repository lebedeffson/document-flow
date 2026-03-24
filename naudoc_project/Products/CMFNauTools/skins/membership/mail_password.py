## Script (Python) "mail_password"
##title=Mail a user's password
##parameters=userids
# $Id: mail_password.py,v 1.3 2005/05/14 05:43:50 vsafronovich Exp $
# $Revision: 1.3 $

REQUEST=context.REQUEST
for userid in userids:
    context.portal_registration.mailPassword(userid, REQUEST)

return context.mail_password_response( context, REQUEST )
