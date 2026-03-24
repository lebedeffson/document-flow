## Script (Python) "script_metadata_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Change allowed parameters for the given script object
##
# $Id: script_metadata_edit.py,v 1.11 2005/12/04 14:16:25 vsafronovich Exp $
# $Editor: mbernatski $
# $Revision: 1.11 $
from Products.CMFNauTools.SecureImports import parseDate, updateLink

REQUEST = context.REQUEST
r = REQUEST.get

message = ''

action_path = context.getTypeInfo().getActionById( 'metadata' )

if REQUEST.has_key('addField'):
    #Add new parameter
    typ = r('fType')
    val = 'value_' + typ
    if typ == 'date':
        value = parseDate( 'value', REQUEST, default=None )
    elif typ == 'link':
        value = updateLink( context, 'property', r('id'), value=r(val,'') )
    else:
        value = REQUEST.get(val,'')

    context.addParameter( r('id'),
                          r('fType'),
                          r('title'),
                          value,
                        )
    message = 'Parameter added'
    action_path = 'script_parameters_form'

if REQUEST.has_key('deleteField'):
    #Delete parameters
    action_path = 'script_parameters_form'
    if REQUEST.has_key('fields'):
        context.deleteParameters(r('fields'))
        message = 'Parameter(s) deleted'
    else:
        message = 'Select one or more parameters first'
        return REQUEST['RESPONSE'].redirect(
                  context.absolute_url( action=action_path
                                      , message=message
                                      ))

if REQUEST.has_key('saveValues'):
    #Saving default values and title for parameters
    for param in context.listParameters():
        cid = param['id']
        title = r('title_%s' % cid)
        typ = param['data_type']
        if typ == 'date':
            value = parseDate('default_%s' % cid, REQUEST, default=None )
            if value:
                value = str(value)
        elif typ == 'lines':
            value = list(r('default_%s' % cid))
            if len(value) == 1 and not len(value[0]):
                # empty textarea gets parsed by Zope into
                # a single-element list containing an empty string
                value.pop(0)
        elif typ == 'link':
            val = r('default_%s' % cid , None )
            value = updateLink( context, 'property', cid, value=val )
        else:
            value = r('default_%s' % cid)
        context.editParameter(cid, title, value)

    message = 'Changes saved'
    action_path = 'script_parameters_form'

if REQUEST.has_key('saveTypes'):
    #Saving id, title, object types and supported namespace types of the script
    namespace_type = REQUEST.get('namespace_type', None)
    if namespace_type:
        context.setNamespaceFactory(namespace_type)

    type_names = REQUEST.get('type_names', None)
    if type_names:
        context.setAllowedTypes(type_names)

    if REQUEST.has_key('result_type'):
        context.setResultType( REQUEST['result_type'] or None )

    old_id = context.getId()
    id = REQUEST.get('id', None)
    if id and id != old_id:
        error = context.aq_parent.checkId( id )
        if error:
            return apply( context.script_metadata_edit_form, (context,),
                          script.values( portal_status_message=str(error),REQUEST=REQUEST ) )
        context.aq_parent.manage_renameObjects([old_id,], [id,])
    title = REQUEST.get('title', None)
    if title:
        context.edit(title=title)
    message = 'Changes saved'

return context.redirect(
        action   = action_path,
        message  = message,
        frame    = 'inFrame',
    )
