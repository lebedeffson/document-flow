## Script (Python) "publish_items"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids, comment=None
##title=Handler for batch document publishing form.
##
# $Editor: vpastukhov $
# $Id: publish_items.py,v 1.8 2004/03/09 17:17:07 vpastukhov Exp $
# $Revision: 1.8 $

workflow = context.portal_workflow
category = context.portal_metadata.getCategoryById( 'Publication' )

for id in ids:
    try:
        item = context[ id ]
    except KeyError:
        continue

    # skip unpublishable objects
    if not ( item.implements('isCategorial') and \
             category.isTypeAllowed( item.getPortalTypeName() ) ):
        continue

# XXX Eventually repair this.
#
#    # set publication category if necessary
#    if not item.isInCategory( 'Publication' ):
#        item.setCategory( 'Publication' )

    if workflow.getStateFor( item, category='Publication' ) == 'published':
        continue

    # invoke workflow action
    workflow.doActionFor( item, 'publish', comment=comment )

return context.redirect( action='folder', message="Items have been published." )
