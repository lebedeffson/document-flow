"""
NauDoc/NauSite portal class.

$Editor: vpastukhov $
$Id: NauSite.py,v 1.244 2009/02/18 14:31:21 oevsegneev Exp $
"""
__version__ = '$Revision: 1.244 $'[11:-2]

import os, sys
from copy import deepcopy
from locale import setlocale, getlocale, LC_ALL
from urllib import splittype, splitport
from urlparse import urlparse
from types import StringType, UnicodeType

from Globals import HTMLFile, DTMLFile, package_home, get_request
from AccessControl import ClassSecurityInfo
from Acquisition import aq_get, aq_base
from ZPublisher.HTTPRequest import default_port
from ZPublisher.BeforeTraverse import NameCaller, \
        registerBeforeTraverse, queryBeforeTraverse

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.FSDTMLMethod import FSDTMLMethod
from Products.CMFCore.FSImage import FSImage
from Products.CMFCore.PortalObject import PortalObjectBase
from Products.CMFCore.utils import getToolByName, _checkPermission

from Products.CMFDefault import SkinnedFolder
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

import Config, Converter, Features, Exceptions
from MigrationTool import MigrationTool
from SimpleObjects import ContainerBase
from Utils import InitializeClass, getLanguageInfo, joinpath, pathdelim, cookId, \
                  uniqueOptions, getObjectImplements, ClassTypes

# used by initstate
import MailSMTP, MailPOP, UserFolder

if Config.UseTextIndexNG2:
    from Products.TextIndexNG2 import allStemmers

