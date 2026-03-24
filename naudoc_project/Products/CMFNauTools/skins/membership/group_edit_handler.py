## Script (Python) "group_edit_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Handler for group edit form.
##
# $Editor: vpastukhov $
# $Id: group_edit_handler.py,v 1.1 2004/03/09 14:43:01 vpastukhov Exp $
# $Revision: 1.1 $

context.portal_membership.manage_changeGroup( REQUEST=context.REQUEST )
