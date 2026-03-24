## Script (Python) "registry_options"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Add a report item
# $Editor: kfirsov$
# $Id: registry_options.py,v 1.11 2005/05/14 05:43:52 vsafronovich Exp $
# $Revision: 1.11 $

REQUEST = context.REQUEST
r = REQUEST.get

department = r('department')
reg_num_forming_rule = r('reg_num_forming_rule')
parent_registry = r('parent_registry')
last_id = r('last_id')
author_can_delete_entry = r('author_can_delete_entry')

context.editMetadata( title=r('title', Missing)
                    , description=r('description', Missing)
                    )
context.setRegNumFormingRule( reg_num_forming_rule )
context.setParentRegistry(parent_registry)
context.setInternalCounter( last_id )
context.setDelEntryAuthorAllowed( author_can_delete_entry )
context.setDepartment(department)

if REQUEST is not None:

    message = ''
    if r('add_field'):
        fname = r('fname')
        ftitle = r('ftitle')
        ftype = r('ftype')
        fedit = r('fedit')
        system_field = r('system_field')
        context.addColumn( id = fname
                         , title = ftitle
                         , type = ftype
                         , editable_after_reg = fedit
                         , system_field = system_field
                         )

        message = "Field added"
    elif r('del_fields'):
        ids=r('selected_fields')
        for id in ids:
            context.delColumn(id)


        if ids:
            message = "Field removed"
    else:
        if not context.listColumns():
            message = "You have to specify at least one report field"
        else:
            message = "Changes saved"

    REQUEST[ 'RESPONSE' ].redirect(context.absolute_url(action='registry_options_form', message=message))