class NauSite( ContainerBase, PortalObjectBase, DefaultDublinCoreImpl ):
    """
        The *only* function this class should have is to help in the setup
        of a new NauSite.  It should not assist in the functionality at all.
    """
    _class_version = 1.98

    meta_type = 'NauSite'
    isPrincipiaFolderish = 1

    __resource_type__ = 'portal'

    __implements__ = Features.isPortalRoot, \
                     Features.isStatic, \
                     Features.isPrincipiaFolderish, \
                     Features.hasTabs, \
                     PortalObjectBase.__implements__, \
                     DefaultDublinCoreImpl.__implements__

    security = ClassSecurityInfo()

    manage_converters = DTMLFile('dtml/manageConverters', globals())

    manage_options = uniqueOptions( PortalObjectBase.manage_options + \
                                    ContainerBase.manage_options + \
                                    ( {'label':'Converters', 'action':'manage_converters'}, )
                                  )


    _properties = (
            {'id':'product_version',    'type':'string',  'mode':'w'},
            {'id':'title',              'type':'string',  'mode':'w', 'title':'Portal title'},
            {'id':'description',        'type':'text',    'mode':'w', 'title':'Portal description'},
            {'id':'server_url',         'type':'string',  'mode':'w', 'title':'Server address'},
            {'id':'email_from_address', 'type':'string',  'mode':'w'},
            {'id':'email_from_name',    'type':'string',  'mode':'w'},
            {'id':'validate_email',     'type':'boolean', 'mode':'w'},
            {'id':'stemmer',            'type':'string',  'mode':'w'},
            {'id':'fs_storage',         'type':'boolean', 'mode':'w'},
            {'id':'members_folder',     'type':'link',    'mode':'w', 'title':'Personal folders container'},
            {'id':'defaults_folder',    'type':'link',    'mode':'w', 'title':'Default content folder'},
            {'id':'templates_folder',   'type':'link',    'mode':'w', 'title':'Document templates folder'},
            {'id':'messages_folder',    'type':'link',    'mode':'w', 'title':'Message templates folder'},
            {'id':'scripts_folder',     'type':'link',    'mode':'w', 'title':'Scripts folder'},
            {'id':'directories_folder', 'type':'link',    'mode':'w', 'title':'Directory objects folder'},
            #{'id':'archive_folder',     'type':'link',    'mode':'w', 'title':'Archive folder'},
        )

    # overriden by Implicit in ItemBase
    __of__ = PortalObjectBase.__of__

    # overriden by ObjectManager in ContainerBase
    _super_checkId = PortalObjectBase._checkId
    _verifyObjectPaste = PortalObjectBase._verifyObjectPaste

    # default attribute values
    title = ''
    description = ''
    server_url = None
    product_version = None
    fs_storage = False

    service_unavailable = DTMLFile( 'dtml/service_unavailable', globals() )

    def __init__( self, id, title=None ):
        """
            Initializes class instance.
        """
        ContainerBase.__init__( self )
        PortalObjectBase.__init__( self, id, title )
        DefaultDublinCoreImpl.__init__( self )

    def _initstate( self, mode ):
        """
            Initializes instance attributes.
        """
        if not ContainerBase._initstate( self, mode ):
            return 0

        # install our before_traverse hook
        if not queryBeforeTraverse( self, __name__ ):
            registerBeforeTraverse( self, NameCaller('_beforeTraverseHook'), __name__ )

        if not mode:
            return 1

        migration = self._getOb( 'portal_migration', None )
        if migration is None:
            obj = MigrationTool()
            self._setObject( obj.getId(), obj )

        if getattr( self, 'server_url', None ) is None:
            REQUEST = get_request()
            self._setPropValue( 'server_url', REQUEST and REQUEST.physicalPathToURL('') or '' )

        # upgrade to the new user folder
        oldusers = getattr( self, 'acl_users', None )
        if oldusers and not isinstance( oldusers, UserFolder.UserFolder ):
            self._delObject( oldusers.getId() )
            oldusers.id = 'nux'

            newusers = UserFolder.UserFolder()
            newusers._setObject( oldusers.getId(), oldusers )

            self._setObject( newusers.getId(), newusers )
            newusers.setSourceFolder( id=oldusers.getId() )

        for view in self.portal_skins.objectValues():
            if getattr( view, '_isDirectoryView', None ):
                view._dirpath = view._dirpath.replace( '\\', pathdelim )

        if hasattr( self, 'MailServer' ): # < 1.94
            self._upgrade( 'MailHost',   MailSMTP.MailSMTP )
            self._upgrade( 'MailServer', MailPOP.MailPOP )

            mail_pop = self._getOb( 'MailServer' )
            self._delObject( 'MailServer' )

            mail_pop._setId( 'MailPOP' )
            self._setObject( 'MailPOP', mail_pop, set_owner=0 )

        return 1

    def _beforeTraverseHook( self, container, REQUEST, *args ):
        """
            Prepares global environment before any object inside is accessed.
        """
        stack = REQUEST['TraversalRequestNameStack']
        try:
            self.fixProxiedRequest( REQUEST )
            self.setPortalLocale()
            self.setContentCharset( REQUEST )
        except:
            pass

        licensing = getToolByName( self, 'portal_licensing', None )
        if licensing is None or \
           (not Config.DisableMigration and
            (self.product_version != Config.ProductVersion or
             self.fs_storage != Config.EnableFSStorage)):
            getToolByName( self, 'portal_migration' ).enterMigrationMode()

        mpath = list( Config.MaintainanceMode.get( self._p_oid ) or [] )
        if not mpath:
            return

        mpath.reverse()

        if stack and ( stack[-1] in ['portal_errorlog', 'scripts.js', 'styles.css'] or \
                       stack[0] == 'manage' or stack[0].startswith('manage_') ):
            return

        if stack[ -len(mpath): ] != mpath:
            REQUEST['TraversalRequestNameStack'] = ['maintainance']

    security.declareProtected( CMFCorePermissions.View, 'maintainance' )

    def maintainance( self, REQUEST=None ):
        """
            Maintainance mode.
        """
        if _checkPermission( CMFCorePermissions.ManagePortal, self ):
            mpath = Config.MaintainanceMode.get( self._p_oid )
            return self.redirect( action=joinpath(mpath), status=307, relative=False, REQUEST=REQUEST )

        return self.service_unavailable( self, REQUEST )

    def _afterValidateHook( self, user, published=None, REQUEST=None ):
        """
            Prepares global enviroment after the user is authenticated.
        """
        self.setContentCharset( REQUEST )
        self.fixFormLanguage( REQUEST )

        stack = REQUEST['TraversalRequestNameStack']
        if not ( stack and ( stack[-1] in ['portal_errorlog', 'scripts.js', 'styles.css'] or \
                       stack[0] == 'manage' or stack[0].startswith('manage_') ) ):
            licensing = getToolByName( self, 'portal_licensing', None )
            if licensing is None and not Config.MaintainanceMode.get( self._p_oid ):
                getToolByName( self, 'portal_migration' ).enterMigrationMode()
            elif licensing:
                licensing.validateUser()

        if isinstance( published, FSImage ):
            REQUEST.RESPONSE.setHeader('Cache-Control', 'public, max-age=7200, must-revalidate')
        elif isinstance( published, FSDTMLMethod ):
            REQUEST.RESPONSE.setHeader('Expires', 'Tue, 22 Jan 1980 01:01:01 GMT')

    security.declarePublic( 'productVersion' )
    def productVersion( self ):
        """
            Returns version string of the product.
        """
        return Config.ProductEdition

    security.declarePublic( 'getPortalObject' )
    def getPortalObject( self ):
        """
            Returns the portal object itself.
        """
        return self

    def view( self, REQUEST=None ):
        """
            Invokes the default view of the content storage.
        """
        REQUEST = REQUEST or self.REQUEST
        return self.storage(REQUEST)


    security.declarePrivate( 'fixProxiedRequest' )
    def fixProxiedRequest( self, REQUEST ):
        """
            Fixes environment if request was processed by frontend server.
        """
        # mod_proxy: X-Forwarded-Server
        # mod_accel: X-Host, X-Real-IP, X-URI, X-Method
        server    = REQUEST.get('SERVER_URL')
        real_host = REQUEST.get('HTTP_X_FORWARDED_SERVER') or REQUEST.get('HTTP_X_HOST')
        real_addr = REQUEST.get('HTTP_X_REAL_IP')
        real_uri  = REQUEST.get('HTTP_X_URI')

        # change SERVER_URL to frontend server's address and protocol
        if server and real_host:
            proto = REQUEST.get('HTTP_X_METHOD') or splittype( server )[0]
            host, port = splitport( real_host )
            REQUEST.setServerURL( proto, host, port or default_port.get( proto ) )

        # set REMOTE_ADDR to the real client's address
        if real_addr:
            REQUEST.environ['REMOTE_ADDR'] = real_addr

        # modify SCRIPT_NAME for proxied requests like
        # http://frontend/prefix/portal -> http://backend/portal
        if real_uri:
            # TODO: handle different portal name on frontend
            pos = real_uri.find( REQUEST['PATH_INFO'] )
            if pos > 0:
                REQUEST._script = real_uri[ 1:pos ].split('/')

    security.declarePrivate( 'setPortalLocale' )
    def setPortalLocale( self ):
        """
            Changes system locale according to the portal language.
        """
        info = getLanguageInfo( self )

        # find default and effective locale settings
        def_locale = info.get( sys.platform + '_locale' ) or info.get( os.name + '_locale' )
        cur_locale = getlocale()
        cur_locale = (None not in cur_locale) and '.'.join( cur_locale ) or ''

        # check whether locale is already ok
        if def_locale is None or cur_locale.lower() == def_locale.lower():
            return

        # change effective locale
        try:
            setlocale( LC_ALL, def_locale )
        except Exceptions.LocaleError:
            pass

    security.declarePublic( 'setContentCharset' )
    def setContentCharset( self, REQUEST=None ):
        """
            Sets response charset according to the user's selected language.
        """
        REQUEST = REQUEST or aq_get( self, 'REQUEST', None )
        if REQUEST is None:
            return

        lang = REQUEST.cookies.get( 'LOCALIZER_LANGUAGE' )
        info = getLanguageInfo( lang, None )

        if lang is None or info is None:
            mbstool = getToolByName( self, 'portal_membership' )
            lang    = mbstool.getLanguage( preferred=1, REQUEST=REQUEST )
            info    = getLanguageInfo( lang )

            REQUEST.set( 'LOCALIZER_LANGUAGE', lang )
            if not mbstool.isAnonymousUser():
                path = joinpath( '', REQUEST._script, self.absolute_url( relative=1 ) )
                REQUEST.RESPONSE.setCookie( 'LOCALIZER_LANGUAGE', lang, path=path )

        charset = info['http_charset']
        REQUEST.set( 'LOCALIZER_CHARSET', charset )
        REQUEST.set( 'management_page_charset', charset )
        REQUEST.RESPONSE.setHeader( 'content-type', 'text/html; charset=%s' % charset )

    security.declarePublic( 'fixFormLanguage' )
    def fixFormLanguage( self, REQUEST ):
        """
            Replaces HTML-encoded entities with their corresponding
            characters in the POST form data.
        """
        if REQUEST is None:
            return

        lang = REQUEST.get( 'LOCALIZER_LANGUAGE' )
        map  = Config.LanguageEntitiesMap.get( lang )
        if map is None:
            return

        for key, value in REQUEST.form.items():
            if type(value) in [ StringType, UnicodeType ]:
                for entity, char in map.items():
                    value = value.replace( entity, char )
                REQUEST.form[ key ] = value

        if REQUEST.REQUEST_METHOD == 'PUT':
            value = REQUEST.other.get('BODY')
            if value is not None:
                for entity, char in map.items():
                    value = value.replace( entity, char )
                REQUEST.other['BODY'] = value

    security.declareProtected( CMFCorePermissions.ManagePortal, 'addLocalizerMessages' )
    def addLocalizerMessages( self, namespace=None ):
        """
        """
        PortalGenerator().setupMessageCatalog( self, namespace=namespace )
        return 'OK'

    security.declareProtected( CMFCorePermissions.View, 'isEffective' )
    def isEffective( self, date ):
        """
            Override DefaultDublinCoreImpl's test, since we are always viewable.
        """
        return 1

    def reindexObject( self, idxs=[] ):
        """
            Overrides DefaultDublinCoreImpl's method.
        """
        pass

    def _instance_onCreate( self ):
        self.product_version = Config.ProductVersion

    def _containment_onAdd( self, item, container ):
        """
            Is called after our parent *item* is added to the *container*.
        """
        # Not calling base class's methods from here avoids reinitialization
        # of all the content objects after product version change.
        # Setup is carried by generator anyway.
        pass

    def _containment_onDelete( self, item, container ):
        """
            Is called before our parent *item* is deleted from its *container*.
        """
        PortalObjectBase.manage_beforeDelete( self, item, container )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'listAvailableConverters' )
    def listAvailableConverters( self ):
        """
        """
        return Converter.AvailableConverters
    #listAvailableConverters = staticmethod( listAvailableConverters ) ( and remove self above)

    def getStorage(self):
        return self._getOb('storage')

    def getArchive(self):
        return self._getOb('archive')

    security.declareProtected( CMFCorePermissions.View, 'getNavRoot' )
    def getNavRoot(self, arch ):
        """
        """
        if 1:#not arch:
             return self.getStorage()

        return self.getArchive()

    def listTabs(self):
        """
            See Feature.hasTabs interface
        """
        REQUEST = self.REQUEST
        msg = getToolByName( self, 'msg' )
 
        tabs = []
        append_tab = tabs.append

        #type = self.getTypeInfo()
        link = REQUEST.get('link', '')

        for action, title in [ ('member_tasks', 'My tasks')
                             , ('member_mail', 'My mail')
                             , ('member_documents', 'My documents')
                             , ('member_favorites', 'My favorites')
                             , ('accessible_documents', 'Accessible documents')
                             ]:
        
            append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                        , 'title' : msg(title)
                        } )

            if link.find(action) >=0:
                tabs[-1]['selected'] = True
                tabs[-1]['selected_color'] = '#ffffff'

        return tabs


