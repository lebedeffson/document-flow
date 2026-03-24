"""
NauDoc (CMFNauTools) product initialization script.

$Editor: vpastukhov $
$Id: __init__.py,v 1.169 2008/12/24 13:11:02 oevsegneev Exp $
"""
__version__ = '$Revision: 1.169 $'[11:-2]
 
import os, os.path, sys

from types import StringType, TupleType

from email.Charset import BASE64, QP, ALIASES, CHARSETS, \
        add_charset, add_alias, add_codec

import Globals, ZODB
from zLOG import LOG, TRACE, DEBUG, INFO, ERROR

# apply patches before initialization of our classes

import Patches
#1del  Patches XXX errors, repaire this

from AccessControl.Permission import registerPermissions
from App.Common import package_home

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit as _ToolInit, \
                                   manage_addToolForm

import Config, Features

this_module = sys.modules[ __name__ ]

# add 'bin' subdirectory to the system search path
bin_dir   = os.path.join( package_home( globals() ), 'bin' )
path_list = os.environ.get( 'PATH', '' ).split( os.pathsep )

if os.access( bin_dir, os.X_OK ) and bin_dir not in path_list:
    path_list.insert( 0, bin_dir )
    os.environ['PATH'] = os.pathsep.join( path_list )

del bin_dir, path_list

skins_dir = os.path.join( package_home( globals() ), 'skins' )
for name in os.listdir( skins_dir ):
    if not os.path.isdir( os.path.join( skins_dir, name ) ) or \
       name in ['CVS']:
        continue
    
    if name.startswith('site_'):
        Config.SiteSkinViews.append( name )
    else:
        Config.SkinViews.append( name )

# check whether TextIndexNG2 is installed
if not hasattr( Config, 'UseTextIndexNG2' ):
    try:
        import Products.TextIndexNG2.TextIndexNG
        try:
            import Products.TextIndexNG2.Stemmer
        except ImportError:
            import Stemmer
            del Stemmer
    except ImportError:
        Config.UseTextIndexNG2 = False
    else:
        Config.UseTextIndexNG2 = True

# check whether the Python Imaging Library is installed
if not hasattr( Config, 'UsePILImage' ):
    try:
        import PIL.Image
        del PIL
    except ImportError:
        Config.UsePILImage = False
    else:
        Config.UsePILImage = True

# check whether LDAPUserFolder product is installed
if not hasattr( Config, 'UseLDAPUserFolder' ):
    try:
        import ldap, Products.LDAPUserFolder
        del ldap
    except ImportError:
        Config.UseLDAPUserFolder = False
    else:
        Config.UseLDAPUserFolder = True

# check whether ExternalEditor product is installed
if not hasattr( Config, 'UseExternalEditor' ):
    try:
        import Products.ExternalEditor
    except ImportError:
        Config.UseExternalEditor = False
    else:
        Config.UseExternalEditor = True

# check whether ExtFile product is installed
if not hasattr( Config, 'UseExtFile' ):
    try:
        import Products.ExtFile
    except ImportError:
        Config.UseExtFile = False
        # implicitly set EnableFSStorage to false
        Config.EnableFSStorage = False
    else:
        Config.UseExtFile = True

# load main NauDoc modules
import NauSite

# import helper modules
from SimpleObjects import ContainerBase
from Utils import loadModules, getLanguageInfo, getObjectImplements

# build transliteration maps
for lang, tables in Config.TransliterationMap.items():
    charmap = {}
    tables  = [ tables ]

    while tables:
        table = tables.pop(0)

        if type(table) is TupleType:
            tables[ 0:0 ] = list( table )
            continue

        elif type(table) is StringType:
            tables.insert( 0, Config.TransliterationMap[ table ] )
            continue

        table.setdefault( ' ', '_' )

        for i in range(256):
            c = chr(i)
            if table.has_key(c):
                charmap[c] = table[c]
            elif not charmap.has_key(c):
                charmap[c] = c

    Config.TransliterationMap[ (lang,) ] = charmap

del lang, tables, i, c, table, charmap

# fix Russian charsets in email package
_charset_map = {
        'cp1251' : (QP, None, None),
        'koi8-r' : (QP, None, None),
    }

_charset_aliases = {
        'windows-1251' : 'cp1251',
        '1251'         : 'cp1251',
        'koi8r'        : 'koi8-r',
    }

for name, item in _charset_map.items():
    add_charset( name, *item )
    add_codec( name, name )

for alias, name in _charset_aliases.items():
    add_alias( alias, name )

del alias, name, item

# try to auto-determine the system character set
import locale
current = locale.getlocale()
cur_name = (None not in current) and '.'.join( current ) or ''
cur_set = current[1]
def_set = locale.getdefaultlocale()[1]

for lang, info in Config.Languages.items():
    if not info.has_key( 'system_charset' ):
        name = info.get( sys.platform+'_locale' ) or info.get( os.name+'_locale' ) or ''
        charset_candidate = (name.lower() == cur_name.lower()) and cur_set or def_set
        info['system_charset'] = ALIASES.get( charset_candidate, charset_candidate )

del locale

class ToolInit( _ToolInit ):

    def initialize(self, context):
        # Add only one meta type to the folder add list.
        context.registerClass(
            meta_type = self.meta_type,
            constructors = (manage_addToolForm,
                            manage_addTool,
                            self,),
            icon = self.icon
            )

        for tool in self.tools:
            tool.__factory_meta_type__ = self.meta_type
            tool.icon = 'misc_/%s/%s' % (self.product_name, self.icon.split('/')[-1])

Globals.InitializeClass( ToolInit )

