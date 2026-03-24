#! /bin/env python2.3
"""
Tests for absolute_url and relative_url.

$Id: testURLs.py,v 1.1 2005/12/09 15:12:02 vsafronovich Exp $
$Editor: vsafronovich $
"""
__version__='$Revision: 1.1 $'[11:-2]

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase

from Zope2 import zpublisher_validated_hook

ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('TextIndexNG2')

class URLsTests( NauDocTestCase.NauDocTestCase ):

    _remove_naudoc = False
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        storage = self.naudoc.storage
        storage.invokeFactory( type_name='HTMLDocument'
                             , id='test', title='test'
                             , description='test description'
                             , category='Document'
                             )
        doc = storage['test']
        doc.createVersion( doc.getVersion().getId() )

        get_transaction().commit()

    def testAbsoluteURLs(self):
        naudoc = self.naudoc
        folder = naudoc.storage
        tool = naudoc.portal_url
        doc = folder.test
        ver1 = doc.getVersion()
        self.assertEquals( naudoc.absolute_url(), 'http://nohost/%s' % self.naudoc_id )
        self.assertEquals( naudoc.absolute_url(1), self.naudoc_id )


        self.assertEquals( folder.absolute_url()
                         , 'http://nohost/%s/%s'% (self.naudoc_id,folder.getId() ) )
        self.assertEquals( folder.absolute_url(1)
                         , '%s/%s' % (self.naudoc_id,folder.getId() ))

        self.assertEquals( naudoc.absolute_url(), tool() )
        self.assertEquals( tool.absolute_url()
                         , 'http://nohost/%s/%s'% (self.naudoc_id, tool.getId() ) )
        self.assertEquals( tool.absolute_url(1)
                         , '%s/%s' % (self.naudoc_id, tool.getId() ))

        self.assertEquals( doc.absolute_url() 
                         , '%s/%s'% (folder.absolute_url(), doc.getId() ) )

        self.assertEquals( ver1.absolute_url()
                         , '%s/version/%s'% (doc.absolute_url(), ver1.getId() ) )

    def testRelativeURLs(self):
        naudoc = self.naudoc
        folder = naudoc.storage
        tool = naudoc.portal_url
        doc = folder.test
        ver1 = doc.getVersion()
        ver2 = doc.getVersion( doc.createVersion( ver1.getId() ) )

        REQUEST = self.app.REQUEST
        REQUEST['PARENTS'] = [self.app]
        REQUEST['PUBLISHED'] = naudoc
        #REQUEST.traverse( naudoc.physical_path()
        #                , validated_hook=zpublisher_validated_hook )

        self.assertRelative( naudoc, '.' )
        self.assertRelative( folder, '%(object_id)s' )
        self.assertRelative( tool, '%(object_id)s' )
        self.assertRelative( doc, 'storage/%(object_id)s')
        self.assertRelative( ver1, 'storage/%(object_id)s')
        self.assertRelative( ver2, 'storage/%(object_id)s/%(version_id)s')

        # changed published info
        REQUEST.other.clear()
        REQUEST['PUBLISHED'] = folder
        REQUEST.environ['PATH_INFO'] = folder.absolute_url(1) + '/'
        #REQUEST.traverse( folder.physical_path()
        #                , validated_hook=zpublisher_validated_hook )

        kw = {}

        self.assertRelative( naudoc, '..' )
        self.assertRelative( folder, '.' )
        self.assertRelative( tool, '../%(object_id)s', **kw )
        self.assertRelative( doc, '%(object_id)s', **kw)
        self.assertRelative( ver1, '%(object_id)s', **kw)
        #self.assertRelative( ver2, '%(object_id)s/%(version_id)s')


        kw['action'] = 'foo'

        self.assertRelative( naudoc, '../%(action)s', **kw)
        self.assertRelative( folder, './%(action)s', **kw )
        self.assertRelative( tool, '../%(object_id)s/%(action)s', **kw)
        self.assertRelative( doc, '%(object_id)s/%(action)s', **kw)
        self.assertRelative( ver1, '%(object_id)s/%(action)s', **kw)
        #self.assertRelative( ver2, '%(object_id)s/%(version_id)s/%(action)s', **kw)

        kw['frame'] = 'inFrame'

        self.assertRelative( naudoc, '../%(frame)s?link=%(action)s', **kw )
        self.assertRelative( folder, './%(frame)s?link=%(action)s', **kw )
        self.assertRelative( tool, '../%(object_id)s/%(frame)s?link=%(action)s', **kw )
        self.assertRelative( doc, '%(object_id)s/%(frame)s?link=%(action)s', **kw )
        self.assertRelative( ver1, '%(object_id)s/%(frame)s?link=%(action)s', **kw )
        #self.assertRelative( ver2, '%(object_id)s/%(version_id)s/%(frame)s?link=%(action)s', **kw )

        # TODO: test version`s 2 urls

    def assertRelative( self, object, msg, **kw ):
        url = object.relative_url(**kw)

        if object.implements('isVersion'):
            kw.setdefault( 'object_id', object.getVersionable().getId())
            kw.setdefault( 'version_id', 'version/%s'%object.getId())
        else:
            kw.setdefault( 'object_id', object.getId() )

        self.assertEquals( url, msg % kw )

    def beforeTearDown(self):
        self.naudoc.storage.deleteObjects( ['test'] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(URLsTests))
    return suite

if __name__ == '__main__':
    framework()
