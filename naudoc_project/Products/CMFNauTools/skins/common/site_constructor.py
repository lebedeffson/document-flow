## Script (Python) "site_constructor"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id, repository_url, skin_id, title='', skin_links=[], storage_id='storage', sync_addr='', sync_path=''
##title=
##
# $Editor: vpastukhov $
# $Id: site_constructor.py,v 1.18 2005/05/14 05:43:50 vsafronovich Exp $
# $Revision: 1.18 $

from Products.CMFNauTools.SecureImports import cookId, SimpleError, refreshClientFrame

site_id = cookId( context, id, title=title, prefix='site' )

try:
    site_id = context.manage_addProduct['CMFNauTools'].manage_addSiteContainer(
         id              = site_id,
         title           = title,
         skin_links      = skin_links,
         storage_id      = storage_id,
         repository_url  = repository_url,
         sync_addr       = sync_addr,
         sync_path       = sync_path,
         skin_id         = skin_id,
         )
except SimpleError, error:
    error.abort()
    return apply( context.site_constructor_form, (context, context.REQUEST),
                  script.values( use_default_values=1, portal_status_message=str(error) ) )


refreshClientFrame( 'navTree' )
refreshClientFrame( 'workspace' )

return context[ site_id ].redirect( action='folder_contents', message="Site added" )
