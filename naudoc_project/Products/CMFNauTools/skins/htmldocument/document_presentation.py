## Script (Python) "document_presentation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=presentation_level, is_index=None
##title=Handler for the document presentation form.
##
# $Editor: vpastukhov $
# $Id: document_presentation.py,v 1.14 2007/07/19 07:59:14 oevsegneev Exp $
# $Revision: 1.14 $

REQUEST = context.REQUEST

context.setIndexDocument( is_index )

try:    presentation_level = int( presentation_level )
except: presentation_level = 0

context.setPresentationLevel( presentation_level )

REQUEST.RESPONSE.redirect( context.absolute_url( action='view' ), status=303 )
