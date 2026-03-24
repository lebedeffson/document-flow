"""
Mail Folder classes.

$Editor: vpastukhov $
$Id: MailFolder.py,v 1.69 2005/11/30 17:13:27 ikuleshov Exp $
"""
__version__ = '$Revision: 1.69 $'[11:-2]

from types import ListType, TupleType

from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOSet
from Globals import HTMLFile
from ZODB.PersistentList import PersistentList
from zLOG import LOG, TRACE

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.NauScheduler.TemporalExpressions import UniformIntervalTE

import Config, Exceptions
from ActionInformation import ActionInformation as AI
from Config import Roles, Permissions
from Features import createFeature
from Heading import Heading, HeadingType
from HTMLDocument import HTMLDocument, HTMLDocumentType
from Mail import mailFromDocument, formatFromAddress
from MailFilter import MailFilter
from Monikers import Moniker
from SimpleObjects import OrderedContainerBase, ContentResource
from Utils import InitializeClass, cookId, getNextTitle, \
        getObjectByUid, joinpath, extractParams, inheritActions, isSequence


IncomingMailFolderType = {
        'id'                        : 'Incoming Mail Folder',
        'content_meta_type'         : 'Incoming Mail Folder',
        'title'                     : "Incoming Mail Folder",
        'description'               : "Folder for receiving e-mail messages.",
        'content_icon'              : 'folder_icon.gif',
        'sort_order'                : 0.31,
        'product'                   : 'CMFNauTools',
        'factory'                   : 'addIncomingMailFolder',
        'permissions'               : ( Permissions.UseMailServerServices, ),
        'filter_content_types'      : 1,
        'allowed_content_types'     : ( HTMLDocumentType['id'], HeadingType['id'] ),
        'allowed_categories'        : ['IncomingMail'],
        'inherit_categories'        : 0,
        'immediate_view'            : 'folder_edit_form',
        'actions'                   : inheritActions( HeadingType ),
    }

OutgoingMailFolderType = {
        'id'                        : 'Outgoing Mail Folder',
        'content_meta_type'         : 'Outgoing Mail Folder',
        'title'                     : "Outgoing Mail Folder",
        'description'               : "Folder for sending e-mail messages.",
        'content_icon'              : 'folder_icon.gif',
        'sort_order'                : 0.32,
        'product'                   : 'CMFNauTools',
        'factory'                   : 'addOutgoingMailFolder',
        'permissions'               : ( Permissions.UseMailHostServices, ),
        'filter_content_types'      : 1,
        'allowed_content_types'     : ( HTMLDocumentType['id'], HeadingType['id'] ),
        'allowed_categories'        : ['OutgoingMail'],
        'inherit_categories'        : 0,
        'immediate_view'            : 'folder_edit_form',
        'actions'                   : inheritActions( HeadingType ),
    }


class MailFolderBase( Heading ):
    """
        Base Mail Folder class
    """
    _class_version = 1.39

    meta_type = None
    portal_type = None

    __implements__ = createFeature('isMailFolder'), \
                     Heading.__implements__

    security = ClassSecurityInfo()

    def hasMainPage( self ):
        """ Mail folder has no main page
        """
        return 0

    def getMainPage( self ):
        """ Mail folder has no main page
        """
        return None

InitializeClass( MailFolderBase )


class IncomingMailFolder( MailFolderBase ):
    """
        Incoming Mail Folder class
    """
    _class_version = 1.42

    meta_type = 'Incoming Mail Folder'
    portal_type = 'Incoming Mail Folder'

