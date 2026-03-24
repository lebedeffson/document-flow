## Script (Python) "manage_delUsers"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userids=None
##title=Handler for portal users deletion.
##
# $Editor: vpastukhov $
# $Id: manage_delUsers.py,v 1.7 2005/05/14 05:43:50 vsafronovich Exp $
# $Revision: 1.7 $

REQUEST = container.REQUEST

if userids:
    context.portal_membership.deleteMembers( userids )
    qst='?portal_status_message=User(s)+deleted'
else:
    qst='?portal_status_message=Select+one+or+more+users+first'

REQUEST.RESPONSE.redirect( context.absolute_url() + '/manage_users_form'+qst )
