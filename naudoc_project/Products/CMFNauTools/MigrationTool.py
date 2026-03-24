"""
Product version migration tool.

$Editor: ikuleshov $
$Id: MigrationTool.py,v 1.36 2008/03/21 08:59:44 oevsegneev Exp $
"""
__version__ = '$Revision: 1.36 $'[11:-2]

import copy

from os import listdir
from sys import modules as _sys_modules, exc_info, \
                setrecursionlimit, getrecursionlimit
from threading import Thread, Event
from types import DictType, TupleType, NoneType

import transaction
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent
from App.Common import package_home
from ExtensionClass import Base
from Globals import DTMLFile
from OFS.Uninstalled import Broken, BrokenClass
from OFS.Image import Pdata
from zLOG import LOG, TRACE, INFO, ERROR
from ZPublisher.BaseRequest import RequestContainer

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Config, Exceptions
from SimpleObjects import ToolBase, SimpleRecord
from Utils import InitializeClass, listClassBases, getClassName, \
        SequenceTypes, StringTypes, NumericTypes, loadModules

_migration_contexts = {}

state_init = 'init'
state_start = 'start'
state_check = 'check'
state_configure = 'configure'
state_migrate = 'migrate'

gauge_threshold = 50

writer_event = Event()

class MigrationContext:

    def __init__( self, portal ):
        self.portal = aq_inner(portal)

        self.old_version = portal.getProperty( 'product_version' )
        self.new_version = Config.ProductVersion

        self.old_version_tag = _parseVersion( self.old_version )
        self.new_version_tag = _parseVersion( self.new_version )

        self.state = state_init
        self.state_queue = [state_start, state_check, state_configure, state_migrate]

        self.objects_count = {}
        self.class_order = []
        self.class_bases = {}

        self.script_names = Missing
        self.all_scripts = {}
        self.class_scripts = {}
        self.before_scripts = []
        self.object_scripts = []
        self.after_scripts = []

        self.script_options = {}
        self.script_init = {}

        self.mark_catalog = {}
        self.mark_indexes = {}

        self.default_recursion_limit = 1000

    def register( self ):
        _migration_contexts[ self.portal._p_oid ] = self

    def free( self ):
        del _migration_contexts[ self.portal._p_oid ]

    def cmpVersion( self, version ):
        """
            Compares current portal version against the specified one.

            Arguments:

                'version' -- a version string

            Result:

                Zero if versions are equal, negative value if portal
                is older than the given version, and positive otherwise.

            Exceptions:

                'ValueError' -- version argument is not valid
        """
        return cmp( self.old_version_tag, _parseVersion(version) )

    def markForReindex( self, object=Missing, idxs=Missing, catalog='portal_catalog', recursive=False ):
        # XXX object and recursive are not supported yet
        if idxs is Missing:
            self.mark_catalog[ catalog ] = True
        else:
            marker = self.mark_indexes.setdefault( catalog, {} )
            for idx in idxs:
                marker[idx] = marker.get(idx,0) + 1

    def fixBrokenState( self, object ):
        """
            Restores state of broken object.
        """
        assert isinstance( object, BrokenClass )
        object._p_jar.setstate(object)


