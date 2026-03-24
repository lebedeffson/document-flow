"""
Image attachment class. Supports tiff images with multiple frames.
$Id: ImageAttachment.py,v 1.23 2008/11/21 15:22:05 oevsegneev Exp $
"""
__version__ = '$Revision: 1.23 $'[11:-2]

from zLOG import LOG, DEBUG, TRACE, INFO

import re, os
from cStringIO import StringIO
from ntpath import basename as nt_basename
from types import StringType

from AccessControl import ClassSecurityInfo
from Acquisition import aq_get, aq_parent
from ZPublisher.HTTPRequest import FileUpload

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.Photo import Photo
from Products.Photo.PhotoImage import PhotoImage

import Config, Features
from ActionInformation import ActionInformation as AI
from Features import createFeature
from SimpleObjects import ContentBase
from Utils import InitializeClass

if Config.UsePILImage:
    from PIL import Image

if Config.EnableFSStorage:
    from Products.Photo import ExtPhotoImage
    from Products.ExtFile.ExtImage import ExtImage

    class PhotoImage(ExtPhotoImage.PhotoImage):
        """
            Provides two modifications of ExtFile behaviour:

                1. _get_zodb_path returns our configurable path.

                2. Backup files are not keeped.

        """

        _repository = ['var']

        def _get_zodb_path(self, parent=None):
            portal_id = getToolByName(self, 'portal_url').getPortalObject().getId()
            date = self.aq_parent.created()

            return [portal_id] + map(date.strftime, Config.FSStorageFormat)

        def manage_beforeDelete(self, item, container):
            self._register()
            self._v_delete_files = True

        def manage_upload(self, file = '',REQUEST = None):
            if isinstance(file, StringType):
                # it is broken by ExtPhotoImage
                ExtImage.manage_upload(self, file)
            else:
                self.manage_file_upload(file)

        def _newImage(self, id, file, path):
            img = PhotoImage(id, path=path).__of__(self)
            img.manage_file_upload(file, self._content_type())
            return img

        def _instance_onMove(self):
            if hasattr(self, '_v_delete_files'):
                del self._v_delete_files

        def _finish(self):
            if getattr(self, '_v_delete_files', False):
                for filename in (self._temp_fsname(self.filename),
                                 self._fsname(self.filename)):
                    if os.path.isfile(filename):
                        try: os.remove(filename)
                        except OSError: pass

            else:
                ExtPhotoImage.PhotoImage._finish(self)

class ImageAttachment( ContentBase, Photo ):
    """
        Image which supports tiff images with multiple frames.
    """
    _class_version = 1.0

    meta_type   = 'Image Attachment'
    portal_type = 'Image Attachment'

    security = ClassSecurityInfo()

    __implements__ = ( createFeature('isImageAttachment')
                     , Features.isAttachment
                     , Features.isImage
                     , Features.isExternallyEditable
                     , ContentBase.__implements__
                     , Photo.__implements__
                     )

    # for use by external editor
    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'PUT' )
