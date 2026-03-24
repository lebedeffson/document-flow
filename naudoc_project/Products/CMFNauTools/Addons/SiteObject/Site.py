# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/SiteObject/Site.py
# Compiled at: 2008-12-19 18:26:58
"""
Container class for the external site.

$Editor: vpastukhov $
$Id: Site.py,v 1.3 2008/12/19 15:26:58 oevsegneev Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]
from cStringIO import StringIO
from copy import copy
from string import join
from types import StringType, ListType, TupleType
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from Acquisition import aq_base, aq_parent, aq_inner
from BTrees.IOBTree import IOBTree
from Globals import DTMLFile, HTML
from ZODB.PersistentList import PersistentList
from ZODB.PersistentMapping import PersistentMapping
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.Portal import PortalGenerator
import SiteImage, SubscriptionFolder, NauPublishTool
from Products.CMFNauTools import Config, Features, Exceptions
from Products.CMFNauTools import DTMLDocument, HTMLDocument
from Products.CMFNauTools import Storefront, TabularReport, Voting
from Products.CMFNauTools.ActionInformation import ActionInformation as AI
from Products.CMFNauTools.Config import Permissions, Roles
from Products.CMFNauTools.Heading import Heading, HeadingType
from Products.CMFNauTools.SiteAnnounce import SiteAnnounce
from Products.CMFNauTools.SyncableContent import SyncableRoot
from Products.CMFNauTools.Utils import cookId, InitializeClass, joinpath, splitpath, inheritActions, _checkPermission
SiteContainterType = {'id': 'Site Container', 'meta_type': 'Site Container', 'title': 'Site Container', 'description': 'External site container.', 'icon': 'site_icon.gif', 'sort_order': 0.9, 'product': 'CMFNauTools', 'factory': 'manage_addSiteContainer', 'factory_form': 'site_skin_change', 'permissions': (CMFCorePermissions.ManagePortal,), 'filter_content_types': 0, 'immediate_view': 'folder', 'condition': 'python: not object.getSite()', 'actions': (inheritActions(HeadingType, 'contents', 'view') + ({'id': 'edit', 'name': 'Site settings', 'action': 'site_edit_form', 'permissions': (CMFCorePermissions.ManageProperties,), 'category': 'object'}, {'id': 'bad_links', 'name': 'Find broken links', 'action': 'bad_links_form', 'permissions': (CMFCorePermissions.ListFolderContents,), 'category': 'object'}) + inheritActions(HeadingType, 'accessgroups'))}

class SiteContainer(Heading, SyncableRoot):
    """ Site Container class """
    __module__ = __name__
    _class_version = 1.84
    meta_type = 'Site Container'
    portal_type = 'Site Container'
    __implements__ = (
     Features.isSiteRoot, Heading.__implements__, SyncableRoot.__implements__)
    __unimplements__ = (
     Features.isContentStorage, Features.isCategorial)
    security = ClassSecurityInfo()
    managed_roles = Config.ManagedLocalRoles
    _properties = Heading._properties + SyncableRoot._properties + ({'id': 'home_page', 'type': 'string', 'mode': 'w'}, {'id': 'external_path', 'type': 'string', 'mode': 'w'}, {'id': 'publishers', 'type': 'lines', 'mode': 'w'})
    _actions = (
     AI(id='synchronize', title='Update remote site', action=Expression(text='string: ${object_url}/updateRemoteCopy'), category='object', permissions=(Permissions.UpdateRemoteObjects,), condition=Expression('python: object.checkRemoteParams()')),)
    updateRemoteCopy = SyncableRoot.updateRemoteCopy
    deleteRemoteCopy = SyncableRoot.deleteRemoteCopy
    _sync_reserved = SyncableRoot._sync_reserved + Heading._sync_reserved + ('external_path', 'announce_task')
    _sync_subobjects = Heading._sync_subobjects + ('announce_task',)
    security.declareProtected(CMFCorePermissions.ManageProperties, 'setSyncProperties')
    security.declareProtected(Permissions.UpdateRemoteObjects, 'updateRemoteCopy')
    security.declareProtected(Permissions.UpdateRemoteObjects, 'deleteRemoteCopy')
    home_page = ''
    external_path = None

    def _initstate(self, mode):
        """
            Initialize attributes
        """
        if not Heading._initstate(self, mode):
            return 0
        if not hasattr(self, 'presented_documents'):
            self.presented_documents = IOBTree()
        if not hasattr(self, 'presentation_levels'):
            self.presentation_levels = PersistentMapping()
            for level in range(len(Config.SitePresentationLevels)):
                self.presentation_levels[level] = Config.SitePresentationLevels[level]

        elif type(self.presentation_levels) is ListType:
            l = self.presentation_levels
            self.presentation_levels = PersistentMapping()
            for level in range(len(l)):
                self.presentation_levels[level] = l[level]

        for attr in ('primary_document', 'secondaryDocuments', 'lockedDocuments', 'locked_documents', 'locked_max_count', 'primary_max_count', 'secondary_max_count'):
            try:
                delattr(self, attr)
            except:
                pass

        if getattr(self, 'repository_url', None):
            self.external_path = joinpath(self.repository_url, self.getId())
            delattr(self, 'repository_url')
        if not hasattr(self, 'announce_task'):
            self.announce_task = SiteAnnounce(id='announce_task')
        if not hasattr(self, 'voting'):
            self.voting = None
        return 1
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setTitle')

    def setTitle(self, title):
        """ Dublin Core element - resource name
        """
        super(SiteContainer, self).setTitle(title)
        if aq_parent(self) is None:
            return
        external = self.getExternalRoot()
        if external is not None:
            external.setTitle(title)
        return

    security.declareProtected(CMFCorePermissions.View, 'getSiteObject')

    def getSiteObject(self):
        """ Return this site object
        """
        return self
        return

    security.declareProtected(CMFCorePermissions.View, 'getSiteStorage')

    def getSiteStorage(self):
        """ Return site storage object
        """
        return self._getOb(self.storage_id)
        return

    security.declareProtected(CMFCorePermissions.View, 'getExternalRootPath')

    def getExternalRootPath(self):
        """ Return physical path to external site root
        """
        return self.external_path
        return

    security.declarePublic('getExternalRootUrl')

    def getExternalRootUrl(self, relative=None):
        """ Return external site root URL
        """
        path = self.getExternalRootPath()
        request = getattr(self, 'REQUEST', None)
        if request is not None:
            root = request.get('VirtualRootPhysicalPath', None)
            if root:
                root_path = joinpath(root)
                if path.startswith(root_path):
                    path = path[len(root_path):]
            path = joinpath('', request._script, path)
        return path
        return

    security.declarePrivate('getExternalRoot')

    def getExternalRoot(self):
        """ Return external site object
        """
        portal = self.unrestrictedTraverse(self.getExternalRootPath(), None)
        return getattr(portal, '_isPortalRoot', 0) and portal or None
        return

    security.declareProtected(CMFCorePermissions.View, 'siteId')

    def siteId(self):
        """           Return site id
        """
        return self.getId()
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_addSiteContainer')

    def manage_addSiteContainer(self, id, title='', skin_links=[], storage_id='storage', repository_url='', sync_addr=None, sync_path=None, skin_id=None):
        """           Add a new SiteContainer object with id *id*.
        """
        repository = self.unrestrictedTraverse(repository_url, Missing)
        if repository is Missing:
            raise Exceptions.SimpleError, 'Repository not found'
        msg = getToolByName(self, 'msg')
        site_id = cookId(repository, str(id))
        site = SiteContainer(site_id, title)
        self._setObject(site_id, site)
        site = self._getOb(site_id)
        site.storage_id = storage_id
        site.external_path = joinpath(repository_url, site_id)
        site.manage_permission(Permissions.AddDTMLDocuments, (
         Roles.Manager, Roles.Owner, Roles.Author, Roles.Editor, Roles.Writer), 0)
        site.manage_addProduct['CMFNauTools'].manage_addHeading(id=storage_id, title=msg('Site content'))
        site.getSiteAnnounceObject().createTask()
        storage_url = joinpath(site.getPhysicalPath(), storage_id)
        gen = SiteGenerator()
        p = gen.create(site, repository, site_id, title, False)
        p.manage_addProduct['CMFNauTools'].manage_addNauPublisher(id='go', internal=storage_url)
        skins = getToolByName(p, 'portal_skins')
        site_skin = getToolByName(p, 'portal_site_skins')[skin_id]
        title_dict = {'custom': 'Skin design', 'images': 'Skin images'}
        for link in skin_links:
            link_id = link.split('/')[-1]
            site.manage_addProduct['CMFNauTools'].manage_addHeading(id=link_id, title=msg(title_dict.get(link_id, '')))
            folder = site[link_id]
            skins._objects += ({'id': link_id, 'meta_type': (folder.meta_type)},)
            skins._setOb(link_id, folder)
            folder.manage_addProperty('ext_link', link, 'text')
            defaults = getattr(site_skin, link_id, None)
            if not defaults:
                continue
            if link_id == 'custom':
                folder._reserved_names = (
                 'document_view', 'voting_view')
                for (id, value) in defaults.objectItems('Filesystem DTML Method'):
                    folder.manage_addProduct['CMFNauTools'].addDTMLDocument(id=id, title=id, file=value.document_src(), category='SimplePublication')

            elif link_id == 'images':
                for (id, value) in defaults.objectItems('Filesystem Image'):
                    folder.manage_addProduct['CMFNauTools'].addSiteImage(id=id, title=id, file=value._readFile(1), category='SimplePublication')
                    image = folder[id]
                    if hasattr(image, '_setPortalTypeName'):
                        image._setPortalTypeName('Site Image')

        site.publishSkins(comment='Published by NauSite')
        site.setSyncProperties(sync_addr, sync_path)
        site.updateRemoteCopy()
        return site_id
        return

    security.declarePrivate('publishSkins')

    def publishSkins(self, comment=None):
        """
            Publish skin object on newly created site.
        """
        workflow = getToolByName(self, 'portal_workflow')
        for folder in self.objectValues():
            for item in folder.objectValues():
                workflow.doActionFor(item, 'publish', comment=comment, sync=0)

        return

    def _instance_onCreate(self):
        return

    def _instance_onDestroy(self):
        self.getSiteAnnounceObject().delTask()
        portal = self.getExternalRoot()
        if portal is not None:
            repository = aq_parent(aq_inner(portal))
            portal._CMFCatalogAware__recurse = lambda *args: None
            try:
                repository.manage_delObjects(portal.getId())
            finally:
                del portal._CMFCatalogAware__recurse
        return

    def _instance_onClone(self, source, item):
        (repository_url, cmf_site_id) = splitpath(self.external_path)
        portal = self.getExternalRoot()
        if portal is None:
            return
        repository = aq_parent(aq_inner(portal))
        if not _checkPermission('Add CMF Sites', repository):
            raise Exceptions.CopyError, 'You have not enough permissions to create a Site.'
        new_id = 'copy_of_' + cmf_site_id
        while hasattr(aq_base(repository), new_id):
            new_id = 'copy_of_' + new_id

        repository.manage_clone(portal, new_id)
        self.external_path = joinpath(repository_url, new_id)
        portal = self.getExternalRoot()
        portal.internal_url = None
        portal._getOb('go').internal = None
        self.relink()
        return

    def _containment_onAdd(self, container, item):
        portal = self.getExternalRoot()
        if portal is not None:
            path = self.physical_path()
            portal.internal_url = path
            portal._getOb('go').internal = joinpath(path, 'storage')
        return

    def _containment_onDelete(self, container, item):
        portal = self.getExternalRoot()
        if portal is not None:
            portal.internal_url = None
            portal._getOb('go').internal = None
        return

    security.declareProtected(CMFCorePermissions.ManageProperties, 'setPresentationLevel')

    def setPresentationLevel(self, object, level=None):
        """
            Set new primary document of the current SiteContainer
        """
        uid = object.getUid()
        level = int(level or 0)
        docs = self.presented_documents
        changed = 0
        if level:
            uids = docs.get(level, PersistentList())
            if uid in uids:
                return
            for elem in docs.values():
                try:
                    elem.remove(uid)
                except ValueError:
                    pass

            max_count = self.presentation_levels[level].get('max_count')
            if max_count and len(uids) >= max_count:
                uids.pop(0)
            uids.append(uid)
            docs[level] = uids
            changed = 1
        else:
            for elem in docs.values():
                try:
                    elem.remove(uid)
                    changed = 1
                except ValueError:
                    pass

        if changed:
            self.updateRemoteCopy(recursive=0)
        return

    security.declarePublic('getPresentationLevel')

    def getPresentationLevel(self, object):
        """ Get the way document is displayed on the external site.
        """
        uid = object.getUid()
        docs = self.presented_documents
        for (level, uids) in docs.items():
            if uid in uids:
                return level

        return None
        return

    def _findPresentedDocuments(self, level, subpath=None):
        """
            Finds all catalog records of presented documents for the given level and subpath.
        """
        uids = self.presented_documents.get(level, None)
        if not uids:
            return ()
        if subpath:
            if type(subpath) is StringType and not subpath.startswith(self.storage_id + '/') or type(subpath) in (ListType, TupleType) and subpath[0] != self.storage_id:
                path = joinpath(self.physical_path(), self.storage_id, subpath)
            else:
                path = joinpath(self.physical_path(), subpath)
        else:
            path = self.physical_path()
        catalog = getToolByName(self, 'portal_catalog')
        results = list(catalog.searchResults(path=path, nd_uid=list(uids)))
        uids_idx = uids.index
        results.sort((lambda a, b, ui=uids_idx: cmp(ui(a.nd_uid), ui(b.nd_uid))))
        return results
        return

    security.declareProtected(CMFCorePermissions.AccessContentsInformation, 'listPresentationLevels')

    def listPresentationLevels(self):
        """
            Returns list of document presentation levels
        """
        levels = self.presentation_levels.items()
        levels.sort()
        return [_[1] for level in levels]
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setPresentationLevelProperties')

    def setPresentationLevelProperties(self, level, max_count, title):
        """
            Sets the properties for document presentation level
        """
        self.presentation_levels[level] = {'max_count': max_count, 'title': title}
        current_uids = self.presented_documents.get(level)
        if max_count and current_uids and len(current_uids) > max_count:
            self.presented_documents[level] = current_uids[len(current_uids) - max_count:]
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'addPresentationLevel')

    def addPresentationLevel(self, max_count, title):
        """
            Adds new presentation level
        """
        self.presentation_levels[len(self.presentation_levels)] = {'max_count': max_count, 'title': title}
        self.updateRemoteCopy(recursive=0)
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'deletePresentationLevel')

    def deletePresentationLevel(self):
        """
            Removes last presentation level
        """
        level = len(self.presentation_levels) - 1
        del self.presentation_levels[level]
        if self.presented_documents.has_key(level):
            del self.presented_documents[level]
        self.updateRemoteCopy(recursive=0)
        return

    security.declareProtected(CMFCorePermissions.ManagePortal, 'relink')

    def relink(self):
        """
        """
        skins = self.getExternalRoot()['portal_skins']
        for id in ('custom', 'images'):
            ob = self._getOb(id, None)
            if ob is None:
                continue
            old = skins._getOb(id, None)
            if old is not None:
                if old._p_oid == ob._p_oid:
                    continue
                skins._delOb(id)
            skins._setOb(id, aq_base(ob))

        return 'done'
        return

    security.declareProtected(CMFCorePermissions.View, 'addPublication')

    def addPublication(self, folder_uid, document_id, doc_modif_time):
        """
            Adds data about published document to SiteAnnounce object.

            For more details see SiteAnnounce.addPublication().
        """
        self.getSiteAnnounceObject().addPublication(folder_uid, document_id, doc_modif_time)
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'getSiteAnnounceObject')

    def getSiteAnnounceObject(self):
        """
            Returns site's SiteAnnounce object.
        """
        return self.announce_task
        return

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'announcePublished')

    def announcePublished(self):
        """
            Starts announce_task's announcePublished().

            This wrapper is needed to make it work, because SiteAnnounce instance
            is not placed in physicalPath. Methods being called from portal_scheduler
            as periodical task.
        """
        return self.getSiteAnnounceObject().announcePublished()
        return


InitializeClass(SiteContainer)
addSiteContainer = SiteContainer.manage_addSiteContainer.im_func
default_factories = (
 HTMLDocument.HTMLDocumentType, HeadingType, SubscriptionFolder.SubscriptionFolderType, SubscriptionFolder.SubscriptionRootType, Storefront.StorefrontType, DTMLDocument.DTMLDocumentType, NauPublishTool.NauPublisherType, SiteImage.SiteImageType, TabularReport.TabularReportType, Voting.VotingType)

class SiteGenerator(PortalGenerator):
    __module__ = __name__

    def setupTools(self, p):
        """Set up initial tools"""
        for name in Config.SiteTools:
            if name.startswith('CMF '):
                factory = p.manage_addProduct['CMFCore']
            elif name.startswith('Default '):
                factory = p.manage_addProduct['CMFDefault']
            else:
                factory = p.manage_addProduct['CMFNauTools']
            factory.manage_addTool(name, None)

        return

    def setupDefaultSkins(self, p):
        ps = getToolByName(p, 'portal_skins')
        ps.addSkinSelection('Site', 'custom,images', make_default=1)
        for view in Config.SiteSkinViews:
            before = view == 'site_mandatory' and 'custom' or None
            ps.addSkinLayer(view, 'skin/%s' % view, globals(), before=before)

        ps.addSkinSelection('Mail', 'custom')
        p.setupCurrentSkin()
        return

    def setupTypes(self, p, initial_types=default_factories):
        tptool = getToolByName(p, 'portal_types', None)
        if not tptool:
            return
        for tp in initial_types:
            if not tptool.getTypeInfo(tp['id']):
                tptool.addType(tp['id'], tp)

        return

    def setupActions(self, p):
        tool = getToolByName(p, 'portal_actions')
        tool.action_providers = tuple(Config.SiteActionProviders)
        return

    def setupPermissions(self, p):
        mp = p.manage_permission
        mp(CMFCorePermissions.ListFolderContents, ['Anonymous'], 1)
        mp(CMFCorePermissions.View, ['Anonymous'], 1)
        return

    def setup(self, p, create_userfolder):
        self.setupTools(p)
        if create_userfolder:
            self.setupUserFolder(p)
        self.setupRoles(p)
        self.setupPermissions(p)
        self.setupDefaultSkins(p)
        self.setupTypes(p, default_factories)
        self.setupActions(p)
        self.setupMimetypes(p)
        return

    def create(self, container, repository, id, title, create_userfolder):
        portal = self.klass(id, title=title)
        repository._setObject(id, portal)
        p = repository.this()._getOb(id)
        self.setup(p, create_userfolder)
        p.internal_url = container.physical_path()
        return p
        return


class SitesInstaller:
    __module__ = __name__
    after = True

    def install(self, p):
        msgcat = getToolByName(p, 'msg')
        lang = msgcat.get_default_language()
        p.manage_addProduct['OFSP'].manage_addFolder(id='external', title=msgcat.gettext('External sites', lang=lang))
        return


def initialize(context):
    context.registerContent(SiteContainer, addSiteContainer, SiteContainterType, activate=False)
    context.registerInstaller(SitesInstaller)
    return
