""" FSFolder class
$Id: FSFolder.py,v 1.24 2006/06/22 11:27:15 oevsegneev Exp $

$Editor: kfirsov $
"""
__version__ = "$Revision: 1.24 $"[11:-2]

from zLOG import LOG, DEBUG, TRACE, INFO

from ntpath import splitext as nt_splitext
import os
import stat

from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from Acquisition import aq_parent

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Config, Features, Exceptions
from FSFile import FSObject, FSFile, translit_str, recode_str
from Heading import Heading
from Utils import cookId, InitializeClass


FSFolderType = { 'id'             : 'FS Folder'
               , 'meta_type'      : 'FS Folder'
               , 'title'          : "File System Folder"
               , 'description'    : "FS Folder objects can be embedded in "
                                    "Portal documents and added to the external sites."
               , 'icon'           : 'fs_folder_icon.gif'
               , 'sort_order'   : 0.8
               , 'product'        : 'CMFNauTools'
               , 'factory'        : 'addFSFolder'
               , 'factory_form'   : 'fs_folder_factory_form'
               , 'immediate_view' : 'folder'
               , 'permissions'    : ( CMFCorePermissions.ManagePortal, )
               , 'allowed_content_types' :
                    ( 'FS Folder',
                      'FS File',
                      'Site Image'
                    )
               , 'actions'        :
                 ( { 'id'            : 'view'
                   , 'name'          : "View"
                   , 'action'        : 'folder'
                   , 'permissions'   : ( CMFCorePermissions.View, )
                   , 'category'      : 'folder'
                   }
                 , { 'id'            : 'metadata'
                   , 'name'          : "Metadata"
                   , 'action'        : 'fs_folder_edit_form'
                   , 'permissions'   : (
                      CMFCorePermissions.ModifyPortalContent, )
                   , 'category'      : 'folder'
                   }
                 )
               }

def addFSFolder( self
            , id
            , path =''
            , title=''
            , description=''
            , REQUEST=None
            ):
    """
        Adds a File System Folder
    """
    self._setObject(id, FSFolder( id, path, title, description, root=1))

