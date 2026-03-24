""" FSFile class
$Id: FSFile.py,v 1.22 2006/06/22 11:27:15 oevsegneev Exp $

$Editor: kfirsov $
"""
__version__ = "$Revision: 1.22 $"[11:-2]


from zLOG import LOG, DEBUG, TRACE, INFO

from ntpath import splitext as nt_splitext
import os
import stat

from AccessControl import ClassSecurityInfo
from cStringIO import StringIO
from DateTime import DateTime
from OFS.content_types import guess_content_type
from ZPublisher.HTTPRequest import FileUpload

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Config
from Exceptions import SimpleError
import Features
from SimpleObjects import ContentBase, Persistent
from Utils import InitializeClass, recode_string, translit_string, getLanguageInfo

FSFileType = { 'id'             : 'FS File'
             , 'meta_type'      : 'FS File'
             , 'title'          : "File System File"
             , 'description'    : "FS Files can be embedded in FS Folders."
             , 'icon'           : 'fs_file.gif'
             , 'sort_order'     : 0.8
             , 'product'        : 'CMFNauTools'
             , 'factory'        : 'addFSFile'
             , 'immediate_view' : 'metadata_edit_form'
             , 'permissions'    : ( CMFCorePermissions.ManagePortal, )
             , 'disallow_manual': 1
             , 'actions'        :
               ( { 'id'            : 'view'
                 , 'name'          : "View"
                 , 'action'        : 'fs_file_view'
                 , 'permissions'   : ( CMFCorePermissions.View, )
                 }
               , { 'id'            : 'metadata'
                 , 'name'          : "Metadata"
                 , 'action'        : 'metadata_edit_form'
                 , 'permissions'   : (
                   CMFCorePermissions.ModifyPortalContent, )
                 }
               )
             }

def addFSFile( self
        , id
        , filepath
        , fullname
        , title = ''
        , description = ''
        ):
    """
        Adds a File System File
    """
    self._setObject(id, FSFile( id, filepath, fullname, title, description ) )


def recode_str( context, what ):
    lang = getLanguageInfo( context )
    python_charset = lang['python_charset']
    sys_charset = lang['system_charset']
    return recode_string( what, enc_from=sys_charset, enc_to=python_charset)

def translit_str( context, what ):
    lang = getToolByName(context, 'msg').get_selected_language()

    python_charset = Config.Languages.get(lang)['python_charset']
    sys_charset = Config.Languages.get(lang)['system_charset']

    recoded_what = recode_string( what, enc_from=sys_charset, enc_to=python_charset)
    return translit_string(recoded_what, lang=lang)

class FSObject( Persistent ):
    """
        Base class for both FSFile and FSFolder.
    """
    security = ClassSecurityInfo()

    def __init__(self, path):
        """
            Constructs instance of FSObject.

            Arguments:

                'path' -- Path in filesystem to object we want to present.
        """
        Persistent.__init__( self )
        self._path = os.path.normpath( path )

        if not self.checkExists():
            raise SimpleError( "No such directory. Path: %(path)s.", path=path )

        #extract name from path
        self._name = os.path.split( self._path )[1]

        self.creation_date = DateTime( os.stat( self._path )[stat.ST_MTIME] )
        self.modification_date = None
        self.updateModificationDate()

    def updateModificationDate( self ):
        """
            Updates date from object in filesystem.

            Result:

                True if time changed, False otherwise.
        """
        if not self.checkExists():
            return False

        mt = DateTime( os.stat( self._path )[stat.ST_MTIME] )
        if mt != self.modification_date:
            self.modification_date = mt
            return True
        return False


    def modified( self ):
        """
            Dublin Core element - date resource last modified,
              returned as DateTime.
        """
        self.updateModificationDate()
        return self.modification_date

    def checkUpdate( self, doNotRecurse=None ):
        #must be implemented by heirs.
        pass


    #name comes from CMFCore.FSObject
    security.declareProtected( CMFCorePermissions.View, 'getObjectFSPath' )
    def getObjectFSPath(self):
        """
            Returns the path of the file in FS.
        """
        return self._path[:]

    security.declareProtected( CMFCorePermissions.View, 'isAccessibeFS' )
    def isAccessibeFS(self):
        """
            More restrictive than checkExists().
        """
        return os.access(self._path, os.F_OK | os.R_OK)


    security.declareProtected( CMFCorePermissions.View, 'checkExists' )
    def checkExists(self):
        """
            Check if object in FS exists.
        """
        return os.path.exists( self._path )


    def _update(self):
        """
            Updates size and modification time if the file in FS was modified.
        """
        #Do not present next two methos because this class is just mix-in class.
        self.get_size(reRead=1)
        self.reindexObject()


