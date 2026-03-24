## Script (Python) "directory_settings_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=root=None, level=None, pattern=None, branch_title_pattern=None, entry_title_pattern=None, title_pattern=None, owner=None
##title=Handler for the directory settings form.
##
# $Editor: vpastukhov $
# $Id: directory_settings_handler.py,v 1.4 2006/03/30 11:14:14 oevsegneev Exp $
# $Revision: 1.4 $

from Products.CMFNauTools.SecureImports import SimpleError

REQUEST = context.REQUEST

action = 'directory_view'
message = ''

try:
    # save settings
    if REQUEST.has_key('save_settings'):

        context.setSoleRoot( root )
        context.setMaxLevel( level )
        context.setCodePattern( pattern or None )
        context.setTitlePattern( branch_title_pattern or None, 1 )
        context.setTitlePattern( entry_title_pattern or None, 0 )
        #context.setOwnerObject( owner )

        message = "Changes saved."

    # abandon changes
    elif REQUEST.has_key('cancel'):

        message = "Action cancelled."

except SimpleError, error:
    error.abort()
    return context.directory_settings_form( context, REQUEST, portal_status_message=error )

return context.redirect( action=action, message=message )
