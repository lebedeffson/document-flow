#! /bin/env python2.3
"""
Create and destroy NauDoc Site portal.

$Id: testSite.py,v 1.3 2005/12/09 15:53:42 vsafronovich Exp $
"""
__version__='$Revision: 1.3 $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import transaction
import NauDocTestCase
from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class SiteCreationTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0

    def testSiteCreation(self):
        storage = self.naudoc.storage
 
        publisher = self.naudoc.portal_publisher
 
        repository = publisher.get_repository()
        skins = publisher.soft_links

        storage.manage_addProduct['CMFNauTools'].\
                manage_addSiteContainer( id='test_site_id'
                                       , title='Test_site'
                                       , repository_url=repository
                                       , skin_links=skins
                                       , skin_id='naumen_ru_v2'
                                       )

        get_transaction().commit()

        site = storage._getOb('test_site_id')
  
        self.assert_(site.hasObject('storage'))
        self.assert_(site.hasObject('custom'))
        self.assert_(site.hasObject('images'))
        
        self.assert_(site._getOb('custom').objectIds() > 0)
        self.assert_(site._getOb('images').objectIds() > 0)

        self.assert_(site.getExternalRoot() is not None )

        # Check that Publisher EP exists and set up properly
        esite = site.getExternalRoot()
        assert( hasattr(esite, 'go') )
        publisherEP = esite['go']
        self.assertEquals( publisherEP.meta_type, 'Publisher Entry Point' )
        self.assertEquals( publisherEP.internal, '/'.join(site.getPhysicalPath()) + '/storage' )

    def beforeTearDown(self):
        #remove folders
        self.naudoc.storage.deleteObjects( ['test_site_id'] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class SiteTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0
   
    def afterSetUp(self):
        storage = self.naudoc.storage
 
        publisher = self.naudoc.portal_publisher
 
        repository = publisher.get_repository()
        skins = publisher.soft_links

        storage.manage_addProduct['CMFNauTools'].\
                manage_addSiteContainer( id='test_site_id'
                                       , title='Test_site'
                                       , repository_url=repository
                                       , skin_links=skins
                                       , skin_id='naumen_ru_v2'
                                       )

        get_transaction().commit()

        self.site = storage.test_site_id

    def testPublication(self):
        external = self.naudoc.external
        # Verify external site creation

        self.site.manage_addProduct['CMFNauTools'].addHTMLDocument('public_html', category='SimplePublication')
        site_ex  = self.site.getExternalRoot()
        REQUEST = self.app.REQUEST
        REQUEST['traverse_subpath'] = [self.naudoc.getId(), 'external', self.site.getId(), 'public_html']
        self.assert_( site_ex.go(REQUEST) )

    def test_listPublications(self):
        self.site.storage.\
               manage_addProduct['CMFNauTools'].addHTMLDocument('sample_html'
                                                               , title='Sample HTML'
                                                               , category='SimplePublication')

        sample_html = self.site.storage.sample_html

        from Products.CMFCore.utils import getToolByName

        workflow = getToolByName(self.naudoc, 'portal_workflow')
        workflow.doActionFor( sample_html, 'publish', comment='' )

        site_ex  = self.site.getExternalRoot()
        results = site_ex.go.publishedItems()

        self.assertEquals( len(results), 1)

        self.assertEquals( results[0]['Title'], 'Sample HTML')

    def test_listSubFolders(self):

        self.site.storage.manage_addProduct['CMFNauTools'].manage_addHeading('heading1')
        self.site.storage.heading1.manage_addProduct['CMFNauTools'].manage_addHeading('heading2')

        site_ex  = self.site.getExternalRoot()
        results = site_ex.go.listSubFolders('heading1')
        self.failIf( results )

        self.site.storage.heading1.heading2.manage_addProduct['CMFNauTools']\
                 .addHTMLDocument('sample_html', title='Sample HTML', category='SimplePublication')

        sample_html = self.site.storage.heading1.heading2.sample_html

        from Products.CMFCore.utils import getToolByName

        workflow = getToolByName(self.site, 'portal_workflow')
        workflow.doActionFor(sample_html, 'publish', comment='')

        results = site_ex.go.listSubFolders('heading1')
        self.assertEquals(results,
                          [ { 'id': 'heading2'
                            , 'absolute_url': '/' + site_ex.absolute_url(1) + '/go/heading1/heading2'
                            , 'hasMainPage' : False
                            ,        'title': ''
                            ,    'meta_type': 'Heading'
                            ,  'Description': ''
                            ,  'title_or_id': 'heading2'
                            }
                          ]
              )

    def test_getParents(self):
        site = self.site
        site.storage.manage_addProduct['CMFNauTools'].manage_addHeading('heading1')
        site.storage.heading1.manage_addProduct['CMFNauTools'].manage_addHeading('heading2')
        site.storage.heading1.heading2.manage_addProduct['CMFNauTools']\
                    .addHTMLDocument('sample_html', title='Sample HTML', category='SimplePublication')
        sample_html = site.storage.heading1.heading2.sample_html

        site_ex  = self.site.getExternalRoot()

        self.assertEquals(sample_html.external_url()
                         , '/' + site_ex.absolute_url(1) + '/go/heading1/heading2/sample_html')

        from Products.CMFCore.utils import getToolByName

        workflow = getToolByName(self.site, 'portal_workflow')
        workflow.doActionFor(sample_html, 'publish', comment='')

        results = site_ex.go.getParents(['heading1', 'heading2'])
        self.assertEquals(results,
                          [{ 'id': 'heading2'
                           , 'absolute_url': '/' + site_ex.absolute_url(1) + '/go/heading1/heading2'
                           ,        'title': ''
                           ,    'meta_type': 'Heading'
                           ,  'Description': ''
                           ,  'title_or_id': 'heading2'
                          }]
              )

    def beforeTearDown(self):
        del self.site

        #remove folders
        self.naudoc.storage.deleteObjects( ['test_site_id'] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(SiteCreationTests) )
    suite.addTest( makeSuite(SiteTests) )
    return suite

if __name__ == '__main__':
    framework()
