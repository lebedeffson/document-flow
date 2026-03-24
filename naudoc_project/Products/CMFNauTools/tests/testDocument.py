#! /bin/env python2.3
"""
Create and destroy NauDoc documents. Measure time needed.

$Id: testDocument.py,v 1.9 2006/01/29 14:41:12 vsafronovich Exp $
"""
__version__='$Revision: 1.9 $'[11:-2]

import os, sys, random
import Configurator
import re as re

Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase

from Testing import ZopeTestCase

from DateTime import DateTime
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.Utils import getToolByName
from Products.CMFNauTools.Utils import getLanguageInfo

import AccessControl.SecurityManagement, AccessControl.SpecialUsers

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')

class DocumentCreationTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0
    document_base_name = 'ztc_test_document_'
    document_base_title = 'NauDoc test case document'
    number_of_documents = Constants.LARGE

    def testDocumentCreation(self):
        storage = self.naudoc.storage

        for i in range(self.number_of_documents):
            id = self.cookId( i )
            title = "%s %d" % (self.document_base_title, i)

            storage.invokeFactory( type_name='HTMLDocument',
                                       id=id,
                                       title=title,
                                       description='test description',
                                       category='Document' )

            #test that it was created
            obj = storage._getOb( id )

        get_transaction().commit()
        #XXX tests needed

    def cookId(self, i):
        return '%s%d' % (self.document_base_name, i)

    def beforeTearDown(self):
        #remove folders
        documents_ids = map(self.cookId, range(self.number_of_documents))
        self.naudoc.storage.deleteObjects( documents_ids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

document_text = \
"""
    Some text goes here.

    And here...

    And even here!
"""

document_text_with_links = \
"""
URL: <naudoc:this>

Attribute: <naudoc:field/ResponsAuthor>
"""

class DocumentEditTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0
    document_base_name = 'ztc_test_document_'
    document_base_title = 'NauDoc test case document'
    number_of_documents = Constants.SMALL

    def afterSetUp(self):
        self._create_documents()

    def testDocumentEdit(self):
        for i in range(self.number_of_documents):
            doc_id = self.cookId( i )
            document = self.naudoc.storage._getOb( doc_id )
            document._edit( document_text )
            self.assertEqual(document.CookedBody(), document_text)
        get_transaction().commit()

    def testDocumentActions(self):
        doc = self.naudoc.storage.objectValues( feature='isHTMLDocument' )[0]
        type = doc.getTypeInfo()

        getAction = type.getActionById
        for action_id, action in [ ('edit', 'document_edit_form')
                                 , ('view', 'document_view')
                                 ]:
            self.assertEquals( getAction(action_id), action )

    def testDocumentAttributeEdit(self):
        for i in range(self.number_of_documents):
            doc_id = self.cookId( i )
            document = self.naudoc.storage._getOb( doc_id )

            attrs = { 'MotiveAnnDoc' : 'test'
                    , 'DocInPlan' : True
                    , 'ImplementationDocDate' : DateTime(2005, 02, 15)
                    , 'ResponsAuthor' : ( NauDocTestCase.admin_name, )
               }
            document.setCategoryAttributes( attrs )

            self.assertEqual(document.getCategoryAttribute('MotiveAnnDoc'), 'test')
            self.assertEqual(document.getCategoryAttribute('ImplementationDocDate'), DateTime(2005, 02, 15))
            self.assert_(document.getCategoryAttribute('DocInPlan'))
            #XXX shoul userlist be tuple or a list ?
            self.assertEqual( tuple(document.getCategoryAttribute('ResponsAuthor')), (NauDocTestCase.admin_name, ))
        get_transaction().commit()

    def testReplaceLinks(self):
        document = self.getRandomDocument()
     
        document._edit( document_text_with_links )
  
        body = document.CookedBody(view=True)
        self.assert_( 'naudoc:this' not in body )
        self.assert_( 'class="category-attribute"' in body )

    def cookId(self, i):
        return "%s%d" % (self.document_base_name, i)

    def getRandomDocument(self):
        # XXX wrap naudoc, this must be done somewhere but not here
        naudoc = self.app._getOb(self.naudoc_id)
        id = self.cookId(random.choice(range(self.number_of_documents)))
        return naudoc._getOb('storage')._getOb( id )

    def _create_documents(self):
        storage = self.naudoc.storage

        for i in range(self.number_of_documents):
            title = "%s %d" % (self.document_base_title, i)
            doc_id=self.cookId(i)

            storage.invokeFactory( type_name='HTMLDocument',
                                       id=doc_id,
                                       title=title,
                                       description='test description',
                                       category='NormativeDocument' )

            #test that it was created
            obj = storage._getOb( doc_id )

        get_transaction().commit()


    def beforeTearDown(self):
        #remove documents
        documents_ids = map(self.cookId, range(self.number_of_documents))
        self.naudoc.storage.deleteObjects( documents_ids )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class Dummy:
    filename = None
    def __init__( self, fn='just/test.txt', text='TestText' ):
        self.filename=fn
        self.text = text
    def seek(t, a=None, b=None): pass
    def write(t): pass
    def close(): pass
    def fileno(): raise 'this sux'
    def flush(): pass
    def read(self, a=None, b=None): 
        if a:
            return self.text[a:]
        elif b:
            return self.text[:b]
        elif a and b:
            return self.text[a:b]
        else:
            return self.text
    def readline(): return ''
    def readlines(): return []
    def tell(t=None): return 0
    def truncate(i): pass
    def writelines(i): pass


class DocumentTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0

    def afterSetUp(self):

        self.naudoc.manage_addProduct['CMFNauTools'].addHTMLDocument('html_test'
                                                                    , category='Document')

        self.d = self.naudoc.html_test

    def check_insert(self, where, what, class_names, filename, html):
        #check add
        where.text = html
        where.addFile(what)
        if filename not in where.objectIds():
            self.fail('addFile did not attach file: ' + what.filename)
        #check classtype
        ok = 0
        for class_name in class_names:
            if str(getattr(where, filename).__class__).find(' '+class_name+' ') != -1:
                ok = 1
                break
        if not ok:
            self.fail('Wrong class of created file: ' + str(getattr(where, filename).__class__) )

    def check_delete(self, where, filename, text):
        where.text = text
        trimmed_html = where.removeFile(filename)
        trimmed_html = re.sub('\s', '', trimmed_html)
        self.assertEqual( where.text, '<body></body>', 'Link to deleted attach was not removed')
        if filename in where.objectIds() :
            self.fail('deleteFile did not remove file: ' + filename)

    def te_comment_st_AddFile_DelFile_PasteFile_ObjectIds_ObjectValues_ObjectItems(self):

        html_test = self.d

        fle1 = Dummy('just/test.txt')
        #just add and remove simple 'file'
        self.check_insert(html_test, fle1, ['OFS.Image.File'], 'test.txt', '<body></body>')
        #check pasteFile here
        ht1 = html_test.pasteFile('test.txt')
        ht11 = '<body><a href="test.txt">test</a></body>'
        self.assertEqual( ht11 , ht1 , 'link doesn''t inserted correctly(or format is changed):\n '+ ht1)
        self.check_delete(html_test, 'test.txt', ht1)

        #test type: html
        fle2 = Dummy('just/test.html')
        self.check_insert(html_test, fle2, ['OFS.DTMLDocument.DTMLDocument'], 'test.html', '<body></body>')
        ht2 = html_test.pasteFile('test.html')
        ht12 = '<body><a href="test.html">test</a></body>'
        self.assertEqual( ht12 , ht2 , 'link doesn''t inserted correctly(or format is changed):\n '+ ht2)
        self.check_delete(html_test, 'test.html', ht2)

        #test type: dtml
        fle3 = Dummy('just/test_html')
        self.check_insert(html_test, fle3, ['OFS.DTMLDocument.DTMLDocument'], 'test_html', '<body></body>')
        #check pasteFile here
        ht3 = html_test.pasteFile('test_html')
        ht13 ='<body><a href="test_html">test_html</a></body>'
        self.assertEqual( ht13 , ht3 , 'link doesn''t inserted correctly(or format is changed):\n '+ ht3)
        self.check_delete(html_test, 'test_html', ht3)

        #test type: gif
        fle4 = Dummy('just/test.gif')
        self.check_insert(html_test, fle4, ['Products.Photo.Photo.Photo', 'OFS.Image.Image'], 'test.gif', '<body></body>')
        #check pasteFile here
        ht4 = html_test.pasteFile('test.gif')
        ht14 ='<body><img src="test.gif" border=0></body>'
        self.assertEqual( ht14 , ht4 , 'link doesn''t inserted correctly(or format is changed):\n '+ ht4)
        self.check_delete(html_test, 'test.gif', ht4)

    def testRating(self):
        html_test = self.d
        html_test.rate(4)
                                    
        self.assert_(html_test.rated(), 'rated() error')
        self.assertEqual( html_test.get_rating(), 4 , 'get_rating error')

    def testListTabs(self):
        document = self.d

        tabs = document.listTabs()
        self.assert_( tabs is not None )
        self.assert_( len(tabs) > 4 )

        tabs = document.getVersion().listTabs()
        self.assert_( tabs is not None )
        self.assert_( len(tabs) > 4 )

    def testDocumentWithDiscussions(self):
        document = self.d

        pd = getToolByName( self.naudoc, 'portal_discussion' )
        pd.getDiscussionFor(document)

        self.assertEquals( document.talkback.replyCount( document ), 0 )
        self.assertEquals( document.talkback.replyCount( document.getVersion() ), 0 )

    def beforeTearDown(self):
        #remove document
        self.naudoc.deleteObjects( ['html_test'] )
        get_transaction().commit()
   
        del self.d

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class DocFunctionalTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):

        self.naudoc.storage.manage_addProduct['CMFNauTools'].addHTMLDocument('html_test'
                                                                    , category='Document')

        self.d = self.naudoc.storage.html_test

    def testMetadata(self):
        path = '/%s/metadata_edit_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testFollowupForm(self):
        path = '/%s/document_follow_up_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testEditForm(self):
        path = '/%s/document_edit_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testConfirmationForm(self):
        path = '/%s/document_confirmation_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testAttachesForm(self):
        path = '/%s/document_attaches' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testLinksForm(self):
        path = '/%s/document_link_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testChangeOwnerShipForm(self):
        path = '/%s/change_ownership_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testDistributionForm(self):
        path = '/%s/distribute_document_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )
     
    def testSubscriptionForm(self):
        path = '/%s/manage_document_subscription' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testDistributionLog(self):
        path = '/%s/distribution_log_form' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )
 
    def testWorkflowHistory(self):
        path = '/%s/document_workflow_history' % self.d.physical_path()
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def beforeTearDown(self):
        del self.d

        self.naudoc.storage.deleteObjects(['html_test'])
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )

