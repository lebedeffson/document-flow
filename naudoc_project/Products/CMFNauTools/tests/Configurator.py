import os

os.environ['SOFTWARE_HOME'] = os.path.abspath('')
os.environ['INSTANCE_HOME'] = os.path.abspath('')

#import sys
#sys.stderr = open('error.log', 'w')

#If ZOPE_CONFIG set, use it as Zope configuration file
#This works if we are in INSTANCE_HOME/lib/python/Products/CMFNauTools/tests_ztc
#os.environ['ZOPE_CONFIG'] = os.path.abspath('../../../../../etc/zope.conf')

#os.environ['PROFILE_TESTS'] = '1'
#os.environ['PROFILE_SETUP'] = '0'
#os.environ['PROFILE_TEARDOWN'] = '0'

PreferredNauDocInstance = None # or instance id

class Constants:
    SMALL = 1
    FEW = 2
    MEDIUM = 5
    LARGE = 20
    HUGE = 100

