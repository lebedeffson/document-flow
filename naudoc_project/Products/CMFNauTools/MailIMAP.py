"""
MailIMAP -- client class for communication with IMAP-4 servers

$Editor: mbernatski $
$Id: MailIMAP.py,v 1.6 2005/09/23 07:28:24 vsafronovich Exp $
"""
__version__ = "$Revision: 1.6 $"[11:-2]

from zLOG import LOG, DEBUG, TRACE, INFO, ERROR

from imaplib import IMAP4
from sys import exc_info

from AccessControl import ClassSecurityInfo
from BTrees.OIBTree import OIBTree
from BTrees.IIBTree import IIBTree
from BTrees.OOBTree import OOBTree

import Config
from Config import Permissions
from Exceptions import SimpleError
from Mail import MailServerBase
from Utils import InitializeClass, SequenceTypes


class MailIMAP( MailServerBase ):
    """
        IMAP4 mail service class.
    """
    _class_version = 1.0

    meta_type = 'Mail IMAP'

    security = ClassSecurityInfo()

    # default attribute values
    protocol = 'imap'
    default_port = 143

    # temporary session state
    _v_login  = None
    _v_folder = None

    _v_state  = None

    # temporary UID lists
    _v_all_uids  = None

    def _connect( self ):
        # opens connection to the server
        self._v_conn = IMAP4( self.host, self.port )

    def _disconnect( self ):
        # closes connection to the server
        self._v_conn.logout()

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
            self._v_conn.login( login, str(password) or '""' )
        except:
            LOG( 'MailIMAP.open', ERROR, '[%s] unable to login as "%s"' % (self.address(), login), error=exc_info() )
            self.close()
            raise

        self._v_login = login

        if state is None:
            self._v_state = OOBTree()
        else:
            self._v_state = state

    def close( self ):
        """
            Closes mail session.
        """
        self._v_all_uids = None

        if self._v_folder is not None:
            self._v_conn.expunge()

        self._v_login = self._v_folder = None
        MailServerBase.close( self )

    security.declarePrivate( 'getState' )
    def getState( self ):
        """
            Returns private object for keeping mail state
            (such as a list of received messages) across sessions.

            Result:

                Opaque object.
        """
        return self._v_state

    security.declarePrivate( 'openFolder' )
    def openFolder( self, name=Config.MailInboxName ):
        """
            Selects named folder for work.

            Positional arguments:

                'name' -- folder name
        """
        if not self._v_conn:
            self.open()

        if self._v_folder != None:
            self._v_conn.expunge()

        response = self._v_conn.select( name )
        if response[0] != 'OK':
            raise MailIMAPError( 'mail.invalid_folder_name', name=name )

        self._v_folder = name

        if not self._v_state.has_key( name ):
            self._v_state[ name ] = OOBTree()
            self._v_state[ name ]['uid_validity'] = None
            self._v_state[ name ]['seen_uids'] = IIBTree()

        self._v_selected = self._v_state[ name ]

        answer_list = self._v_conn.response( 'UIDVALIDITY' )

        answer = answer_list[1][0]
        if answer is not None:
            answer = int( answer )
            if not self._v_selected.has_key( 'uid_validity' ):
                self._v_selected['uid_validity'] = answer
            elif self._v_selected['uid_validity'] != answer:
                self._v_selected['uid_validity'] = answer

    def _listUids( self ):
        all_uids  = self._v_all_uids = []
        imap = self._v_conn
        try:
            res, answer_list = imap.uid( 'SEARCH', None, 'ALL' )
        except IMAP4.error:
            LOG( 'MailIMAP._listUids', ERROR,
                 '[%s@%s] error getting message index' % \
                 (self._v_login, self.address()), error=exc_info() )
            raise

        uids_list = answer_list[0].strip().split()
        all_uids.extend( uids_list )
        seen_uids = self._v_selected
        if seen_uids:
            for uid in seen_uids.keys():
                try:
                    all_uids.index( str( uid ) )
                    continue
                except ValueError:
                    del seen_uids[ uid ]

        try:
            res, answer_list = imap.uid( 'SEARCH', None, 'DELETED' )
        except IMAP4.error:
            LOG( 'MailIMAP._listUids', ERROR,
                 '[%s@%s] error getting message index' % \
                 (self._v_login, self.address()), error=exc_info() )
            raise

        uids_del = answer_list[0].strip().split()
        for uid in uids_del:
            try:
                index = all_uids.index( str( uid ) )
                all_uids[index] = None
            except ValueError:
                continue

        return all_uids

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
        imap = self._v_conn
        all_uids  = self._v_all_uids
        seen_uids = self._v_selected
        msgs = []

        if all_uids is None:
            all_uids = self._listUids()

        if seen_uids is None:
            all  = True
            mark = False

        #LOG( 'MailIMAP.fetchMessages', TRACE, 'server has %d message(s)' % len(all_uids) )

        for i in range( len(all_uids) ):
            uid = all_uids[i]
            if uid is None or seen_uids.has_key( uid ):
                continue

            #LOG( 'MailIMAP.fetchMessages', TRACE, 'retrieving message %d uid=%s' % (i, uid) )

            try:
                answer, answer_body = imap.uid( 'FETCH', uid, '(BODY.PEEK[])' )
                msg_text = answer_body[0][1]
            except:
                LOG( 'MailIMAP.fetchMessages', ERROR,
                     '[%s@%s] cannot retrieve message %d uid=%s' % \
                     (self._v_login, self.address(), i, uid), error=exc_info() )
                continue

            try:
                msg = self.createMessage( source=msg_text )

            except:
                LOG( 'MailIMAP.fetchMessages', ERROR, \
                     '[%s@%s] cannot parse message %d uid=%s' % \
                     (self._v_login, self.address(), i, uid), error=exc_info() )
                continue

            msg.uid = uid
            msgs.append( msg )

            if mark:
                seen_uids[ uid ] = 1

        self._v_selected['seen_uids'] = seen_uids
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
        seen_uids = self._v_selected['seen_uids']
        for name in names:
            if name == 'seen':
                value = seen_uids.get( uid )
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

                Now only 'seen' flag is supported
                (should the message be marked as seen or unseen)
        """
        if flags.has_key('seen'):
            if flags['seen']:
                self._v_selected['seen_uids'][ uid ] = 1
            else:
                try: del self._v_selected['seen_uids'][ uid ]
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

        """
        imap = self._v_conn
        all_uids  = self._v_all_uids
        seen_uids = self._v_selected
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

            # execute IMAP4 STORE command
            try:
                imap.uid( 'STORE', uid, '+FLAGS', '(\\DELETED)' )
                count += 1

            except IMAP4.error:
                LOG( 'MailIMAP.deleteMessages', ERROR,
                     '[%s@%s] cannot delete message %d uid=%s' % \
                     (self._v_login, self.address(), i, uid), error=exc_info() )
                continue

            # cleanup seen mapping
            if seen_uids.has_key( uid ):
                del seen_uids[ uid ]

        return count

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

InitializeClass( MailIMAP )

class MailIMAPError( SimpleError ): pass

def manage_addMailIMAP( self, id='MailIMAP', title='', host=None, port=None, REQUEST=None ):
    """
        Creates a new MailIMAP instance and adds it into the container
    """
    self._setObject( id, MailIMAP( id, title, host, port ) )

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect( REQUEST.URL1 )


def initialize( context ):
    # module initialization callback

    context.registerClass(
        MailIMAP,
        permission      = Permissions.AddMailServerObjects,
        constructors    = (manage_addMailIMAP,),
    )
