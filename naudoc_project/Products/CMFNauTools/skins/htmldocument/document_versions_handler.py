## Script (Python) "document_versions_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=Handle document versions
##
# $Id: document_versions_handler.py,v 1.2 2004/01/16 16:46:24 vpastukhov Exp $
# $Revision: 1.2 $

if REQUEST.get('create_version'):
    return context.version_create_form( context, REQUEST )

elif REQUEST.get('compare_versions'):

    original = context.getVersion( REQUEST['ver_id_for_compare'] )
    revised  = context.getVersion( REQUEST['ver_id'] )
    result   = revised.getChangesFrom( original )

    return context.document_compare_results( context, REQUEST, \
                    result=result, original=original, revised=revised )

return context.redirect( action='document_versions_form' )
