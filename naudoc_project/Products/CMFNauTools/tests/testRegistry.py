"""
Test registry with 20 documents in it.

$Id: testRegistry.py,v 1.8 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$ $'[11:-2]

import os, sys, random
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
ZopeTestCase.installProduct('TextIndexNG2')

class RegistryTests(NauDocTestCase.NauFunctionalTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    doc_count = Constants.LARGE

    def afterSetUp(self):
        #create registry in storage folder
        self.reg_id = 'G'
        self.userids = []
        folder = self.naudoc.storage
        folder.manage_addProduct['CMFNauTools'].\
            addRegistrationBook( id=self.reg_id
                                ,title=self.reg_id
                                ,description='test'
                               )
        reg = folder._getOb(self.reg_id)
        reg.setRegisteredCategory('Document')

        wft = getToolByName( reg, 'portal_workflow' )

        #create 20 documents and register they in registration book
        for i in xrange(self.doc_count):
            id = self.cookId(i)
            title = id
            folder.invokeFactory( type_name='HTMLDocument'
                                 ,id=id
                                 ,title=title
                                 ,description='test description'
                                 ,category='Document'
                                )
            doc = folder._getOb( id )
            reg.register(doc)

            if (i % 5) == 0:
                wft.doActionFor( doc, 'retract')
        #create users
        for number in range(3):
            self._addUser(number)
        get_transaction().commit()
 
    def cookId( self, i ):
        return 'D%s' % i

    def testRegistry( self ):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc.storage._getOb(self.reg_id)
        path = '/%s/view' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )
    def testRegistrySettings( self ):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc.storage._getOb(self.reg_id)
        obj.addColumn( 'Id', 'Id', **obj.getMetaColumnParams('Id') ) 
        obj.addColumn( 'Title', 'Title', **obj.getMetaColumnParams('Title') )
       
        path = '/%s/registration_book_edit_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testResults( self ):

        reg = self.naudoc.storage._getOb( self.reg_id )

        self.assertEquals( len(map(None,reg.searchEntries())), self.doc_count )

        search_title = self.cookId(random.choice(range(self.doc_count)))
        self.assertEquals( len(map(None,reg.searchEntries( title=search_title))), 1 )

        private_count = 1+(self.doc_count-1)/5 
        self.assertEquals( len(map(None,reg.searchEntries( state='private')))
                         , private_count)

        self.assertEquals( len(map(None,reg.searchEntries( state={'query':'private'
                                                                 , 'operator':'not'})))
                         , self.doc_count - private_count )


    def testRegistrationNumberAttributeId( self ):
        reg = self.naudoc.storage._getOb( self.reg_id )
        attr_id = 'Test_Attr_id'
        reg.setRegistrationNumberAttributeId(attr_id)
        self.assertEquals(reg.getRegistrationNumberAttributeId(), attr_id)

    def testDepartment( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        dept = 'Test Department'
        reg.setDepartment(dept)
        self.assertEquals(reg.getDepartment(), dept)

    def testRegistrationNumberTemplate( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        rule = 'TestRule'
        reg.setRegistrationNumberTemplate(rule)
        self.assertEquals(reg.getRegistrationNumberTemplate(), rule)

    def testRegister( self ):
        docs_to_reg = 3
        reg = self.naudoc.storage._getOb(self.reg_id)
        folder = self.naudoc.storage
        id = self.cookId('Test_ID')
        title = id
        folder.invokeFactory( type_name='HTMLDocument'
                             ,id=id
                             ,title=title
                             ,description='test description'
                             ,category='Document'
                            )
        doc = folder._getOb(id)
        # register by object
        self.assertEqual(reg.register(doc), True)
        self.assertEqual(reg.unregister(doc), True)
        # register by Uid
        self.assertEqual(reg.register(doc.getUid()), True)
        self.assertEqual(reg.unregister(doc.getUid()), True)
        # unregister List
        for i in range(docs_to_reg):
            id = 'Doc_%d' % i
            title = id
            folder.invokeFactory( type_name='HTMLDocument'
                                 ,id=id
                                 ,title=title
                                 ,description='test description'
                                 ,category='Document'
                                )
            doc = folder._getOb( id )
            reg.register(doc)
        reg.unregister([(folder._getOb('Doc_%d' % k)) for k in range(docs_to_reg)])
        ids = [('Doc_%d' % k) for k in range(docs_to_reg)]
        ids.append(self.cookId('Test_ID'))
        folder.deleteObjects( ids )

    def testPapersFolder( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        folder = self.naudoc.storage
        id = 'Heading'
        title = id
        folder.invokeFactory( type_name='Heading'
                                       ,id=id
                                       ,title=title
                                       ,description='test description'
                                       ,category='Folder'
                                      )
        TestHeading = folder._getOb( id )
        reg.setPapersFolder(TestHeading.getUid())
        self.assertEqual(reg.getPapersFolder(), (TestHeading.getUid(),TestHeading.Title()))
        folder.deleteObjects( [id] )

    def testRegisterPaperDocument( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        folder = self.naudoc.storage
        doc_id = 'Doc_%f' % random.random()
        title = doc_id
        folder.invokeFactory( type_name='HTMLDocument'
                             ,id=doc_id
                             ,title=title
                             ,description='test description'
                             ,category='Document'
                            )
        doc = folder._getOb(doc_id)

        id = self.cookId('Test_IDPD') 
        title = id

        Request = {'id': id, 'title': title, 'description': 'Test Description'
                   ,'doc_uid': doc.getUid(), 'doc_version': 'Test Version'}

        res = str(reg.registerPaperDocument(Request))
        self.assertEqual('<html>' in res.lower(),True)
        
        hid = 'H_%f' % random.random()
        htitle = hid
        folder.invokeFactory( type_name='Heading'
                                       ,id=hid
                                       ,title=htitle
                                       ,description='test description'
                                       ,category='Folder'
                                      )
        TestHeading = folder._getOb(hid)
        reg.setPapersFolder(TestHeading.getUid())

        Request = {'id': id, 'title': title, 'description': 'Test Description',
                   'category':'Normative document',
                   'doc_uid': doc.getUid(), 'doc_version': 'Test Version'}
        res = reg.registerPaperDocument(Request)
        req_res = reg.redirect(action='paper_document_registration', 
                               message='Document was registered')
        self.assertEqual(res,req_res)
        folder.deleteObjects( [doc_id, hid] )

    def testRecencyPeriod( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        rp = int(random.expovariate(0.01))
        reg.setRecencyPeriod(rp)
        self.assertEqual(reg.getRecencyPeriod(),rp)

    def testCanAdd( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        folder = self.naudoc.storage
        hid = 'H_%f' % random.random()
        htitle = hid
        folder.invokeFactory( type_name='Heading'
                                       ,id=hid
                                       ,title=htitle
                                       ,description='test description'
                                       ,category='Folder'
                                      )
        TestHeading = folder._getOb(hid)
        member = []
        
        username1 = self.userids[0]
        username2 = self.userids[1]
        reg.setPapersFolder(TestHeading.getUid())
        #-----------------OE---------------
        TestHeading.setLocalRoles(username1, ('Owner','Editor'))        
        self.login(username1)
        self.assertEqual(reg.canAdd(),1)
        #-----------------OR
        TestHeading.setLocalRoles(username1, ('Owner','Reader'))
        self.login(username1)
        self.assertEqual(reg.canAdd(),1)
        #-----------------OA
        TestHeading.setLocalRoles(username1, ('Owner','Author'))
        self.login(username1)
        self.assertEqual(reg.canAdd(),1)
        #-----------------OW
        TestHeading.setLocalRoles(username1, ('Owner','Writer'))
        self.login(username1)
        self.assertEqual(reg.canAdd(),1)
        #-----------------Author
        TestHeading.setLocalRoles(username2, ('Author'))
        self.login(username2)
        self.assertEqual(reg.canAdd(),False)
        #-----------------Reader
        TestHeading.setLocalRoles(username2, ('Reader'))
        self.login(username2)
        self.assertEqual(reg.canAdd(),False)
        #-----------------Writer
        TestHeading.setLocalRoles(username2, ('Writer'))
        self.login(username2)
        self.assertEqual(reg.canAdd(),False)
        #-----------------Editor
        TestHeading.setLocalRoles(username2, ('Editor'))
        self.login(username2)
        self.assertEqual(reg.canAdd(),False)
        #-----------------Admin
        self.login()
        self.assertEqual(reg.canAdd(),1)
        folder.deleteObjects([hid])

    def testlistTabs( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        username = self.userids[2]
        self.login( username )
        Tabs = reg.listTabs()
        TabsName = []
        for i in range(len(Tabs)):
            TabsName.append(Tabs[i][Tabs[i].keys()[1]])
        self.assertEqual('View' in TabsName, True)
        self.login()
        Tabs = reg.listTabs()
        TabsName = []
        for i in range(len(Tabs)):
            TabsName.append(Tabs[i][Tabs[i].keys()[1]])
        self.assertEqual('View' in TabsName and 'Settings' in TabsName, True)

    def testRegistredCategory( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        category = 'Folder'
        reg.setRegisteredCategory(category)
        self.assertEqual(reg.getRegisteredCategory(),category)
        category = 'Document'
        reg.setRegisteredCategory(category)
        self.assertEqual(reg.getRegisteredCategory(),category)

    def testDocumentAllowedToRegister( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        folder = self.naudoc.storage
        hid = 'H_%f' % random.random()
        htitle = hid
        folder.invokeFactory( type_name='Heading'
                                       ,id=hid
                                       ,title=htitle
                                       ,description='test description'
                                       ,category='Folder'
                                      )
        doc = folder._getOb(hid)

        category = 'Folder'
        reg.setRegisteredCategory(category)
        self.assertEqual(reg.isDocumentAllowedToRegister(doc), 1)

        category = 'Document'
        reg.setRegisteredCategory(category)
        self.assertEqual(reg.isDocumentAllowedToRegister(doc), 0)
        folder.deleteObjects([hid])

    def testLastSequenceNumber( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        old_current_val = reg.getLastSequenceNumber()
        folder = self.naudoc.storage
        doc_id = 'H_%f' % random.random()
        doc_title = doc_id
        folder.invokeFactory( type_name='HTMLDocument'
                                       ,id=doc_id
                                       ,title=doc_title
                                       ,description='test description'
                                       ,category='Document'
                                      )
        doc = folder._getOb(doc_id)
        reg.register(doc.getUid())
        new_current_val = reg.getLastSequenceNumber()
        self.assertEqual(bool((new_current_val - old_current_val) == 1), True)
        folder.deleteObjects([doc_id])

    def testInternalCounter( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        pre_counter = reg.getLastSequenceNumber()
        counter = 65535
        reg.setInternalCounter(counter)
        self.assertEqual(reg.getLastSequenceNumber(),counter)
        reg.setInternalCounter(pre_counter)
        self.assertEqual(reg.getLastSequenceNumber(),pre_counter)
   
    def testHideRegistrationDate( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        pre_value = reg.hide_registration_date
        value = 1
        reg.setHideRegistrationDate(value)
        self.assertEqual(reg.hide_registration_date, bool(value))
        reg.setHideRegistrationDate(pre_value)
        self.assertEqual(reg.hide_registration_date, pre_value)

    def testHideCreator( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        pre_value = reg.hide_creator
        value = 1
        reg.setHideCreator(value)
        self.assertEqual(reg.hide_creator, bool(value))
        reg.setHideCreator(pre_value)
        self.assertEqual(reg.hide_creator, pre_value)

    def testHideVersion( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        pre_value = reg.hide_version
        value = 1
        reg.setHideVersion(value)
        self.assertEqual(reg.hide_version, bool(value))
        reg.setHideVersion(pre_value)
        self.assertEqual(reg.hide_version, pre_value)

    def testFilterColumns( self ):
        reg = self.naudoc.storage._getOb(self.reg_id)
        category = 'Folder'
        reg.setRegisteredCategory(category)
        metadata = getToolByName( reg, 'portal_metadata' )
        workflow = getToolByName( reg, 'portal_workflow' )
        category = metadata.getCategoryById( reg.getRegisteredCategory() )
        wf = category.getWorkflow()
        states = wf.states.objectIds()
        test = [( x, workflow.getStateTitle( wf.getId(), x ) ) for x in states]
        Col_List = []
        for x in reg.getFilterColumns():
            Col_List.append(test in x.values())
        self.assertEqual(sum(Col_List), True)
        category = 'Document'
        reg.setRegisteredCategory(category)

        states = wf.states.objectIds()
        test = [( x, workflow.getStateTitle( wf.getId(), x ) ) for x in states]
        Col_List = []
        for x in reg.getFilterColumns():
            Col_List.append(test in x.values())
        self.assertEqual(sum(Col_List), False)

    """
    def testSearchEntries(self):
        reg = self.naudoc.storage._getOb(self.reg_id)

    def testExecuteQuery(self):
        reg = self.naudoc.storage._getOb(self.reg_id)
    """
       
    def beforeTearDown( self ):
        folder = self.naudoc.storage
        if folder._getOb(self.reg_id, None):
            reg = folder.deleteObjects([self.reg_id])
        if folder._getOb('D0', None):
            ids = [('D%s' % k) for k in xrange(20)]
            folder.deleteObjects( ids )
        self.naudoc.portal_membership.deleteMembers( self.userids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown(self)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RegistryTests))
    return suite

if __name__ == '__main__':
    framework()
