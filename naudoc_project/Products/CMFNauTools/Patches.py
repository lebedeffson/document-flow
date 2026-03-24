"""
Monkey patches for Zope.

NEVER EVER IMPORT ANYTHING ELSE FROM CMFNAUTOOLS HERE !!!

$Editor: vpastukhov $
$Id: Patches.py,v 1.146 2006/10/18 13:50:06 ypetrov Exp $
"""
__version__ = '$Revision: 1.146 $'[11:-2]

import re, sys
from cgi import escape
from string import translate, strip
from sys import _getframe as getframe
import threading, time
from types import StringType, UnicodeType, MethodType, \
      ListType, TupleType, DictType, ClassType

from Zope2 import App
from Acquisition import aq_base, aq_parent, aq_inner, aq_get
from AccessControl.SecurityManagement import getSecurityManager, newSecurityManager
from ExtensionClass import ExtensionClass
from ThreadedAsync import register_loop_callback

# apply Nux patches before initialization of our classes
import Products.NuxUserGroups

# for Globals.get_request
import Products.Localizer

import Config

from logging import getLogger
LOG = getLogger(Config.ProductName)

def patch( name ):
    LOG.info( 'Patching %s' % name )

# experimental flag for Zope reloading mechanism
__reload_module__ = 0

#
# 1. Creates global variables - True, False, StopIteration, Missing, Trust.
#
# 2. Addes 'bool' function to builtins namespace to imitate python 2.2 'bool'.
#
# 3. Replaces 'isinstance' function with a variant that supports
#    extension classes under Python 2.1.
#
# 4. Adds 'dict' type factory under Python < 2.2
#

patch('__builtins__')

try:
    True, False
except NameError:
    __builtins__['True']  = 1==1
    __builtins__['False'] = 1==0

try:
    bool(True)
except NameError:
    import operator
    __builtins__['bool'] = operator.truth
    del operator

try:
    StopIteration
except NameError:
    __builtins__['StopIteration'] = IndexError
except:
    pass

def safeIsInstance( object, klass ):
    try:
        if _nau_isinstance( object, klass ):
            return True
    except TypeError:
        if type(klass) is TupleType:
            for item in klass:
                if safeIsInstance( object, item ):
                    return True
        return False
    try:
        return issubclass( object.__class__, klass )
    except (AttributeError, TypeError):
        return False

try:
    isinstance( None, ExtensionClass )
    isinstance( None, (ExtensionClass,) )

except TypeError: # python < 2.2
    __builtins__['_nau_isinstance'] = isinstance
    __builtins__['isinstance'] = safeIsInstance

class MarkerValue:
    """
        Special 'marker' values class.
    """

    def __init__( self, name, value=False, builtin=True ):
        self.__name__  = name
        self.__value__ = value
        if builtin:
            __builtins__.setdefault( name, self )

    def __nonzero__( self ):
        return self.__value__

    def __repr__( self ):
        return self.__name__

    def __getstate__( self ):
        raise TypeError, "%s cannot be pickled" % repr(self)

# magical value to indicate omitted keyword arguments
MarkerValue( 'Missing' )

# magical argument value to bypass security checks
MarkerValue( 'Trust' )

def dictFactory( source=Missing ):
    if source is Missing:
        return {}
    elif isinstance( source, DictType ):
        return source.copy()
    elif isinstance( source, (ListType,TupleType) ):
        d = {}
        for k, v in source:
            d[k] = v
        return d
    raise TypeError

try:
    dict
except NameError: # python < 2.2
    __builtins__['dict'] = dictFactory


#
# 1. Adds BooleanType as an alias to IntType under Python < 2.3
#
# 2. Adds StringTypes into types module under Python < 2.2
#

import types

try:
    types.BooleanType
except AttributeError: # python < 2.3
    LOG( Config.ProductName, INFO, 'Patching types' )
    types.BooleanType = types.IntType

try:
    types.StringTypes
except AttributeError: # python < 2.2
    types.StringTypes = (types.StringType, types.UnicodeType)


#
# Adds 'windows-1251' alias for 'cp1251' charset in Python < 2.2
#

try:
    u''.encode('windows-1251')

except LookupError:
    patch('encodings')

    from encodings.aliases import aliases as encodings_aliases
    from encodings import _cache as encodings_cache

    encodings_aliases['windows_1251'] = 'cp1251'
    del encodings_cache['windows-1251']


from smtplib import SMTP
if not hasattr( SMTP, 'login' ): # python < 2.2
    import base64
    from smtplib import SMTPException

    try:
        import hmac
    except ImportError:
        hmac = None

    def encode_base64(s, eol=None):
        return "".join(base64.encodestring(s).split("\n"))

    def encode_cram_md5(challenge, user, password):
        challenge = base64.decodestring(challenge)
        response = user + " " + hmac.HMAC(password, challenge).hexdigest()
        return encode_base64(response, eol="")

    def encode_plain(user, password):
        return encode_base64("%s\0%s\0%s" % (user, user, password), eol="")

    def smtp_login(self, user, password):
        """
            For Python 2.1 and lower compatibility.

            Log in on an SMTP server that requires authentication.

            The arguments are:
            - user:     The user name to authenticate with.
            - password: The password for the authentication.

            If there has been no previous EHLO or HELO command this session, this
            method tries ESMTP EHLO first.

            This method will return normally if the authentication was successful.

        """

        AUTH_PLAIN = "PLAIN"
        AUTH_CRAM_MD5 = "CRAM-MD5"
        AUTH_LOGIN = "LOGIN"

        if self.helo_resp is None and self.ehlo_resp is None:
            if not (200 <= self.ehlo()[0] <= 299):
                (code, resp) = self.helo()
                if not (200 <= code <= 299):
                    raise SMTPHeloError(code, resp)

        if not self.has_extn("auth"):
            raise SMTPException("SMTP AUTH extension not supported by server.")

        # Authentication methods the server supports:
        authlist = self.esmtp_features["auth"]
        if authlist.startswith('='):
            authlist = authlist[1:]
        authlist = authlist.split()

        # List of authentication methods we support: from preferred to
        # less preferred methods. Except for the purpose of testing the weaker
        # ones, we prefer stronger methods like CRAM-MD5:

        preferred_auths = [AUTH_CRAM_MD5, AUTH_PLAIN, AUTH_LOGIN]
        if hmac is None:
            preferred_auths.remove(AUTH_CRAM_MD5)

        # Determine the authentication method we'll use
        authmethod = None
        for method in preferred_auths:
            if method in authlist:
                authmethod = method
                break

        if authmethod == AUTH_CRAM_MD5:
            (code, resp) = self.docmd("AUTH", AUTH_CRAM_MD5)
            if code == 503:
                # 503 == 'Error: already authenticated'
                return (code, resp)
            (code, resp) = self.docmd(encode_cram_md5(resp, user, password))
        elif authmethod == AUTH_PLAIN:
            (code, resp) = self.docmd("AUTH",
                AUTH_PLAIN + " " + encode_plain(user, password))
        elif authmethod == AUTH_LOGIN:
            (code, resp) = self.docmd("AUTH",
                "%s %s" % (AUTH_LOGIN, encode_base64(user, eol="")))
            if code != 334:
                raise SMTPException("Authorization failed.")
            (code, resp) = self.docmd(encode_base64(password, eol=""))
        elif authmethod == None:
            raise SMTPException("No suitable authentication method found.")
        if code not in [235, 503]:
            # 235 == 'Authentication successful'
            # 503 == 'Error: already authenticated'
            raise SMTPException("Authorization failed.")
        return (code, resp)

    patch('smtplib')
    
    SMTP.login = smtp_login

