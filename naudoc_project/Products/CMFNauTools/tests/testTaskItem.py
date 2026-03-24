import os, sys, random, DateTime.DateTime
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
#ZopeTestCase.installProduct('TextIndexNG2')

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

class TaskItemTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    user_count = 3
    doc = None
    def afterSetUp(self):
        #create TaskItemContainer
        self.userids = []
        for i in range( self.user_count ):
            self._addUser(i)
        folder = self.naudoc.storage
        doc_id = 'Test_Doc'
        title = doc_id
        folder.invokeFactory( type_name='HTMLDocument'
                             ,id=doc_id
                             ,title=title
                             ,description='test description'
                             ,category='Document'
                            )
        doc = folder._getOb(doc_id)
        self.task_container = getToolByName( doc, 'portal_followup' )
        self.task_container = self.task_container._createFollowupFor( doc )
        self.task_id = self._addTask( self.task_container )
        self.task = self.task_container.getTask( self.task_id )
        self.doc = doc
        get_transaction().commit()
    
    def testCreatorSupervisor( self ):
        task = self.task
        task_id = self.task_id
        self.assertEqual( task.Creator(), self.log_as_user )
        self.assertEqual( task.Supervisor(), None )
        task.setSupervisor( self.userids[0] )
        self.assertEqual( task.Supervisor(), self.userids[0] )
        self.assert_( not task.isSupervisor() )
        self.assert_( task.isSupervisor( user=self.userids[0] ) )
        self.assert_( task.isCreator() )
        self.assert_( not task.isCreator( user=self.userids[0] ) )
    
    def testCanSendNotifications( self ):
        task = self.task
        task_id = self.task_id
        self.assert_( task.canSendNotifications() )
        self.login( self.userids[0] )
        self.assert_( not task.canSendNotifications() )
        task.setSupervisor( self.userids[0] )
        self.assert_( task.canSendNotifications() )
        task.Finalize( result_code="success", safe=Trust )
        self.assert_( not task.canSendNotifications() )
        self.login()
    
    def testEnableDisable( self ):
        task = self.task
        task_id = self.task_id
        enabled = task.isEnabled()
        task.Enable( no_mail=True )
        self.assert_( task.isEnabled() )
        task.Disable()
        self.assert_( not task.isEnabled() )
    
    def testDocumentParameters( self ):
        task = self.task
        task_id = self.task_id
        self.assertEqual( task.DocumentCategory(), "Document" )
        self.assertEqual( task.DocumentFolder(), self.naudoc.storage.Title() )
    
    def testListResultCodes( self ):
        task = self.task
        manual = 0
        result_codes_not_manual = task.listResultCodes( manual=manual )
        manual = 1
        result_codes_manual = task.listResultCodes( manual=manual )
        self.assertEqual( result_codes_manual, result_codes_not_manual )
        new_task_id = self._addTask( self.task_container, brains_type="request" )
        new_task = self.task_container.getTask( new_task_id )
        manual = 0
        result_codes_not_manual = new_task.listResultCodes( manual=manual )
        manual = 1
        result_codes_manual = new_task.listResultCodes( manual=manual )
        self.assert_( result_codes_manual != result_codes_not_manual )
    
    def testUsers( self ):
        task = self.task
        #create Groups
        group = "NewGroup"
        REQUEST =self.app.REQUEST
        REQUEST['addGroup'] = True
        REQUEST['group'] = group
        self.naudoc.portal_membership.manage_groups( REQUEST=REQUEST )
        self.naudoc.portal_membership.manage_changeGroup( group=group,
                                                          group_users=self.\
                                                          userids[0:(self.user_count-1)],
                                                          title=None, REQUEST=None)
        #test Users function
        userids = []
        count = 3
        flatten = False
        flatten_groups = False
        users_list = task.listInvolvedUsers( flatten=flatten, flatten_groups=flatten_groups )
        self.assertEqual( self.userids, users_list )
        self.assert_( task.isInvolved( self.userids[0] ) )
        self.assert_( not task.isInvolved( self.log_as_user ) )
        self.assertEqual( task.listPendingUsers(), self.userids )
        self.assertEqual( task.listRespondedUsers(), [] )
        self.login( self.userids[0] )
        task.Respond( status="informed", REQUEST=REQUEST )
        self.assertEqual( task.listPendingUsers(), self.userids[1:self.user_count] )
        self.assertEqual( task.listRespondedUsers(), [self.userids[0]] )
        self.login()
        for i in range( count ):
            userids.append( "group:%s" % (group) )
        #test setInvolvedUsers
        task.setInvolvedUsers( userids )
        self.assertEqual( task.listInvolvedUsers(), userids )
        #test flatten
        flatten = True
        flatten_groups = False
        users_list = task.listInvolvedUsers( flatten=flatten, flatten_groups=flatten_groups )
        self.assertEqual( self.userids[0:(self.user_count-1)] , users_list )
        #test group_flatten
        userids = []
        for i in range( count ):
            userids.append( "group:%s" % (group) )
        task.involved_users = userids
        flatten = False
        flatten_groups = True
        users_list = task.listInvolvedUsers( flatten=flatten, flatten_groups=flatten_groups )
        self.assertEqual( (self.userids[0:(self.user_count-1)])*count , users_list )
        self.naudoc.portal_membership.manage_changeGroup( group=group,
                                                          group_users=[],
                                                          title=None, REQUEST=None)
        REQUEST['delGroup'] = True
        REQUEST['groups'] = [group]
        self.naudoc.portal_membership.manage_groups( REQUEST=REQUEST )
    
    def testBrainsType( self ):
        task = self.task
        self.assertEqual( task.BrainsType(), "information" )
        brains_type = "directive"
        new_task_id = self._addTask( self.task_container, brains_type=brains_type )
        new_task = self.task_container.getTask( new_task_id )
        self.assertEqual( new_task.BrainsType(), brains_type )
    
    def testAttachedFilesObjectIds( self ):
        task = self.task
        self.assertEqual( task.objectIds(), [] )
        self.assertEqual( task.listAttachedFiles(), [] )
        file = Dummy()
        task.attachFile( file=file )
        self.assert_( task.objectIds() is not None )
        self.assert_( task.listAttachedFiles() is not None )
    
    def testCanRespond( self ):
        task = self.task
        brains_type = "directive"
        new_task_id = self._addTask( self.task_container, brains_type=brains_type )
        new_task = self.task_container.getTask( new_task_id )
        #test canRespond by involved user
        self.login( self.userids[0] )
        status="informed"
        self.assert_( task.canRespond( status=status ) )
        status="reject"
        self.assert_( new_task.canRespond( status=status ) )
        #test canRespond with not existed status
        false_status = "False Status"
        self.assert_( not task.canRespond( status=false_status ) )
        #test canRespond by not involved user
        self.login()
        status="informed"
        self.assert_( not task.canRespond( status=status ) )
        status="reject"
        self.assert_( not new_task.canRespond( status=status ) )
    
    def testSeenBy( self ):
        task = self.task
        REQUEST = self.app.REQUEST
        self.assertEqual( task.SeenBy(), [] )
        portal_followup = getToolByName( task, 'portal_followup', None )
        logger = portal_followup.getLogger()
        for i in self.userids:
            self.login( i )
            logger.addSeenByFor( task, i )
            task.Respond( status="informed", REQUEST=REQUEST )
        self.assertEqual( task.SeenBy(), self.userids )
        self.login()
        
    def testResultCode(self ):
        task = self.task
        self.assert_( task.ResultCode() is None )
        result_code = "success"
        safe = Trust
        task.Finalize( result_code=result_code, safe=safe )
        self.assertEqual( task.ResultCode(), result_code )
    
    def testStateKeysOpenReportSearchResponses( self ):
        #task = self.task
        new_task_id = self._addTask( self.task_container, brains_type="directive" )
        new_task = self.task_container.getTask( new_task_id )
        self.assert_( not bool( len( new_task.StateKeys() ) ) )
        closed_report = 1
        status = "commit"
        REQUEST = self.app.REQUEST
        user = self.userids[0]
        self.login( user )
        new_task.Respond( status=status, REQUEST=REQUEST, text="responded",\
                          close_report=closed_report )
        responses = [ (c["response_id"], c["isclosed"]) for\
                      c in new_task.searchResponses( uname=user ) ]
        self.assertEqual( responses, [(1, closed_report)] )
        self.login()
        res = new_task.StateKeys()
        self.assert_( sum( [ self.userids[0] in i for i in res] ) )
        new_task.OpenReportFor( user )
        responses = [ (c["response_id"], c["isclosed"]) for\
                      c in new_task.searchResponses( uname=user ) ]
        self.assertEqual( (2, 0) in responses, True )
        self.assertEqual( new_task.StateKeys(), res*2 )
        
    def testGetPhysicalPathGetBase( self ):
        task = self.task
        self.assertEqual( task.getPhysicalPath(), tuple( task.physical_path().split("/") ) )
        self.assertEqual( task.getBase(), self.doc )
    
    def testGetFinalizationMode( self ):
        task = self.task
        self.assertEqual( task.getFinalizationMode(), "manual_creator" )
    
    def testClosed( self ):
        task = self.task
        self.assert_( not task.isClosed() )
        closed_report = "Report is closed"
        status = "informed"
        REQUEST = self.app.REQUEST
        for user in self.userids:
            self.login( user )
            task.Respond( status=status, REQUEST=REQUEST, text="responded",\
                          close_report=closed_report )
        self.assert_( task.isClosed() )
        self.login()
    
    def testResponse( self ):
        brains_type = "directive"
        new_task_id = self._addTask( self.task_container, brains_type=brains_type )
        new_task = self.task_container.getTask( new_task_id )
        response_list = new_task.listAllowedResponseTypes( uname=self.userids[0] )
        for respond_type_id in response_list:
            self.assert_( new_task.getResponseTypeById( respond_type_id["id"] ) is not None )
        false_response_type_id = "test_id"
        self.assert_( new_task.getResponseTypeById( false_response_type_id ) is None )
        self.assert_( not len(new_task.listResponseTypes()) )
        for i in range( len( response_list ) ):
            respond_type_id = response_list[i]["id"]
            self.login( self.userids[i % self.user_count] )
            status = respond_type_id
            REQUEST = self.app.REQUEST
            new_task.Respond( status=status, REQUEST=REQUEST, text="responded")
            self.assertEqual( new_task.get_responses().getIndexKeys("member"),
                              self.userids[:(i+1)] )
        self.assertEqual( len(response_list), len(new_task.listResponseTypes()) )
        self.login()
    
    def testFinalizeStartedEditable( self ):
        task = self.task
        self.assert_( not task.isFinalized() )
        self.assert_( task.isEditable() )
        
        self.login( self.userids[0] )
        status = "informed"
        REQUEST = self.app.REQUEST
        task.Respond( status=status, REQUEST=REQUEST, text="responded")
        self.assert_( task.isStarted() )
        self.login()
        status = "finalize"
        REQUEST = self.app.REQUEST
        task.Respond( status=status, REQUEST=REQUEST, text="responded")
        self.assert_( task.isFinalized() )
        self.assert_( not task.isEditable() )
        
        brains_type = "request"
        new_task_id = self._addTask( self.task_container, brains_type=brains_type )
        new_task = self.task_container.getTask( new_task_id )
        self.assert_( not new_task.isFinalized() )
        new_task.Finalize( result_code="success", safe=Trust )
        self.assert_( new_task.isFinalized() )
    
    def testAlarms( self ):
        task = self.task
        alarm_id = task._alarm_schedule_id
        settings = None
        task.setAlarm( settings=settings )
        self.assertEqual( task._alarm_schedule_id, alarm_id )
        #task.Alarm()
        settings = {}
        settings["type"] = 'percents'
        settings["value"] = 10
        task.setAlarm( settings=settings )
        self.assert_( task._alarm_schedule_id != alarm_id )
        task.stopSchedule()
        self.assertEqual( task._alarm_schedule_id, alarm_id )
        settings = {}
        effective_date = DateTime.DateTime()
        expiration_date = DateTime.DateTime()
        settings["type"] = 'percents'
        settings["value"] = 10
        task.setAlarm( settings=settings )
        task.setEffectiveDate( effective_date )
        task.setExpirationDate( expiration_date )
        task.resetSchedule()
        self.assert_( task._alarm_schedule_id != alarm_id )
        self.assertEqual( task.effective_date, effective_date )
    
    def testLevels( self ):
        brains_type = "elaborated"
        new_task_id = self._addTask( self.task_container, brains_type=brains_type )
        new_task = self.task_container.getTask( new_task_id )
        task_count = 5
        brains_types = ["information"] * task_count
        task_list = []
        for i in range( len( brains_types ) ):
            title = "New Information Task%d" % i
            brains_type = brains_types[i]
            duration = Constants.HUGE
            involved_users = self.userids
            kw = {'duration':duration,"involved_users":involved_users,'brains_type':brains_type,
                  "description":'he-he'}
            task = kw
            task_list.append( task )
        
        new_task.elaborate( items=task_list )
        leveled_tree = new_task.getLeveledTaskTree()
        self.assert_( len( leveled_tree ) == (task_count+1) )
        self.assertEqual( new_task.findRootTask().getId(), new_task_id )
        self.assertEqual( leveled_tree[task_count].findRootTask().getId(), new_task_id )
        self.assertEqual( leveled_tree[task_count].getLevel(), 2 )
        self.assertEqual( leveled_tree[0].getLevel(), 0 )
    
    def testViewer( self ):
        task = self.task
        for user in self.userids:
            self.assert_( task.isViewer( user=user ) )
        user = self._addUser( (self.user_count + 5) )
        self.assert_( task.isViewer() )
        self.login( user )
        self.assert_( not task.isViewer() )
        self.login()
        self.assert_( not task.isViewer( user=user ) )
    
    def testListUsersWithClosedReports( self ):
        task = self.task
        for user in self.userids:
            self.login( user )
            status = "informed"
            REQUEST = self.app.REQUEST
            task.Respond( status=status, REQUEST=REQUEST, text="responded", close_report=1 )
        self.login()
        self.assertEqual( task.listUsersWithClosedReports(), self.userids )
    
    def testGetSourceAction( self ):
        task_id = self._addTask( self.task_container )
        task = self.task_container.getTask( task_id )
        task_template_id = "task_template_id"
        self.assert_( task.getSourceAction() is None )
        task_id = self._addTask( self.task_container, task_template_id=task_template_id )
        task = self.task_container.getTask( task_id )
        self.assertEqual( task.getSourceAction(), task_template_id )
        new_task_template_id = "new_task_template_id"
        task.setSourceAction( action=new_task_template_id )
        self.assertEqual( task.getSourceAction(), new_task_template_id )
    
    def testBinding( self ):
        task = self.task
        self.assertEqual( task.isBoundTo().getId(), self.doc.getId() )
        #create new tasks
        new_task1_id = self._addTask( self.task_container )
        new_task1 = self.task_container.getTask( new_task1_id )
        new_task2_id = self._addTask( self.task_container )
        new_task2 = self.task_container.getTask( new_task2_id )
        #bind task to new tasks
        task.BindTo( bind_to=new_task1 )
        self.assertEqual( task.isBoundTo(), new_task1 )
        task_id = self._addTask( self.task_container, bind_to=new_task1_id )
        task = self.task_container.getTask( task_id )
        self.assertEqual( task.isBoundTo(), new_task1 )
        task.BindTo( bind_to=new_task2 )
        self.assertEqual( [c.id for c in task.parentsInThread()], [ self.doc.id, new_task2.id ] )
    
    def testGetResultById( self ):
        task = self.task
        id = "success"
        self.assert_( task.getResultById( id=id ) is not None )
    
    def testDates( self ):
        task = self.task
        effective_date = DateTime.DateTime()
        expiration_date = DateTime.DateTime()
        task.setEffectiveDate( effective_date )
        task.setExpirationDate( expiration_date )
        self.assertEqual( task.effective_date, effective_date )
        self.assertEqual( task.expiration_date, expiration_date )
    
    def testPortalType( self ):
        task = self.task
        self.assertEqual( task.portal_type, task.BrainsType() )
    
    def testGetHistory( self ):
        task = self.task
        self.assertEqual( task.getHistory(), [] )
        selected_users = self.userids[0:(self.user_count-1)]
        text = "Test Text"
        task.KickUsers(selected_users, text)
        self.assertEqual( task.getHistory()[0]["rcpt"], selected_users )
        self.assertEqual( task.getHistory()[0]["actor"], self.log_as_user )
    
    def testValidate( self ):
        task = self.task
        new_user = self._addUser( self.user_count+1 )
        self.assert_( task.validate() )
        self.login( new_user )
        self.assert_( not task.validate() )
        self.login()
    
    def testEdit( self ):
        task = self.task
        title = "new_task_title"
        kw = {"title":title}
        task.edit( **kw )
        self.assertEqual( task.title, title )
        portal_followup = getToolByName(task, 'portal_followup', None)
        new_title = "new_title"
        task.setTitle( new_title )
        portal_title = portal_followup.getMetadataForUID( task.physical_path() )['Title']
        self.assert_( task.Title()!=portal_title )
        task.updateIndexes()
        portal_title = portal_followup.getMetadataForUID( task.physical_path() )['Title']
        self.assertEqual( task.Title(), portal_title )
    
    def testAlarm( self ):
        task = self.task
        task.Alarm()
    
    def testDeleteObject( self ):
        task = self.task
        self.assertEqual( self.task_container.objectIds(), [task.id] )
        task.deleteObject()
        self.assertEqual( self.task_container.objectIds(), [] )
    
    def _addTask( self, where, bind_to=None, brains_type=None, task_template_id=None ):
        if brains_type is None:
            brains_type = "information"
        duration = 100
        description = 'description'
        title = "test title"
        involved_users =  self.userids[0:self.user_count]
        params = { 'description'       : description,
                   'involved_users'    : involved_users,
                   'duration'          : duration,
                   "bind_to"           : bind_to
                   }
        if task_template_id:
            params["task_template_id"] = task_template_id
        if brains_type == "elaborated":
            params["items"]= []
        if brains_type == "directive":
            params["plan_time"] = 10
        task = where.createTask( title=title,
                                 type=brains_type,
                                 **params
                                 )
        return task
    
    def cookId( self, i ):
        return 'D%s' % i
    
    def beforeTearDown( self ):
        folder = self.naudoc.storage
        self.task_container.deleteTask( self.task_id )
        self.naudoc.portal_membership.deleteMembers( self.userids )
        self.naudoc.storage.deleteObjects(['Test_Doc'])
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown(self)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TaskItemTests))
    return suite

if __name__ == '__main__':
    framework()