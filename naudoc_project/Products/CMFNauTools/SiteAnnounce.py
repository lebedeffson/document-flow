""" SiteAnnounce class.
$Id: SiteAnnounce.py,v 1.18 2005/11/20 16:43:48 vsafronovich Exp $

$Editor: kfirsov $
"""
__version__ = '$Revision: 1.18 $'[11:-2]

from zLOG import LOG, INFO

import copy
import os
import threading
from random import random


from Acquisition import Implicit, aq_parent, aq_inner
from OFS.Traversable import Traversable
from ZODB.POSException import ConflictError

from Products.CMFCore.utils import getToolByName
from Products.NauScheduler.TemporalExpressions import DailyTE

from SimpleObjects import Persistent
from SyncableContent import SyncableContent
from Utils import getObjectByUid


class SubscribedUser:
    """
        Simple helper class to store each subscriber's data.

        Main goal is to store temporary data (like email, folders,
        where user is subscribed, and folders with published documents).
        After all, there is  renderMailText() method that renders
        mail message to user using all these data.
    """
    def __init__(self, email, isMember):
        """
            Simple constructor.
        """
        self.email = email
        self.isMember  = isMember
        self.foldersData = {}

    def setSubscribedFolder(self, f_uid, data=[]):
        """
            Adds data about given folder.

            Arguments:

                'f_uid' -- Uid of folder where user is subscribed.

                'data' -- List of folders uids, where published documents placed.
        """
        folders = self.foldersData.setdefault(f_uid, f_uid in data and [f_uid] or [])
        for folder in data:
            if not self.foldersData.has_key(folder):
                folders.append(folder)
                self.foldersData[ folder ] = []

    def renderMailText(self, mails_texts, context, lang):
        """
            Renders full email message for user about all published
            documents and in which folders they are publishde. Also
            inserts in the message data about folders on which user is
            subscribed (to make it easy to unsubscribe).

            Arguments:

                'mails_texts' -- Dictionary, where keys are (folder uid, flag)
                    and values are strings. 'flag' may be 'internal' - all
                    links placed in string are for portal member, or
                    'external' - all links placed in string are for external
                    (thrue publisher). Values - strings with rendered text
                    for the folder (about all published documents).

                'context' -- Since the SubscribedUser class does not support
                    acquisition, context is needed to access dtmls and to
                    get objects by their uid.

                'lang' -- Language for messages.

            Result:

                String.
        """
        where = self.isMember and 'internal' or 'external'

        #insert mail header
        results = [ context.announce_header(lang=lang) ]

        realy_documents_presented = 0

        for uid_where_subscribed, uids_with_data in self.foldersData.items():
            mails = []
            for uid_with_data in uids_with_data:
                #folders with published documents
                folder_text = mails_texts.get( (uid_with_data, where), '')
                if folder_text:
                    realy_documents_presented = 1

                mails.append( folder_text )

            if len(uids_with_data):
                #folder where user subscribed
                folder = getObjectByUid(context=context, uid=uid_where_subscribed)

                if self.isMember:
                    unsubscription_url = folder.absolute_url( action='manage_subscription' )
                else:
                    unsubscription_url = folder.server_url + folder.external_url(
                                        action='subscription',
                                        params={ 'action':'unsubscribe', 'email':self.email } )
                mails.append( \
                    context.announce_unsubscribe(lang=lang, unsubscription_url=unsubscription_url) \
                    )

            results.append('\n'.join(mails))

        if not realy_documents_presented:
            raise AttributeError, 'No documents presented'

        #append footer
        results.append( context.announce_footer(lang=lang) )
        return ''.join(results)


