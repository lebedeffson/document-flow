## Script (Python) "switch_member"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=old_member=None, new_member=None, switch_opened=None
##title=Action to change ownership
##
# $Editor: oevsegneev $
# $Id: switch_member.py,v 1.1 2009/02/17 15:04:22 oevsegneev Exp $

if not ( new_member and old_member ):
    return context.switch_member_form( context,
                                       context.REQUEST,
                                       portal_status_message='Please specify members to switch')

context.portal_membership.switchMember( old_member, new_member, switch_opened )

return context.switch_member_form( context,
                                   context.REQUEST,
                                   portal_status_message='Member switched')
