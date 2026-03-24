""" Shortcuts are references to other objects within the same CMF site..

$Id: Shortcut.py,v 1.38 2006/05/04 12:15:35 ynovokreschenov Exp $
"""
__version__ = "$Revision: 1.38 $"[11:-2]

import string
import urlparse
from types import StringType

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner, aq_base

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.Link import Link as CMFLink

import Features
from Config import Roles
from SimpleObjects import ContentBase, ProxyReaderFactory
from Utils import InitializeClass, getObjectByUid, cookId, joinpath, _checkPermission

not_found_message = 'The object shortcut is referenced to cannot be found. This object has probably been deleted or transferred.'

ShortcutType = { 'id'             : 'Shortcut'
               , 'meta_type'      : 'Shortcut'
               , 'description'    : "A Shortcut is a Link to an intra-portal resource."
               , 'icon'           : 'link_icon.gif'
               , 'sort_order'     : 0.8
               , 'product'        : 'CMFNauTools'
               , 'factory'        : 'addShortcut'
               , 'factory_form'   : 'shortcut_add_form'
               , 'permissions'  : ( CMFCorePermissions.View, )
               , 'disallow_manual': 0
               , 'actions'        :
                 ( { 'id'            : 'view'
                   , 'name'          : "View"
                   , 'action'        : ''
                   , 'permissions'   : ( CMFCorePermissions.View, )
                   },
                   { 'id'            : 'edit'
                   , 'name'          : "Edit"
                   , 'action'        : 'shortcut_edit_form'
                   , 'permissions'   : ( CMFCorePermissions.ModifyPortalContent, )
                   },
#                  { 'id'            : 'metadata'
#                  , 'name'          : "Metadata"
#                  , 'action'        : 'metadata_edit_form'
#                  , 'permissions'   : ( ModifyPortalContent, )
#                  }
                 )
               }

def addShortcut( self, id, remote, title='', description='', remote_version=None ):
    """
        Add a Shortcut
    """
    if id is None:
        id = cookId( self.this(), prefix='shortcut' )

    self._setObject( id, Shortcut(id, title, description) )

    # Bind shortcut to the document
    shortcut = self._getOb(id)
    shortcut.edit(remote=remote, remote_version=remote_version)

class Shortcut( ContentBase, ProxyReaderFactory, CMFLink ):
    """
        A Shortcut -- special kind of Link.
    """
    _class_version = 1.28

    meta_type = 'Shortcut'

    security = ClassSecurityInfo()

    __implements__ = (  ContentBase.__implements__,
                        Features.isPortalContent,
                        Features.reindexAfterRefresh,
                        Features.createFeature('isShortcut'),
                        )

    def __init__( self
                , id
                , title
                , description=''
                ):
        ContentBase.__init__(self, id)
        ProxyReaderFactory.__init__(self, id)
        # Can not create link right now because a Shortcut object
        # was not instantiated yet

        self.title = title
        self.description = description
        self.link_id = None

    def __before_publishing_traverse__(self, self2,  REQUEST=None):
        object = self.getObject()

        if object:
            if object.implements('isVersion'):
                object.makeCurrent()
            uid = str( object.getUid() )
        else:
            obj_uid = self.getObjectUid()
            if obj_uid:
                uid = str( obj_uid.base() )
            else:
                translated_message = getToolByName( self, 'msg' )( not_found_message )
                #raise 'NotFound', translated_message
                REQUEST.RESPONSE.write(translated_message)
                REQUEST.RESPONSE.setStatus(404, 'Missing Shortcut')

        stack = REQUEST['TraversalRequestNameStack']

        if stack and stack[-1] == uid:
            return

        stack.append( uid )


    def getRemoteUrl(self, **kw):
        """
          Returns the remote URL of the Link
        """
        obj = self.getObject()
        if obj:
            return obj.absolute_url(**kw)

        return self.aq_parent.relative_url(message='Unable to find the linked document')

    def getIcon(self):
        """
          Instead of a static icon, like for Link objects, we want
          to display an icon based on what the Shortcut links to.
        """
        object = self.getObject()
        if object and hasattr( object, 'getIcon' ):
            return object.getIcon()

        return 'p_/broken'

    icon = getIcon

    def getObject(self):
        """
          Returns the actual object that the Shortcut is linking to
        """
        link = self._getLink()
        return link and link.getTargetObject()

    def getObjectUid(self):
        """
          Returns the actual object uid that the Shortcut is linking to
        """
        link = self._getLink()
        return link and link.getTargetUid()

    def _getLink(self):
        if not self.link_id:
            return None
        return getToolByName( self, 'portal_links' )._getOb( self.link_id, None )

    def edit(self, remote, remote_version=None ):
        """
          Update and reindex.
          'remote' can be either remote object itself or an object uid string
          'remote_version' -- version id string
        """
        self._edit( remote, remote_version )
        self.reindexObject(idxs=['portal_type'])

    def _edit( self, remote, remote_version=None ):
        """
          Edits the Shortcut
        """
        if type(remote) is StringType:
            remote = getObjectByUid(self, remote)

        if not self.Title():
            # TODO consider version num for the title
            self.setTitle(remote.Title())

        # Create a link to the remote object.
        # Link is the one and only way to keep in touch with the
        # remote document.
        links_tool = getToolByName(self, 'portal_links')
        if remote_version and remote.implements('isVersionable'):
            remote = remote.getVersion(remote_version)
        self.link_id = links_tool.restrictedLink( self, remote, 'shortcut' )

        if remote.implements('isVersion'):
            self.portal_type = remote.getVersionable().portal_type
        else:
            self.portal_type = remote.portal_type

    def externalEditLink_(self, object, borrow_lock=0):
        """ Insert the external editor link to an object if appropriate
        """
        link = ''

        if object is self:
            object = self.getObject()

        if object and _checkPermission(CMFCorePermissions.ModifyPortalContent, object):
            if object.implements('isVersionable'):
                object = object.getVersion()
            link = object.externalEditLink_(object, borrow_lock)

        return link

InitializeClass( Shortcut )

def initialize( context ):
    # module initialization callback

    context.registerContent( Shortcut, addShortcut, ShortcutType )
