#! /bin/env python2.3
"""
Create and destroy NauDoc folders. Measure time needed.

$Id: testFolder.py,v 1.13 2006/03/03 09:26:53 ynovokreschenov Exp $
"""
__version__='$Revision: 1.13 $'[11:-2]

import os, sys
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')

# External Editor is needed because it patched manage_main, which is rendered in manage_pasteObjects
ZopeTestCase.installProduct('ExternalEditor')

class FoldersCreationTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0
    folder_base_name = 'ztc_test_folder_'
    folder_base_title = 'NauDoc test case folder'
    number_of_folders = Constants.LARGE

    def testFolderCreation(self):
        storage = self.naudoc.storage

        for i in range(self.number_of_folders):
            id = self.cookId(i)
            title = "%s %d" % (self.folder_base_title, i)
            storage.invokeFactory( type_name='Heading',
                                       id=id,
                                       title=title,
                                       description='test description',
                                       category='Folder' )

            #test that it was created
            obj = storage._getOb( id )
            self.assert_( obj is not None )

        get_transaction().commit()

    def cookId(self, i):
        return '%s%d' % (self.folder_base_name, i)

    def beforeTearDown(self):
        folders_ids = map(self.cookId, range(self.number_of_folders))
        self.naudoc.storage.deleteObjects( folders_ids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class FoldersTransferTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    folder_count = Constants.LARGE
    doc_count = Constants.FEW
    folder_to = 'to'

    def _createFoldersAndDocuments(self):
        storage = self.naudoc.storage
        for i in range( self.folder_count ):
            id = "F%s" %i
            storage.invokeFactory( type_name='Heading'
                                 , id=id
                                 , title=id
                                 , description='test description'
                                 , category='Folder'
                                 )

            folder = storage._getOb( id )
            for i in range( self.doc_count ):
                id = "D%s" %i
                folder.invokeFactory( type_name='HTMLDocument'
                                    , id=id
                                    , title=id
                                    , description='test description'
                                    , category='Document'
                                    )

        get_transaction().commit()

    def _deleteFolders(self):
        folder = self.naudoc.storage
        ids2remove = [('F%s' % k) for k in range(self.folder_count)]
        folder.deleteObjects( ids2remove )
        get_transaction().commit()

    def afterSetUp(self):
        self._createFoldersAndDocuments()

        storage = self.naudoc.storage
        storage.invokeFactory( type_name='Heading'
                             , id=self.folder_to
                             , title=self.folder_to
                             , description='test description'
                             , category='Folder'
                             )

        get_transaction().commit()

    def testFoldersCopying(self):
        REQUEST = self.naudoc.REQUEST

        folder_from = self.naudoc.storage
        folder_to = self.naudoc.storage._getOb( self.folder_to )

        ids = [('F%s' % k) for k in range( self.folder_count )]
        ids.sort()
        folder_from.manage_copyObjects( ids, REQUEST=REQUEST )
        folder_to.manage_pasteObjects( REQUEST=REQUEST )
        fids = folder_to.objectIds()
        fids.sort()
        self.assertEquals(ids, fids)
    
    def testFoldersMoving(self):
        REQUEST = self.naudoc.REQUEST

        folder_from = self.naudoc.storage
        folder_to = self.naudoc.storage._getOb( self.folder_to )

        ids = [('F%s' % k) for k in range( self.folder_count )]
        ids.sort()
        folder_from.manage_cutObjects(ids, REQUEST)
        folder_to.manage_pasteObjects( REQUEST=REQUEST )
        fids = folder_to.objectIds()
        fids.sort()
        self.assertEquals(ids, fids)
    
    def beforeTearDown(self):
        self._deleteFolders()

        folder = self.naudoc.storage
        folder.deleteObjects( [self.folder_to] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class FoldersDeletionTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0                                  
    log_as_user = NauDocTestCase.admin_name
    folder_count = Constants.LARGE
    doc_count = Constants.FEW

    _createFoldersAndDocuments = FoldersTransferTests._createFoldersAndDocuments.im_func
    _deleteFolders = FoldersTransferTests._deleteFolders.im_func

    def afterSetUp(self):
        self._createFoldersAndDocuments()

    def testDeleteFolders(self):
        folder = self.naudoc.storage
        ids = [('F%s' % k) for k in range(self.folder_count)]
        folder.deleteObjects( ids )
        get_transaction().commit()

    def beforeTearDown(self):
        self._deleteFolders()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class FolderTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0                                  
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):

        self.naudoc.manage_addProduct['CMFNauTools'].manage_addHeading('heading_test')
        get_transaction().commit()

        self.d = self.naudoc.heading_test

    def testManage_permissions(self):
        heading_test = self.d
        root = self.app
        # get all existent groups
        req = root.REQUEST
        # clear all permissions
        membership = self.naudoc.portal_membership
        membership._addGroup('Group 1')
        membership._addGroup('Group 2')
        membership._addGroup('Group 3')
        membership._addGroup('Group 4')

        heading_test.manage_permissions(req)
        self.assertEqual( heading_test.get_local_group_roles(), (), \
                'Error while clearing permissions' )

        #set new permissions and test them
        req['Group 1'] = ['Editor']
        req['Group 2'] = ['Author']
        req['Group 3'] = ['Reader']
        req['Group 4'] = ['Writer']
        heading_test.manage_permissions(req)

        self.assertEqual( heading_test.get_local_group_roles()
                         , (('Group 1', ('Editor',)), ('Group 2', ('Author',)), ('Group 3', ('Reader',)), ('Group 4', ('Writer',)))
                         , 'Groups were not set up correctly' )

        membership._delGroups(['Group 1','Group 2','Group 3','Group 4'])

    def testSetLocalRoles_GetLocalRoles_DelLocalRoles(self):
        heading_test = self.d

        # first we create htmldocument into heading
        id = 'test_reindex_roles'
        heading_test.manage_addProduct['CMFNauTools'].addHTMLDocument(id,
                        title='title', description='descr', text_format='html',
                        text='text goes here', category='Document')
        t = getattr(heading_test, id)

        #---test roles assignment---
        heading_test.setLocalRoles('tester1', ('Writer', 'Reader'))
        heading_test.setLocalRoles('tester2', ['Editor', 'Writer'])
        t1_h_roles = heading_test.getLocalRoles('tester1')[0]
        t1_h_roles.sort()
        if  t1_h_roles != ['Reader', 'Writer']:
            self.fail('Bad roles for tester1 in Heading')
        t2_h_roles = heading_test.getLocalRoles('tester2')[0]
        t2_h_roles.sort()
        if t2_h_roles != ['Editor', 'Writer']:
            self.fail('Bad roles for tester2 in Heading')

        t1_t_roles = t.getLocalRoles('tester1')[0]
        t1_t_roles.sort()
        if t1_t_roles != ['Reader', 'Writer']:
            self.fail('Bad roles for tester1 in subobject')
        t2_t_roles = t.getLocalRoles('tester2')[0]
        t2_t_roles.sort()
        if t2_t_roles != ['Editor', 'Writer']:
            self.fail('Bad roles for tester2 in subobject')

        heading_test.delLocalRoles(['tester2'])

        self.assertEqual(((),), heading_test.getLocalRoles('tester2'), \
                'Roles of tester2 was not deleted')
        self.assertNotEqual(((),), heading_test.getLocalRoles('tester1'), \
                'Roles of tester1 was deleted')

        self.assertEqual(((),), t.getLocalRoles('tester2'), \
                'Roles of tester2 was not deleted in subobject')
        self.assertNotEqual(((),), t.getLocalRoles('tester1'), \
                'Roles of tester1 was deleted in subobject')

    def testUserRoles(self):
        heading_test = self.d

        id = 'test_reindex_roles'
        heading_test.manage_addProduct['CMFNauTools'].addHTMLDocument(id,
                        title='title', description='descr', text_format='html',
                        text='text goes here')
        t = getattr(heading_test, id)

        import AccessControl.SecurityManagement, AccessControl.SpecialUsers
        system = AccessControl.SpecialUsers.system
        AccessControl.SecurityManagement.newSecurityManager(None, system)

        from Products.CMFCore.utils import _getAuthenticatedUser
        uname =  _getAuthenticatedUser(heading_test).getUserName()
        heading_test.setLocalRoles(uname, ['Editor', 'Author'])
        h_roles = heading_test.user_roles()
        h_roles.sort()
        self.assertEqual( h_roles,  ['Author', 'Editor'], \
                'Bad roles for current user')

        t_roles = t.user_roles()
        t_roles.sort()
        self.assertEqual( t_roles,  ['Author', 'Editor'], \
                'Bad roles for current user in subobject')

        #test user_roles
        heading_test.delLocalRoles([uname,])
        self.assertEqual( len(heading_test.user_roles()), 0, \
                'Current user roles removal error')
        self.assertEqual( len(t.user_roles()), 0, \
                'Current user roles removal error in subobject')

    def testReindexSubObjects(self):
        """
        We test Reindex objects inside the given folder
        (it updates 'allowedRolesAndUsers')
        """

        def role_for_user(uname, roles_and_users):
            roles = {}
            cur_role = 'no roles'
            for role_or_user in roles_and_users:
                if role_or_user.find('user:') == -1:
                    cur_role = role_or_user
                if role_or_user.find( 'user:'+uname ) != -1:
                    roles[ cur_role ] = 1
            try:
                del roles['no roles']
            except:
                pass
            return roles

        heading_test = self.d

        # first we add htmldocument into the heading
        id = 'test_reindex_roles'
        heading_test.manage_addProduct['CMFNauTools'].addHTMLDocument(id,
                        title='title', description='descr', text_format='html',
                        text='text goes here')
        t = getattr(heading_test, id)

        import AccessControl.SecurityManagement, AccessControl.SpecialUsers
        system = AccessControl.SpecialUsers.system
        AccessControl.SecurityManagement.newSecurityManager(None, system)

        from Products.CMFCore.utils import _getAuthenticatedUser
        uname =  _getAuthenticatedUser(heading_test).getUserName()

        # XXX reviewer role does not exists any more
        heading_test.manage_setLocalRoles(uname, ['Reviewer'])

        from Products.CMFCore.utils import getToolByName
        catalog = getToolByName(heading_test, 'portal_catalog', None)

        heading_test.reindexObject(recursive=True)

        results = catalog.searchResults(path = heading_test.absolute_url(1))
        for result in results:
            roles_and_users = catalog.getIndexDataForRID(  \
                                                    results[0].getRID() )['allowedRolesAndUsers']
            roles = role_for_user(uname, roles_and_users)
            self.failIf('Reviewer' not in roles.keys(), \
                    'After reindexSubObjects() user has no role Reviewer')
            self.assertEqual( len( roles.keys() ), 1, \
                    'After reindexSubObjects() user has wrong roles')

        heading_test.manage_delLocalRoles([uname])

        results = catalog.searchResults(path = heading_test.absolute_url(1))
        for result in results:
            roles_and_users = catalog.getIndexDataForRID(  \
                                                    results[0].getRID() )['allowedRolesAndUsers']
            roles = role_for_user(uname, roles_and_users)
            self.failIf('Reviewer' not in roles.keys(), \
                    'Before reindexSubObjects() user has no role Reviewer')
            self.assertEqual( len( roles.keys() ), 1, \
                    'Before reindexSubObjects() user has wrong roles')

        heading_test.reindexObject(recursive=True)

        results = catalog.searchResults(path = heading_test.absolute_url(1))
        for result in results:
            roles_and_users = catalog.getIndexDataForRID(  \
                                                    results[0].getRID() )['allowedRolesAndUsers']
            roles = role_for_user(uname, roles_and_users)
            self.failIf( len( roles.keys() ) > 0, \
                    'After reindexSubObjects() roles was not removed')

    def beforeTearDown(self):
        self.naudoc._delObject('heading_test')
        get_transaction().commit()

        del self.d

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class FolderFunctionalTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    folder_id = 'test_folder_1_'

    def afterSetUp(self):
        #create SESSION in REQUEST
        self.app.__before_publishing_traverse__(self.app, self.app.REQUEST)

        storage = self.naudoc.storage
        storage.invokeFactory( type_name='Heading',
                               id=self.folder_id,
                               title=self.folder_id,
                               description='test description',
                               category='Folder' )

        self.folder = storage._getOb( self.folder_id )

    def testStorageView(self):
        naudoc = self.app._getOb( self.naudoc_id )
 
        # test default view
        naudoc.storage()

        path = '/%s/folder/' % self.naudoc.storage.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testMetadata(self):
        # test metadata_edit_form
        path = '/%s/metadata_edit_form/' % self.folder.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

        # test metadata_edit
        path = '/%s/metadata_edit/' % self.folder.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        extra = { 'title':'new_title',
                  'description':'new_description',
                }
        response = self.publish(path, basic_auth, extra=extra)

        self.assertEquals( self.folder.title, extra['title'] )
        self.assertEquals( self.folder.description, extra['description'] )        

    def testProperties(self):
        path = '/%s/folder_edit_form/' % self.folder.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testViewingOrder(self):
        path = '/%s/viewing_order/' % self.folder.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testAccess(self):
        path = '/%s/manage_access_form/' % self.folder.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def beforeTearDown(self):
        del self.folder
        self.naudoc.storage.deleteObjects([self.folder_id])
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )         
  
  
  
class FolderFuncTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    folder_id = 'test_folder_1_'
    
    def afterSetUp(self):
        #create SESSION in REQUEST
        self.app.__before_publishing_traverse__(self.app, self.app.REQUEST)

        self.userids = []

        storage = self.naudoc.storage
        storage.invokeFactory( type_name='Heading',
                               id=self.folder_id,
                               title=self.folder_id,
                               description='test description',
                               category='Folder' )
        self.folder = storage._getOb( self.folder_id )
        for number in range(3):
            self._addUser( number )
        get_transaction().commit()
    
    def testEditorCreator(self):
        folder = self.folder
        user1 = self.userids[1]
        self.assertEqual( folder.getEditor().getUserName(), self.log_as_user )
        self.assertEqual( folder.Creator(), self.log_as_user )
        self.assertEqual( self.log_as_user in folder.editor(), True )
        self.assertEqual( len( folder.editor() ), 1 )
        folder.setLocalRoles( user1, ('Editor', 'Owner','Creator') )
        self.assertEqual( folder.getEditor().getUserName(), user1 )
        self.assertEqual( user1 in folder.editor(), True )
        self.assertEqual( len( folder.editor() ), 1 )
        self.assertEqual( folder.Creator(), user1 )
        folder.setLocalRoles( self.log_as_user, ('Editor', 'Owner','Creator') )
        self.login()
    
    def testMainPage( self ):
        folder = self.folder
        main_page_id = "Main_Page"
        self.assertEqual( folder.hasMainPage(), False )
        self.assertEqual( folder.getMainPage(), None )
        folder.invokeFactory( type_name='HTMLDocument',
                               id=main_page_id,
                               title=main_page_id,
                               description='test description',
                               category='Document' )
        main_page = folder._getOb( main_page_id )
        folder.setMainPage( main_page )
        self.assertEqual( folder.hasMainPage(), True )
        self.assertEqual( folder.getMainPage(), main_page )
        
        folder.deleteObjects( [main_page_id] )
    
    def testCategory( self ):
        folder = self.folder
        #test Inheritance
        temp =  folder.getCategoryInheritance()
        inher = False
        folder.setCategoryInheritance( inher )
        self.assertEqual( folder.getCategoryInheritance(), inher )
        inher = True
        folder.setCategoryInheritance( inher )
        self.assertEqual( folder.getCategoryInheritance(), inher )
        folder.setCategoryInheritance( temp )
        self.assertEqual( folder.getCategoryInheritance(), temp )
        #test AllowedCategory
        allowed_cat_list = [c.id for c in folder.listAllowedCategories()]
        test_cat = "Folder"
        self.assertEqual( folder.isCategoryAllowed(test_cat), test_cat in allowed_cat_list )
        new_allowed_cat_list = allowed_cat_list[1-len(allowed_cat_list):]
        folder.setAllowedCategories( ["Folder"] )
        folder.setAllowedCategories( new_allowed_cat_list )
        cat_list = [c.id for c in folder.listAllowedCategories()]
        #self.assertEqual( cat_list, new_allowed_cat_list )
        self.assertEqual( folder.isCategoryAllowed(test_cat),
                          ((test_cat in allowed_cat_list) and 
                           (test_cat not in allowed_cat_list[1-len(allowed_cat_list):]))
                          )
        folder.setAllowedCategories( allowed_cat_list )
    
    def testList( self ):
        folder = self.folder
        self.assert_( len(folder.listDocuments())==0 )
        catalog = getToolByName( folder, 'portal_catalog' )
        wf_tool = getToolByName( folder, 'portal_workflow' )
        #List Documents
        documents = []
        for i in range( Constants.MEDIUM ):
            doc_id = "Doc_%d" % i
            folder.manage_addProduct['CMFNauTools'].addHTMLDocument(doc_id
                                                                    , category='Document')
            documents.append( doc_id )
        self.assert_( len( folder.listDocuments() )==Constants.MEDIUM )
        folder.deleteObjects( documents )
        #List Publications
        self.assert_( len(folder.listPublications())==0 )
        documents = []
        for i in range( Constants.MEDIUM ):
            doc_id = "Doc_%d" % i
            folder.manage_addProduct['CMFNauTools'].addHTMLDocument(doc_id
                                                                    , category='Publication')
            documents.append( doc_id )
            document=folder._getOb( doc_id )
            wf_tool.doActionFor( document, 'publish')
            #document.reindexObject()
            #folder.reindexObject()
            catalog.reindexObject(document)
        self.assertEqual( len( folder.listPublications() ), Constants.MEDIUM )
        folder.deleteObjects( documents )
        #List Directives
        self.assert_( len(folder.listDirectives())==0 )
        documents = []
        for i in range( Constants.MEDIUM ):
            doc_id = "Doc_%d" % i
            folder.invokeFactory( type_name='HTMLDocument',
                                  id=doc_id,
                                  title=doc_id,
                                  description='test description',
                                  category='Directive' )
            documents.append( doc_id )
            document=folder._getOb( doc_id )
            wf_tool.doActionFor( document, 'apply')
            catalog.reindexObject(document)
        self.assert_( len( folder.listDirectives() )==Constants.MEDIUM )
        folder.deleteObjects( documents )
    
    def testArchiveProperty( self ):
        folder = self.folder
        #Save current and create new Archive property
        old_arch_prop = folder.getArchiveProperty()
        new_arch_prop = {'NewProp':1}
        #Change ArchiveProperty
        folder.setArchiveProperty( archiveProperty=new_arch_prop )
        self.assertEqual( folder.getArchiveProperty(), new_arch_prop )
        #Restore ArchiveProperty
        folder.setArchiveProperty( archiveProperty=old_arch_prop )
        self.assertEqual( folder.getArchiveProperty(), old_arch_prop )
    
    def testSubscription( self ):
        folder = self.folder
        self.assert_( not folder.isSubscribed() )
        user = self.userids[0]
        member = self.naudoc.portal_membership.getMemberById(user)
        folder.subscribe()
        self.assert_( folder.isSubscribed() )
        self.assert_( len( folder.listSubscribed() )==1 )
        self.login( user )
        folder.subscribe()
        self.login()
        self.assert_( len( folder.listSubscribed() )==2 )
        status = "You have not been signed up for the topic updates mailing. Try to subscribe again."
        self.assertEqual( str(folder.confirm_subscription( user=user )),status )
        status = "Now you will receive update notifications for this folder."
        self.assert_( str(folder.confirm_subscription( user=member ))==status )
        self.login( user )
        folder.unsubscribe()
        self.login()
        folder.unsubscribe()
        self.assert_( not folder.isSubscribed() )
        self.assert_( len( folder.listSubscribed() )==0 )
        self._delUser(user)
    
    def testMaxNumberOfPages( self ):
        folder = self.folder
        mnop = folder.getMaxNumberOfPages()
        new_mnop = Constants.MEDIUM
        folder.setMaxNumberOfPages( new_mnop )
        self.assert_( folder.getMaxNumberOfPages()==new_mnop )
        folder.setMaxNumberOfPages( mnop )
        self.assert_( folder.getMaxNumberOfPages()==mnop )
        
    def testAllowedContentTypes( self ):
        folder = self.folder
        #print folder.allowedContentTypes()
    
    def testGetContentsSize( self ):
        folder = self.folder
        self.assert_(folder.getContentsSize()==0)
        for i in range(Constants.MEDIUM):
            doc_id = "Doc_%d" % i
            folder.invokeFactory( type_name='HTMLDocument',
                                  id=doc_id,
                                  title=doc_id,
                                  description='test description',
                                  category='Directive' )
        self.assert_( folder.getContentsSize()==Constants.MEDIUM )
        folder.deleteObjects( ["Doc_%d" % i for i in range(Constants.MEDIUM)] )
        self.assert_(folder.getContentsSize()==0)
    
    def testViewing( self ):
        folder = self.folder
        REQUEST = self.app.REQUEST
        catalog = getToolByName( folder, 'portal_catalog' )
        wf_tool = getToolByName( folder, 'portal_workflow' )
        heads = []
        #create folders
        for i in range( Constants.MEDIUM ):
            head_id = "head_%d" % i
            folder.invokeFactory( type_name='Heading',
                                  id=head_id,
                                  title=head_id,
                                  description='test description',
                                  category='Folder' )
            heads.append( head_id )
            head=folder._getOb( head_id )
        #publish doc
        for i in range(Constants.MEDIUM):
            doc_id = "Doc0%d" % i
            head.invokeFactory( type_name='HTMLDocument',
                                id=doc_id,
                                title=doc_id,
                                description='test description',
                                category='Publication' )
            document = head._getOb( doc_id )
            wf_tool.doActionFor( document, "publish" )
            catalog.reindexObject( head )
            catalog.reindexObject( document )
        documents = []
        for i in range(Constants.MEDIUM):
            doc_id = "Doc0%d" % i
            folder.invokeFactory( type_name='HTMLDocument',
                                id=doc_id,
                                title=doc_id,
                                description='test description',
                                category='Publication' )
            document = folder._getOb( doc_id )
            wf_tool.doActionFor( document, "publish" )
            catalog.reindexObject( folder )
            catalog.reindexObject( document )
            documents.append( doc_id )
        #test
        folder.shiftHeading( head_id, 1 )
        folder.shiftDocument( doc_id, 1 )
        count = 0
        ord_doc = folder.getViewingDocumentOrder()
        for i in range(Constants.MEDIUM):
            doc_id = "Doc0%d" % i
            count += doc_id in ord_doc
        self.assert_( count, Constants.MEDIUM )
        self.assert_( head_id in folder.getViewingOrder() )
        folder.deleteObjects( heads )
    
    def testManageFixupOwnershipAfterAdd( self ):
        folder = self.folder
        new_owner = self.userids[2]
        folder.setLocalRoles( new_owner, ('Editor', 'Owner', 'Creator') )
        self.assertEqual( str(folder.getOwner()), new_owner )
        folder.manage_fixupOwnershipAfterAdd()
        self.assertEqual( str(folder.getOwner()), self.log_as_user )
        self.login( new_owner )
        folder.manage_fixupOwnershipAfterAdd()
        self.assertEqual( str(folder.getOwner()), new_owner )
        self.login()
        self._delUser( new_owner )
        folder.manage_fixupOwnershipAfterAdd()
        self.assertEqual( str(folder.getOwner()), self.log_as_user )
    
    def testManageChangeProperties( self ):
        folder = self.folder
        old_title = folder.Title()
        new_title = "NewTitle"
        folder.manage_changeProperties( {'title':new_title} )
        self.assertEqual( folder.Title(), new_title )
        folder.manage_changeProperties( {'title':old_title} )
        self.assertEqual( folder.Title(), old_title )
    
    def testManagePermissions( self ):
        folder = self.folder
        membership = self.naudoc.portal_membership
        REQUEST = {}
        role = 'Reader'
        REQUEST['all_users'] = [role]
        folder.manage_permissions( REQUEST=REQUEST )
        self.assert_( membership.isGroupInRole( folder, 'all_users', role ) )
    
    def testAllowedContentTypes( self ):
        folder = self.folder
        self.assert_( 'Heading' in [c.id for c in folder.allowedContentTypes()] )
    
    def testReindexObject( self ):
        folder = self.folder
        catalog = getToolByName( self.naudoc.storage, 'portal_catalog' )
        old_title = folder.Title()
        new_title = "New Title"
        folder.title = new_title
        catalog_title = catalog.getMetadataForUID( folder.physical_path() )['Title']
        self.assertEqual( catalog_title, old_title )
        folder.reindexObject()
        catalog_title = catalog.getMetadataForUID( folder.physical_path() )['Title']
        self.assertEqual( catalog_title, new_title )
        folder.title = old_title
        folder.reindexObject()
        catalog_title = catalog.getMetadataForUID( folder.physical_path() )['Title']
        self.assertEqual( catalog_title, old_title )
    
    def testGetPublishedFolders( self ):
        folder = self.folder
        catalog = getToolByName( folder, 'portal_catalog' )
        wf_tool = getToolByName( folder, 'portal_workflow' )
        heads = []
        for i in range( Constants.MEDIUM ):
            head_id = "head_%d" % i
            folder.invokeFactory( type_name='Heading',
                                  id=head_id,
                                  title=head_id,
                                  description='test description',
                                  category='Folder' )
            heads.append( head_id )
            head=folder._getOb( head_id )
        self.assertEqual( folder.getPublishedFolders(), [] )
        doc_id = "Doc0"
        head.invokeFactory( type_name='HTMLDocument',
                              id=doc_id,
                              title=doc_id,
                              description='test description',
                              category='Publication' )
        document = head._getOb( doc_id )
        wf_tool.doActionFor( document, "publish" )
        catalog.reindexObject( head )
        catalog.reindexObject( document )
        self.assertEqual( folder.getPublishedFolders()[0]['id'], head_id )
        folder.deleteObjects( heads )
    
    def testGetFolderFilter( self ):
        folder = self.folder
        REQUEST = self.app.REQUEST
        filter_name = 'MyFilter'
        self.naudoc.portal_membership.saveFilter( filter_id="New", filter_name=filter_name )
        self.naudoc.portal_membership.setMainFilter( filter_id="New" )
        self.assert_( self.naudoc.portal_membership.isMainFilterId( filter_id='New' ) )
        REQUEST['filter_is_on'] = True
        self.assertEqual( folder.getFolderFilter( REQUEST=REQUEST )['name'], filter_name )
        REQUEST['filter_is_on'] = False
        self.assertEqual( folder.getFolderFilter( REQUEST=REQUEST ), {} )
        self.naudoc.portal_membership.deleteFilter( filter_id="New" )
    
    def testGetBadLinks( self ):
        folder = self.folder
        head_id = "head_%d" % 0
        folder.invokeFactory( type_name='HTMLDocument',
                              id=head_id,
                              title=head_id,
                              description='test description',
                              category='Publication' )
        head=folder._getOb( head_id )
        link1 = "<a href=\"new_link\">New Link </a>"
        link2 = "<a href=\"new_link\">New Link </a>"
        text = "test_text1 %s test_text2 %s" % (link1, link2)
        head.edit( text_format="html", text=text, file="", safety_belt="" )
        head.reindexObject()
        self.assert_( folder.getBadLinks()!=[] )
        self.assertEqual( folder.getBadLinks()[0][1], 2 )
        text = "Test Text"
        head.edit( text_format="html", text=text, file="", safety_belt="" )
        head.reindexObject()
        self.assertEqual( folder.getBadLinks(), [] )
        folder.deleteObjects( [head_id] )
    
    def _delUser( self, members ):
        portal_membership = self.naudoc.portal_membership
        portal_membership.deleteMembers( members )
    
    def cookUserId( self, i ):
        return '%s%d' % ( 'Test_User', i )
    
    def beforeTearDown(self):
        del self.folder
        self.naudoc.storage.deleteObjects([self.folder_id])
        self._delUser( self.userids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )
    
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(FoldersCreationTests) )
    suite.addTest( makeSuite(FoldersTransferTests) )
    suite.addTest( makeSuite(FoldersDeletionTests) )
    suite.addTest( makeSuite(FolderTests) )
    suite.addTest( makeSuite(FolderFunctionalTests) )
    suite.addTest( makeSuite(FolderFuncTests) )
    return suite

if __name__ == '__main__':
    framework()
