## Script (Python) "fs_folder_add"
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=id, title, description, folder_path
##title=Add FS Folder
# $Id: fs_folder_add.py,v 1.6 2006/06/22 11:27:16 oevsegneev Exp $
# $Revision: 1.6 $
# $Editor: kfirsov $

from Products.CMFNauTools.SecureImports import cookId, SimpleError
from Products.CMFNauTools.SecureImports import refreshClientFrame

id = cookId(context, id, title=title)

try:
    context.manage_addProduct['CMFNauTools'].addFSFolder( id=id
                                                    , title=title
                                                    , description=description
                                                    , path=folder_path
                                                    )
except SimpleError, err_msg:
    return apply( context.fs_folder_factory_form, (context, context.REQUEST),
                  script.values( use_default_values=1, portal_status_message=err_msg ) )

ob = context[id]

refreshClientFrame('navTree')
refreshClientFrame('workspace')

info = context.portal_types.getTypeInfo( ob )

return ob.redirect( action=info.immediate_view )
