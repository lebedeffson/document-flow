## Script (Python) "docflow_report_edit"
##parameters=REQUEST, category, include_inherited=0, search_all=0
##bind context=context

# $Id: docflow_report_edit.py,v 1.11 2005/11/27 17:06:11 vsafronovich Exp $
# $Editor: ishabalin $
# $Revision: 1.11 $

title = REQUEST.get('title')
description = REQUEST.get('description')

if title:
    context.setTitle (title)
if description:
    context.setDescription (description)

cat_obj = context.portal_metadata.getCategoryById(category)

context.setSearchableCategory(category, include_inherited, search_all)
message = 'Changes saved'

if REQUEST.get('add_column_attr'):
    attr_id = REQUEST.get('attribute', None)
    if attr_id:
        attr = cat_obj.getAttributeDefinition(attr_id)
        sort_query = {'sort_on': 'CategoryAttributes', 'sort_attr': '%s/%s' % (cat_obj.getId(), attr_id) }
        context.addColumn(  id=attr_id,
                            title=attr.Title(),
                            type='attribute',
                            argument=attr_id,
                            sort_query=sort_query,
                            )
        message = 'Column added'

if REQUEST.get('add_column_state'):
    state_id = REQUEST.get('state', None)
    if state_id:
        state_title = context.portal_workflow.getStateTitle(cat_obj.getWorkflow().getId(), state_id)
        context.addColumn(  id=state_id,
                            title=state_title,
                            type='stateflag',
                            argument=state_id,
                            )
        message = 'Column added'

if REQUEST.get('add_column_meta'):
    meta_id = REQUEST.get('metadata', None)
    if meta_id:
        params = context.getMetaColumnParams(meta_id)

        context.addColumn(  id=meta_id,
                            title=context.msg(meta_id),
                            **params
                            )
        message = 'Column added'

if REQUEST.get('delete_columns'):
    for column in context.listColumns():
        if REQUEST.get('del_' + column.getId()):
            context.delColumn(column.getId())
            message = 'Column removed'

context.reindexObject()
edit_form = context.absolute_url(   action='docflow_report_edit_form',
                                    message=message)
REQUEST['RESPONSE'].redirect(edit_form)