class FSFile( FSObject, ContentBase ):
    """
        FS File class

        Objects of this class represent File System files.
    """

    _class_version = 1.01

    __implements__ = ( Features.isFSFile
                     , Features.isStatic
                     , Features.isPortalContent
                     , ContentBase.__implements__
                     )

    meta_type = 'FS File'
    portal_type = 'FS File'

    isCategorial = 0
    isDocument = 0
    isPrincipiaFolderish = 0

    security = ClassSecurityInfo()

    _size = None

    def __init__(self, id, path, title='', description='' ):
        """
            Constructs instance of FSFile.

            Arguments:

                'id' -- Object identifier.

                'path' -- Path in FS to the object we want to wrap.

                'title' -- Optional title.

                'description' -- Optional description.

        """
        FSObject.__init__(self, path)

        ContentBase.__init__( self, id, title )
        self.description = description

        self._basename, self._extension = nt_splitext( self._name )

        while self._extension and self._extension[0]=='.':
            self._extension = self._extension[1:]

        self.get_size(reRead=1)

        #guess content type
        self.content_type, enc = guess_content_type(name=self._name.lower(), default=Config.DefaultAttachmentType)

    def wrapWithFileUpload( self ):
        """
            Creates new ZPublisher.HTTPRequest.FileUpload instance which wraps
            our FSFile data.

            Result:

                ZPublisher.HTTPRequest.FileUpload instance.
        """
        class aFieldStorage: pass
        item = aFieldStorage()
        item.file = StringIO()
        self._read( item.file )

        item.filename = "%s_attach.%s" % ( translit_str(self, self._basename), self._extension)
        #item.headers  = {'Content-type': self.content_type}
        item.headers = None

        return FileUpload(item)


    def _initstate( self, mode ):
        """
            Initialize attributes
        """
        if not ContentBase._initstate( self, mode ):
            return 0

        if hasattr(self, '_filepath'):
            self._path = self._filepath
            del self._filepath

        if hasattr(self, '_fullname'):
            self._name = self._fullname
            del self._fullname

        return 1


    def _instance_onCreate(self):
        """
            If there is empty title, create it from filename.
        """
        self.title = self.title or recode_str(self, self._name)

    security.declareProtected( CMFCorePermissions.View, 'read' )
    def read(self):
        """
            Returns contents of wrapped FS file.

            Used in ExternalEditor.
        """
        data = StringIO()
        self._read( data )
        return data.getvalue()

    security.declareProtected( CMFCorePermissions.View, '_read' )
    def _read(self, outstream):
        """
            Reads binary data from file and writes it to outstream.

            Arguments:

                'outstream' -- Object of file type.
        """
        try:
            fp = open(self._path, 'rb')
            try:
                size=self.get_size(reRead=1)
                fp.seek(0)
                blocksize=2<<16
                pos=0
                while pos<size:
                    outstream.write(fp.read(blocksize))
                    pos=pos+blocksize
                fp.seek(0)
            except:
                outstream.write(fp.read())
            fp.close()
        except IOError:
            pass

    #XXX may be use FSImage.index_html instead ???
    security.declareProtected( CMFCorePermissions.View, 'index_html' )
    def index_html(self, REQUEST, RESPONSE):
        """
            Returns the file data.
        """
        self.checkUpdate()
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', self.get_size())

        RESPONSE.setHeader( 'Content-Disposition', '%s; filename="%s"; size="%d"' % \
            ( self.content_type, self._name, self.get_size() ) )
        self._read( outstream=RESPONSE )


    security.declareProtected(CMFCorePermissions.View, 'get_size')
    def get_size(self, reRead=0):
        """
            Returns the FS file size.

            Arguments:

                'reRead' -- If true, forces to update size from FS.
        """

        if not self.checkExists():
            self._size = None
        elif reRead:
            try:
                self._size = os.stat(self._path)[stat.ST_SIZE]
            except OSError:
                self._size = None
        return self._size


    security.declareProtected(CMFCorePermissions.View, 'getSize')
    getSize = get_size


    security.declareProtected( CMFCorePermissions.View, 'getFullName' )
    def getFullName(self):
        """
            Returns full FS file name.

            The name was recoded to python charset.
        """

        return recode_str(self, self._name)


    security.declareProtected( CMFCorePermissions.View, 'getFilePath' )
    def getFilePath(self):
        """
            Returns the FS file object path (recoded for view to python charset).
        """
        return recode_str(self, self._path)

    security.declareProtected( CMFCorePermissions.View, 'checkUpdate' )
    def checkUpdate( self, doNotRecurse=None ):
        """
            Checks if object modification time is the same with that of os file.

            Arguments:

                'doNotRecurse' -- ignored
        """
        if not self.checkExists():
            self.parent()._delObject( self.getId() )
            return

        date_chanded = self.updateModificationDate()
        if date_chanded:
            self._update()


    security.declareProtected( CMFCorePermissions.View, 'isViewable' )
    def isViewable(self):
        """
            Checks if object can be viewed in browser.
        """
        return self._extension.lower() in ['bmp','jpg','gif','png','pcx','txt','htm','html']

    security.declareProtected( CMFCorePermissions.View, 'getIcon' )
    def getIcon(self, relative_to_portal=0):
        """
            Returns the file type sensitive icon.
        """
        icon = FSFileType['icon']
        icon = Config.Icon2FileMap.get(self._extension.lower(), icon)

        if not relative_to_portal:
            # Relative to REQUEST['BASEPATH1']
            portal_url = getToolByName( self, 'portal_url' )
            res = portal_url(relative=1) + '/' + icon
            while res[:1] == '/':
                res = res[1:]
            return res

        return icon

    def getOwner( self ):
        """
            Returns owner for this object.

            There is no owner for files stored in file system.
        """
        return None


    def cb_isMoveable(self):
        """ Disallow moved via clipboard
        """
        return 0

InitializeClass( FSFile )

def initialize( context ):
    # module initialization callback

    context.registerContent( FSFile, addFSFile, FSFileType )
