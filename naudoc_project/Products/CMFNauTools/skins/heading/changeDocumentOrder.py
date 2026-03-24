## Script (Python) "changeDocumentOrder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id, order
##title=Changes viewing order of publications in the folder.
##
# $Editor: vpastukhov $
# $Id: changeDocumentOrder.py,v 1.3 2004/03/09 17:17:07 vpastukhov Exp $
# $Revision: 1.3 $

REQUEST = context.REQUEST

context.shiftDocument(id, order)

qst='?portal_status_message=Folder+changed'

REQUEST.RESPONSE.redirect( context.absolute_url()
                         + '/viewing_order' + qst )
