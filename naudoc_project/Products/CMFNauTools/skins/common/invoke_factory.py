## Script (Python) "invoke_factory"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name,id,title=None,subject=None,description=None,type_args=None,cat_id=None,mail_type=None, upload=None, upload_id=None, nomencl_num=None, postfix=None, doc_uid=None, doc_version=None, selected_template=None
##title=Create content
##
# $Editor: vpastukhov $
# $Id: invoke_factory.py,v 1.72 2008/10/15 12:26:55 oevsegneev Exp $
# $Revision: 1.72 $

from Products.CMFNauTools.SecureImports import SimpleError, SentinelError, cookId, refreshClientFrame

REQUEST = context.REQUEST
types = context.portal_types
metadata = context.portal_metadata

if type_args:
    # convert record to dictionary
    type_args = type_args.copy()
else:
    type_args = {}

try:
    type_info = types.getTypeInfo( type_name )
    if type_info is None:
        # XXX getTypeInfo should raise exception on its own
        raise KeyError, type_name
    immediate_view = type_info.immediate_view

    # setup object Id
    id = id.strip()
    if not id:
        id = cookId( context, title=title )

    # prepare general metadata
    type_args['title'] = title
    type_args['description'] = description

    if type_info.typeImplements('hasLanguage'):
        type_args['language'] = context.portal_membership.getLanguage()

    # prepare category parameters
    if type_info.typeImplements('isCategorial'):
        category = metadata.getCategoryById( cat_id )
        if category.disallowManual():
            raise SimpleError( 'categories.category_disallowed', category=category.getId() )

        # document template
        type_args['category'] = cat_id
        if selected_template:
            type_args['category_template'] = selected_template

        # category attributes
        attrs = context.process_attributes( category=category, pattern='attr/%s', REQUEST=REQUEST )
        if attrs:
            type_args['category_attributes'] = attrs

        # primary object
        primary = category.getPrimaryCategory()
        if primary:
            if not doc_uid:
                raise SimpleError( "Select primary document" )
            type_args['category_primary'] = (doc_uid,)

        if type_info.typeImplements('isHTMLDocument') and category.isTempletCreation():
            immediate_view = 'document_view'

    # handle uploaded files
    if upload:
        if type_info.typeImplements('isHTMLDocument'):
            # we want to create document with template text
            upload_params = { 'id':upload_id, 'associate':1 }
            type_args['attachments'] = [ (upload, upload_params) ]
            immediate_view = 'document_view'
        elif type_info.typeImplements('isScript'):
            type_args['file'] = upload

    # now create the object
    context.invokeFactory( type_name, id, **type_args )
    obj = context[ id ]

    links_to = REQUEST.get('links_to', [])
    for link in links_to:
        doc_uid = link.get('uid')
        if doc_uid:
            doc_relation = link['relation']

            if obj.implements('isVersionable'):
                ver_id = obj.getCurrentVersionId()
            else:
                ver_id = None

            context.portal_links.restrictedLink( obj, doc_uid, doc_relation,
                                                 source_ver_id=ver_id )

except SimpleError, error:
    error.abort()
    return apply( context.invoke_factory_form, (context, REQUEST),
                  script.values( use_default_values=1, portal_status_message=error ) )

except SentinelError, error:
    error.abort()
    return apply( context.invoke_factory_form, (context, REQUEST),
                  script.values( use_default_values=1, portal_status_message=error ) )

else:
    refreshClientFrame('workspace')

    if obj.implements('isPrincipiaFolderish'):
        refreshClientFrame('navTree')

    if not immediate_view:
        return context.redirect( action='folder', frame='inFrame', message="Object created." )

    return obj.redirect( action=immediate_view, frame='inFrame' )
