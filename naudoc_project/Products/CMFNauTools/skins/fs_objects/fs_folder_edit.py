## Script (Python) "fs_folder_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Edit a filefolder
##
# $Id: fs_folder_edit.py,v 1.7 2004/04/02 09:19:50 vsafronovich Exp $
# $Revision: 1.7 $
# $Editor: kfirsov $

from Products.CMFNauTools.SecureImports import refreshClientFrame, SimpleError

REQUEST=context.REQUEST
try:
    if REQUEST.has_key('folder_path'):
        context.setPath( REQUEST.get('folder_path') )
    context.edit(REQUEST.title, REQUEST.description)
except SimpleError, err_msg:
    return context.redirect( action='fs_folder_edit_form', message=err_msg )

refreshClientFrame('workspace')
refreshClientFrame('navTree')

info = context.portal_types.getTypeInfo( context )

return context.redirect( action=info.immediate_view )
