"""
HTMLDocument class.

$Editor: vpastukhov $
$Id: HTMLDocument.py,v 1.325 2008/12/03 13:05:40 oevsegneev Exp $
"""
__version__ = '$Revision: 1.325 $'[11:-2]

from cgi import escape
from types import ListType, StringType, StringTypes, TupleType

from sys import version_info
if version_info[:2] < (2, 3):
    import pre as re
else:
    import re

import transaction
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from AccessControl.User import SpecialUser
from Acquisition import aq_base, aq_parent, aq_get, Implicit
from DateTime import DateTime
from OFS.ObjectManager import ObjectManager
from ZPublisher.HTTPRequest import FileUpload
from zLOG import LOG, TRACE

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName, \
        _getAuthenticatedUser, _checkPermission
from Products.CMFDefault.Document import Document
from Products.CMFDefault.utils import html_headcheck, formatRFC822Headers

import Config, Features, Exceptions
from ActionInformation import ActionInformation as AI
from Config import Months, Permissions
from ContentRating import ContentRating
from ContentVersions import VersionableContent, InitializeVersionableClass
from Features import createFeature
from File import FileAttachment, addFile as _addFile
from HTMLCleanup import HTMLCleaner
from HTMLDiff import HTMLDiff
from Mail import MailMessage, getContentId, mailFromDocument
from SimpleNauItem import SimpleNauItem
from SyncableContent import SyncableContent
from TaskItemContainer import TaskItemContainer
from Utils import InitializeClass, getLanguageInfo, \
        joinpath, isBroken, parseDate, parseUid, cookId
from WorkflowTool import WorkflowMethod


HTMLDocumentType = {   'id'             : 'HTMLDocument'
                     , 'meta_type'      : 'HTMLDocument'
                     , 'title'          : "Document"
                     , 'description'    : "HTML-document with WYSIWYG editor"
                     , 'icon'           : 'doc_icon.gif'
                     , 'sort_order'     : 0.4
                     , 'product'        : 'CMFNauTools'
                     , 'factory'        : 'addHTMLDocument'
                     , 'immediate_view' : 'document_edit_form'
                     , 'allow_discussion': 1
                     , 'actions'        :
                        ( { 'id'            : 'view'
                          , 'name'          : "View"
                          , 'action'        : 'document_view'
                          , 'permissions'   : (
                                CMFCorePermissions.View,
                             )
                          }
                        , { 'id'            : 'followup'
                          , 'name'          : "Follow-up tasks"
                          , 'action'        : 'document_follow_up_form'
                          , 'permissions'   : (
                              CMFCorePermissions.View, )
                          }
                        , { 'id'            : 'edit'
                          , 'name'          : "Edit"
                          , 'action'        : 'document_edit_form'
                          , 'permissions'   : (
                              CMFCorePermissions.ModifyPortalContent, )
                          }
                        , { 'id'            : 'request_confirmation'
                          , 'name'          : "Request confirmation"
                          , 'action'        : 'document_confirmation_form'
                          , 'permissions'   : (
                              CMFCorePermissions.RequestReview, )
                          }
                        , { 'id'            : 'metadata'
                          , 'name'          : "Metadata"
                          , 'action'        : 'metadata_edit_form'
                          , 'permissions'   : (
                              CMFCorePermissions.ModifyPortalContent, )
                          }
                        , { 'id'            : 'attachments'
                          , 'name'          : "Attachments"
                          , 'action'        : 'document_attaches'
                          , 'permissions'   : (
                              CMFCorePermissions.View, )
                          }
                        , { 'id'            : 'link'
                          , 'name'          : "Links"
                          , 'action'        : 'document_link_form'
                          , 'permissions'   : (
                              CMFCorePermissions.View, )
                          }

                        , { 'id'            : 'ownership'
                          , 'name'          : "Change ownership"
                          , 'action'        : 'change_ownership_form'
                          , 'permissions'   : (
                              ZopePermissions.take_ownership, )
                          }

                        , { 'id'            : 'distribute_document'
                          , 'name'          : "Distribute document"
                          , 'action'        : 'distribute_document_form'
                          , 'permissions'   : (
                              CMFCorePermissions.View, )
                          }

                        , { 'id'            : 'subscription'
                          , 'name'          : "Manage subscription"
                          , 'action'        : 'manage_document_subscription'
                          , 'permissions'   : (
                              CMFCorePermissions.View, )
                          }
                        , { 'id'            : 'distribution_log'
                          , 'name'          : "Distribution log"
                          , 'action'        : 'distribution_log_form'
                          , 'permissions'   : (
                              CMFCorePermissions.View, )
                          }
                        , { 'id'            : 'workflow_history'
                          , 'name'          : "Workflow history chart"
                          , 'action'        : 'document_workflow_history'
                          , 'permissions'   : (
                              CMFCorePermissions.View, )
                          }
                        )
                     }

class CopyHolders:

    security = ClassSecurityInfo()

    _versionable_attrs = ( '_copies_holders' ,)

    security.declareProtected( CMFCorePermissions.View, 'listCopiesHolders' )
    def listCopiesHolders( self ):
        """
            Returns list of copies holders.

            Note:

                Only for NormativeDocument category.
        """
        return self._copies_holders

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setCopiesHolders' )
    def setCopiesHolders( self, id, **kw ):
        """
            Sets copies holders.

            Arguments:

                '**kw' -- keyword of fields
                'id'   -- list of copies holders id

            Note:

                Only for NormativeDocument category.
        """
        copies_holders = []

        #XXX
        for idx in range( len( id ) ):
            copies_holder = { 'id': id[idx] }
            for k, i in kw.items():
                copies_holder[k] = i[idx]
            copies_holders.append(copies_holder)

        self._copies_holders = copies_holders

    security.declareProtected( CMFCorePermissions.ManageProperties, 'addCopiesHolder' )
    def addCopiesHolder( self, **kw):
        """
            Adds copies holder.

            Arguments:

                '**kw' -- keyword of fields

            Note:

                Only for NormativeDocument category.
        """
        kw['id'] = cookId( self._copies_holders, prefix='copy_holder' )
        self._copies_holders.append(kw)

        # XXX self is already version
        self.getVersion()._p_changed = 1

    security.declareProtected( CMFCorePermissions.ManageProperties, 'deleteCopiesHolders' )
    def deleteCopiesHolders( self, ids):
        """
            Deletes copies holders.

            Arguments:

                'ids' -- list of copies holders ids.

            Note:

                Only for NormativeDocument category.
        """
        for id in ids:
            for holder in self._copies_holders[:]:
                if holder['id'] == id:
                    self._copies_holders.remove(holder)

        # XXX self is already version
        self.getVersion()._p_changed = 1

