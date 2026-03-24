## Script (Python) "registration_book_migration"
##parameters=registry_uid
##bind context=context
##bind script=script

# $Id: registration_book_migration.py,v 1.2 2004/02/10 11:53:35 ishabalin Exp $
# $Editor: ishabalin $
# $Revision: 1.2 $

REQUEST = context.REQUEST
col2attr = {}
reg = context.portal_catalog.getObjectByUid(registry_uid)

if not reg:
    message = registry_uid
    return apply(   context.registration_book_migration_form, (context, REQUEST),
                    script.values(portal_status_message=message))

for col in reg.listColumns():
    col_id = col.getId()
    attr_id = REQUEST.get('col_%s' % (col_id), None)
    if attr_id:
        col2attr[col_id] = attr_id

skip_mismatches = not not REQUEST.get('skip_mismatches', 1)
cnt = context.migrate(reg, col2attr, skip_mismatches=skip_mismatches)

message = '%d document(s) registered' % (cnt)
return apply(   context.registration_book_view_form, (context, REQUEST),
                script.values(portal_status_message=message))
