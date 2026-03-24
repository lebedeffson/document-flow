"""Task Item container class.

$Editor: ikuleshov $
$Id: TaskItemContainer.py,v 1.11 2007/02/01 15:27:56 oevsegneev Exp $
"""
__version__ = '$Revision: 1.11 $'[11:-2]

from threading import Event
from random import random

from AccessControl import ClassSecurityInfo, Permissions
from Acquisition import aq_inner, aq_base, aq_parent
from Globals import PersistentMapping
from OFS.ObjectManager import ObjectManager
from ZODB.POSException import ConflictError
 
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser, _checkPermission

import Features
from Config import Roles
from SimpleObjects import Persistent, InstanceBase, ContentBase
from Utils import InitializeClass, cookId

class TaskItemContainer( InstanceBase, ObjectManager ):
    """
    """
    _class_version = 1.78

    meta_type = 'Task Item Container'
    id = 'followup'

    isTaskContainer = 1

    __resource_type__ = 'container'

    security = ClassSecurityInfo()
    security.declareProtected( CMFCorePermissions.View, 'getId' )
    security.setDefaultAccess(1)

    def __init__(self):
        InstanceBase.__init__( self )
        self._container = PersistentMapping()

    security.declareProtected( CMFCorePermissions.View, '__bobo_traverse__' )
    def __bobo_traverse__( self, REQUEST, name ):
        """
          This will make this container traversable
        """
        target = getattr(self, name, None)
        if target is not None:
            return target
        else:
            try:
                #base = self.getBase()
                #version_id = self.getTask(name)._getVersionId()
                #if base.implements(('isVersionable', 'isVersion',)) and version_id:
                #    base.getVersion( version_id ).makeCurrent()
                return self.getTask(name)
            except KeyError:
                parent = aq_parent( aq_inner( self ) )
                if parent.getId() == name:
                    return parent
                else:
                    REQUEST.RESPONSE.notFoundError("%s\n%s" % (name, ''))

    #
    #   Threading interface
    #
    security.declareProtected( CMFCorePermissions.View,
                               'createTask' )
    def createTask( self,
                    title,
                    type=None,
                    bind_to=None,
                    creator=None,
                    REQUEST=None,
                    **kw
                  ):
        id = cookId( self._container, prefix='task' )
        creator = creator or _getAuthenticatedUser( self ).getUserName()
        followup = getToolByName( self, 'portal_followup' )    

        # Compatibility issue
        if kw.has_key( 'brains_type' ):
            type = kw[ 'brains_type' ]
            del kw[ 'brains_type' ]
        if not type:
            type = 'directive'

        type_info = followup.getTaskType( type )
        factory = type_info.getFactory()
        task = factory( id,
                        title,
                        creator=creator,
                        **kw
                       )
        
        self._container[ id ] = task
        task = self._container[ id ].__of__( self )
        task.manage_fixupOwnershipAfterAdd()
        # Try to give user the local role "Owner", but only if
        # no local roles have been set on the task yet.
        if hasattr( task, '__ac_local_roles__' ):
            if task.__ac_local_roles__ is None:
                if creator != 'Anonymous User':
                    task.manage_setLocalRoles( creator, ['Owner'] )

        if bind_to and self.getTask( bind_to ):
            parent = self.getTask( bind_to )
        else:
            parent = self._getTask()
        task.BindTo( parent )

        task.manage_afterAdd( task, self )

        # In case the task is being created in the portal root we should 
        # allow every member to view the task item or there will be no way 
        # to access the child item for inolved members of ancestor tasks.
        if self.parent().implements( Features.isPortalRoot ): 
            task.manage_permission( CMFCorePermissions.View, ( Roles.Reader, Roles.Owner, Roles.Manager, Roles.Editor, Roles.Member), 0 )
        else:
            task.manage_permission( CMFCorePermissions.View, ( Roles.Reader, Roles.Owner, Roles.Manager, Roles.Editor,), 0 )

        if not task.effective().isFuture():
            task.Enable( None )

        # What indexes are updated here?
        task.updateIndexes()

        if REQUEST is not None:
            task.redirect( REQUEST=REQUEST, action='view' )
        else:
            return id

    security.declareProtected( CMFCorePermissions.View, 'getBase' )
    getBase = InstanceBase.parent

    security.declareProtected( CMFCorePermissions.View, 'getTask' )
    def getTask( self, task_id ):
        """
            Returns a task item, given its ID;  raise KeyError
            if not found.
        """
        return self._container[ task_id ].__of__( self )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'deleteTask' )
    def deleteTask( self, task_id ):
        """
            Remove a task item from this container
        """
        if self._container.has_key( task_id ):
            task = self._container.get( task_id ).__of__( self )
            task._ItemBase__instance_destroyed = True
            task.manage_beforeDelete(task, self)

            sub_tasks = task.followup.getBoundTasks( recursive = 1 )
            for sub_task in sub_tasks:
                sub_task._ItemBase__instance_destroyed = True
                sub_task.manage_beforeDelete(sub_task, self)
                sub_task_id = sub_task.getId()
                del self._container[sub_task_id]

            del self._container[task_id]

    security.declareProtected( CMFCorePermissions.View, 'getBoundTasks' )
    def getBoundTasks( self, version_id=None, recursive=None ):
        """
            Returns the list of the bound tasks and filters out tasks from another document versions.

            Adds acquisition wrapper to the task items.
        """
        objects = []
        a = objects.append

        for task in self._getBoundTasks( recursive ):
            task = task.__of__( self )
            if version_id:
                # if document's version doesn't match task's version,
                # don't append task to bound list
                if task._getVersionId() != version_id:
                    continue
            a( task )

        return objects

    security.declareProtected( CMFCorePermissions.View, 'getBoundTaskIds' )
    def getBoundTaskIds( self, version_id=None, recursive=None ):
        """
            Returns the list of the bound tasks ids
        """
        return [ task.getId() for task in self.getBoundTasks( version_id, recursive ) ]

    security.declareProtected( CMFCorePermissions.View, 'quotedContents' )
    def quotedContents( self ):
        """
          Returns this object's contents in a form suitable for inclusion
          as a quote in a response.
        """

        return ""

    #
    #   Utility methods
    #
    security.declarePrivate( '_getTaskParent' )
    def _getTaskParent( self, bind_to=None ):
        """
          Returns the object indicated by the 'bind_to', where
          'None' represents the "outer" content object.
        """
        outer = self._getTask( outer=1 )
        if bind_to is None:
            return outer
        parent = self._container[ bind_to ].__of__( aq_inner( self ) )
        return parent.__of__( outer )

    security.declarePrivate( '_getTask' )
    def _getTask( self, outer=0 ):
        tb = outer and aq_inner( self ) or self
        parent = getattr( tb, 'aq_parent', None )
        while parent is not None and parent.implements( 'isVersion' ):
            parent = parent.getVersionable()
        return parent

    security.declarePrivate( '_getBoundTasks' )
    def _getBoundTasks( self, recursive ):
        """
          Returns a list of task ids which are replies to our task.

          Does not add acquisition wrapper to the returned tasks.
        """
        task = self._getTask()
        outer = self._getTask( outer=1 )

        if task == outer:
            bind_to = None
        else:
            bind_to = task.getId()

        result = []
        a = result.append
        for value in self._container.values():
            if hasattr( value, 'bind_to' ) and value.bind_to == bind_to:
                a( value )
                if recursive:
                    result.extend( self.__of__(value)._getBoundTasks( recursive=1 ) )

        return result

    def _instance_onClone(self, source, item ):
        """
          Copy/paste event handler
        """
        # Remove tasks from the document copy
        # it is horrible to clear the container with out invoke manage_beforeDelete
        # and our ItemBase hooks, but in this method it is impossible to call deleteTask method
        # because it deleted scheduler elements of the source object.
        self._container.clear()

    def _containment_onAdd( self, item, container ):
        ObjectManager.manage_afterAdd( self, item, container )

    def _containment_onDelete( self, item, container ):
        ObjectManager.manage_beforeDelete( self, item, container )

    #
    #   OFS.ObjectManager query interface.
    #
    security.declareProtected( CMFCorePermissions.AccessContentsInformation,
                               'objectIds' )
    def objectIds( self, spec=None ):
        """
            Returns a list of the Task Items ids.
        """
