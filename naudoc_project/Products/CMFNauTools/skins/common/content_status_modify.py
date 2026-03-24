## Script (Python) "content_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None, transition=None, comment=''
##title=Modify the status of a content object
##
# $Editor: vpastukhov $
# $Id: content_status_modify.py,v 1.27 2007/11/08 14:50:03 oevsegneev Exp $
# $Revision: 1.27 $

from Products.CMFNauTools.SecureImports import SimpleError, refreshClientFrame

# if we are in context of version get first not version object
object = context
while object.implements('isVersion'):
    object = object.getVersionable()

try:
    # invoke workflow action
    res = context.portal_workflow.doActionFor( object, transition, comment=comment )

except SimpleError, error:
    error.abort()
    return context.change_state(context, REQUEST,
                                **script.values( portal_status_message=error, comment=comment ) )
                                # XXX why comment is passed here?

try:
    object = res['ObjectMoved']
except:
    pass

refreshClientFrame( 'workspace' )

if object.implements('isVersionable'):
    # for redirect into current version
    object = object.getVersion()

object.redirect( relative=False, action='view', message="State changed" )
