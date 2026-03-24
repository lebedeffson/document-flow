"""
Legacy NauItem class.

$Editor: vpastukhov $
$Id: SimpleNauItem.py,v 1.150 2005/05/14 05:43:48 vsafronovich Exp $
"""
__version__ = '$Revision: 1.150 $'[11:-2]

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as ZopePermissions
from Acquisition import aq_parent

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Config, Features
from Config import Roles, Permissions
from ContentCategory import ContentCategory

from SimpleObjects import ContentBase
from Utils import InitializeClass, joinpath


class SimpleNauItem( ContentBase, ContentCategory ):
    """
        Abstract base class for NauDoc content objects
    """
    _class_version = 1.112

    __implements__ = ( Features.isPortalContent,
                       ContentBase.__implements__,
                       ContentCategory.__implements__ )

    security = ClassSecurityInfo()

    def __init__( self, id=None, title=None, category=None, category_template=None,
                        category_primary=None, category_attributes=None, **kwargs ):
        """ Initialize class instance
        """
        ContentBase.__init__( self, id, title, **kwargs )
        ContentCategory.__init__( self, category, category_template,
                                        category_primary, category_attributes )

    #
    # External site interaction methods
    #
    security.declareProtected( CMFCorePermissions.View, 'getSite')
    def getSite( self ):
        """
            Return parent Site object or None.
        """
        try:
            return self.getSiteObject()
        except AttributeError:
            return None

    security.declareProtected( CMFCorePermissions.View, 'getSubscription')
    def getSubscription( self ):
        """
            Return parent Subscription object or None.
        """
        try:
            return self.getSubscriptionObject()
        except AttributeError:
            return None

    security.declarePublic( 'external_url' )
    def external_url( self, relative=0, **kw ):
        """
            Returns URL for this object on the external site.
        """
        site = self.getSite()
        if site is None:
            return None

        url  = self.absolute_url( 1, **kw )
        top  = site.getSiteStorage().absolute_url( 1 )
        root = site.getExternalRootUrl( relative=relative )

        return joinpath( root, 'go', url[ len(top): ] )

    #
    # Site presentation interface methods
    #
    def isPublished( self ):
        """ Check whether document is published on the external site
        """
        if not self.getSite():
            return None

        wftool = getToolByName( self, 'portal_workflow', None )
        if wftool is None:
            return None

        return wftool.getStateFor( self ) == 'published'

    security.declareProtected( Permissions.PublishPortalContent, 'setIndexDocument' )
    def setIndexDocument( self, flag=1 ):
        """Set mark on the document, that it must be used
           as index page for topic on external site
        """
        topic = aq_parent( self )

        flag  = not not flag
        topic.setMainPage( flag and self or None )

    security.declarePublic( 'isIndexDocument' )
    def isIndexDocument( self ):
        """ Check whether the document is an index page fot its topic
        """
        topic = aq_parent( self )

        main_page = topic.getMainPage()
        if not main_page:
            return None

        return main_page.getUid() == self.getUid()

    security.declareProtected( Permissions.PublishPortalContent, 'setPresentationLevel' )
    def setPresentationLevel( self, level=None ):
        """ Set news level of the document.
        """
        site = self.getSite()
        if site:
            site.setPresentationLevel( self, level )

    security.declarePublic( 'getPresentationLevel' )
    def getPresentationLevel( self ):
        """ Get the way document is displayed on the external site.
        """
        site = self.getSite()
        if not site:
            return None

        return site.getPresentationLevel( self )

    def _remote_transfer( self, context=None, container=None, server=None, path=None, id=None, parents=None, recursive=None ):
        """ Transfer local object to remote server
        """
        remote = ContentCategory._remote_transfer( self, context, container, server, path, id, parents, recursive )
        ContentBase._remote_onTransfer(self, remote)

        return remote

InitializeClass( SimpleNauItem )
