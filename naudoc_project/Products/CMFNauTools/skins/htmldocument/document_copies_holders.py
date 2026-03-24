## Script (Python) "document_copies_holders"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST,department=None,number=None,workshop=None,position=None,description=None,id,ids=None
##title=
##
# $Editor: oevsegneev $
# $Id: document_copies_holders.py,v 1.4 2005/05/14 05:43:50 vsafronovich Exp $
# $Revision: 1.4 $

REQUEST = context.REQUEST
RESPONSE = REQUEST.RESPONSE

qst=''

if REQUEST.has_key('delete_holders'):
    if ids:
        context.deleteCopiesHolders(ids)
    else:
        qst='?portal_status_message=Select+one+or+more+users+first'

if REQUEST.has_key('add_holder'):
    context.addCopiesHolder( number = REQUEST.get('new_holder_number'),
                             workshop = REQUEST.get('new_holder_workshop'),
                             department = REQUEST.get('new_holder_department'),
                             position = REQUEST.get('new_holder_position'),
                             description = REQUEST.get('new_holder_description')
                           )

if REQUEST.has_key('save_holders'):
    context.setCopiesHolders(id, number=number, workshop=workshop, department=department, position=position, description=description)

context.REQUEST[ 'RESPONSE' ].redirect( context.absolute_url() + '/document_copies_holders_form'+qst)
