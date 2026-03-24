## Script (Python) "registry_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, record_id, comment=''
##title=Edit entry
# $Editor: kfirsov$
# $Id: registry_edit.py,v 1.2 2004/03/17 06:59:37 vsafronovich Exp $
# $Revision: 1.2 $

context.editEntry(record_id, REQUEST=REQUEST, comment=comment, redirect=0)

message = "Entry changed"
context.redirect( message=message )