#    __resource_type__ = 'inbox'

    __implements__ = createFeature('isIncomingMailFolder'), \
                     MailFolderBase.__implements__

    security = ClassSecurityInfo()

    _actions = MailFolderBase._actions + \
        (
            AI(
                id='check',
                title="Check mail",
                description="Receive incoming mail now",
                action=Expression( 'string: ${object_url}/mail_fetch' ),
                permissions=( Permissions.UseMailServerServices, ),
                category='folder',
                condition=Expression( 'python: object.mail_login' ),
                visible=1,
            ),
            AI(
                id='mail_filters',
                title="Configure mail filters",
                description="Configure mail message filters",
                action=Expression( 'string: ${object_url}/mail_filters_form' ),
                permissions=( Permissions.UseMailServerServices, ),
                category='folder',
                visible=1,
            ),
            AI(
                id='activate',
                title="Activate mail",
                description="Enable automatic mail check",
                action=Expression( 'string: ${object_url}/activate' ),
                permissions=( Permissions.UseMailServerServices, ),
                category='folder',
                condition=Expression( 'python: not object.mail_enabled' ),
                visible=1,
            ),
            AI(
                id='deactivate',
                title="Deactivate mail",
                description="Disable automatic mail check",
                action=Expression( 'string: ${object_url}/deactivate' ),
                permissions=( Permissions.UseMailServerServices, ),
                category='folder',
                condition=Expression( 'python: object.mail_enabled' ),
                visible=1,
            ),
        )

    _subitems = [ 'mail_filters' ]

    _properties = MailFolderBase._properties + (
            {'id':'mail_type',     'type':'string',  'mode':'w'},
            {'id':'mail_login',    'type':'string',  'mode':'w'},
            {'id':'mail_password', 'type':'string',  'mode':'w'},
            {'id':'mail_folder',   'type':'string',  'mode':'w'},
            {'id':'mail_keep',     'type':'boolean', 'mode':'w'},
            {'id':'mail_enabled',  'type':'boolean', 'mode':'w'},
            {'id':'mail_interval', 'type':'int',     'mode':'w'},
            {'id':'mail_category', 'type':'string',  'mode':'w'},
        )

    # default attribute values
    mail_type = 'pop'
    mail_login = None
    mail_keep = False
    mail_enabled = None
    mail_folder = Config.MailInboxName
    mail_interval = Config.MailDefaultInterval
    mail_category = Config.MailDefaultCategory
    mail_state = None
    mail_task = None

    def __init__( self, id, title=None, **kwargs ):
        # instance constructor
        MailFolderBase.__init__( self, id, title, **kwargs )
        self.mail_filters = MailFilterContainer( 'mail_filters' )

    def _initstate( self, mode ):
        # initializes attributes
        if not MailFolderBase._initstate( self, mode ):
            return 0

        if hasattr( self, 'mail_filter' ): # < 1.41
            self.mail_filters = MailFilterContainer( 'mail_filters' )
            flt = self._upgrade( 'mail_filter', MailFilter )
            if len(flt):
                flt._setId( 'senders' )
                flt.setTitle( "Allowed senders" )
                self.mail_filters.addObject( flt )
            del self.mail_filter

        if hasattr( self, 'mail_seen' ): # < 1.42
            self.mail_state = self.mail_seen
            del self.mail_seen

        return 1

    def getServer( self ):
        """
            Returns the nearest mail server object.

            Result:

                'MailServerBase' object.
        """
        protocol = self.mail_type
        if protocol == 'pop':
            return getToolByName( self, 'MailPOP', None )
        elif protocol == 'imap':
            return getToolByName( self, 'MailIMAP', None )

    def setServerType( self, id ):
        """
            Configures server type (IMAP4 or POP3).
        """
        if self.mail_type == id:
            return # nothing to do
        self.mail_type = id
        if self.mail_state is not None:
            del self.mail_state

    def setFolder( self, folder ):
        """
            Configures server folder from which fetch messages (for IMAP4 servers).
        """
        self.mail_folder = folder

    security.declareProtected( Permissions.UseMailServerServices, 'activate' )
    def activate( self, enable=True, REQUEST=None ):
        """
            Enables automatic mail delivery.
        """
        if not enable:
            return self.deactivate()

        server = self.getServer()
        if not server:
            raise Exceptions.SimpleError( 'mail.server_not_found' )

        scheduler = getToolByName( self, 'portal_scheduler', None )
        if scheduler:
            se = self.mail_task and scheduler.getScheduleElement( self.mail_task )
            if se is not None:
                se.resume()
            else:
                title = '%s://%s@%s' % (server.protocol.lower(), self.mail_login, server.address())
                temporal_expr = UniformIntervalTE( seconds=(self.mail_interval * 60) )
                self.mail_task = scheduler.addScheduleElement( self.fetchMail
                                                             , temporal_expr=temporal_expr
                                                             , title=title
                                                             )

        self.mail_enabled = True

        if REQUEST is not None:
            return self.redirect( message="New mail will be checked automatically.", REQUEST=REQUEST )

    security.declareProtected( Permissions.UseMailServerServices, 'deactivate' )
    def deactivate( self, suspend=True, REQUEST=None ):
        """
            Disables automatic mail retrieval.
        """
        scheduler = getToolByName( self, 'portal_scheduler', None )
        task = self.mail_task

        if scheduler and task:
            se = scheduler.getScheduleElement( task )
            if se is not None:
                if suspend:
                    se.suspend()
                else:
                    scheduler.delScheduleElement( task )

        self.mail_enabled = False

        if REQUEST is not None:
            return self.redirect( message="Mail will not be checked.", REQUEST=REQUEST )

    def setMailAccount( self, login=None, password=None, register=True ):
        """
            Changes mail account name and password.
        """
        server = self.getServer()
        if not server:
            register = 0

        if login is not None:
            login = str( login ).strip()
            old   = self.mail_login

            if login != old:
                self.mail_login = login
                if not login:
                    self.deactivate()
            else:
                register = 0

            if register:
                if old:   server.unregisterAccount( self, old )
                if login: server.registerAccount( self, login )

        if password is not None:
            self.mail_password = str( password )

    def setKeepMessages( self, value ):
        """
            Configures whether seen messages are deleted from the server.
        """
        self.mail_keep = int( value )

    def setInterval( self, value ):
        """
            Changes time interval for background mail checking.

            Sets new interval for periodic mail delivery and updates
            scheduler task frequency accordingly.  If specified interval
            is shorter than minimum interval allowed by the mail server,
            uses that minimum instead.

            Arguments:

                'value' -- integer interval in minutes
        """
        value = int( value )
        server = self.getServer()
        scheduler = getToolByName( self, 'portal_scheduler', None )

        # check against server's minimum interval
        if server:
            minvalue = server.getProperty('min_interval')
            if minvalue and value < minvalue:
                value = minvalue

        self.mail_interval = value

        # update task frequency to the new interval
        if scheduler and self.mail_task:
            se = scheduler.getScheduleElement( self.mail_task )
            if se is None:
                return
            interval = value * 60
            temporal_expr = UniformIntervalTE( seconds=interval )
            se.setTemporalExpression( temporal_expr )

    def addFilter( self, id=None, title=None, position=None, action=None ):
        """
        """
        filters = self.mail_filters
        id = cookId( filters, id, prefix='filter', title=title )

        if not title:
            titles = [ f.Title() for f in self.listFilters() ]
            msgcat = getToolByName( self, 'msg' )
            title = getNextTitle( msgcat.gettext( "Filter" ), titles )

        if position is None:
            position = -1

        flt = filters.addObject( MailFilter( id, title ), position=position )
        flt.setAction( action )

        return id

    def deleteFilter( self, id ):
        """
        """
        self.mail_filters.deleteObjects( id )

    def moveFilter( self, id, position=None, offset=None, before=None ):
        """
        """
        if before is not None:
            ids = self.mail_filters.objectIds()
            try:
                position = ids.index( before )
            except ValueError:
                raise KeyError, before

        self.mail_filters._moveObject( id, position, offset )

    def getFilter( self, id, default=Missing ):
        """
        """
        try:
            return self.mail_filters[ id ]
        except KeyError:
            if default is Missing:
                raise
            return default

    def listFilters( self ):
        """
        """
        return self.mail_filters.objectValues()

    def getActionInfo( self, id ):
        """
        """
        return getToolByName( self, 'portal_actions' ).getActionInfo( id )

    def listAvailableActions( self ):
        """
        """
        return getToolByName( self, 'portal_actions' ).listActionsByCategory( 'mail_filter' )

    security.declareProtected( Permissions.UseMailServerServices, 'testServer' )
    def testServer( self, raise_exc=True ):
        """
            Checks connectivity against the POP3 server.

            The test is unsuccessful if connection is not configured,
            server cannot be reached or does not accept login creadentials,
            or another error occurs.

            Arguments:

                'raise_exc' -- boolean flag, whether to raise an exception
                               (default), otherwise return boolean result

            Result:

                Boolean, true if connection is OK.
        """
        server = self.getServer()
        if not server:
            if raise_exc:
                raise Exceptions.SimpleError( 'mail.server_not_found' )
            return False

        try:
            server.open( self.mail_login, self.mail_password )
        except Exception, exc:
            if raise_exc:
                raise Exceptions.SimpleError( exc=exc )
            return False
        else:
            server.close()

        return True

    security.declareProtected( Permissions.UseMailServerServices, 'fetchMail' )
    def fetchMail( self ):
        """
            Fetches new mail messages from the POP3 server.
        """
        #LOG( 'MailFolder.fetchMail', TRACE, '%s started' % self.getId() )

        server = self.getServer()
        if not server:
            raise Exceptions.SimpleError( 'mail.server_not_found' )

        actions = getToolByName( self, 'portal_actions' )
        default_action = actions.getActionInfo( 'mail_filter_default' )

        editor  = self.getEditor()
        filters = self.mail_filters.objectValues()
        count   = 0

        server.open( self.mail_login, self.mail_password, state=self.mail_state )
        try:
            if self.mail_state is None:
                self.mail_state = server.getState()

            server.openFolder( self.mail_folder )

            if not self.mail_keep:
                server.deleteMessages( old=True )

            for msg in server.fetchMessages( mark=False ):
                for mfilter in filters:
                    if mfilter.match( msg ):
                        action = mfilter.getAction().getActionHandler()
                        break
                else:
                    action = default_action.getHandler()

                attempts = 3
                while attempts > 0:
                    attempts -= 1

                    try:
                        server.setFlags( msg.uid, seen=True )
                        action.perform( folder=self, message=msg, creator=editor )

                        get_transaction().commit()
                        attempts = -1

                    except Exceptions.ConflictError:
                        # the message may have been handled by the concurrent thread
                        if server.getFlags( msg.uid, 'seen' ):
                            attempts = 0

                #LOG( 'MailFolder.fetchMail', TRACE, 'added document %s uid=%s' % (doc_id, doc_ob.getUid()) )

                if attempts < 0:
                    count += 1
                    if not self.mail_keep:
                        server.deleteMessages( msg.uid )

                #try: self.announce_publication( doc_id )
                #except: pass

        finally:
            server.close()

        #LOG( 'MailFolder.fetchMail', TRACE, '%s finished, %d' % (self.getId(), count) )
        return count

    def _instance_onCreate( self ):
        # configures initial credentials
        #
        server = self.getServer()
        membership = getToolByName( self, 'portal_membership' )

        # try to guess mail login name from creator's properties
        member = not membership.isAnonymousUser() and membership.getAuthenticatedMember()
        if member:
            addr = member.getMemberEmail()
            if addr:
                login = addr.split( '@', 1 )[0]
            else:
                login = member.getUserName()

            if server and server.isAccountRegistered( login ):
                login = ''
        else:
            login = ''

        # defer registration till _containment_onAdd
        self.setMailAccount( login, '', register=False )

    def _instance_onClone( self, source, item ):
        # clears settings of the new object
        #
        self.setMailAccount( '', '', register=False )
        self.mail_enabled = False
        self.mail_task = None

    def _instance_onDestroy( self ):
        # removes scheduler task
        #
        self.deactivate( suspend=False )
        self.mail_filters.manage_beforeDelete( self, self )

    def _containment_onAdd( self, item, container ):
        # registers account and configures task
        #
        server    = self.getServer()
        scheduler = getToolByName( self, 'portal_scheduler', None )

        if server:
            # check interval against server's minimal interval
            self.setInterval( self.mail_interval )

            # clear or register mail account
            login = self.mail_login
            if login:
                if server.isAccountRegistered( login ):
                    self.setMailAccount( '', '', register=False )
                else:
                    server.registerAccount( self, login )
        else:
            # no server is available -- disable task
            self.deactivate()

    def _containment_onDelete( self, item, container ):
        # unregisters mail account
        #
        server = self.getServer()
        login  = self.mail_login

        if login and server:
            server.unregisterAccount( self, self.mail_login )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'manage_changeProperties' )
    def manage_changeProperties( self, REQUEST=None, **kw ):
        """
            Changes existing object properties.
        """
        login, password, server_type, folder, enabled, interval, category = \
                extractParams( kw, REQUEST, 'mail_login', 'mail_password', 'mail_type',
                               'mail_folder', 'mail_enabled', 'mail_interval', 'mail_category' )

        if server_type is not None:
            self.setServerType( server_type )

        if login is not None:
            self.setMailAccount( login, password )

        if folder is not None:
            self.setFolder( folder )

        if interval is not None:
            if interval:
                self.setInterval( int(interval) )
            else:
                self.deactivate()

        if category is None:
            category = self.mail_category

        if self.isCategoryAllowed( category ):
            kw['mail_category'] = category
        else:
            raise Exceptions.SimpleError( 'mail.incoming_category_not_allowed',
                                          category=category, folder=Moniker(self) )

        res = MailFolderBase.manage_changeProperties( self, REQUEST and {}, **kw )

        if enabled is None and self.mail_enabled is None and self.mail_login:
            enabled = True

        if enabled is not None:
            self.activate( not not enabled )

        return res

    def filtered_meta_types( self, user=None ):
        """ Disallow interactive item creation
        """
        return ()

    def cb_dataValid( self ):
        """ Disallow paste into self
        """
        return 0

    def _verifyObjectPaste( self, object, validate_src=True ):
        """ Disallow paste into self
        """
        raise Exceptions.CopyError # TODO

