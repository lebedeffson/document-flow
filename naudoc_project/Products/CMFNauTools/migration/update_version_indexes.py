"""
$Id: update_version_indexes.py,v 1.2 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = 'Fix nd_uid index of versionable content'
version = '3.4.0.0'
classes = ['Products.CMFNauTools.HTMLDocument.HTMLDocument']

def migrate( context, object ):
    if object.implements('isVersion'):
	object.reindexObject( idxs=['nd_uid'] )
