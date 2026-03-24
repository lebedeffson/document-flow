## Script (Python) "personalize"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None, userid=None
##title=Personalization Handler
##
# $Id: personalize.py,v 1.8 2004/11/17 15:26:30 vpastukhov Exp $
# $Revision: 1.8 $

from Products.CMFNauTools.SecureImports import SimpleError


if userid is None:
    member = context.portal_membership.getAuthenticatedMember()
    try:
        member.setProperties(REQUEST)

    except SimpleError, error:
        error.abort()
        return apply( context.personalize_form, (context,),
                      script.values( portal_status_message=error )  )

    if REQUEST.has_key('portal_skin'):
        context.portal_skins.updateSkinCookie()

else:
    member = context.portal_membership.getMemberById( userid )
    member.setMemberProperties( REQUEST )

    if not member.has_role('Orphaned'):
        roles = list( member.getRoles() )

        if 'Manager' in roles:
            roles.remove('Manager')
        if REQUEST.get('manager'):
            roles.append('Manager')

        member.setSecurityProfile( roles=roles )

qs = '/personalize_form?portal_status_message=Member+changed.'

if userid:
    qs += '&userid=%s' % userid

context.REQUEST.RESPONSE.redirect(context.portal_url() + qs)
