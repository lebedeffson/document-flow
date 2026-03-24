"""
$Id: fix_ContainerTab.py,v 1.3 2004/09/02 05:57:43 vsafronovich Exp $
$Editor: kfirsov $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

title = 'Update container tab and its content'
version = '3.2.0.34'
classes = ['Products.DCWorkflow.ContainerTab.ContainerTab']

from Products.CMFNauTools.WorkflowTool import ContainerTab

def migrate( context, object ):
    mapping = getattr( object, '_mapping', None )
    if mapping is not None:
        try:
            delattr(mapping, '_v_data_cache')
            mapping._p_changed = 1
        except:
            pass
    return object
