"""
Migration script -- fixes category templates.

$Editor: ishabalin $
$Id: fix_category_templates.py,v 1.11 2004/08/12 13:10:11 vpastukhov Exp $
"""
__version__ = '$Revision: 1.11 $'[11:-2]

title = 'Fix category templates'
version = '3.1.2.47'
classes = [ 'Products.CMFNauTools.CategoryDefinition.CategoryDefinition' ]

from Acquisition import aq_base
from Products.CMFNauTools.Exceptions import SimpleError
from Products.CMFNauTools.Utils import getToolByName, getObjectByUid

def check( context, object ):
    base = aq_base(object)
    return hasattr( base, 'template') or hasattr( base, 'templates' ) # template is old style

def migrate( context, object ):
    links = getToolByName( object, 'portal_links' )

    base = aq_base(object)
    if hasattr( base, 'templates'):
        template_uids = object.templates
        selected_template = object.getProperty('work_template')
    else: # one template
        template_uids = [ object.template ]
        selected_template = object.template

    template_uids = filter( None, template_uids )
    for uid in template_uids:
        tdoc = getObjectByUid( object, uid )
        if tdoc is not None and not links.searchLinks( target=uid, relation='reference' ):
            link = links.createLink( object, tdoc, 'reference' )
            if uid == selected_template:
                object._updateProperty( 'work_template', link.getId() )

    try:
        object._delProperty('templates')
    except SimpleError:
        if hasattr( base, 'template'):
            del base.template
        if hasattr( base, 'templates'):
            del base.templates
