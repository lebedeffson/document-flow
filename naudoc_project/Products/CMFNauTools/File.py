"""
Implementation of the file attachments for the documents.

    'FileAttachment' class -- file attachment implementation

    'addFile' function -- handles upload of a new file object
                          and attaches it to the container

$Editor: vpastukhov $
$Id: File.py,v 1.38 2006/10/06 13:20:12 oevsegneev Exp $
"""
__version__ = '$Revision: 1.38 $'[11:-2]

import re, os
from cStringIO import StringIO
from ntpath import basename as nt_basename, splitext as nt_splitext
from types import StringType, UnicodeType, ListType

import OFS.Image
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from OFS.Image import File, cookId, Image
from ZPublisher.HTTPRequest import FileUpload

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

import Config, Exceptions, Features
import Converter
from ActionInformation import ActionInformation as AI
from Features import createFeature
from ImageAttachment import ImageAttachment
from SimpleNauItem import SimpleNauItem
from SimpleObjects import ContentBase
from Utils import InitializeClass, extractBody, translit_string

if Config.EnableFSStorage:
    from Products.ExtFile import ExtFile

    ExtFile.REPOSITORY = ExtFile.SYNC_ZODB
    ExtFile.REPOSITORY_EXTENSIONS = ExtFile.ZOPEID

    class File(ExtFile.ExtFile):
        """
            Adapter from ExtFile interface to OFS.File.

            Also provides two modifications of ExtFile behaviour:

                1. _get_zodb_path returns our configurable path.

                2. Backup files are not keeped.

        """
        _repository = ['var']

        def __init__(self, id, title, file, content_type='', precondition=''):
            ExtFile.ExtFile.__init__(self, id, title)
            #self.manage_upload(file)

        def __str__(self):
            return open(self._get_fsname(self.filename), 'rb').read()

        def _get_zodb_path(self, parent=None):
            portal_id = getToolByName(self, 'portal_url').getPortalObject().getId()
            date = self.created()

            return [portal_id] + map(date.strftime, Config.FSStorageFormat)

        def index_html(self, REQUEST, RESPONSE):
            return ExtFile.ExtFile.index_html(self, REQUEST = REQUEST)

        def _setId(self, id):
            pass

        def update_data(self, data, content_type = None, size = None):
            ExtFile.ExtFile.manage_upload(self, data, content_type)

        def manage_upload(self, file = '', REQUEST = None):
            if isinstance(file, StringType):
                self.update_data(file)
            else:
                self.manage_file_upload(file)

        def manage_beforeDelete(self, item, container):
            self._register()
            self._v_delete_files = True

        def _finish(self):
            if getattr(self, '_v_delete_files', False):
                for filename in (self._temp_fsname(self.filename),
                                 self._fsname(self.filename)):
                    if os.path.isfile(filename):
                        try: os.remove(filename)
                        except OSError: pass

            else:
                ExtFile.ExtFile._finish(self)

        def _file_read(self):
            # special method for ExternalEditor, which in contrast to
            # manage_FTPget doesn't spoil RESPONSE when it not needed.

            filename = self._get_fsname(self.filename)
            return open(filename, 'rb').read()

manage_addAttachmentForm = DTMLFile( 'dtml/imageAdd', OFS.Image.__dict__, Kind='Attachment' )

def manage_addAttachment( self, id, file='', title='', filename=None, content_type='', REQUEST=None ):
    """
        Creates a new FileAttachment object and inserts it
        into the container.

        Arguments:

            'id' -- identifier string of the new object

            'file' -- optional FileUpload object or string;
                      if not given, the object is created with
                      empty contents

            'title' -- optional title of the object;
                       empty by default

            'filename' -- optional name of the file to be stored
                          in the respective object property;
                          if not given, the method tries to obtain
                          it from the FileUpload object or uses 'id'
                          value as a last resort

            'content_type' -- optional MIME type of the file contents

            'REQUEST' -- optional Zope request object

        Result:

            Redirect to the main management screen of the container
            if REQUEST is specified.
    """
    # XXX make this work
    #if not isinstance( self, SimpleNauItem ):
    #    raise TypeError, 'This object cannot contain attachments.'

    id = str(id)
    title = str(title)
    content_type = str(content_type)

    # first, create the file without data:
    self._setObject( id, FileAttachment( id, title, '', content_type ) )
    ob = self._getOb( id )

    if not filename:
        filename = isinstance( file, FileUpload ) and file.filename or id
    ob._setPropValue( 'original_filename', nt_basename( filename ) )

    # Now we "upload" the data.  By doing this in two steps, we
    # can use a database trick to make the upload more efficient.
    if file:
        ob.manage_upload( file )

    # force given content type
    if content_type:
        ob._setPropValue( 'content_type', content_type )

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect( self.absolute_url() + '/manage_main' )


_activex_types = Converter.MSWordConverter.content_types


