import unittest

import Zope
from Acquisition import Implicit

try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.tests.base.testcase import SecurityRequestTest

class DublinCoreTests( SecurityRequestTest ):

    def _makeSite( self ):
        from OFS.Folder import Folder
        site = Folder( 'site' )
        self.root._setObject( 'site', site )
        return self.root._getOb( 'site' )

    def _makeDummyContent( self, **kw ):

        from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

        class DummyContent( Implicit, DefaultDublinCoreImpl ):
            pass

        return DummyContent( **kw )

    def test_interface(self):
        from Products.CMFCore.interfaces.DublinCore \
                import DublinCore as IDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import CatalogableDublinCore as ICatalogableDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import MutableDublinCore as IMutableDublinCore
        from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

        verifyClass(IDublinCore, DefaultDublinCoreImpl)
        verifyClass(ICatalogableDublinCore, DefaultDublinCoreImpl)
        verifyClass(IMutableDublinCore, DefaultDublinCoreImpl)

    def test_publisher_no_metadata_tool( self ):

        site = self._makeSite()
        content = self._makeDummyContent().__of__( site )

        self.assertEqual( content.Publisher(), 'No publisher' )

    def test_publisher_with_metadata_tool( self ):

        PUBLISHER = 'Some Publisher'

        site = self._makeSite()
        site.portal_metadata = DummyMetadataTool( publisher=PUBLISHER )
        content = self._makeDummyContent().__of__( site )

        self.assertEqual( content.Publisher(), PUBLISHER )

class DummyMetadataTool( Implicit ):

    def __init__( self, publisher ):
        self._publisher = publisher

    def getPublisher( self ):

        return self._publisher

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( DublinCoreTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
