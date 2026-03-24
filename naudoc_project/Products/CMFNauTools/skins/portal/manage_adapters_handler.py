## Script (Python) "manage_adapters_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, adapter_id=None, adapter_ids=None, service_id=None, service_ids=None
##title=
##
# $Editor: vpastukhov $
# $Id: manage_adapters_handler.py,v 1.2 2004/02/08 14:01:39 vpastukhov Exp $
# $Revision: 1.2 $

from Products.CMFNauTools.SecureImports import SimpleError

tool = context.portal_connector
message = None

try:
    if REQUEST.has_key('add_adapter'):
        if adapter_id:
            adapter = tool.createAdapter( adapter_id )
            return adapter.redirect( action='edit_adapter_form', message="Adapter added.", REQUEST=REQUEST )
        else:
            message = "Please specify adapter type."

    elif REQUEST.has_key('enable_adapters'):
        for id in adapter_ids:
            tool.activateAdapter( id )
        message = "Adapters have been activated."

    elif REQUEST.has_key('disable_adapters'):
        for id in adapter_ids:
            tool.deactivateAdapter( id )
        message = "Adapters have been deactivated."

    elif REQUEST.has_key('delete_adapters'):
        if adapter_ids:
            tool.deleteObjects( adapter_ids )
            message = "Adapter(s) deleted."
        else:
            message = "Please select one or more adapters."

    elif REQUEST.has_key('save_adapter'):
        context.manage_changeProperties( REQUEST )
        if context.testConnection():
            message = "Adapter has successfully connected."
        else:
            message = "Adapter was unable to connect using new settings."

    elif REQUEST.has_key('add_service'):
        if service_id:
            service = tool.createService( context.getId(), service_id )
            return service.redirect( action='edit_service_form', message="Service added.", REQUEST=REQUEST )
        else:
            message = "Please specify service type."

    elif REQUEST.has_key('delete_services'):
        if service_ids:
            tool.deleteObjects( service_ids )
            message = "Service(s) deleted."
        else:
            message = "Please select one or more services."

    elif REQUEST.has_key('save_service'):
        context.manage_changeProperties( REQUEST )
        message = "Service has been reconfigured."

    elif REQUEST.has_key('cancel'):
        message = "Action cancelled."

except SimpleError, error:
    error.abort()
    return apply( context.manage_adapters_form, (context,),
                  script.values( portal_status_message=error ) )

return tool.redirect( action='manage_adapters_form', message=message, REQUEST=REQUEST )
