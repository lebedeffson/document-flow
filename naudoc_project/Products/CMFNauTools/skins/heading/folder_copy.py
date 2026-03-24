## Script (Python) "folder_copy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Copies object from a folder to the clipboard.
##
# $Editor: vpastukhov $
# $Id: folder_copy.py,v 1.4 2005/05/14 05:43:51 vsafronovich Exp $
# $Revision: 1.4 $

REQUEST = context.REQUEST

if REQUEST.has_key('ids'):
    context.manage_copyObjects(REQUEST['ids'], REQUEST, REQUEST.RESPONSE)
    return context.redirect(REQUEST=REQUEST, action='folder', message='Item(s) Copied')
else:
    return context.redirect(REQUEST=REQUEST, action='folder', message='Please select one or more items to copy first')
