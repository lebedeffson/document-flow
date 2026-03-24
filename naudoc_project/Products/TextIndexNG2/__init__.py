###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

# some ZCatalog monkey patching

import os, sys

package_home = os.path.dirname(__file__)
if not package_home in sys.path:
    sys.path.append(package_home)


def getEntriesFromRegistry(self, id):
    """ get infos from a TXNG registry """

    from Products.TextIndexNG2.Registry import LexiconRegistry
    from Products.TextIndexNG2.Registry import ConverterRegistry
    from Products.TextIndexNG2.Registry import NormalizerRegistry
    from Products.TextIndexNG2.Registry import ParserRegistry
    from Products.TextIndexNG2.Registry import SplitterRegistry
    from Products.TextIndexNG2.Registry import StopwordsRegistry
    from Products.TextIndexNG2.Registry import StorageRegistry

    registry = None 

    try:
        registry = vars()['%sRegistry' % id]
    except:
        import traceback
        traceback.print_exc()
        raise

    keys = registry.allIds()
    keys.sort()
    
    result = []
    for k in keys:
        result.append( (k, registry.getRegisteredObject(k)) ) 

    return result


def allStemmers(self):
    """ return a list of all stemmers """

    import Stemmer

    keys = Stemmer.availableStemmers()
    keys.sort()

    return keys

def allSimilarityAlgorithms(self):
    """ return a list of all similarity algorithms """

    import Similarity

    keys = Similarity.availableAlgorithms()
    keys.sort()
    
    return keys





try:
    import normalizer, Stemmer, Similarity, indexsupport
except ImportError:
    from zLOG import LOG, ERROR
    LOG("TextIndexNG",ERROR,"Import of Python extensions failed")
    


def initialize(context):
    from Products.TextIndexNG2 import TextIndexNG

    manage_addTextIndexNGForm = TextIndexNG.manage_addTextIndexNGForm 
    manage_addTextIndexNG     = TextIndexNG.manage_addTextIndexNG
    
    context.registerClass( 
        TextIndexNG.TextIndexNG,
        permission='Add Pluggable Index', 
        constructors=(manage_addTextIndexNGForm,
        manage_addTextIndexNG),
        icon='www/index.gif',
        visibility=None
        )

    context.registerHelp()
    context.registerHelpTitle("Zope Help")

    from Products.ZCatalog.ZCatalog import ZCatalog
    ZCatalog.getEntriesFromRegistry = getEntriesFromRegistry
    ZCatalog.allSimilarityAlgorithms = allSimilarityAlgorithms
    ZCatalog.allStemmers = allStemmers