#
# Adds 'get', 'set', 'reduce', 'html_quote', 'url_quote'
# and 'url_quote_plus' functions to DTML builtins.
#

patch('TemplateDict')

from AccessControl.ZopeGuards import guarded_getitem
from DocumentTemplate.DT_Util import TemplateDict, NotBindable, safe_callable
from DocumentTemplate.DT_Var import html_quote, url_quote, url_quote_plus

def guarded_reduce(f, seq, init=Missing):
    safe_seq = []
    for idx in range(len(seq)): # use enumerate in python 2.3
        item = guarded_getitem(seq, idx)
        safe_seq.append(item)
    if init is Missing:
        return reduce(f, safe_seq)
    return reduce(f, safe_seq, init)

def TemplateDict_get( self, key, default=None, call=False ):
    try:
        return self.getitem( key, call )
    except KeyError:
        return default

def TemplateDict_set( self, key, value ):
    stack = []
    data = last_dict = None
    while True:
        try:
            stack.append( self._pop() )
        except IndexError:
            break
        if not isinstance( stack[-1], DictType ):
            if data is None:
                data = last_dict
            continue
        last_dict = stack[-1]
        if last_dict.has_key( key ):
            data = last_dict
            break
    while stack:
        self._push( stack.pop() )
    if data is None:
        raise TypeError, self
    data[ key ] = value

TemplateDict.get            = TemplateDict_get
TemplateDict.set            = TemplateDict_set
TemplateDict.reduce         = NotBindable( guarded_reduce )
TemplateDict.html_quote     = NotBindable( html_quote )
TemplateDict.url_quote      = NotBindable( url_quote )
TemplateDict.url_quote_plus = NotBindable( url_quote_plus )


#
# Enables dtml-in tag to use methods as sorting keys.
#
# Enhances make_sortfunctions to use new sort functions
#

patch('DT_In')

from DocumentTemplate import DT_In
from DocumentTemplate.sequence import SortEx

def DT_In_basic_type( value ):
    try:
        return DT_In._nau_basic_type( value )
    except TypeError:
        return False

try:
    DT_In.basic_type( {}.get )
except TypeError:
    DT_In._nau_basic_type = DT_In.basic_type
    DT_In.basic_type = DT_In_basic_type

_sorters = DT_In._sorters = {}

def DT_In_make_sortfunctions(sortfields, md):
    """Accepts a list of sort fields; splits every field, finds comparison
    function. Returns a list of 3-tuples (field, cmp_function, asc_multplier)"""

    sf_list = []
    for f in sortfields:
        if isinstance(f, basestring):
            f = f.split('/')
        elif isinstance(f, tuple):
            f = list(f)
        l = len(f)

        if l == 1:
            f.append('cmp')
            f.append('asc')
        elif l == 2:
            f.append('asc')
        elif l == 3:
            pass
        else:
            raise SyntaxError, "sort option must contain no more than 2 slashes"

        f_name = f[1]

        func = _sorters.get(f_name ) or md.getitem(f_name, 0)
        if isinstance( func, ClassType):
            func = func(md) # func is class, so make object

        sort_order = f[2].lower()

        if sort_order in ('asc', ''):
            multiplier = +1
        elif sort_order in ('desc', 'reverse'):
            multiplier = -1
        else:
            raise SyntaxError, "sort oder must be either ASC or DESC"

        sf_list.append((f[0], func, multiplier))

    return sf_list

DT_In.make_sortfunctions = DT_In_make_sortfunctions
sys.modules['DocumentTemplate.sequence.SortEx'].make_sortfunctions = DT_In_make_sortfunctions


#
# 1. Provides HTTPRequest with a hacked variant of cgi.escape function
# to prevent errors during request stringification (non-string keys
# in request or response data container are the cause).
#
# 2. Adds 'setdefault' method for the record object.
#

patch('HTTPRequest')

from ZPublisher import HTTPRequest

def HTTPRequest_escape( s, quote=None ):
    return escape( str(s), quote )

def record_setdefault( self, key, value ):
    return self.__dict__.setdefault( key, value )

HTTPRequest.escape = HTTPRequest_escape
HTTPRequest.record.setdefault = record_setdefault


#
# Saves objects modified by their _initstate method during autoupdate.
# The reason to have this is that it is impossible to set _p_changed
# flag inside __setstate__.
#
'''
LOG.info( 'Patching Transaction' )

from ZODB.Transaction import Transaction

def transaction_commit( self, subtransaction=None ):
    #LOG.debug( 'in Transaction.commit hook' )

    for ob in self._objects:
        if not getattr( ob, '_Persistent__changed', None ):
            continue

        del ob._Persistent__changed
        if not ob._p_changed:
            ob._p_changed = 1

        try:    ob_repr = repr(ob)
        except: ob_repr = '<%s instance at 0x%x>' % (ob.__class__.__name__, id(ob))

        try:    ob_id = ob.getId()
        except: ob_id = getattr( ob, '__name__', '<unknown>' )

        LOG.debug( 'Transaction.commit: updated %s [%s]' % (ob_repr, ob_id) )

    self._nau_commit( subtransaction )

if not hasattr( Transaction, '_nau_commit' ):
    Transaction._nau_commit = Transaction.commit

Transaction.commit = transaction_commit
'''