class MigrationTool( ToolBase ):
    """
        Product version migration tool.
    """
    _class_version = 1.0

    migration_html_header = DTMLFile( 'migration/dtml/migration_html_header', globals() )
    migration_html_footer = DTMLFile( 'migration/dtml/migration_html_footer', globals() )

    start_form = DTMLFile( 'migration/dtml/start_form', globals() )
    check_form = DTMLFile( 'migration/dtml/check_form', globals() )
    finished_form = DTMLFile( 'migration/dtml/finished_form', globals() )
    configuration_before = DTMLFile( 'migration/dtml/configuration_before', globals() )
    configuration_after = DTMLFile( 'migration/dtml/configuration_after', globals() )

    id = 'portal_migration'
    meta_type = 'NauSite Migration Tool'

    security = ClassSecurityInfo()

    security.declareObjectProtected(CMFCorePermissions.ManagePortal)

    def migrateProduct(self, REQUEST):
        """
        """
        context = self.getMigrationContext( None, REQUEST=REQUEST )

        if context is None:
            return self.getPortalObject().redirect()

        proceed = REQUEST.get('next') or (context.state == state_init)
        if proceed:
            context.state = context.state_queue.pop(0)

        state = context.state
        if state == state_start:
            return self.start_form( self, REQUEST )

        elif state == state_check:
            self.prepareMigration( REQUEST )
            if not context.objects_count:
                self.leaveMigrationMode()
                return self.finished_form( self, REQUEST )

            return self.check_form( self, REQUEST )

        elif state == state_configure:
            if not REQUEST.get('configure_next'):
                self.prepareConfiguration()

                if not context.configuration_queue:
                    return self.configuration_after( self, REQUEST )

                return self.configuration_before( self, REQUEST )
            else:
                now_configuring = context.now_configuring
                if now_configuring:
                    context.script_options[ now_configuring ] = copy.deepcopy( REQUEST.form )

                next_script = self._getNextConfigurableScript()
                if next_script:
                    context.now_configuring = next_script.__name__
                    return next_script.configuration_form.__of__( self )( self, REQUEST )
                else:
                    return self.configuration_after( self, REQUEST )

        elif state == state_migrate:
            self.doMigration(REQUEST)
            self.leaveMigrationMode()
            return self.finished_form( self, REQUEST )

    def _getNextConfigurableScript(self):
        context = self.getMigrationContext()
        try:
            script =  context.configuration_queue.pop()
        except IndexError:
            script = None

        return script

    def prepareConfiguration(self):
        context = self.getMigrationContext()
        if getattr( context, 'configuration_queue', None ) is None:
            all_scripts = context.all_scripts
            scripts_names = context.objects_count.keys()
            scripts = [all_scripts[name] for name in scripts_names]
            context.configuration_queue = [ script for script in scripts if getattr(script, 'configuration_form', None) ]

        context.now_configuring = None

    def getMigrationContext( self, default=Missing, REQUEST=Missing ):
        try:
            context = _migration_contexts[ self.parent()._p_oid ]
        except KeyError:
            if default is Missing:
                raise LookupError, self.parent().getId()
            return default

        if REQUEST is not Missing:
            context.request = RequestContainer( REQUEST=REQUEST )

        context.portal = self.parent()

        return context

    def enterMigrationMode(self):
        if self.getMigrationContext( None ) is not None:
            return

        portal = self.parent()

        Config.MaintainanceMode[ portal._p_oid ] = [ self.getId(), 'migrateProduct' ]
        MigrationContext( portal ).register()

        context = self.getMigrationContext()
        context.default_recursion_limit = getrecursionlimit()
        setrecursionlimit( Config.MigrationRecursionLimit )

    def leaveMigrationMode(self):
        context = self.getMigrationContext()
        setrecursionlimit( context.default_recursion_limit )
        portal  = context.portal
        context.free()

        try: del Config.MaintainanceMode[ portal._p_oid ]
        except: pass

    def prepareMigration( self, REQUEST=None ):
        context = self.getMigrationContext()
        if context.objects_count:
            return

        # TODO - add other useful variables here
        context.product_root = package_home( globals() )
        self._prepareScripts()

        object = context.portal
        counts = context.objects_count

        try:
            self._write( self._header_html() )
            self._write( 'Performing preliminary checks ' )
            for script in context.before_scripts:
                self._writer_start()
                if not script.check or script.check( context, object ):
                    self._write( '. ' )
                    counts[ script.__name__ ] = counts.get( script.__name__, 0 ) + 1
                self._writer_stop()

            self._write( 'done' '<br>' )

            self._write( 'Recursively checking portal objects ' )
            for classes in context.class_order:
                walkObjects( object, self._checkObject, args=(classes,) )
            self._write( 'done' '<br>' )

            self._write( 'Performing final checks ' )
            for script in context.after_scripts:
                self._writer_start()
                if not script.check or script.check( context, object ):
                    self._write( '. ' )
                    counts[ script.__name__ ] = counts.get( script.__name__, 0 ) + 1
                self._writer_stop()
            self._write( 'done' '<br>' )

            self._write( 'Committing transaction . . .' )
            self._writer_start()
            transaction.commit()
            self._writer_stop()
            self._write( 'done' '<br>' )

            self._write( self._proceed_html() )

        except:
            portal_errorlog = getToolByName( self, 'portal_errorlog' )
            portal_errorlog.raising( exc_info() )
            self._write( self._error_html() )
            transaction.abort()

    def doMigration( self, REQUEST=None ):
        context = self.getMigrationContext()
        object  = context.portal

        # TODO - no need to travel all the scripts here,
        # should skip those that has zero objects_count

        try:
            self._write( self._header_html() )
            for script in context.before_scripts:
                LOG( 'MigrationTool.migration:', INFO, 'check before %s' % script.title )
                if not script.check or script.check( context, object ):
                    LOG( 'MigrationTool.migration:', INFO, 'start before %s' % script.title )
                    self._writer_start()
                    self._write( script.title )
                    script.migrate( context, object )
                    # Let the newly created objects to obtain their own oid or walker
                    # will become crazy otherwise.
                    transaction.commit(1)
                    self._writer_stop()
                    self._write( '<br>' )
		    LOG( 'MigrationTool.migration', INFO, 'finish before %s' % script.title )

            self._write( 'Recursively migrating portal objects ' )
            for classes in context.class_order:
	        LOG( 'MigrationTool.migration:', INFO, 'start walk classes' )
                walkObjects( object, self._migrateObject, args=(classes,) )
		LOG( 'MigrationToll.migration:', INFO, 'finish walk classes' )
            self._write( 'done' '<br>' )

            self._write( 'Performing final actions' '<br>' )
            for script in context.after_scripts:
	        LOG( 'MifrationTool.migration:', INFO, 'check after %s' % script.title )
                if not script.check or script.check( context, object ):
		    LOG( 'MigrationTool.migration:', INFO, 'start after %s' % script.title )
                    self._write( script.title )
                    self._writer_start()
                    script.migrate( context, object )
                    transaction.commit(1)
                    self._writer_stop()
                    self._write( '<br>' )
		    LOG( 'MigrationTool.migration:', INFO, 'finish after %s' % script.title)
            self._write( 'done' '<br>' )

            LOG( 'MigrationTool.migration:', INFO, 'start commit transaction' )
            self._write( 'Committing transaction . . .' )
            self._writer_start()
            transaction.commit()
            self._writer_stop()
            self._write( 'done' '<br>' )
            LOG( 'MigrationTool.migration:', INFO, 'finish commit transaction' )

            self._write( self._proceed_html( method='finished_form' ) )

            object._setPropValue( 'fs_storage', Config.EnableFSStorage )
            object._setPropValue( 'product_version', context.new_version )
        except:
            portal_errorlog = getToolByName( self, 'portal_errorlog' )
            portal_errorlog.raising( exc_info() )
            self._write( self._error_html() )
            transaction.abort()

    def _checkConsistency( self, object, container, parents, name ):
        try:
            object._p_mtime
        except POSKeyError, exc:
            self._write( 'x ' )
            LOG( 'ZODB', ERROR, 'Consistency failure. Reference to oid \'%s\' will be removed from %s' % ( `object._p_oid`, `container` ) , error=exc_info() )
            if parents and name:
                if isinstance( container, TupleType ) and len( parents ) >= 2:
                    base = aq_base( object )
                    container_new = tuple( [ x for x in container if not x is base ] )
                    container_name = parents[-1][0]
                    super = parents[-2][1]
                    try:
                        if hasattr( super, '__dict__' ):
                            super.__dict__[ container_name ] = container_new
                        else:
                            super[ container_name ] = container_new
                        super._p_changed = 1
                    except:
                        LOG( 'ZODB', ERROR, 'Can\'t remove reference to oid \'%s\' from %s' % ( `object._p_oid`, `container` ) , error=exc_info() )
                    else:
                        transaction.commit(1)
                    return False

                try:
                    if hasattr( container, '__dict__' ):
                        del container.__dict__[name]
                    else:
                        del container[name]
                    container._p_changed = 1
                    return False
                except:
                    LOG( 'ZODB', ERROR, 'Can\'t remove reference to oid \'%s\' from %s' % ( `object._p_oid`, `container` ) , error=exc_info() )
                else:
                    transaction.commit()

        except AttributeError:
            pass
        except:
            LOG( 'ZODB', ERROR, 'Can\'t load oid \'%s\' from %s' % ( `object._p_oid`, `container` ) , error=exc_info() )
        return True

    def _checkObject( self, object, container, parents, name, classes ):
        self._v_count = getattr( self, '_v_count', 0 ) + 1
        if self._v_count % gauge_threshold == 0:
            self._write( '. ' )

        if not self._checkConsistency( object, container, parents, name ):
            return

        if type(classes) not in SequenceTypes:
            classes = [ classes ]

        context = self.getMigrationContext()
        counts  = context.objects_count

        context.container = container
        context.name = name
        context.parents = parents

        bases = context.class_bases.get( object.__class__ )
        if not bases:
            bases = context.class_bases[ object.__class__ ] = []
            # TODO - add 'inclusive' and 'names' arguments for listClassBases
            for klass in [ object.__class__ ] + listClassBases( object.__class__ ):
                try:
                    bases.insert( 0, getClassName( klass ) )
                except:
                    pass

        for klass in bases:
            if klass not in classes:
                continue

            for script in context.class_scripts[ klass ]:
                if script.strict_classes and getClassName( object.__class__ ) not in script.classes:
                    continue
                if script.check_tag and object._version_tag != object._class_tag:
                    pass # class versions differ
                elif script.check and not script.check( context, object ):
                    continue # check function failed
                elif script.check_tag:
                    continue # versions do match and check function failed -> do not migrate
                counts[ script.__name__ ] = counts.get( script.__name__, 0 ) + 1

    def _migrateObject( self, object, container, parents, name, classes ):
        self._v_count = getattr( self, '_v_count', 0 ) + 1
        if self._v_count % gauge_threshold == 0:
            self._write( '. ' )

        if self._v_count % Config.MigrationSubtransactionThreshold == 0:
            self._write( 'c ' )
            transaction.commit(1)

        if type(classes) not in SequenceTypes:
            classes = [ classes ]
        # assume that context.class_bases was previously initialized
        # by _checkObject
        context = self.getMigrationContext()
        bases = context.class_bases.get( object.__class__, [] )

        # TODO - it is necessary to have not only the direct container,
        # but the nearest enclosing persistent object for class upgrades
        context.container = container
        context.name = name
        context.parents = parents

        try:
            for klass in bases:
                if klass not in classes:
                    continue
                for script in context.class_scripts[ klass ]:
                    if script.strict_classes and getClassName( object.__class__ ) not in script.classes:
                        continue
                    if not script.check or script.check( context, object ):
                        script.migrate( context, object )
        finally:
            del context.container, context.name

    def _prepareScripts(self):
        context = self.getMigrationContext()
        if context.all_scripts:
            return

        # context.script_names exist for debugging purposes
        context.all_scripts = self._loadScripts(context.script_names)
        class_scripts = context.class_scripts = {}
        portal_version = context.old_version_tag

        # XXX Order and dependency.
        for script in context.all_scripts.values():
            version = getattr( script, 'version', None )
            if portal_version and version:
                # Skip scripts with invalid version id.
                try:
                    version = _parseVersion( version )
                except ValueError:
                    #print 'skip(reason 1)', script.__name__
                    continue

                if len(version) > len(portal_version) or portal_version > version:
                    #print 'skip(reason 2)', script.__name__
                    continue

                strict_version = getattr( script, 'strict_version', None )
                if strict_version and portal_version != version:
                    #print 'skip(reason 3)', script.__name__
                    continue

            if not hasattr( script, 'check' ):
                script.check = None

            if not hasattr( script, 'order' ):
                script.order = 50

            classes = getattr( script, 'classes', None )
            if classes:
                if not hasattr( script, 'strict_classes' ):
                    script.strict_classes = False
                if not hasattr( script, 'check_tag' ):
                    script.check_tag = False

                for klass in classes:
                    try: class_scripts[ klass ].append( script )
                    except KeyError: class_scripts[ klass ] = [ script ]

            else:
                # service script
                if getattr( script, 'after_script', None ):
                    context.after_scripts.append( script )
                else:
                    context.before_scripts.append( script )

            broken = getattr( script, 'broken_classes', None )
            if broken:
                for klass in broken:
                    klsname = klass.split('.')[-1]
                    modname = klass[ :-len(klsname)-1 ]
                    module = _sys_modules.setdefault( modname, SimpleRecord() )
                    if not hasattr( module, klsname ):
                        setattr( module, klsname, Broken( None, None, (modname,klsname) ) )

        all_scripts = [ context.after_scripts, context.before_scripts ]
        all_scripts.extend( class_scripts.values() )
        for scripts in all_scripts:
            scripts.sort( lambda x, y: cmp( x.order, y.order ) )

        context.class_order = [ class_scripts.keys() ]

    def _loadScripts(self, script_names = Missing):
        scripts = {}
        # loadModules returns unqualified module names as keys
        for script in loadModules('migration', script_names, refresh = True).values():
            scripts[ script.__name__ ] = script

        if script_names is Missing:
            addons = getToolByName(self, 'portal_addons')

            for addon_id in addons.listActiveAddons():
                for addon_script in loadModules( '%s.%s.migration' % ( Config.AddonsPackageName, addon_id )
                                               , raise_exc=False).values():
                    scripts[ addon_script.__name__ ] = addon_script

        return scripts

    def _write( self, msg, REQUEST=None ):
        if REQUEST is None:
            REQUEST = getattr( self, 'REQUEST', None )

        if REQUEST is not None:
            response = REQUEST['RESPONSE']
            if not getattr( response, '_wrote', None ):
                response.setHeader( 'content-type', 'text/html' )
                response.setHeader( 'content-length', 1 << 30  )
                response.write( ' ' * 1024 )

            response.write( msg )
            response.flush()

    def _stupid_writer( self, text, interval, REQUEST ):
        while not writer_event.isSet():
            writer_event.wait( interval )
            if not writer_event.isSet() and hasattr( REQUEST, 'RESPONSE' ):
                REQUEST['RESPONSE'].write( text )
        writer_event.clear()

    def _writer_start( self, text=' .', interval=15, REQUEST=None ):
        if REQUEST is None:
            REQUEST = getattr( self, 'REQUEST', None )

        if REQUEST is None:
            return

        dispatcher = Thread( target=self._stupid_writer,
                             name='stupid_writer',
                             args=( text, interval, REQUEST )
                           )
        dispatcher.setDaemon(1)
        dispatcher.start()
        return dispatcher

    def _writer_stop( self ):
        writer_event.set()
        while writer_event.isSet():
            Event().wait( 0.01 )

    def _header_html( self ):
        return """
               <script type="text/javascript">//<!--
                   var cleanExit;
                   var leaveText = 'Clicking OK will detach you from the migration tool console but will not stop the migration process. It is strongly recommended to stay on the current page and proceed with migration.';

                   function warnOnUnload()
                   {
                       if ( cleanExit ) return;
                       window.event.returnValue = window.leaveText;
                   }

                   window.onbeforeunload = warnOnUnload;
               //--></script>
               """

    def _proceed_html( self, method='', prompt='Press OK to proceed' ):
        return """
               <form action="%(method)s" method="POST" name="next_form">
                   <input type=submit value=" Next &gt;&gt; ">
               </form>
               <script type="text/javascript">//<!--
                  alert( "%(prompt)s" );
                  cleanExit = true;
                  document.forms['next_form'].submit()
               //--></script>
               """ % { 'prompt': prompt, 'method': method }

    def _error_html( self ):
        portal_errorlog = getToolByName( self, 'portal_errorlog' )
        error_id = portal_errorlog.getLastEntryId()
        error_url = error_id and portal_errorlog.absolute_url( action='error_log_entry', params={'id':error_id} )
        return """
               <br>
               An error occured while walking through the portal objects.
               <p><a href="%(error_url)s" target="_blank">View error log entry</a></p>
               <script type="text/javascript">//<!--
                  cleanExit = true;
               //--></script>

               """ % { 'error_url': error_url }

