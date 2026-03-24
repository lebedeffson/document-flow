"""
$Id: delete_extrime_dates.py,v 1.6 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: vsafronovich $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

title = 'Delete extrime dates'
version = '3.4.0.0'
before_script = 1
order = 50 # Must be run before setup_catalog

#version = '3.2.0.189'

from Acquisition import aq_base
from OFS.Uninstalled import BrokenClass

from Products.CMFCore.utils import getToolByName

from Products.CMFNauTools.SimpleObjects import ContentBase

def migrate( context, object ):
    catalog = getToolByName( context.portal, 'portal_catalog' )

    list = [ ( 'expires'     
             , ContentBase._DefaultDublinCoreImpl__CEILING_DATE
             , 'expiration_date'
             , min
             )
           , ( 'effective'
             , ContentBase._DefaultDublinCoreImpl__FLOOR_DATE
             , 'effective_date'
             , max
             )
           ]

    for index, extrime_value, arg, fun in list:
        query = { index: { 'query': extrime_value
                         , 'range': 'range:%s'%fun.__name__
                         }
                # now search on task and discussion items too
                #, 'implements':'isPortalContent' # this exclude TaskItems
                }
        results = catalog.searchResults( **query )
        for r in results:
            try:
                item = r.getObject()
            except:
                continue

            if item is None:
                continue

            if isinstance(item, BrokenClass):
                context.fixBrokenState(item)

            base = aq_base(item)
            attr = getattr( base, arg, None)
            if attr is not None and fun(attr, extrime_value) == extrime_value :
                # clear arg value
                setattr( base, arg, None )
