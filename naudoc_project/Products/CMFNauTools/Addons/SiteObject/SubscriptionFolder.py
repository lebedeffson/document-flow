# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/SiteObject/SubscriptionFolder.py
# Compiled at: 2008-10-15 16:48:07
""" SubscriptionFolder, Subscription and SubscribedUser classes
$Id: SubscriptionFolder.py,v 1.1 2008/10/15 12:48:07 oevsegneev Exp $
$Editor: kfirsov $
"""
__version__ = '$Revision: 1.1 $'
from zLOG import LOG, DEBUG, TRACE, INFO, ERROR
from types import StringType
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from App.FactoryDispatcher import FactoryDispatcher
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from ZODB.PersistentMapping import PersistentMapping
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Localizer import get_request
from Products.NauScheduler.TemporalExpressions import DailyTE
from Products.CMFNauTools import Features
from Products.CMFNauTools.Config import Permissions
from Products.CMFNauTools.Exceptions import SimpleError
from Products.CMFNauTools.Heading import Heading, HeadingType
from Products.CMFNauTools.Mail import formatFromAddress, mailFromDocument
from Products.CMFNauTools.SimpleObjects import Persistent
from Products.CMFNauTools.Utils import InitializeClass, extractParams, extractBody, inheritActions, SequenceTypes
SubscriptionFolderType = {'id': 'Subscription Folder', 'content_meta_type': 'Subscription Folder', 'title': 'Subscription Folder', 'description': 'Subscription Folder', 'icon': 'folder_icon.gif', 'sort_order': 0.3, 'product': 'CMFNauTools', 'factory': 'addSubscriptionFolder', 'permissions': (Permissions.AddSubscriptionFolder,), 'condition': 'python: object.getSubscription()', 'filter_content_types': 1, 'allowed_content_types': ('Subscription Folder', 'HTMLDocument'), 'immediate_view': 'folder_edit_form', 'actions': (inheritActions(HeadingType, 'contents', 'view', 'edit') + ({'id': 'subscribers', 'name': 'Subscribers', 'action': 'manage_subscription_form', 'permissions': (Permissions.SubscribeUsers,), 'category': 'folder'}, {'id': 'send', 'name': 'Send queued email', 'action': 'confirm_dispatch', 'permissions': (Permissions.UseMailServerServices,), 'category': 'folder'}, {'id': 'test_delivery', 'name': 'Test delivery', 'action': 'test_delivery', 'permissions': (Permissions.UseMailServerServices,), 'category': 'folder'}, {'id': 'edit_user', 'name': 'Edit user', 'action': 'subscribe_user', 'permissions': (Permissions.SubscribeUsers,), 'category': 'folder', 'visible': False}))}
SubscriptionRootType = {'id': 'Subscription Root', 'content_meta_type': 'Subscription Root', 'title': 'Subscription Root', 'description': 'Subscription Root', 'factory': 'addSubscription', 'permissions': (Permissions.AddSubscriptionRoot,), 'condition': "python: object.id=='storage' and getattr(object.getSite(), 'storage', None)==object", 'sort_order': 0.3, 'immediate_view': 'folder_edit_form', 'product': 'CMFNauTools', 'content_icon': 'folder_icon.gif', 'icon': 'folder_icon.gif', 'actions': (inheritActions(HeadingType, 'contents', 'view', 'edit') + ({'id': 'edit_users', 'name': 'Manage subscribed users', 'action': 'manage_subscription_form', 'permissions': (Permissions.SubscribeUsers,), 'category': 'folder'}, {'id': 'subscribe_user', 'name': 'Subscribe user', 'action': 'subscribe_user', 'permissions': (Permissions.SubscribeUsers,), 'category': 'folder'}, {'id': 'import', 'name': 'Import from file', 'action': 'subscr_import_form', 'permissions': (Permissions.SubscribeUsers,), 'category': 'folder'}, {'id': 'send', 'name': 'Send queued email', 'action': 'confirm_dispatch', 'permissions': (Permissions.UseMailServerServices,), 'category': 'folder'}, {'id': 'test_delivery', 'name': 'Test delivery', 'action': 'test_delivery', 'permissions': (Permissions.UseMailServerServices,), 'category': 'folder'}, {'id': 'edit_user', 'name': 'Edit user', 'action': 'subscribe_user', 'permissions': (Permissions.SubscribeUsers,), 'category': 'folder', 'visible': False})), 'allowed_content_types': ('Subscription Folder', 'HTMLDocument'), 'filter_content_types': 1}

