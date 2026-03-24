## Script (Python) "vdocument_options"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Configure the Business Procedure object
# $Editor: ikuleshov $
# $Id: vdocument_options.py,v 1.22 2005/05/14 05:43:53 vsafronovich Exp $
# $Revision: 1.22 $
from Products.CMFNauTools.SecureImports import SimpleError

REQUEST = context.REQUEST
r = REQUEST.form.get
h = REQUEST.form.has_key
message = ""

if h('apply'):
    context.editMetadata( title=r('title','')
                        , description=r('description','')
                        )

elif h('add_column'):
    column_id = r('column_id')
    column_title = r('column_title')
    column_type = r('column_type')

    if column_title:
        kwargs = {}
        if column_type == 'lines':
            kwargs['options'] = REQUEST.get('value_list',[])

        try:
            context.addColumn( id = column_id
                             , title = column_title
                             , type = column_type
                             , **kwargs
                             )
        except SimpleError, error:
            error.abort()
            return apply( context.vdocument_options_form, (context, REQUEST),
                          script.values( use_default_values=1, portal_status_message= str(error) ) )


        message = "Column added"

elif h('del_columns'):
    ids=r('selected_columns', [])
    if ids:
        for id in ids:
            context.delColumn(id)
        message = "Column removed"
    else:
        message = "Please select at least one column"

elif h('set_key_columns'):
    ids=r('selected_columns',[])
    for id in ids:
        context.setKeyColumn(id)
    message = "Key columns list changed"

elif h('reset_key_columns'):
    ids=r('selected_columns',[])
    for id in ids:
        context.resetKeyColumn(id)
    message = "Key columns list changed"

elif h('add_step'):
    step_title = r('step_title')
    if step_title:
        context.addStep(step_title)
        message = "Step added"
    else:
        message = "Please specify the step title"
elif h('delete.x'):
    if r('deletefile'):
        context.removeFile(r('deletefile'))
        message = 'Attached file has been removed'

elif h('add_attach') and r('attach'):
    fileid = context.addDocTemplate( r('attach') )
    message = 'File has been attached'

steps_count = len( context.listStepValues() )

for step_id in range(1, steps_count + 1):
    if h('modify_step_%d' % step_id):
        return context.vdocument_modifystep_form(context, REQUEST, step_id = step_id)

    elif h('delete_step_%d' % step_id):
        context.delStep(step_id)
        message = "Step removed"

    elif h('moveup_step_%d' % step_id):
        context.moveStepUp(step_id)
        message = "Step moved up to the queue"

    elif h('movedown_step_%d' % step_id):
        context.moveStepDown(step_id)
        message = "Step moved down to the queue"

if not steps_count:
    message = "Document must contain at least one step"

if message:
    return context.redirect( action='vdocument_options_form', message=message)

if not context.listColumns():
    message = "You have to specify at least one column"
else:
    message = "Changes saved"
return context.redirect( action='vdocument_options_form', message=message)
