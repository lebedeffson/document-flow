## Script (Python) "vdocument_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Edit entry
# $Editor: ikuleshov $
# $Id: vdocument_edit.py,v 1.8 2004/05/17 06:47:54 vsafronovich Exp $
# $Revision: 1.8 $
REQUEST = context.REQUEST
r = REQUEST.get

comment = r('comment','')
context.parent().editEntry( context.getId(), REQUEST=REQUEST, comment=comment, redirect=0)

message = ''
if r('next_step'):
    return context.vdocument_next_step_form(context, REQUEST)
elif r('rollback'):
    return context.vdocument_rollback_form1(context, REQUEST)
elif r('abandon'):
    return context.parent().abandonEntry( context.getId(), comment, REQUEST)
elif r('save'):
    message = "Entry changed"

context.parent().redirect( message=message )