InitializeClass( MigrationTool )

from BTrees.check import _type2kind

from DateTime import DateTime as DateTimeType

BTreeTypes = tuple( _type2kind.keys() )

_ignored_types = ( StringTypes, NumericTypes, NoneType, BTreeTypes, DateTimeType, Pdata )

from ZODB.POSException import POSKeyError

def walkObjects( object, method, stack=None, parents=[], name=None, args=() ):
    if isinstance( object, _ignored_types ):
        return

    if stack is None:
        stack = {}
    seen = stack.has_key

    p_oid = getattr( object, '_p_oid', None )
    if p_oid is not None:
        if seen( p_oid ):
            return
        stack[ p_oid ] = 1

    # load ghost objects
    try:
        getattr( object, '_p_mtime', None )
    except POSKeyError:
        # Leave broken object unloaded in order to repair it later
        pass

    parent = None
    parents = list( parents )
    if parents:
        parent = parents[-1][1]

    # created acquisition context
    wrapped = object
    if isinstance( parent, Base ) and hasattr( object, '__of__' ):
        try:
            wrapped = object.__of__( parent )
        except TypeError:
            return
        if not hasattr( wrapped, '__class__' ) or type( wrapped ) in _ignored_types:
            wrapped = object

    # execute callback method
    if hasattr( object, '__class__' ):
        apply( method, (wrapped, parent, parents, name) + args )

    parents.append( ( name, wrapped ) )

    # cycle through the object attributes
    try:
        items = object.__dict__.items()
    except:
        pass
    else:
        for key, value in items:
            try:
                if key.startswith('_p_') or key.startswith('_v_'): continue
            except:
                pass
            try:
                if seen( value._p_oid ): continue
            except:
                pass
            walkObjects( value, method, stack, parents, key, args )

    # see whether we've got a mapping or a sequence
    if type(object) not in SequenceTypes + ( DictType, ):
        try:
            if not callable( object.__getitem__ ): return
        except:
            return

    # cycle through the mapping items
    try:
        # first check unwrapped
        getattr( aq_base(object), 'items' )
        items = object.items()
    except:
        pass
    else:
        for key, value in items:
            try:
                if seen( value._p_oid ): continue
            except:
                pass
            walkObjects( value, method, stack, parents, key, args )

    # cycle through the sequence items
    try:
        length = len(object)
    except:
        pass
    else:
        for idx in range( length ):
            try:
                item = object[ idx ]
            except:
                break
            try:
                if seen( item._p_oid ): continue
            except:
                pass
            walkObjects( item, method, stack, parents, idx, args )

def _parseVersion( version ):
    return version and tuple([ int(n) for n in version.split('.') ])

class MigrationError( Exceptions.SimpleError ): pass
Exceptions.MigrationError = MigrationError

def initialize( context ):
    # module initialization callback

    context.registerTool( MigrationTool )