#
# 1. Adds 'True' and 'False' values to Python Script and DTML builtins.
#
# 2. Adds 'reduce' functions to Python Script builtins.
#
# 3. Adds 'values' method to python scripts -- returns actual script
# parameters as a dictionary.
#

patch('PythonScript')

from AccessControl import safe_builtins
from RestrictedPython.Eval import RestrictionCapableEval
from Products.PythonScripts import PythonScript
from Products.CMFCore.FSPythonScript import FSPythonScript

RestrictionCapableEval.globals['True']  = True
RestrictionCapableEval.globals['False'] = False
RestrictionCapableEval.globals['Missing'] = Missing

safe_builtins['True']  = True
safe_builtins['False'] = False
safe_builtins['Missing'] = Missing

safe_builtins['reduce'] = guarded_reduce
PythonScript.safe_builtins = safe_builtins

PythonScript = PythonScript.PythonScript

def pythonscript_values( self, **kw ):
    res  = {}
    vars = getframe(1).f_locals
    skip = ['self','REQUEST']

    for name in self.params().split(','):
        name = name.split('=', 1)[0].strip()
        if name not in skip and vars.has_key( name ):
            res[ name ] = vars[ name ]

    res.update( kw )
    return res

PythonScript.values   = pythonscript_values
FSPythonScript.values = pythonscript_values

#
# 1. Modifies newSecurityManager function to preserve SecurityContext
# stack during authorization process, but only if the new user is the
# same as the old one, or if the user is just getting authenticated.
#
# 2. Relaxes SecurityManager.addContext behaviour -- increase stack
# only if new context is an owned object or has proxy roles set on it;
# in particular, filesystem-based objects bypass this restriction.
#
# Required for ProxyAccessProvider.
#

patch('SecurityManagement')

from AccessControl import SecurityManagement
from AccessControl import SpecialUsers
from AccessControl import User
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.SecurityManager import SecurityManager
from AccessControl.SecurityManagement import SecurityContext, \
        get_ident, _managers as SecurityManagers

def security_newSecurityManager( request, user ):
    """Set up a new security context for a request for a user
    """
    thread_id = get_ident()
    security  = SecurityManagers.get( thread_id, None )
    #print '@@@ in newSecurityManager', thread_id, \
    #   (hasattr(security,'_context') and security._context.stack or '-')

    if security is not None:
        #print '@@@', thread_id, security._context.user, user
        old = aq_base( security._context.user )
        if old is aq_base( user ):
            return
        if old is SpecialUsers.nobody:
            security._context.user = user
            for context in security._context.stack:
                try: context.securityUserChanged()
                except AttributeError: pass
            return

    #print '@@@ creating new SecurityManager'
    SecurityManagers[ thread_id ] = SecurityManager(
        thread_id,
        SecurityContext(user),
        )

SecurityManagement.newSecurityManager = security_newSecurityManager
User.newSecurityManager = security_newSecurityManager
App.startup.newSecurityManager = security_newSecurityManager

def sm_setSecurityManager( manager ):
    """install *manager* as current security manager for this thread."""
    thread_id = get_ident()
    old = SecurityManagers.get( thread_id, None )
    SecurityManagers[ thread_id ] = manager
    return old

if not hasattr(SecurityManagement,'setSecurityManager'):
    SecurityManagement.setSecurityManager = sm_setSecurityManager

def security_addContext( self, object, force=None ):
    if not force:
        base  = aq_base( object )
        force = getattr( base, '_owner', None ) is not None
        force = force or getattr( base, '_proxy_roles', None )
    if force:
        #print '@@@ addContext', getattr(object, 'id', ''), type(aq_base(object)), object.getOwner()
        self._nau_addContext( object )

if not hasattr( SecurityManager, '_nau_addContext' ):
    SecurityManager._nau_addContext = SecurityManager.addContext

SecurityManager.addContext = security_addContext


#
# 1. Adds proxy roles and executable owner checking to checkPermission
# for ProxyAccessProvider.
#
# 2. Prevents VersionableRoles from merging versionable content local
# roles with local roles of the currently selected version, thus we can
# safely check version objects for permissions.
#

patch('ZopeSecurityPolicy')

from AccessControl.ZopeSecurityPolicy import ZopeSecurityPolicy

def zope_checkPermission( self, permission, object, context ):
    roles = rolesForPermissionOn( permission, object )
    if type(roles) is StringType:
        roles = [ roles ]

    versionable = None
    if hasattr( aq_base(object), 'implements') and object.implements('isVersion'):
        versionable = object.getVersionable()

    if versionable is not None:
        versionable._v_disable_versionable_roles = 1

    try:
        result = context.user.allowed( object, roles )

    finally:
        if hasattr( versionable, '_v_disable_versionable_roles' ):
            del versionable._v_disable_versionable_roles

    if not result:
        # try proxy roles
        if self._checkProxyRoles( object, roles, context ):
            result = 1

    return result

def zope_checkProxyRoles( self, object, roles, context ):
    if not context.stack:
        return 0

    eo = context.stack[-1]

    proxy_roles = getattr( eo, '_proxy_roles', None )
    if not proxy_roles:
        return 0

    # If the executable had an owner, can it execute?
    if getattr( self, '_ownerous', 1 ):
        owner = eo.getOwner()
        if (owner is not None) and not owner.allowed( object, roles ):
            return 0

    for r in proxy_roles:
        if r in roles:
            return 1

    return 0

ZopeSecurityPolicy.checkPermission = zope_checkPermission
ZopeSecurityPolicy._checkProxyRoles = zope_checkProxyRoles


#
# The same as above, but for _checkPermission in CMFCore.
#

patch('CMFCore')