def addSubscriptionFolder(self, id, title='', REQUEST=None, **kwargs):
    """
        Adds new SubscriptionFolder object.

        Arguments:

            'self' -- FactoryDispatcher instance

            'id' -- identifier of created folder

            'title' -- folder's title

            'REQUEST' -- REQUEST object
    """
    assert isinstance(self, FactoryDispatcher), 'FactoryDispatcher expected'
    destination = self.Destination()
    if destination.implements(Features.isSubscription):
        self._setObject(id, SubscriptionFolder(id, title, **kwargs), set_owner=0)
        item = self._getOb(id)
        item.redirect(action='folder_edit_form', message='Subscription folder added.', REQUEST=REQUEST)
    else:
        raise SimpleError(message='Subscription Folder may be created only in Subscription Root or other Subscription Folder.')
    return


class SubscriptionFolder(Heading):
    """ Subscription Folder class

        SubscriptionFolder is a type of Heading. It's title is topic name for
        all documents stored in it.

        SubscriptionFolder may be placed only in another SubscriptionFolder or
        Subscriptions root.
    """
    __module__ = __name__
    _class_version = 2.0
    meta_type = 'Subscription Folder'
    portal_type = 'Subscription Folder'
    __implements__ = (
     Features.canHaveSubfolders, Features.isContentStorage, Features.isPublishable, Features.isSubscription, Heading.__implements__)
    __unimplements__ = (
     Features.hasContentFilter, Features.isCategorial)
    security = ClassSecurityInfo()
    _actions = ()

    def _returnWithMessage(self, result, REQUEST=None, publisher=0):
        """
            The only goal of this helper method is to reduce stupid checks in code.

            Returns result or redirects to 'folder' action depending on
            'REQUEST' and 'publisher' values.

            Arguments:

                'result' -- result to return

                'REQUEST' -- REQUEST object or None

                'publisher' -- flag, if true, forces return result instead of redirect.

        """
        if publisher or REQUEST is None:
            return result
        return self.redirect(action='folder', message=result, status=303)
        return

    def _createMessageText(self, mail_template, *args, **kwargs):
        """
            Calls mail_template, inserting self as first arg.

            Result:

                Text.
        """
        return apply(mail_template, tuple([self] + list(args)), kwargs)
        return

    def _sendMessage(self, receiver, full_message=None, message_body=None, subject=None, ctype='text/plain'):
        """

            Creates mail message and sends it to the receiver.
            Adds 'From' header according subscription settings.

            Arguments:

                'receiver' -- Either string with email or tuple
                                (reciver_name, receiver_email) or
                                SubscribedUser - who will receive email.

                'full_message' -- Text already containing mail headers (such as
                                Subject, To, etc.)

                'message_body' -- Text without mail headers. There must one of
                                full_message or message_body in parameters.

                'subject' -- Value of the 'Subject' header.

                'ctype' -- Content type.

            Result:

                Number of sent messages.

        """
        if not (full_message or message_body):
            raise ValueError, 'Invalid message text'
        server = getToolByName(self, 'MailHost')
        if full_message:
            message = server.createMessage(source=full_message)
        else:
            message = server.createMessage(ctype=ctype)
            message.get_body().set_payload(payload=message_body)
        if subject is not None:
            message.set_header('Subject', subject)
        message.set_header('from', (self.mail_from_name, self.mail_from_address))
        if type(receiver) is StringType:
            receiver = (
             '', receiver)
        if isinstance(receiver, SubscribedUser):
            receiver = (
             receiver.getInitials(), receiver.email)
        message.set_header('to', receiver)
        return server.send(message, mto=(receiver[1],))
        return

    security.declareProtected(Permissions.UseMailServerServices, 'sendMail')

    def sendMail(self, REQUEST=None):
        """
            Searches documents in the 'queued' state and sends them.
            Recursively calls o.sendMail() for each subfolder o.
        """
        sent = 0
        ids = [_[1] for brain in self.listQueued()]
        sent = self.sendQueued(ids, REQUEST)
        children = self.objectValues('Subscription Folder')
        for child in children:
            sent += child.sendMail(REQUEST)

        return sent
        return

    security.declareProtected(Permissions.UseMailServerServices, 'testDelivery')

    def testDelivery(self, test_doc_ids=[], test_users=[], REQUEST=None):
        """
            Performs test delivery of documents with given ids to given users.
            No actual workflow actions perform here.

            Arguments:

                'test_doc_ids' -- Identifiers of documents in this folder.

                'test_users' -- List with emails.

                'REQUEST' -- REQUEST object.

            Result:

                Number of sent messages if REQUEST is None.
                Else status string.

        """
        if not test_users:
            return self._returnWithMessage('Please select at least one subscriber.', REQUEST)
        if not test_doc_ids:
            return self._returnWithMessage('Please select at least one document.', REQUEST)
        documents = map(self._getOb, test_doc_ids)
        users = filter(None, map(self.getUser, test_users))
        delivered = 0
        if documents and users:
            delivered = self._makeTextAndSendDocumentsAndDoWorkflow(documents, users, do_workflow_actions=0)
        result = 'Nothing was sent due to errors.'
        if delivered:
            result = 'Sent %d message(s).' % delivered
        return self._returnWithMessage(result, REQUEST)
        return

    def _listAllUsersForSelf(self):
        """
            The only goal of this method is to encapsulate the way of getting
            subscribed users (the same way for Subscription and
            SubscriptionFolder).

            Returns list of subscribed users in this and upper folders.
        """
        return self.listUsersFor(context=self)
        return

    security.declareProtected(Permissions.UseMailServerServices, 'dispatchNow')

    def dispatchNow(self, document):
        """
            Makes message from document, sends round this message to all
            users subscribed in this or upper folder(s). Also performs
            workflow actions with document.

            Note: Is called when selected 'dispatch now' in document workflow.

            Arguments:

                'document' -- HTMLDocument object in the "sending" state.

            Result:

                Number of sent messages.

        """
        users = self._listAllUsersForSelf()
        delivered = 0
        if users:
            delivered = self._makeTextAndSendDocumentsAndDoWorkflow([document], users, do_workflow_actions=1)
        if not delivered:
            raise SimpleError, 'Nothing was sent due to errors.'
        return delivered
        return

    security.declareProtected(Permissions.UseMailServerServices, 'sendQueued')

    def sendQueued(self, ids, REQUEST=None):
        """
            Makes message from documents with given ids, sends round these
            messages to all users subscribed in this or upper folder(s).
            Also performs workflow actions with documents.

            Arguments:

                'ids' -- Identifiers of documents in this folder (documents
                        should be in the "queued" state).
                'REQUEST' -- REQUEST object.

            Result:

                Number of sent messages if REQUEST is None.
                Else status string.
        """
        users = self._listAllUsersForSelf()
        documents = map(self._getOb, ids)
        delivered = 0

        def doNothing():
            return

        wftool = getToolByName(self, 'portal_workflow')
        for document in documents:
            if wftool.getStateFor(document) == 'queued':
                wftool.wrapWorkflowMethod(document, 'to_sending', doNothing, (), {})

        if documents and users:
            delivered = self._makeTextAndSendDocumentsAndDoWorkflow(documents, users, do_workflow_actions=1)
        result = 'Nothing was sent due to errors.'
        if delivered:
            result = 'Sent %d message(s).' % delivered
        return self._returnWithMessage(result, REQUEST)
        return

    def getServerUrl(self, REQUEST=None):
        """
            Evaluates URL of the server.

            Result:

                String.
        """
        rq = REQUEST or get_request()
        return rq is not None and rq.get('SERVER_URL', None) or self.server_url
        return

    def _makeTextAndSendDocumentsAndDoWorkflow(self, documents, users, do_workflow_actions=1):
        """
            Generates one text from all the documents and sends this text round
            to given users. If set 'do_workflow_actions', performs workflow
            actions with documents.

            Arguments:

                'documents' -- HTMLDocument instances.

                'users' -- SubscribedUser instances.

                'do_workflow_actions' -- Flag indicating whether perform
                                        workflow actions with documents or not.

            Result:

                Number of sent messages.
        """
        if not (documents and users):
            return 0
        text = self._makeTextFromDocuments(documents)
        edit_props_url = self.getServerUrl() + self.getSubscription().external_url(1)
        delivered = 0
        for user in users:
            new_text = self._createMessageText(self.mailings_document, doc_text=text, lang=getToolByName(self, 'msg').get_selected_language(), text_type='html', edit_props_url=edit_props_url, unsubscription_url=user.URLToUnsubscribe)
            new_text = '<html><body>' + new_text + '</body></html>'
            LOG('Subscription', INFO, 'sending email to %s ...' % user.email)
            try:
                res = self._sendMessage(user, message_body=new_text, subject=self.subject_header, ctype='text/html')
            except SimpleError, error:
                LOG('Subscription', ERROR, 'sending email to %s failed. Reason: %s' % (user.email, repr(error)))
                res = 0
            else:
                if not res:
                    LOG('Subscription', INFO, 'sending email to %s failed' % user.email)

            delivered += res

        if do_workflow_actions:
            wftool = getToolByName(self, 'portal_workflow')
            action = delivered and 'publish' or 'fail'
            for document in documents:
                if wftool.getStateFor(document) == 'sending':
                    wftool.doActionFor(document, action)

        return delivered
        return

    security.declareProtected(CMFCorePermissions.View, 'getPublishedFolders')

    def getPublishedFolders(self):
        """
            Returns list of folders description in which published documents are presented.

            Result:

                List of mappings.
        """
        if not self.getSubscription().getSubscribedUser(self.REQUEST.get('subscribed_email', '')):
            return []
        return Heading.getPublishedFolders(self)
        return

    security.declareProtected(CMFCorePermissions.View, 'listPublications')

    def listPublications(self, exact=None, features=[]):
        """
            Returns list of published documents ids in this folder.

            Only if subscribed_email is set in REQUEST. 'subscribed_email'
            must be set in cookies (REQUEST) to get access to subscription
            archive.
        """
        if not self.getSubscription().getSubscribedUser(self.REQUEST.get('subscribed_email', '')):
            return []
        return Heading.listPublications(self, exact=exact, features=features)
        return

    security.declareProtected(CMFCorePermissions.View, 'listQueued')

    def listQueued(self, ids=None, **kw):
        """
            Searches in catalog for queued messages.

            Arguments:

                'ids' -- ids of documents to search
        """
        catalog = getToolByName(self, 'portal_catalog')
        states = ids and ('evolutive', 'pending', 'queued', 'failed') or ('queued',)
        query = {'parent_path': (self.physical_path()), 'category': 'MailingItem', 'state': states, 'implements': ('isVersionable',)}
        if ids and type(ids) in SequenceTypes:
            query['id'] = ids
        return catalog.searchResults(**query)
        return

    def _makeTextFromDocuments(self, documents):
        """
            Renders one text for all given documents.

            Arguments:

                'documents' -- Either HTMLDocument instances or their ids.

            Result:

                Text.
        """
        result = []
        server = getToolByName(self, 'MailHost')
        is_first_document = 1
        for document in documents:
            if type(document) is StringType:
                document = self._getOb(document)
            message = mailFromDocument(document, factory=server.createMessage)
            result.append(self.mailings_doc(self, topic_title=is_first_document and self.Title() or None, doc_title=document.Title(), doc_text=extractBody(message.get_body().get_payload()), text_type='html'))
            is_first_document = 0

        return ('').join(result)
        return

    security.declareProtected(Permissions.SubscribeUsers, 'addSubscriptionForUsers')

    def addSubscriptionForUsers(self, folder_users=[], REQUEST=None):
        """
            Changes subscribers settings: add this topic to their subscription.

            Arguments:

                'folder_users' -- emails of users who will be subscribed in
                                this folder

                'REQUEST' -- REQUEST object

            Result:

                String.
        """
        users = filter(None, map(self.getUser, folder_users))
        message = 'No changes were made.'
        for user in users:
            if user and not user.isSubscribedToFolder(self):
                message = 'Subscription data has been changed.'
                user.addSubscriptionInFolder(self)

        return self._returnWithMessage(message, REQUEST)
        return


