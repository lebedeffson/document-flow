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

class TaskItemContainerTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    user_count = 3
    doc = None
    task_duration = 0
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
        self.doc = doc
        get_transaction().commit()
    
    def testObjectValuesObjectItemsObjectIdsGetTaskDeleteTask( self ):
        task_container = self.task_container
        self.assertEqual( task_container.objectValues(), [] )
        self.assertEqual( task_container.objectIds(), [] )
        self.assertEqual( task_container.objectItems(), [] )
        #add task
        where = task_container
        test_task = self._addTask( where=where )
        #test functions
        self.assertEqual( task_container.objectValues(),
                          [ task_container.getTask( test_task ) ]
                          )
        self.assertEqual( task_container.objectItems(),
                          [(test_task, task_container.getTask( test_task ))]
                          )
        self.assertEqual( task_container.objectIds(), [ test_task ] )
        task_container.deleteTask( test_task )
        self.assertEqual( task_container.objectValues(), [] )
        self.assertEqual( task_container.objectIds(), [] )
        self.assertEqual( task_container.objectItems(), [] )
    
    def testBoundTasks( self ):
        task_container = self.task_container
        self.assertEqual( task_container.getBoundTasks(), [] )
        self.assertEqual( task_container.getBoundTaskIds(), [] )
        doc = self.doc
        folder = self.naudoc.storage
        tasks = []
        where = task_container
        test_task = self._addTask( where=where )
        tasks.append( test_task )
        self.assertEqual( task_container.getBoundTasks(), [task_container.getTask( test_task )] )
        #Create New Version of Document
        doc.createVersion( ver_id='21' )
        version1 = doc.getCurrentVersionId()
        v1 = doc.getVersion( version1 )
        v2 = doc.getEditableVersion()
        v2.makeCurrent()
        version2 = doc.getCurrentVersionId()
        doc.activateCurrentVersion()
        #create task for new version
        where = task_container
        test_task = self._addTask( where=where )
        tasks.append( test_task )
        #test for all versions
        bound_tasks = task_container.getBoundTasks()
        bound_taskids = task_container.getBoundTaskIds()
        res = [ i for i in tasks if task_container.getTask( i ) in bound_tasks ]
        res_id = [ i for i in tasks if i in bound_taskids ]
        self.assertEqual( res, tasks )
        self.assertEqual( res_id, tasks )
        #test for version1
        bound_tasks = task_container.getBoundTasks( version_id=version1 )
        self.assertEqual( bound_tasks, [task_container.getTask( tasks[0] )] )
        bound_taskids = task_container.getBoundTaskIds( version_id=version1 )
        self.assertEqual( bound_taskids, [ tasks[0] ] )
        #test for version2
        bound_tasks = task_container.getBoundTasks( version_id=version2 )
        self.assertEqual( bound_tasks, [task_container.getTask( tasks[1] )] )
        bound_taskids = task_container.getBoundTaskIds( version_id=version2 )
        self.assertEqual( bound_taskids, [ tasks[1] ] )
        #restore version_0.1 as current
        v1.makeCurrent()
        doc.activateCurrentVersion()
    
    def testBoundTaskRecursive( self ):
        task_container = self.task_container
        doc = self.doc
        folder = self.naudoc.storage
        tasks = []
        where = task_container
        test_task_id = self._addTask( where=where, brains_type="elaborated" )
        test_task = task_container.getTask( test_task_id )
        tasks.append( test_task )
        title = "New Information Task"
        duration = self.task_duration
        involved_users = [self.userids[0]]
        kw = {'duration':duration,"involved_users":involved_users,'brains_type':"information",
              "description":'he-he', "expiration_date":DateTime.DateTime()}
        test_task.elaborate([kw])
        self.assertEqual( len( task_container.getBoundTasks( recursive=1 ) ), 2 )
        self.assertEqual( len( task_container.getBoundTasks( recursive=None ) ), 1 )
    
    def _addTask( self, where, bind_to=None, brains_type=None ):
        if brains_type is None:
            brains_type = "information"
        duration = 100
        description = 'description'
        title = "test title"
        params = { 'description'       : description,
                   'involved_users'    : self.userids,
                   'duration'          : duration,
                   "bind_to"           : bind_to
                   }
        if brains_type == "elaborated":
            params["items"]= []
        task = where.createTask( title=title,
                                 type=brains_type,
                                 **params
                                 )
        return task
    
    def cookId( self, i ):
        return 'D%s' % i
    
    def beforeTearDown( self ):
        folder = self.naudoc.storage
        self.naudoc.portal_membership.deleteMembers( self.userids )
        self.naudoc.storage.deleteObjects(['Test_Doc'])
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown(self)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TaskItemContainerTests))
    return suite

if __name__ == '__main__':
    framework()