InitializeClass( IncomingMailFolder )


class MailFilterContainer( OrderedContainerBase ):
    """
        Container for MailFilter objects.
    """
    meta_type = 'Mail Filter Container'

InitializeClass( MailFilterContainer )


class IncomingMailFolderResource( ContentResource ):

    id = 'inbox'
    keys = []

    def identify( portal, object ):
        filter = None
        if object.implements('isActionDefinition'):
            object = object.parent()
        if object.implements('isMailFilter'):
            filter = object
            object = filter.parent().parent()
        if not object.implements('isIncomingMailFolder'):
            raise TypeError, object
        uid = ContentResource.identify.im_func( portal, object )
        if filter:
            uid['filter'] = filter.getId()
        return uid

    def lookup( portal, filter=None, **kwargs ):
        object = ContentResource.lookup.im_func( portal, **kwargs )
        if filter:
            object = object.getFilter( filter )
        return object


def addIncomingMailFolder( self, id, title='', REQUEST=None, **kwargs ):
    """
        IncomingMailFolder factory.
    """
    self._setObject( id, IncomingMailFolder( id, title, **kwargs ) )

    if REQUEST is not None:
        return self[ id ].redirect( message="Incoming e-mail folder added.",
                                    action='folder_edit_form', REQUEST=REQUEST )