#    PUT = Photo.PUT

    if Config.UseExternalEditor:
        _actions = \
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
                  Photo._properties + \
                  (
                      {'id':'original_filename', 'type':'string'},
                  )

    # default attribute values
    original_filename = None # XXX: it is used anywhere?

    icon = Photo.icon
    content_type = getContentType = Photo.content_type

    def __init__( self, id, title, file, content_type='', precondition='',
                  store='Image', engine='PIL', quality=75, pregen=0, timeout=0):
        """
            Initializes class instance
        """
        ContentBase.__init__( self, id )
        Photo.__init__(self, id, title, file, content_type, precondition,
                 store, engine, quality, pregen, timeout)
        file.seek(0)
        self._data = file.read()
        self._num_frames = 0
        self._is_TIFF = content_type=='image/tiff'

        #photoconf = self.propertysheets.get('photoconf')
        #photoconf.manage_changeProperties(timeout=3600)
        #photoconf.manage_changeProperties()

        filename = isinstance( file, FileUpload ) and file.filename or id
        self._setPropValue( 'original_filename', nt_basename( filename ) )

        #force given content type
        #if content_type:
        #    self._setPropValue( 'content_type', content_type )

    def getIcon(self):
        """
            Returns the portal-relative icon for this type.
        """
        # TODO: remove this method when factory_type_information with icon
        #       will be defined for this class
        return 'image_icon.gif'

    security.declareProtected( CMFCorePermissions.View, 'isTextual' )
    def isTextual( self ):
        """
            Checks whether the file contents can be represented as text.

            Result:

                Boolean value, always false for images .
        """
        return 0

    security.declareProtected( CMFCorePermissions.View, 'RawBody' )
    def RawBody( self ):
        """
            Returns raw image data.

            Result:

                String (potentially big).
        """
        return str( self._original.data )

    security.declareProtected( CMFCorePermissions.View, 'getFramesNumber' )
    def getFramesNumber(self):
        """
            Returns number of frames in the image.

            Result:

                int
        """
        return self._num_frames

    security.declareProtected(CMFCorePermissions.View, 'isTIFF' )
    def isTIFF(self):
        """
            Returns whether this image is in tiff format.

            Result:

                Boolean.
        """
        return self._is_TIFF

    def index_html(self, REQUEST, RESPONSE, display=None):
        """
            Returns the image data.
        """
        # display may be set from a cookie (?)
        if display and self._displays.has_key(display):
            if not self._isGenerated(display):
                # Generate photo on-the-fly
                if re.match(r'frame\d', display) and not Config.SaveImageFrames and \
                    self.getFramesNumber() > 1:
                    #do not store rendered image
                    return self._getDisplayPhoto(display).index_html(REQUEST, RESPONSE)
                elif not re.match(r'thumbnail_frame\d', display) and not Config.SaveImageDisplays:
                    return self._getDisplayPhoto(display).index_html(REQUEST, RESPONSE)
                self._makeDisplayPhoto(display, 1)
            else:
                timeout = self.propertysheets.get('photoconf').getProperty('timeout')
                if timeout and self._photos[display]._age() > (timeout / 2):
                    self._expireDisplays((display,), timeout)
            # Return resized image
            return self._photos[display].index_html(REQUEST, RESPONSE)

        # Return original image
        return self._original.index_html(REQUEST, RESPONSE)

    security.declareProtected( CMFCorePermissions.View, 'isBroken' )
    def isBroken(self):
        ""
        if Config.EnableFSStorage:
            return self._original.is_broken()
        return False

    def _shouldGenerate(self, display):
        """
            Returns whether display should be generated.
        """
        return Photo._shouldGenerate(self, display) or \
            self.isTIFF() and re.match(r'thumbnail_frame\d+', display) and 1

    def _getDisplayData(self, display):
        """
            Returns raw photo data for given display.

            Changes Photo._getDisplayData() the next way: if self is tiff image
            and display format is "frameXX" or "thumbnail_frameXX", frame number
            XX will be converted to PNG and resized according its settings.

            Arguments:

                'display' -- name of display to use

            Result:

                file object (StringIO).
        """
        engine = self.propertysheets.get('photoconf').getProperty('engine')
        quality = self.propertysheets.get('photoconf').getProperty('quality')
        kwargs = { 'engine': engine, 'quality': quality }

        if Config.UsePILImage and self._is_TIFF:
            #generate PNG frame

            if re.match(r'frame\d+', display) or re.match(r'thumbnail_frame\d+', display):
                try:
                    frameno = int(display.replace('frame', ''))
                except ValueError:
                    frameno = int(display.replace('thumbnail_frame', ''))
            else:
                frameno = 0

            im = Image.open( StringIO(self._original._data()) )

            # fix width & height
            if self.width() != im.size[0]: self._original.width = im.size[0]
            if self.height() != im.size[1]: self._original.height = im.size[1]

            im.seek(0)
            try:
                for frame in range(frameno):
                    im.seek(im.tell()+1)
            except EOFError:
                pass # end of sequence
            
            png_data = StringIO()
            im.save(png_data, 'PNG')

            # creating Photo containing PNG data
            png_data.seek(0)

            kwargs['frame_data'] = png_data

        ( width, height ) = self._displays[display]

        if width == 0 and height == 0:
            width = self.width()
            height = self.height()

        ( width, height ) = self._getAspectRatioSize( width, height )

        return self._resize( display, width, height, **kwargs )

    def _getAspectRatioSize(self, width, height):
        """Return proportional dimensions within desired size."""
        img_width, img_height = (self.width(), self.height())

        if img_width <= width:
            return (img_width, img_height)
        else:
            height = img_height * width / img_width

        return (width, height)

    def _resize(self, display, width, height, engine='PIL', quality=75, frame_data=None):
        """
            Resize and resample photo.

            Arguments:

                'frame_data' -- File object (StringIO). If given, forces to use
                it as image data in place of original image data.

                'display, width, height, engine, quality' -- see Photo._resize for
                more help

            Result: resized image (file object)

            Extends Photo._resize to resize only given frame if needed.
        """
        newimg = StringIO()
        if engine == 'PIL':  # Use PIL
            if frame_data is not None:
                img = Image.open( frame_data )
            else:
                img = Image.open(self._original._PILdata())
            fmt = img.format
            img = img.resize((width, height))
            img.save(newimg, fmt, quality=quality)
        elif engine == 'ImageMagick':  # Use ImageMagick
            #do not convert multi-framed tiffs
            origimg = self._original
            if sys.platform == 'win32':
                from win32pipe import popen2
                imgin, imgout = popen2('convert -quality %s -geometry %sx%s - -'
                                       % (quality, width, height), 'b')
            else:
                from popen2 import popen2
                imgout, imgin = popen2('convert -quality %s -geometry %sx%s - -'
                                       % (quality, width, height))
            imgin.write(origimg._IMdata())
            imgin.close()
            newimg.write(imgout.read())
            imgout.close()

        newimg.seek(0)
        return newimg

    def _instance_onCreate( self ):
        """
            Handle pasting of new photos.
        """
        if hasattr(self, '_original'):
            return

        # Added Photo (vs. imported)
        # See note in PUT()

        self._original = PhotoImage(self.id, self.title, path=self.absolute_url(1))
        self._original.manage_upload( StringIO(self._data), self.content_type() )

        #content_type = self.propertysheets.get('photoconf').getProperty('content_type')
        #if content_type:
        #    self._original.content_type = content_type
        if hasattr(self, '_data') and Config.UsePILImage:
            im = Image.open( StringIO(self._data) )
            try:
                im.seek(0)
            except ValueError:
                #this is gif or something else (one frame only)
                pass
            self._num_frames = 0
            displays = self._displays
