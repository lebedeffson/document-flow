"""
$Id: update_categories.py,v 1.4 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: mbernatski $
"""
__version__ = '$Revision: 1.4 $'[11:-2]

title = 'Update the portal categories'
version = '3.4.0.0'
before_script = 1
order = 45

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from ZODB.PersistentList import PersistentList

def check( context, object ):
    portal_metadata = getToolByName( object, 'portal_metadata' )
    categories = portal_metadata.objectValues()
    for cat in categories:
        if not getattr( cat, '_order', None ):
            return True
    return False

def migrate( context, object ):
    portal_metadata = getToolByName( object, 'portal_metadata' )
    categories = portal_metadata.objectValues()
    for cat in categories:
        if not getattr( cat, '_order', None ):
            init_list = [ attr.getId() for attr in cat._listAttributeDefinitions() ]
            cat._order = PersistentList( init_list )
