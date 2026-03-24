"""
$Id: update_resource_uids.py,v 1.2 2004/06/18 15:03:01 vpastukhov Exp $
$Editor: vpastukhov $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = 'Update object references'
classes = ['Products.CMFNauTools.ResourceUid.ResourceUid']
version = '3.1.5.54'

from Products.CMFNauTools.Exceptions import LocatorError
from Products.CMFNauTools.ResourceUid import ResourceUid

def check( context, object ):
    if object.type is None:
        return True

    try:
        target = object.deref( context.portal )
        uid = ResourceUid( target )
    except ( LocatorError, TypeError ):
        return False
    else:
        return (object.type != uid.type)

def migrate( context, object ):
    container = context.container

    try:
        target = object.deref( context.portal )
        uid = ResourceUid( target )
    except ( LocatorError, TypeError ):
        object.type = 'content'
    else:
        object.type = uid.type
        for key, value in uid.dict().items():
            if not hasattr( object, key ):
                setattr( object, key, value )

    if hasattr( container, '_p_changed' ):
        container._p_changed = 1

    if container.meta_type == 'Link':
        if context.name == 'source_uid':
            idx = 'SourceUid'
        elif context.name == 'target_uid':
            idx = 'TargetUid'
        else:
            idx = None
        if idx:
            context.markForReindex( container, catalog='portal_links', idxs=[idx] )
