"""
$Id: setup_stemmer.py,v 1.5 2004/04/30 10:46:08 vpastukhov Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.5 $'[11:-2]

title = 'Upgrade full-text search index'
version = '2.12'
before_script = 1

from Globals import DTMLFile
from Products.CMFCore.utils import getToolByName
try:
    from Products.TextIndexNG2 import allStemmers
except ImportError:
    allStemmers = None

configuration_form = DTMLFile( 'dtml/setup_stemmer_form', globals() )

def check( context, object ):
    if allStemmers is None:
        return False

    catalog = getToolByName( object, 'portal_catalog' )
    try:
        textindex = catalog._catalog.getIndex('SearchableText')
    except KeyError:
        pass
    else:
        if textindex.meta_type == 'TextIndexNG2':
            return False

    context.script_init[ __name__ ] =  {'all_stemmers': allStemmers(object) }

    return True

def migrate( context, object ):
    script_options = context.script_options[ __name__ ]
    stemmer = object.stemmer = script_options.get('stemmer')

    catalog = getToolByName( object, 'portal_catalog' )
    catalog.delIndex( 'SearchableText' )
    catalog.setupIndexes( idxs=['SearchableText'] )

    context.markForReindex( idxs=['SearchableText'] )