class FileAttachment( ContentBase, File ):
    """
        File attachment class.

        Implementation of the file object attached to the main document
        or other container.  File attachment has its own UID and has
        a searchable record in the portal catalog.

        This object support upload and download operations and can be used
        as an external source of the main document text.
    """
    _class_version = 1.3

    meta_type   = 'File Attachment'
    portal_type = 'File Attachment'

    security = ClassSecurityInfo()

    __implements__ = ( createFeature('isFileAttachment')
                     , Features.isAttachment
                     , Features.isExternallyEditable
                     , ContentBase.__implements__
                     , File.__implements__
                     )

    if Config.UseExternalEditor:
        _actions = ContentBase._actions + \
            (
                AI(
                    id          = 'external_edit',
                    title       = 'Edit using external editor',
                    icon        = 'external_editor.gif',
                    action      = Expression('string: ${object_url}/externalEdit'),
                    permissions = ( CMFCorePermissions.ModifyPortalContent, ),
                    condition   = Expression( 'python: not object.isLocked()' ),
                    visible     = 0
                ),
            )

    _properties = ContentBase._properties + \
                  File._properties[1:] + \
                  (
                      {'id':'original_filename', 'type':'string'},
                  )

    # default attribute values
    original_filename = None
    _extension = ''

    # access rights of the owner are determined by the parent document
    _owner_role = None

    # overriden by PortalContent in ContentBase
    __len__ = File.__len__

    # for use by the external editor
    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'PUT' )
    PUT = File.PUT

    def __init__( self, id, title, file, content_type='' ):
        """
            Creates a new FileAttachment instance.

            Arguments:

                'id' -- identifier string of the object

                'file' -- either FileUpload object or string data
                          for the file contents

                'title' -- title of the object

                'content_type' -- optional MIME type of the file

        """
        ContentBase.__init__( self, id )

        #full name we get here is already recoded
        self._extension = nt_splitext( id )[-1].lower()
        while self._extension and self._extension[0] == '.':
            self._extension = self._extension[1:]

        File.__init__( self, id, title, file, content_type )

    def _initstate( self, mode ):
        # initialize attributes
        if not ContentBase._initstate( self, mode ): return 0

        if not self.id:
            # < 1.2 used __name__ for id
            self.id = self.__name__

        if type(self._extension) is ListType:
            # < 1.3
            self._extension = self._extension[-1]
            while self._extension and self._extension[0] == '.':
                self._extension = self._extension[1:]

        return 1

    def __nonzero__( self ):
        # used to override __len__
        return 1

    def _setId( self, id ):
        # we need this because File is Item_w__name__
        ContentBase._setId( self, id )
        File._setId( self, id )

    def view( self, REQUEST=None ):
        """
            Implements the default view of the file contents.

            Arguments:

                'REQUEST' -- optional Zope request object

            Result:

                See 'index_html' method description.
        """
        REQUEST = REQUEST or self.REQUEST
        return self.index_html( REQUEST, REQUEST.RESPONSE )

    def index_html( self, REQUEST=None, RESPONSE=None ):
        """
            Returns the contents of the file.

            Sets 'Content-Type' header in the response to the object's
            content type.  Sets value of the 'Content-Disposition' header
            to either 'inline' or 'attachment' accordingly to the file type,
            and a 'filename' parameter to the real name of the file.

            Arguments:

                'REQUEST' -- Zope request object

                'RESPONSE' -- Zope response object

            Result:

                String containing the file data.
        """
        ctype = self.getContentType()
        ctype = ctype and ctype.split('/')[0]
        fname = self.getProperty('original_filename') or self.getId()

        RESPONSE.setHeader( 'Content-Disposition', '%s; filename="%s"; size="%d"' % \
                ( ctype == 'text' and 'inline' or 'attachment', fname, self.getSize() ) )

        return File.index_html( self, REQUEST, RESPONSE )

    security.declareProtected( CMFCorePermissions.View, 'RawBody' )
    def RawBody( self ):
        """
            Returns raw file data.

            Result:

                String (potentially big).
        """
        return str( self )

    security.declareProtected( CMFCorePermissions.View, 'CookedBody' )
    def CookedBody( self, format='text' ):
        """
            Extracts text from the file contents and returns it
            in the requested format.

            Arguments:

                'format' -- optional output format specifier, 'html' and 'text'
                            (used by default) are supported

            Result:

                String respesenting the file text.
        """
        if not self.isTextual():
            return '' # XXX maybe raise error or do smth else?

        text = Converter.convert( str(self), self.getContentType(), format=format )

        if format == 'html':
            # we show document in frame thus we need text inside BODY tag
            text = extractBody( text )
        return text

    security.declareProtected( CMFCorePermissions.View, 'isTextual' )
    def isTextual( self ):
        """
            Checks whether the file contents can be represented as text.

            For example, '*.doc', '*.rtf', '*.html', '*.txt' are considered
            textual.  Depends on the installed document converters.

            Result:

                Boolean value, true if the file is textual.
        """
        return Converter.isConvertible( self.getContentType() )

    security.declareProtected( CMFCorePermissions.View, 'isBroken' )
    def isBroken(self):
        ""
        if Config.EnableFSStorage:
            return self.is_broken()
        return False

    def useActiveView(self):
        """
            Checks whether the file contents can be represented as ActiveX object.

            Result:

                Boolean value

        """
        return self.getContentType() in _activex_types

    def update_data( self, data, content_type=None, size=None, reindex=True ):
        # private method for changing file contents;
        # notifies container document that is should update its text
        # in case this file is used as the text source.
        File.update_data( self, data, content_type, size )

        if reindex:
            self.reindexObject( idxs=['SearchableText'] )

        parent = self.parent()
        if parent is not None and parent.implements('isCompositeDocument'):
            parent._notifyAttachChanged( self.getId() )

    def SearchableText( self ):
        # returns indexable text for the fulltext search
        text = self.getId()
        text += ' ' + self.title
        try:
            text += ' ' + self.CookedBody( format='text' )
        except Converter.ConverterError:
            pass
        return text

    def getIcon( self ):
        """
            Returns the file type sensitive icon.

            Result:

                String.
        """

        return Config.Icon2FileMap.get(self._extension.lower(), 'file.gif')

    def _instance_onClone(self, source, item):
        File.manage_afterClone(self, item)

    def _instance_onMove(self):
        if hasattr(self, '_v_delete_files'):
            del self._v_delete_files

    def _containment_onDelete(self, item, container):
        File.manage_beforeDelete(self, item, container)