class OutgoingMailFolder( MailFolderBase ):
    """
        Outgoing Mail Folder class
    """
    _class_version = 1.39

    meta_type = 'Outgoing Mail Folder'
    portal_type = 'Outgoing Mail Folder'

    __implements__ = createFeature('isOutgoingMailFolder'), \
                     MailFolderBase.__implements__

    security = ClassSecurityInfo()

    mail_notify = HTMLFile( 'skins/mail_templates/mail_notify', globals() )

    _actions = (
            AI(
                id='send',
                title='Send mail',
                description='Send queued mail',
                action=Expression( 'string: ${object_url}/confirm_dispatch' ),
                permissions=( Permissions.UseMailHostServices, ),
                category='folder',
                #condition=Expression( 'python: object.mail_login' ),
                visible=1,
            ),
        )

    _properties = MailFolderBase._properties + (
            {'id':'mail_from_name',     'type':'string',        'mode':'w'},
            {'id':'mail_from_address',  'type':'string',        'mode':'w'},
        )

    # default attribute values
    mail_from_name    = None
    mail_from_address = None
    mail_category     = 'OutgoingMail'

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not MailFolderBase._initstate( self, mode ):
            return 0

        if getattr( self, 'mail_recipients', None ) is None:
            self.mail_recipients = OOSet()

        return 1

    def setFromAddress( self, email=None, name=None, register=True ):
        """ Set e-mail address for the From header
        """
        server = getToolByName( self, 'MailHost', None )
        if not server:
            register = 0

        if name is not None:
            self.mail_from_name = str( name ).strip()

        if email is not None:
            email = str( email ).strip()
            old   = self.mail_from_address

            if email != old:
                self.mail_from_address = email
            else:
                register = 0

            if register:
                if old:   server.unregisterAccount( self, old )
                if email: server.registerAccount( self, email )

    def getRecipients( self ):
        """ Get list of recipients e-mail addresses
        """
        return self.mail_recipients

    def setRecipients( self, *addrs ):
        """ Set list of recipients e-mail addresses
        """
        self.mail_recipients.clear()
        if addrs:
            self.mail_recipients.update( addrs )

    security.declareProtected( Permissions.UseMailHostServices, 'sendMail' )
    def sendMail( self, uids=None ):
        """ Send mail messages through the smtp server
        """
        server = getToolByName( self, 'MailHost' )
        mstool = getToolByName( self, 'portal_membership' )
        wftool = getToolByName( self, 'portal_workflow' )

        # TODO: must use language from user prefs
        try:
            lang = self.msg.get_selected_language()
        except AttributeError:
            lang = self.msg.get_default_language()

        internal_emails = []
        external_emails = []

        for addr in self.mail_recipients:
            member = addr.find('@') < 0 and mstool.getMemberById( addr ) or None
            if member:
                internal_emails.append( member )
            else:
                external_emails.append( addr )

        mfrom = self.mail_from_address
        queue = self.listQueued( uids=uids )
        count = 0

        server.open()
        try:
            for item in queue:
                doc = item.getObject()

                try:    wftool.doActionFor( doc, 'deliver' )
                except: continue

                internal = []
                external = []

                rcpts = doc.getCategoryAttribute( 'recipientAddress' )
                #names = doc.getCategoryAttribute( 'recipientName' ) TODO: set To header

                if rcpts:
                    for addr in rcpts.replace( ',', ' ' ).split():
                        member = addr.find('@') < 0 and mstool.getMemberById( addr ) or None
                        if member:
                            internal.append( member )
                        else:
                            external.append( addr )

                if not (internal or external):
                    if not (internal_emails or external_emails):
                        try:    wftool.doActionFor( doc, 'fail', comment='No recipients specified.' )
                        except: pass
                        continue

                    internal = internal_emails
                    external = external_emails

                res = 0

                if internal:
                    text = self.mail_notify( doc, message=doc, parent=self, lang=lang )
                    msg  = server.createMessage( source=text )
                    formatFromAddress( doc, msg, self.mail_from_name, self.mail_from_address )
                    res += server.send( msg, internal, mfrom, raise_exc=False )

                if external:
                    msg  = mailFromDocument( doc, factory=server.createMessage )
                    formatFromAddress( doc, msg, self.mail_from_name, self.mail_from_address )
                    res += server.send( msg, external, mfrom, raise_exc=False )

                try:    wftool.doActionFor( doc, res and 'fix' or 'fail' )
                except: pass

                count += res and 1 or 0

        finally:
            server.close()

        return count, len(queue)-count

    security.declareProtected( Permissions.UseMailHostServices, 'listQueued' )
    def listQueued( self, ids=None, uids=None, container=None ):
        """ Search catalog for queued messages
        """
        if container is None:
            container = self

        elif not self.isParentOf( container, distant=True, identic=True ):
            raise RuntimeError, "container is not a subfolder"

        catalog = getToolByName( self, 'portal_catalog' )
        query   = {
                    'implements'   : {
                        'query'    : ['isPortalContent','isDocument','isCategorial'],
                        'operator' : 'and' },
                    'hasBase'      : self.mail_category,
                  }

        if ids is not None:
            assert isSequence(ids), "ids must be a list of identifiers"
            query['id'] = ids
            query['parent_path'] = container.physical_path()
        else:
            query['path'] = self.physical_path()

        if uids is not None:
            assert isSequence(uids), "uids must be a list of identifiers"
            query['nd_uid'] = uids

        if ids is uids is None:
            query['state'] = ['pending','queued']
        else:
            query['state'] = ['pending','queued','failed']

        return catalog.searchResults( **query )

    def manage_afterAdd( self, item, container ):
        """ Actions to be executed after the object is created
        """
        MailFolderBase.manage_afterAdd( self, item, container )

        mstool = getToolByName( self, 'portal_membership' )
        member = mstool.getAuthenticatedMember()
        email  = member.getMemberEmail()

        server = getToolByName( self, 'MailHost', None )
        if server and server.isAccountRegistered( email ):
            email = ''

        self.setFromAddress( email, member.getMemberName() )

    def manage_beforeDelete( self, item, container ):
        """ Actions to be executed before the object is deleted
        """
        if self.mail_from_address:
            server = getToolByName( self, 'MailHost', None )
            if server:
                server.unregisterAccount( self, self.mail_from_address )

        MailFolderBase.manage_beforeDelete( self, item, container )

    security.declareProtected( CMFCorePermissions.ManageProperties, 'manage_changeProperties' )
    def manage_changeProperties( self, REQUEST=None, **kw ):
        """ Change existing object properties
        """
        from_name, from_addr, recipients = \
                extractParams( kw, REQUEST, 'mail_from_name',
                               'mail_from_address', 'mail_recipients' )

        if not (from_name is None and from_addr is None):
            self.setFromAddress( from_addr, from_name )

        if recipients is not None:
            self.setRecipients( *recipients )

        return MailFolderBase.manage_changeProperties( self, REQUEST and {}, **kw )

    def _getCopy( self, container ):
        """ Copy operation support
        """
        new = MailFolderBase._getCopy( self, container )

        new.setFromAddress( '' )

        return new

InitializeClass( OutgoingMailFolder )


def addOutgoingMailFolder( self, id, title='', REQUEST=None, **kwargs ):
    """
        OutgoingMailFolder factory.
    """
    self._setObject( id, OutgoingMailFolder( id, title, **kwargs ) )

    if REQUEST is not None:
        return self[ id ].redirect( message="Outgoing e-mail folder added.",
                                    action='folder_edit_form', REQUEST=REQUEST )


def initialize( context ):
    # module initialization callback

    #context.registerResource( 'inbox', IncomingMailFolderResource, moniker='content' )

    context.registerContent( IncomingMailFolder, addIncomingMailFolder, IncomingMailFolderType )
    context.registerContent( OutgoingMailFolder, addOutgoingMailFolder, OutgoingMailFolderType )
