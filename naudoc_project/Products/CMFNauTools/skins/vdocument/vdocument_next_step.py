## Script (Python) "vdocument_next_step"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=chief_user=None, comment=''
##title=
# $Editor: ikuleshov $
# $Id: vdocument_next_step.py,v 1.5 2004/04/02 07:35:43 vsafronovich Exp $
# $Revision: 1.5 $
context.parent().nextEntryStep( context.getId(), chief_user=chief_user, comment=comment)

context.redirect( message='Step changed')
