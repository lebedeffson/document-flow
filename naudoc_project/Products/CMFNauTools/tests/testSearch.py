"""
Search a document by text, category and category attribute.

$Id: testSearch.py,v 1.3 2006/03/16 10:48:07 ynovokreschenov Exp $
"""
__version__='$ $'[11:-2]

import os, sys, random
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.SearchProfile import SearchQuery
from DateTime import DateTime

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class SearchFunctionalTests(NauDocTestCase.NauFunctionalTestCase):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        #create SESSION in REQUEST
        self.app.__before_publishing_traverse__(self.app, self.app.REQUEST)

        folder = self.naudoc.storage
        i = 1
        id="D%s" %i
        title="D%s" %i
        folder.invokeFactory( type_name='HTMLDocument'
                             ,id=id
                             ,title=title
                             ,description='test description'
                             ,category='NormativeDocument'
                            )
        doc = folder._getOb( id )
        doc.setCategoryAttribute( 'RevokeDocNo', 'test' )
        i = 2
        id="D%s" %i
        title="D%s" %i
        folder.invokeFactory( type_name='HTMLDocument'
                             ,id=id
                             ,title=title
                             ,description='test description'
                             ,category='Directive'
                            )
        doc = folder._getOb( id )
        #doc.setCategoryAttribute( 'RevokeDocNo', 'test' )
        get_transaction().commit()

    def testSearchText(self):
        REQUEST = self.app.REQUEST
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')

        query    = SearchQuery()
        query_id = query.getId()

        query.implements = ['isHTMLDocument']
        query.scope = 'global'
        query.text = 'D1'

        REQUEST.SESSION.set(( 'search',query_id ), query)

        browser_id = REQUEST.SESSION.getBrowserIdManager().getBrowserId()

        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        # removing substring like 'Items found: 1. Query: "D2"' from response
        s = str(response.getBody()).find(query.text)
        resp = str(response.getBody())[s+len(query.text):]
        
        self.assert_(query.text in resp)
        self.assert_('D2' not in str(response.getBody()))

        #query.text = ''
        #query.category = None
        #query.attributes = {}
    
    def testSearchCategory(self):
        REQUEST = self.app.REQUEST
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')

        query    = SearchQuery()
        query_id = query.getId()

        query.implements = ['isHTMLDocument']
        query.scope = 'global'
        query.category = ['NormativeDocument']

        REQUEST.SESSION.set(( 'search',query_id ), query)

        browser_id = REQUEST.SESSION.getBrowserIdManager().getBrowserId()

        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        self.assert_('D1' in str(response.getBody()))
        self.assert_('D2' not in str(response.getBody()))
        
    def testSearchAttributes(self):
        REQUEST = self.app.REQUEST
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')

        query    = SearchQuery()
        query_id = query.getId()

        query.implements = ['isHTMLDocument']
        query.scope = 'global'

        attribute = {}
        attribute['query'] = 'test'
        attribute['attributes'] = [ 'NormativeDocument/RevokeDocNo' ]
        query.attributes = { 'query': [attribute], 'operator': 'and'}

        REQUEST.SESSION.set(( 'search',query_id ), query)

        browser_id = REQUEST.SESSION.getBrowserIdManager().getBrowserId()

        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        self.assert_('D1' in str(response.getBody()))
        self.assert_('D2' not in str(response.getBody()))
        
    def beforeTearDown(self):
        folder = self.naudoc.storage
        #if folder._getOb('D1', None):
        folder.deleteObjects(['D1', 'D2'])
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class SearchFormsTests(NauDocTestCase.NauFunctionalTestCase):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        self.app.__before_publishing_traverse__(self.app, self.app.REQUEST)

        folder = self.naudoc.storage.members
        id = 'D1'
        title = id
        folder.invokeFactory( type_name='HTMLDocument'
                             ,id=id
                             ,title=title
                             ,description='description1'
                             ,category='NormativeDocument'
                            )
        doc = folder._getOb( id )
        #doc.setCategoryAttribute( 'RevokeDocNo', 'test' )

        id = 'D2'
        title = id
        folder.invokeFactory( type_name='DTMLDocument'
                             ,id=id
                             ,title=title
                             ,description='description2'
                             ,category='SimpleDocument'
                            )
        doc = folder._getOb( id )
        id = 'D3'
        title = id
        folder.invokeFactory( type_name='HTMLDocument'
                             ,id=id
                             ,title=title
                             ,description='description3'
                             ,category='Directive'
                            )
        doc = folder._getOb( id )
        get_transaction().commit()
    
    def testSearchText(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')

        # testing: 'text'
        path = '/%s/search_query' % self.naudoc.absolute_url(1)
        extra = { 'category':'any',
                  'search':True,
                  'oid':'',
                  'description':'',
                  'title':'',
                  'text':'D2',
                  'ctrl_attributes_trigger':True,
                  'scope_value':'global',
                  'standard_trigger':True,
                  'created_till':None,
                  'special_trigger':None,
                  'scope_trigger':False,
                  'created_from':None,
                  'otype':'any',
                  'objects':[''],
                  'location':self.naudoc.absolute_url(1),
                  'batch_length':10,
                  'normative_trigger':None,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # getting _ZopeId from response
        s = str(response).find('_ZopeId="')+len('_ZopeId="')
        browser_id = str(response)[s:s+19]

        # getting query_id from response
        s = str(response).find('query_id%3D')+len('query_id%3D')
        query_id = str(response)[s:s+9]

        REQUEST = self.app.REQUEST
        namesp = REQUEST.SESSION.getBrowserIdManager().getBrowserIdNamespaces()
        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(['form'])
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
        
        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        # removing substring like 'Items found: 1. Query: "D2"' from response
        s = str(response.getBody()).find(extra['text'])
        resp = str(response.getBody())[s+len(extra['text']):]

        #f = open('1.htm', 'w')
        #f.write(str(response))
        #f.close()
        
        self.assert_(extra['text'] in resp)
        self.assert_('D1' not in str(response.getBody()))
        self.assert_('D3' not in str(response.getBody()))

        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(list(namesp))
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
    
    def testSearchObjectCategory(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        
        # testing: 'category' of HTMLDocument (should be found a D3 document only)
        path = '/%s/search_query' % self.naudoc.absolute_url(1)
        extra = { 'category':'Directive',
                  'search':True,
                  'oid':'',
                  'description':'',
                  'title':'',
                  'text':'',
                  'ctrl_attributes_trigger':True,
                  'scope_value':'global',
                  'standard_trigger':True,
                  'created_till':None,
                  'special_trigger':None,
                  'scope_trigger':False,
                  'created_from':None,
                  'otype':'HTMLDocument',
                  'objects':[''],
                  'location':self.naudoc.absolute_url(1),
                  'state':{'Directive':'any'},
                  'batch_length':10,
                  'normative_trigger':None,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # getting _ZopeId from response
        s = str(response).find('_ZopeId="')+len('_ZopeId="')
        browser_id = str(response)[s:s+19]

        # getting query_id from response
        s = str(response).find('query_id%3D')+len('query_id%3D')
        query_id = str(response)[s:s+9]

        REQUEST = self.app.REQUEST
        namesp = REQUEST.SESSION.getBrowserIdManager().getBrowserIdNamespaces()
        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(['form'])
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
        
        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        #f = open('3.htm', 'w')
        #f.write(str(response))
        #f.close()
        
        self.assert_('D3' in str(response.getBody()))
        self.assert_('D1' not in str(response.getBody()))
        self.assert_('D2' not in str(response.getBody()))
        
        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(list(namesp))
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
    
    def testSearchOid(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        
        # testing: 'oid' (should be found a D1 document only)
        path = '/%s/search_query' % self.naudoc.absolute_url(1)
        extra = { 'category':'any',
                  'search':True,
                  'oid':'D1',
                  'description':'',
                  'title':'',
                  'text':'',
                  'ctrl_attributes_trigger':True,
                  'scope_value':'global',
                  'standard_trigger':True,
                  'created_till':None,
                  'special_trigger':None,
                  'scope_trigger':False,
                  'created_from':None,
                  'otype':'any',
                  'objects':[''],
                  'location':self.naudoc.absolute_url(1),
                  'batch_length':10,
                  'normative_trigger':None,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # getting _ZopeId from response
        s = str(response).find('_ZopeId="')+len('_ZopeId="')
        browser_id = str(response)[s:s+19]

        # getting query_id from response
        s = str(response).find('query_id%3D')+len('query_id%3D')
        query_id = str(response)[s:s+9]

        REQUEST = self.app.REQUEST
        namesp = REQUEST.SESSION.getBrowserIdManager().getBrowserIdNamespaces()
        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(['form'])
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
        
        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        #f = open('4.htm', 'w')
        #f.write(str(response))
        #f.close()

        self.assert_('D1' in str(response.getBody()))
        self.assert_('D2' not in str(response.getBody()))
        self.assert_('D3' not in str(response.getBody()))   

        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(list(namesp))
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
    
    def testSearchDescription(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        
        # testing: 'oid' (should be found a D1 document only)
        path = '/%s/search_query' % self.naudoc.absolute_url(1)
        extra = { 'category':'any',
                  'search':True,
                  'oid':'',
                  'description':'description1',
                  'title':'',
                  'text':'',
                  'ctrl_attributes_trigger':True,
                  'scope_value':'global',
                  'standard_trigger':True,
                  'created_till':None,
                  'special_trigger':None,
                  'scope_trigger':False,
                  'created_from':None,
                  'otype':'any',
                  'objects':[''],
                  'location':self.naudoc.absolute_url(1),
                  'batch_length':10,
                  'normative_trigger':None,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # getting _ZopeId from response
        s = str(response).find('_ZopeId="')+len('_ZopeId="')
        browser_id = str(response)[s:s+19]

        # getting query_id from response
        s = str(response).find('query_id%3D')+len('query_id%3D')
        query_id = str(response)[s:s+9]

        REQUEST = self.app.REQUEST
        namesp = REQUEST.SESSION.getBrowserIdManager().getBrowserIdNamespaces()
        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(['form'])
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
        
        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        #f = open('5.htm', 'w')
        #f.write(str(response))
        #f.close()

        self.assert_('D1' in str(response.getBody()))
        self.assert_('D2' not in str(response.getBody()))
        self.assert_('D3' not in str(response.getBody())) 

        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(list(namesp))
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
        
    def testSearchTitle(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        
        # testing: 'oid' (should be found a D1 document only)
        path = '/%s/search_query' % self.naudoc.absolute_url(1)
        extra = { 'category':'any',
                  'search':True,
                  'oid':'',
                  'description':'',
                  'title':'D1',
                  'text':'',
                  'ctrl_attributes_trigger':True,
                  'scope_value':'global',
                  'standard_trigger':True,
                  'created_till':None,
                  'special_trigger':None,
                  'scope_trigger':False,
                  'created_from':None,
                  'otype':'any',
                  'objects':[''],
                  'location':self.naudoc.absolute_url(1),
                  'batch_length':10,
                  'normative_trigger':None,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # getting _ZopeId from response
        s = str(response).find('_ZopeId="')+len('_ZopeId="')
        browser_id = str(response)[s:s+19]

        # getting query_id from response
        s = str(response).find('query_id%3D')+len('query_id%3D')
        query_id = str(response)[s:s+9]

        REQUEST = self.app.REQUEST
        namesp = REQUEST.SESSION.getBrowserIdManager().getBrowserIdNamespaces()
        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(['form'])
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()

        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        #f = open('6.htm', 'w')
        #f.write(str(response))
        #f.close()

        self.assert_('D1' in str(response.getBody()))
        self.assert_('D2' not in str(response.getBody()))
        self.assert_('D3' not in str(response.getBody()))

        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(list(namesp))
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
    
    def testSearchTimeCreated(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        
        # testing: 'oid' (should be found a D1 document only)
        path = '/%s/search_query' % self.naudoc.absolute_url(1)
        extra = { 'category':'any',
                  'search':True,
                  'oid':'',
                  'description':'',
                  'title':'',
                  'text':'',
                  'ctrl_attributes_trigger':True,
                  'scope_value':'recursive',
                  'standard_trigger':True,
                  'created_till':DateTime(),
                  'special_trigger':None,
                  'scope_trigger':False,
                  'created_from':DateTime(),
                  'otype':'any',
                  'objects':[''],
                  'location':self.naudoc.absolute_url(1),
                  'batch_length':1000,
                  'normative_trigger':None,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # getting _ZopeId from response
        s = str(response).find('_ZopeId="')+len('_ZopeId="')
        browser_id = str(response)[s:s+19]

        # getting query_id from response
        s = str(response).find('query_id%3D')+len('query_id%3D')
        query_id = str(response)[s:s+9]

        REQUEST = self.app.REQUEST
        namesp = REQUEST.SESSION.getBrowserIdManager().getBrowserIdNamespaces()
        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(['form'])
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
        
        path = '/%s/search_results?_ZopeId=%s&query_id=%s&batch_length=10' % (self.naudoc.physical_path(), browser_id, query_id)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        #f = open('7.htm', 'w')
        #f.write(str(response))
        #f.close()

        # TODO: when batch_length value will be work next 3 strings should be uncommented
        #self.assert_('D1' in str(response.getBody()))
        #self.assert_('D2' in str(response.getBody()))
        #self.assert_('D3' in str(response.getBody()))

        REQUEST.SESSION.getBrowserIdManager().setBrowserIdNamespaces(list(namesp))
        REQUEST.SESSION.getBrowserIdManager().updateTraversalData()
        
    def beforeTearDown(self):
        folder = self.naudoc.storage.members
        folder.deleteObjects(['D1', 'D2', 'D3'])
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class SearchLoadTests(NauDocTestCase.NauFunctionalTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):
        #create SESSION in REQUEST
        self.app.__before_publishing_traverse__(self.app, self.app.REQUEST)
        get_transaction().commit()

    def testSearchLoad(self):
        REQUEST = self.app.REQUEST
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        
        query    = SearchQuery()
        query_id = query.getId()
        query.implements = ['isHTMLDocument']
        query.scope = 'global'
        query.text = 'test_search'

        REQUEST.SESSION.set(( 'search',query_id ), query)
        browser_id = REQUEST.SESSION.getBrowserIdManager().getBrowserId()

        folder = self.naudoc.portal_membership.getPersonalFolder( 'favorites', create=1 )

        id = 'test_search_profile'
        title = 'test_search_title'
        folder.invokeFactory( type_name='Search Profile'
                             ,id=id
                             ,title=title
                             ,query_id=query_id
                             ,description='test description'
                            )
        req = folder._getOb( id )
        get_transaction().commit()
        
        # testing search_form
        path = '/%s/search_form' % self.naudoc.absolute_url(1)
        extra = { 'profile_id':req.getUid(),
                  'load':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # checking that test_search_profile is appears in the list of saved profiles
        self.assert_( title in response.getBody() )
        # checking that search data is loaded to search fields
        self.assert_( query.text in response.getBody() )

        # deleting folder
        self.naudoc.storage.deleteObjects([folder.getId()])
        
    def beforeTearDown(self):
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(SearchFunctionalTests))
    suite.addTest(makeSuite(SearchFormsTests))
    suite.addTest(makeSuite(SearchLoadTests))
    return suite

if __name__ == '__main__':
    framework()