InitializeClass( CopyHolders )

class HTMLDocument( VersionableContent, SimpleNauItem, ObjectManager, Document, ContentRating, SyncableContent, CopyHolders ):
    """
        Subclassed Document type
    """
    _class_version = 1.21

    meta_type = 'HTMLDocument'
    portal_type = 'HTMLDocument'

    __implements__ = ( createFeature('isHTMLDocument'),
                       Features.isDocument,
                       Features.isCompositeDocument,
                       Features.isPublishable,
                       Features.isLockable,
                       Features.hasLanguage,
                       Features.isPrintable,
                       Features.isExternallyEditable,
                       Features.hasTabs,
                       Features.hasHeadingInfo,
                       SimpleNauItem.__implements__,
                       Document.__implements__,
                       ObjectManager.__implements__,  # remove ?
                       SyncableContent.__implements__,
                       VersionableContent.__implements__,
                     )

    _actions = (
            AI(
                id          = 'external_edit',
                title       = "External editor",
                description = "Edit using external editor",
                icon        = 'external_editor.gif',
                action      = Expression(
                                "python: '%s/externalEdit' % "
                                        "(lambda v=object.getVersion():"
                                            "(v.getAssociatedAttachment() or v).absolute_url())()"
                                # XXX lambda was used only to assign variable in expression
                              ),
                permissions = ( CMFCorePermissions.ModifyPortalContent, ),
                condition   = Expression(
                                "python: portal.portal_properties.getConfig('UseExternalEditor') "
                                    "and not object.isLocked() "
                                    "and portal.portal_workflow.getStateFor(folder) == 'editable' "
                                    "and object.getEditableVersion(latest=0)"
                              ),
                visible     = Config.UseExternalEditor,
            ),
        )

    security = ClassSecurityInfo()

    # override access settings
    security.declareProtected( CMFCorePermissions.View, 'Format' )
    #security.declarePublic( 'getMetadataHeaders' ) XXX must be View ???

    manage_options = SimpleNauItem.manage_options + \
                     ObjectManager.manage_options
                     #Document.manage_options

    # A list of supported MIME types for the document content,
    # in order of preference
    allowed_content_types = ( 'text/html', 'text/plain' )

    # default attribute values
    _versionable_methods = (
            '_edit', '_ver_edit', '_replaceLinks', 'getChangesFrom',
            'addFile', 'pasteFile', 'removeFile',
            'listAttachments', 'associateWithAttach',
            'getCategoryAttribute', 'setCategoryAttribute',
            '_getCategoryAttribute', '_setCategoryAttribute',
            '_getCategorySheet', '_category_onChangeAttribute',
            'listTabs', 'view'
        )

    _versionable_methods_common = (
            'absolute_url', 'relative_url', 'redirect', 'parent_path',
            'reindexObject'
        )

    _versionable_attrs = (
            'text', 'cooked_text', 'title', 'description',
            'modification_date', 'effective_date', 'creation_date',
            'associated_with_attach', 'attachments',
            'workflow_history', '__propsets__',
        ) + CopyHolders._versionable_attrs

    _versionable_perms = (
            CMFCorePermissions.View,
            CMFCorePermissions.ModifyPortalContent,
            Permissions.MakeVersionPrincipal,
            Permissions.ViewAttributes,
            Permissions.ModifyAttributes,
        )

    # XXX must implement support for versionable WorkflowMethods
    # then remove this hack
    _ver_edit = Document.edit
    security.declarePublic( 'edit' )

    edit = WorkflowMethod( '_ver_edit', 'modify', \
                           security=security, \
                           method_permission=CMFCorePermissions.ModifyPortalContent, \
                           invoke_after=1 )

    # restore ObjectManager methods overridden by PortalContent
    objectItems = ObjectManager.objectItems
    objectValues = ObjectManager.objectValues
    tpValues = ObjectManager.tpValues

    # restore Document methods overridden by DublinCore
    Format = Document.Format
    setFormat = Document.setFormat
    getMetadataHeaders = Document.getMetadataHeaders
    SearchableText = Document.SearchableText

    def __init__( self, id, title=None, text_format='html', text='', **kwargs ):
        """
            Initialize class instance
        """
        VersionableContent.__init__( self ) # NB must be the first
        SimpleNauItem.__init__( self, id, title, **kwargs )
        self.setFormat( text_format )
        Document._edit.im_func( self, text )

    def _initstate( self, mode ):
        """
            Initialize attributes
        """
        if not SimpleNauItem._initstate( self, mode ):
            return 0

        if getattr( self, 'changes_log', None ) is None:
            self.changes_log = []

        if hasattr( self, '_directive' ):
            delattr( self, '_directive' )

        followup = getattr( self, 'followup', None )
        if followup is None or not isinstance( followup, TaskItemContainer ):
            self.followup = TaskItemContainer()

        for id, item in self.objectItems():
            if isinstance( item, PortalFolder ):
                self._delObject( id )
            if isBroken( item, 'SearchableAttach' ):
                self._upgrade( id, FileAttachment )

        if hasattr( self, 'registry_id' ):
            self.registry_data = {}
            self.registry_data[ self.registry_id ] = ['Not specified']
            delattr( self, 'registry_id' )
        elif hasattr( self, 'registry_data' ):
            for key in self.registry_data.keys():
                if type(self.registry_data[ key ]) is not ListType:
                    self.registry_data[ key ] = [ self.registry_data[ key ] ]
        else:
            self.registry_data = {}

        if not hasattr( self, 'subscribed_users'):
            self.subscribed_users = {}

        if type(self.subscribed_users) is ListType:
            new_su = {}
            for user in self.subscribed_users:
                new_su[ user ] = [ MagicSaveTransition ]

            self.subscribed_users = new_su

        if not hasattr( self, 'distribution_log' ):
            self.distribution_log = []

        if hasattr( aq_base( self ), 'workflow_history' ):
            # copying workflow_history from document to principal version
            self.getVersion( self.getPrincipalVersionId() ).workflow_history = \
                getattr( aq_base( self ), 'workflow_history' )
            # deleting workflow_history from document
            delattr( aq_base( self ), 'workflow_history' )

            # initializing followup tasks
            version_id_to_initialize = self.getPrincipalVersionId()
            for task in self.followup.objectValues():
                if not hasattr( task, 'version_id' ):
                    task.version_id = version_id_to_initialize
                elif task.version_id is None:
                    task.version_id = version_id_to_initialize

        if hasattr( self, '__propsets__' ): # < 1.21
            # rely on __setattr__ magic
            self.__propsets__ = self.__propsets__
            del self.__propsets__

        return 1

    def __before_publishing_traverse__( self, object, REQUEST ):
        """
            Allow subobjects to be called
        """
        path = REQUEST['TraversalRequestNameStack']

        if len(path) > 1 and path[-1] == self.getId():
            del path[-1]

    def Language( self ):
        """
            Returns document language code.

            Result:

                String.
        """
        return Document.Language( self ) \
            or getToolByName( self, 'msg' ).get_default_language()

    security.declarePublic( 'getFontFamily' )
    def getFontFamily( self ):
        """
            Returns font family names for the document text.

            Result:

                String.
        """
        return getLanguageInfo( self.Language() )['document_font']

    def getContentsSize( self ):
        """
            Returns total size of the document text and all attachments.
            See 'ContentBase.getContentsSize'.
        """
        size = len( self.text or '' )
        for id, attach in self.listAttachments():
            size += attach.get_size()
        return size

    def isContentEmpty( self ):
        """
            See 'ContentBase.isContentEmpty'.
        """
        return not ( self.text.strip() or self.listAttachments() )

    security.declareProtected( CMFCorePermissions.View, 'FormattedBody' )
    def FormattedBody( self, html=1, width=None, canonical=None, REQUEST=None ):
        """
            Returns formatted document body.

            Arguments:

                'html' -- Boolean. Indicates whether the document text should be
                          formatted according to the HTML rules.

                'width' -- Not implemented. Specifies the maximum string width.

                'canonical' -- Boolean. Forces external links to be rendered in a
                               canonical way. See ItemBase.absolute_url for details.

            Result:

                String.
        """
        lang = self.Language()
        charset = getLanguageInfo( lang )['http_charset']

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader( 'content-type', 'text/html; charset=%s' % charset )

        if html or self.text_format == 'html':
            site = self.getSite()
            if site and hasattr(site.custom,'default_stylesheet'):
                site_style = '<link rel=\"stylesheet\" type=\"text/css\" href=\"'+site.getExternalRootUrl()+'/go/default_stylesheet\" />\n'
            else:
                site_style = ''

            if canonical:
                meta = '<meta http-equiv="Content-Type" content="text/html; charset=%s" />\n' % charset
            else:
                meta = ''

            bodytext = _formattedBodyTemplate % {
                        'title'     : escape( self.Title() ),
                        'head'      : meta,
                        'style'     : site_style,
                        'language'  : lang,
                        'font'      : self.getFontFamily(),
                        'body'      : self.CookedBody( canonical=canonical, view=1 ),
                    }
        else:
            bodytext = self.EditableBody(view=1)

        if width is not None:
            # TODO: reformat width
            pass

        return bodytext

    def CookedBody( self, stx_level=None, setlevel=0, canonical=None, view=True ):
        """
            Returns the prepared basic rendering of an object.

            For Documents, basic rendering means pre-rendered structured text, or
            what was between the <BODY> tags of HTML.

            Arguments:

                'stx_level' -- Integer value for the stx text level.

                'setlevel' -- Boolean. Indicates whether the document needs to
                              be recooked with new stx_level. See Document.CookedBody for
                              further explanations.

                'canonical' -- Boolean. Forces external links to be rendered in a
                               canonical way. See ItemBase.absolute_url for details.


                'view' -- Boolean. This argument is passed to the _replaceLinks method.

            Result:

                String.
        """
        text = Document.CookedBody( self, stx_level, setlevel )
        #change border=1 to border=0 in TABLE tags having "border-collapse: collapse"
        r_table = re.compile( r'<TABLE[^>]*border-collapse\:\s+collapse;?[^>]*>', re.I )
        r_border = re.compile( r'border=\s*(1)', re.I)
        matched = r_table.search( text )
        while matched:
            subst = r_border.sub( 'border=0', text[ matched.start() : matched.end() ] )
            text  = text[ :matched.start() ] + subst + text[ matched.end(): ]
            matched = r_table.search( text, matched.start() + len(subst) )

        return self._replaceLinks( text, canonical=canonical, view=view )

    def EditableBody( self, view=True ):
        """
            Returns the document editable body.

            Arguments:

                'view' -- Boolean. This argument is passed to the _replaceLinks method.

            Result:

                String.
        """
        return self._replaceLinks( Document.EditableBody( self )
                                 , types = ('attach', 'this', 'field', 'portal')
                                 , view = view
                                 )

    def listBodyFields( self ):
        """
            Returns document fields which placed in document body.
        """
        fields = []
        regex = re.compile( r'\{?\bnaudoc:(\w+)\b/+([/?&=#A-Za-z0-9._\-+%]*)\}?' )
        text = Document.EditableBody( self )
        match = regex.search( text )
        while match:
            option = match.group(1)
            subst  = match.group(2)
            if option == 'field':
                fields.append( subst )
            match = regex.search( text, match.end() )

        return fields

    def _replaceLinks( self, text, types=None, canonical=None, view=None ):
        """
            Renders special links in the given text.

            Arguments:

                'text' -- String containing the document text.

                'types' -- List of the processed link types. Link type can take
                           the value of either 'attach', 'this', field',
                           'portal' or 'site'. All types of links will be
                           processed in case the argument's value is None.

                'canonical' -- Boolean. Forces external links to be rendered in a
                               canonical way. See ItemBase.absolute_url for details.

                'view' -- Indicates whether the document category attributes should
                          be rendered as text values or as input form fields.

            Currently supported link codes are: {naudoc:field/<attribute_name>},
            {naudoc:attach/<attachment_name} and {naudoc:this}.

            Result:

                String.
        """
        REQUEST = aq_get( self, 'REQUEST', None )
        portal_url = getToolByName( self, 'portal_url' )()

        absolute_url = self.absolute_url()
        if canonical:
            relative_url = self.absolute_url( canonical=canonical )
            content_id   = getContentId( self, extra=1 )
        else:
            relative_url = self.relative_url()

        if REQUEST and REQUEST.get( 'ExternalPublish' ):
            external_url = portal_url
            # XXX must find real ids
            external_storage   = 'storage'
            external_publisher = 'go'
        else:
            site = self.getSite()
            external_url = site and site.relative_url() or portal_url
            external_storage = external_publisher = None

        regex = re.compile( r'\{?\bnaudoc:(\w+)\b/*([/?&=#A-Za-z0-9._\-+%]*)\}?' )
        match = regex.search( text )
        
        while match:
            option = match.group(1)
            subst  = match.group(2)

            if types and option not in types:
                subst = None

            elif option == 'attach':
                if canonical:
                    subst = 'cid:' + (content_id % subst)
                else:
                    #subst = joinpath( relative_url, subst )
                    # XXX: this is a hack, relative_url should be fixed instead
                    subst = joinpath( absolute_url, subst )

            elif option == 'this':
                if not subst.startswith('#'):
                    subst = joinpath( relative_url, subst )

            elif option == 'portal':
                subst = joinpath( portal_url, subst )

            elif option == 'site':
                if external_storage and subst.startswith( external_storage ):
                    subst = joinpath( external_url, external_publisher, subst[ len(external_storage): ] )
                else:
                    subst = joinpath( external_url, subst )

            #elif option == 'uid':
            #   pass # TODO

            elif option == 'field':
                name = subst
                template_name = (external_storage and 'external_view') or \
                                (view and 'view') or \
                                'edit'
                subst = self.getField(name, template_name)

            if subst is None:
                match = regex.search( text, match.end() )
            else:
                text  = text[ :match.start() ] + subst + text[ match.end(): ]
                match = regex.search( text, match.start() + len(subst) )

        return text

    def _edit( self, text, *args, **kw ):
        """
            Changes the document text.

            The given text is being parsed so that all form input items
            which names match the document's category attributes ids are
            replaced with the "{naudoc:field/<attribute_name>}" code. Each
            link containing the document's attachment url is replaced with
            "{naudoc:attach/<attachment_name}" code. Finally, every url
            pointing to the document itself is replaced with the
            "{naudoc:this}" string. _replaceLinks() method perfoms the
            backward convertion.

            Arguments:

                'text' -- New document text.

                '*args', '**kw' -- Additional arguments to be passed to Document._edit.

        """
        field_template = '{naudoc:field/%s}'

        # replacing all <span id="field:...">...</span> elements
        r_span = re.compile(r'<span [^>]*?\bid=(?P<q>"?)field:([-_a-z0-9]+)(?P=q).*?</span>', re.I | re.S)
        match = r_span.search(text)
        while match:
            subst = field_template % match.group(2)
            text = text[:match.start()] + subst + text[match.end():]
            match = r_span.search(text, match.start() + len(subst))

        # replacing relative links
        attachments = [ id for id, ob in self.listAttachments() ]
        self_urls = [ self.getVersion().absolute_url() 
                    , self.getVersionable().absolute_url()
                    , self.getVersion().relative_url()
                    , self.getVersionable().relative_url() ]

        regex = re.compile( '(?:' + '|'.join( map(re.escape, self_urls) ) + ')' + \
                              r'\b(?:/+(([A-Za-z0-9._\-+%]+)[/?&=#A-Za-z0-9._\-+%]*))\b'
                              )

        match = regex.search( text )

        while match:
            subst, id = match.groups()
            if id in attachments:
                subst = joinpath( 'naudoc:attach', subst )
            else:
                subst = joinpath( 'naudoc:this', subst )

            text  = text[ :match.start() ] + subst + text[ match.end(): ]
            match = regex.search( text, match.start()+len(subst) )

        charset = getLanguageInfo( self.Language() )['http_charset']
        charmap = Config.CharsetEntityMap.get( charset )
        if charmap:
            # TODO: make utility filter
            for char, entity in charmap.items():
                text = text.replace( char, entity )

        self._notifyOnDocumentChange()

        Document._edit.im_func( self, text, *args, **kw )

    def cleanup(self, no_clean_html=None):
        """
            Removes redundant HTML tags and attributes from the document text.

            Arguments:

                'no_clean_html' -- Boolean. Indicates whether the HTML source
                                   should be cleaned or not. In any case every
                                   reference to the document attachment will be
                                   converted into the relative url.
            Result:


        """
        # Remove absolute links to attached files, make them relative
        html = self.text
        rgx = re.compile(r'%s/' % ( self.absolute_url()) )
        html = re.sub(rgx,"" , html)

        if not no_clean_html:
            # Cleanup Word HTML
            html = HTMLCleaner(html, None, 0, '', 'SCRIPT STYLE')

        Document._edit(self, text=html)

        return html

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'addFile' )
    def addFile( self, file, id=None, title=None, paste=False, associate=False, try_to_associate=False, **kwargs ):
        """
            Attach a file to the document
        """
        #assert hasattr( file, 'read' )
        assert( isinstance( file, StringTypes + (FileUpload,) ))
        associate = associate or try_to_associate # TODO rename try_to_associate everywhere
        id = _addFile( self, id, file, title, **kwargs )
        new_file = self._getOb( id )
        #LOG( 'HTMLDocument.addFile', TRACE, '[%s] added %s="%s", %d bytes' % (self.id, id, title, len(file)) )

        if associate:
            self.associateWithAttach( id, optional=True )

        if paste and not self.associated_with_attach:
            self.pasteFile( id )

        self.notifyModified()
        self.reindexObject( idxs=['modified'] )
        return id

    security.declareProtected( CMFCorePermissions.View, 'getAssociatedAttachment' )
    def getAssociatedAttachment( self, default=None ):
        """
            Returns attachment object associated with the document text.

            Arguments:

                'default' -- optional value to return instead of None
                             if no association is set

            Result:

                Object or default value (None if not given).
        """
        id = self.associated_with_attach
        if not id:
            return default
        return self[ id ]

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'associateWithAttach' )
    def associateWithAttach( self, id, optional=False ):
        """ Set association with attachment file ONLY if we can convert file to html or text.
        """
        attachment = self[ id ]
        if optional and ( self.cooked_text or not attachment.isTextual() ):
            return False

        self.failIfLocked()

        text = attachment.CookedBody( format='html' )
        self.associated_with_attach = id
        Document._edit.im_func( self, text=text ) # self is a version
        #self.cleanup() - called by document_edit.py

        self.notifyModified()
        self.reindexObject( idxs=['SearchableText', 'modified'] )
        self._notifyOnDocumentChange()

        return True

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'removeAssociation' )
    def removeAssociation(self, id):
        """ Remove association with attachment.
        """
        if self.associated_with_attach != id:
            return

        self.failIfLocked()

        self.associated_with_attach = None
        # clear the document text
        Document._edit.im_func( self, text='' )

        self.notifyModified()
        self.reindexObject( idxs=['SearchableText', 'modified'] )
        self._notifyOnDocumentChange()

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'pasteFile' )
    def pasteFile( self, id, size=None ):
        """
            Insert the file reference into the HTML code
            Do not touch the file itself
        """
        if not id or self.text_format != 'html':
            return

        self.failIfLocked()

        ob   = self._getOb( id )
        link = ob.getId()

        if ob.implements('isImage') or ob.meta_type in ( 'Image', 'Photo' ):
            if size:
                addon = '<a href="naudoc:attach/%s" target="_blank"><img src="naudoc:attach/%s?display=%s" border="0"></a>'  % ( link, link, size or '' )
            else:
                addon = '<img src="naudoc:attach/%s" border="0">' % link
        else:
            addon = '<a href="naudoc:attach/%s" target="_blank">%s</a>' % ( link, escape( ob.title ) )

        if ob.implements('isImage') and callable(getattr(ob, 'isTIFF')) and ob.isTIFF():
            if size is not None:
                addon = '<a href="naudoc:attach/%s" target="_blank"><img src="naudoc:attach/%s?display=%s" border="0"></a>'  % ( link, link, size or '' )
            else:
                if ob.getFramesNumber() > 1:
                    result = []
                    for frame_no in range(ob.getFramesNumber()):
                        result.append( \
                            """
                            <SPAN nowrap>
                              <a href="naudoc:attach/%s/attach_img_view?frame=%d" target="_blank">
                              <img style="margin-top:20px; margin-left:10px" src="naudoc:attach/%s?display=thumbnail_frame%d" border="0"></a>
                              %d&nbsp;&nbsp;
                            </SPAN>
                            """  % ( link, frame_no, link, frame_no, frame_no+1 ) )
                    addon = '\n'.join(result)
                else:
                    addon = '<img src="naudoc:attach/%s?display=frame0" border="0">'  % link

        addon += '<br>'
        html = self.text

        # XXX there should never be body tag at all
        bodyre = re.compile( r'<body\b.*?>', re.DOTALL|re.I )
        body = bodyre.search(html)
        if not body:
            html = addon + html
        else:
            html = html[:body.end()] + addon + html[body.end():]

        self._edit( html )
        self.notifyModified()
        self.reindexObject( idxs=['SearchableText', 'modified'] )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'removeFile' )
    def removeFile( self, id ):
        """
            Removes attached file from the document together with all references to the file from the document text.

            Arguments:

                'id' -- Attachment id.

            Result:

                Document source text.
        """
        if not id:
            return

        self.failIfLocked()

        idxs = ['modified']

        if self.associated_with_attach == id:
            self.associated_with_attach = None
        elif not self.associated_with_attach:
            html = self.text
            ob   = self._getOb( id )
            if ob.implements('isImage') or ob.meta_type in ( 'Image', 'Photo' ):
                # TODO: links to images with size (see above) are not stripped
                delre = re.compile('<img[^<>]+?src=[^<>]*?%s.*?><br>' % id, re.I|re.DOTALL)
            else:
                delre = re.compile('<a([^<>]+?)href=([^<>]*?)%s(.*?)>(.*?)</a><br>' % id, re.I|re.DOTALL)

            if ob.implements('isImage') and callable(getattr(ob, 'isTIFF')) and ob.isTIFF():
                if ob.getFramesNumber() > 1:
                    delre = re.compile(r'<span[^<>]*>\s*<a[^<>]+?href=[^<>]*?%s\W+[^<>]*>\s*<img[^<>]+?src=[^<>]*?%s\W+.*?</span>\s*(?:<br>)*' % (id, id), re.I|re.DOTALL)
                else:
                    delre = re.compile('<img[^<>]+?src=[^<>]*?%s\W+.*?><br>' % id, re.I|re.DOTALL)

            html = delre.sub('', html)
            Document._edit.im_func( self, text=html )  # self is a version
            idxs.append('SearchableText')

        self.manage_delObjects( id )
        self.notifyModified()
        self.reindexObject( idxs=idxs )
        self._notifyOnDocumentChange()

    def _notifyAttachChanged(self, id):
        """
            Notifies document that particular attachment file was changed.

            Arguments:

                'id' -- Attachment file id.

            In case the attachment file is associated with the document's editable
            version, file contents will be converted and inserted into the
            version text.
        """
        idxs = ['modified']
        if self.associated_with_attach == id:
            #this is textual document
            #try to convert document text to html
            try:
                text = self[ id ].CookedBody( format='html' )
            except Exceptions.ConverterError:
                text = self.cooked_text
            Document._edit( self, text=text )
            self.cleanup()
            idxs.append('SearchableText')
            self._notifyOnDocumentChange()
        self.notifyModified()
        self.reindexObject( idxs=idxs )

    def _containment_onAdd( self, item, container ):
        # placement callback
        # XXX fix permissions for versionable
        for perm in self._versionable_perms:
            delattr( self, perm )

    def _instance_onClone( self, source, item ):
        # copy callback
        owner = item.getOwner()
        if owner is not None:
            self.changeOwnership( owner.getUserName() )

        self.registry_data = {}
        self.reindexObject( idxs=['registry_ids'] )

        # if working member is not owner of principal version, create a new one
        user = _getAuthenticatedUser( self )
        if not isinstance( user, SpecialUser ): # scheduler check
            version = self.getVersion()
            if user.getId() not in version.getVersionOwners():
                self.createVersion( version.id, title=version.title, description=version.description )

    def _instance_onDestroy( self ):
        # destructor callback

        # XXX place this in SimpleNauItem._instance_onDestroy
        self.setPresentationLevel( None )

        # if the document has subordinates, it cannot be deleted
        if self.listSubordinateDocuments():
            raise Exceptions.BeforeDeleteError( message="Can't delete document, because it has subordinate documents." )

        # release link to the primary document
        self.setPrimaryDocument( None )

    def _notifyOfCopyTo( self, container, op=0 ):
        """
            Pre-copy/move operation notification.

            Arguments:

                'container' -- Object container.

                'op' -- Operation type indicator. Can take the value of either
                        1 for the move operation or 0 for the copy
                        operation.
        """
        if op == 1: # move operation
            self.failIfLocked()

    def notifyWorkflowCreated( self ):
        """
            Notifies the workflow that *self* was just created.
        """
        Document.notifyWorkflowCreated( self )
        self.reindexObject( idxs=['state'] )

    def reindexObject( self, idxs=[], versionable=True ):
        """
            Reindexes the document and/or its version.
        """
        if self._versionable_onReindex( idxs, versionable ):
            SimpleNauItem.reindexObject.im_func( self, idxs )

    def _instance_onMove(self):
        # move callback
        for id, attachment in self.listAttachments():
            if attachment.implements('isItem'):
                attachment._instance_onMove()

    def objectIds( self, spec=None ):
        ids = ObjectManager.objectIds(self, spec)
        followup = ( hasattr( aq_base( self ), 'followup' ) and
                      self.followup or None )
        if followup is not None:
            ids.append('followup')
        return ids

    security.declareProtected( CMFCorePermissions.View, 'listAttachments' )
    def listAttachments( self ):
        """
            Returns a list of the document's file attachments.

            Result:

                List of (id, attachment) pairs.
        """
        return [i for i in self.objectItems() if i[0] not in ['followup','version']]

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'lockAttachment' )
    def lockAttachment(self, id):
        """
            Locks attachment file so it cannot be modified by another user.

            Arguments:

                'id' -- File id.

            Result:

                Message string.
        """
        self.failIfLocked()

        file = self[ id ]
        if not _checkPermission( CMFCorePermissions.ModifyPortalContent, file ):
            return 0

        file.manage_permission( CMFCorePermissions.ModifyPortalContent, ())
        file.manage_permission( ZopePermissions.delete_objects, ())
        return 1

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'PUT' )
    def PUT( self, REQUEST, RESPONSE ):
        """
            Handle HTTP (and presumably FTP?) PUT requests
        """
        # TODO fix characters in REQUEST.BODY
        body = REQUEST.get('BODY', '')
        guessedformat = REQUEST.get_header('Content-Type', 'text/plain')
        ishtml = (guessedformat == 'text/html') or html_headcheck(body)

        if ishtml: self.setFormat('text/html')
        else: self.setFormat('text/plain')

        body = HTMLCleaner(body)

        try:
            headers, body, format = self.handleText(text=body)
            safety_belt = headers.get('SafetyBelt', '')
            self.setMetadata(headers)
            self._edit(text=body, safety_belt=safety_belt)
        except 'EditingConflict', msg:
            # XXX Can we get an error msg through?  Should we be raising an
            #     exception, to be handled in the FTP mechanism?  Inquiring
            #     minds...
            transaction.abort()
            RESPONSE.setStatus(450)
            return RESPONSE
        except Exceptions.ResourceLockedError, msg:
            transaction.abort()
            RESPONSE.setStatus(423)
            return RESPONSE

        RESPONSE.setStatus(204)
        self.reindexObject()
        return RESPONSE

    security.declarePublic('registry_ids')
    def registry_ids(self):
        """
            Used by catalog.
        """
        return getattr(self, 'registry_data', {}).keys()

    security.declareProtected( CMFCorePermissions.View, 'isSubscribed' )
    def isSubscribed(self, transition_id=Missing, REQUEST=None):
        """
            Checks that current user is subscribed for document changes

            Arguments:

               'transition_id' -- Transition id to check. Default value :
                    MagicSaveTransition, which means to check whether the
                    current user is subscribed on notifications about
                    document changes.

               'REQUEST' -- Zope REQUEST object.

            Result:

                Boolean.
        """
        membership_tool = getToolByName( self, 'portal_membership' )
        if membership_tool.isAnonymousUser(): return 0

        if transition_id is Missing:
            transition_id = MagicSaveTransition

        transitions = self.subscribed_users.get( membership_tool.getAuthenticatedMember().getUserName(), [] )
        return transition_id in transitions

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'getUserSubscription' )
    def getUserSubscription(self, username):
        """
            Returns tuple of transitions on which user want to receive notifications.

            Arguments:

                'username' -- user id
        """
        return tuple(self.subscribed_users.get( username, []))

    security.declareProtected( CMFCorePermissions.View, 'subscribe' )
    def subscribe(self, REQUEST=None):
        """
            Subscribe user for document changes
        """
        membership_tool = getToolByName( self, 'portal_membership' )
        if membership_tool.isAnonymousUser():
            return

        uname = membership_tool.getAuthenticatedMember().getUserName()

        subscribe_save = REQUEST.get('changes') and [ MagicSaveTransition ] or []
        transitions = REQUEST.get('transitions', []) + subscribe_save


        message = "You have subscribed for notifications about document changes"

        if transitions:
            self.subscribed_users[ uname ] = transitions
        else:
            try:
                del self.subscribed_users[ uname ]
            except KeyError:
                pass
            message = "You have unsubscribed from notifications about document changes"

        self._p_changed = 1

        return REQUEST.RESPONSE.redirect( self.absolute_url( action='view',
                                                             message=message ) )

    security.declareProtected( CMFCorePermissions.View, 'listSubscribedUsers' )
    def listSubscribedUsers(self):
        """
            Returns tuple of subscribed users ids that still exist as members
        """
        membership_tool = getToolByName( self, 'portal_membership' )
        deleted_users = []

        for user in self.subscribed_users.keys():
            if not membership_tool.getMemberById(user):
                deleted_users.append(user)

        # remove deleted users from list of subscribed
        for d_user in deleted_users:
            del self.subscribed_users[ d_user ]

            #self.subscribed_users = [ user for user in self.subscribed_users if user not in deleted_users ]
        self._p_changed = 1

        return tuple(self.subscribed_users.keys())

    security.declarePrivate( '_notifyOnDocumentChange' )
    def _notifyOnDocumentChange(self):
        """
            Notifies subscribed users that document is changed
        """
        membership = getToolByName( self, 'portal_membership' )
        emails = []

        if membership.isAnonymousUser():
            current_user = None
        else:
            current_user = membership.getAuthenticatedMember().getMemberName()

        for user in self.listSubscribedUsers():

            if user == current_user: continue

            if MagicSaveTransition not in self.getUserSubscription( user ):
                continue

            # building emails list for subscribed users that have permission to view this document
            member = membership.getMemberById( user, containment = True )
            #email = member and member.has_permission(CMFCorePermissions.View, self) and member.getMemberEmail()
            email = member and member.getMemberEmail()
            if email: emails.append(email)

        if emails:
            mailhost = getToolByName( self, 'MailHost' )
            links = getToolByName( self, 'portal_links' )

            url = links.absolute_url( action='locate'
                                    , params={'uid':self.getUid()}
                                    , canonical=1 )
            subscription_url = links.absolute_url( action='locate'
                                    , params={'uid':self.getUid()
                                             ,'action':'manage_document_subscription'}
                                    , canonical=1 )

            mailhost.sendTemplate( 'document_subscription_announce'
                                 , emails
                                 , restricted=Trust
                                 , raise_exc=0 
                                 , doc_title=self.title_or_id()
                                 , doc_descr=self.Description()
                                 , user=current_user
                                 , url=url
                                 , subscription_url=subscription_url
                                 )

    security.declarePublic( 'distributeDocument' )
    def distributeDocument( self, template, mto=None, mfrom=None, subject=None, from_member=None, namespace=None, REQUEST=None, lang=None, raise_exc=Missing, letter_parts=[], letter_type=None, **kw ):
        """
          distribute document
          letter_content - is array with values of what to distribute
                           (see 'skins/distribute_document_form.dtml')

          in self.distribution_log are stored log about document's distribution
        """

        source_link = self.absolute_url(canonical=1)
        source_title = self.Title()

        mail = getToolByName( self, 'MailHost' )
        portal_membership = getToolByName( self, 'portal_membership' )

        if letter_type == 'as_is':
            msg  = mailFromDocument( self, factory=mail.createMessage )
        else:

            msg  = mail.createMessage( 'text/plain', multipart=1 )

            document_attachment_list = []
            lang_info = getLanguageInfo( self )
            if 'attachment' in letter_parts:
                # Attaches
                for id, file in self.listAttachments():
                    ctype = file.getContentType()
                    fname = file.getProperty('filename') or file.getId()
                    document_attachment_list.append( fname )

                    item = MailMessage( ctype or Config.DefaultAttachmentType )
                    msg.attach( item, filename=fname )

                    item.set_payload( file.RawBody() )

            skins = getToolByName( self, 'portal_skins' )
            try:
                letter_text = getattr( aq_base( skins['mail_templates'] ), template )
            except AttributeError:
                raise KeyError, template

            text = letter_text( self, namespace or REQUEST,
                                lang=lang,
                                document_attachment_list=document_attachment_list,
                                source_link=source_link,
                                letter_parts=letter_parts,
                                **kw
                              )

            fmt = self.Format()

            msg.get_body().from_text( text )

            if 'body' in letter_parts:
                #Document body
                item = MailMessage( fmt, charset=mail.getOutputCharset( self.Language() ) )
                msg.attach( item, inline=1, filename='letter.html', location='letter' )

                item.set_payload( self.FormattedBody( html=0, width=76, canonical=1 ) )

            if 'metadata' in letter_parts:
                #Metadata
                item = MailMessage(fmt, charset=mail.getOutputCharset( self.Language() ) )
                msg.attach( item, inline=1, filename='metadata.html', location='metadata' )

                try:
                    metadata_template = getattr( aq_base( skins['mail_templates'] ), 'metadata_template' )
                except AttributeError:
                    raise KeyError, template
                metadata = metadata_template( self, namespace or REQUEST, lang=lang, charset=getLanguageInfo( lang )['http_charset'], **kw )
                item.set_payload( metadata )

        # store event to log
        ts = str(int(DateTime()))
        member = portal_membership.getAuthenticatedMember()
        who_id = member.getId()
        log_id = len(self.distribution_log)

        self.distribution_log.append( { 'date'       : ts
                                      , 'message'    : msg
                                      , 'who_id'     : who_id
                                      , 'recipients' : mto
                                      , 'log_id'     : log_id
                                      } )
        self._p_changed = 1

        mto = portal_membership.listPlainUsers( mto, context=self )

        return self.MailHost.send( msg, mto, mfrom, subject, from_member=from_member, raise_exc=raise_exc )


    security.declarePublic( 'receiveMailCopyFromDistributionLog' )
    def receiveMailCopyFromDistributionLog( self, REQUEST ):
        """
           receive copy email-message from distribution log
        """
        log_id = REQUEST.get('mail_to_receive')
        msg = self.distribution_log[int(log_id)]['message']
        mailhost = aq_get( self, 'MailHost', None, 1 )
        membership_tool = getToolByName( self, 'portal_membership' )
        user_email = membership_tool.getAuthenticatedMember().getProperty('email')
        mailhost.send( msg, [user_email] )
        return REQUEST.RESPONSE.redirect( self.absolute_url( action='distribution_log_form',
                                                             message="The email is sent." ) )


    def manage_FTPget( self, REQUEST=None, RESPONSE=None ):
        """
            Get the document body for FTP download (also used for the WebDAV SRC)
        """
        hdrlist = self.getMetadataHeaders()

        if self.text_format == 'html':
            lang    = self.Language()
            charset = getLanguageInfo( lang )['http_charset']
            hdrtext = '<meta http-equiv="Content-Type" content="text/html; charset=%s" />' % charset

            for name, content in hdrlist:
                if name.lower() == 'title':
                    continue
                hdrtext += '\n<meta name="%s" content="%s" />' % \
                           ( name, escape( str(content), 1 ) )

            bodytext = _formattedBodyTemplate % {
                        'title'     : escape( self.Title() ),
                        'head'      : hdrtext,
                        'style'     : '',
                        'language'  : lang,
                        'font'      : self.getFontFamily(),
                        'body'      : self.EditableBody(),
                    }
        else:
            hdrtext  = formatRFC822Headers( hdrlist )
            bodytext = '%s\r\n\r\n%s' % ( hdrtext, self.text )

        return bodytext

    security.declareProtected( CMFCorePermissions.View, 'getChangesFrom' )
    def getChangesFrom( self, other, text = None ):
        """
            Returns HTML diff between *other* and this version.

            Arguments:

                'other' -- version object to compare against
                'text'  -- text to compare against

            Result:

                String containing HTML code.
        """
        current = self.getCurrentVersionId()

        # XXX should we check permissions on *other*?
        self.makeCurrent()
        b = self.CookedBody()
        if text != None:
            return HTMLDiff( b, text )

        other.makeCurrent()
        a = other.CookedBody()

        # restore selected version
        self.getVersion( current ).makeCurrent()

        return HTMLDiff( a, b )


    security.declareProtected( CMFCorePermissions.View, 'getWorkflowHistory' )
    def getWorkflowHistory( self, include_subordinates=None ):
        """
            Returns workflow history for the document.

            Arguments:

                'include_subordinates'     --  if true, the method follows links
                                            to all subordinate documents

            Result:

                Dictionary
                {   'object':       document version object,
                    'action_date':  action_date,
                    'state':        state
                }
        """

        wf_tool = getToolByName(self, 'portal_workflow')
        ct_tool = getToolByName(self, 'portal_catalog')

        wf = self.getCategory().getWorkflow()

        result = []

        for ver_id in self.listVersions():
            obj = self.getVersion(ver_id['id'])
            if hasattr(obj, 'workflow_history'):
                all_history = getattr(obj, 'workflow_history')
                history = all_history.get(wf.getId())
                if history:
                    for item in history:
                        entry = {}
                        entry['object'] = obj
                        entry['action_date'] = item['time']
                        entry['state'] = wf_tool.getStateTitle(wf.getId(), item['state'])
                        result.append(entry)

        if include_subordinates:
            for doc_uid in self.listSubordinateDocuments():
                doc = ct_tool.getObjectByUid(doc_uid)
                if doc:
                    result = result + doc.getWorkflowHistory()

        result.sort(lambda a,b: cmp(a['action_date'], b['action_date']))
        return result

    def listTabs(self):
        """
            See Feature.hasTabs interface
        """
        REQUEST = aq_get(self, 'REQUEST')
        msg = getToolByName( self, 'msg' )
 
        tabs = []
        append_tab = tabs.append

        type = self.getTypeInfo()
        link = REQUEST.get('link', '')
     
        action = type.getActionById( 'view' )
        append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                    , 'title' : msg('View')
                    } )
        if link.find('view') >= 0:
            tabs[-1]['selected'] = True

        editable = self.getEditableVersion(latest=0, wrap_selected=False)
        if editable:
            action = type.getActionById( 'edit' )
            append_tab( { 'url' : editable.relative_url( action=action, frame='inFrame'  )
                        , 'title' : msg('Edit')
                        } )
            if link.find(action) >= 0:
                tabs[-1]['selected'] = True

        action=type.getActionById( 'metadata' )
        append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                    , 'title' : msg('Metadata')
                    } )
        if link.find(action) >= 0:
            tabs[-1]['selected'] = True
            tabs[-1]['selected_color'] = '#ffffff'

        action=type.getActionById( 'attachments' )
        attachCounts=len( self.listAttachments() )
        append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                    , 'title' : msg('Attachments') + ' ('+ ( msg('n/a'), str(attachCounts) )[attachCounts > 0] +')' 
                    } )
        if link.find(action) >= 0:
            tabs[-1]['selected'] = True
            tabs[-1]['selected_color'] = '#ffffff'
   
        if 'NormativeDocument' in self.hasBase():
            holdersCount=len( self.listCopiesHolders() )
            append_tab( { 'url' : self.relative_url( action='document_copies_holders_form', frame='inFrame' )
                        , 'title' : msg('Copies holders') + ' ('+ ( msg('n/a'), str(holdersCount) )[holdersCount > 0] +')'
                        } )
            if link.find('copies_holders') >= 0:
                tabs[-1]['selected'] = True
                tabs[-1]['selected_color'] = '#ffffff'
       
        category = self.getCategory()
        if category.getId() == 'NormativeDocument' and category.listSubordinateCategories():
            append_tab( { 'url' : self.relative_url( action='document_primary_category_changes_form', frame='inFrame' )
                        , 'title' : msg('Changes')
                        } )
            if link.find('primary_category_changes') >= 0:
                tabs[-1]['selected'] = True
                tabs[-1]['selected_color'] = '#ffffff'

        action = type.getActionById( 'followup' )

        total = len(self.followup.getBoundTasks())

        append_tab( { 'url' : self.relative_url( action=action, frame='inFrame' )
                    , 'title' : msg('Tasks')+' ('+ ( msg('n/a'), str(total) )[total>0] +')'
                    } )
        if link.find(action) >= 0:
            tabs[-1]['selected'] = True
            tabs[-1]['selected_color'] = '#ffffff'
  
        if self.getSite() and self.isPublished() \
           and _checkPermission( Config.Permissions.PublishPortalContent, self ):
            append_tab( { 'url' : self.relative_url( action='document_presentation_form', frame='inFrame')
                        , 'title' : msg('Web presentation') 
                        } )
            if link.find('presentation') >= 0:
                tabs[-1]['selected'] = True

        commentsCount=hasattr(self, 'talkback') and self.talkback.replyCount( self ) or 0
        append_tab( { 'url' : self.relative_url( action='document_comments', frame='inFrame')
                     , 'title' : msg('Comments') + ' ('+ ( msg('n/a'), str(commentsCount) )[commentsCount > 0] +')' 
                     } )
        if link.find('document_comments') >= 0 or link.find('discussion_reply_form') >= 0:
            tabs[-1]['selected'] = True

        if _checkPermission( CMFCorePermissions.View, self ):
            versions_count = len( self.listVersions() )
            append_tab( { 'url' : self.relative_url( action='document_versions_form', frame='inFrame')
                        , 'title' : msg('Versions') + ' ('+ ( msg('n/a'), str(versions_count) )[versions_count > 0] +')'
                        } )
            if link.find('versions') >= 0:
                tabs[-1]['selected'] = True

        return tabs

    security.declareProtected(CMFCorePermissions.View, 'getField')
    def getField(self, name, template_type = 'view'):
        """
            Returns field template
        """
        _ = getToolByName(self, 'msg')
        try:
            attribute = self.getCategory().getAttributeDefinition(name)
        except KeyError:
            title = ""
            field = '(%s)' % \
                    _("field '%s' was removed from document category") % \
                    name
        else:
            title = attribute.Title()

            if self.checkAttributePermissionView(attribute):
                field = attribute.getViewFor(self.getVersion(), template_type)
            else:
                field = '(%s)' % \
                        _("you are not allowed to read field '%s'") % \
                        name

        return '<span class="category-attribute" id="field:%s" title="%s">%s</span>' % \
                    (name, title, field)

    security.declareProtected(CMFCorePermissions.View, 'getHeadingInfo')
    def getHeadingInfo(self):
        msg = getToolByName( self, 'msg' )
        version = self.getVersion()
        title = '%s / %s %s' % (version.Title() or version.id, msg('Current version is'), version.getVersionNumber())

        return title

