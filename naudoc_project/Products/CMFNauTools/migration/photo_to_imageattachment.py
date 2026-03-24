"""
$Id: photo_to_imageattachment.py,v 1.5 2004/06/11 12:12:39 vpastukhov Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.5 $'[11:-2]

from Products.CMFNauTools.ImageAttachment import ImageAttachment

title = 'Convert attachments of type Photo to ImageAttachment'
version = '2.12'
classes = ['Products.Photo.Photo.Photo']
strict_classes = 1

def migrate(context, object):
    object = context.container._upgrade( context.name, ImageAttachment )
    object._num_frames = 0
    object._is_TIFF = 0
    object._setPropValue( 'filename', object.getId() )
    object.setupResourceUid()
    object.reindexObject()