InitializeClass( NauSite )


# This class is based on Products.CMFDefault.Portal.PortalGenerator class
class PortalGenerator:

    klass = NauSite

    _installers = []

    def setup( self, p ):
        installers = self._installers
        # One sort
        installers.sort(lambda x,y: cmp(x.priority, y.priority) )
 
        for installer in installers:
            installer.install(p)

    def create(self, parent, id, title, language, **kw):
        id = str(id)
        portal = self.klass(id=id, title=title)
        parent._setObject(id, portal)
        # Return the fully wrapped object.
        p = parent._getOb(id)

        # XXX
        p._v_init_language = language
        p._v_init_properties = kw

        self.setup(p)
        return p

languages = []
for lang, info in Config.Languages.items():
    languages.append( {
            'id'      : lang,
            'title'   : info.get( 'title', lang ),
            'default' : lang == Config.DefaultLanguage,
        } )

if Config.UseTextIndexNG2:
    stemmers = allStemmers( None )
else:
    stemmers = []


manage_addNauSiteForm = HTMLFile( 'dtml/addNauSite', globals(),
                                  all_languages = languages,
                                  all_stemmers  = stemmers )

del languages, stemmers, lang, info


def manage_addNauSite( self, id='docs', title='NauDoc', REQUEST=None,
                       description='',
                       email_from_address=None,
                       email_from_name=None,
                       validate_email=0,
                       language=None,
                       stemmer=None):
    """
        Adds NauDoc instance.
    """
    gen = PortalGenerator()
    p = gen.create( self, id.strip(), title, language
                  , description=description
                  , email_from_address=email_from_address
                  , email_from_name=email_from_name
                  , validate_email=email_from_name
                  , server_url=self.getPhysicalRoot().absolute_url()
                  , stemmer=stemmer
                  )

    if REQUEST is not None:
        p.redirect( relative=False, action='finish_nausite_construction' )