InitializeVersionableClass( HTMLDocument )
InitializeClass( HTMLDocument )


_formattedBodyTemplate = """
<html>
<head>
%(head)s
<title>%(title)s</title>
<style type="text/css">
body {
    font-family: %(font)s;
    color: black;
}
body, table {
    font-size: 12px;
}
</style>
%(style)s
</head>
<body lang="%(language)s">
%(body)s
</body>
</html>
"""

MagicSaveTransition = '__save__'


def addHTMLDocument( self, id, title=None, attachments=(), attachment_associate=None,
                     category=None, category_template=None, REQUEST=None, **kwargs ):
    """
        Adds an HTML document.

        Keyword arguments (in addition to Dublin Core ones):

            'attachments' -- list of file objects to attach to the document

            'attachment_associate' -- index of file in the 'attachments' list
                                      to associate the document's text with

            'category' -- category of the document; either object or Id (required)

            'category_primary' -- primary object if the 'category' is subordinate

            'category_template' -- Id of the category template if other than default
                                   one should be used

            'category_attributes' -- mapping from attribute name to values
    """
    if category:
        metadata = getToolByName( self, 'portal_metadata' )
        catobj = metadata.getCategoryById( category )

        if catobj and catobj.isContentFixed():
            attachment_associate = None

        elif attachment_associate is not None:
            category_template = None

    obj = HTMLDocument( id, title, category=category,
                        category_template=category_template, **kwargs )

    self._setObject( id, obj )
    obj = self._getOb( id )

    associate_id = None

    for idx in range( len(attachments) ):
        file = attachments[ idx ]
        params = {}
        if isinstance( file, TupleType ):
            file, params = file

        new_id = obj.addFile( file, **params )
        if idx == attachment_associate:
            associate_id = new_id

    if associate_id:
        obj.associateWithAttach( associate_id )

def initialize( context ):
    # module initialization callback
    context.registerContent( HTMLDocument, addHTMLDocument, HTMLDocumentType )
