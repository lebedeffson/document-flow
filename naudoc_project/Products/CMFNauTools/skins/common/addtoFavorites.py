## Script (Python) "addtoFavorites"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Add item to favourites
##parameters=
# $Editor: ikuleshov $
# $Id: addtoFavorites.py,v 1.24 2004/06/11 12:12:38 vpastukhov Exp $
# $Revision: 1.24 $

from Products.CMFNauTools.SecureImports import refreshClientFrame

favorites = context.portal_membership.getPersonalFolder( 'favorites', create=1 )

# find shorcut links to the current object
links = context.portal_links.searchLinks( target=context, relation='shortcut' )
ver_id = context.implements('isVersion') and context.getId() or None
uids  = [ str( link['source_uid'] ) for link in links ]

# find shorcut objects in favorites referencing the current object
uids = uids or [''] # XXX catalog ignores empty list (fixed in Zope 2.6.4)
results = context.portal_catalog.searchResults( path=favorites.physical_path(),
                                                nd_uid=uids, implements='isShortcut' )

if results:
    message = "Shortcut to this object already exists in the Favorites."

else:
    # TODO auto-generate title with optional number suffix
    favorites.manage_addProduct['CMFNauTools'].addShortcut( None, context )
    refreshClientFrame('favorites')
    message = "Object has been added to the Favorites."

parent_or_self = context.implements( 'isVersion' ) and context.getVersionable() or context
type_info = parent_or_self.getTypeInfo()

action_path = type_info.getActionById( 'view', 'edit' )
if action_path == 'edit':
    action_path = type_info.getActionById( 'edit' )

return context.redirect(
        action   = action_path,
        message  = message,
    )
