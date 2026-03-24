#! /bin/env python2.3
"""

$Id: testLinks.py,v 1.2 2005/12/09 15:40:59 vsafronovich Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase

ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('TextIndexNG2')

from Products.CMFNauTools.Exceptions import SimpleError

class DocumentLinkToolTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = False

    def afterSetUp(self):

        # create Heading:
        
        self.naudoc.manage_addProduct['CMFNauTools'].manage_addHeading('topic1', title='topic 1')

        self.assert_(self.naudoc.topic1, 'Heading \'topic1\' not created')
        self.hd = self.naudoc.topic1

        self.pl = self.naudoc.portal_links

        # create 2 HTML documents in heading:
        self.hd.manage_addProduct['CMFNauTools'].addHTMLDocument('doc1'
                                                                , title='t1'
                                                                , description='d1'
                                                                , text='This is doc1'
                                                                , category='Document')

        self.hd.manage_addProduct['CMFNauTools'].addHTMLDocument('doc2'
                                                                , title='t2'
                                                                , description='d2'
                                                                , text='This is doc2'
                                                                , category='Document')

        self.doc1 = self.hd.doc1
        self.doc2 = self.hd.doc2

        get_transaction().commit()

    def testlistRelations(self):
        rels = self.pl.listRelations()
        self.assert_( rels, 'listRelations() returned empty relations.')

    def testRestrictedLink(self):
        # construct REQUEST
        self.app.REQUEST['source_uid']= self.doc1.nd_uid
        self.app.REQUEST['target_uid'] = self.doc2.nd_uid
        self.app.REQUEST['relation']= 'reference'

        # test goes here
        result = self.pl.restrictedLink( REQUEST=self.app.REQUEST )
        self.assert_( result, 'Error creating link: '+result)

        res = self.pl.searchResults(id=result)
        self.assert_(res, 'Link not found in portal_links.')
        link = res[0].getObject()

        self.assertEqual(link.source_uid, self.doc1.nd_uid, 'Invalid source_uid')
        self.assertEqual(link.target_uid, self.doc2.nd_uid, 'Invalid dest_uid')
        self.assertEqual(link.getSourceMetadata(name='Title'), self.doc1.Title()
                        , 'Invalid source_title')
        self.assertEqual(link.getTargetMetadata(name='Title'), self.doc2.Title()
                        , 'Invalid dest_title')

        # test that only one link between 2 documents may be created
        self.assertRaises( SimpleError, lambda *ignore: self.pl.restrictedLink( self.app.REQUEST )
                         , 'Link must not be created')


    def test_createLink(self):
        link = self.pl.createLink(self.doc1, self.doc2, 'reference')

        res = self.pl.searchResults(id=link.getId())
        self.assert_(res, 'Link not found in portal_links.')
        self.assertEqual(link, res[0].getObject())

        self.assertEqual(link.relation, 'reference', 'Invalid relation type')
        self.assertEqual(str(link.source_uid), self.doc1.nd_uid, 'Invalid source_uid')
        self.assertEqual(str(link.target_uid), self.doc2.nd_uid, 'Invalid dest_uid')
        return link.getId()

    def test_removeLink(self):
        #create link
        link_id = self.test_createLink()

        self.pl.removeLink(link_id)

        res = self.pl.searchResults(id=link_id)
        self.failIf(res, 'Link still exists in portal_links in catalog.')

        res = self.pl.objectIds()
        self.failIf( link_id in res, 'Link still exists in portal_links.')

    def testRemoveLinks(self):
        #create link
        link_id = self.test_createLink()

        self.app.REQUEST['remove_links'] = [link_id]
        result = self.pl.removeLinks( REQUEST=self.app.REQUEST )
        #self.assert_(result.find('success')+1, 'Error removing links: '+result)

        res = self.pl.searchResults(id=link_id)
        self.failIf(res, 'Link still exists in portal_links in catalog.')

        res = self.pl.objectIds()
        self.failIf( link_id in res, 'Link still exists in portal_links.')

    def testRemoveBoundLinks(self):
        link_id = self.test_createLink()
        self.pl.removeBoundLinks(self.hd)

        res = self.pl.searchResults(id=link_id)
        self.assert_(res, 'Link not found in portal_links.')
        res = res[0]

        self.assertEqual(res.target_removed, 0, 'Link not marked as \'destination removed\'')
        self.assert_(res.target_uid is not None, 'Links\' dest_uid is not None')

        self.pl.removeBoundLinks(self.doc1)

        res = self.pl.searchResults(id=link_id)
        self.failIf(res, 'Link not removed from portal_links.')

    def beforeTearDown(self):
        # this must removed bound links
        self.naudoc.manage_delObjects(['topic1'])
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown(self)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(DocumentLinkToolTests) )
    return suite

if __name__ == '__main__':
    framework()

