## Script (Python) "registration_book_edit"
##parameters=
##bind context=context
##bind script=script

# $Id: registration_book_edit.py,v 1.22 2005/10/06 11:56:48 vsafronovich Exp $
# $Editor: ishabalin $
# $Revision: 1.22 $

REQUEST = context.REQUEST

title = REQUEST.get('title')
context.setTitle (title)
description = REQUEST.get('description')
context.setDescription (description)
category_id = REQUEST.get('category')
context.setRegisteredCategory(category_id)
reg_no_attr = REQUEST.get('reg_no_attr', None)
context.setRegistrationNumberAttributeId(reg_no_attr)
reg_no_rule = REQUEST.get('reg_no_rule', '')
context.setRegistrationNumberTemplate(reg_no_rule)
dept = REQUEST.get('department', '')
context.setDepartment(dept)
papers_folder = REQUEST.get('dest_folder_uid', None)
context.setPapersFolder(papers_folder)

message = 'Changes saved'

for column in context.listColumns():
    column.setTitle(REQUEST.get('title_' + column.getId()))
    if REQUEST.get('delete_columns') and REQUEST.get('del_' + column.getId()):
        context.delColumn(column.getId())
        message = 'Column removed'

if REQUEST.get( 'change_counter' ) == 'change':
    context.setInternalCounter( REQUEST.get('last_id') )

if REQUEST.get('add_attribute_column'):
    attr_id = REQUEST.get('attribute')
    if attr_id:
        category = context.portal_metadata.getCategoryById(category_id)
        attr = category.getAttributeDefinition(attr_id)
        if attr:
            sort_query = {  'sort_on': 'CategoryAttributes',
                            'sort_attr': '%s/%s' % ( category.getId(), attr.getId() ) }
            context.addColumn( id=attr.getId(),
                                title=context.msg( attr.Title() ),
                                type='attribute',
                                argument=attr.getId(),
                                sort_query=sort_query,
                                )

if REQUEST.get('add_meta_column'):
    meta_id = REQUEST.get('meta')
    if meta_id:
        params = context.getMetaColumnParams(meta_id)
 
        context.addColumn( id=meta_id,
                           title=context.msg(meta_id),
                           **params
                           )

hide_registration_date = REQUEST.get('hide_registration_date', 0)
context.setHideRegistrationDate( hide_registration_date )

hide_crator = REQUEST.get('hide_creator', 0)
context.setHideCreator( hide_crator )

hide_version = REQUEST.get('hide_version', 0)
context.setHideVersion( hide_version )

recency_period = REQUEST.get( 'recency_period', 0 )
context.setRecencyPeriod( recency_period )

return apply(   context.registration_book_edit_form, (context, REQUEST),
                script.values(portal_status_message=message))
