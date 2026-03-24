"""
Test DocFlowReport with 20 documents in it.

$Id: testDocflowReport.py,v 1.8 2006/02/15 13:25:26 ynovokreschenov Exp $
"""
__version__='$ $'[11:-2]

import os, sys
import random
import Configurator
Constants = Configurator.Constants


if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools import NauSite

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class DocflowReportTests(NauDocTestCase.NauFunctionalTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    doc_count = Constants.LARGE
    pub_count = Constants.MEDIUM

    dfr_id = 'DFR'
    
    def afterSetUp( self ):
        #create SESSION in REQUEST
        self.app.__before_publishing_traverse__(self.app, self.app.REQUEST)

        #create DocFlowReportDoc
        id = self.dfr_id
        title = id
        folder = self.naudoc.storage
        folder.manage_addProduct['CMFNauTools'].\
                                addDocflowReport( id = id
                                                , title = title
                                                , description = 'testDescr'
                                                )
        dfr = folder._getOb( self.dfr_id )
        self.dfr = dfr
        dfr.setSearchableCategory( 'Publication'
                                 , search_all=True
                                 )

        wft = getToolByName( dfr, 'portal_workflow' )
        #create 20 documents
        for i in xrange(self.doc_count):
            id="D%s" %i
            title="D%s" %i
            folder.invokeFactory( type_name='HTMLDocument'
                                , id=id
                                , title=title
                                , description='test description'
                                , category='Document'
                                )
            doc = folder._getOb( id )

            if (i % 5) == 0:
                wft.doActionFor( doc, 'retract')
        #create 5 Publications
        for i in range(self.pub_count):
            hid="H%d" % i
            htitle=hid
            folder.invokeFactory( type_name='HTMLDocument'
                                       ,id=hid
                                       ,title=htitle
                                       ,description='test description'
                                       ,category='Publication'
                                      )
            doc = folder._getOb( id )
                
        get_transaction().commit()

    def testSearchableCategory( self ):
        dfr = self.dfr
        dfr.setSearchableCategory( 'Document',
                                include_inherited=None,
                                search_all=None )
        category = dfr.getSearchableCategory()
        self.assertEqual( category, 'Document' )

    def testIncludeInherited( self ):
        dfr = self.dfr
        _include_inherited = True
        dfr.setSearchableCategory( 'Document',
                                include_inherited=_include_inherited,
                                search_all=None )
        self.assertEqual( dfr.isIncludeInherited(), _include_inherited )
        _include_inherited = False
        dfr.setSearchableCategory( 'Document',
                                include_inherited=_include_inherited,
                                search_all=None )
        self.assertEqual( dfr.isIncludeInherited(), _include_inherited )

    def testSearchAll( self ):
        dfr = self.dfr
        _search_all = True
        dfr.setSearchableCategory( 'Document',
                                include_inherited=None,
                                search_all=_search_all )
        self.assertEqual( dfr.isSearchAll(), _search_all )
        _search_all = False
        dfr.setSearchableCategory( 'Document',
                                include_inherited=None,
                                search_all=_search_all )
        self.assertEqual( dfr.isSearchAll(), _search_all )
    
    
    def testGetFilterColumns( self ):
        dfr = self.dfr
        _search_all = True
        #set SerchableCategory to 'Document' and compared category to 'Document'
        dfr.setSearchableCategory( 'Document',
                                include_inherited=None,
                                search_all=_search_all )
        metadata = getToolByName( dfr, 'portal_metadata' )
        workflow = getToolByName( dfr, 'portal_workflow' )
        category = metadata.getCategoryById( dfr.getSearchableCategory() )
        wf = category.getWorkflow()
        states = wf.states.objectIds()
        test = [( x, workflow.getStateTitle( wf.getId(), x ) ) for x in states]
        Col_List = []
        for x in dfr.getFilterColumns():
            Col_List.append(test in x.values())
        self.assertEqual( sum(Col_List), True )
        #set compared category to 'Folder'
        category = metadata.getCategoryById( 'Folder' )
        wf = category.getWorkflow()
        states = wf.states.objectIds()
        test = [( x, workflow.getStateTitle( wf.getId(), x ) ) for x in states]
        Col_List = []
        for x in dfr.getFilterColumns():
            Col_List.append( test in x.values() )
        self.assertEqual( sum( Col_List ), False )

    def testSearchEntries( self ):
        dfr = self.dfr
        #search documents
        dfr.setSearchableCategory( 'Document',
                                search_all=True )
        _res = dfr.searchEntries(show_all_versions=1, kw={} )
        _search_result = [(i.Title) for i in _res]
        self.assertEqual( _search_result, [("D%s" % i) for i in xrange( self.doc_count )] )
        #search folders
        dfr.setSearchableCategory( 'Publication',
                                search_all=True,
                                include_inherited=True )
        _res = dfr.searchEntries(show_all_versions=1, kw={} )
        _search_result = [(i.Title) for i in _res]
        self.assertEqual( _search_result, [("H%s" % i) for i in xrange( self.pub_count )] )

    def testExecuteQuery( self ):
        dfr = self.dfr

        result = dfr.executeQuery( self.app.REQUEST )
        self.assertEqual(result.has_key('results'),True)
    
    def beforeTearDown( self ):
        folder = self.naudoc.storage
        if folder._getOb( self.dfr_id, None ):
            reg = folder.deleteObjects( [self.dfr_id] )
        if folder._getOb( 'D0', None ):
            ids = [('D%s' % k) for k in xrange(self.doc_count)]
            folder.deleteObjects( ids )
        if folder._getOb( 'H0', None ):
            ids = [('H%s' % k) for k in range(self.pub_count)]
            folder.deleteObjects( ids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )


class DocflowReportTestsViewSettings( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    doc_count = Constants.LARGE

    dfr_id = 'DFR'

    def afterSetUp(self):
        #create registry in storage folder

        folder = self.naudoc.storage
        folder.manage_addProduct['CMFNauTools'].\
            addDocflowReport( id=self.dfr_id
                            , title=self.dfr_id
                            , description='test'
                            )
        dfr = folder._getOb(self.dfr_id)
        dfr.setSearchableCategory('Document'
                                 , search_all=True
                                 )

        wft = getToolByName( dfr, 'portal_workflow' )

        #create 20 documents and register they in registration book
        for i in xrange(self.doc_count):
            id="D%s" %i
            title="D%s" %i
            folder.invokeFactory( type_name='HTMLDocument'
                                , id=id
                                , title=title
                                , description='test description'
                                , category='Document'
                                )
            doc = folder._getOb( id )

            if (i % 5) == 0:
                wft.doActionFor( doc, 'retract')

        get_transaction().commit()

    def testView(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc.storage._getOb(self.dfr_id)
        path = '/%s/view' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testSettings(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc.storage._getOb(self.dfr_id)
        obj.addColumn( 'Id', 'Id', **obj.getMetaColumnParams('Id') ) 
        obj.addColumn( 'Title', 'Title', **obj.getMetaColumnParams('Title') )
       
        path = '/%s/docflow_report_edit_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def beforeTearDown(self):
        folder = self.naudoc.storage
        if folder._getOb(self.dfr_id, None):
            reg = folder.deleteObjects([self.dfr_id])
        if folder._getOb('D0', None):
            ids = [('D%s' % k) for k in xrange(self.doc_count)]
            folder.deleteObjects( ids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class DocflowReportFormsTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    docflow_report = 'test_docflow_report'
    
    def afterSetUp(self):
        storage = self.naudoc.storage.members
        id = self.docflow_report
        title = id
        description = 'test description'
        storage.invokeFactory( type_name='Docflow Report',
                               id=id,          
                               title=title,
                               description=description,
                             )
        
    def testDocflowReport(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        log_as_user = NauDocTestCase.admin_name
        
        storage = self.naudoc.storage.members
        id = self.docflow_report
        obj = storage._getOb( id )
       
        # test registration_book_factory_form
        path = '/%s/docflow_report_edit_form' % obj.absolute_url(1)
        extra = {}
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test docflow_report_edit
        path = '/%s/docflow_report_edit' % obj.absolute_url(1)
        extra = { 'title':'new_title',
                  'description':'new description',
                  'category':'Folder',
                  'include_inherited':True,
                  'search_all':True,

                  'metadata':'Title',
                  'add_column_meta':True,

                  'attribute':'nomenclative_number',
                  'add_column_attr':True,

                  'state':'fixed',
                  'add_column_state':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        self.assertEquals( obj.title, extra['title'] )
        self.assertEquals( obj.description, extra['description'] )
        self.assertEquals( obj.category_id, extra['category'] )
        self.assertEquals( obj.include_inherited, extra['include_inherited'] )
        self.assertEquals( obj.search_all, extra['search_all'] )
        
        columns = [i.id for i in obj.listColumns()]
        self.assert_( extra['metadata'] in columns )
        self.assert_( extra['attribute'] in columns )
        self.assert_( extra['state'] in columns )

        # test moveColumns
        i1 = columns.index('Title')

        path = '/%s/moveColumn?direction:int=1&id=Title' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        columns = [i.id for i in obj.listColumns()]
        i2 = columns.index('Title')
        self.assertEquals( i2, (i1-1) )

        # test docflow_report_edit deleting columns
        path = '/%s/docflow_report_edit' % obj.absolute_url(1)
        extra_del = { 'category':'Folder',
                      'del_Title':True,
                      'delete_columns':True,
                    }
        response = self.publish(path, basic_auth, extra=extra_del)
        self.assertResponse( response )        

        columns = [i.id for i in obj.listColumns()]
        self.assert_( extra['metadata'] not in columns )
        
    def beforeTearDown(self):
        storage = self.naudoc.storage.members
        storage.deleteObjects( [self.docflow_report] )
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(DocflowReportTests))
    suite.addTest(makeSuite(DocflowReportTestsViewSettings))
    suite.addTest(makeSuite(DocflowReportFormsTests))
    return suite

if __name__ == '__main__':
    framework()
