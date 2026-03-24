""" DTMLDocument class
$Id: DTMLDocument.py,v 1.58 2005/06/27 10:22:25 ypetrov Exp $
"""
__version__='$Revision: 1.58 $'[11:-2]

from types import StringType

from AccessControl import ClassSecurityInfo
from OFS.DTMLMethod import DTMLMethod

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

import Config, Features
from ActionInformation import ActionInformation as AI
from Config import Permissions
from Exceptions import ResourceLockedError
from SimpleNauItem import SimpleNauItem
from SyncableContent import SyncableContent
from Utils import InitializeClass, installPermission

DTMLDocumentType = { 'id'             : 'DTMLDocument'
                   , 'meta_type'      : 'DTMLDocument'
                   , 'title'          : "DTML Document"
                   , 'description'    : "Simple DTML-document"
                   , 'icon'           : 'dtml_icon.gif'
                   , 'sort_order'     : 0.45
                   , 'product'        : 'CMFNauTools'
                   , 'factory'        : 'addDTMLDocument'
                   , 'immediate_view' : 'dtml_edit_form'
                   , 'permissions'    : ( Permissions.AddDTMLDocuments, )
                   , 'actions'        :
                                ( #{ 'id'          : 'view'
                                  #, 'name'        : "View"
                                  #, 'action'      : 'dtml_view_form'
                                  #, 'permissions' : (
                                  #    CMFCorePermissions.View, )
                                  # },
                                  { 'id'          : 'edit'
                                  , 'name'        : "Edit"
                                  , 'action'      : 'dtml_edit_form'
                                  , 'permissions' : (
                                       CMFCorePermissions.ModifyPortalContent, )
                                  },
                                  { 'id'        : 'metadata'
                                  , 'name'        : "Metadata"
                                  , 'action'      : 'metadata_edit_form'
                                  , 'permissions' : (
                                       CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                   }

class DTMLDocument( SimpleNauItem, DTMLMethod, SyncableContent ):
    """ NauSite DTML document """
    _class_version = 1.38

    meta_type = 'DTMLDocument'
    portal_type = 'DTMLDocument'

    __implements__ = ( Features.isDocument,
                       Features.isTemplate,
                       Features.isPublishable,
                       Features.isCategorial,
                       Features.isPrintable,
                       Features.isExternallyEditable,
                       DTMLMethod.__implements__,
                       SyncableContent.__implements__,
                       SimpleNauItem.__implements__,
                     )

    if Config.UseExternalEditor:
        _actions = \
            (
                AI(
                    id          = 'external_edit',
                    title       = 'Edit using external editor',
                    icon        = 'external_editor.gif',
                    action      = Expression('string: ${object_url}/externalEdit'),
                    permissions = ( CMFCorePermissions.ModifyPortalContent, ),
                    condition   = Expression( 'python: not object.isLocked()' ),
                    visible     = 0
                ),
            )

    security = ClassSecurityInfo()

    manage_options = SimpleNauItem.manage_options + \
                     DTMLMethod.manage_options

    effective_date  = None
    expiration_date = None

    def __init__( self, id, title=None, text='', **kwargs ):
        """ Initialize class instance
        """
        SimpleNauItem.__init__( self, id, title, **kwargs )
        DTMLMethod.__init__( self, text, None, id )

    def _initstate( self, mode ):
        # initialize attributes
        if not SimpleNauItem._initstate( self, mode ):
            return 0

        # versions < 1.38 used to be Item_w__name__
        if not getattr( self, 'id', None ):
            self.id = self.__name__

        return 1

    security.declareProtected( CMFCorePermissions.View, '__call__', 'CookedBody' )
    CookedBody = __call__ = DTMLMethod.__call__

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'PUT' )
    PUT = DTMLMethod.PUT

    security.declareProtected( CMFCorePermissions.View, 'view' )
    def view(self, REQUEST=None):
        """
        This method is called only from NauSite user interface (and is not called by default)
        """
        return self.redirect(action = 'dtml_edit_form', REQUEST = REQUEST)

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'edit' )
    def edit(self, title, data, REQUEST=None):
        if self.wl_isLocked():
            raise ResourceLockedError, 'This DTML Method is locked via WebDAV'
        if title: self.title=str(title)
        if type(data) is not type(''): data=data.read()
        self.munge(data)
        self.ZCacheable_invalidate()
        if REQUEST:
            message="Content changed."
            return self.view(self,REQUEST,potal_status_message=message)

    def upload(self,file='', REQUEST=None):
        """Replace the contents of the document with the text in file."""
        self._validateProxy(REQUEST)
        if self.wl_isLocked():
            raise ResourceLockedError, (
                'This document has been locked via WebDAV.')
        if type(file) is not type(''): file=file.read()
        self.munge(file)
        self.ZCacheable_invalidate()
        if REQUEST:
            message="Content uploaded."
            return self.dtml_edit_form(self,REQUEST,portal_status_message=message)

    def SearchableText(self):
        return ' '.join( ( self.getId()
                         , self.Title()
                         , DTMLMethod.PrincipiaSearchSource(self)
                         ) )

installPermission( DTMLDocument, CMFCorePermissions.ReplyToItem )
InitializeClass( DTMLDocument )


_default_dd_html="""<dtml-var standard_html_header>
<h2><dtml-var title_or_id></h2>
<p>
This is the <dtml-var id> DTML Document.
</p>
<dtml-var standard_html_footer>"""

def addDTMLDocument( self, id, title='', file='', REQUEST=None, **kwargs ):
    """
        Adds a DTML Document object with the contents of file.
        If 'file' is empty, default document text is used.
    """
    if type(file) is not StringType:
        file = file.read()
    if not file:
        file = _default_dd_html

    obj = DTMLDocument( id, title, text=file, **kwargs )
    self._setObject( id, obj )

    if REQUEST is not None:
        try: u=self.DestinationURL()
        except: u=REQUEST['URL1']
        REQUEST.RESPONSE.redirect(u+'/manage_main')

def initialize( context ):
    # module initialization callback

    context.registerContent( DTMLDocument, addDTMLDocument, DTMLDocumentType )
