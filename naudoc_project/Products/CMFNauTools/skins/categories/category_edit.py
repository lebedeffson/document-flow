## Script (Python) "category_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None
##title=
##
# $Id: category_edit.py,v 1.14 2005/12/07 15:46:48 vsafronovich Exp $
# $Revision: 1.14 $

from Products.CMFNauTools.SecureImports import SimpleRecord, SimpleError

message=''

if REQUEST.has_key('save_changes'):
    try:
        context.setTemplate( REQUEST.get('template_uid'), REQUEST.get('template_version') )
    except SimpleError, error_message:
        error_message.abort()
        return context.main_category_form( context, REQUEST, portal_status_message=error_message )

    message = 'Changes saved'

elif REQUEST.has_key('delete_templates'):
    selected_templates = REQUEST.get('selected_templates')
    if selected_templates:
        context.deleteTemplates( selected_templates)

        message = 'Template(s) deleted'

elif REQUEST.has_key('set_work_template'):
    selected_templates = REQUEST.get('selected_templates')
    if selected_templates:
        context.setWorkTemplate( selected_templates[0])

        message = 'Work template selected'

REQUEST['RESPONSE'].redirect( context.absolute_url(action='main_category_form', message=message))
