#
# Default test case & fixture for NauDoc testing
#
# The fixture consists of:
#
#   - a naudoc (self.naudoc)
#   - a default member inside the naudoc (manager)
#
# The default user is logged in and has the 'Manager' and 'Member' roles.
#

# $Id: NauDocTestCase.py,v 1.8 2006/02/09 07:05:57 ynovokreschenov Exp $

import Configurator
PreferredNauDocInstance = Configurator.PreferredNauDocInstance
del Configurator

import AccessControl
from AccessControl.SecurityManagement import newSecurityManager

from Testing.ZopeTestCase import ZopeTestCase, FunctionalTestCase

from Products.CMFNauTools import NauSite

#XXX this must be fixed somethere but not in here
#------------------------------------------------
print 'Patched Localizer'

from Products.Localizer.MessageCatalog import MessageCatalog

MC_gettext = lambda self, text, *a, **k: text
MessageCatalog.gettext = MC_gettext
MessageCatalog.__call__ = MC_gettext
MessageCatalog.get_selected_language = lambda *a, **k: 'ru'
MessageCatalog.get_default_language = lambda *a, **k: 'ru'
#------------------------------------------------

print 'Patched __builtin__'
import transaction
import __builtin__
__builtin__.get_transaction = transaction.get
del __builtin__
#------------------------------------------------

user_role = 'Manager'
admin_name = 'test_nd_user_1_'

from Testing import ZopeTestCase as ZTCPackage

# Open ZODB connection
app = ZTCPackage.app()

# Set up sessioning objects
ZTCPackage.utils.setupCoreSessions(app)

# Close ZODB connection
ZTCPackage.close(app)

class NauDocTestCase(ZopeTestCase):

    _remove_naudoc = 0

    naudoc_id = 'test_docs_1_'

    _setup_fixture = 1

    def _loginAsManager(self):
        manager = AccessControl.User.UnrestrictedUser('TestCase Manager','',('Manager',), [])
        newSecurityManager(None, manager)

    def _setup(self):
        '''Sets up the fixture. Framework authors may
           override.
        '''
        if self._setup_fixture:
            self._loginAsManager()

            if not PreferredNauDocInstance:
                try:
                    self.naudoc = self.app._getOb( self.naudoc_id )
                except AttributeError:
                    #does not exists yet so create one
                    self._setupNauDoc()
            else: 
                self.naudoc = self.app._getOb( PreferredNauDocInstance )

            self._setupAdmin() #create admin if he is not created yet
            self.login()

    def _setupNauDoc(self):
        '''Creates and configures the naudoc.'''
        NauSite.manage_addNauSite( \
            self.app,
            id=self.naudoc_id,
            title='NauDoc',
            description='',
            email_from_address=None,
            email_from_name=None,
            validate_email=0,
            language='ru',
            stemmer='russian')
        self.naudoc = self.app._getOb(self.naudoc_id)
        get_transaction().commit()

    def _setupAdmin(self):
        '''XXX - make this wrapper for _setupMember(**kw)
        '''
        props = { 'username' : admin_name,
                  'email'    : 'foo@bar.baz' }
        reg_tool = self.naudoc._getOb( 'portal_registration' )
        try:
            member = reg_tool.addMember( admin_name, 'secret',
                roles=[ 'Member', 'Manager' ],
                domains=[],
                properties=props )

            self.naudoc.portal_licensing.addActiveUsers( admin_name )
#            #create home folder
#            username = member.getUserName()
#            home     = member.getHomeFolder( create=1 )
        except ValueError:
            pass
        self.logout()

    def login(self, name=admin_name):
        '''Logs in.'''
        uf = self.naudoc.acl_users
        user = uf.getUserById(name)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

    def beforeTearDown(self):
        if not PreferredNauDocInstance and self._remove_naudoc:
            #try:
            self.app._delObject( self.naudoc_id )
            get_transaction().commit()
            #except:
            #    pass

    def _addUser( self, number ):
        username = self.cookUserId( number )
        email = 'foo%d@bar.baz' % number
        portal_membership = self.naudoc.portal_membership
        portal_registration = self.naudoc.portal_registration
        portal_licensing = self.naudoc.portal_licensing
        failMessage = portal_registration.testPropertiesValidity(
                                 {'username':username,
                                  'email':email
                                 } )
        roles = [ 'Member' ]
        REQUEST = self.app.REQUEST
        REQUEST['username'] = username
        password = REQUEST['password'] = REQUEST['confirm'] = 'secret'
        REQUEST['home']=''
        REQUEST['domains']=[]
        REQUEST['fname']='User'
        REQUEST['lname']='Userov%d' % number
        REQUEST['mname']='Testovich'
        REQUEST['groups']=['all_users']
        REQUEST['email']=email
        REQUEST['phone']=("%.3d" % number) * 3
        REQUEST['position']='tester %d' % number
        REQUEST['company']='Naumen'
        REQUEST['notes']='Notes goes here...'
        REQUEST['noHome']='on' #create home folder.
        member = portal_registration.addMember( username, password, roles, [], properties=REQUEST )
        portal_licensing.addActiveUsers( username )
        self.userids.append( username )
        portal_membership.setDefaultFilters( username )
        username = member.getUserName()
        home     = member.getHomeFolder( create=0 )
        return username
    
    def cookUserId( self, i ):
        return '%s%d'%('Test_User', i)

class NauFunctionalTestCase( NauDocTestCase, FunctionalTestCase):

    # We do not Use a new copy of ZODB in each test
    _app = NauDocTestCase._app
    _close = NauDocTestCase._close
    
    def assertResponse(self, response):
        # XXX move to NauFunctional
       
        #test if we got any error
        bobo_exception_headers = filter(lambda s: s.startswith('bobo-exception'), response.headers.keys())
        err_msg = []
        for k in bobo_exception_headers:
            err_msg.append( "%s: %s" % (k, response.headers[k]))
        if err_msg:
            err_msg.append( self.naudoc.portal_errorlog._getLog()[-1]['tb_text'] )
            self.fail( "Error while getting path %s with error:\n" % response.getPath() + '\n'.join(err_msg) )

        self.assert_(response.getStatus() in [200, 302, 303])

    def beforeTearDown(self):
        #clear SESSION
        self.app.temp_folder.session_data._reset()

        NauDocTestCase.beforeTearDown(self)
        get_transaction().commit()
