## Script (Python) "manage_unlockUsers"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userids=None
##title=
##
# $Editor: oevsegneev $
# $Id: manage_unlockUsers.py,v 1.4 2005/05/14 05:43:50 vsafronovich Exp $
# $Revision: 1.4 $

request = container.REQUEST
RESPONSE =  request.RESPONSE
if userids:
    for userid in userids:
        user = context.portal_membership.getMemberById(userid)
        roles = []
        for r in user.getRoles():
            if r != 'Locked':
                roles.append(r)
        user.setSecurityProfile( roles=list(roles) )
    qst='?portal_status_message=User(s)+unlocked'
else:
    qst='?portal_status_message=Select+one+or+more+users+first'

context.REQUEST[ 'RESPONSE' ].redirect( context.absolute_url() + '/manage_users_form'+qst)
