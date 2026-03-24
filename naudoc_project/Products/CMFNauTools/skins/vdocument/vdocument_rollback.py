## Script (Python) "vdocument_rollback_step"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=rollback_step=None, chief_user=None, comment=''
##title=
# $Editor: ikuleshov $
# $Id: vdocument_rollback.py,v 1.6 2004/04/02 07:35:43 vsafronovich Exp $
# $Revision: 1.6 $
context.parent().entryRollback( context.getId(), rollback_step=rollback_step, chief_user=chief_user, comment=comment)

context.redirect( message='Step changed' )
