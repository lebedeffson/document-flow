#! /bin/env python2.3
"""

$Id: testCategory.py,v 1.13 2006/02/10 12:24:37 ynovokreschenov Exp $
"""
__version__='$Revision: 1.13 $'[11:-2]

import os, sys
import Configurator
Constants = Configurator.Constants

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import NauDocTestCase

from Testing import ZopeTestCase
from DateTime import DateTime
from Products.CMFNauTools import NauSite
from Products.CMFNauTools.Utils import getToolByName

from Products.CMFNauTools.DefaultWorkflows import assignActionTemplateToTransition


import AccessControl.SecurityManagement, AccessControl.SpecialUsers

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('Localizer')

class CategoriesTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = 0
 
    def afterSetUp(self):
        self.cat_container = self.naudoc.portal_metadata

    def testexportToXML(self):
        REQUEST = self.app.REQUEST
        REQUEST['selected_categories'] = ['Document']

        res = self.cat_container.exportAsXML(REQUEST)

        self.assert_(res is not None)
        self.assert_(isinstance(res, str))

class CategoryFunctionalTests(NauDocTestCase.NauFunctionalTestCase):

    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def testCategoriesForm(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/manage_categories_form' % obj.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testMainCategoryForm(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        cat = obj.portal_metadata.getCategoryById('Document')
        path = '/%s/main_category_form' % cat.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

    def testCategoryMetadata(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        cat = obj.portal_metadata.getCategoryById('Document')
        path = '/%s/metadata_edit_form' % cat.absolute_url(1)
        response = self.publish(path, basic_auth)

        self.assertResponse( response )

class CategoryActionTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name

    def testCategoriesForm(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        obj  = self.naudoc
        path = '/%s/manage_categories' % obj.absolute_url(1)

        # adding new category
        extra_add = { 'category_id':'test_category', 'category_title':'test_title', 'addCategory':True }
        response = self.publish(path, basic_auth, extra=extra_add)
        category_id = self.naudoc.portal_metadata.getCategoryById( extra_add['category_id'] ).getId()
        category_title = self.naudoc.portal_metadata.getCategoryById( extra_add['category_id'] ).title
        
        # checking export to XML
        extra_xml = { 'selected_categories':['test_category'], 'exportAsXML':True }
        response = self.publish(path, basic_auth, extra=extra_xml)
        self.assert_( '<?xml' in str(response) )
        
        # checking: is the category added
        self.assertEquals( category_id, extra_add['category_id'] )
        self.assertEquals( category_title, extra_add['category_title'] )

        # deleting new category
        extra_del = { 'selected_categories':['test_category'], 'deleteCategories':True }
        response = self.publish(path, basic_auth, extra=extra_del)
        categories = self.naudoc.portal_metadata.listCategories()
        category_ids = [c.getId() for c in categories]
        self.assert_(extra_add['category_id'] not in category_ids)

class DocumentCategoryTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    _test_category = 'test_category'
    category = ''
    
    def afterSetUp(self):
        self.naudoc.portal_metadata.addCategory( self._test_category, title=self._test_category )
        self.category = self.naudoc.portal_metadata.getCategoryById( self._test_category )

    def testCategoryBase(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category

        # test category_bases_form
        path = '/%s/category_bases_form' % category.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )
        # checking cancel button
        extra = { 'cancel':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        # checking base category settings
        path = '/%s/category_bases' % category.absolute_url(1)
       
        bases_list_old = category.listBases()
        category_bases_old = [i.getId() for i in bases_list_old]
        
        bases_new = ['Folder']
        extra = { 'bases':bases_new, 'submit':True } 
        response = self.publish(path, basic_auth, extra=extra)
        
        bases_list_new = category.listBases()
        category_bases_new = [i.getId() for i in bases_list_new]
        
        self.assertEquals( bases_new, category_bases_new )

        category.setBases(category_bases_old)
        
    def testCategoryPrimary(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        
        # primary_category_select_form
        path = '/%s/primary_category_select_form' % category.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )
        # checking cancel button
        extra = { 'cancel':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        # set_primary_category
        path = '/%s/set_primary_category' % category.absolute_url(1)
       
        primary_old = category.getPrimaryCategory()
        
        extra = { 'primary':'Folder', 'submit':True }
        response = self.publish(path, basic_auth, extra=extra)
        primary_new = category.getPrimaryCategory()
        self.assertEquals( extra['primary'], primary_new )

        category.setPrimaryCategory(primary_old)
        
    def testCategoryTypes(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        
        # category_types_form
        path = '/%s/category_types_form' % category.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )
        # checking cancel button
        extra = { 'cancel':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )  
        # category_types
        path = '/%s/category_types' % category.absolute_url(1)
       
        allowed_types_old = category.listAllowedTypes()
        
        types = ['Folder']
        extra = { 'type_names':types, 'submit':True }
        response = self.publish(path, basic_auth, extra=extra)
        allowed_types_new = category.listAllowedTypes()
        self.assertEquals( types, allowed_types_new )

        category.setAllowedTypes(allowed_types_old)

    def beforeTearDown(self):
        category_ids = []
        category_ids.append(self._test_category)
        self.naudoc.portal_metadata.deleteCategories( category_ids )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )   

class WorkflowTransitionsTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    _test_category = 'test_category'
    category = ''
    wf = ''

    def afterSetUp(self):
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata

        self.category = portal_metadata.addCategory( cat_id=self._test_category, title=self._test_category, default_workflow=0, allowed_types=['HTMLDocument'])
        self.category.setBases(['SimpleDocument'])
        self.wf = self.category.getWorkflow()
        self.wf.setProperties(title="%s workflow" % self._test_category)
        self.wf.transitions.addTransition(self._test_category)
        get_transaction().commit()

    def testAddDelTransitions(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category

        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata
        
        # test workflow_transitions form
        path = '/%s/workflow_transitions' % category.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        # checking adding and deleting trans_id
        path = '/%s/workflows' % category.absolute_url(1)
        wf = self.wf
        wf_id = wf.getId()

        trans_id = 'test_transition'
        extra = { 'trans_id':trans_id, 'addTransition':True }
        response = self.publish(path, basic_auth, extra=extra)
        
        trans_info = portal_workflow.getTransitionInfo(wf_id, trans_id)
        self.assert_(trans_info is not None)

        trans_ids = []
        trans_ids.append(trans_id)
        extra = { 'ids':trans_ids, 'deleteTransitions':True }
        response = self.publish(path, basic_auth, extra=extra)
        
        try:
            portal_workflow.getTransitionInfo(wf_id, trans_id)
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def testTransitionProperties(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        wf = self.wf
        wf_id = wf.getId()
        
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata
        
        trans_id = 'test_transition'
        
        # test transition_properties form
        path = '/%s/transition_properties' % self.category.absolute_url(1)
        
        portal_workflow.addTransition(wf_id, trans_id)

        extra = { 'transition':trans_id }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test transition_properties
        # TODO: all_actions
        path = '/%s/workflows' % self.category.absolute_url(1)
        test_title = 'test_title'
        guard_permissions = ['Make version principal']
        guard_roles = ['writer']

        extra = { 'transition':trans_id, 'new_state_id':'archive', 'actbox_name':'test_trans_name',\
                  'title':test_title, 'guard_permissions':guard_permissions, 'guard_roles':guard_roles,\
                  'trigger_workflow_method':True, 'save_transition':True }
        response = self.publish(path, basic_auth, extra=extra)

        tr_info = portal_workflow.getTransitionInfo(wf_id, trans_id)
        roles = portal_workflow.getTransitionGuardRoles(wf_id, trans_id)
        guard = portal_workflow.getTransitionGuard(wf_id, trans_id)
        permissions = guard.permissions
        transitions = wf.transitions
        for transition in transitions.values():
            self.assertEquals( transition.trigger_type, extra['trigger_workflow_method'] )
        
        self.assertEquals(tr_info['title'], extra['title'])
        self.assertEquals(tr_info['new_state_id'], extra['new_state_id'])
        self.assertEquals(tr_info['actbox_name'], extra['actbox_name'])
        self.assertEquals(roles, guard_roles)
        self.assertEquals(permissions, guard_permissions)
    
    def beforeTearDown(self):
        category_ids = []
        category_ids.append(self._test_category)
        self.naudoc.portal_metadata.deleteCategories( category_ids )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )

class CategoryMetadataTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    _test_category = 'test_category'
    category = ''
    wf = ''

    def afterSetUp(self):
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata

        self.category = portal_metadata.addCategory( cat_id=self._test_category, title=self._test_category, default_workflow=0, allowed_types=['HTMLDocument'])
        self.category.setBases(['SimpleDocument'])
        self.wf = self.category.getWorkflow()
        self.wf.setProperties(title="%s workflow" % self._test_category)
        self.wf.transitions.addTransition(self._test_category)
        
        self._create_script()

        get_transaction().commit()

    def _create_script(self):
        storage = self.naudoc.storage

        storage.invokeFactory( type_name='Script'
                             , id='test_script'
                             , title='test_script'
                             , description='test description'
                             )

        script = self.naudoc._getOb('storage')._getOb('test_script')
        script.setBody('# test script\np = 1 + 1\nreturn p')

        get_transaction().commit()

    def testCategoryAttributes(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        
        # test category_metadata_form form
        path = '/%s/category_metadata_form' % category.absolute_url(1)
        extra = { 'add_form':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test category_metadata functions
        self._test_category_attributes('test_id', 'boolean', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'currency', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'date', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'float', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'int', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'lines', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'link', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'splitter', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'string', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'text', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'time_period', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'userlist', True, 'test_title', True, False)
        self._test_category_attributes('test_id', 'subordinate', True, 'test_title', True, False)

    def testComputedAttribute(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        
        # test category_metadata_form form
        path = '/%s/category_metadata_form' % category.absolute_url(1)
        extra = { 'add_form':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test category_metadata functions
        category = self.category
        path = '/%s/category_metadata' % category.absolute_url(1)
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        id = 'test_id'
        # creating attribute
        extra = { 'id':id,
                  'type':'computed',
                  'multiple':True,
                  'title':'test_title',
                  'mandatory':True,
                  'read_only':False,
                  'script_object':'test_script',
                  'add':True
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        attr_def = category.getAttributeDefinition(id)
        
        self.assertEquals( attr_def.getId(), extra['id'] )
        self.assertEquals( attr_def.multiple, False )
        self.assertEquals( attr_def.title, extra['title'] )
        self.assertEquals( attr_def.mandatory, extra['mandatory'] )
        self.assertEquals( attr_def.read_only, extra['read_only'] )
        
        # editing attribute
        path = '/%s/category_metadata' % category.absolute_url(1)
        extra = { 'id':id,
                  'type':type,
                  'multiple':False,
                  'title':'new_title',
                  'mandatory':False,
                  'read_only':True,
                  'script_object':'test_script',
                  'save':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        attr_def = category.getAttributeDefinition(id)
        
        self.assertEquals( attr_def.getId(), extra['id'] )
        self.assertEquals( attr_def.multiple, False )
        self.assertEquals( attr_def.title, extra['title'] )
        self.assertEquals( attr_def.mandatory, extra['mandatory'] )
        self.assertEquals( attr_def.read_only, extra['read_only'] )
        
        # deleting attribute
        extra = { 'ids':[id], 'delete':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        try:
            category.getAttributeDefinition(id)
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')
        
    def testDerivedAttribute(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        
        # test category_metadata_form form
        path = '/%s/category_metadata_form' % category.absolute_url(1)
        extra = { 'add_form':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test category_metadata functions
        category = self.category
        path = '/%s/category_metadata' % category.absolute_url(1)
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        id = 'test_id'
        # creating attribute
        extra = { 'id':id,
                  'type':'derived',
                  'multiple':True,
                  'title':'test_title',
                  'mandatory':True,
                  'read_only':False,
                  'derived_attr':'',
                  'primary_attr':'',
                  'add':True
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        attr_def = category.getAttributeDefinition(id)
        
        self.assertEquals( attr_def.getId(), extra['id'] )
        self.assertEquals( attr_def.multiple, False )
        self.assertEquals( attr_def.title, extra['title'] )
        self.assertEquals( attr_def.mandatory, extra['mandatory'] )
        self.assertEquals( attr_def.read_only, extra['read_only'] )
        self.assertEquals( attr_def.isDerived(), True )

        # editing attribute
        path = '/%s/category_metadata' % category.absolute_url(1)
        extra = { 'id':id,
                  'type':type,
                  'multiple':False,
                  'title':'new_title',
                  'mandatory':False,
                  'read_only':True,
                  'derived_attr':'',
                  'primary_attr':'',
                  'save':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        attr_def = category.getAttributeDefinition(id)
        
        self.assertEquals( attr_def.getId(), extra['id'] )
        self.assertEquals( attr_def.multiple, False )
        self.assertEquals( attr_def.title, extra['title'] )
        self.assertEquals( attr_def.mandatory, extra['mandatory'] )
        self.assertEquals( attr_def.read_only, extra['read_only'] )
        self.assertEquals( attr_def.isDerived(), True )
        
        # deleting attribute
        extra = { 'ids':[id], 'delete':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        try:
            category.getAttributeDefinition(id)
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

    def _test_category_attributes(self, id, type, multiple, title, mandatory, read_only):
        category = self.category
        path = '/%s/category_metadata' % category.absolute_url(1)
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        # creating attribute
        if type == 'computed':
            script_object  = self.naudoc.storage._getOb('test_script')
            script_object.setNamespaceFactory('category_attribute')
            properties = { 'script_object':script_object }
            extra = { 'id':id, 'type':type, 'multiple':multiple, 'title':title, 'mandatory':mandatory,\
                      'read_only':read_only, 'properties':properties, 'add':True }
            response = self.publish(path, basic_auth, extra=extra)
            self.assertResponse( response )
        else:
            extra = { 'id':id, 'type':type, 'multiple':multiple, 'title':title, 'mandatory':mandatory,\
                      'read_only':read_only, 'add':True }
            response = self.publish(path, basic_auth, extra=extra)
            self.assertResponse( response )

        attr_def = category.getAttributeDefinition(id)
        self.assertEquals( attr_def.getId(), extra['id'] )
        if extra['type'] is 'subordinate':
            self.assertEquals( attr_def.isSubordinate(), True )
        else:
            self.assertEquals( attr_def.type, extra['type'] )
                
        if extra['type'] in ['lines','userlist']:
            self.assertEquals( attr_def.multiple, extra['multiple'] )
        else:
            self.assertEquals( attr_def.multiple, False )
            
        self.assertEquals( attr_def.title, extra['title'] )
        self.assertEquals( attr_def.mandatory, extra['mandatory'] )
        self.assertEquals( attr_def.read_only, extra['read_only'] )


        # test category_attr_edit form
        path1 = '/%s/category_attr_edit' % category.absolute_url(1)
        extra = { 'id':id }
        response = self.publish(path1, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # editing attribute
        extra = { 'id':id, 'type':type, 'title':'new_title', \
                  'mandatory':(not mandatory), 'read_only':(not read_only), 'save':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        attr_def = category.getAttributeDefinition(id)
        
        self.assertEquals( attr_def.getId(), extra['id'] )
        if extra['type'] is 'subordinate':
            self.assertEquals( attr_def.isSubordinate(), True )
        else:
            self.assertEquals( attr_def.type, extra['type'] )
        self.assertEquals( attr_def.title, extra['title'] )
        self.assertEquals( attr_def.mandatory, extra['mandatory'] )
        self.assertEquals( attr_def.read_only, extra['read_only'] )

        # deleting attribute
        ids = [id]
        extra = { 'ids':ids, 'delete':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        try:
            category.getAttributeDefinition(id)
        except KeyError:
            pass
        else:
            self.fail('KeyError must be raisen')

        get_transaction().commit()
        
        
    def beforeTearDown(self):
        category_ids = []
        category_ids.append(self._test_category)
        self.naudoc.portal_metadata.deleteCategories( category_ids )
        self.naudoc.storage.deleteObjects( ['test_script'] )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )
    
class WorkflowStatesTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    _test_category = 'test_category'
    category = ''
    wf = ''

    def afterSetUp(self):
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata

        self.category = portal_metadata.addCategory( cat_id=self._test_category, \
                                                     title=self._test_category, \
                                                     default_workflow=0, allowed_types=['HTMLDocument'])
        self.category.setBases(['PrikazBasic'])
        self.wf = self.category.getWorkflow()
        self.wf.setProperties(title="%s workflow" % self._test_category)
        self.wf.transitions.addTransition(self._test_category)
        get_transaction().commit()

    def testWorkflowStates(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        wf_id = self.wf.getId()
        wf = self.wf
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        
        # test workflow_states form
        path = '/%s/workflow_states' % category.absolute_url(1)
        response = self.publish(path, basic_auth)
        self.assertResponse( response )

        # test addung wrorkflow state
        path = '/%s/workflows' % category.absolute_url(1)
        state_id = 'test_id'
        ids = [state_id]
        extra = { 'wf_id':wf_id, 'state_id':state_id, 'addState':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        self.assertEquals( portal_workflow.getStateTitle(wf_id, state_id), extra['state_id'] )

        # test setting setInitialState
        path = '/%s/workflows' % category.absolute_url(1)
        extra = { 'wf_id':wf_id, 'ids':[state_id], 'setInitialState':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        self.assertEquals( [wf.initial_state], extra['ids'] )
        
        # test state_properties form
        path = '/%s/state_properties' % category.absolute_url(1)
        extra = { 'wf_id':wf_id, 'state':state_id }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test state properties editing
        trans_ids = ['tr1', 'tr2']
        for id in trans_ids:
            wf.transitions.addTransition(id)
            trans_info = portal_workflow.getTransitionInfo(wf_id, id)

        state_title = 'test_title'
        path = '/%s/workflows' % category.absolute_url(1)
        extra = { 'wf_id':wf_id, 'state':state_id, 'title':state_title, 'transitions':trans_ids,\
                  'only_one_version_can_exists':True, 'transition_for_exclude':'fix', 'save_state':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        self.assertEquals( wf.states.get(state_id).title, extra['title'] )
        self.assertEquals( list(wf.states.get(state_id).transitions), extra['transitions'] )
        if extra['only_one_version_can_exists']==True:
            self.assertEquals( wf.states.allow_only_single_version[state_id], extra['transition_for_exclude'] )

        # test deliting wrorkflow state
        path = '/%s/workflows' % category.absolute_url(1)
        extra = { 'wf_id':wf_id, 'ids':ids, 'deleteStates':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        for id in ids:
            self.assert_( self.wf.states.get(id) is None )

    def testWorkflowStatePermissions(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        wf_id = self.wf.getId()
        wf = self.wf
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        
        # test state_properties form
        path = '/%s/state_properties' % category.absolute_url(1)
        extra = { 'state':'archive' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # testing state permissions
        path = '/%s/workflows' % category.absolute_url(1)
        
        extra = { 'wf_id':wf_id,
                  'state':'archive',
                  'force_update_roles':True,
                  'set_permissions':True,
                  'acquire_Access contents information':True,
                  'Access contents information|Author':True,
                  'Access contents information|Editor':True,
                  'Access contents information|Manager':True,
                  'Access contents information|Member':True,
                  'Access contents information|Owner':True,
                  'Access contents information|Reader':True,
                  'Access contents information|VersionOwner':True,
                  'Access contents information|Writer':True,

                  'acquire_Create object versions':True,
                  'Create object versions|Author':True,
                  'Create object versions|Editor':True,
                  'Create object versions|Manager':True,
                  'Create object versions|Member':True,
                  'Create object versions|Owner':True,
                  'Create object versions|Reader':True,
                  'Create object versions|VersionOwner':True,
                  'Create object versions|Writer':True,

                  'acquire_Delete objects':True,
                  'Delete objects|Author':True,
                  'Delete objects|Editor':True,
                  'Delete objects|Manager':True,
                  'Delete objects|Member':True,
                  'Delete objects|Owner':True,
                  'Delete objects|Reader':True,
                  'Delete objects|VersionOwner':True,
                  'Delete objects|Writer':True,

                  'acquire_List folder contents':True,
                  'List folder contents|Author':True,
                  'List folder contents|Editor':True,
                  'List folder contents|Manager':True,
                  'List folder contents|Member':True,
                  'List folder contents|Owner':True,
                  'List folder contents|Reader':True,
                  'List folder contents|VersionOwner':True,
                  'List folder contents|Writer':True,

                  'acquire_Make version principal':True,
                  'Make version principal|Author':True,
                  'Make version principal|Editor':True,
                  'Make version principal|Manager':True,
                  'Make version principal|Member':True,
                  'Make version principal|Owner':True,
                  'Make version principal|Reader':True,
                  'Make version principal|VersionOwner':True,
                  'Make version principal|Writer':True,

                  'acquire_Manage properties':True,
                  'Manage properties|Author':True,
                  'Manage properties|Editor':True,
                  'Manage properties|Manager':True,
                  'Manage properties|Member':True,
                  'Manage properties|Owner':True,
                  'Manage properties|Reader':True,
                  'Manage properties|VersionOwner':True,
                  'Manage properties|Writer':True,

                  'acquire_Modify attributes':True,
                  'Modify attributes|Author':True,
                  'Modify attributes|Editor':True,
                  'Modify attributes|Manager':True,
                  'Modify attributes|Member':True,
                  'Modify attributes|Owner':True,
                  'Modify attributes|Reader':True,
                  'Modify attributes|VersionOwner':True,
                  'Modify attributes|Writer':True,

                  'acquire_Modify portal content':True,
                  'Modify portal content|Author':True,
                  'Modify portal content|Editor':True,
                  'Modify portal content|Manager':True,
                  'Modify portal content|Member':True,
                  'Modify portal content|Owner':True,
                  'Modify portal content|Reader':True,
                  'Modify portal content|VersionOwner':True,
                  'Modify portal content|Writer':True,

                  'acquire_Reply to item':True,
                  'Reply to item|Author':True,
                  'Reply to item|Editor':True,
                  'Reply to item|Manager':True,
                  'Reply to item|Member':True,
                  'Reply to item|Owner':True,
                  'Reply to item|Reader':True,
                  'Reply to item|VersionOwner':True,
                  'Reply to item|Writer':True,

                  'acquire_Take ownership':True,
                  'Take ownership|Author':True,
                  'Take ownership|Editor':True,
                  'Take ownership|Manager':True,
                  'Take ownership|Member':True,
                  'Take ownership|Owner':True,
                  'Take ownership|Reader':True,
                  'Take ownership|VersionOwner':True,
                  'Take ownership|Writer':True,

                  'acquire_View':True,
                  'View|Author':True,
                  'View|Editor':True,
                  'View|Manager':True,
                  'View|Member':True,
                  'View|Owner':True,
                  'View|Reader':True,
                  'View|VersionOwner':True,
                  'View|Writer':True,

                  'acquire_View attributes':True,
                  'View attributes|Author':True,
                  'View attributes|Editor':True,
                  'View attributes|Manager':True,
                  'View attributes|Member':True,
                  'View attributes|Owner':True,
                  'View attributes|Reader':True,
                  'View attributes|VersionOwner':True,
                  'View attributes|Writer':True,

                  'acquire_WebDAV Lock items':True,
                  'WebDAV Lock items|Author':True,
                  'WebDAV Lock items|Editor':True,
                  'WebDAV Lock items|Manager':True,
                  'WebDAV Lock items|Member':True,
                  'WebDAV Lock items|Owner':True,
                  'WebDAV Lock items|Reader':True,
                  'WebDAV Lock items|VersionOwner':True,
                  'WebDAV Lock items|Writer':True,

                  'acquire_WebDAV Unlock items':True,
                  'WebDAV Unlock items|Author':True,
                  'WebDAV Unlock items|Editor':True,
                  'WebDAV Unlock items|Manager':True,
                  'WebDAV Unlock items|Member':True,
                  'WebDAV Unlock items|Owner':True,
                  'WebDAV Unlock items|Reader':True,
                  'WebDAV Unlock items|VersionOwner':True,
                  'WebDAV Unlock items|Writer':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        states = wf.states
        sdef = states['archive']
        roles = ['Author', 'Editor', 'Manager', 'Member', 'Owner', 'Reader', 'VersionOwner', 'Writer']
        roles.sort()
        for mp in sdef.getManagedPermissions():
            self.assertEquals( sdef.getPermissionInfo(mp)['acquired'], 1 )
            rez = sdef.getPermissionInfo(mp)['roles']
            rez.sort()
            self.assertEquals( rez, roles )

    def testWorkflowAttributesPermissions(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        wf_id = self.wf.getId()
        wf = self.wf
        portal_workflow = self.naudoc.portal_workflow
        portal_metadata = self.naudoc.portal_metadata
        
        # test workflow_attributes_permissions form
        path = '/%s/workflow_attributes_permissions' % category.absolute_url(1)
        extra = { 'state':'archive', 'attr':'DocDate' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
        # testing workflow_attributes_permissions
        path = '/%s/workflows' % category.absolute_url(1)
        extra = { 'wf_id':wf_id,
                  'state':'archive',
                  'set_attr_properties':True,
                  'attribute_id':'DocDate',

                  'mandatory':True,
                  
                  'acquire_Modify attributes':True,
                  'Modify attributes|Author':True,
                  'Modify attributes|Editor':True,
                  'Modify attributes|Manager':True,
                  'Modify attributes|Member':True,
                  'Modify attributes|Owner':True,
                  'Modify attributes|Reader':True,
                  'Modify attributes|VersionOwner':True,
                  'Modify attributes|Writer':True,
                  
                  'acquire_View attributes':False,
                  'View attributes|Author':True,
                  'View attributes|Editor':True,
                  'View attributes|Manager':True,
                  'View attributes|Member':True,
                  'View attributes|Owner':True,
                  'View attributes|Reader':True,
                  'View attributes|VersionOwner':True,
                  'View attributes|Writer':True,
                }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        available_roles = list(portal_metadata.getManagedRoles_())
        available_roles.sort()
        
        sapr = wf.state_attr_permission_roles
        # modify_attributes
        modify_attributes = sapr[('archive', 'DocDate')]['Modify attributes']
        self.assert_(isinstance(modify_attributes, list))

        modify_attributes = list(modify_attributes)
        modify_attributes.sort()
        self.assertEquals(available_roles, modify_attributes)
        
        # view_attributes
        view_attributes = sapr[('archive', 'DocDate')]['View attributes']
        self.assert_(isinstance(view_attributes, tuple))

        view_attributes = list(view_attributes)
        view_attributes.sort()
        self.assertEquals(available_roles, view_attributes)
        # is mandatory
        self.assert_(wf.states[extra['state']].isAttributeMandatory(extra['attribute_id']))
        
    def beforeTearDown(self):
        category_ids = []
        category_ids.append(self._test_category)
        self.naudoc.portal_metadata.deleteCategories( category_ids )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )

class WorkflowPermissionsTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    _test_category = 'test_category'
    category = ''

    def afterSetUp(self):
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata

        self.category = portal_metadata.addCategory( cat_id=self._test_category, \
                                                     title=self._test_category, \
                                                     default_workflow=0, allowed_types=['HTMLDocument'])
        self.category.setBases(['SimpleDocument'])
        self.wf = self.category.getWorkflow()
        self.wf.setProperties(title="%s workflow" % self._test_category)
        self.wf.transitions.addTransition(self._test_category)
        get_transaction().commit()

    def testWorkflowPermissions(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        wf = category.getWorkflow()
        wf_id = wf.getId()
       
        # test workflow_permissions form
        path = '/%s/workflow_permissions' % category.absolute_url(1)
        extra = { 'wf_id':wf_id }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test add/delete workflow permissions
        path = '/%s/workflows' % category.absolute_url(1)
        
        wf.delManagedPermissions(wf.permissions)
        permissions = wf.getPossiblePermissions()

        number_of_perms = Constants.FEW
        for i in range(number_of_perms):
            p = permissions[i]
            if p is None: break
            self._add_permission(str(p))
            self.assert_( p in list(wf.permissions) )

        self._del_permissions(list(wf.permissions))
        self.assertEquals( wf.permissions, () )

    def _add_permission(self, p):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        wf = category.getWorkflow()
        wf_id = wf.getId()
        path = '/%s/workflows' % category.absolute_url(1)
        
        extra = { 'wf_id':wf_id, 'p':p , 'addManagedPermission':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        
    def _del_permissions( self, ids, ):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        wf = category.getWorkflow()
        wf_id = wf.getId()
        path = '/%s/workflows' % category.absolute_url(1)
        
        extra = { 'wf_id':wf_id, 'ids':ids, 'delManagedPermissions':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

    def beforeTearDown(self):
        category_ids = []
        category_ids.append(self._test_category)
        self.naudoc.portal_metadata.deleteCategories( category_ids )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )

class TemplateSummaryTests( NauDocTestCase.NauFunctionalTestCase ):
    _remove_naudoc = 0
    log_as_user = NauDocTestCase.admin_name
    _test_category = 'test_category'
    category = ''
    template_id = "test_template"

    def afterSetUp(self):
        storage = self.naudoc
        portal_workflow = storage.portal_workflow
        portal_metadata = storage.portal_metadata
        self.userids = []

        self.category = portal_metadata.addCategory( cat_id=self._test_category, 
                                                     title=self._test_category, 
                                                     default_workflow=0,
                                                     allowed_types=['HTMLDocument']
                                                    )
        self.category.setBases(['SimpleDocument'])
        self.wf = self.category.getWorkflow()
        self.wf.setProperties(title="%s workflow" % self._test_category)
        self.wf.transitions.addTransition(self._test_category)
        self._addUser(1)
        self._assign_tasktemplate()
        get_transaction().commit()

    def testTemplateSummary(self):
        basic_auth = "%s:%s" % (self.log_as_user, 'secret')
        category = self.category
        wf = category.getWorkflow()
        wf_id = wf.getId()
        portal_metadata = self.naudoc.portal_metadata
        c_id = category.getId()
        
        # test template_summary form
        path = '/%s/task_template_summary' % category.absolute_url(1)
        extra = { 'wf_id':wf_id }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )

        # test action_task_template_summary
        path = '/%s/action_task_template_summary' % category.absolute_url(1)
        state_ids = wf.states.objectIds()
        trans_ids = wf.transitions.objectIds()
        
        for sid in state_ids:
            extra = { 'wf_id':wf_id, 'state':sid, sid+'_transitions':trans_ids, 'save_state2transition':True }
            response = self.publish(path, basic_auth, extra=extra)
            self.assertResponse( response )
            sdef = wf.states[sid]
            self.assertEquals(list(sdef.transitions), trans_ids)
        
        # test script2transition_add
        path = '/%s/actionOverTable' % category.absolute_url(1)
        python_script = "result_codes['test_template']=='success' and state=='fixed'"
        template_id = self.template_id
        
        # creating resultcodes2TransitionModel
        extra = { 'c_id':c_id, 'python_script':python_script, 'transition':trans_ids[0],\
                  'note':'notes', 'action':'add_script' }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        result = category.resultcodes2TransitionModel.variants
        self.assertEquals( result[1]['note'], extra['note'] )
        self.assertEquals( result[1]['transition'], extra['transition'] )
        self.assertEquals( result[1]['python_script'], extra['python_script'] )
        # changing resultcodes2TransitionModel
        new_python_script = "state=='fixed'"
        extra = { 'c_id':c_id, 'python_script':new_python_script, 'transition':trans_ids[0],\
                  'note':'new_notes', 'action':'change', 'id_variant':1 }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        result = category.resultcodes2TransitionModel.variants
        self.assertEquals( result[1]['note'], extra['note'] )
        self.assertEquals( result[1]['transition'], extra['transition'] )
        self.assertEquals( result[1]['python_script'], extra['python_script'] )
        # deleting resultcodes2TransitionModel
        extra = { 'c_id':c_id, 'python_script':python_script, 'transition':trans_ids[0],\
                  'note':'notes', 'action':'delete', 'id_variant':1 }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        result = category.resultcodes2TransitionModel.variants
        self.assertEquals( result, {} )

        # test save_state2tasktemplatedie
        path = '/%s/action_task_template_summary' % category.absolute_url(1)
        task_templates = ['_make_version_principal']
        select_name = '%s_result_code_%s' % ( state_ids[0], task_templates[0] )
        extra = { 'wf_id':wf_id, select_name:'success', state_ids[0]+'_task_templates':task_templates, 'save_state2tasktemplatedie':True }
        response = self.publish(path, basic_auth, extra=extra)
        self.assertResponse( response )
        self.assertEquals( portal_metadata.getCategory(c_id).state2TaskTemplateToDie[state_ids[0]][task_templates[0]], extra[select_name] )

    def _assign_tasktemplate(self):
        template_id = self.template_id
        users = self.naudoc.acl_users.getUsers()
        category = self.category
        c_id = category.getId()
        portal_metadata = self.naudoc.portal_metadata
        portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
                    category_id=c_id,
                    action="add_root_task_definition",
                    request={ "task_definition_type" : "followup_request",
                              "template_id" : template_id,
                              "name" : template_id,
                              "title" : template_id,
                              "involved_users" : users,
                              "description" : template_id
                             }
                    )
        get_transaction().commit()

    def beforeTearDown(self):
        self.naudoc.portal_metadata.deleteCategories( [self._test_category] )
        self.naudoc.portal_membership.deleteMembers( self.userids )
        get_transaction().commit()
        NauDocTestCase.NauFunctionalTestCase.beforeTearDown( self )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(CategoriesTests) )
    suite.addTest( makeSuite(CategoryFunctionalTests) )
    suite.addTest( makeSuite(CategoryActionTests) )
    suite.addTest( makeSuite(DocumentCategoryTests) )
    suite.addTest( makeSuite(WorkflowTransitionsTests) )
    suite.addTest( makeSuite(CategoryMetadataTests) )
    suite.addTest( makeSuite(WorkflowStatesTests) )
    suite.addTest( makeSuite(WorkflowPermissionsTests) )
    suite.addTest( makeSuite(TemplateSummaryTests) )

    return suite

if __name__ == '__main__':
    framework()