InitializeClass( FileAttachment )


def manage_addImage(self, id, file, title='', precondition='', content_type='',
                    REQUEST=None):
    """
    Add a new Image object.

    Creates a new Image object 'id' with the contents of 'file'.
    """

    id=str(id)
    title=str(title)
    content_type=str(content_type)
    precondition=str(precondition)

    id, title = cookId(id, title, file)

    #self=self.this()

    # First, we create the image without data:
    self._setObject(id, ImageAttachment(id,title,'',content_type, precondition))

    # Now we "upload" the data.  By doing this in two steps, we
    # can use a database trick to make the upload more efficient.
    if file:
        self._getOb(id).manage_upload(file)
    if content_type:
        self._getOb(id).content_type=content_type

    if REQUEST is not None:
        try:    url=self.DestinationURL()
        except: url=REQUEST['URL1']
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
    return id


def addFile( self, id=None, file=None, title=None, REQUEST=None, **kw ):
    """
        Handles upload of a new file object and attaches it to the container.

        Arguments:

            'id' -- optional identifier string of the new object;
                    if not given, generated from either 'title'
                    or filename of the FileUpload, or by random
                    if neither is suitable

            'file' -- FileUpload object or string data for the
                      attachment contents

            'title' -- optional title of the object;
                       is set to filename by default

            'REQUEST' -- optional Zope request object

        Result:

            Identifier string of the new attachment object.
    """
    if file is None:
        return None

    self.failIfLocked()

    idx = nidx = 0
    filename = isinstance( file, FileUpload ) and \
               nt_basename( file.filename )   or None
    old_suffix = None

    if not id:
        lang = getToolByName( self, 'portal_membership' ).getLanguage( REQUEST=REQUEST )
        id   = translit_string( filename or title, lang )
        basename = suffix = ''

        if id:
            # replace illegal characters
            id = re.sub( r'^[^a-zA-Z0-9\.]+|[^a-zA-Z0-9-_~\,\.]+', '', id )
            if filename:
                basename, suffix = nt_splitext( id )
                if not basename:
                    id = None
            elif id:
                basename = id
        if not basename:
            nidx = 1
            basename = 'file'

        # place an original filename to the object's id
        # and change it to the sequental number
        while not ( id and self._getOb( id, None ) is None ):
            idx += 1
            id = '%s_%03d%s' % ( basename, idx, suffix )

    basename, suffix = nt_splitext( filename or id )
    suffix = old_suffix or suffix.lower()

    if title is None:
        title = re.sub( r'[\s_]+', ' ', basename.strip() )
        if title and idx > nidx:
            title += ' [%d]' % (idx - nidx)
    if not title:
        title = id

    # Choose the way to add the file and attach it to the document
    if suffix in ['.gif', '.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
#        if Config.UsePILImage:
        if type(file) in [StringType, UnicodeType]:
            file = StringIO( file )

        ctype = ''
        if suffix in ['.tif', '.tiff']:
            ctype = 'image/tiff'

        img = ImageAttachment(id, title=title, file=file, content_type=ctype, \
            engine='PIL', quality=95, timeout=0)
        self._setObject(id, img)

#        else:
#            manage_addImage( self, id, file=file, title=title )
    else:
        # XXX
        self.manage_addProduct['CMFNauTools'].manage_addAttachment( id, file=file, title=title, REQUEST=REQUEST, **kw )

    return id


def initialize( context ):
    # register FileAttachment constructor as a Zope factory
    context.registerClass(
        FileAttachment,
        permission      = CMFCorePermissions.ModifyPortalContent,
        constructors    = ( manage_addAttachmentForm, manage_addAttachment ),
        icon            = 'icons/file_icon.gif',
    )
