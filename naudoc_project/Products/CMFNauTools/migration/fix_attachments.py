"""
$Id: fix_attachments.py,v 1.7 2005/05/14 05:43:46 vsafronovich Exp $
$Editor: inemihin $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

title = 'Migrate attachments'
version = '3.0.2.0'
classes = ['Products.CMFNauTools.HTMLDocument.HTMLDocument']

from Products.CMFCore.utils import getToolByName

_reserved_ids = [ 'version', 'followup' ]

def check( context, object ):
    for id in object.objectIds():
        if id not in _reserved_ids:
            return True
    return False

def migrate( context, object ):
    for version_id in object.version.objectIds():
        version = object.getVersion( version_id )
        for id in version.attachments:
            try:
                version.manage_pasteObjects( object.manage_copyObjects( id ) )
            except:
                pass

    for id in object.objectIds():
        if id not in _reserved_ids:
            try:
                object.manage_delObjects( [id] )
            except:
                pass
