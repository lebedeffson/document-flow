"""
$Id: fix_indexes.py,v 1.3 2007/10/10 10:56:17 oevsegneev Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

title = 'Fix catalog indexes'
version = '3.4.0.1'
classes = ['Products.CMFNauTools.CatalogTool.CatalogTool', 'Products.ZCatalog.ZCatalog.ZCatalog']

from BTrees.Length import Length

from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.PluginIndexes.PathIndex.PathIndex import PathIndex
from Products.CMFNauTools.AttributesIndex import AttributesIndex

def check(context, object):
    for idx in object.Indexes.objectValues():
        if isinstance(idx, (UnIndex, PathIndex)) and \
           not hasattr(idx, '_length'):
    	    return True

    return False

def migrate( context, object ):
    #hack for AttributesIndex

    for idx in object.Indexes.objectValues():
        if isinstance(idx, (UnIndex, PathIndex)) and \
           not hasattr(idx, '_length'):
            idx._length = Length(len(idx._index))
