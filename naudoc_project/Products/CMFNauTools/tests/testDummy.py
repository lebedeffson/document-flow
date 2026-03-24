#! /bin/env python2.3

import os, sys
import Configurator
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


from Testing import ZopeTestCase

#install products we need
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')


class TestDummy(ZopeTestCase.ZopeTestCase):
    """

    """
    _setup_fixture = 0 # No default fixture

    def testDummy(self):
        self.assertEquals( 1+1, 2, "Your system is in trouble!")

if __name__ == '__main__':
    framework()
