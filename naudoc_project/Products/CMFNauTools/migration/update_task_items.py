"""
$Id: update_task_items.py,v 1.7 2008/04/08 13:11:18 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

title = 'Update task items'
version = '3.3.1.2'
classes = [ 'Products.CMFNauTools.TaskItem.TaskItem' ]

from Products.CMFNauTools import Features
from Products.CMFNauTools.Exceptions import MigrationError
from Products.CMFCore.utils import getToolByName

portal_types = { 'TaskBrains_Directive'         : 'directive',
                 'TaskBrains_Request'           : 'request',
                 'TaskBrains_SignatureRequest'  : 'signature_request',
                 'TaskBrains_PublicationRequest': 'publication_request',
                 'TaskBrains_Modification'      : 'modification',
                 'TaskBrains_Inform'            : 'information',
                 'TaskBrains_ToApproval'        : 'to_approval',
               }

def check( context, object ):
    try:
        # Get persistent task items container object.
        container = context.parents[-3][1]
    except IndexError:
        return False
    return hasattr( container, 'implements' ) and container.implements( 'isTaskContainer' )

def migrate( context, object ):
    container = context.parents[-3][1]
    followup = getToolByName( context.portal, 'portal_followup' )
    context.fixBrokenState(object)

    brains_type = object.brains.__class__.__name__
    if getattr( object, 'temporal_expr', None ) is not None:
        type_name = 'recurrent'
    else:
        type_name = portal_types[ brains_type ]

    type_info = followup.getTaskType( type_name )
    if not type_info:
        raise MigrationError, "There is no information about '%s' task type." % type_name

    object = container._upgrade( object.getId(), type_info.getFactory(), container=container._container )
    del object.brains

    if object.finalized is None:
        object.finalized = False

    if getattr( object, '_expiration_schedule_id', None ):
        scheduler = getToolByName( context.portal, 'portal_scheduler', None )
        if scheduler:
            scheduler.delScheduleElement( object._expiration_schedule_id )
        object = object.__of__( context.portal )
        object.setAlarm( { 'type'         : 'percents',
                           'value'        : 10,
                           'note'         : '',
                           'include_descr': True,
                         } )

        del object._expiration_schedule_id