from Products.CMFCore import utils as CMFCoreUtils

def cmfcore_checkPermission( permission, object ):
    roles = rolesForPermissionOn( permission, object )
    if type(roles) is StringType:
        roles = [ roles ]

    # XXX Dummy hack to prevent VersionableRoles from merging versionable content
    # local roles with local roles of the currently selected version, thus we can
    # safely check version objects for permissions.

    versionable = None
    if hasattr( aq_base(object), 'implements') and object.implements('isVersion'):
        versionable = object.getVersionable()

    if versionable is not None:
        versionable._v_disable_versionable_roles = 1

    try:
        security = getSecurityManager()
        result   = security.getUser().allowed( object, roles )

    finally:
        if hasattr( versionable, '_v_disable_versionable_roles' ):
            del versionable._v_disable_versionable_roles

    if not result:
        # try proxy roles
        #print '######', security._context.user, security._context.stack
        if security._policy._checkProxyRoles( object, roles, security._context ):
            result = 1

    return result

CMFCoreUtils._checkPermission = cmfcore_checkPermission


#
# Security performance optimization -- when gathering permission
# names from the class inheritance, cache result and return it on
# subsequent calls.  Speeds up content creation and copying.
#

patch('Role')

from AccessControl import Role
from Products.DCWorkflow import utils as DCWorkflowUtils

def role_gather_permissions( klass, result, seen ):
    cache = klass.__dict__.get('__ac_permissions_cache__')

    if cache is None:
        cache = {}

        bases = list( klass.__bases__ )
        while bases:
            base = bases.pop(0)

            perms = base.__dict__.get('__ac_permissions_cache__')
            if perms is not None:
                cache.update( perms )

            else:
                perms = base.__dict__.get('__ac_permissions__')
                if perms is not None:
                    for p in perms:
                        cache.setdefault( p[0], (p[0], ()) )
                bases = list( base.__bases__ ) + bases

        klass.__ac_permissions_cache__ = cache

    for name, value in cache.items():
        if not seen.has_key( name ):
            seen[ name ] = None
            result.append( value )

    return result

Role.gather_permissions = role_gather_permissions
CMFCoreUtils.gather_permissions = role_gather_permissions
DCWorkflowUtils.gather_permissions = role_gather_permissions


#
# Fixes missing BasicGroup.getId method, adds new isReadOnly method,
# and sets up reasonable attribute access.
#

patch( 'BasicGroup' )

from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import Item
from Products.NuxUserGroups.UserFolderWithGroups import BasicGroup

# must have clear name for __roles__ to be accessible
def isReadOnly( self ):
    return 0

def isUsersStorage( self ):
    return 0

BasicGroup.getId = Item.getId.im_func
BasicGroup.isReadOnly = isReadOnly
BasicGroup.isUsersStorage = isUsersStorage

security = ClassSecurityInfo()
security.declarePublic( 'getId', 'isReadOnly', 'isUsersStorage', 'Title' )

# this basically removes security declaration for Title
perms = []
skip  = lambda name, has=security.names.has_key: not has(name)
for item in BasicGroup.__ac_permissions__:
    perms.append( item[:1] + (filter( skip, item[1] ),) + item[2:] )
BasicGroup.__ac_permissions__ = tuple(perms)

security.apply( BasicGroup )


#
# Allows for portal object to define _afterValidateHook callback method,
# which will be called during HTTP request processing, right after the user
# is authenticated and becomes known.
#

import Zope2
from Products.CMFCore.utils import getToolByName
from ZPublisher.Publish import get_module_info

def zpublisher_validated_hook( self, user ):
    if Zope2 is None:
        return

    Zope2._nau_zpublisher_validated_hook( self, user )

    try:
        published = self.PUBLISHED
        if type(published) in [ MethodType,]:
            published = published.im_self
        portal = published.getPortalObject()
    except AttributeError:
        pass
    else:
        if hasattr( portal, '_afterValidateHook' ):
            portal._afterValidateHook( user, published, REQUEST=self )

zpublisher_validated_hook._nau = True

def install_validated_hook( *args ):
    # Wait for old validate_hook
    while Zope2.zpublisher_validated_hook is None:
        time.sleep(0.5)

    if not hasattr( Zope2, '_nau_zpublisher_validated_hook' ):
        patch('ZPublisher validate_hook')
        Zope2._nau_zpublisher_validated_hook = Zope2.zpublisher_validated_hook
        Zope2.zpublisher_validated_hook = zpublisher_validated_hook

        # drop modules cache
        modules_cache = get_module_info.func_defaults[0]
        if modules_cache:
            modules_cache.clear()

if hasattr( Zope2, '_nau_zpublisher_validated_hook' ):
    # some insane had used refresh
    patch('ZPublisher validate_hook')
    Zope2.zpublisher_validated_hook = zpublisher_validated_hook
else:
    LOG.debug( 'Registering callback' )
    threading.Thread( target=install_validated_hook, args=(), kwargs={} ).start()




#
# 1. ZCatalog performance optimization -- uses fast multiunion instead
# of a loop to merge subsets into resulting set.  Speeds up queries
# utilizing 'effective' index.
#
# 2. Adds 'not', 'and_not', 'or_not' ( 'and_not'=='not' ) operators for index queries.
#
# 3. Adds 'operator' to query options to Field and Date Indexes
#
# 4. extends PathIndex to use depth parameter.
#
# 5. changes PathIndex`s leafs class to IITreeSet from IISet.

patch('UnIndex')

from types import IntType
from BTrees.IIBTree import IISet, IITreeSet, union, intersection, difference
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.PluginIndexes.common.util import parseIndexRequest
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from Products.PluginIndexes.PathIndex.PathIndex import PathIndex

try:
    from BTrees.IIBTree import multiunion
except ImportError: # Zope < 2.6
    multiunion = None

if multiunion is None:
    def multiunion( seq ):
        return reduce( union, seq, None )

def multiintersection( seq ):
    return reduce( intersection, seq, None )

