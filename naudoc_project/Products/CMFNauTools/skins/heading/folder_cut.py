## Script (Python) "folder_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cuts objects from a folder to the clipboard.
##
# $Editor: vpastukhov $
# $Id: folder_cut.py,v 1.5 2004/03/15 12:44:36 ishabalin Exp $
# $Revision: 1.5 $

REQUEST = context.REQUEST

if REQUEST.has_key('ids'):
    try:
        context.manage_cutObjects(REQUEST['ids'], REQUEST)
        return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder?portal_status_message=Item(s)+Cut')
    except:
        return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder?portal_status_message=unauthorized')
else:
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder?portal_status_message=Please+select+one+or+more+items+to+cut+first')
