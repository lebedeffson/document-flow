## Script (Python) "set_primary_category"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=primary=None
##title=
##
# $Id: set_primary_category.py,v 1.6 2004/03/23 13:17:06 ishabalin Exp $
# $Editor: ishabalin $
# $Revision: 1.6 $

REQUEST = context.REQUEST

message = ''
if not REQUEST.get('cancel'):
    message = 'You have changed the primary category'
    if not primary:
        context.setPrimaryCategory()
    else:
        context.setPrimaryCategory(primary)

REQUEST['RESPONSE'].redirect( context.absolute_url(message=message) )