def unindex_apply_index( self, request, cid='' ):
    if isinstance( request, parseIndexRequest ):
        record = request
    else:
        record = parseIndexRequest(request, self.id, self.query_options)

    # XXXXX in 2.7 Zope Catalog record.keys may be () or []
    if Config.Use27CatalogQuery and record.keys is None or not record.keys:
        return None

    index = self._index
    r = opr = None

    # experimental code for specifing the operator
    operator = record.get('operator', self.useOperator)
    # XXX: operators should be attribute of the class not instance
    if not operator in self.operators:
        if operator in ['not', 'and_not', 'or_not'] and self.meta_type in [ 'FieldIndex', 'DateIndex', 'KeywordIndex' ]:
            self.operators = tuple( self.operators ) + (operator,)
        else:
            raise RuntimeError,"operator not valid: %s" % escape(operator)

    # depending on the operator we use intersection or union
    if operator.startswith('and'):
        set_func = intersection
        multi_set_func = multiintersection
    else:
        set_func = union
        multi_set_func = multiunion

    # Range parameter
    range_parm = record.get('range')
    if range_parm:
        opr = 'range'
        opr_args = []
        if range_parm.find('min') > -1:
            opr_args.append('min')
        if range_parm.find('max') > -1:
            opr_args.append('max')

    if record.get('usage'):
        # see if any usage params are sent to field
        opr = record.usage.lower().split(':')
        opr, opr_args=opr[0], opr[1:]

    if opr == 'range':   # range search
        if 'min' in opr_args:
            lo = min(record.keys)
        else:
            lo = None
        if 'max' in opr_args:
            hi = max(record.keys)
        else:
            hi = None

        r = multi_set_func( index.values(lo,hi) )

    else: # not a range search
        for key in record.keys:
            r = set_func( r, index.get(key, IISet()) )

    if operator.endswith('not'):
        r = difference( IISet(self._unindex.keys()), r )

    if r is None:
        r = IISet()
    elif isinstance( r, IntType ):
        r = IISet([r])

    return r, (self.id,)

UnIndex._apply_index = unindex_apply_index

def dateindex_apply_index( self, request, cid='' ):
    record = parseIndexRequest(request, self.id, self.query_options)

    # XXXXX in 2.7 Zope Catalog record.keys may be () or []
    if Config.Use27CatalogQuery and record.keys is None or not record.keys:
        return None

    record.keys = map( self._convert, record.keys )

    return UnIndex._apply_index( self, record, cid=cid)

DateIndex._apply_index = dateindex_apply_index

for Index in [ FieldIndex, DateIndex ]:
    if 'operator' not in Index.query_options:
        Index.query_options.append( 'operator' )


patch('PathIndex')
PathIndex_LOG = getLogger( 'PathIndex' )

def pathindex_insertEntry(self, comp, id, level):
    """Insert an entry.

       comp is a path component 
       id is the docid
       level is the level of the component inside the path
    
       patched to use IITreeSet
    """
    index = self._index
    if not index.has_key(comp):
        index[comp] = IOBTree()

    if not index[comp].has_key(level):
        index[comp][level] = IITreeSet()

    index[comp][level].insert(id)

    if level > self._depth:
        self._depth = level

def pathindex_index_object(self, docid, obj, threshold=100):
    """ hook for (Z)Catalog """

    # PathIndex first checks for an attribute matching its id and
    # falls back to getPhysicalPath only when failing to get one.
    # The presence of 'indexed_attrs' overrides this behavior and
    # causes indexing of the custom attribute.

    attrs = getattr(self, 'indexed_attrs', None)
    if attrs:
        index = attrs[0]
    else:
        index = self.id

    f = getattr(obj, index, None)
    if f is not None:
        if safe_callable(f):
            try:
                path = f()
            except AttributeError:
                return 0
        else:
            path = f

        if not isinstance(path, (StringType, TupleType)):
            raise TypeError('path value must be string or tuple of strings')
    else:
        try:
            path = obj.getPhysicalPath()
        except AttributeError:
            return 0

    if isinstance(path, (ListType, TupleType)):
        comps = filter(None, path)
        path = '/'.join(path)
    elif isinstance( path, StringType ):
        comps = filter(None, path.split('/') )
    else:
        raise TypeError( path )

    len_comps = len( comps )

    # Make sure we reindex properly when path change
    if self._unindex.get(docid, path) != path:
        self.unindex_object(docid)

    # 2.7 Index length Support 
    #if not self._unindex.has_key(docid):
    #    if hasattr(self, '_migrate_length'):
    #        self._migrate_length()
    #    self._length.change(1)

    for i in range(len_comps): # enumerate in python 2.3
        self.insertEntry(comps[i], docid, i)

    # Add terminator
    self.insertEntry(None, docid, len_comps-1)

    # XXX
    if not path.startswith('/'):
        path = '/'+path

    self._unindex[docid] = path
    return 1

def pathindex_unindex_object(self, docid):
    """ hook for (Z)Catalog """

    if not self._unindex.has_key(docid):
        PathIndex_LOG.error( 'Attempt to unindex nonexistent document'
                             ' with id %s' % docid)
        return

    # There is an assumption that paths start with /
    path = self._unindex[docid]

    # redundant
    #if not path.startswith('/'):
    #    path = '/'+path

    comps = filter( None, path.split('/') )
    len_comps = len( comps )

    def unindex(comp, level, index=self._index, docid=docid):
        try:
            index[comp][level].remove(docid)

            if not index[comp][level]:
                del index[comp][level]

            if not index[comp]:
                del index[comp]
        except KeyError:
            PathIndex_LOG.error( 'Attempt to unindex document'
                                 ' with id %s failed at level'
                                 ' %s' % (docid, level) )

    for level in range(len_comps):
        unindex(comps[level], level)

    # Remove the terminator
    unindex( None, len_comps - 1 )

    # 2.7 Index length Support 
    #if hasattr(self, '_migrate_length'):
    #    self._migrate_length()
    #  self._length.change(-1)

    del self._unindex[docid]

