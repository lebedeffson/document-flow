## Script (Python) "category_bases"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=bases=[]
##title=
##
# $Id: category_bases.py,v 1.2 2004/01/16 16:46:22 vpastukhov Exp $
# $Revision: 1.2 $
REQUEST = context.REQUEST

message = ''
if not REQUEST.get('cancel'):
    message = 'You have changed the list of base categories'
    context.setBases(bases)

REQUEST['RESPONSE'].redirect( context.absolute_url(message=message) )
