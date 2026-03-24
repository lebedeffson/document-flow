""" BackupTool class

$Editor: kfirsov $
$Id: BackupTool.py,v 1.8 2008/08/13 10:29:32 oevsegneev Exp $
"""
__version__ = '$Revision: 1.8 $'[11:-2]

import os
import re

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Globals import InitializeClass
from ZODB.FileStorage.FileStorage import FileStorageError


from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.NauScheduler.TemporalExpressions import UniformIntervalTE

from ActionInformation import ActionInformation as AI
from SimpleObjects import ToolBase


from zLOG import LOG, ERROR, INFO, WARNING

try:
    import repozo
except ImportError:
    BACKUP_POSSIBLE = False
    LOG( 'BackupTool', ERROR, 'Cannot import repozo. Backup operation will not be available.' )
else:
    BACKUP_POSSIBLE = True


#stanched from repozo
class RepozoOptions:
    mode = None         # BACKUP or RECOVER
    file = None         # name of input Data.fs file
    repository = None   # name of directory holding backups
    full = False        # True forces full backup
    date = None         # -D argument, if any
    output = None       # where to write recovered data; None = stdout
    quick = False       # -Q flag state
    gzip = False        # -z flag state

class PackOptions:
    interval = None #UniformIntervalTE instance
    #we suppose that we know nothing about
    #UniformIntervalTE' internal structure
    interval_seconds = 0

    days_older = 0


class BackupOptions:
    interval = None #UniformIntervalTE instance
    interval_seconds = 0
    copies = 0
    path = ''
    gzip = False


def timeTupleFromIntervalSeconds(seconds):
    mod = int( seconds )
    res = []
    for divisor in ( 60*60*24, 60*60, 60, 1 ):
        div, mod = divmod( mod, divisor )
        res.append(div)
    return tuple(res)


