"""
$Id: update_msg.py,v 1.7 2005/10/19 09:55:33 vsafronovich Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

title = 'Update portal messages catalog'
before_script = 1

from Products.CMFCore.utils import getToolByName

from Products.CMFNauTools import Config
from Products.CMFNauTools.Utils import joinpath

def migrate(context, object):
    langs = Config.Languages

    msgcat = getToolByName( object, 'msg' )
    path = joinpath( context.product_root, 'locale' )

    for lang, info in langs.items():
        charset = info['python_charset'].upper()
        msgcat.update_po_header( lang, '', '', '', charset )

        # import PO file into the Message Catalog
        try:
            file = open( joinpath( path, '%s.po' % lang ), 'rt' )
        except IOError:
            pass
        else:
            try:
                msgcat.manage_import( lang, file )
            finally:
                file.close()

        # import categories PO file into the Message Catalog
        try:
            file = open( joinpath( path, 'categories-%s.po' % lang ), 'rt' )
        except IOError:
            pass
        else:
            try:
                msgcat.manage_import( lang, file )
            finally:
                file.close()

        # fix empty string (just in case...)
        msgcat.manage_editLS( '', (lang, '') )
