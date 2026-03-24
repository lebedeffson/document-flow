## Script (Python) "licensing_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, active_users=[]
##title=Handler for license management form.
##
# $Editor: ikuleshov $
# $Id: licensing_handler.py,v 1.2 2005/12/23 12:40:48 ikuleshov Exp $
# $Revision: 1.2 $
from Products.CMFNauTools.SecureImports import SimpleError

if REQUEST.has_key( 'cancel' ):
    return REQUEST['RESPONSE'].redirect( context.portal_url() )
    
message = ''
tool = context.portal_licensing
try:
    tool.setActiveUsers( active_users )
except SimpleError, error:
    error.abort()
    message = error

return tool.redirect( action='licensing', message=message, REQUEST=REQUEST )