def pathindex_search(self, path, default_level=0, depth=0):
    """
    path is either a string representing a
    relative URL or a part of a relative URL or
    a tuple (path,level).

    level >= 0  starts searching at the given level
    level <  0  search on all levels

    depth if greater then zero search only down to a depth value
  
    """
    assert isinstance( depth, IntType), `depth`

    if isinstance(path, StringType):
        startlevel = default_level
    else:
        path  = path[0]
        startlevel = int(path[1])

    comps = filter(None, path.split('/'))
    len_comps = len( comps )

    if not len_comps and not depth:
        return IISet(self._unindex.keys())

    index = self._index
    results = None

    startlevels = startlevel >=0 and [startlevel] or range(self._depth + 1)

    for startlevel in startlevels:

        ids = None
        for level in range(startlevel, startlevel + len_comps):
            comp = comps[level-startlevel]

            try:
                ids = intersection(ids, index[comp][level])
            except KeyError:
                break # path not founded

        else:
            if depth:
                endlevel = startlevel + len_comps - 1
                try:             
                    depthset = multiunion( index[None].values( endlevel
                                                             , endlevel + depth
                                                             )
                                         )
                except KeyError:
                    pass
                else:
                    ids = intersection( ids, depthset )

            results = union( results, ids )

    return results or IISet()

def pathindex_apply_index(self, request, cid=''):
     """ hook for (Z)Catalog
         'request' --  mapping type (usually {"path": "..." }
         additionaly a parameter "path_level" might be passed
         to specify the level (see search())

         'cid' -- ???
     """

     record = parseIndexRequest(request,self.id,self.query_options)
     if record.keys==None: return None

     level    = record.get('level',0)
     operator = record.get('operator',self.useOperator).lower()
     depth    = record.get('depth', 0)

     # depending on the operator we use intersection of union
     if operator == "or":  set_func = union
     else: set_func = intersection

     res = None
     for k in record.keys:
         rows = self.search(k, level, depth)
         res = set_func(res,rows)

     return res or IISet(), (self.id,)

def pathindex_keyForDocument(self, id ):
    return aq_parent(self).paths[id]

def pathindex_documentToKeyMap(self):
    return aq_parent(self).paths

def pathindex_items(self):
    return aq_parent(self).uids.items()
    

# TODO: write own PathIndex class
PathIndex.insertEntry = pathindex_insertEntry
PathIndex.index_object = pathindex_index_object
PathIndex.unindex_object = pathindex_unindex_object
PathIndex.search = pathindex_search
PathIndex._apply_index = pathindex_apply_index
PathIndex.keyForDocument = pathindex_keyForDocument
PathIndex.documentToKeyMap = pathindex_documentToKeyMap
PathIndex.items = pathindex_items

for Index in [ PathIndex ]:
    for name in [ 'depth' ]:
        if name not in Index.query_options:
            Index.query_options = tuple(Index.query_options) + (name,)


#
# Enable AttributesIndex sorting feature by means of using
# special sort index returned by getSortIndex.
#

patch('Catalog')

from Products.ZCatalog.Catalog import Catalog, CatalogError

def Catalog_getSortIndex(self, args):
    """Returns a search index object or None."""
    sort_index_name = self._get_sort_attr("on", args)
    if sort_index_name is not None:
        # self.indexes is always a dict, so get() w/ 1 arg works
        sort_index = self.indexes.get(sort_index_name)
        if sort_index is None:
            raise CatalogError, 'Unknown sort_on index'
        else:
            sort_index = sort_index.__of__(self) # XXX use self.getIndex instead
            if hasattr(sort_index, 'getSortIndex'):
                sort_index = sort_index.getSortIndex(args)

            if not hasattr(sort_index, 'keyForDocument'):
                raise CatalogError(
                    'The index chosen for sort_on is not capable of being'
                    ' used as a sort index.'
                    )
        return sort_index
    else:
        return None

Catalog._getSortIndex = Catalog_getSortIndex


#
# Implements support for 'restrictions' (aka anti-permissions).
# Required for object 'freezing' feature.
#

patch('Permissions')

from Acquisition import Implicit
from AccessControl import Permission as PermissionModule
from AccessControl.Permission import Permission, name_trans
from AccessControl.PermissionRole import rolesForPermissionOn

class RestrictedPermission( Implicit ):

    def __init__( self, name, roles ):
        self.roles = roles
        self.name = name

    def __of__( self, parent ):
        if Config.DisableAccessRestrictions:
            return self.roles

        if aq_parent( parent ) is None:
            return self
        return self.getRestrictedRoles( parent )

    def __repr__( self ):
        return repr( self.getRestrictedRoles() )

    def getRestrictedRoles( self, object=None ):
        if object is None:
            object = aq_parent( aq_inner( self ) )

        # XXX implement restrictions cache
        ac_restrs = getattr( object, '__ac_restricted_permissions__', None)
        if ac_restrs:
            restriction = ac_restrs.get( self.name )
            if type( restriction ) is StringType:
                roles = [ r for r in self.roles if r not in \
                            rolesForPermissionOn( restriction, object, () ) ]
                if type( self.roles ) is TupleType:
                    roles = tuple( roles )
                return roles
        return self.roles

    def getDefaultRoles( self ):
        return self.roles

PermissionModule.RestrictedPermission = RestrictedPermission

def permission__init__(self,name,data,obj,default=None):
    self.name=name
    self._p='_'+translate(name,name_trans)+"_Permission"
    self.data=data
    self.obj=aq_inner( obj )
    self.default=default

Permission.__init__ = permission__init__

def permission_setRoles(self, roles):
    obj=self.obj
    if type(roles) is ListType and not roles:
        if hasattr(obj, self._p): delattr(obj, self._p)
    else:
        ac_restrs = getattr( obj, '__ac_restricted_permissions__', None )
        if ac_restrs and type( ac_restrs.get( self.name ) ) is StringType:
            roles = RestrictedPermission( self.name, roles )
        setattr(obj, self._p, roles)

    for name in self.data:
        if name=='': attr=obj
        else: attr=getattr(obj, name)
        try: del attr.__roles__
        except: pass
        try: delattr(obj,name+'__roles__')
        except: pass

Permission.setRoles = permission_setRoles


#
# Tweak access permissions on mxDateTime objects so that they can
# be used from restricted code.
#

patch('mxDateTime')

from mx.DateTime import DateTimeType, RelativeDateTime
from AccessControl.SimpleObjectPolicies import ContainerAssertions

ContainerAssertions[ DateTimeType ] = 1
RelativeDateTime.__allow_access_to_unprotected_subobjects__ = 1


