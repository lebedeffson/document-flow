## Script (Python) "change_ownership"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid
##title=Action to change ownership
##
# $Id: change_ownership.py,v 1.6 2004/05/27 13:20:08 ikuleshov Exp $

# do not change permission on version
object = context
while object.implements('isVersion'):
    object = object.getVersionable()
object.changeOwnership( userid, explicit=1 )

while not context.portal_membership.checkPermission('View', object):
    object = object.aq_parent

context.REQUEST['RESPONSE'].redirect( object.absolute_url( message="Owner changed" ) )