class FSFolder( FSObject, Heading ):
    """
        FS Folder class

        Objects of this class represent folder in File System (looks like
        Heading in NauDoc).
    """
    _class_version = 1.02

    meta_type = 'FS Folder'
    portal_type = 'FS Folder'

    __implements__ = ( Features.isFSFolder
                     , Features.isPrincipiaFolderish
                     , Features.isStatic
                     , Heading.__implements__
                     )

    __unimplements__ = ( Features.isCategorial
                       , Features.hasSubscription
                       )

    _update_needed = None

    security = ClassSecurityInfo()

    root = None

    def __init__(self, id, path, title='', description='', root=0):
        """
            Constructs instance of FSFolder.

            Arguments:

                'id' -- Object identifier.

                'path' -- Path in FS to the object we want to wrap.

                'title' -- Optional title.

                'description' -- Optional decription.
        """
        FSObject.__init__(self, path)

        Heading.__init__(self, id, title)
        self.description = description
        self.root = root

    def _initstate( self, mode ):
        """
            Initialize attributes
        """
        if not Heading._initstate( self, mode ):
            return 0

        if hasattr(self, '_folder_path'):
            self._path = self._folder_path
            del self._folder_path

        return 1

    def _instance_onCreate( self ):
        """
            Instance creation event hook.
            Updates the FSFolder contents.
        """
        self.manage_permission( CMFCorePermissions.AddPortalContent )
        self._update_needed = 1
        self.checkUpdate()

    def listDocuments( self, REQUEST=None, **kw ):
        """
            Extends Heading.listDocuments().

            Besides Heading.listDocuments operations, checks if the folder
            (or any subobject in the folder) in FS was changed.
        """
        # Update contents here
        self.checkUpdate()
        return Heading.listDocuments( self, REQUEST, **kw )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'edit' )
    def edit(self, title=None, description=None):
        """
            Edits FSFolder properties. Updates FS folder data (filelist,
            modification date and so on) and reindexes data in the catalog.

            Arguments:

                'title' -- Optional title.

                'description' -- Optional description.
        """
        self.setTitle( title )
        self.setDescription( description )
        self.checkUpdate()

        # XXX is this needed?
        self.reindexObject()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setPath' )
    def setPath(self, path=None):
        """
            Sets the path of the folder in FS.

            Arguments:

                'path' -- Path in FS to the object we want to wrap.
        """
        if not path:
            return
        folder_path = os.path.normpath( path )
        if not os.path.exists( folder_path ):
            raise Exceptions.SimpleError( "No such directory. Path: %s.", path=folder_path )
        self._path = folder_path
        self._completelyUpdate()


    def _completelyUpdate(self):
        #Completely update - remove all objects and then create them from self._path
        self.manage_delObjects( self.objectIds() )
        self._update_needed = 1
        self.checkUpdate()
        self.reindexObject()

    def isAccessibeFS(self):
        """
            More restrictive than checkExists().
        """
        return os.access(self._path, os.F_OK | os.R_OK | os.X_OK)

    def _update(self, doNotRecurse=None):
        """
            Updates FSFolder and its contents.
        """
        if doNotRecurse:
            self._update_needed = 1
            return

        #collect all file objects in the directory
        paths = {}
        if self.isAccessibeFS():
            for entry in os.listdir( self._path ):
                entry_path = os.path.join( self._path, entry )
                paths[ entry_path ] = entry

        #remove non-existent objects
        for o_id, object in self.objectItems():
            obj_path_is_dir = os.path.isdir( object.getObjectFSPath() )

            if not object.checkExists() \
                or (obj_path_is_dir and object.implements('isFSFile')) \
                or (not obj_path_is_dir and object.implements('isFSFolder')):
                self._delObject( o_id )
            else:
                object.checkUpdate( doNotRecurse=1 )
                try:
                    del paths[ object.getObjectFSPath() ]
                except KeyError:
                    pass

        #create new fs files and folders
        for path, name in paths.items():
            factory = FSFile
            if os.path.isdir( path ):
                factory = FSFolder
            self._createFSObject( path, name, factory=factory)

        self._update_needed = None

        # XXX is this needed?
        self.reindexObject()

    def _createFSObject(self, file_path, file_name, factory=FSFile):
        """
            Creates object of FSFile or FSObject.

            Arguments:

                'file_path' -- Full path to the object in file system.

                'file_name' -- Name of the obejct in file system.

                'factory' -- Class of object to create. May be FSFile or FSFolder.
        """
        recoded_name = recode_str( self, file_name )
        translit_name = translit_str( self, file_name )

        id = cookId(self, translit_name)

        obj = factory( id=id, path=file_path, title=recoded_name )

        self._setObject(id, obj)
#        obj = self._getOb(id)

#        obj.manage_permission(ZopePermissions.delete_objects, [], 0)

    def checkUpdate(self, doNotRecurse=None):
        """
            Checks if object modification time is the same with that of os file.

            Arguments:

                'doNotRecurse' -- If true, updates only this object's data,
                    does not tests subobjects.
        """
        if not self.checkExists():
            self.parent()._delObject( self.getId() )
            return

        date_chanded = self.updateModificationDate()
        if date_chanded or self._update_needed:
            self._update( doNotRecurse )

    security.declareProtected( ZopePermissions.delete_objects, 'deleteObjects' )
    def deleteObjects(self, ids=[]):
        """
        """
        raise NotImplementedError

    def cb_dataValid( self ):
        """ Disallow paste into self
        """
        return 0

    def _verifyObjectPaste( self, object, validate_src=1 ):
        """ Disallow paste into self
        """
        raise Exceptions.CopyError

    def cb_isMoveable(self):
        """ Disallow moved subFSFolders via clipboard
        """
        return self.root and Heading.cb_isMoveable(self) or 0

InitializeClass( FSFolder )

def initialize( context ):
    # module initialization callback

    context.registerContent( FSFolder,  addFSFolder,  FSFolderType )
