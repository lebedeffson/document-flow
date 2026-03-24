## Script (Python) "change_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=password, confirm, domains=None, userid=None
##title=Action to change password
##

mt = context.portal_membership
failMessage=context.portal_registration.testPasswordValidity(password, confirm)

if failMessage:
    return context.password_form(context,
                                 context.REQUEST,
                                 error=failMessage)

if userid is None:
    member = mt.getAuthenticatedMember()
    mt.setPassword(password, domains)
    mt.credentialsChanged(password)
else:
    member = mt.getMemberById(userid)
    password = password or None
    member.setSecurityProfile(password=password, domains=domains)

return context.personalize_form(context,
                                context.REQUEST,
                                portal_status_message='Password changed.')
