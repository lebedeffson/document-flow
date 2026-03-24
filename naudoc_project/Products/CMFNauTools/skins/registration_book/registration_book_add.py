## Script (Python) "registration_book_add"
##title=Add Registration Book
##parameters=type_name, id, title, description=None, cat_id=None
##bind script=script
##bind context=context

# $Id: registration_book_add.py,v 1.2 2004/02/10 11:53:35 ishabalin Exp $
# $Editor: ishabalin $
# $Revision: 1.2 $

from Products.CMFNauTools.SecureImports import SimpleError
from Products.CMFNauTools.SecureImports import cookId
from Products.CMFNauTools.SecureImports import refreshClientFrame

REQUEST = context.REQUEST

if not cat_id:
    message = 'Please, select registered category'
    return apply(   context.registration_book_factory_form, (context, REQUEST),
                    script.values(  use_default_values=1,
                                    portal_status_message=message ) )

id = id.strip()
if not id:
    id = cookId(context, title=title)

try:
    context.\
    manage_addProduct['CMFNauTools'].\
    addRegistrationBook(    id=id,
                            title=title,
                            description=description,
                            )

except SimpleError, error:
    error.abort()
    return apply(   context.registration_book_factory_form, (context, REQUEST),
                    script.values(  use_default_values=1,
                                    portal_status_message=error ) )

obj = context[id]

obj.setTitle(title)
if description:
    obj.setDescription(description)
obj.setRegisteredCategory(cat_id)

obj.reindexObject()
refreshClientFrame('workspace')

info = context.portal_types.getTypeInfo(obj)
if not info.immediate_view:
    return context.redirect(    action='folder',
                                frame='inFrame',
                                message="Object created." )

return obj.redirect(action=info.immediate_view)
