"""
MailSMTP -- client class for communication with SMTP servers

SMTP -- subclassed from smtplib.py's SMTP if it does not support 'login' method.

$Editor: vpastukhov $
$Id: MailSMTP.py,v 1.36 2005/12/13 12:20:37 ikuleshov Exp $
"""
__version__ = '$Revision: 1.36 $'[11:-2]

import base64
from email.Utils import formatdate, make_msgid, parseaddr, getaddresses
from smtplib import SMTP, SMTPException, SMTPResponseException, \
        SMTPSenderRefused, SMTPRecipientsRefused
from sys import exc_info
from types import StringType

import transaction
from Acquisition import aq_base, aq_parent
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from AccessControl.SecurityManagement import getSecurityManager
from Globals import get_request
from DocumentTemplate import HTMLFile
from zLOG import LOG, TRACE, INFO, ERROR

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _checkPermission

from Products.MailHost.MailHost import MailHost

import Config, Exceptions
from Config import Permissions
from Exceptions import SimpleError
from Mail import MailServerBase, MailMessage
from MemberDataTool import MemberData
from Utils import InitializeClass, flattenString, uniqueValues

class TransEmailManager:

    smtp = None
    _transaction_done = False
    subtransaction = False
 
    def __init__(self, host, port):
        self.host = host
        self.port = port

        # think about later connect
        self.smtp = SMTP( host, port )
      
        self.queue = []
 
        transaction.get().register( self )

    def __getattr__(self, name):
        return getattr( self.smtp, name)

    def __del__(self):
        try:
            if self.smtp:
                self.smtp.quit()
        except SMTPException:
            LOG( 'MailSMTP', ERROR,
                 '[%s] disconnect error' % self.address(), error=exc_info() )

    def address(self):
        if not self.host or self.port == MailSMTP.default_port:
            return self.host

        return '%s:%s' % (self.host, self.port)

    # SMTP changed methods
    def sendmail(self, *args, **kwargs ):
        self.queue.append( ( args, kwargs ) )
        return {} # no errors returns

    def quit(self):
        # do not quit here
        pass
    
    #######################################################
    # ZODB Transaction hooks
    #######################################################

    def commit(self, reallyme, t): 
        """ Called for every (sub-)transaction commit """
        pass

    def tpc_begin(self, transaction, subtransaction=False): 
        """ Called at the beginning of a transaction
            N.B. subtransaction argument is removed in ZODB 3.4
        """
        self.subtransaction = bool(subtransaction)

    def tpc_abort(self, transaction): 
        """ Called on abort - but not always :( """
        pass

    def abort(self, reallyme, t): 
        """ Called if the transaction has been aborted """
        self.queue[:] = []

    def tpc_vote(self, transaction):
        """ Only called for real transactions, not subtransactions """
        self._transaction_done = True

    def tpc_finish(self, transaction):
        """ Called at the end of a successful transaction """
        if self.subtransaction or not self._transaction_done:
            # finished the subtransaction
            # or transaction finished without tpc_vote (this shouldn't happen)
            # do nothing in this case
            return

        smtp_server = self.smtp
        queue = self.queue
        while queue:
            args, kwargs = queue.pop()

            errors = None
            # only log smtp errors
            try:
                errors = smtp_server.sendmail( *args, **kwargs )
            except SMTPSenderRefused, exc:
                LOG( 'MailSMTP', ERROR, '[%s] SMTP sender address <%s> refused' % (self.address(), exc.sender) )
                #raise MailSMTPError( 'mail.smtp_sender_refused', exc=exc )

            except SMTPRecipientsRefused, exc:
                #LOG( 'MailSMTP', ERROR, '[%s] SMTP recipients addresses <%s> refused' % self.address(), exc.recipients )
                errors = exc.recipients

            except SMTPException, exc:
                LOG( 'MailSMTP', ERROR, '[%s] SMTP sending error:' % self.address(), error=exc_info() )
                #raise MailSMTPError( 'mail.smtp_delivery_error', exc=exc )

            if errors:
                LOG( 'MailSMTP', ERROR, '[%s] SMTP errors during send:' % self.address() )
                for addr, error in errors.items():
                    LOG( 'MailSMTP', ERROR, '<%s> - %s %s' % (addr, error[0], error[1]) )
                #count -= len(errors)

        self._transaction_done = False

    def sortKey(self, *ignored):
        """ The sortKey method is used for recent ZODB compatibility which
            needs to have a known commit order for lock acquisition.
            I don't care about commit order, so return the constant 1
        """
        return 1

class CleanUp:
    pass

