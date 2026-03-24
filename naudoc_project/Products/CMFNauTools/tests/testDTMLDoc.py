#! /bin/env python2.3
"""

$Id: testDTMLDoc.py,v 1.2 2005/12/10 09:55:31 vsafronovich Exp $
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

class DummyWithContent:
    filename = None
    content = None

    def __init__(self, fn='just/test.txt', cnt=''):
        self.filename=fn
        self.content=cnt;

    def seek(t, a=None, b=None): pass
    def write(t): pass
    def close(): pass
    def fileno(): raise 'this sux'
    def flush(): pass
    def read(self, a=None, b=None): return self.content
    def readline(): return ''
    def readlines(): return []
    def tell(t=None): return 0
    def truncate(i): pass
    def writelines(i): pass


sample_dtml_content = """
<dtml-var key1>, <dtml-var key2>
<dtml-in key3>&dtml-sequence-item;</dtml-in>

"""

rendered_dtml_content = """
value1, 654321
abc
"""

class DTMLDocumentTests(NauDocTestCase.NauDocTestCase):

    _remove_naudoc = False
    log_as_user = NauDocTestCase.admin_name

    def afterSetUp(self):

        self.naudoc.storage.manage_addProduct['CMFNauTools']\
                   .addDTMLDocument('dtml_test'
                                   , category='SimplePublication')

        self.d = self.naudoc.storage.dtml_test
        get_transaction().commit()

    def testEdit(self):
        d = self.d
        d.edit('new title', 'new data')
        self.assertEqual( d.Title(), 'new title', 'Error editing title')
        self.assertEqual( str(d), 'new data', 'Error editing contents')

    def testView(self):
        d = self.d
        d.edit('sample content', sample_dtml_content)
        result = apply(d, (self, self.app.REQUEST), { 'key1': 'value1'
                                                     , 'key2': 654321
                                                     , 'key3': ['a', 'b', 'c']
                                                     })
        self.assertEqual( result, rendered_dtml_content, 'Can not render DTML Method')

    def testUpload(self):
        d = self.d
        f = DummyWithContent("dummy.dtml", "sample\n content")
        d.upload(f)
        self.assertEqual( str(d), "sample\n content", 'Error uploading file')

    def testWorkflow(self):
        from Products.CMFCore.utils import getToolByName

        dtml_doc = self.d
        workflow = getToolByName( dtml_doc, 'portal_workflow')
        workflow.doActionFor( dtml_doc, 'publish')
        state = workflow.getInfoFor(dtml_doc, 'state')
        self.assertEqual( state, "published", 'Error adding DTML method to the site')

    def beforeTearDown(self):
        self.naudoc.storage._delObject('dtml_test')
        get_transaction().commit()
        del self.d

        NauDocTestCase.NauDocTestCase.beforeTearDown(self)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest( makeSuite(DTMLDocumentTests) )
    return suite

if __name__ == '__main__':
    framework()

