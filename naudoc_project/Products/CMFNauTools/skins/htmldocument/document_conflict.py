## Script (Python) "document_conflict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=Document conflict processing
##
# $Editor: oevsegneev $
# $Id: document_conflict.py,v 1.4 2005/07/14 12:46:26 vsafronovich Exp $
# $Revision: 1.4 $

REQUEST = context.REQUEST

if REQUEST.get('create_version'):
    major = context.getMaxMajorAndMinorNumbers()[0]
    minor = context.getMaxMajorAndMinorNumbers()[1]
    new_id = 'version_%s.%s' % (major, minor+1)
    text = REQUEST.get('text')
    context.createVersion( REQUEST.get('id'), new_id, title = REQUEST.get('title'), description = REQUEST.get('description'))
    context.getVersion(new_id).makeCurrent()
    context.edit(None, REQUEST.get('text'), '')

if REQUEST.get('save'):
    context.edit(None, REQUEST.get('text'), '')

if REQUEST.get('show'):
    REQUEST.set('show_diff', 1)
    REQUEST.set('diff', context.getChangesFrom(None, REQUEST.get('text')))
    return context.document_conflict_form( context, REQUEST=REQUEST )

return REQUEST.RESPONSE.redirect(
    context.getVersion().absolute_url( redirect=1, action='document_edit_form', frame='inFrame' ),
    status=303 )