#            self._original.width, self._original.height = im.size
            try:
                while 1:
                    #displays["frame%d" % self._num_frames]=im.size
                    displays["frame%d" % self._num_frames]=(944, 944) #resize to fit in page
                    displays["thumbnail_frame%d" % self._num_frames]=(128, 128) #thumbnails for frame
                    im.seek(im.tell()+1)
                    self._num_frames += 1
            except EOFError:
                pass # end of sequence
            self._displays.update(displays)
            self._num_frames += 1

            delattr(self, '_data')
        if self._validImage():
            self._makeDisplayPhotos()

    def _instance_onClone( self, source, item ):
        """
            Prepare photos for cloning.
        """
        Photo.manage_afterClone( self, item )

    def _instance_onMove(self):
        if Config.EnableFSStorage:
            self._original._instance_onMove()
            for photo in getattr(self, '_photos', {}).values():
                photo._instance_onMove()

    def _containment_onAdd( self, item, container ):
        self._original.manage_afterAdd( item, container )
        for photo in getattr(self, '_photos', {}).values():
            photo.manage_afterAdd( item, container )

    def _containment_onDelete( self, item, container ):
        Photo.manage_beforeDelete( self, item, container )

    def _getDisplayPhoto(self, display):
        """
            Overrides Photo._getDisplayPhoto
        """
        image = Photo._getDisplayPhoto( self, display )
        if Config.EnableFSStorage:
            return image.aq_base
        return image

InitializeClass( ImageAttachment )
