## Script (Python) "dtml_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, title='', data=' '
##title=Edit a document
##
# $Editor: $
# $Id: dtml_edit.py,v 1.6 2004/06/05 11:49:50 vsafronovich Exp $
# $Revision: 1.6 $

REQUEST = context.REQUEST

context.edit(title, data)

message = 'Document saved.'
context.redirect( action='dtml_edit_form', message=message)
