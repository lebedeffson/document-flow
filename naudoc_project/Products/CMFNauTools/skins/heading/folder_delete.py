## Script (Python) "folder_delete"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None
##title=Deletes objects from a folder.
##
# $Editor: vpastukhov $
# $Id: folder_delete.py,v 1.11 2004/03/09 17:17:07 vpastukhov Exp $
# $Revision: 1.11 $

from Products.CMFNauTools.SecureImports import refreshClientFrame

params = {}

if ids:
    ndeleted = context.deleteObjects( ids )

    if ndeleted:
        # TODO only refresh tree if some folderish object was deleted
        refreshClientFrame( 'navTree' )
        # XXX is workspace really needs to be refreshed from here?
        refreshClientFrame( 'workspace' )

    if not ndeleted:
        message = 'Object(s) were not deleted. Either you have no permission to delete them or they are locked.'
    elif ndeleted < len(ids):
        message = '%(count)d object(s) were not deleted. Either you have no permission to delete them or they are locked.'
        params['count:int'] = len(ids) - ndeleted
    else:
        message = 'Deleted.'

else:
    message = 'Please select one or more items first.'

return context.redirect( action='folder', message=message, params=params )
