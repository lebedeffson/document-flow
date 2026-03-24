## Script (Python) "metadata_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None,title=None,subject=None,description=None,language=None,category=None,contributors=None,effective_date=None,expiration_date=None,format=None,rights=None
##title=Update Content Metadata
##
# $Editor: vpastukhov $
# $Id: metadata_edit.py,v 1.56 2006/04/27 12:56:24 ikuleshov Exp $
# $Revision: 1.56 $

from Products.CMFNauTools.SecureImports import refreshClientFrame, \
        SimpleError, ResourceLockedError

REQUEST = context.REQUEST

object = context

if object.implements('isTaskItem'):
    object = object.getBase()

if object.implements('isVersion'):
    object = object.getVersionable()

# test for valid id (new)
if id and id != object.getId():
    error = object.parent().checkId( id )
    if error:
        return apply( context.metadata_edit_form, (context, REQUEST),
                      script.values( portal_status_message=str(error) ) )

relative = True

props = {}
for prop in object.listEditableProperties():
    name = 'property/%s' % prop['id']
    if REQUEST.has_key( name ):
        # TODO add support for complex types
        props[ prop['id'] ] = REQUEST[ name ]

try:
    if props:
        object.manage_changeProperties( **props )
    
    if object.implements('isCategorial'):
        if category and object.Category() != category:
            if not context.portal_properties.getConfig('AllowChangeCategory'):
                raise SimpleError( "Changing the object's category is not allowed." )
            object.setCategory( category )

        attrs = context.process_attributes( object=object, pattern='attr/%s', REQUEST=REQUEST )
        if attrs:
            object.setCategoryAttributes( attrs )

    if id and id != object.getId():
        object.parent().manage_renameObject( object.getId(), id )
        relative = False

    def nonEmptyParam( param ):
        if param is not None:
            return param
        else:
            return Missing
        
    if object.implements('Contentish') and \
       context.portal_membership.checkPermission( 'Modify portal content', object ):
        object.editMetadata( title=nonEmptyParam(title)
                           , description=nonEmptyParam(description)
                           , subject=nonEmptyParam(subject)
                           , contributors=nonEmptyParam(contributors)
                           , effective_date=nonEmptyParam(effective_date)
                           , expiration_date=nonEmptyParam(expiration_date)
                           , format=nonEmptyParam(format)
                           , language=nonEmptyParam(language)
                           , rights=nonEmptyParam(rights)
                           )

    if object.implements('isCategoryDefinition') and \
       context.portal_membership.checkPermission( 'Modify portal content', object ):
        object.setTitle(nonEmptyParam(title))
        object.setDescription(nonEmptyParam(description))

except SimpleError, error:
    error.abort()
    return apply( context.metadata_edit_form, (context, REQUEST),
                  script.values( portal_status_message=error ) )

except ResourceLockedError, error:
    error.abort()
    message = "Metadata cannot be changed since the document is locked."

else:
    message = "Metadata changed"

    refreshClientFrame('workspace')

    if context.implements('isDirectory'):
        refreshClientFrame('directory')
    elif context.implements('isPrincipiaFolderish'):
        refreshClientFrame('navTree')

if REQUEST.get( 'change_and_edit', 0 ):
    action_id = 'edit'
elif REQUEST.get( 'change_and_view', 0 ):
    action_id = 'view'
else:
    action_id = 'metadata'

#XXX
if context.implements('isTaskItem'):
    action_path = 'view'
elif object.implements('isPortalContent'):
    action_path = object.getTypeInfo().getActionById( action_id )
else:
    action_path = 'metadata_edit_form'    

return context.redirect(
        action   = action_path,
        message  = message,
        frame    = 'inFrame',
        relative = relative
    )