#
# Extends CMF filesystem directory views to use paths relative
# to SOFTWARE_HOME, providing for database mobility between
# differently configured Zope installations.
#
# XXX maybe should patch minimalpath instead
#

patch('DirectoryRegistry')

from os import path
from Globals import SOFTWARE_HOME
from Products.CMFCore.DirectoryView import DirectoryRegistry
from Products.CMFCore.utils import minimalpath

def directoryregistry_getDirectoryInfo( self, dirpath ):
    dirpath = path.normpath( dirpath )
    if not self._directories.has_key( dirpath ):
        dirpath = path.join( minimalpath(SOFTWARE_HOME), dirpath )
    return self._directories.get( dirpath, None )

DirectoryRegistry.getDirectoryInfo = directoryregistry_getDirectoryInfo


#
# Sets a global flag in request indicating that an object on external
# site is being published.
#

patch('CMFSite')

from Products.CMFDefault.Portal import CMFSite

def cmfsite_traverseHook( self, container, request, *args ):
    request.set( 'ExternalPublish', 1 )

CMFSite._nausite_traverseHook = cmfsite_traverseHook


#
# Adds a Visitor role to the current user if request for an object
# on external site is being handled.
#

patch('SimpleUser')

from AccessControl.User import SimpleUser
from Products.Localizer import get_request
try:
    from Products.LDAPUserFolder.LDAPUser import LDAPUser
except ImportError:
    LDAPUser = None

# use original method name for __roles__ to work
def getRoles( self ):
    roles = self._nau_getRoles()

    request = aq_get( self, 'REQUEST', get_request() )
    if request is None:
        return roles

    if request.other.get( 'ExternalPublish' ):
        roles += (Config.VisitorRole,)

    return roles

if not hasattr( SimpleUser, '_nau_getRoles' ):
    SimpleUser._nau_getRoles = SimpleUser.getRoles
SimpleUser.getRoles = getRoles

if LDAPUser is not None:
    if not hasattr( LDAPUser, '_nau_getRoles' ):
        LDAPUser._nau_getRoles = LDAPUser.getRoles
    LDAPUser.getRoles = getRoles


#
# Adds method for retrieving the language name by it's code.
#

try:
    from Products.Localizer.Utils import get_language_name

except ImportError:
    patch('LanguageManager')

    from Products.Localizer.LanguageManager import LanguageManager
    from Products.Localizer.Utils import languages

    def get_language_name( self, id=None ):
        if id is None:
            id = self.get_default_language()
        return languages.get( id, '???' )

    LanguageManager.get_language_name = get_language_name

from Products.Localizer.MessageCatalog import MessageCatalog, empty_po_header
from ZODB.PersistentMapping import PersistentMapping

def messagecatalog_init(self, id, title, languages):
        # XXX inherit MessageCatalog from InstanceBase
        self.id = id
        self.title = title

        # Language Manager data
        self._languages = tuple(languages)
        self._default_language = languages[0]

        # Here the message translations are stored
        self._messages = OOBTree()

        # Data for the PO files headers
        self._po_headers = PersistentMapping()
        for lang in self._languages:
            self._po_headers[lang] = empty_po_header

patch('Localizer')
MessageCatalog.__init__ = messagecatalog_init

#
# replace Localizes`s patch for Publish
# because it deletes reference to REQUEST uncorrectly
#

from ZPublisher import Publish

def _nau_new_publish(request, *args, **kwargs):
    ident = get_ident()
    Publish._requests[ident] = request
    try:
        x = Publish.old_publish(request, *args, **kwargs)
    finally:
        # in the conflict situation 'publish' method called again, recursively.
        # so reference deleted from innermost call, and we need this check.
        if Publish._requests.has_key(ident):
            del Publish._requests[ident]

    return x

# add attr to function to easy validate that it is patched.
_nau_new_publish._nau = True

if hasattr(Publish, 'old_publish') and not hasattr(Publish.publish, '_nau'):
    Publish.publish = _nau_new_publish


#
# Supersedes the Owned.changeOwnership method due to the
# accidental acquisition of the 'objectValues' method from parent
# containers which led to weird and unpredictable results.
#
patch('Owned')

from AccessControl.Owned import Owned, UnownableOwner, ownerInfo

def owned_changeOwnership(self, user, recursive=0, aq_get=aq_get):
    new=ownerInfo(user)
    if new is None: return # Special user!
    old=aq_get(self, '_owner', None, 1)
    if old==new: return
    if old is UnownableOwner: return

    if hasattr( aq_base( self), 'objectValues' ):
        for child in self.objectValues():
            if recursive:
                child.changeOwnership(user, 1)
            else:
                # make ownership explicit
                child._owner=new

    if old is not UnownableOwner:
        self._owner=new

Owned.changeOwnership = owned_changeOwnership


#
# Adds staff list support to BasicUser class
#

patch('BasicUser')

from AccessControl.PermissionRole import _what_not_even_god_should_do
from AccessControl.User import BasicUser
from time import time as now

