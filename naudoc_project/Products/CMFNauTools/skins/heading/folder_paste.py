## Script (Python) "folder_paste"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Pastes objects to a folder from the clipboard.
##
# $Editor: vpastukhov $
# $Id: folder_paste.py,v 1.9 2004/05/24 13:27:32 ikuleshov Exp $
# $Revision: 1.9 $

from Products.CMFNauTools.SecureImports import refreshClientFrame, CopyError, formatErrorValue
from Products.CMFNauTools.SecureImports import listClipboardObjects

REQUEST=context.REQUEST

if REQUEST.has_key('proceed'):
    return context.fsobjects_paste()

if REQUEST.has_key('default_paste'):
    context.manage_pasteObjects( REQUEST=REQUEST )
    refreshClientFrame( 'navTree' )
    message = "Item(s) Pasted"
    return context.redirect( action='folder', message=message )


if context.cb_dataValid():
    try:
        cp_objects = listClipboardObjects( context, REQUEST = REQUEST, feature='isFSFile' )
        if cp_objects != []:
            REQUEST.SESSION.set('fsobjects', [(ob.getId(), ob.title_or_id()) for ob in cp_objects])
            return context.fsobjects_paste_form( context, REQUEST=REQUEST )
        else:
            context.manage_pasteObjects( REQUEST=REQUEST )
    except CopyError, message:
        return context.redirect( action='folder', message=formatErrorValue( CopyError, message ) )

    refreshClientFrame( 'navTree' )
    message = "Item(s) Pasted"

else:
    message = "Copy or cut one or more items to paste first"

return context.redirect( action='folder', message=message )
