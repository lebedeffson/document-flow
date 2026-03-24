# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/SiteObject/NauPublishTool.py
# Compiled at: 2008-10-15 16:48:07
"""
NauSite publisher.

$Editor: vpastukhov $
$Id: NauPublishTool.py,v 1.1 2008/10/15 12:48:07 oevsegneev Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
from sys import exc_info
from types import StringType
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base, aq_inner, aq_parent
from DocumentTemplate.DT_HTML import HTML
from Globals import DTMLFile
from OFS.SimpleItem import SimpleItem
from ZPublisher.BeforeTraverse import NameCaller, registerBeforeTraverse, queryBeforeTraverse
from zLOG import LOG, TRACE, INFO
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain
from Products.CMFNauTools import Config
from Products.CMFNauTools.Exceptions import Unauthorized
from Products.CMFNauTools.Features import createFeature
from Products.CMFNauTools.SimpleObjects import InstanceBase, ToolBase
from Products.CMFNauTools.Utils import InitializeClass, joinpath, MethodTypes, getObjectImplements
NauPublisherType = {'id': 'Publisher Entry Point', 'meta_type': 'Publisher Entry Point', 'description': 'Publisher Entry Point fetches published documents for the external site', 'icon': 'publisher.gif', 'product': 'CMFNauTools', 'factory': 'manage_addPublisherEP', 'filter_content_types': 0, 'immediate_view': 'view', 'disallow_manual': 1}

class NauPublishTool(ToolBase, SimpleItem):
    """
        NauSite Publisher Tool
    """
    __module__ = __name__
    _class_version = 1.93
    meta_type = 'NauSite Publisher Tool'
    id = 'portal_publisher'
    zeohost = ''
    zeoport = 0
    default_repository = ''
    soft_links = []
    security = ClassSecurityInfo()
    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainPublishTool', globals())
    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_external')
    manage_external = DTMLFile('dtml/setupExternalSites', globals())
    manage = manage_main = DTMLFile('dtml/setupZEOSyncer', globals())
    manage_main._setName('manage_main')
    manage_options = ({'label': 'ZEOSyncer', 'action': 'manage_main'}, {'label': 'External sites', 'action': 'manage_external'}, {'label': 'Overview', 'action': 'manage_overview'}) + ToolBase.manage_options + SimpleItem.manage_options

    def __init__(self):
        """ Initialize class instance
        """
        ToolBase.__init__(self)
        self.default_repository = 'PORTAL_ROOT/external'
        self.soft_links = ['portal_skins/custom', 'portal_skins/images']
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'editZEOProperties')

    def editZEOProperties(self, zeohost='localhost', zeoport=0, REQUEST=None):
        """
          Form handler for the publisher settings
        """
        msg = 'Tool updated.'
        self.zeohost = zeohost
        self.zeoport = zeoport
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message=msg, management_view='ZEOSyncer')
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'get_repository')

    def get_repository(self):
        """
            Return the path to the default sites repository
        """
        default_repository = self.default_repository.replace('PORTAL_ROOT', '/' + self.portal_url(1))
        return default_repository
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'editExternalProperties')

    def editExternalProperties(self, soft_links='', default_repository='', REQUEST=None):
        """
            Form handler for the publisher settings
        """
        msg = 'Tool updated.'
        self.soft_links = soft_links
        rendered_repository = default_repository.replace('PORTAL_ROOT', '/' + self.portal_url(1))
        try:
            folder = self.restrictedTraverse(rendered_repository)
            if not getattr(folder, 'isPrincipiaFolderish', 0):
                raise ValueError, '%s is not a valid CMF folder' % rendered_repository
            self.default_repository = default_repository
        except:
            msg = '%s is not a valid CMF folder' % default_repository

        if REQUEST is not None:
            return self.manage_external(self, REQUEST, manage_tabs_message=msg, management_view='External sites')
        return


InitializeClass(NauPublishTool)

class NauPublisher(InstanceBase):
    """
      Publisher Entry Point

      Allows site visitors to access published content
    """
    __module__ = __name__
    _class_version = 1.93
    meta_type = 'Publisher Entry Point'
    __implements__ = (
     createFeature('isPublisher'), InstanceBase.__implements__)
    isPrincipiaFolderish = 1
    manage_options = ({'label': 'Publisher settings', 'action': 'manage_main'},) + InstanceBase.manage_options
    security = ClassSecurityInfo()
    security.setDefaultAccess(1)
    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_main')
    manage = manage_main = DTMLFile('dtml/setupPublisherEP', globals())
    manage_main._setName('manage_main')
    index_html = None
    internal = ''

    def __init__(self, id, title=None, internal=''):
        """ Initialize class instance
        """
        InstanceBase.__init__(self, id, title=title)
        self.internal = internal
        return

    def __before_publishing_traverse__(self, self2, REQUEST=None):
        path = REQUEST['TraversalRequestNameStack']
        subpath = path[:]
        path[:] = []
        subpath.reverse()
        REQUEST.set('traverse_subpath', subpath)
        return

    def __call__(self, REQUEST, **kw):
        """
          Returns the requested document or the published items list
        """
        traverse_subpath = REQUEST['traverse_subpath']
        path = joinpath(self.getSiteUrl(), traverse_subpath)
        result = None
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('SiteObject'):
            msg = getToolByName(self, 'msg')
            return msg('sentinel.trial_expired') % msg('"Site" object type')
        try:
            result = self.fetchObject(path, REQUEST)
        except (AttributeError, KeyError):
            LOG('NauPublisher', INFO, 'path=%s' % path, error=exc_info())
            result = self.site_error_message(self, REQUEST, path=path)
        except (Unauthorized, 'Unauthorized'):
            REQUEST['RESPONSE'].unauthorized()

        return result
        return

    security.declarePublic('heading_absolute_url')

    def heading_absolute_url(self, subpath=None):
        """ """
        if subpath is None:
            subpath = self.REQUEST.get('traverse_subpath', [])
        while subpath:
            path = joinpath(self.internal, subpath)
            search_args = {'state': 'published', 'path': path, 'sort_on': 'Date', 'sort_order': 'reverse'}
            catalog = getToolByName(self, 'portal_catalog')
            results = apply(catalog.searchResults, (), search_args)
            if results:
                break
            subpath = subpath[:-1]

        return joinpath(subpath)
        return

    security.declarePublic('heading_external_url')

    def heading_external_url(self, subpath=None):
        """ """
        headingPath = self.absolute_url() + '/' + self.heading_absolute_url(subpath)
        return headingPath
        return

    security.declarePublic('maxNumOfPages')

    def maxNumOfPages(self):
        """
          returns maximum number of pages
        """
        headingPath = self.getSiteUrl() + '/' + self.heading_absolute_url()
        heading = self.unrestrictedTraverse(headingPath)
        maxNumOfPage = heading.getMaxNumberOfPages()
        return maxNumOfPage
        return

    security.declarePublic('archiveProperty')

    def archiveProperty(self):
        """
          returns virtual archive property
        """
        headingPath = self.getSiteUrl() + '/' + self.heading_absolute_url()
        heading = self.unrestrictedTraverse(headingPath)
        return heading.getArchiveProperty()
        return

    security.declarePublic('publishedItems')

    def publishedItems(self, subpath=None, exact=False, meta_types=(), features=(), exclude_main=False):
        """
          Return the list of the published items
        """
        headingPath = self.getSiteUrl() + '/' + self.heading_absolute_url(subpath)
        heading = self.unrestrictedTraverse(headingPath, None)
        if heading is None:
            return
        items = []
        for item in heading.listPublications(exact, meta_types, features):
            if exclude_main and heading.main_page == item['nd_uid']:
                continue
            items.append({'absolute_url': (self.external_url(item)), 'meta_type': (item['meta_type']), 'id': (item['id']), 'Title': (item['Title']), 'Title_or_id': (item['Title'] or item['id']), 'Description': (item['Description']), 'Date': (item['Date']), 'EffectiveDate': (item['EffectiveDate']), 'CreationDate': (item['CreationDate']), 'isIndexDocument': (heading.main_page == item['nd_uid'])})
            if heading.implements('isStorefront'):
                doc = item.getObject()
                items[-1]['product_title'] = doc.getCategoryAttribute('product_title', '')
                items[-1]['product_description'] = doc.getCategoryAttribute('product_description', '')
                items[-1]['product_price'] = doc.getCategoryAttribute('product_price', '')
                if 'photo.gif' in map((lambda x: x[0]), doc.listAttachments()):
                    items[-1]['photo'] = items[-1]['absolute_url'] + '/photo.gif'

        return items
        return

    security.declarePublic('boxView')

    def boxView(self, REQUEST=None):
        """           Box view
        """
        if REQUEST is not None:
            return self.listBoxForm(self, REQUEST)
        return

    security.declarePublic('getPublisher')

    def getPublisher(self):
        """
           Return context of publisher (to get site root in subdocuments)
        """
        return self
        return

    this = getPublisher
    security.declarePublic('getSite')

    def getSite(self):
        """
          Return the internal site object
        """
        site_url = self.getSiteUrl()
        site = self.unrestrictedTraverse(site_url, None)
        return site.aq_parent
        return

    security.declarePublic('getSiteUrl')

    def getSiteUrl(self):
        """
          Return the path to the internal site
        """
        if self.internal == 'self':
            return joinpath(self.portal_url.getPortalObject().getPhysicalPath())
        return self.internal
        return

    security.declarePublic('getParents')

    def getParents(self, subpath=None):
        """
          Return the list of item's containers
        """
        if subpath is None:
            subpath = self.REQUEST.get('traverse_subpath', [])
        site = aq_parent(aq_inner(self))
        parents = []
        pathlen = len(subpath)
        level = 1
        while level <= pathlen:
            if level == pathlen:
                parent = getattr(site, subpath[-1], None)
                if not (parent is None or parent.aq_inContextOf(site)):
                    parent = None
            else:
                parent = None
            if parent is None:
                path = joinpath(self.getSiteUrl(), subpath[:level])
                parent = self.unrestrictedTraverse(path, None)
                if parent is None:
                    break
            if parent.title or level == pathlen:
                parents.insert(0, {'absolute_url': (parent.external_url()), 'meta_type': (parent.meta_type), 'title': (parent.title), 'title_or_id': (parent.title_or_id()), 'Description': (parent.Description()), 'id': (parent.getId())})
                if getObjectImplements(parent, 'isVersionable'):
                    break
            level += 1

        parents.reverse()
        return parents
        return

    security.declareProtected(CMFCorePermissions.View, 'listSubFolders')

    def listSubFolders(self, subpath=None):
        """
          Return folders list
        """
        headingPath = joinpath(self.getSiteUrl(), self.heading_absolute_url(subpath))
        internal_folder = self.unrestrictedTraverse(headingPath, None)
        if internal_folder is None:
            return
        results = internal_folder.getPublishedFolders()
        return results
        return

    security.declareProtected(CMFCorePermissions.View, 'getHeading')

    def getHeading(self, subpath=None):
        """ Returns heading, specified by subpath """
        headingPath = self.getSiteUrl() + '/' + self.heading_absolute_url(subpath)
        internal_folder = self.unrestrictedTraverse(headingPath, None)
        return internal_folder
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'editProperties')

    def editProperties(self, REQUEST=None):
        """
          Forms handler for the publisher settings
        """
        msg = 'Tool updated.'
        if REQUEST.has_key('title'):
            self.title = REQUEST['title']
        if REQUEST.has_key('internal'):
            internal = REQUEST['internal']
            if internal == 'self':
                self.internal = internal
            else:
                try:
                    internal_site = self.restrictedTraverse(internal)
                    if not internal_site.hasProperty('publishers'):
                        internal_site.manage_addProperty('publishers', '', 'lines')
                    publishers = internal_site.publishers
                    my_url = joinpath(self.getPhysicalPath())
                    if my_url not in tuple(publishers):
                        publishers.append(my_url)
                        internal_site.manage_changeProperties(publishers=publishers)
                    self.internal = internal
                except:
                    msg = '%s is not a valid CMF Site' % internal

        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message=msg)
        return

    security.declarePrivate('fetchObject')

    def fetchObject(self, path, REQUEST=None):
        """
            Fetches the published object from the internal site
        """
        base_path = path.split('/')
        if base_path[-1] in ('view',):
            base_path = base_path[:-1]
        o_id = base_path[-1]
        object = self.restrictedTraverse(o_id, None)
        method = None
        if object is not None:
            site = aq_parent(aq_inner(self))
            if type(object) in MethodTypes:
                method = object
                object = method.im_self
            try:
                if object.aq_inContextOf(site) and hasattr(aq_base(site), object.getId()):
                    if method is None:
                        method = hasattr(aq_base(object), 'index_html') and object.index_html or None
                    if not (method is None and callable(object) or callable(method)):
                        object = None
                else:
                    object = None
            except AttributeError:
                object = None

        if object is not None:
            if method is None:
                return object(self, REQUEST=REQUEST)
            if method.__name__ == 'index_html':
                return method(REQUEST, REQUEST.RESPONSE)
            return method(REQUEST=REQUEST)
        internal_object = self.unrestrictedTraverse(joinpath(base_path))
        method = None
        if type(internal_object) in MethodTypes:
            if not getSecurityManager().validate(None, internal_object.im_self, None, internal_object):
                raise Unauthorized
            return internal_object(REQUEST)
        if getObjectImplements(internal_object, 'isPrincipiaFolderish') and getObjectImplements(internal_object, 'isPublishable'):
            main_page = internal_object.getMainPage()
            if main_page is not None:
                internal_object = main_page
            else:
                method = self.listPublishedForm
        if isinstance(internal_object, HTML) or getObjectImplements(internal_object, 'isDocTemp'):
            method = internal_object
        object = self._setExternalContext(internal_object)
        if method is not None:
            return method(object, REQUEST, **REQUEST.form)
        if object.index_html is None:
            return object()
        return object.index_html(REQUEST, REQUEST.RESPONSE, **REQUEST.form)
        return

    security.declarePublic('getPresentedDocuments')

    def getPresentedDocuments(self, level=1, main=None, subpath=None):
        """
            DEPRECATED: use getLastPresentedDocument or listPresentedDocuments instead
        """
        site = aq_base(self.getSite())
        if main or site.presentation_levels[level].get('max_count') == 1:
            return self.getLastPresentedDocument(level, subpath)
        else:
            return self.listPresentedDocuments(level, subpath)
        return

    security.declarePublic('listPresentedDocuments')

    def listPresentedDocuments(self, level, subpath=None):
        """
            Get all presented documents for the given level and subpath.
        """
        results = self.getSite()._findPresentedDocuments(level, subpath)
        return [_[1] for res in results]
        return

    security.declarePublic('getLastPresentedDocument')

    def getLastPresentedDocument(self, level, subpath=None):
        """
            Get last presented document for the given level and subpath.
        """
        results = self.getSite()._findPresentedDocuments(level, subpath)
        if not results:
            return None
        else:
            return self._setExternalContext(results[0].getObject())
        return

    security.declarePublic('getVoting')

    def getVoting(self):
        """
            Returns main voting object of site.
        """
        uid = aq_base(self.getSite()).voting
        if uid:
            ct = getToolByName(self, 'portal_catalog')
            result = ct.searchResults(path=self.getSiteUrl(), nd_uid=uid)
            if result:
                return self._setExternalContext(result[0].getObject())
        return None
        return

    def _setExternalContext(self, object):
        """
            Puts requested object in context of the external site
            and returns its acquisition wrapper.
        """
        if object.aq_inContextOf(self):
            return object
        parents = []
        parent = aq_parent(object)
        while parent is not None:
            if parent.implements('isSiteRoot'):
                break
            parents.append(parent)
            parent = aq_parent(parent)
        else:
            return None

        slot = self
        while len(parents):
            slot = aq_base(parents.pop()).__of__(slot)

        return aq_base(object).__of__(slot)
        return

    security.declarePublic('external_url')

    def external_url(self, item=None, path=None):
        """
          Apply new URL rules
        """
        if path is None:
            if item is None:
                return self.absolute_url()
            if isinstance(item, AbstractCatalogBrain):
                path = item.getPath()
            else:
                path = item.physical_path()
        base = self.getSiteUrl() + '/'
        if path.startswith(base):
            path = path[len(base):]
        return self.REQUEST.physicalPathToURL(joinpath(self.getPhysicalPath(), path))
        return

    security.declarePublic('subscription')

    def subscription(self, REQUEST=None):
        """
          Interface between external site users and heading
          subscription methods
        """
        r = REQUEST.get
        email = r('email', None)
        secret_code = r('secret_code', None)
        subpath = r('subpath', None) or r('traverse_subpath', [])[:-1]
        if type(subpath) is not StringType:
            subpath = joinpath(subpath)
        action = r('action', 'subscribe')
        result = 'Got empty email'
        path = self.getSiteUrl() + '/' + subpath
        redirect_str = '%s/%s' % (self.absolute_url(), subpath)
        ob = self.unrestrictedTraverse(path, None)
        if ob is not None:
            if not ob.implements('hasSubscription'):
                ob = ob.aq_parent
            if email:
                if action == 'subscribe':
                    result = ob.subscribe(email, 1, REQUEST)
                elif action == 'unsubscribe':
                    result = ob.unsubscribe(email, publisher=1)
                elif action == 'confirm' and secret_code:
                    result = ob.confirm_subscription(email, secret_code, REQUEST, 1)
                elif action == 'loginSubscribed':
                    result = ob.loginSubscribed(email, REQUEST)
                    redirect_str += result and '?portal_status_message=%s' % result or ''
                    return REQUEST.RESPONSE.redirect(redirect_str)
                elif action == 'change':
                    result = ob.edit_user(email, 1, REQUEST)
                    redirect_str += result and '?portal_status_message=%s' % result or ''
                    return REQUEST.RESPONSE.redirect(redirect_str)
        if REQUEST is not None:
            redirect_str += result and '?portal_status_message=%s' % result or ''
            REQUEST.RESPONSE.redirect(redirect_str)
        return

    security.declarePublic('subscriptableFolders')

    def subscriptableFolders(self, parent_path=None):
        """
          List all subscriptable folders
        """
        if parent_path is None:
            parent_path = joinpath(self.getSite().getSiteStorage().getPhysicalPath(), 'subscriptions')
        parent = self.unrestrictedTraverse(parent_path)
        if parent is None:
            return []
        result = []
        fldrs = parent.objectValues('Subscription Folder')
        for fldr in fldrs:
            result.append({'absolute_url': (fldr.absolute_url(1)), 'meta_type': (fldr.meta_type), 'title': (fldr.title), 'title_or_id': (fldr.title_or_id()), 'Description': (fldr.Description()), 'id': (fldr.getId()), 'uid': (fldr.getUid())})

        return result
        return

    security.declarePublic('getSubscribedUserInfo')

    def getSubscribedUserInfo(self, email):
        """
          Returns user info given by email
        """
        url = joinpath(self.getSite().getSiteStorage().getPhysicalPath(), 'subscriptions')
        subscr_root = self.unrestrictedTraverse(url)
        if subscr_root:
            return subscr_root.getSubscribedUser(email)
        else:
            return {}
        return

    def manage_afterAdd(self, item, container):
        InstanceBase.manage_afterAdd(self, item, container)
        if not queryBeforeTraverse(container, 'NauSiteTraverseHook'):
            registerBeforeTraverse(container, NameCaller('_nausite_traverseHook'), 'NauSiteTraverseHook')
        return


InitializeClass(NauPublisher)
manage_addNauPublisherForm = DTMLFile('dtml/addNauPublisher', globals())

def manage_addNauPublisher(self, id, title='', internal='', REQUEST=None):
    """       Add a new Publisher object with id *id*.
    """
    ob = NauPublisher(id, title, internal)
    self._setObject(id, ob)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url() + '/manage_main')
    return


def initialize(context):
    context.registerTool(NauPublishTool)
    context.registerContent(NauPublisher, manage_addNauPublisher, NauPublisherType)
    return
