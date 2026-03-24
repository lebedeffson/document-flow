"""
$Id $
$Editor: ypetrov $
"""
__version__ = '$Revision $'[11:-2]

classes = ['Products.CMFNauTools.File.FileAttachment',
           'Products.CMFNauTools.ImageAttachment.ImageAttachment']
title = 'Setup FS storage for attachments'

from types import DictType

from Products.CMFNauTools import Config
from Products.CMFNauTools.ImageAttachment import PhotoImage, ImageAttachment

def _change_class(object, name, klass):
    mapping = isinstance(object, DictType)

    if mapping:
        old = object[name]
    else:
        old = getattr(object, name)

##    print old.__dict__
##    print old.__class__, klass

    if old.__class__ == klass:
        return old

    new = klass.__basicnew__()
    new.__dict__.update(old.__dict__)

    if mapping:
        object[name] = new
        return object[name]
    else:
        setattr(object, name, new)
        return getattr(object, name)

def _has_data(object):
    if isinstance(object, ImageAttachment):
        object = object._original

    return hasattr(object, 'data')

if Config.EnableFSStorage:

    def check(context, object):
        return _has_data(object)

    def _migrate(fileobj, image_url = None):
        if hasattr(fileobj, 'filename'):
            # 'filename' renamed to 'original_filename' to avoid conflicts
            # with ExtFile
            fileobj.original_filename = fileobj.filename

        if image_url is not None:
            # migrating ImageAttachment
            fileobj._path = image_url
            fileobj.prev_filename = []
            fileobj.prev_content_type = ''
            fileobj.prev_ratio = 1
            fileobj.has_preview = 0

        fileobj.id = fileobj.__dict__['__name__']
        fileobj.filename = []
        fileobj.manage_upload( str(fileobj.data), None )

        for attr in 'data', 'size', 'width', 'height', 'precondition', \
                    '__name__':
            if fileobj.__dict__.has_key(attr):
                delattr(fileobj, attr)

    def migrate(context, object):
        object = object.aq_base.__of__(context.portal)
        if isinstance(object, ImageAttachment):
            #print '-->ok'
            # migrating ImageAttachment
            url = object.absolute_url(1)

            fileobj = _change_class(object, '_original', PhotoImage)
            _migrate(fileobj, url)

            if object._photos:
                # XXX direct migration of displays have problem -- their __dict__s are empty
                #     so we reset cache and them should be regenerated on demand
                object._photos = {}

##            for id in object._photos.keys():
##                print 'photo', id
##                fileobj = _change_class(object._photos, id, PhotoImage)
##                _migrate(fileobj, url)
##
##            # persistence magic
##            if object._photos: object._photos = object._photos

        else:
            # migrating FileAttachment
            _migrate(object)

else:

    import os.path
    from types import ListType

    def check(context, object):
        #print '-->checkX', _has_data(object)
        return not _has_data(object)

    def _get_path(fileobj):
        path = [INSTANCE_HOME, 'var']

        if isinstance(fileobj.filename, ListType):
            path.extend(fileobj.filename)
        else:
            path.append(fileobj.filename)

        return os.path.join(*path)

    def _migrate(fileobj):
        if fileobj.__dict__.has_key('id'):
            fileobj.__name__ = fileobj.__dict__['id']
        else:
            fileobj.__name__ = fileobj.getId()

        path = _get_path(fileobj)
        if os.path.isfile(path):
            file = open(path, 'rb')
            fileobj.manage_upload(file, None)
            file.close()
            os.remove(path)
        else:
            fileobj.manage_upload('', None)

        for attr in 'filename', 'use_download_permission_check', 'descr', \
                    'redirect_default_view', 'prev_filename', \
                    'prev_content_type', 'prev_ratio', 'has_preview', \
                    '_path', 'id':
            if fileobj.__dict__.has_key(attr):
                delattr(fileobj, attr)

    def migrate(context, object):
        if isinstance(object, ImageAttachment):
            # migrating ImageAttachment
            fileobj = _change_class(object, '_original', PhotoImage)
            _migrate(fileobj)

            if object._photos:
                # XXX
                object._photos = {}

##            for id in object._photos.keys():
##                fileobj = _change_class(object._photos, id, PhotoImage)
##                _migrate(fileobj)
##
##            # persistence magic
##            if object._photos: object._photos = object._photos

        else:
            # migrating FileAttachment
            _migrate(object)
