## Script (Python) "document_signatures"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, s_action, sign_cont, include_attaches=None
##title=
##
# $Editor: oevsegneev $
# $Id: document_signatures.py,v 1.1.1.1 2007/03/23 13:46:13 oevsegneev Exp $
# $Revision: 1.1.1.1 $

REQUEST = context.REQUEST
RESPONSE = REQUEST.RESPONSE

qst=''


if s_action == 'sign':
    if context.addSignature( sign_cont, include_attaches ):
        qst='?portal_status_message=Sign+added+successfully'
    else:
        qst='?portal_status_message=An+error+occured_while_signing'

context.REQUEST[ 'RESPONSE' ].redirect( context.absolute_url() + '/document_signatures_form'+qst)
