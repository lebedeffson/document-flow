## Script (Python) "reconfig"
##title=Reconfigure Portal
##parameters=
##
# $Id: reconfig.py,v 1.3 2004/04/29 15:39:37 ypetrov Exp $

REQUEST = context.REQUEST
context.portal_properties.editProperties(REQUEST)
context.redirect(action = 'reconfig_form', message = "Portal settings changed")
