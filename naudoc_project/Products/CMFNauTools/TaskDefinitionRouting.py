"""
$Id: TaskDefinitionRouting.py,v 1.24 2008/01/29 09:44:59 oevsegneev Exp $

Action template for routing document via shortcut or moving to another folder.
"""

__version__ = '$Revision: 1.24 $'[11:-2]

import sys

from Acquisition import aq_base, aq_inner, aq_parent
from OFS.CopySupport import CopyError, eNotSupported, sanity_check

from Products.CMFCore.WorkflowCore import ObjectMoved

import Exceptions
from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import cookId, InitializeClass, getObjectByUid, getToolByName, getFolderAnyway
from PatternProcessor import PatternProcessor

#--------------------------------------------------------------
class TaskDefinitionRouting( TaskDefinition ):
    """
        Document routing on the basis of shortcut and/or relocation between folders.
    """
    _class_version = 1.00


    dest_folder_type = 'path'
    dest_folder_template = '.'
    dest_folder_uid = None
    dest_folder_title = ''
    dest_folder_URL = ''

    def __init__( self, routing_type='routing_shortcut' ):
        """
            Creates new instance.
            May be 2 types of routing:

                1. Creating shortcut in the specific folder
                2. Moving document itself to the specific folder

        """
        TaskDefinition.__init__( self )
        self.type = routing_type

    def changeTo( self, taskDefinition ):
        """
          Changes self data.

          Changes 'dest_folder_uid' explicitly; 'dest_folder_title' and
          'dest_folder_URL' are changed according 'dest_folder_uid'.

          Arguments:

            'task_definition' -- instance of TaskDefinition, to which
                                 needed to change
        """
        TaskDefinition.changeTo( self, taskDefinition )

        # specific fields
        self.dest_folder_type = taskDefinition.dest_folder_type
        self.dest_folder_template = taskDefinition.dest_folder_template
        self.dest_folder_uid = taskDefinition.dest_folder_uid
        object = getObjectByUid( self, self.dest_folder_uid )
        if object:
            self.dest_folder_title = object.title_or_id()
            self.dest_folder_URL = object.absolute_url()

    def toArray( self ):
        """
          Converts object's fields to dictionary

          Result:

            Dictionary as { 'field_name': 'field_value', ... }

        """
        arr = TaskDefinition.toArray( self )
        arr["dest_folder_type"] = self.dest_folder_type
        arr["dest_folder_template"] = self.dest_folder_template
        arr["dest_folder_uid"] = self.dest_folder_uid
        arr["dest_folder_title"] = self.dest_folder_title
        arr["dest_folder_URL"] = self.dest_folder_URL
        return arr

    def activate( self, object, context, transition ):
        """
            Activate taskDefinition (action template)

            According self.type will be created shortcut in the folder defined
            earlier or object itself will be moved there. There is no need for
            user who changes state of the object to have appropriate
            permissions in destination folder to move object there.

            Arguments:

                'object' -- object in context of which happened activation

                'ret_from_up' -- dictionary

            Result:

                Also returns dictionary, which is passed to next (inner)
                taskDefinition's activate (if presented)

        """
        if not ( self.dest_folder_type=='path' and self.dest_folder_uid \
                or self.dest_folder_type=='template' and self.dest_folder_template ):
            raise Exceptions.SimpleError( "Task template '%(task)s' is not configured properly.", task=self )

        # locating destination folder
        if self.dest_folder_type == 'template':
            path = PatternProcessor.processString( self.dest_folder_template, fmt='folder_routing', doc=object )
            folder_to_move = getFolderAnyway( object, path=path )
        else:
            folder_to_move = getObjectByUid( self, self.dest_folder_uid )

        if folder_to_move is None:
            raise Exceptions.SimpleError('Folder not found')

        if self.type == 'routing_shortcut':

            #generate id first
            shortcut_id = cookId( folder_to_move, id=object.getId() )

            #create shortcut
            folder_to_move.manage_addProduct['CMFNauTools'].addShortcut(id=shortcut_id, remote=object)

        elif self.type == 'routing_object':
            dest_id = object.getId()

            #if no copies permitted uncomment this:
            #folder_to_move._checkId( dest_id )

            #code from OFS.CopySupport to prevent security check
            if not self.object_cb_isMoveable(object):
                raise CopyError, eNotSupported % dest_id
            try:    object._notifyOfCopyTo(folder_to_move, op=1)
            except: raise CopyError, sys.exc_info()[1]

            if not sanity_check(folder_to_move, object):
                raise CopyError, 'This object cannot be pasted into itself'

            object=object.moveObject( folder_to_move )
            object.manage_changeOwnershipType(explicit=0)
            raise ObjectMoved( object )
        else:
            raise Exceptions.SimpleError('Invalid routing type')

    def object_cb_isMoveable(self, object):
        """
        Overrides cb_isMoveable() for the object.

            Does not make ALL necessary checks but here it is not needed.
        """
        # Is object moveable? Returns 0 or 1
        if not (hasattr(object, '_canCopy') and object._canCopy(1)):
            return 0
        if hasattr(object, '_p_jar') and object._p_jar is None:
            return 0
        try:    n=aq_parent(aq_inner(object))._reserved_names
        except: n=()

        o_id = object.id
        if callable(object.id):
            o_id = object.id()

        if o_id in n:
            return 0
        return 1

InitializeClass( TaskDefinitionRouting )

class TaskDefinitionFormRouting( TaskDefinitionForm ):
    """
      Class view (form)

    """
    _template = 'task_definition_routing'

class TaskDefinitionControllerRouting( TaskDefinitionController ):
    """
      Class controller

    """

    def __init__( self, routing_type='routing_shortcut' ):
        """
            Constructs instance with selected routing type.
        """
        self.routing_type = routing_type

    def getEmptyArray( self ):
        """
          Returns dictionary with empty values.

          Arguments:

            'emptyArray' -- dictionary to fill

        """
        emptyArray = TaskDefinitionController.getEmptyArray( self )
        emptyArray['dest_folder_type'] = 'path'
        emptyArray['dest_folder_template'] = '.'
        emptyArray['dest_folder_uid'] = None
        emptyArray['dest_folder_title'] = ''
        emptyArray['dest_folder_URL'] = ''
        return emptyArray

    def getTaskDefinitionByRequest( self, request ):
        """
            Gets destination folder uid from request and srotes it in
            TaskDefinitionRouting() instance.

        """
        taskDefinition = TaskDefinitionRouting( self.routing_type )
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )
        taskDefinition.dest_folder_type = request.get('dest_folder_type', 'path')
        taskDefinition.dest_folder_uid = request.get('dest_folder_uid', None)
        taskDefinition.dest_folder_template = request.get('dest_folder_template', None)

        return taskDefinition


class TaskDefinitionRegistryRouting( TaskDefinitionRegistry ):
    """
        Class that provides information for factory about class
    """
    type_list = ( { "id": "routing_shortcut"
                  , "title": "Document routing via shortcut"
                  },
                  { "id": "routing_object"
                  , "title": "Document routing via moving between folders"
                  },
                )

    Form = TaskDefinitionFormRouting()

    dtml_token = 'routing'

    def getControllerImplementation( self, task_definition_type ):
        """
            Returns controller implementation

            Arguments:

                'task_definition_type' -- type of action
                # task_definition_type - 'routing_shortcut' or 'routing_object'
        """
        return TaskDefinitionControllerRouting( task_definition_type )


def initialize( context ):
    context.registerAction( TaskDefinitionRegistryRouting() )