class DocumentFunctionsTests( NauDocTestCase.NauFunctionalTestCase ):
    user_count = 3
    def afterSetUp(self):
        self.naudoc.storage.manage_addProduct['CMFNauTools'].addHTMLDocument('html_test'
                                                                    , category='Document')
        self.d = self.naudoc.storage.html_test
        self.userids = []
        get_transaction().commit()

    def testLanguage(self):
        document = self.d
        self.assertEqual( document.Language(), 'ru' )
        
    def testGetFontFamily(self):
        document = self.d
        self.assert_( document.getFontFamily() is not None )

    def testContentOperations(self):
        document = self.d
        self.assert_( document.isContentEmpty() )
        self.assertEqual( document.getContentsSize(), 0 )
        text = "Test Text"
        document.edit( text_format="html", text=text, file="", safety_belt="")
        self.assertEqual( document.getContentsSize(), len(text) )
        self.assert_( not document.isContentEmpty() )
        #test file content
        file_text = "This is Text of File"
        file = Dummy( fn="test_file.txt", text=file_text)
        document.edit( text_format="html", text=text, file=file, safety_belt="")
        self.assertEqual( document.getContentsSize(), len(file_text) )
    
    def testBodyOperations( self ):
        document = self.d
        #document.FormattedBody( html=1, width=None, canonical=None, REQUEST=None )
        text = "LONGTestText"
        document.edit( text_format="html", text=text, file="", safety_belt="" )
        self.assertEqual( document.CookedBody(), text )
        self.assert_( ("%s\n</body>" % text) in \
                          document.FormattedBody( html=1
                                                  , width=5
                                                  , canonical=None
                                                  , REQUEST=None )
                      )
        self.assertEqual( document.EditableBody(), text )
        self.assert_( "<html>" in document.FormattedBody( html=0,
                                                              width=None,
                                                              canonical=None,
                                                              REQUEST=None ),
                      )
        document.edit( text_format="text", text=text, file="", safety_belt="" )
        self.assert_( "<html>" not in document.FormattedBody( html=0,
                                                              width=None,
                                                              canonical=None,
                                                              REQUEST=None ),
                          )
        
    def testListBodyFields( self ):
        document = self.d
        string = "wqewqe"
        text = "LONGTestText naudoc:field/%s naudoc:field/qweqwe naudoc:fieldssss " % string
        document.edit( text_format="html", text=text, file="", safety_belt="" )
        self.assertEqual( document.listBodyFields(), [string, 'qweqwe'] )
    
    def testAssociatingAndAttachmenting( self ):
        for number in range( self.user_count ):
            self._addUser( number )
        document = self.d
        user1 = self.userids[1]
        user0 = self.userids[0]
        document.setLocalRoles(user0, ('Editor', 'Owner'))
        document.setLocalRoles(user1, ('Reader'))
        self.login( user0 )
        self.assert_( document.getAssociatedAttachment() is None )
        # Create files
        file1_text = "Text1"
        file2_text = "Text2"
        test_file = Dummy( fn='text.txt', text=file1_text )
        test_file2 = Dummy( fn='text2.txt', text=file2_text )
        #add file without association
        file1 = document.addFile( test_file )
        self.assert_( document.getAssociatedAttachment() is None )
        #add file with association
        file2 = document.addFile( file=test_file2, associate=True )
        self.assertEqual( str(document.getAssociatedAttachment()), file2_text )
        self.assert_( document.associateWithAttach( id=file1, optional=False ) )
        self.assertEqual( str(document.getAssociatedAttachment()), file1_text )
        #test remove association
        document.removeAssociation(id=file2)
        self.assertEqual( str(document.getAssociatedAttachment()), file1_text )
        document.removeAssociation(id=file1)
        self.assert_( document.getAssociatedAttachment() is None )
        #check Attacments in Attachment list
        self.assert_( ( (file1, document[file1]) in document.listAttachments() ) and \
                          ( (file2, document[file2]) in document.listAttachments() )
                      )
        #test remove Attachment
        document.removeFile( file1 )
        self.assert_( len(document.listAttachments()) == 1 )
        #test lock Attachment
        self.assertEqual(document.lockAttachment( file2 ), 1)
        file1 = document.addFile( test_file )
        self.login( user1 )
        file = document[ file2 ]
        file.text = 'NewText'
        document.removeFile( file2 )
        self.login( user0 )
        document.removeFile( file1 )
        self.assert_( document.getAssociatedAttachment() is None )
        self.login()
    
    def testSubscription( self ):
        for number in range( self.user_count ):
            self._addUser( number )
        transitions = {}
        subscr_user_num = 1
        subscr_user_num2 = 0
        #add Subsribtion type for Users
        for i in range( self.user_count ):
            if i==subscr_user_num:
                transitions[i] = [ 'copy', 'paste' ]
            elif i==subscr_user_num2:
                transitions[i] = [ 'copy' ]
            else:
                transitions[i] = []
        
        transition = transitions[subscr_user_num]
        REQUEST = self.app.REQUEST
        REQUEST[ 'changes' ] = True
        REQUEST[ 'transitions' ] = transition
        document = self.d
        self.login( self.userids[subscr_user_num] )
        document.subscribe( REQUEST=REQUEST )
        for i in range( self.user_count ):
            self.login( self.userids[i] )
            self.assertEqual( document.isSubscribed(), i==subscr_user_num )
        self.login( self.userids[subscr_user_num2] )
        transition = transitions[subscr_user_num2]
        REQUEST[ 'changes' ] = False
        REQUEST[ 'transitions' ] = transition
        document.subscribe( REQUEST=REQUEST )
        # test pointed subscr
        for i in range( self.user_count ):
            usub = document.getUserSubscription( username=self.userids[i] )
            result = [( int( k in usub ) ) for k in transitions[i] ]
            result = sum( result )
            self.assert_( result==len( transitions[i] ) )
            self.login( self.userids[i] )
            self.assertEqual( document.isSubscribed( transition_id='copy' ),
                              ( i==subscr_user_num ) or ( i==subscr_user_num2 ) )
            self.assertEqual( document.isSubscribed( transition_id='paste' ),
                              (i==subscr_user_num) )
        #test subscribtionlist
        subscr_users_list = document.listSubscribedUsers()
        result = [(int ( k in self.userids ) ) for k in subscr_users_list ]
        result = sum( result )
        self.assert_( result==2 )
        self.login()
        
    def testManage_FTPget( self ):
        document = self.d
        text = "New HTML TEXT"
        document.edit( text_format="html", text=text, file="", safety_belt="" )
        self.assert_( "<html>" in document.manage_FTPget() )
        text = "New PLAIN TEXT"
        document.edit( text_format="text", text=text, file="", safety_belt="" )
        self.assert_( "<html>" not in document.manage_FTPget() )
        
    
    def testGetField( self ):
        document = self.d
        self.naudoc.storage.manage_addProduct['CMFNauTools'].addHTMLDocument('test_nd'
                                                                    , category='NormativeDocument')
        pub = self.naudoc.storage.test_nd
        document.createVersion( ver_id='21' )
        field = pub.getField("CodeDoc")
        self.assert_( ("was removed from document category" not in field) and \
                      ("you are not allowed to read" not in field) )
        self.naudoc.storage.deleteObjects(['test_nd'])
        field = document.getField("CodeDoc")
        self.assert_( ("was removed from document category" in field) or \
                      ("you are not allowed to read" in field) )
        
        
    def testGetChangesFrom( self ):
        self.naudoc.storage.manage_addProduct['CMFNauTools'].addHTMLDocument('html_test2'
                                                                    , category='Document')
        document = self.naudoc.storage.html_test2
        text1 = "Test"
        text2 = "%s %s" % (text1, "Append")
        document.edit( text_format="html", text=text1, file="", safety_belt="" )
        #get changes from Text
        diff = document.getChangesFrom( other=None, text=text2 )
        self.assertEqual( '%s<span class="diff_inserted"> Append</span>' % text1, diff )
        document.createVersion( ver_id='21' )
        version1 = document.getCurrentVersionId()
        v1 = document.getVersion( version1 )
        v2 = document.getEditableVersion()
        v2.makeCurrent()
        version2 = document.getCurrentVersionId()
        document.activateCurrentVersion()
        document.edit( text_format="html", text=text2, file="", safety_belt="" )
        #get changes from another Version
        diff = document.getChangesFrom( other=document.getVersion(version1) )
        self.assertEqual( '%s<span class="diff_inserted"> Append</span>' % text1, diff )
        v1.makeCurrent()
        document.activateCurrentVersion()
        #get changes from another Version
        diff =  document.getChangesFrom( other=document.getVersion(version2) )
        self.assertEqual( '%s<span class="diff_deleted"> Append</span>' % text1, diff )
        #compare version_0.1 with version_0.1
        document.activateCurrentVersion()
        diff =  document.getChangesFrom( other=document.getVersion("version_0.1") )
        self.assertEqual( text1, diff )
        self.naudoc.storage.deleteObjects(['html_test2'])
    
    def testReindexObject( self ):
        document = self.d
        document.reindexObject()
        catalog = getToolByName( self.naudoc.storage, 'portal_catalog' )
        document.title = "New"
        catalog_title = catalog.getMetadataForUID( document.physical_path() )['Title']
        self.assert_( catalog_title!=document.title )
        document.reindexObject(idxs=['state'])
        catalog_title = catalog.getMetadataForUID( document.physical_path() )['Title']
        self.assert_( catalog_title==document.title )
        
    def cookUserId( self, i ):
        return '%s%d' % ( 'Test_User', i )
    
    def beforeTearDown(self):
        del self.d
        self.naudoc.storage.deleteObjects(['html_test'])
        self.naudoc.portal_membership.deleteMembers( self.userids )
        get_transaction().commit()
        NauDocTestCase.NauDocTestCase.beforeTearDown( self )
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(DocumentCreationTests) )
    suite.addTest( makeSuite(DocumentEditTests) )
    suite.addTest( makeSuite(DocumentTests) )
    suite.addTest( makeSuite(DocFunctionalTests) )
    suite.addTest( makeSuite(DocumentFunctionsTests) )
    return suite

if __name__ == '__main__':
    framework()
