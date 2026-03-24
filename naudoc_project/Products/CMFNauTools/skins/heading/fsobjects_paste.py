## Script (Python) "fsobjects_paste"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Filling metadata for fs objects from clipboard
##
# $Id: fsobjects_paste.py,v 1.11 2004/09/10 15:27:55 vpastukhov Exp $
# $Revision: 1.11 $
# $Editor: kfirsov $

from Products.CMFNauTools.SecureImports import listClipboardObjects
from Products.CMFNauTools.SecureImports import parseDate, refreshClientFrame

REQUEST = context.REQUEST

if REQUEST.has_key('next'):
    obj = context.popObjectFromClipboard(context, REQUEST=REQUEST)
    if obj is not None:
        category = context.portal_metadata.getCategoryById( REQUEST.get('cat_id', 'Document') )
        attrs = context.process_attributes( category=category, pattern='attr/%s', REQUEST=REQUEST )
        obj.setCategoryAttributes( attrs=attrs )

    fsobjects = listClipboardObjects( context, REQUEST=REQUEST, feature='isFSFile' )

    if fsobjects == []:
        refreshClientFrame( 'navTree' )
        message = "Item(s) Pasted"
        return context.redirect( action='folder', message=message )

    current_fsobject_num = REQUEST.SESSION.get('fsob_curr_num')
    REQUEST.SESSION.set('fsob_curr_num', current_fsobject_num+1)
    REQUEST.SESSION.set('fsob_left_num', len(fsobjects))
    REQUEST.SESSION.set('fsobjects', [(ob.getId(), ob.title_or_id()) for ob in fsobjects])
    return context.invoke_factory_form( context, REQUEST=REQUEST, type_name='HTMLDocument', batch_mode=1 )

if REQUEST.has_key('finish'):
    refreshClientFrame( 'navTree' )
    message = "Filling finished"
    return context.redirect( action='folder', message=message )

REQUEST.SESSION.set('fsob_curr_num', 0)
REQUEST.SESSION.set('fsob_left_num', len(listClipboardObjects( context, REQUEST=REQUEST, feature='isFSFile' )))
return context.invoke_factory_form( context, REQUEST=REQUEST, type_name='HTMLDocument', batch_mode=1 )
