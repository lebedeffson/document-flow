## Script (Python) "change_language"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lang
##title=Change launguage
##
# $Editor: vpastukhov $
# $Id: change_language.py,v 1.3 2004/02/08 14:01:38 vpastukhov Exp $
# $Revision: 1.3 $

REQUEST=context.REQUEST
msg=context.msg

#set default language for the member
context.portal_membership.setMemberLanguage(lang)

#change the language in GUI
msg.changeLanguage(lang, REQUEST, REQUEST.RESPONSE)
