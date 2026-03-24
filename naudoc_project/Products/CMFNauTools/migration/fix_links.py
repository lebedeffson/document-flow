"""
$Id: fix_links.py,v 1.6 2004/06/11 12:13:44 vpastukhov Exp $
$Editor: vpastukhov $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

title = 'Migrate inter-object links'
classes = ['Products.CMFNauTools.DocumentLinkTool.Link']
#check_tag = 1
version = '3.1.5.46'

from types import StringType
from Acquisition import aq_base
from Products.CMFNauTools.ResourceUid import ResourceUid

def migrate( context, object ):
    # rely on _initstate in Link class for now
    context.markForReindex( object, catalog='portal_links' )
    return

    base = aq_base( object )
    indexes = {}

    if not hasattr( base, 'creation_date' ): # < 1.35
        base.creation_date = base.bobobase_modification_time()
        indexes['created'] = 1

    if not hasattr( base, 'modification_date' ): # < 1.35
        base.modification_date = base.bobobase_modification_time()
        indexes['modified'] = 1

    if hasattr( base, 'source_uid' ) and type( base.source_uid ) is StringType: # < 1.28
        base.source_uid = ResourceUid( base.source_uid )
        indexes['SourceUid'] = 1

    if hasattr( base, 'dest_uid' ): # < 1.28
        base.target_uid = ResourceUid( base.dest_uid )
        del base.dest_uid
        indexes['TargetUid'] = 1

        extra = base.extra
        if extra:
            source_uid = base.source_uid
            target_uid = base.target_uid
            for key, value in extra.items():
                if key.startswith('source_'):
                    setattr( source_uid, key[ len('source_'): ], value )
                elif key.startswith('destination_'):
                    setattr( target_uid, key[ len('destination_'): ], value )
                elif key in ['field_id','uname','status']:
                    setattr( source_uid, key, value )
                else:
                    continue
                del extra[ key ]
            indexes['Extra'] = 1

    if hasattr( base, 'dest_removed' ): # < 1.29
        base.target_removed = not not base.dest_removed
        del base.dest_removed
        indexes['target_removed'] = 1

    if hasattr( base, 'source' ): # < 1.32
        base.source_data = base.source
        del base.source

    if hasattr( base, 'destination' ): # < 1.32
        base.target_data = base.destination
        del base.destination

    if hasattr( base, 'relation_type' ): # < 1.47.2.1.2.1
        if base.relation_type == 0:
            base.relation = 'dependence'
        else:
            base.relation = 'reference'
        del base.relation_type
        indexes['relation'] = 1

        if base.relation_direction:
            temp = base.source_uid
            base.source_uid = base.target_uid
            base.target_uid = temp
            temp = base.source_data
            base.source_data = base.target_data
            base.target_data = temp
            indexes['SourceUid'] = 1
            indexes['TargetUid'] = 1
        del base.relation_direction

    if base.relation == 'dependence' and \
            not base.__dict__.has_key('target_locked'): # < 1.36
        base.target_locked = True

    context.markForReindex( object, catalog='portal_links', idxs=indexes.keys() )
