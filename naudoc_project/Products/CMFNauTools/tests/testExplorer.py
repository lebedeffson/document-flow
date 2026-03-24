#! /bin/env python2.3
"""

$Id: testExplorer.py,v 1.2 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')

from thread import get_ident
from ZPublisher import Publish
from ZPublisher.BaseRequest import BaseRequest

from Products.Localizer.AcceptLanguage import AcceptLanguage

from Products.CMFNauTools.Explorer import FolderExplorer, getExplorerType
from Products.CMFNauTools.JungleTag import IBasicTree
from Products.CMFNauTools.Utils import getObjectImplements

class ExplorerTests( NauDocTestCase.NauDocTestCase ):

    _remove_naudoc = False
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        #create SESSION in REQUEST
        self.app.__before_publishing_traverse__(self.app, self.app.REQUEST)

        # XXX move to base class
        if hasattr(Publish, '_requests'):
            # Provide Localizer.get_request method with fake request object.
            ident = get_ident()
            Publish._requests[ident] = self.app.REQUEST
        

    def testExplorerCreation(self):
        storage = self.naudoc._getOb('storage')

        ExplorerType = getExplorerType( storage )
        self.assertEquals( ExplorerType, FolderExplorer )

        explorer = ExplorerType( storage, **{} )
        self.assert_( explorer is not None )
        self.assert_( explorer._v_object.REQUEST is not None )

        tree = explorer.tree_index(None)

        self.assert_( getObjectImplements( tree, IBasicTree) )
        self.assertEquals( tree.root_item, storage.getUid() )

        items = tree.get_items( storage.getUid() )
        self.assert_( len(list(items)) >= 2 ) 
        
        content = explorer.content_index( None )
       
        self.assertEquals( content['object'].getUid(), storage.getUid() )

    def beforeTearDown(self):
        ident = get_ident()
        if hasattr(Publish, '_requests') and Publish._requests.has_key(ident):
            Publish._requests[ident].close()
            del Publish._requests[ident]

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(ExplorerTests) )
    return suite

if __name__ == '__main__':
    framework()
