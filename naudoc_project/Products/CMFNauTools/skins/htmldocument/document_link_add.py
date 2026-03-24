## Script (Python) "document_link_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=target_uid, relation, target_ver_id=None, batch_length=None, query_id=None
##title=
##
# $Id: document_link_add.py,v 1.6 2006/07/11 09:10:50 oevsegneev Exp $

from Products.CMFNauTools.SecureImports import SimpleError

REQUEST = context.REQUEST

if context.implements('isVersion') or context.implements('isVersionable'):
    source_uid = context.getVersion().getResourceUid()
else:
    source_uid = context.getUid()

try:
    context.portal_links.restrictedLink( source_uid, target_uid, relation, REQUEST=REQUEST )

except SimpleError, error:                                              
    error.abort()
    return apply( context.document_link_form, (context, REQUEST),
                  script.values( portal_status_message=error ) )

return context.redirect( action='document_link_form',
                         message="Link was successfully created." )