factory_type_information = [] # this is muttable list, that filled by registerContent

SkinnedFolder_fti = deepcopy( SkinnedFolder.factory_type_information )
SkinnedFolder_fti[0]['disallow_manual'] = 1
cmf_factory_type_information = SkinnedFolder_fti


def registerInstaller( installer ):
    assert isinstance( installer, ClassTypes ), repr(installer)
   
    priority = getattr( installer, 'priority', 50 )

    # make object
    installer = installer()

    if getattr( installer, 'after', False ):
        # increase priority by 100 on after installers
        priority += 100

    # return priority back to object
    installer.priority = priority

    # add installer to pool
    PortalGenerator._installers.append( installer )

    # add installer`s namespace to portalgenerator
    installer_name = getattr( installer, 'name', None )
    if installer_name is not None:
        assert callable( installer ), repr( installer )
        setattr( PortalGenerator, installer_name, installer )

class MessageCatalogInstaller:
    name ='setupMessageCatalog'
    priority = 5 # the first
    def install( self, portal, language=None, namespace=None ):
        # XXX need to find way to pass parameters to installers
        language = getattr(portal, '_v_init_language', language)

        language = language or Config.DefaultLanguage
        langs = Config.Languages

        msgcat = getToolByName( portal, 'msg', None )
        created = False

        if msgcat is None:
            portal.manage_addProduct['Localizer'].\
                   manage_addMessageCatalog( 'msg', 'Messages', [language] )

            msgcat = getToolByName( portal, 'msg' )
            created = True

        namespace = namespace or globals()
        path = joinpath( package_home(namespace), 'locale' )

        for lang, info in langs.items():
            # do not add language unless translations exist
            try:
                file = open( joinpath( path, '%s.po' % lang ), 'rt' )
            except IOError:
                continue

            try:
                if lang not in msgcat.get_languages():
                    msgcat.manage_addLanguage( lang )

                charset = info['python_charset'].upper()

                # import PO file into the Message Catalog
                msgcat.update_po_header( lang, '', '', '', charset )
                msgcat.manage_import( lang, file )
            finally:
                file.close()

            # import categories PO file into the Message Catalog
            try:
                file = open( joinpath( path, 'categories-%s.po' % lang ), 'rt' )
            except IOError:
                pass
            else:
                try:
                    msgcat.manage_import( lang, file )
                finally:
                    file.close()

            # fix empty string (just in case...)
            msgcat.manage_editLS( '', (lang, '') )

        if created:
            # select default language
            msgcat.manage_changeDefaultLang( language )

            # setup environment
            portal.setPortalLocale()

            #portal will be always sets content charset after validate hook
            #portal.setContentCharset()

    __call__ = install

