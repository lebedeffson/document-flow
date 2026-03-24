"""
MailPOP -- client class for communication with POP-3 servers

$Editor: vpastukhov $
$Id: MailPOP.py,v 1.8 2004/05/07 13:27:02 vpastukhov Exp $
"""
__version__ = '$Revision: 1.8 $'[11:-2]

from poplib import POP3, error_proto
from sys import exc_info

from AccessControl import ClassSecurityInfo
from BTrees.OIBTree import OIBTree
from zLOG import LOG, TRACE, ERROR

import Config
from Config import Permissions
from Exceptions import SimpleError
from Mail import MailServerBase
from Utils import InitializeClass, SequenceTypes


class MailPOP( MailServerBase ):
    """
        POP3 mail service class.
    """
    _class_version = 1.34

    meta_type = 'Mail POP'

    security = ClassSecurityInfo()

    # default attribute values
    protocol = 'pop'
    default_port = 110

    # temporary session state
    _v_login  = None
    _v_folder = None

    # temporary UID lists
    _v_all_uids  = None
    _v_seen_uids = None

    def open( self, login, password, state=None ):
        """
            Opens mail session.

            Positional arguments:

                'login' -- login name string

                'password' -- password string

            Keyword arguments:

                'state' -- optional mapping containing UIDs
                           of messages already seen by the client
        """
        if self._v_conn and self._v_login == login:
            return

        MailServerBase.open( self )

        try:
            self._v_conn.user( str(login) )
            self._v_conn.pass_( str(password) or '""' )

        except error_proto, exc:
            LOG( 'MailPOP.open', ERROR, '[%s] unable to login as "%s"' % (self.address(), login), error=exc_info() )
            self.close()
            raise MailPOPError( 'mail.pop_cannot_login', login=login, exc=exc )

        except:
            self.close()
            raise

        self._v_login = login

        if state is None:
            self._v_seen_uids = OIBTree()
        else:
            self._v_seen_uids = state

    def close( self ):
        """
            Closes mail session.
        """
        self._v_login = self._v_folder = None
        self._v_all_uids = self._v_seen_uids = None

        MailServerBase.close( self )

    def _connect( self ):
        # opens connection to the server
        self._v_conn = POP3( self.host, self.port )

    def _disconnect( self ):
        # closes connection to the server
        self._v_conn.quit()

    security.declarePrivate( 'getState' )
    def getState( self ):
        """
            Returns private object for keeping mail state
            (such as a list of seen messages) accross sessions.

            Result:

                Opaque object.
        """
        return self._v_seen_uids

    security.declarePrivate( 'openFolder' )
    def openFolder( self, name=Config.MailInboxName ):
        """
            Selects named folder (always 'INBOX' for POP3) for work.

            Positional arguments:

                'name' -- folder name
        """
        if name != Config.MailInboxName:
            raise MailPOPError( 'mail.invalid_folder_name', name=name )

        if not self._v_conn:
            self.open()

        if self._v_folder != name:
            self._v_folder = name
            self._v_all_uids = None

    security.declarePrivate( 'fetchMessages' )
    def fetchMessages( self, all=False, mark=False ):
        """
            Fetches messages from the current folder.

            Keyword arguments:

                'all' -- boolean flag indicating that all messages on
                         the server should be fetched; default is to fetch
                         only messages not marked as seen

                'mark' -- boolean flag, if true (default) then fetched
                          messages will be marked as seen

            Result:

                A list of 'MailMessage' objects.
        """
        conn = self._v_conn
        if not conn:
            return []

        all_uids  = self._v_all_uids
        seen_uids = self._v_seen_uids
        msgs = []

        if all_uids is None:
            all_uids = self._listUids()

        if seen_uids is None:
            all  = True
            mark = False
        else:
            seen = seen_uids.has_key

        #LOG( 'MailPOP.fetchMessages', TRACE, 'server has %d message(s)' % len(all_uids) )

        for i in range( len(all_uids) ):
            uid = all_uids[i]
            if uid is None or ( not all and seen( uid ) ):
                continue

            #LOG( 'MailPOP.fetchMessages', TRACE, 'retrieving message %d uid=%s' % (i, uid) )

            try:
                res, lines, size = conn.retr( i )

            except:
                LOG( 'MailPOP.fetchMessages', ERROR,
                     '[%s@%s] cannot retrieve message %d uid=%s' % \
                     (self._v_login, self.address(), i, uid), error=exc_info() )
                continue

            try:
                msg = self.createMessage( source='\n'.join(lines) )

            except:
                LOG( 'MailPOP.fetchMessages', ERROR, \
                     '[%s@%s] cannot parse message %d uid=%s' % \
                     (self._v_login, self.address(), i, uid), error=exc_info() )
                continue

            msg.uid = uid
            msgs.append( msg )

            if mark:
                seen_uids[ uid ] = 1

        return msgs

    security.declarePrivate( 'getFlags' )
    def getFlags( self, uid, *names ):
        """
            Returns value of the specified flag of a message.

            Arguments:

                'uid' -- mail UID of the message

                '*names' -- names of the flags of interest

            Result:

                Flag value if a single name was given,
                tuple of values otherwise, in the same order as names.
        """
        result = []

        for name in names:
            if name == 'seen':
                value = self._v_seen_uids.get( uid )
            else:
                value = None
            result.append( value )

        if len(names) == 1:
            return result[0]
        else:
            return tuple(result)

    security.declarePrivate( 'setFlags' )
    def setFlags( self, uid, **flags ):
        """
            Marks given message with specified flag(s).

            Positional arguments:

                'uid' -- mail UID of the message

            Keyword arguments:

                '**flags' -- name-value pairs for each flag

            Note:

                For POP3, only 'seen' flag is supported
                (should the message be marked as seen or unseen)
        """
        if flags.has_key('seen'):
            if flags['seen']:
                self._v_seen_uids[ uid ] = 1
            else:
                try: del self._v_seen_uids[ uid ]
                except: pass

    security.declarePrivate( 'deleteMessages' )
    def deleteMessages( self, uid=None, old=False, all=False ):
        """
            Deletes one or more messages from the current folder.

            Positional arguments:

                'uid' -- mail UID of the message, or list of UIDs

            Keyword arguments:

                'old' -- boolean flag indicating that messages already
                        seen should be deleted; overrides 'uid' argument

                'all' -- boolean flag indicating that all messages on
                        the server should be deleted; overrides both 'uid'
                        and 'old' arguments

            Result:

                Number of deleted messages.

            Note:

                In POP3 messages are not actually deleted until QUIT.
        """
        conn = self._v_conn
        if not conn:
            return 0

        all_uids  = self._v_all_uids
        seen_uids = self._v_seen_uids
        count = 0

        if all_uids is None:
            all_uids = self._listUids()

        if all:
            # remove all messages
            uidlist = filter( None, all_uids )

        elif old:
            # remove seen messages
            if seen_uids is None:
                return 0
            uidlist = seen_uids.keys()

        elif type(uid) in SequenceTypes:
            # remove given set of messages
            uidlist = uid

        else:
            # remove a single message
            uidlist = [ uid ]

        for uid in uidlist:
            # find message number by UID
            try:
                i = all_uids.index( uid )
            except ValueError:
                continue

            # forget this UID at this point
            all_uids[i] = None

            # execute POP3 DELE command
            try:
                conn.dele( i )
                count += 1

            except error_proto:
                LOG( 'MailPOP.deleteMessages', ERROR,
                     '[%s@%s] cannot delete message %d uid=%s' % \
                     (self._v_login, self.address(), i, uid), error=exc_info() )
                continue

            # cleanup seen mapping
            if seen_uids.has_key( uid ):
                del seen_uids[ uid ]

        return count

    def _listUids( self ):
        """
            Returns UIDs of messages in the current folder.

            If 'state' mapping was given when selecting folder,
            clears it from UIDs not on the server anymore.

            Result:

                List of message UID values, starting from 1.
                Deleted messages have corresponding UID element
                set to 'None'.
        """
        conn = self._v_conn
        if not conn:
            return []

        all_uids  = self._v_all_uids = []
        seen_uids = self._v_seen_uids

        try:
            res, lines, size = conn.uidl()

        except error_proto, exc:
            LOG( 'MailPOP._listUids', ERROR,
                 '[%s@%s] error getting message index' % \
                 (self._v_login, self.address()), error=exc_info() )
            # Some moron POP3 servers may respond with an error like
            # "-ERR maildrop empty" instead of sending an empty list.
            # Thus we just ignore errors to UIDL command.
            #raise MailPOPError( 'mail.pop_server_error', exc=exc )
            return all_uids

        for line in lines:
            try:
                i, uid = line.strip().split()
                i = int(i)
            except ValueError:
                raise MailPOPError( 'mail.pop_invalid_response', response=line )

            # extend uids list to fit the message number
            all_uids.extend( [None] * (i-len(all_uids)+1) )
            all_uids[i] = uid

        if seen_uids:
            for uid in seen_uids.keys():
                if not all_uids.count( uid ):
                    del seen_uids[ uid ]

        return all_uids

    security.declareProtected( Permissions.UseMailServerServices, 'createMessage' )
    def createMessage( self, *args, **kw ):
        """
            Creates a new mail message instance with character set
            conversion from e-mail to portal encoding.

            Arguments:

                '*args', '**kw' -- arguments for the 'MailMessage'
                                   constructor

            Result:

                'MailMessage' object.
        """
        if not kw.has_key('charset'):
            kw['charset'] = self.getInputCharset()
        return MailServerBase.createMessage( self, *args, **kw )

InitializeClass( MailPOP )


class MailPOPError( SimpleError ):

    def __init__( self, *args, **kwargs ):
        SimpleError.__init__( self, *args, **kwargs )

        if not kwargs.has_key('response'):
            if isinstance( self.precedent, error_proto ):
                error = str( self.precedent )
                if error.startswith('-ERR '):
                    error = error[5:]
            else:
                error = ''
            self.kwargs['response'] = error


def manage_addMailPOP( self, id='MailPOP', title='', host=None, port=None, REQUEST=None ):
    """
        Creates a new MailPOP instance and adds it into the container
    """
    self._setObject( id, MailPOP( id, title, host, port ) )

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect( REQUEST.URL1 )


def initialize( context ):
    # module initialization callback

    context.registerClass(
        MailPOP,
        permission      = Permissions.AddMailServerObjects,
        constructors    = (manage_addMailPOP,),
    )
