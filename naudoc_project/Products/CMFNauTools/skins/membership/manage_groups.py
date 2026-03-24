## Script (Python) "manage_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Handler for groups management form.
##
# $Editor: vpastukhov $
# $Id: manage_groups.py,v 1.2 2004/03/09 14:53:54 vpastukhov Exp $
# $Revision: 1.2 $

REQUEST = context.REQUEST

if REQUEST.get('addGroup', None) and not REQUEST.get('group', None):
    REQUEST.RESPONSE.redirect( context.absolute_url() + '/manage_groups_form')
else:
    context.portal_membership.manage_groups(REQUEST)
