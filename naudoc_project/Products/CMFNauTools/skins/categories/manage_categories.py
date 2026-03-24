## Script (Python) "mamage_categories"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Change allowed subjects for the given content type
##
# $Id: manage_categories.py,v 1.8 2006/04/10 10:07:33 oevsegneev Exp $
# $Revision: 1.8 $

from Products.CMFNauTools.SecureImports import DuplicateIdError

REQUEST = context.REQUEST
message = ''

if REQUEST.has_key('addCategory'):
    #Adding new category
    category_id = REQUEST['category_id']
    category_title = REQUEST['category_title']

    try:
        context.portal_metadata.addCategory(cat_id=category_id, title=category_title)
    except DuplicateIdError, error:
        return apply( context.manage_categories_form, (context, REQUEST),
                   script.values( use_default_values=1, portal_status_message=str(error) ) )

if REQUEST.has_key('deleteCategories'):
    #Deleting categories
    selected_categories = REQUEST.get('selected_categories')
    if selected_categories:
        errors = context.portal_metadata.deleteCategories(selected_categories)
        if errors['docs']:
            message = 'Documents of some categories is still exists.'
        if errors['deps']:
            message = message + ' Some categories has dependent ones.'
        

if REQUEST.has_key('exportAsXML'):
    try:
        return context.portal_metadata.exportAsXML(REQUEST)
    finally:
        setHeader = REQUEST.RESPONSE.setHeader
        setHeader("Content-type", "text/xml");
        setHeader("Content-Disposition", "attachment; filename=categories.xml");
        setHeader("Cache-Control", "must-revalidate, post-check=0, pre-check=0");
        setHeader("Pragma", "no-cache");
        setHeader("Expires", "0");

return context.redirect( action='manage_categories_form', message=message )