class CookieAuthInstaller:
    def install(self, p):
        p.manage_addProduct['CMFCore'].manage_addCC(
            id='cookie_authentication')
        p.cookie_authentication.auto_login_page = ''

class RolesInstaller:
    def install(self, p):
        """ Set up the suggested roles. """
        p.__ac_roles__ = Config.PortalRoles

class PermissionsInstaller:
    name = 'setupPermissions'

    def install(self, p, check=False):
        count=0
        # Set up some suggested roles to permission mappings.
        mp = p.manage_permission
        for entry in Config.PortalPermissions:
            p_name = '_%s_Permission' % entry[0].replace( ' ', '_' )
            if not hasattr( p, p_name ):
                if check:
                    count += 1
                else:
                    # i.e. apply permission if there is no one yet,
                    # and not check mode
                    mp( *entry )
        return count
    __call__ = install

class PropertiesInstaller:
    def install(self, p):
        # XXX
        properties = p._v_init_properties

        email_from_address = properties['email_from_address']
        if email_from_address is None:
            email_from_address = 'postmaster@%s' % urlparse( properties['server_url'] )[1].split(':')[0]

        email_from_name = properties['email_from_name']
        if email_from_name is None:
            email_from_name = p.Title()

        p._setPropValue( 'email_from_address', email_from_address )
        p._setPropValue( 'email_from_name', email_from_name )
        p._setPropValue( 'validate_email', bool(properties['validate_email']) )
        p._setPropValue( 'server_url', properties['server_url'] )
        p._setPropValue( 'stemmer', properties['stemmer'] )

        p.setDescription( properties['description'] )

