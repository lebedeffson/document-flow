## Script (Python) "interface_preferences"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Personalization Handler.
##
REQUEST=context.REQUEST

context.portal_membership.setInterfacePreferences( REQUEST )

if REQUEST.has_key('portal_skin'):
    context.portal_skins.updateSkinCookie()

if REQUEST.has_key('lang'):
    lang = REQUEST.get('lang')
    context.portal_membership.setMemberLanguage(lang)
    context.msg.changeLanguage(lang, REQUEST, REQUEST.RESPONSE)
    if context.portal_membership.getLanguage() != lang:
        return context.REQUEST.RESPONSE.redirect(context.portal_url())

qs = '/interface_preferences_form?portal_status_message=Member+changed.'

context.REQUEST.RESPONSE.redirect(context.portal_url() + qs)
