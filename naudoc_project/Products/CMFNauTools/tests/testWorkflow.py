#! /bin/env python2.3
"""
setup:

    Creates 'ztc_test_category' category with transition 'ztc_test_transition'
    and task template 'ztc_registry_version'.

    Creates 'ztc_registry' Registry book for that category.

    Creates documents of that category .

test:
    Makes transition 'ztc_test_transition' for each created document.

    Makes checks:
        check correct transitions
        check registrations in registry book
        check workflow history


$Id: testWorkflow.py,v 1.2 2006/03/06 14:33:42 vsafronovich Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

import os, sys
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase
from Testing import ZopeTestCase

from Acquisition import aq_base
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.Utils import getToolByName
from Products.CMFNauTools.DefaultWorkflows import setupWorkflowVars, assignActionTemplateToTransition

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')

class DocumentWorkflowTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = False

    number_of_documents = Constants.LARGE

    document_base_name = 'ztc_test_document_'
    document_base_title = 'NauDoc test case document'

    registry_id = 'ztc_registry'
    registry_uid = None

    category_id = 'ztc_test_category'
    state_id1 = 'ztc_test_state_1'
    state_id2 = 'ztc_test_state_2'
    transition_id = 'ztc_test_transition'

    def afterSetUp(self):
        self._setup_category()
        self._create_registry()
        self._assign_tasktemplate()
        self._create_docs()

    def cookId(self, i):
        return "%s%d" % (self.document_base_name, i)

    def testWorkflow(self):

        self.make_transitions()

        #check correct transitions
        storage = self.naudoc.storage
        portal_workflow = storage.portal_workflow
        for i in range( self.number_of_documents ):
            document = storage._getOb( self.cookId(i) )
            self.assertEqual(portal_workflow.getInfoFor( document, 'state', ''), self.state_id2)
            self.assert_( len(document.followup.objectIds())>0 )
            self.assertEqual( document.followup.objectIds(), ['task_001'] )
            task = document.followup.objectValues()[0]
            self.assertEqual( task.meta_type, 'Informational Task' )

        #check registrations
        valid_ids = map(self.cookId, range(self.number_of_documents))

        registered_ids = []
        registry=storage._getOb( self.registry_id )
        for entry in registry.searchEntries():
            registered_object = entry['target'].getObject()
            registered_ids.append( registered_object.getVersionable().getId() )

        valid_ids.sort() #unnecessary
        registered_ids.sort()
        self.assertEqual( registered_ids, valid_ids )

        #check workflow history
        valid_states = [ self.state_id1, self.state_id2 ]
        valid_states.sort()
        for i in range(self.number_of_documents):
            document = storage._getOb( self.cookId(i) )
            document_wh = document.getWorkflowHistory()
            wh_states = [wh_item['state'] for wh_item in document_wh]
            wh_states.sort()
            self.assertEqual( wh_states, valid_states)


    def make_transitions(self):
        storage = self.naudoc.storage
        for i in range( self.number_of_documents ):
            document = storage._getOb( self.cookId(i) )
            storage.portal_workflow.doActionFor( document.getVersionable(), \
                self.transition_id, comment='comment' )
        get_transaction().commit()


    def _setup_category(self):
        mdtool = getToolByName( self.naudoc, 'portal_metadata' )
        if not mdtool.getCategoryById( self.category_id ):
            category = mdtool.addCategory( self.category_id, self.category_id, default_workflow=0, allowed_types=['HTMLDocument'] )
            category.setBases(['SimpleDocument'])
            wf=category.getWorkflow()
            wf.setProperties(title="%s workflow" % self.category_id)
            wf.states.addState( self.state_id1 )
            wf.states.addState( self.state_id2 )
            wf.transitions.addTransition(self.transition_id) #self.state_id1 -> self.state_id2
            setupWorkflowVars(wf)
            wf.states.setInitialState( self.state_id1 )
            sdef = wf.states[ self.state_id1 ]
            sdef.setProperties(
                                title=self.state_id1,
                                transitions=(self.transition_id,)
                              )

            tdef = wf.transitions[self.transition_id]
            tdef.setProperties(
                                title=self.transition_id,
                                new_state_id=self.state_id2,
                                actbox_name=self.transition_id,
                                actbox_url=self.actbox_url( tdef.getId() ),
                              )
        get_transaction().commit()

    def _create_registry(self):
        storage = self.naudoc.storage
        storage.manage_addProduct['CMFNauTools'].addRegistrationBook(
                                                         id=self.registry_id,
                                                         title=self.registry_id,
                                                         description=self.registry_id,
                                                         )

        registry = storage._getOb( self.registry_id )
        #registry.setTitle(self.registry_id)
        registry.setRegisteredCategory(self.category_id)

        #registry.reindexObject()
        get_transaction().commit()
        self.registry_uid = registry.getUid()


    def _assign_tasktemplate(self):
        portal_metadata=getToolByName( self.naudoc, 'portal_metadata' )
        template_id = "ztc_registry_version"

        portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
                    category_id=self.category_id,
                    action='add_root_task_definition',
                    request={ "task_definition_type" : "register_version",
                              "template_id" : template_id,
                              "name" : template_id,
                              "registry_uid" : self.registry_uid
                             }
                    )
        #get_transaction().commit()
        assignActionTemplateToTransition(
            portal_metadata=portal_metadata,
            category_id=self.category_id,
            action_template_id=template_id,
            transition=self.transition_id )

        template_id = "ztc_create_task"

        portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
                    category_id=self.category_id,
                    action='add_root_task_definition',
                    request={ "task_definition_type" : "followup_information",
                              "template_id" : template_id,
                              "name" : template_id,
                              "title" : template_id,
                              "interval": 86400 / 2, # half of day
                              "involved_users": ['_test_user1','_test_user2'],
                              "description": template_id,
                              "supervisor_user" : '',
                             }
                    )

        assignActionTemplateToTransition(
            portal_metadata=portal_metadata,
            category_id=self.category_id,
            action_template_id=template_id,
            transition=self.transition_id )

        get_transaction().commit()

    def _create_docs(self):
        storage = self.naudoc.storage

        for i in range(self.number_of_documents):
            title = "%s %d" % (self.document_base_title, i)
            doc_id=self.cookId(i)

            storage.invokeFactory( type_name='HTMLDocument',
                                       id=doc_id,
                                       title=title,
                                       description='test description',
                                       category=self.category_id )

            #test that it was created
            obj = storage._getOb( doc_id )

        get_transaction().commit()

    def actbox_url(self, transition_id ):
        return '%(content_url)s/change_state?transition=' + transition_id

    def beforeTearDown(self):
        #remove documents
        documents_ids = map(self.cookId, range(self.number_of_documents))
        self.naudoc.storage.deleteObjects( documents_ids )

        #remove registration book
        self.naudoc.storage.deleteObjects( [self.registry_id] )

        #remove category

        mdtool = getToolByName( self.naudoc, 'portal_metadata' )
        mdtool.deleteCategories( [self.category_id] )
        get_transaction().commit()

        NauDocTestCase.NauDocTestCase.beforeTearDown( self )



class WorkflowTests(NauDocTestCase.NauDocTestCase):
    _remove_naudoc = 0

    log_as_user = NauDocTestCase.admin_name

    def testGetCategoryDefinition(self):
        
        workflowtool = self.naudoc.portal_workflow
        for wf in workflowtool.objectValues(spec='Workflow'):
            cat = wf.getCategoryDefinition()
            self.assertEquals( aq_base(cat.getWorkflow()),aq_base(wf) )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(DocumentWorkflowTests) )
    suite.addTest( makeSuite(WorkflowTests) )
    return suite

if __name__ == '__main__':
    framework()