class MimetypesInstaller:
    def install(self, p):
        p.manage_addProduct[ 'CMFCore' ].manage_addRegistry()
        reg = p.content_type_registry

        reg.addPredicate( 'dtml', 'extension' )
        reg.getPredicate( 'dtml' ).edit( extensions="dtml" )
        reg.assignTypeName( 'dtml', 'DTMLDocument' )

        reg.addPredicate( 'link', 'extension' )
        reg.getPredicate( 'link' ).edit( extensions="url, link" )
        reg.assignTypeName( 'link', 'Link' )

        reg.addPredicate( 'news', 'extension' )
        reg.getPredicate( 'news' ).edit( extensions="news" )
        reg.assignTypeName( 'news', 'News Item' )

        reg.addPredicate( 'document', 'major_minor' )
        reg.getPredicate( 'document' ).edit( major="text", minor="" )
        reg.assignTypeName( 'document', 'HTMLDocument' )

        reg.addPredicate( 'image', 'major_minor' )
        reg.getPredicate( 'image' ).edit( major="image", minor="" )
        reg.assignTypeName( 'image', 'Site Image' )

        reg.addPredicate( 'file', 'major_minor' )
        reg.getPredicate( 'file' ).edit( major="application", minor="" )
        reg.assignTypeName( 'file', 'File' )

        reg.addPredicate( 'script', 'extension' )
        reg.getPredicate( 'script' ).edit( extensions="py" )
        reg.assignTypeName( 'script', 'Script' )

class PortalResource:

    def identify( portal, object ):
        if not getObjectImplements( object, 'isPortalRoot' ):
            raise TypeError, object
        assert aq_base(object) is aq_base(portal)
        return { 'uid' : None }

    def lookup( portal, **kwargs ):
        return portal

def initialize( context ):
    # module initialization callback
    context.register( registerInstaller )

    for installer in ( MessageCatalogInstaller, CookieAuthInstaller
                     , RolesInstaller, PermissionsInstaller
                     , PropertiesInstaller, MimetypesInstaller
                     ):
         context.registerInstaller( installer )

    context.registerFtis( factory_type_information )
    context.registerFtis( cmf_factory_type_information )

    context.registerResource( 'portal', PortalResource )

    context.registerClass(
            NauSite,
            constructors = (manage_addNauSiteForm, manage_addNauSite),
            icon = 'icons/nausite.gif'
        )