#        if spec and spec is not TaskItem.meta_type:
#            return []
        return self._container.keys()


    security.declareProtected( CMFCorePermissions.AccessContentsInformation,
                               'objectItems' )
    def objectItems(self, spec=None):
        """
            Return a list of (id, subobject) tuples for our TaskItems.
        """
        r=[]
        a=r.append
        g=self._container.__getitem__
        for id in self.objectIds( spec ):
            a( (id, g( id ).__of__( self ) ) )
        return r

    security.declareProtected( CMFCorePermissions.AccessContentsInformation,
                               'objectValues' )
    def objectValues(self):
        """
          Returns the tasks list stored within the current container
        """
        return [ x.__of__(self) for x in self._container.values() ]

    def changeOwnership(self, *args, **kwargs):
        pass

InitializeClass( TaskItemContainer )

class ContainerResource:

    id = 'container'

    def identify( portal, object ):
        try:
            uid = object.getBase().physical_path()
        except AttributeError:
            uid = None
        return { 'uid' : uid }

    def lookup( portal, uid=None, **kwargs ):
        object = portal.unrestrictedTraverse( str(uid), None )
        if object is None:
            raise Exceptions.LocatorError( 'container', uid )
        return object.followup


def initialize( context ):
    context.registerResource( 'container', ContainerResource)