class MailSMTP( MailServerBase, MailHost ):
    """
        SMTP mail service class.

        Surpasses 'MailHost' product, which it is based on and retains
        compatibility with.
    """
    _class_version = 1.34

    meta_type = 'Mail SMTP'

    security = ClassSecurityInfo()

    if Config.EnableDeferredSendMail:
        SMTPFactory = TransEmailManager
    else:
        SMTPFactory = SMTP

    protocol = 'smtp'
    default_port = 25

    _login = None
    _password = None

    def _connect( self ):
        # opens connection to the server
        self._v_conn = self.SMTPFactory( self.host, self.port )

    def _disconnect( self ):
        # closes connection to the server
        self._v_conn.quit()

    def open( self, login=Missing, password=Missing ):
        MailServerBase.open( self )

        if login is Missing:
            login = self.login()
        if not login:
            return

        if password is Missing:
            password = self.password() or ''

        try:
            self._v_conn.login( login, password )

        except SMTPException, exc:
            LOG( 'MailSMTP', ERROR, '[%s] unable to login as "%s"' % (self.address(), login), error=exc_info() )
            raise MailSMTPError( 'mail.smtp_cannot_login', login=login, exc=exc )

    def close( self ):
        REQUEST = get_request()
        for obj in REQUEST._held:
            if isinstance( obj, CleanUp):
                # do not hold CleanUp second time
                return

        #print "close"
        clean = CleanUp()
        clean.__del__ = lambda mailhost=self: MailServerBase.close( mailhost )
        REQUEST._hold( clean )

    security.declareProtected( ZopePermissions.change_configuration, 'login' )
    def login( self ):
        """
            Returns login to SMTP server required
            authentication.
        """
        return self._login

    security.declareProtected( ZopePermissions.change_configuration, 'password' )
    def password( self ):
        """
            Returns password to SMTP server required
            authentication.
        """
        return self._password

    security.declareProtected( ZopePermissions.change_configuration, 'setCredentials' )
    def setCredentials( self, login=Missing, password=Missing ):
        """
            Set login and password for SMTP server requiring
            authentication.

            Arguments:

                'login' -- optional SMTP username, string

                'password' -- optional SMTP password, string
        """
        if login is not Missing:
            self._login = login
        if password is not Missing:
            self._password = password

    security.declarePublic( 'sendTemplate' )
    def sendTemplate( self, template, mto=None, mfrom=None, subject=None, \
                      from_member=None, raise_exc=Missing, \
                      namespace=None, lang=None, restricted=True, REQUEST=None, **kw ):
        """
            Creates a new message from a DTML template and sends it through
            the SMTP server.

            This method renders DTML document or method and sends result
            by SMTP as an e-mail message.  The template to send can be
            specified as the object itself, or by its identifier, which
            is used as a key for lookup in the 'Mail' skin of the portal.
            In both cases, the current user must have *Reply to item* access
            right on the template object, otherwise an exception is raised.

            The template receives current acquisition context as the client
            object, 'namespace' argument or request as DTML namespace, with
            additional keyword arguments put on top of the namespace, along
            with the language code as 'lang' variable.

            Positional arguments:

                'template' -- document template object or identifier string

                'mto', 'mfrom', 'subject' -- see 'send' method description

            Keyword arguments:

                'from_member' -- see 'send' method description

                'raise_exc' -- if true, ignore delivery errors; DTML errors
                        are raised nonetheless

                'namespace' -- mapping object that represents DTML namespace

                'lang' -- language code passed to the template; if omitted,
                        default language of the portal is used

                'restricted' --

                'REQUEST' -- optional Zope request object; if 'namespace'
                        argument is omitted, request is used instead

                '**kw' -- additional variables to pass to the template

            Result:

                See 'send' method description.

            Exceptions:

                'Unauthorized' -- the current user has insufficient
                        rights to send the template

            Note:

                This method is declared public so that it can be used
                by objects on the external sites.
        """
        context = aq_parent( self )
        restricted = restricted is not Trust

        if callable( template ):
            if isinstance( template, HTMLFile ):
                id = template.name()
            else:
                id = template.getId()

        else:
            id = template
            skins = getToolByName( context, 'portal_skins' )
            try:
                template = getattr( skins.getSkinByName('Mail'), id )
            except ( AttributeError, KeyError ):
                raise KeyError, id
            # XXX move this to skins tool
            template = aq_base( template ).__of__( context )

        if restricted and not _checkPermission( CMFCorePermissions.ReplyToItem, template ):
            raise Exceptions.Unauthorized, id

        # XXX must use language from recipients' settings
        lang = lang or getToolByName( self, 'msg' ).get_default_language()

        template = template( context, namespace or REQUEST, lang=lang, **kw )
        msg = self.createMessage( source=template )

        return self.send( msg, mto, mfrom, subject, from_member=from_member, raise_exc=raise_exc )

    def send( self, msg, mto=None, mfrom=None, subject=None, encode=None, \
              from_member=None, raise_exc=Missing ):
        """
            Sends a message through the SMTP server.

            The message to send can be either an object or a string.
            In the latter case, the string is directly passed to the
            'MailHost' product along with other arguments for compatibility.
            The connection to the server is opened automatically.

            Both sender and recipients may be specified either as e-mail
            addresses or portal user names.

            If sender address is not given, the message in sent on behalf
            of either portal administrative address or the current user
            depending on 'from_member' argument.

            If recipients list is omitted, the list of addresses is
            extracted from all of 'To', 'CC', 'BCC', 'Resent-To' and
            'Resent-CC' fields of the message.

            Additionally 'Date', 'Message-Id' and 'X-Mailer' fields in
            the header are set before delivery, and 'BCC' field is removed
            for security.

            Positional arguments:

                'msg' -- 'MailMessage' object or a string

                'mto' -- optional list of recipients

                'mfrom' -- optional address of the message originator

                'subject' -- optional message subject; overrides
                        one in the message

                'encode' -- only for compatibility with 'MailHost' product

            Keyword arguments:

                'from_member' -- boolean value, determines whether
                        administrative address (by default) or address
                        of the current user (if value is true) is used
                        as the message source if 'mfrom' argument is omitted

                'raise_exc' -- if true, delivery errors are ignored

            Result:

                Number of successful recipient addresses.
        """
        count = 0
        send_errors = {}
        raise_exc = raise_exc or raise_exc is Missing

        if not self.address():
            return count

        try:
            if not isinstance( msg, MailMessage ):
                count = MailHost.send( self, msg, mto, mfrom, subject, encode )
                self.close()
                return count

            if subject is not None:
                msg.set_header( 'subject', flattenString(subject) )

            if 'date' not in msg:
                msg.set_header( 'date', formatdate( None, 1 ) )

            if 'message-id' not in msg:
                msg.set_header( 'message-id', make_msgid() )

            if 'x-mailer' not in msg:
                msg.set_header( 'x-mailer', '%s v%s' % (Config.MailerName, self._class_version) )

            prptool = getToolByName( self, 'portal_properties', None )
            mbstool = getToolByName( self, 'portal_membership', None )
            member = mname = None

            if not mfrom:
                if from_member and mbstool and not mbstool.isAnonymousUser():
                    member = mbstool.getAuthenticatedMember()

                elif 'from' in msg:
                    mfrom = parseaddr( msg.get( 'from', decode=1 ) )[1]
                    if not mfrom and prptool:
                        mfrom = prptool.getProperty( 'email_from_address' )

                elif prptool:
                    mname = prptool.getProperty( 'email_from_name' )
                    mfrom = prptool.getProperty( 'email_from_address' )

            else:
                if type(mfrom) is StringType:
                    if mbstool and mfrom.find('@') < 0:
                        member = mbstool.getMemberById( mfrom )

                elif isinstance( mfrom, MemberData ):
                    member = mfrom

            if member:
                mname = member.getMemberName()
                mfrom = member.getMemberEmail()

            if not mfrom:
                mfrom = getSecurityManager().getUser().getUserName()

            if 'from' not in msg:
                msg.set_header( 'from', (mname, mfrom) )

            list_to = None

            if mto is None:
                mdict = {}
                for header in ( 'to', 'cc', 'bcc', 'resent-to', 'resent-cc' ):
                    for mname, email in getaddresses( msg.get_all( header ) ):
                        if email:
                            mdict[ email ] = header
                mto = mdict.keys()

            elif 'to' in msg:
                list_to = []

            if 'bcc' in msg:
                msg.remove_header( 'bcc' )

            mto = mbstool.listPlainUsers( mto )
            mto = uniqueValues( mto )

            for item in mto:
                if not item:
                    continue
                member = None

                if type(item) is StringType:
                    if mbstool and item.find('@') < 0:
                        member = mbstool.getMemberById( item )

                elif isinstance( item, MemberData ):
                    member = item

                if member:
                    mname = member.getMemberName()
                    email = member.getMemberEmail()
                else:
                    mname = None
                    email = str( item )

                if not email:
                    LOG( 'MailSMTP', ERROR, 'no e-mail address found for user "%s"' % item )
                    continue

                if list_to is None:
                    msg.set_header( 'to', (mname, email) )
                    (sent, errors) = self._send( mfrom, [email], msg )
                    count += sent
                    if errors:
                        send_errors.update( errors )
                else:
                    list_to.append( email )

            if list_to:
                (sent, errors) = self._send( mfrom, list_to, msg )
                count += sent
                if errors:
                    send_errors.update( errors )

            self.close()

            if send_errors:
                raise MailSMTPError( 'mail.smtp_recipients_refused', errors=send_errors )

        except:
            if raise_exc:
                raise

        return count

    def _send( self, *args ):
        # send the message (overrides MailHost method)
        if not self._v_conn:
            self.open()

        if len(args) == 2: # Zope 2.5
            mfrom, mto = args[0]['from'], args[0]['to']
        else:
            mfrom, mto = args[0:2]

        body = args[-1]
        if isinstance( body, MailMessage ):
            body = body.as_string()

        #LOG( 'MailSMTP', TRACE, 'sending mail:\n%s => %s\n%s' % (mfrom, str(mto), body) )

        options = []
        count   = len(mto)
        errors  = None

        # TODO set 8bitmime only if necessary (from C-T-E)
        if self._v_conn.has_extn( '8bitmime' ):
            options.append( 'body=8bitmime' )

        try:
            errors = self._v_conn.sendmail( mfrom, mto, body, options )

        except SMTPSenderRefused, exc:
            LOG( 'MailSMTP', ERROR, '[%s] SMTP sender address <%s> refused' % (self.address(), exc.sender) )
            raise MailSMTPError( 'mail.smtp_sender_refused', exc=exc )

        except SMTPRecipientsRefused, exc:
            errors = exc.recipients

        except SMTPException, exc:
            LOG( 'MailSMTP', ERROR, '[%s] SMTP sending error:' % self.address(), error=exc_info() )
            raise MailSMTPError( 'mail.smtp_delivery_error', exc=exc )

        if errors:
            LOG( 'MailSMTP', ERROR, '[%s] SMTP errors during send:' % self.address() )
            for addr, error in errors.items():
                LOG( 'MailSMTP', ERROR, '<%s> - %s %s' % (addr, error[0], error[1]) )
            count -= len(errors)

        #self._v_conn.rset()

        return (count, errors)

    security.declareProtected( Permissions.UseMailHostServices, 'createMessage' )
    def createMessage( self, *args, **kw ):
        """
            Creates a new mail message instance with character set
            conversion from portal to e-mail encoding.

            Arguments:

                '*args', '**kw' -- arguments for the 'MailMessage'
                        constructor

            Result:

                'MailMessage' object.
        """
        if not kw.has_key('charset'):
            kw['charset'] = self.getOutputCharset()
        kw['to_mail'] = 1
        return MailServerBase.createMessage( self, *args, **kw )

