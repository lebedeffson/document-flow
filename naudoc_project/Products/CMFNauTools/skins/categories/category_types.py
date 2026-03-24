## Script (Python) "category_types"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_names=[]
##title=
##
# $Id: category_types.py,v 1.4 2004/03/24 11:40:58 spinagin Exp $
# $Revision: 1.4 $
REQUEST = context.REQUEST

message = ''
if not REQUEST.get('cancel'):
    message = 'You have changed the list of allowed content types'
    context.setAllowedTypes(type_names)

REQUEST['RESPONSE'].redirect( context.absolute_url(message=message) )