InitializeClass(SubscriptionFolder)

class SubscribedUser(Persistent):
    """
        Class describing users who have been subscribed.
    """
    __module__ = __name__
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, email='', lname='', fname='', mname='', company_name='', position='', company_business_activity='', contact='', phones='', post_address='', account_manager=None, secret_code=None):
        """
            Create user with given data.

            Arguments:

                'email' -- user email

                'lname' -- last name

                'fname' -- first name

                'mname' -- middle name

                'company_name' -- company title

                'position' -- user's job

                'company_business_activity' -- branch in which company works

                'contact' -- contact name

                'phones' -- phones

                'post_address' -- post address

                'account_manager' -- account manager (NauDoc's user, who
                    subscribed this user)

                'secret_code' -- secret code to confirm subscription

        """
        self.email = email
        self.lname = lname
        self.fname = fname
        self.mname = mname
        self.company_name = company_name
        self.position = position
        self.company_business_activity = company_business_activity
        self.contact = contact
        self.phones = phones
        self.post_address = post_address
        self.account_manager = account_manager
        self.subscribed_folders = PersistentMapping()
        if secret_code is None:
            self._isPending = None
            self.secret_code = None
            self.pendingDate = None
        else:
            self._isPending = 1
            self.secret_code = secret_code
            self.pendingDate = DateTime() + 30
        self._isUnsubscribed = None
        self.URLToUnsubscribe = ''
        return

    def isPendingTooLong(self):
        """
            Checks if pending time for confirmation has expired.
        """
        if self.pendingDate is not None and self.pendingDate < DateTime():
            return 1
        return 0
        return

    def isPending(self):
        """
            Cheeck if user is pending (did not confirmed subscription yet).
        """
        return self._isPending
        return

    def getInitials(self):
        """
            Returns string with lname, fname, mname.
        """
        result = '%s %s' % (self.lname, self.fname)
        result = result.strip()
        if result:
            result = '%s %s' % (result, self.mname)
        return result.strip()
        return

    def setURLToUnsubscribe(self, newURL):
        """
            Set unsubscribe Url.

            We cannot use just absolute or external url of root to send in
            emails because when called with portal_scheduler it does not work.

            Arguments:

                'newURL' -- url that user have to visit to unsubscribe
        """
        self.URLToUnsubscribe = newURL
        return

    def isUnsubscribed(self):
        """
            Returns state - is user subscribed or not.

            Result:

                Boolean.
        """
        return self._isUnsubscribed
        return

    def renewSubscription(self):
        """
            Renews subscription of user.

            He will receive mail again.
        """
        self._isUnsubscribed = None
        return

    def discontinueSubscription(self):
        """
            Stops subscription of user.

            He will not receive mail any more.
        """
        self._isUnsubscribed = 1
        return

    def edit(self, lname='', fname='', mname='', company_name='', position='', company_business_activity='', contact='', phones='', post_address='', account_manager=None):
        """
            Changes whole the user's data.

            Arguments:

                see __init__() for details
        """
        self.lname = lname
        self.fname = fname
        self.mname = mname
        self.company_name = company_name
        self.position = position
        self.company_business_activity = company_business_activity
        self.contact = contact
        self.phones = phones
        self.post_address = post_address
        self.account_manager = account_manager
        return

    def addSubscriptionInFolder(self, folder):
        """
            Stores uid of given folder - subscribes user in that folder.

            Arguments:

                'folder' -- SubscriptionFolder instance.
        """
        self.subscribed_folders.setdefault(folder.getUid(), 1)
        return

    def setSubscriptionInFolders(self, folders_uids_list):
        """
            Set uids of folders where user is subscribed. Replace old folders uids with given.

            Arguments:

                'folders_uids_list' -- list of nd_uids of SubscriptionFolders
        """
        subscribed_folders = PersistentMapping()
        for uid in folders_uids_list:
            subscribed_folders[uid] = 1

        self.subscribed_folders = subscribed_folders
        return

    def listSubscribedFolders(self):
        """
            Returns list with folders uids.
        """
        return self.subscribed_folders.keys()
        return

    def isSubscribedToFolder(self, folder_or_uid=None):
        """
            Checks if users is subscribed in given folder.
            Note: does not checks parents of the folder.

            Arguments:

                'folder_or_uid' -- Either SubscriptionFolder or nd_uid.

            Result:

                Boolean.
        """
        folder_uid = folder_or_uid
        if isinstance(folder_or_uid, SubscriptionFolder):
            folder_uid = folder_or_uid.getUid()
        return not self.isUnsubscribed() and self.subscribed_folders.has_key(folder_uid)
        return

    def asVocabulary(self):
        """
            Returns user data as dictionary.
        """
        return {'email': (self.email), 'lname': (self.lname), 'fname': (self.fname), 'mname': (self.mname), 'company_name': (self.company_name), 'position': (self.position), 'company_business_activity': (self.company_business_activity), 'contact': (self.contact), 'phones': (self.phones), 'post_address': (self.post_address), 'account_manager': (self.account_manager), 'subscribed_folders': (self.listSubscribedFolders()), 'aborted': (self._isUnsubscribed)}
        return

    def makeActive(self):
        """
            Makes user active (he becomes subscribed).
        """
        self._isPending = None
        self.secret_code = None
        self.pendingDate = None
        return


