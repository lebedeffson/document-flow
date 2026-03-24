## Script (Python) "logout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Logout handler.
##
# $Editor: vpastukhov $
# $Id: logout.py,v 1.3 2004/03/09 16:48:28 vpastukhov Exp $
# $Revision: 1.3 $

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

if REQUEST.has_key( '__ac' ):
    RESPONSE.expireCookie( '__ac', path='/' )
    return RESPONSE.redirect( context.portal_url() + '/logged_out' )

else:
    return context.manage_zmi_logout( REQUEST, RESPONSE )
