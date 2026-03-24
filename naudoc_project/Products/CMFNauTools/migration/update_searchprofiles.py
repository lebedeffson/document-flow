"""
$Id: update_searchprofiles.py,v 1.6 2006/12/18 14:13:42 oevsegneev Exp $
$Editor: vsafronovich $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

title = 'Update search profiles'
version = '3.2.0.91'
classes = ['Products.CMFNauTools.SearchProfile.SearchProfile']

from urllib import splitquery

from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Filter import Filter
from OFS.DTMLMethod import DTMLMethod
from types import MethodType

def check( context, object):
    query = object.getQuery()
    return bool(query.viewer_mode or query.viewer)

def migrate( context, object ):
    portal = context.portal
    links = getToolByName( portal, 'portal_links')

    query = object.getQuery()

    id = object.getId()
    container = context.container
    container.manage_delObjects( object.getId() )

    if query.viewer_mode:
        mode = query.viewer_mode
        source = portal
    elif query.viewer:     
        mode = None
        url = splitquery(query.viewer)[0]
        url = url[url.find('/%s/storage/' % portal.getId()):]
        source = portal.unrestrictedTraverse( url, None ) 
        if source is None:
            return
        if isinstance( source, MethodType ):
            source = source.im_self
        if isinstance( source, DTMLMethod ):
            source = source.aq_parent
    else:
        return

    container._setObject( id, Filter( id, object.Title()
                                    , object.getQuery()
                                    , description=object.Description() 
                                    ) )
    del object

    filter = container._getOb(id)
    #print `source`, `filter`, `mode`
    filter.edit(source=source)
         