def addSubscription(self, id, title='', REQUEST=None, **kwargs):
    """
        Adds a new object.
    """
    if id != 'subscriptions':
        raise SimpleError(message="Please set only 'subscriptions' id")
    assert isinstance(self, FactoryDispatcher), 'FactoryDispatcher expected'
    destination = self.Destination()
    if destination.implements('isPrincipiaFolderish') and destination.getId() == 'storage' and destination.parent().implements('isSiteRoot'):
        self._setObject(id, Subscription(id, title, **kwargs), set_owner=0)
        item = self._getOb(id)
        item.redirect(action='folder_edit_form', message='Subscription root added.', REQUEST=REQUEST)
    else:
        raise SimpleError(message='Subscription Root may be placed only in storage of external site container')
    return


class Subscription(SubscriptionFolder):
    """
        Subscription Folders hierarchy root class.

        Provides all functionality for subscriptions.
    """
    __module__ = __name__
    _class_version = 2.0
    meta_type = 'Subscription Root'
    portal_type = 'Subscription Root'
    __implements__ = (
     Features.isSubscriptionRoot, SubscriptionFolder.__implements__)
    __unimplements__ = (
     Features.isCategorial,)
    security = ClassSecurityInfo()
    _actions = ()
    _properties = ({'id': 'mail_from_name', 'type': 'string', 'mode': 'w'}, {'id': 'mail_from_address', 'type': 'string', 'mode': 'w'}, {'id': 'subject_header', 'type': 'string', 'mode': 'w'})

    def __init__(self, id, title=None, **kwargs):
        """
            Constructs instance
        """
        SubscriptionFolder.__init__(self, id, title, **kwargs)
        self._users = OOBTree()
        self.subject_header = 'Subscription'
        self.mail_from_name = 'subscriptions'
        self.mail_from_address = 'subscribe@localhost'
        self.sendMailTempExpr = None
        self.sendMailTaskID = None
        return

    security.declareProtected(Permissions.SubscribeUsers, 'getUser')

    def getUser(self, email):
        """
            Returns SubscribedUser for given email or None if user does not exists.
        """
        return self._users.get(email)
        return

    def listAllUsers(self):
        """
            Returns list of all users (SubscribedUser instances).
        """
        return self._users.values()
        return

    def listUsersFor(self, context, include_from_top=1, _want_dict=None):
        """
            Returns users subsctibed in given context.

            Note: if context is self, empty list (dictionary) is returned.

            Arguments:

                'context' -- SubscriptionFolder instance.

                'include_from_top' -- If set, append all users subscribed in
                                        parent fodlers.

                '_want_dict' -- If set, return dictionary rather than list.
            Result:

                List of SubscribedUser instances or
                dictionary where keys are emails and values are SubscribedUser
                instances.
        """
        if context is self:
            if _want_dict:
                return {}
            return []
        result = {}
        for user in self.listAllUsers():
            if user.isPending():
                continue
            if user.isSubscribedToFolder(context):
                result[user.email] = user

        if include_from_top:
            result.update(self.listUsersFor(context.parent(), include_from_top, _want_dict=1))
        if _want_dict:
            return result
        return result.values()
        return

    security.declareProtected(Permissions.SubscribeUsers, 'listUsersMappingsFor')

    def listUsersMappingsFor(self, context=None):
        """
            Goes up from folder to self (root) and collects all users subscribed on those folders.

            Returns list of users propertis (as dictionary).

            Arguments:

                'folder' -- SubscriptionFolder from which to start (if None -
                    returns all users).

            Result:

                List of dictionaries.
        """
        if context is self:
            users = self.listAllUsers()
        else:
            users = self.listUsersFor(context, _want_dict=0)
        return [_[1] for x in users]
        return

    def delUser(self, email):
        """
            Completely removes user from subscription.
        """
        if self.getUser(email):
            del self._users[email]
            self._p_changed = 1
        return

    def getAccountManager(self):
        """
            Returns username of currently logged in user or None if user is not portal member.
        """
        membership = getToolByName(self, 'portal_membership')
        if not membership.isAnonymousUser():
            return membership.getAuthenticatedMember().getUserName()
        return None
        return

    def createUser(self, email, *args, **kw):
        """
            Creates new SubscribedUSer and copies given data.
        """
        user = SubscribedUser(email, *args, **kw)
        self._users[email] = user
        self._p_changed = 1
        return user
        return

    def _listAllUsersForSelf(self):
        """
            The only goal of this method is to encapsulate the way of getting
            subscribed users (the same way for Subscription and
            SubscriptionFolder).

            Helper method.
            Used to overcome listUsersFor() - it does not work properly with Subscription Root.

            Returns list of all subscribed users.

        """
        result = []
        for user in self.listAllUsers():
            if not (user.isPending() or user.isUnsubscribed()):
                result.append(user)

        return result
        return

    security.declareProtected(Permissions.SubscribeUsers, 'listSubscribedUsers')

    def listSubscribedUsers(self):
        """
            Returns mappings of all subscribed users except pending.

            Result:

                List of dictionaries.
        """
        result = []
        for user in self.listAllUsers():
            if not user.isPending():
                result.append(user.asVocabulary())

        return result
        return

    security.declareProtected(CMFCorePermissions.View, 'getSubscribedUser')

    def getSubscribedUser(self, email=None):
        """
            Returns subscribed user data having given email.

            Used on external site.

            Arguments:

                'email' -- user's email
        """
        user = self.getUser(email)
        if user is not None:
            return user.asVocabulary()
        return {}
        return

    def _checkPendingUsers(self):
        """
            Removes users pending too long.
        """
        for user in self.listAllUsers():
            if user.isPendingTooLong():
                self.delUser(user.email)

        return

    def isValidEmail(self, email):
        """
            Return true if email is valid.
        """
        if email.find('@') < 0:
            return 0
        return 1
        return

    security.declareProtected(CMFCorePermissions.View, 'edit_user')

    def edit_user(self, email, publisher=None, REQUEST=None):
        """
            Edits user data.

            Arguments:

                'email' -- email

                'publisher' -- True means that this method being called from
                    NauPublishTool.

                'REQUEST' -- REQUEST object

            Result:

                String or redirect.
        """
        if REQUEST is None:
            raise ValueError, 'REQUEST missing'
        r = REQUEST.get
        user = self.getUser(email)
        if user is None:
            return self.subscribe(email, publisher, REQUEST)
        user.edit(r('lname', ''), r('fname', ''), r('mname', ''), r('company_name', ''), r('position', ''), r('company_business_activity', ''), r('contact', ''), r('phones', ''), r('post_address', ''), self.getAccountManager())
        user.setSubscriptionInFolders(r('folders_to_subscribe', []))
        unsubscription_url = self.getServerUrl(REQUEST) + self.external_url(1, action='subscription', params={'action': 'unsubscribe', 'email': (user.email)})
        user.setURLToUnsubscribe(unsubscription_url)
        if r('renewSubscription'):
            user.renewSubscription()
        self._returnWithMessage('Data has been changed.', REQUEST, publisher)
        return

    security.declareProtected(CMFCorePermissions.View, 'subscribe')

    def subscribe(self, email, publisher=None, REQUEST=None):
        """
            Subscribes new user (remembers him and sends confirmation email).

            Arguments:

                'email' -- user email

                'publisher' -- True means that this methos being called from
                    NauPublishTool.

                'REQUEST' -- REQUEST object
        """
        if REQUEST is None:
            raise ValueError, 'REQUEST missing'
        r = REQUEST.get
        folders_to_subscribe = r('folders_to_subscribe', [])
        user = self.getUser(email)
        try:
            if not self.isValidEmail(email):
                raise SimpleError, 'Invalid email address.'
            if not folders_to_subscribe:
                raise SimpleError, 'Please select at least one folder.'
            if user is not None:
                if user.isPending():
                    self.delUser(email)
                else:
                    raise SimpleError, 'User with such email exists.'
        except SimpleError, message:
            return self._returnWithMessage(message, REQUEST, publisher)

        secret_code = str(int(DateTime()))
        user = self.createUser(email, r('lname', ''), r('fname', ''), r('mname', ''), r('company_name', ''), r('position', ''), r('company_business_activity', ''), r('contact', ''), r('phones', ''), r('post_address', ''), self.getAccountManager(), secret_code)
        user.setSubscriptionInFolders(folders_to_subscribe)
        subscription_url = self.getServerUrl(REQUEST) + self.external_url(1, action='subscription', params={'action': 'confirm', 'email': email, 'secret_code': secret_code})
        self._checkPendingUsers()
        if r('dont_notify'):
            return self.confirm_subscription(email, secret_code, dont_send=1, publisher=publisher, REQUEST=REQUEST)
        titles = []
        for folder in self._listSubscriptableFolders(self, recursive=1):
            if folder.getUid() in folders_to_subscribe:
                titles.append((folder.title_or_id(), folder.Description()))

        res = self._sendMessage(email, full_message=self._createMessageText(self.mailings_on, REQUEST=REQUEST, headings_titles=titles, subscription_url=subscription_url, lang=getToolByName(self, 'msg').get_selected_language()))
        if publisher or REQUEST is None:
            return 'Your request processed. Check your e-mail and confirm subscription.'
        else:
            return self.redirect(action='folder', message='Your request processed. Now user have to confirm subscription.', REQUEST=REQUEST)
        return

    security.declareProtected(CMFCorePermissions.View, 'confirm_subscription')

    def confirm_subscription(self, email, secret_code, REQUEST=None, publisher=None, dont_send=None):
        """
            Completes subscription of user and sends confirmation email meesge.

            Arguments:

                'email' -- user email

                'secret_code' -- Secret code. If matched earlier generated,
                    subscription of user will be confirmed.

                'REQUEST' -- REQUEST object

                'publisher' -- True means that this methos being called from
                    NauPublishTool.

                'dont_send' -- If false, send email message to user.

             Result:

                String.
        """
        status = 'You have been subscribed.'
        uname = email
        user = self.getUser(email)
        if user is not None and user.secret_code == str(secret_code):
            user.makeActive()
            unsubscription_url = self.getServerUrl(REQUEST) + self.external_url(1, action='subscription', params={'action': 'unsubscribe', 'email': (user.email)})
            user.setURLToUnsubscribe(unsubscription_url)
        else:
            return self._returnWithMessage('You have not been signed up. Try to subscribe again.', REQUEST, publisher)
        if dont_send is None:
            titles = []
            for folder in self._listSubscriptableFolders(self, recursive=1):
                if user.isSubscribedToFolder(folder):
                    titles.append((folder.title_or_id(), folder.Description()))

            edit_props_url = self.getServerUrl(REQUEST) + self.getSubscription().external_url(1)
            self._sendMessage(user.email, full_message=self._createMessageText(self.mailings_confirm, REQUEST=REQUEST, headings_titles=titles, subscription_url=user.URLToUnsubscribe, lang=getToolByName(self, 'msg').get_selected_language(), edit_props_url=edit_props_url))
        return self._returnWithMessage(status, REQUEST, publisher)
        return

    security.declareProtected(CMFCorePermissions.View, 'unsubscribe_users')

    def unsubscribe_users(self, remove_users=[], REQUEST=None):
        """
            Unsubscribes users given in remove_users.

            For each users calls self.unsubscribe().

            Arguments:

                'remove_users' -- list of email to insubscribe

                'REQUEST' -- REQUEST object

            Result:

                String.
        """
        result = 'No users have been removed.'
        for email in remove_users:
            result = self.unsubscribe(email, REQUEST)
        else:
            return self._returnWithMessage(result, REQUEST)

        return result
        return

    security.declareProtected(CMFCorePermissions.View, 'unsubscribe')

    def unsubscribe(self, email=None, REQUEST=None, publisher=None):
        """
            Unsubscribe user.

            Arguments:

                'email' -- user email

                'REQUEST' -- REQUEST object

                'publisher' -- True means that this methos being called from
                    NauPublishTool.

            Result:

                String.
        """
        user = self.getUser(email)
        if user is not None:
            user.discontinueSubscription()
        else:
            return self._returnWithMessage('You are not subscribed.', REQUEST, publisher)
        edit_props_url = self.getServerUrl(REQUEST) + self.getSubscription().external_url(1)
        self._sendMessage(email, full_message=self._createMessageText(self.mailings_off, REQUEST=REQUEST, heading_title='', lang=getToolByName(self, 'msg').get_selected_language(), edit_props_url=edit_props_url))
        return self._returnWithMessage('You have been unsubscribed.', REQUEST, publisher)
        return

    security.declareProtected(CMFCorePermissions.View, 'loginSubscribed')

    def loginSubscribed(self, email, REQUEST):
        """
            Sets cookie for session to access mail archieve.

            If not user with given email, returns error message.
            Arguments:

                'email' -- email of user

                'REQUEST' -- REQUEST object

            Result:

                String.
        """
        user = self._users.get(email)
        if user is None:
            return 'User with such email not found.'
        REQUEST.RESPONSE.setCookie('subscribed_email', email)
        return ''
        return

    def getSendInterval(self):
        """TODO:"""
        return self.sendMailTempExpr and self.sendMailTempExpr.days or 0
        return

    def getSendMinute(self):
        """TODO:"""
        return self.sendMailTempExpr and self.sendMailTempExpr.minute or 0
        return

    def getSendHour(self):
        """TODO:"""
        return self.sendMailTempExpr and self.sendMailTempExpr.hour or 0
        return

    security.declareProtected(CMFCorePermissions.ManageProperties, 'manage_changeProperties')

    def manage_changeProperties(self, REQUEST=None, **kw):
        """
            Changes existing object properties.
        """
        (from_name, from_addr, subject_header) = extractParams(kw, REQUEST, 'mail_from_name', 'mail_from_address', 'subject_header')
        if from_name is not None:
            self.mail_from_name = from_name
        if from_addr is not None:
            self.mail_from_address = from_addr
        self.subject_header = subject_header
        (send_h, send_m, send_i) = extractParams(kw, REQUEST, 'send_hour', 'send_minute', 'send_interval')
        if send_i:
            self.sendMailTempExpr = DailyTE(hour=send_h % 24, minute=send_m % 60, second=0, days=abs(send_i))
        scheduler = getToolByName(self, 'portal_scheduler')
        schedule_element = None
        try:
            schedule_element = scheduler.getScheduleElement(self.sendMailTaskID)
        except:
            pass

        if self.sendMailTempExpr:
            if schedule_element:
                schedule_element.setTemporalExpression(self.sendMailTempExpr)
            else:
                self.sendMailTaskID = scheduler.addScheduleElement(self.sendMail, self.sendMailTempExpr, title='Check and dispatch queued documents task (subscription)')
        return

    def _instance_onDestroy(self):
        """
            Kills scheduled tasks.
        """
        scheduler = getToolByName(self, 'portal_scheduler')
        try:
            scheduler.delScheduleElement(self.sendMailTaskID, force=1)
        except:
            pass

        return

    security.declarePublic('listSubscriptableFolders')

    def listSubscriptableFolders(self, parent_path=None):
        """
            TODO
            used in dtml
        """
        result = []
        for folder in self._listSubscriptableFolders(parent_path, recursive=0):
            result.append({'absolute_url': (folder.absolute_url(1)), 'title_or_id': (folder.title_or_id()), 'Description': (folder.Description()), 'uid': (folder.getUid())})

        return result
        return

    def _listSubscriptableFolders(self, parent_or_path=None, recursive=0):
        """
            TODO
        """
        parent = parent_or_path or self
        if isinstance(parent, StringType):
            parent = self.unrestrictedTraverse(parent_or_path)
        children = parent.objectValues('Subscription Folder')
        result = []
        for child in children:
            result.append(child)
            if recursive:
                result.extend(self._listSubscriptableFolders(child, recursive))

        return result
        return

    security.declareProtected(CMFCorePermissions.View, 'getSubscriptionObject')

    def getSubscriptionObject(self):
        """
            Returns this Subscription object

            Result:

                Subscription
        """
        return self
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'importFromCSV')

    def importFromCSV(self, csv_file=None, ignore_titles=None, folders_to_subscribe=None, REQUEST=None):
        raise NotImplementedError
        return


InitializeClass(Subscription)

def initialize(context):
    context.registerContent(SubscriptionFolder, addSubscriptionFolder, SubscriptionFolderType)
    context.registerContent(Subscription, addSubscription, SubscriptionRootType)
    return