def manage_addTool(self, type, REQUEST=None):
    """ Add the tool specified by name.
    """
    # self is a FactoryDispatcher.
    toolinit = self.toolinit
    for tool in toolinit.tools:
        if tool.meta_type == type:
            obj = tool()
            if isinstance( self.this() , ContainerBase):
                self.this().addObject( obj )
            else:
                self._setObject( obj.getId(), obj, set_owner=0 )
            break
    else:
        raise 'NotFound', type

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

class DeferredQueue:

    def __init__(self):
        self.queue = []

    def push(self, *args, **kwargs):
        self.queue.append( (args, kwargs) )

    def pop( self, functor):
        for args, kwargs in self.queue:
            functor( *args, **kwargs )

class SystemRegistrator:

    def __init__( self, pc ):
        self.queues = {}

        # keep all stuff of ProductContext class
        self.__dict__.update( pc.__dict__ )
        for k,v in pc.__class__.__dict__.items():
            if k.startswith('_'):
                continue
            self.__class__.__dict__[k] = v

    def __getattr__(self, name):

        if not name.startswith( 'register' ):
            raise RuntimeError, 'name "%s" must starts with "register" prefix' %s

        return self.queues.setdefault( name, DeferredQueue() ).push

    def register( self, functor ):
        name = functor.__name__
        if self.queues.has_key(name):
            self.queues[name].pop( functor )

            # remove reference to DeferredQueue
            del self.queues[name]
            LOG( 'SystemRegistrator', DEBUG, 'empties DeferredQueue for --> %s' % name )

        if self.__dict__.has_key(name):
            raise RuntimeError, 'Dublicate registration of name "%s"' % name
        LOG( 'SystemRegistrator', DEBUG, 'register --> %s' % name )
        self.__dict__[name] = functor

    def check( self):
        l = len( self.queues )
        if l:
            LOG( 'SystemRegistrator', ERROR, 'not all DeferredQueues are empty. len=%d' % l )

def initialize( context ):

    product = context._ProductContext__prod

    # collect information about product
    Config.ProductName    = product.id
    Config.ProductEdition = product.version.split(None,1)[1]
    Config.ProductVersion = Config.ProductEdition.split(None,1)[0]
    Config.PackagePrefix  = __name__

    Config.ZopeInfo   = context._ProductContext__app.Control_Panel.version_txt()
    Config.PythonInfo = sys.version.replace('\r','').replace('\n',' ')
    Config.ZODBInfo   = ZODB.__version__
    Config.SystemInfo = '%s (%s)' % (sys.platform, os.name)

    lang = getLanguageInfo()
    Config.DefaultCharset = lang['python_charset']
    Config.MailCharset = lang['mail_charset']

    Config.AttachmentSearchable = Converter.AvailableConverters

    Config.MaintainanceMode = {}

    # begin registration
    context = SystemRegistrator( context )

    context.register( registerDirectory )
    context.register( registerPermissions )

    # make folders available as DirectoryViews
    for dir_name in 'skins', 'manual', 'fckeditor':
        context.registerDirectory(dir_name, globals())

    # register custom permissions
    perms = [ perm for perm in dir( Config.Permissions ) if not perm.startswith('_') ]
    perms = [ (getattr( Config.Permissions, perm ), ()) for perm in perms ]
    context.registerPermissions( perms )

    perms = [ perm for perm in dir( Config.Restrictions ) if not perm.startswith('_') ]
    perms = [ (getattr( Config.Restrictions, perm ), ()) for perm in perms ]
    context.registerPermissions( perms, () )

    context.register( registerContent )
    context.register( registerTool )

    # load all modules in the product directory
    for module in loadModules().values():
        init_func = getattr( module, 'initialize', None )
        if callable( init_func ):
            init_func( context )

    # load plugins in the Addons subdirectory
    AddonsTool.initializeAddons( context )

    ToolInit( 'CMF Nau Tools',
              product_name = Config.ProductName,
              tools = tuple( _registered_tools ),
              icon = 'icons/tool.gif',
            ).initialize( context )

    ContentInit( 'CMF Nau Content',
                 content_types = tuple( _registered_content ),
                 extra_constructors = tuple( _registered_factories ),
                 fti = tuple( _registered_ftis ),
                 permission = Config.AddContentPermission,
               ).initialize( context )

    context.registerHelpTitle( 'NauDoc Help' )
    context.registerHelp( directory='help' )

    context.check()

_registered_content = []
_registered_ftis = NauSite.factory_type_information
_registered_factories = []
_registered_tools = []


def registerContent( klass, factory, fti, activate=True ):
    """
        Registers content class and its factory.
    """
    global _registered_content, _registered_ftis, _registered_factories

    if klass in _registered_content:
        raise ValueError, klass
    _registered_content.append( klass )

    if fti:
        type_id = fti['id']
        for item in _registered_ftis:
            if item['id'] == type_id:
                raise ValueError, type_id

        fti['activate'] = activate
        _registered_ftis.append( fti )

    if factory:
        if factory in _registered_factories:
            raise ValueError, factory
        _registered_factories.append( factory )

def registerTool( klass ):
    """
        Registers portal tool class.
    """
    global _registered_tools

    id = klass.id
    meta_type = klass.meta_type
    if klass in _registered_tools or meta_type in Config.PortalTools:
        raise ValueError, klass

    _registered_tools.append( klass )
    Config.PortalTools.append( meta_type )

    # NOTE: workflow tool doesn`t have actions, but it overrides listActions
    if bool( klass._actions ) or klass.__dict__.has_key('listActions'):
        Config.ActionProviders.append( id )

    if klass.site_tool:
        Config.SiteTools.append( meta_type )

    if klass.site_action_provider:
        Config.SiteActionProviders.append( id )

    # TODO: investigate catalogs implements
    if getObjectImplements( klass, 'IZCatalog') or getObjectImplements( klass, Features.isCatalog):
        Config.CatalogTools.append( id )