class BackupTool(ToolBase):
    """
        Backup FileStorage Tool.

        Provides a way to database backup and pack.
        Uses repozo.py to make backups of Data.fs
    """
    _class_version = 1.00

    meta_type = 'NauSite Backup Tool'
    id = 'portal_backup'
    
    __resource_type__ = 'item'

    security = ClassSecurityInfo()

    _actions = (
            AI( id='manageBackup'
              , title='Pack and backup'
              , description='Manage pack and backup options'
              , action=Expression( text='string: ${portal_url}/backup_config_form' )
              , permissions=[ CMFCorePermissions.ManagePortal ]
              , category='global'
              , visible=True
              ),
        )


    def __init__( self ):
        ToolBase.__init__( self )

        self._pack_task_id = None
        self._backup_task_id = None

        self._packOptions = PackOptions()
        self._backupOptions = BackupOptions()

        self._notified_members = []


    security.declareProtected(CMFCorePermissions.ManagePortal, 'getPackOptions')
    def getPackOptions(self):
        """
            Returns pack options.

            Result:

                Dictionary.
        """
        interval = self._packOptions.interval
        d, h, m, s = timeTupleFromIntervalSeconds( self._packOptions.interval_seconds )
        result = {  'nextEvent' : interval and interval.nextOccurence()
                  , 'days' : d
                  , 'hours': h
                  , 'minutes' : m
                  , 'seconds' : s
                  , 'days_older' : self._packOptions.days_older
                 }
        return result

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getBackupOptions')
    def getBackupOptions(self):
        """
            Return backup options.

            Result:

                Dictionary.
        """
        interval = self._backupOptions.interval
        d, h, m, s = timeTupleFromIntervalSeconds( self._backupOptions.interval_seconds )
        result = {  'nextEvent' : interval and interval.nextOccurence()
                  , 'days' : d
                  , 'hours': h
                  , 'minutes' : m
                  , 'seconds' : s
                  , 'path' : self._backupOptions.path
                  , 'copies' : self._backupOptions.copies
                  , 'gzip' : self._backupOptions.gzip
                 }
        return result


    security.declareProtected(CMFCorePermissions.ManagePortal, 'backup')
    def backup( self, REQUEST=None ):
        """
            Uses repozo.py to perform backup (incremental if available).
            Keeps self._backupOptions.copies copies of full backups.
        """
        if not BACKUP_POSSIBLE:
            LOG( 'BackupTool.backup:', ERROR, 'Cannot import repozo. Backup operation is not available.' )
            self.redirect(action='backup_config_form', message="Backup operation is not available", relative=False)
            return "Backup operation is not available"

        opts = RepozoOptions()
        opts.full = True
        opts.mode = repozo.BACKUP
        opts.file = self._p_jar.db().getName()
        opts.gzip = self._backupOptions.gzip
        opts.repository = self._backupOptions.path

        #XXX Test Me!!!
        try:
            res = repozo.do_backup(opts)
            LOG( 'BackupTool.backup:', INFO, 'Database has been backed up.' )

            #leave only self._backupOptions.copies of full backup copies
            good_fname_regexp = re.compile( r'^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}$' )

            all = os.listdir(self._backupOptions.path)
            all.sort()
            likely = []
            full = []
            for fname in all:
                root, ext = os.path.splitext(fname)
                if ext in ['.fs', '.fsz'] and good_fname_regexp.match(root):
                    full.append( fname )
                if ext in ['.fs', '.fsz', '.deltafs', '.deltafsz', '.dat'] and \
                   good_fname_regexp.match(root):
                    likely.append( fname )

            if len(full) > self._backupOptions.copies:
                deadline = os.path.splitext( full[-self._backupOptions.copies] )[0]
                for fname in likely:
                    root, ext = os.path.splitext(fname)
                    if root < deadline:
                        os.remove( os.path.join( self._backupOptions.path, fname ) )
        except Exception, error:
            self._sendNotify( except_text=error )
            raise
        else:
            self._sendNotify( 1 )

        self.redirect(action='backup_config_form', message="Database has been backed up.", relative=False)
        return "Database has been backed up."

    security.declareProtected(CMFCorePermissions.ManagePortal, 'pack')
    def pack(self, REQUEST=None):
        """
            Packs database. Remove old objects revisions.
        """
        packed = False
        cpl = getattr( self.getPhysicalRoot(), 'Control_Panel' )

        try:
            cpl.manage_pack( self._packOptions.days_older )
            self._sendNotify( 2 )
            packed = True
            LOG( 'BackupTool.pack:', INFO, 'Database have been packed.' )
        except FileStorageError:
            # already packed
            LOG( 'BackupTool.pack:', WARNING, 'Database have not been packed.' )
        else:
            # remove Data.fs.old
            try:
                os.remove(self._p_jar.db().getName()+'.old')
                LOG( 'BackupTool.pack:', INFO, 'File %s.old removed.' % self._p_jar.db().getName() )
            except OSError:
                LOG( 'BackupTool.pack:', WARNING, 'Error during file removal (%s.old).' % self._p_jar.db().getName() )

        result = packed and "Database has been packed." or "Database has not been packed"

        self.redirect( action='backup_config_form', message = result, relative=False )
        return result


    security.declareProtected(CMFCorePermissions.View, 'isPackTaskActive')
    def isPackTaskActive(self):
        """
            Returns state of pack task.

            Result:

                Boolean
        """
        return self._isTaskActive(task_id=self._pack_task_id)

    security.declareProtected(CMFCorePermissions.View, 'isBackupTaskActive')
    def isBackupTaskActive(self):
        """
            Returns state of backup task.

            Result:

                Boolean
        """
        return self._isTaskActive(task_id=self._backup_task_id)

    def _isTaskActive(self, task_id):
        #Checks state of the task in portal_scheduler.
        #
        #Arguments:
        #
        #   'task_id' -- identifier of the shedule element (task)
        #
        #Result:
        #
        #   Boolean
        if task_id is None:
            return False

        scheduler = getToolByName(self, 'portal_scheduler')
        try:
            element = scheduler.getScheduleElement(task_id)
        except TypeError:
            element = None
        return scheduler.checkDaemon() and element is not None


    def _instance_onDestroy( self ):
        #Deletes tasks in portal_scheduler.
        #This is improbable event, but anyway...

        scheduler = getToolByName(self, 'portal_scheduler')

        for task_id in (self._pack_task_id, self._backup_task_id):
            if task_id:
                try:
                    scheduler.delScheduleElement( task_id )
                except TypeError, AttributeError:
                    pass


    security.declareProtected(CMFCorePermissions.ManagePortal, 'getNotifiedMembers')
    def getNotifiedMembers( self ):
        """
            Getter for notified members.

            Result:

                List
        """
        return self._notified_members


    def _sendNotify( self, mode=None, except_text='' ):
        #Sends notifications to notified members.
        #
        #Arguments:
        #
        #   'mode' -- message mode. If mode==1, message about backup
        #             will be sent. If mode==2, message about pack
        #             will be sent. If mode is omitted, except_text must
        #             be given.
        #
        #   'except_text' -- Text that will be send to notified members
        #                    about exception raised during backup.

        msg = getToolByName( self, 'msg' )
        lang = msg.get_default_language()

        except_text = msg.gettext( except_text, lang = lang )
        self.MailHost.sendTemplate( template = 'backup_notify',
                                          mto = self._notified_members,
                                          lang = lang,
                                          except_text = except_text,
                                          mode = mode,
                                          date = DateTime().strftime( '%d.%m.%Y %H:%M' )
                                        )

    def _updateScheduledInterval(self, prefix, options, REQUEST):
        #Updates UniformInterval temporal expression stored in
        #options.interval and interval between events in seconds
        #stored in options.interval_seconds.
        #
        #Returns whether time interval was changed.
        #
        #Arguments:
        #
        #   'prefix' -- may be 'pack' or 'backup'. Displays what
        #               options we want to parse from REQUEST.
        #
        #   'options' -- self._packOptions or self._backupOptions
        #                instance according given prefix.
        #
        #   'REQUEST' -- HTTPRequest.
        #
        #Result:
        #
        #   Boolean

        assert prefix in ['pack', 'backup']
        next_date = REQUEST.get('%s_next_date' % prefix)

        interval_seconds = REQUEST.get('%s_interval_days' % prefix, 0) * 86400 + \
                                REQUEST.get('%s_interval_hours' % prefix, 0) * 3600 + \
                                REQUEST.get('%s_interval_minutes' % prefix, 0) * 60

        if prefix=='backup':
            testCopies = self._backupOptions.copies
        else:
            testCopies = True

        time_changed = False

        if next_date and interval_seconds and testCopies:
            temp_TE = UniformIntervalTE(seconds=interval_seconds, start_date=next_date)
            if not ( options.interval and \
                     interval_seconds == options.interval_seconds and \
                     temp_TE.start_date == options.interval.start_date ):
                options.interval = temp_TE
                options.interval_seconds = interval_seconds
                time_changed = True
        else:
            time_changed = True
            options.interval = None
            options.interval_seconds = 0

        return time_changed


    def _refreshScheduledTask(self, time_changed, task_id, options, method, task_title):
        #Refreshes, creates or destroys scheduled task.
        #
        #Arguments:
        #
        #   'time_changed' -- flag indicating that time event parameters
        #                     changed
        #
        #   'task_id' -- task id to check (self._pack_task_id or
        #                self._backup_task_id)
        #
        #   'options' -- self._packOptions or self._backupOptions
        #                instance
        #
        #   'method' -- method that task must call (self.pack or self.backup)
        #
        #   'task_title' -- title for sheduled task
        #
        #Result:
        #
        #   None or identifier of the created task.

        new_task_id = None
        scheduler = getToolByName(self, 'portal_scheduler')
        try:
            task = scheduler.getScheduleElement( task_id )
        except TypeError:
            task = None
        if task and options.interval is None:
            #remove task
            scheduler.delScheduleElement(task_id)
        if task and time_changed and options.interval:
            #change props
            task.setTemporalExpression( options.interval )
        if not task and options.interval:
            #create new one
            new_task_id = scheduler.addScheduleElement( method,
                                             temporal_expr=options.interval,
                                             title=task_title )
        return new_task_id


    #
    #   ZMI methods
    #
    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_reconfigure')
    def manage_reconfigure(self, REQUEST=None):
        """
            Parses data from REQUEST.
        """
        #XXX not thread safe
        self._packOptions.days_older = REQUEST.get('pack_days_older', 0)

        self._backupOptions.copies = REQUEST.get('backup_copies', 0)
        self._backupOptions.path = REQUEST.get('backup_path', '')
        self._backupOptions.gzip = bool( REQUEST.get('backup_gzip', 0) )
        self._notified_members = REQUEST.get('notified_members', [])

        pack_time_changed = self._updateScheduledInterval( 'pack', self._packOptions, REQUEST )

        new_pack_task_id = self._refreshScheduledTask(
                                   time_changed=pack_time_changed
                                 , task_id=self._pack_task_id
                                 , options=self._packOptions
                                 , method=self.pack
                                 , task_title='Pack Database')
        if new_pack_task_id:
            self._pack_task_id = new_pack_task_id


        backup_time_changed = self._updateScheduledInterval( 'backup', self._backupOptions, REQUEST )

        new_backup_task_id = self._refreshScheduledTask(
                                   time_changed=backup_time_changed
                                 , task_id=self._backup_task_id
                                 , options=self._backupOptions
                                 , method=self.backup
                                 , task_title='Backup Database')
        if new_backup_task_id:
            self._backup_task_id = new_backup_task_id


        self._p_changed = 1

        self.redirect(action = 'backup_config_form', message = "Settings have been changed", relative=False)


InitializeClass(BackupTool)

def initialize( context ):
    # module initialization callback
    context.registerTool( BackupTool )
