"""
$Id: guardedtable_entries.py,v 1.5 2004/04/30 11:27:50 vsafronovich Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.5 $'[11:-2]

title = 'Convert table entries'
version = '2.12'
classes = ['Products.CMFNauTools.GuardedTable.GuardedTable']

from Acquisition import aq_base
from Products.CMFNauTools.Utils import cookId

def check(context, object):
    return hasattr( aq_base(object), 'entries' )

def migrate(context, object):
    object._catalog.clear()

    for entry in list(object.entries.values()):
        id = cookId(object, prefix='entry')
        entry.id = id
        object._setObject(id, entry)
        entry = object.getEntryById(id)
        object.catalog_object(entry, id)

    del object.entries