def listAccessTokens( self,
                      include_userid=True,
                      include_positions=True,
                      include_divisions=True,
                      include_groups=True,
                      include_roles=True,
                      userid_prefix='',
                      role_prefix='role:'
                    ):
    """
        Describes portal-wide user's access capabilities through the list of positions, 
        divisions, roles and groups that current user belongs to.
    """
    # This part should work as fast as possible otherwise it will dramatically 
    # slowdown access control performance.
    # XXX Add in-memory caching ASAP

    global _positions_cache
    global _divisions_cache

    if include_userid:
        yield "%s%s" % ( userid_prefix, self.getUserName() )

    if include_groups:
        for g in self.getGroups():
            yield 'group:%s' % g

    if include_roles:
        for r in self.getRoles():
            yield '%s%s' % (role_prefix, r)

    membership = getToolByName( self, 'portal_membership', None )
    if membership is None:
        return 

    key = membership._p_oid
    # Here we try hard to avoid the call to restrictedTraverse method beacuse 
    # it calls BasicUser.allow, then BasicUser.getGroups consequently and therefore 
    # results to infinite recursion.
    if not hasattr(membership, 'getStaffList'):
        return
    staff_list = membership.getStaffList()
    if staff_list is None:
        return

    if not _positions_cache.has_key( key ):
        _positions_cache[ key ] = {}
    if not _divisions_cache.has_key( key ):
        _divisions_cache[ key ] = {}

    expires = _cache_expires.get( key )
    if expires is None or expires < now():
        entries = staff_list.listEntries().listItems()
        for entry in entries:
            employee = entry.getEntryAttribute( 'employee' )
            deputy = entry.getEntryAttribute( 'deputy' )

            position = entry.getId()
            divisions = {} # use dict to avoid dublicate entries
            if entry.isBranch():
                divisions[ entry.getId() ] = 1
    
            parents = entry.listParentNodes()
            for parent in parents:
                divisions[ parent.getId() ] = 1
    
            for u in [ employee, deputy ]:
                if hasattr( u, 'getEntryAttribute' ):
                    u = u.getEntryAttribute( 'associate_user' )
                user_positions = _positions_cache[ key ].get( u, {} )
	        user_positions[ position ] = 1
                _positions_cache[ key ][ u ] = user_positions
    
                user_divisions = _divisions_cache[ key ].get( u, {} )
                user_divisions.update( divisions )
                _divisions_cache[ key ][ u ] = user_divisions

            _cache_expires[ key ] = now() + CACHE_TIMEOUT

    if include_positions:
        for p in _positions_cache[ key ].get( self.getUserName(), [] ):
            yield 'pos:%s' % p

    if include_divisions:
        for d in _divisions_cache[ key ].get( self.getUserName(), [] ):
            yield 'div:%s' % d

_positions_cache = {}
_divisions_cache = {}
_cache_expires = {}
CACHE_TIMEOUT = 1800

# Built on top of NuxUserGroups.BasicUserWithGroups.allowed class.
def allowed(self, object, object_roles=None):
    """Check whether the user has access to object. The user must
       have one of the roles in object_roles to allow access."""
    if object_roles is _what_not_even_god_should_do: return 0

    # Short-circuit the common case of anonymous access.
    if object_roles is None or 'Anonymous' in object_roles:
        return 1

    # Provide short-cut access if object is protected by 'Authenticated'
    # role and user is not nobody
    if 'Authenticated' in object_roles and (
        self.getUserName() != 'Anonymous User'):
        return 1

    # Check for ancient role data up front, convert if found.
    # This should almost never happen, and should probably be
    # deprecated at some point.
    if 'Shared' in object_roles:
        object_roles = self._shared_roles(object)
        if object_roles is None or 'Anonymous' in object_roles:
            return 1

    # Check for a role match with the normal roles given to
    # the user, then with local roles only if necessary. We
    # want to avoid as much overhead as possible.
    user_roles = self.getRoles()
    for role in object_roles:
        if role in user_roles:
            if self._check_context(object):
                return 1
            return None

    # Still have not found a match, so check local roles. We do
    # this manually rather than call getRolesInContext so that
    # we can incur only the overhead required to find a match.
    inner_obj = getattr(object, 'aq_inner', object)
    user_name = self.getUserName()
    groups = self.getGroups() # groups
    while 1:
        tokens = self.listAccessTokens()
        local_roles = getattr(inner_obj, '__ac_local_roles__', None)
        if local_roles:
            if callable(local_roles):
                local_roles = local_roles()
            dict = local_roles or {}

            local_roles = []
            for name in tokens:
                roles = dict.get( name, [])
                if not roles:
                    continue
                local_roles.extend( roles )

            for role in object_roles:
                if role in local_roles:
                    if self._check_context(object):
                        return 1
                    return 0
        # deal with groups
        local_group_roles = getattr(inner_obj, '__ac_local_group_roles__', None)
        if local_group_roles:
            if callable(local_group_roles):
                local_group_roles = local_group_roles()
            dict = local_group_roles or {}
            for g in groups:
                local_group_roles = dict.get(g, [])
                if local_group_roles:
                    for role in object_roles:
                        if role in local_group_roles:
                            if self._check_context(object):
                                return 1
                            return 0
        # end groups
        inner = getattr(inner_obj, 'aq_inner', inner_obj)
        parent = getattr(inner, 'aq_parent', None)
        if parent is not None:
            inner_obj = parent
            continue
        if hasattr(inner_obj, 'im_self'):
            inner_obj=inner_obj.im_self
            inner_obj=getattr(inner_obj, 'aq_inner', inner_obj)
            continue
        break
    return None

def getRolesInContext(self, object):
    """Return the list of roles assigned to the user,
       including local roles assigned in context of
       the passed in object."""
    name=self.getUserName()
    groups=self.getGroups() # groups
    roles=self.getRoles()
    local={}
    object=getattr(object, 'aq_inner', object)
    while 1:
        tokens = self.listAccessTokens()
        local_roles = getattr(object, '__ac_local_roles__', None)
        if local_roles:
            if callable(local_roles):
                local_roles=local_roles()
            dict=local_roles or {}

            local_roles = []
            for name in tokens:
                lroles = dict.get( name, [])
                if not lroles:
                    continue
                for r in lroles:
                    local[r] = 1

            for r in dict.get(name, []):
                local[r]=1
        # deal with groups
        local_group_roles = getattr(object, '__ac_local_group_roles__', None)
        if local_group_roles:
            if callable(local_group_roles):
                local_group_roles=local_group_roles()
            dict=local_group_roles or {}
            for g in groups:
                for r in dict.get(g, []):
                    local[r]=1
        # end groups
        inner = getattr(object, 'aq_inner', object)
        parent = getattr(inner, 'aq_parent', None)
        if parent is not None:
            object = parent
            continue
        if hasattr(object, 'im_self'):
            object=object.im_self
            object=getattr(object, 'aq_inner', object)
            continue
        break
    roles=list(roles) + local.keys()
    return roles

BasicUser.allowed = allowed
BasicUser.getRolesInContext = getRolesInContext
BasicUser.listAccessTokens = listAccessTokens

#Resolving conflict of Localizer v.0.8.1 and CMFCore v.1.4.8
from Products.CMFCore.FSImage import FSImage
from OFS import Image

FSImage._image_tag = Image.old_tag.im_func

