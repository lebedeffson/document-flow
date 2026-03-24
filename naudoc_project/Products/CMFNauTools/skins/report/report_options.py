## Script (Python) "report_options"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=manage report options
# $Editor: ikuleshov$
# $Id: report_options.py,v 1.14 2005/05/14 05:43:52 vsafronovich Exp $
# $Revision: 1.14 $
from Products.CMFNauTools.SecureImports import SimpleError

REQUEST = context.REQUEST
r = REQUEST.form.get
h = REQUEST.form.has_key

if h('apply_changes'):
    context.setAllowedUsers( r('allowed_members',[]), r('allowed_groups',[]) )
    if not context.listColumns():
        message = "You have to specify at least one report field"
    else:
        message = "Changes saved"
elif h('add_field'):

    fname = r('fname')
    ftitle = r('ftitle')
    ftype = r('ftype')

    kwargs = {}
    if ftype == 'lines':
        kwargs['options'] = REQUEST.get('value_list',[])

    try:
        context.addColumn( id = fname
                         , title = ftitle
                         , type = ftype
                         , **kwargs)
    except SimpleError, error:
        error.abort()
        return apply( context.report_options_form, (context, REQUEST),
                      script.values( use_default_values=1, portal_status_message= str(error) ) )

    message = "Field added"

elif h('del_fields'):
    ids=r('selected_fields',[])
    if ids:
        for id in ids:
            context.delColumn(id)
        message = "Field removed"
    else:
        message = "Please select at least one column"

return context.redirect( action='report_options_form',
                         message=message)
