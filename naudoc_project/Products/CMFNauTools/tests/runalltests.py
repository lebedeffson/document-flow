#
# Runs all tests in the current directory [and below]
#
# Execute like:
#   python runalltests.py [-R]
#
# Alternatively use the testrunner:
#   python /path/to/Zope/bin/testrunner.py -qa
#

import os, sys

import Configurator
PreferredNauDocInstance = Configurator.PreferredNauDocInstance

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest, imp
TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

def visitor(recursive, dir, names):
    tests = [n[:-3] for n in names if n.startswith('test') and n.endswith('.py')]

    for test in tests:
        saved_syspath = sys.path[:]
        sys.path.insert(0, dir)
        try:
            file, path, desc = imp.find_module(test, [dir])
            m = imp.load_module(test, file, path, desc)
            if hasattr(m, 'test_suite'):
                suite.addTest(m.test_suite())
        finally:
            file.close()
            sys.path[:] = saved_syspath

    if not recursive:
        names[:] = []

Products2Test = ['CMFNauTools', 'NauScheduler']

if __name__ == '__main__':
    #os.path.walk(os.curdir, visitor, '-R' in sys.argv)

    #Load Product tests
    for product_name in Products2Test:
        os.path.walk(os.path.join(os.pardir, os.pardir, product_name, 'tests'), visitor, '-R' in sys.argv)

    #Load Addons tests
    addons_dir = os.path.join(os.pardir, 'Addons')
    for addon in os.listdir(addons_dir):
        addon = os.path.join(addons_dir, addon )
        if addon in ['CVS']:
            continue

        tests_dir = os.path.join(addon, 'tests')
        if os.path.isdir(tests_dir):
            os.path.walk(tests_dir, visitor, '-R' in sys.argv)

    sys.exit( not TestRunner().run(suite).wasSuccessful() )
