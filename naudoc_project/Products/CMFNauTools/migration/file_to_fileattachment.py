"""
$Id: file_to_fileattachment.py,v 1.2 2004/09/03 04:27:41 ikuleshov Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

from Products.CMFNauTools.File import FileAttachment

title = 'Convert attachments of type File to FileAttachment'
version = '3.2'
classes = ['OFS.Image.File']
strict_classes = 1

def migrate(context, object):
    object = context.container._upgrade( context.name, FileAttachment )
    object._setPropValue( 'filename', object.getId() )
    object.setupResourceUid()
    object.reindexObject()