class SiteAnnounce(Persistent, SyncableContent, Implicit, Traversable): #maybe CopySource?
    """
        SiteAnnounce provides methods for collecting information about
        publications and then sending it in one email letter to each
        subscribed user.

    """

    __resource_type__ = 'item'

    _sync_reserved = SyncableContent._sync_reserved + \
        ( 'sheduled_task', 'sheduled_props', '_announcement_data')

    def __init__(self, id='announce_task'):
        """
            Simple constructor
        """
        self.id = id
        self._announcement_data = {}
        #XXX fix sheduled -> scheduled
        self.sheduled_task = None
        self.sheduled_props = { 'start_hour': 02, \
                                'start_minute' : 00, \
                                'interval' : 24, \
                                'log' : 0 \
                              }
    def getId(self):
        return self.id


    def _DailyTE(self):
        return DailyTE( hour=self.sheduled_props['start_hour'], \
                        minute=self.sheduled_props['start_minute'], \
                        second=0, \
                        days=1)

    def createTask(self, scheduler=None):
        """
            Creates periodical task in portal_scheduler.

            Arguments:

                'scheduler' -- Scheduler object. If not specified,
                    portal_scheduler will be used.
        """
        if scheduler is None:
            scheduler = getToolByName( self, 'portal_scheduler' )

        self.delTask( scheduler )

        #there is bug : we set SELF.announcePublished, but will be called
        # site's announcePublished(). Because there is no self in physicalPath.

        self.sheduled_task = scheduler.addScheduleElement(method=self.announcePublished, \
                    temporal_expr=self._DailyTE(), \
                    title='Announce published documents', \
                    args=(), \
                    kwargs={} )

    def delTask(self, scheduler=None):
        """
            Removed periodical task in portal_scheduler.

            Arguments:

                'scheduler' -- Scheduler object. If not specified,
                    portal_scheduler will be used.
        """
        if scheduler is None:
            scheduler = getToolByName(self, 'portal_scheduler')

        try:
            scheduler.delScheduleElement( self.sheduled_task )
        except (KeyError, TypeError):
            pass

        self.sheduled_task = None

    def addPublication(self, folder_uid, document_id, doc_modif_time):
        """
            Adds data about published document.

            Arguments:

                'folder_uid' -- Uid of the folder in which the document is located.

                'document_id' -- Id of published document.

                'doc_modif_time' -- Last modification time of the document.
        """
        self._announcement_data.setdefault( folder_uid, {} )[document_id] = doc_modif_time
        self._p_changed = 1
        self.updateRemoteCopy( recursive=0 )

        if self.checkRemoteParams():
            #remote ZEO server used
            self._announcement_data = {}


    def setScheduleProperties(self, start_hour=None, start_minute=None, interval=None, log=None):
        """
            Changes announce task properties.

            Also changes started task's properties according given ones.
            If announce task is not started, starts it.

            Arguments:

                'start_hour', 'start_minute' -- time in which to start task (hour:minute)

                'interval' -- interval in hours

                'log' -- use or not logging in scheduled task
        """
        scheduler = getToolByName(self, 'portal_scheduler')

        if start_hour is not None:
            self.sheduled_props['start_hour'] = start_hour

        if start_minute is not None:
            self.sheduled_props['start_minute'] = start_minute

        if interval is not None:
            self.sheduled_props['interval'] = interval

        if log is not None:
            self.sheduled_props['log'] = not not log

        if self.sheduled_task is not None:
            try:
                element = scheduler.getScheduleElement(self.sheduled_task)
                element.setTemporalExpression( self._DailyTE() )
            except (KeyError, TypeError):
                pass

        else:
            self.delTask(scheduler)
            self.createTask(scheduler)

    def _checkDocumentValidity(self, rh, modif_time):
        """
            Checks if the document is still published and was not changed since last publication.

            Arguments:

                'rh' -- document's review_history

                'modif_time' -- last documet's modification time

            Result:

                String (if error), None (if ok).
        """
        if not rh:
            return "No review history available"

        if rh[-1]['action']!='publish':
            return "Review's history last action is: '%s'." % rh[-1]['action']

        if not rh[-1]['published']:
            return "Review's history is not 'published'."

        #three minutes difference check is for documents published by ZEO

        ### XXX may be unneeded here caus'of _announcement_data is dictionary!!!
        three_minutes = 1.0/( 24 * 60 ) * 3
        if abs(modif_time - rh[-1]['time']) > three_minutes:
            return "There is more than 3 minutes difference: modif_time=%s and rh[-1]['time']=%s"%(str(modif_time), str(rh[-1]['time']))


    def _collectDocumentsProps(self, wftool, folder, documents_data):
        """
            Colects documents properties.

            Arguments:

                'wftool' -- WorkflowTool (portal_workflow)

                'folder' -- folder (Heading object) where documents are placed

                'documents_data' -- dictionary: {document id:modification date, ...}

            Result:

                List of dictionaries.
        """
        documents_props = []

        for obj_id in documents_data.keys():
            try:
                document =  folder._getOb( obj_id )
            except AttributeError:
                #document was removed, skip
                continue

            #if errors in these checks, just log about it; don't stop
            rh = wftool.getInfoFor(document, 'review_history')
            result = self._checkDocumentValidity(rh, documents_data[obj_id] )
            #result = None # for test purpose only

            if result:
                LOG( 'SiteAnnounce.announcePublished', INFO, 'Document %s skipped. Reason: %s.' %(`document`, result) )
                continue

            if document is not None:
                try:
                    external_url = self.server_url + document.external_url()
                except:
                    external_url = document.external_url()
                    LOG( 'SiteAnnounce.announcePublished', INFO, 'Document %s skipped. Reason: %s.' %(`document`, 'unknown') )

                documents_props.append( {
                    'title' :   document.title_or_id(),
                    'summary' : document.Description(),
                    'internal': document.absolute_url(),
                    'external': external_url,
                    } )

        return documents_props

    def announcePublished(self):
        """
            'Demon' function.

            It generates email announces about published documents on site
            (stored in self._announcement_data) and sends them to subscribed
            users.

        """
        LOG( 'SiteAnnounce.announcePublished', INFO, 'Start' )

        #copy _announcement_data for safe
        data = copy.deepcopy( self._announcement_data )

        try:
            os.nice(10)
        except AttributeError:
            pass

        #TODO : remove all intermediate data to clear some memory

        users = {} #dict with {user_id:SubscribedUser()}

        mails_texts = {} # (uid, 'external'):text1; (uid, 'internal'):text2; ...

        initial_uids = data.keys()

        wftool = getToolByName( self, 'portal_workflow' )
        membership = getToolByName( self, 'portal_membership' )

        #found documents, lets render text.
        msg = getToolByName( self, 'msg' )
        try:
            lang = msg.get_selected_language()
        except AttributeError:
            lang = msg.get_default_language()

        #in this loop generate intermediate text for all published documents
        #in each given folder
        for uid in initial_uids:
            folder = getObjectByUid(context=self, uid=uid)

            documents_props = self._collectDocumentsProps( wftool, folder, data[uid] )

            if not documents_props:
                #No valid published documents in the folder. There is nothing to announce.
                try:
                    folder_url = folder.absolute_url()
                except AttributeError:
                    folder_url = uid
                LOG( 'SiteAnnounce.announcePublished', INFO, \
                    'No valid published documents in the folder %s. There is nothing to announce.' % folder_url )
                continue

            folder_title = folder.title_or_id()

            internal_text = self.announce_intermediate(
                folder_title = folder_title,
                doc_props = documents_props,
                lang = lang,
                use_url = 'internal'
            )
            mails_texts[ (uid, 'internal') ] = internal_text

            external_text = self.announce_intermediate(
                folder_title = folder_title,
                doc_props = documents_props,
                lang = lang,
                use_url = 'external'
            )
            mails_texts[ (uid, 'external') ] = external_text


        # now lets create email text for each user
        for uid in initial_uids:
            folder = getObjectByUid(context=self, uid=uid)
            list_with_folders_where_docs = [ ]

            while folder and not folder.implements('isPortalRoot'):
                folder_uid = folder.getUid()

                if folder_uid in initial_uids:
                    list_with_folders_where_docs.append( folder_uid )

                if folder.implements('hasSubscription'):
                    usrs = [ u for (u, f) in folder.subscribed_users.items() if f ]

                    for uname in usrs:
                        email = uname
                        if not users.has_key( uname ):
                            isMember = 0

                            if uname.find('@') < 0:
                                member = membership.getMemberById( uname )
                                if member:
                                    isMember = 1
                                    email = member.getMemberEmail()
                                else:
                                    #something strange
                                    continue
                            users[ uname ] = SubscribedUser(email, isMember)
                        users[ uname ].setSubscribedFolder(folder.getUid(), list_with_folders_where_docs)

                folder = aq_parent( aq_inner( folder ) )

        #mail messages
        server = getToolByName( self, 'MailHost' )

        for uname, user in users.items():
            email = user.email
            try:
                message_source = user.renderMailText(mails_texts, self, lang=lang)
            except AttributeError:
                LOG( 'SiteAnnounce.announcePublished', INFO, 'No documents for user "%s"' % uname )
                continue

            # for newer MailSender
            message = server.createMessage( source=message_source )

            #for MailSender older than 08 sep. 2003
            #message = server.message( source=message_source )

            #one user - one message.
            server.send( message, [email] )

        #XXX thread unsafe
        for f_uid, value in data.items():
            for o_id in value.keys():
                try:
                    del self._announcement_data[ f_uid ][ o_id ]
                except KeyError:
                    pass
                try:
                    if not self._announcement_data[ f_uid ]:
                        del self._announcement_data[ f_uid ]
                except KeyError:
                    pass
        self._p_changed = 1

        LOG( 'SiteAnnounce.announcePublished', INFO, 'End' )


    def _remote_transfer( self, context=None, container=None, server=None, path=None, id=None, parents=None, recursive=None ):
        """
        """
        remote = SyncableContent._remote_transfer( self, context, container, server, path, id, parents, recursive )

        for uid, ids_data in self._announcement_data.items():
            uid_record = remote._announcement_data.setdefault( uid, {} )
            uid_record.update( ids_data )
        remote._p_changed = 1
        return remote
