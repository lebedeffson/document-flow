"""
$Id: setup_fckeditor.py,v 1.3 2005/08/21 13:34:06 vsafronovich Exp $
$Editor: ypetrov $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFNauTools.Utils import makepath
version = '3.3.1.0'

title = 'Setup FCKEditor directory view'

def check(context, object):
    return not hasattr(object, 'fckeditor')

def migrate(context, object):
    createDirectoryView(object, makepath('fckeditor'))
