## Script (Python) "directory_columns_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=names=None, name=None, type=None, title=None, usage=None, unique=None, disable=None, properties=None
##title=Handler for the directory columns configuration form.
##
# $Editor: vpastukhov $
# $Id: directory_columns_handler.py,v 1.3 2004/10/28 23:16:41 vpastukhov Exp $
# $Revision: 1.3 $

from Products.CMFNauTools.SecureImports import SimpleError, SimpleRecord, cookId

REQUEST = context.REQUEST

action = 'directory_columns_form'
message = ''
mandatory_error_message = 'Mandatory fields can`t be empty'

null_values = [ None, '' , [] ]
scope_codes = [ 'none', 'parent', 'owner', 'directory' ]

try:
    # add new directory column
    if REQUEST.has_key('add_column'):

        name = name.strip()
        if not name:
            name = cookId( context.columns, prefix='col' )

        if not type:
            raise SimpleError( "Attribute type must be specified." )

        column = context.addColumn( name, type )
        column.setTitle( title or name )

        if properties:
            column.setProperties( properties )

        if usage == 'entries':
            column.setUsage( entries=True )
        elif usage == 'branches':
            column.setUsage( branches=True )

        column.setUnique( scope_codes.index( unique or 'none' ) )
        column.disableInput( disable or False )

    # delete columns
    elif REQUEST.has_key('delete_columns'):

        if names:
            for name in names:
                context.deleteColumn( name )
        else:
            message = "Please select one or more attributes first."

    # save columns settings
    elif REQUEST.has_key('save_columns'):

        columns = {}
        for key, data in REQUEST.form.items():
            if key.startswith('col/'):
                columns[ key[4:] ] = SimpleRecord( data )

        for name, record in columns.items():
            if name == 'title__':
                column = context.getTitleColumn()
                name = name[:-2]
            elif name == 'code__':
                column = context.getCodeColumn()
                name = name[:-2]
            else:
                column = context.getColumn( name )

            if column.isImmutable():
                continue

            if not column.isReserved():
                if record.usage == 'all':
                    column.setUsage( entries=True, branches=True )
                elif record.usage == 'entries':
                    column.setUsage( entries=True )
                elif record.usage == 'branches':
                    column.setUsage( branches=True )

            column.setTitle( record.title or name )
            column.setUnique( scope_codes.index( record.unique or 'none' ) )
            column.disableInput( record.disable or False )

        message = "Changes saved."

    # abandon changes
    elif REQUEST.has_key('cancel'):

        action = 'directory_view'
        message = "Action cancelled."

    # return to the entries list
    elif REQUEST.has_key('back'):

        action = 'directory_view'

except SimpleError, error:
    error.abort()
    return context.directory_columns_form( context, REQUEST, portal_status_message=error )

return context.redirect( action=action, message=message )