InitializeClass( MailSMTP )

def manage_addMailSMTP( self, id='MailHost', title='', host=None, port=None, REQUEST=None ):
    """
        Creates a new MailSMTP instance and adds it into the container
    """
    self._setObject( id, MailSMTP( id, title, host, port ) )

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect( REQUEST.URL1 )

class MailSMTPError( SimpleError ):

    def __init__( self, *args, **kwargs ):
        SimpleError.__init__( self, *args, **kwargs )

        prec = self.precedent
        kwargs = self.kwargs

        if isinstance( prec, SMTPResponseException ):
            kwargs.setdefault( 'code', prec.smtp_code )
            kwargs.setdefault( 'error', prec.smtp_error )
            if isinstance( prec, SMTPSenderRefused ):
                kwargs.setdefault( 'sender', prec.sender )

        elif isinstance( prec, SMTPRecipientsRefused ):
            kwargs.setdefault( 'errors', prec.recipients )

        elif isinstance( prec, SMTPException ):
            kwargs.setdefault( 'error', str(prec) )

        kwargs.setdefault( 'code', '' )
        kwargs.setdefault( 'error', '' )
        kwargs.setdefault( 'response', str(kwargs['code'])+' '+kwargs['error'] )

        kwargs.setdefault( 'sender', '' )
        kwargs.setdefault( 'errors', {} )

        emails = kwargs['errors'].keys()
        emails.sort()
        kwargs.setdefault( 'recipients', ', '.join(emails) )


def initialize( context ):
    # module initialization callback

    context.registerClass(
        MailSMTP,
        permission      = Permissions.AddMailHostObjects,
        constructors    = (manage_addMailSMTP,),
    )
