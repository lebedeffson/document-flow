## Script (Python) "shortcut_add"
##title=Add item to favourites
##parameters=shortcut_id, shortcut_title, description, remote_uid, remote_version=None
# $Id: shortcut_add.py,v 1.2 2004/03/16 14:06:21 ishabalin Exp $
# $Revision: 1.2 $
from Products.CMFNauTools.SecureImports import cookId

shortcut_id = cookId(context, shortcut_id)
context.manage_addProduct['CMFNauTools'].addShortcut( id=shortcut_id
                                                    , title=shortcut_title
                                                    , description=description
                                                    , remote=remote_uid
                                                    , remote_version=remote_version
                                                    )

return context.REQUEST['RESPONSE'].redirect(context.absolute_url(), status=303)
