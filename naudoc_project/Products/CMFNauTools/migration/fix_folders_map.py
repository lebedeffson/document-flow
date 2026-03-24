"""
$Id: fix_folders_map.py,v 1.3 2004/08/23 14:36:43 kfirsov Exp $
$Editor: inemihin $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

title = 'Restore folders consistency'
version = '3.2.0.37'
classes = ['OFS.ObjectManager.ObjectManager']

from Acquisition import aq_base

from Products.DCWorkflow.ContainerTab import ContainerTab

def repair( object, check=False ):
    for m in object._objects:
        try:
            ob = object._getOb( m['id'] )
        except KeyError:
            #this is a special case - ContainerTab
            if not isinstance(object, ContainerTab):
                raise
            continue
        meta_type = getattr( ob, 'meta_type', None )
        if meta_type != m['meta_type']:
            if not check:
                m['meta_type'] = meta_type
                continue
            return True

    return False

def check( context, object ):
    if hasattr( aq_base( object ), 'ob' ):
        return True

    return repair( object, check=True )

def migrate( context, object ):
    # Fix effects of the NauDoc V2.5 publisher's bug.
    if hasattr( aq_base( object ), 'ob' ):
        object._delOb('ob')

    return repair( object )
