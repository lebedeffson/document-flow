"""
$Id: update_discussionitems.py,v 1.6 2004/11/10 14:11:14 ikuleshov Exp $
$Editor: vsafronovich $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

title = 'Update discussion items'
version = '3.1.5.16'
before_script = 1
order = 50 # Must be run before setup_categories_phase1

from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.DiscussionItem import \
        DiscussionItemContainer, DiscussionItem

def migrate( context, object ):
    catalog = getToolByName( context.portal, 'portal_catalog' )
    results = catalog.searchResults( meta_type='Discussion Item' )
    for r in results:
        item = r.getObject()
        if item is None:
            continue

        id = item.getId()
        container = aq_parent( item )

        if not isinstance( container, DiscussionItemContainer ):
            document = container._getDiscussable(1)
            container = document._upgrade( container.getId(), DiscussionItemContainer )
            container = container.__of__( document )

        container._upgrade( id, DiscussionItem, container=container._container )

        item = container.getReply( id )
        if not item.Title():
            item.setTitle( item.Description() )
        item.reindexObject( idxs=['implements'] )
        context.markForReindex( item )
