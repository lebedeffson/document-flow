## Script (Python) "category_metadata"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None, type=None, multiple=None, title=None, properties=None, default=None, mandatory=None, read_only=None, ids=None
##title=Handler for category attributes management forms
##
# $Id: category_metadata.py,v 1.30 2004/09/10 14:30:28 vpastukhov Exp $
# $Revision: 1.30 $

from Products.CMFNauTools.SecureImports import SimpleError, cookId

REQUEST = context.REQUEST
message = ''

try:
    if REQUEST.has_key('add'):
        # add new category attribute

        id = id.strip()
        if not id:
            id = cookId( context.attributes, title=title )

        context.addAttributeDefinition( id, type,
                                        title, default,
                                        multiple=(multiple or False),
                                        mandatory=(mandatory or False),
                                        read_only=(read_only or False),
                                        properties=properties,
                                      )

    elif REQUEST.has_key('delete'):
        # delete selected attributes

        if ids:
            context.deleteAttributeDefinitions( ids )
        else:
            message = "Select one or more fields first"

    elif REQUEST.has_key('save'):
        # save attribute properties and default value

        attr = context.getAttributeDefinition( id )
        if not attr.isInCategory( context ):
            raise ValueError, id

        attr.setTitle( title )
        attr.setProperties( properties or {} )
        attr.setDefaultValue( default )

        if mandatory is not None:
            attr.setMandatory( mandatory )
        if read_only is not None:
            attr.setReadOnly( read_only )

        message = "Changes saved."

    elif REQUEST.has_key('add_form'):
        # invoke attribute construction form

        return context.category_attr_edit( context, REQUEST, construction=True )

    elif REQUEST.has_key('cancel'):
        # cancel current form

        message = "Action cancelled."

except SimpleError, error:
    error.abort()
    return context.category_metadata_form( context, REQUEST, portal_status_message=error )

return context.redirect( action='category_metadata_form', message=message )
