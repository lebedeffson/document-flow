# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DirectoryObject/migration/update_directories.py
# Compiled at: 2005-03-16 14:51:15
"""
$Id: update_directories.py,v 1.2 2005/03/16 11:51:15 vsafronovich Exp $
$Editor: vsafronovich $
"""
__version__ = '$Revision: 1.2 $'[11:-2]
title = 'Update directory indexes and entries'
version = '3.2.0.167'
order = 90
from Products.CMFCore.utils import getToolByName

def migrate(context, object):
    catalog = getToolByName(context.portal, 'portal_catalog')
    results = catalog.searchResults(implements='isDirectory')
    for r in results:
        item = r.getObject()
        if item is None:
            continue
        if item._catalogInit(check=True) > 0:
            item._catalogInit()
            for entry in item.listEntries():
                item._catalogIndexEntry(entry)

    return
