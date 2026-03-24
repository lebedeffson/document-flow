"""
Global settings for the NauDoc product.

$Editor: vpastukhov $
$Id: Config.py,v 1.122 2006/10/06 13:20:12 oevsegneev Exp $
"""
__version__ = '$Revision: 1.122 $'[11:-2]

ProductName             = 'CMFNauTools'

DisableMigration        = 0
MigrationRecursionLimit = 3000
MigrationSubtransactionThreshold = 1000

AutoUpdateObjects       = 1
AutoUpgradeObjects      = 1
AutoUpdateRemote        = 0

BindClassAttributes     = 0

DisableAccessRestrictions = 0

EnableUndo              = 0
EnableDeferredSendMail  = 1
EnableFSStorage         = 0

FSStorageFormat         = '%y', '%m', '%d'

# XXXXX
Use27CatalogQuery       = 0

MaxErrorLogEntries      = 100
MaxTracebackDepth       = 50
MaxArgumentsDepth       = 0
MaxVariablesDepth       = 3
MaxObjectReprLength     = 200

AddonsPackageName       = 'Addons'

DefaultAttachmentType   = 'application/octet-stream'

ErrorReportAddress      = 'naudoc-bugs@naumen.ru'

MailerName              = 'NauMail'
MailInboxName           = 'INBOX'
MailDefaultInterval     = 15
MailDefaultCategory     = 'IncomingMail'


DefaultGroups           = [
                            {
                              'id' : 'all_users',
                              'title' : 'All users',
                            },
                          ]

GroupAccessPolicy       = 'all'

WindowsIntegratedAuth   = [ 'ntlm', 'negotiate' ]

SystemFolders           = [
                            {
                                'path'  : 'storage',
                                'title' : 'Content storage',
                                'permissions' : [ ('List folder contents', ['Owner','Manager', 'Editor', 'Writer', 'Reader', 'Author'], 0),
                                                  ('View', ['Owner','Manager', 'Member'], 1) ],
                            },
                            {
                                'path'  : 'storage/members',
                                'title' : 'Home folders',
                                'property' : 'members_folder',
                            },
                            {
                                'path'  : 'storage/members/user_defaults',
                                'title' : 'Default content',
                                'property' : 'defaults_folder',
                                'optional' : 1,
                            },
                            {
                                'path'  : 'storage/system',
                                'title' : 'System folders',
                                'roles' : [ ('all_users', ['Reader'], 1) ],
                            },
                            {
                                'path'  : 'storage/system/templates',
                                'title' : 'Document templates',
                                'property' : 'templates_folder',
                            },
                            {
                                'path'  : 'storage/system/messages',
                                'title' : 'Message templates',
                                'property' : 'messages_folder',
                            },
                            {
                                'path'  : 'storage/system/scripts',
                                'title' : 'Scripts',
                                'property' : 'scripts_folder',
                            },
                            {
                                'path'  : 'storage/system/directories',
                                'title' : 'Directories',
                                'property' : 'directories_folder',
                            },
                          ]

PersonalFolders         = [
                            {
                                'id' : 'favorites',
                                'title' : 'Favorites',
                            },
                            {
                                'id' : 'searches',
                                'title' : 'Search profiles',
                            },
                          ]

SaveImageFrames         = 0 #should ImageAttachment store rendered frames (in case of multi-framed tiff)
SaveImageDisplays       = 1 #should ImageAttachment store rendered displays

AllowChangeCategory     = 0

NormativeDocumentEffectiveStatus = 'effective'
NormativeDocumentCategory = 'NormativeDocument'

WorkflowChains          = {
                            '__default__' : [
                                'HTMLDocument', 'DTMLDocument', 'Discussion',
                                'Site Image', 'Voting', 'Tabular Report', 'Shortcut',
                                'Heading', 'Storefront',
                                'Incoming Mail Folder', 'Outgoing Mail Folder',
                            ],
                          }

AllowedColumnTypes      = {
                            'boolean':1, 'date':1, 'float':1, 'int':1,  'currency':1,
                            'string':1,  'text':1, 'lines':1, 'file':1, 'link':1,
                          }

DefaultColumnType       = 'string'

DocumentLinkProperties  = [ 'Title', 'Creator' ]

FileExtensionMap        = {
                            'txt'       : 'text/plain',
                            'js'        : 'text/javascript',
                            'css'       : 'text/css',
                            'ico'       : 'image/x-icon',
                            'doc'       : 'application/msword',
                            'pdf'       : 'application/pdf',
                          }

SitePresentationLevels  = [
                            {
                                'title'     : 'Ordinary object',
                                'max_count' : 0
                            },
                            {
                                'title'     : 'Primary news',
                                'max_count' : 1
                            },
                            {
                                'title'     : 'Secondary news',
                                'max_count' : 3
                            },
                            {
                                'title'     : 'Download page',
                                'max_count' : 0
                            },
                          ]

PortalTools             = [] # here tools meta_types lives stored by registerTool.

SiteTools               = [ 'NauSite Actions Tool'
                          , 'NauSite Skins Tool'
                          , 'NauSite Undo Tool'
                          , 'NauSite URL Tool'
                          , 'NauSite Properties Tool'
                          , 'NauSite Types Tool'
                          ]

ActionProviders         = [] # here lives ids of the action-provider-tools

SiteActionProviders     = [ 'portal_membership'
                          , 'portal_actions'
                          , 'portal_registration'
                          , 'portal_discussion'
                          , 'portal_undo'
                          , 'portal_workflow'
                          , 'portal_properties'
                          ]

CatalogTools            = [] # here lives ids of tools with ZCatalog interface

PublicViews             = [ 'public', 'gui' ]
#SkinViews               = [ 'public', 'gui', 'common', 'calendar', 'portal',
#                            'discussions', 'htmldocument', 'vdocument', 'report',
#                            'registry', 'tasks', 'voting', 'heading', 'categories',
#                            'docflow_report', 'docflow_script','registration_book',
#                            'membership', 'mail_templates', 'addons',
#                            'fs_objects', 'explorer', 'subscription', 'scheduler'
#                          ]
SkinViews               = [] # dynamically collected from %Product_dir%/skins directory in __init__


#SiteSkinViews           = [ 'site_mandatory', 'site_common', 'site_images' ]
SiteSkinViews           = [] # dynamically collected from %Product_dir%/skins directory in __init__

DefaultLanguage         = 'en'

Languages               = { 'en' : {
                                'title'          : 'English',
                                'posix_locale'   : 'en_US.ISO8859-1',
                                'win32_locale'   : 'English_United States.1252',
                                'http_charset'   : 'iso-8859-1',
                                'mail_charset'   : 'iso-8859-1',
                                'python_charset' : 'iso8859-1',
                                'general_font'   : 'Verdana, Arial, Helvetica, sans-serif',
                                'message_font'   : 'Arial, Verdana, Helvetica, sans-serif',
                                'input_font'     : 'Verdana, Arial, Helvetica, sans-serif',
                                'symbol_font'    : 'Times New Roman, Times, serif',
                                'title_font'     : 'Arial, Verdana, Helvetica, sans-serif',
                                'document_font'  : 'Verdana, Arial, Helvetica, sans-serif',
                                'date_format'    : '%Y/%m/%d',
                                'datetime_format': '%Y/%m/%d %H:%M',

                            },

                            'ru' : {
                                'title'          : 'Russian',
                                'posix_locale'   : 'ru_RU.CP1251',
                                'win32_locale'   : 'Russian_Russia.1251',
                                'http_charset'   : 'windows-1251',
                                'mail_charset'   : 'koi8-r',
                                'python_charset' : 'cp1251',
                                'general_font'   : 'Verdana, Arial, Helvetica, sans-serif',
                                'message_font'   : 'Arial, Verdana, Helvetica, sans-serif',
                                'input_font'     : 'Verdana, Arial, Helvetica, sans-serif',
                                'symbol_font'    : 'Times New Roman, Times, serif',
                                'title_font'     : 'Arial, Verdana, Helvetica, sans-serif',
                                'document_font'  : 'Verdana, Arial, Helvetica, sans-serif',
                                'date_format'    : '%d.%m.%Y',
                                'datetime_format': '%d.%m.%Y %H:%M',
                            },

                            'kk' : {
                                'title'          : 'Kazakh',
                                'posix_locale'   : 'ru_RU.CP1251',
                                'win32_locale'   : 'Kazakh_Kazakstan.1251',
                                'http_charset'   : 'windows-1251',
                                'mail_charset'   : 'windows-1251',
                                'python_charset' : 'cp1251',
                                'general_font'   : 'KZ Arial',
                                'message_font'   : 'KZ Arial',
                                'input_font'     : 'KZ Arial',
                                'symbol_font'    : 'Times New Roman, Times, serif',
                                'title_font'     : 'KZ Arial',
                                'document_font'  : 'KZ Arial',
                                'date_format'    : '%d.%m.%Y',
                                'datetime_format': '%d.%m.%Y %H:%M',

                            },
                          }

CharsetEntityMap        = {
                            'windows-1251' : {
                                '\x91' : '&lsquo;',
                                '\x92' : '&rsquo;',
                                '\x93' : '&ldquo;',
                                '\x94' : '&rdquo;',
                                '\xAB' : '&laquo;',
                                '\xBB' : '&raquo;',
                                '\x85' : '&hellip;',
                                '\x88' : '&euro;',
                                '\x95' : '&bull;',
                                '\x96' : '&ndash;',
                                '\x97' : '&mdash;',
                                '\x99' : '&trade;',
                                '\xA9' : '&copy;',
                                '\xAE' : '&reg;',
                                '\xA7' : '&sect;',
                                '\xB0' : '&deg;',
                                '\xB1' : '&plusmn;',
                                '\xB9' : '&#8470;',
                            },
                          }

LanguageEntitiesMap     = {
                            'kk' : {
                                '&#1240;' : '\xAA',
                                '&#1186;' : '\x8C',
                                '&#1170;' : '\x81',
                                '&#1198;' : '\x87',
                                '&#1200;' : '\xA6',
                                '&#1178;' : '\x8D',
                                '&#1256;' : '\xA4',
                                '&#1210;' : '\x8E',
                                '&#1241;' : '\xBA',
                                '&#1187;' : '\x9C',
                                '&#1171;' : '\x83',
                                '&#1199;' : '\x89',
                                '&#1201;' : '\xB1',
                                '&#1179;' : '\x9D',
                                '&#1257;' : '\xB5',
                                '&#1211;' : '\x9E',
                            },
                          }

TransliterationMap      = {
                            'ru' : {
                                # transliteration from CP1251 (Russian) text [GOST 16876-71]
                                # differences from GOST - hard (") and soft (') signs are replaced to empty strings
                                '\xc0':'A',  '\xc1':'B',   '\xc2':'V', '\xc3':'G', '\xc4':'D', '\xc5':'E',  '\xc6':'Zh', '\xc7':'Z',
                                '\xc8':'I',  '\xc9':'Jj',  '\xca':'K', '\xcb':'L', '\xcc':'M', '\xcd':'N',  '\xce':'O',  '\xcf':'P',
                                '\xd0':'R',  '\xd1':'S',   '\xd2':'T', '\xd3':'U', '\xd4':'F', '\xd5':'Kh', '\xd6':'C',  '\xd7':'Ch',
                                '\xd8':'Sh', '\xd9':'Shh', '\xda':'' , '\xdb':'Y', '\xdc':'',  '\xdd':'Eh', '\xde':'Ju', '\xdf':'Ja',
                                '\xe0':'a',  '\xe1':'b',   '\xe2':'v', '\xe3':'g', '\xe4':'d', '\xe5':'e',  '\xe6':'zh', '\xe7':'z',
                                '\xe8':'i',  '\xe9':'ji',  '\xea':'k', '\xeb':'l', '\xec':'m', '\xed':'n',  '\xee':'o',  '\xef':'p',
                                '\xf0':'r',  '\xf1':'s',   '\xf2':'t', '\xf3':'u', '\xf4':'f', '\xf5':'kh', '\xf6':'c',  '\xf7':'ch',
                                '\xf8':'sh', '\xf9':'shh', '\xfa':'',  '\xfb':'y', '\xfc':'',  '\xfd':'eh', '\xfe':'ju', '\xff':'ja',
                                '\xa8':'Jo', '\xb8':'jo',
                            },

                            'kk' : ( 'ru', {} ),
                        }

TextIndexNG2Options     = {
                            'splitter_separators' : '.+-_@',
                            'autoexpand'          : 1,
                            'truncate_left'       : 1,
                            'splitter_single_chars': 1,
                        }

NavTreeMenu             = 'navTree'
FollowupMenu            = 'followup_menu'
UserMenu                = 'user'
GlobalMenu              = 'global'
SearchMenu              = 'search'
ArchTreeMenu            = 'ArchTree'
HelpMenu                = 'help'
FavoritesMenu           = 'favorites'

MenuDefault             = 'navTree'

Months                  = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

Icon2FileMap            = {
                            'gif'  : 'image_icon.gif',
                            'jpg'  : 'image_icon.gif',
                            'txt'  : 'doc_icon.gif',
                            'doc'  : 'word_icon.gif',
                            'htm'  : 'doc_icon.gif',
                            'html' : 'doc_icon.gif',
                          }

LDAPSchema              = {
                            'cn' : {
                                'ldap_name'     : 'cn',
                                'friendly_name' : 'Canonical Name',
                                'public_name'   : 'fullname',
                            },

                            'sn' : {
                                'ldap_name'     : 'sn',
                                'friendly_name' : 'Last Name',
                                'public_name'   : 'lname',
                            },

                            'givenName' : {
                                'ldap_name'     : 'givenName',
                                'friendly_name' : 'First Name',
                                'public_name'   : 'fname',
                            },

                            'uid' : {
                                'ldap_name'     : 'uid',
                                'friendly_name' : 'User Identifier',
                                'public_name'   : '',
                            },

                            'mail' : {
                                'ldap_name'     : 'mail',
                                'friendly_name' : 'E-mail Address',
                                'public_name'   : 'email',
                            },

                            'o' : {
                                'ldap_name'     : 'o',
                                'friendly_name' : 'Organization',
                                'public_name'   : 'company',
                            },

                            'description' : {
                                'ldap_name'     : 'description',
                                'friendly_name' : 'Description',
                                'public_name'   : 'notes',
                            },

                            'telephoneNumber' : {
                                'ldap_name'     : 'telephoneNumber',
                                'friendly_name' : 'Phone Number',
                                'public_name'   : 'phone',
                            },
                          }


#===========================================================================

from AccessControl import Permissions as ZopePermissions
from Products.CMFCore import CMFCorePermissions

try: from Products.ExternalEditor import ExternalEditorPermission as UseExternalEditorPerm
except ImportError: UseExternalEditorPerm = 'Use external editor'

AnonymousRole                   = 'Anonymous'
MemberRole                      = 'Member'
ManagerRole                     = 'Manager'
VisitorRole                     = 'Visitor'
LockedRole                      = 'Locked'
OrphanedRole                    = 'Orphaned'
ActiveRole                      = 'Active'

OwnerRole                       = 'Owner'
EditorRole                      = 'Editor'
ReaderRole                      = 'Reader'
WriterRole                      = 'Writer'
AuthorRole                      = 'Author'
VersionOwnerRole                = 'VersionOwner'

PortalRoles                     = ( MemberRole, VisitorRole, EditorRole, WriterRole, ReaderRole, AuthorRole, VersionOwnerRole, LockedRole, ActiveRole )
ManagedLocalRoles               = ( EditorRole, ReaderRole, WriterRole, AuthorRole )
ManagedRoles                    = ( MemberRole, ManagerRole, OwnerRole, EditorRole, ReaderRole, WriterRole, AuthorRole, VersionOwnerRole )
FolderViewerRoles               = ( ManagerRole, OwnerRole, AuthorRole, EditorRole, ReaderRole, WriterRole )

AddContentPermission            = CMFCorePermissions.AddPortalContent

EmployPortalContentPerm         = 'Employ portal content'
PublishPortalContentPerm        = 'Publish portal content'
ArchivePortalContentPerm        = 'Archive portal content'

UpdateRemoteObjectsPerm         = 'Update remote objects'

AddSubscriptionRootPerm         = 'Add Subscription objects'
AddSubscriptionFolderPerm       = 'Add Subscription Folder objects'

SubscribeUsersPerm              = 'Subscribe users'

AddMailServerObjectsPerm        = 'Add MailServer objects'
UseMailServerServicesPerm       = 'Use MailServer services'

AddMailHostObjectsPerm          = ZopePermissions.add_mailhost_objects
UseMailHostServicesPerm         = ZopePermissions.use_mailhost_services

WebDAVLockItemsPerm             = 'WebDAV Lock items'
WebDAVUnlockItemsPerm           = 'WebDAV Unlock items'

AddDTMLDocumentsPerm            = 'Add DTML Documents'

CreateObjectVersionsPerm        = 'Create object versions'
MakeVersionPrincipalPerm        = 'Make version principal'

CopyOrMovePerm                  = 'Copy or Move'
UseErrorLoggingPerm             = 'Log Site Errors'
ManageCommentsPerm              = 'Manage comments'

AddPluggableIndexPerm           = 'Add Pluggable Index'

NoAccessRestr                   = 'No access'
NoModificationRightsRestr       = 'No modification rights'

ViewAttributesPerm              = 'View attributes'
ModifyAttributesPerm            = 'Modify attributes'

#===========================================================================

class Roles: pass

class Permissions: pass

class Restrictions: pass

class Menu: pass

for name, value in globals().items():
    if name.endswith('Role'):
        setattr( Roles, name[:-4], value )
    if name.endswith('Perm'):
        setattr( Permissions, name[:-4], value )
    if name.endswith('Restr'):
        setattr( Restrictions, name[:-5], value )
    if name.endswith('Menu'):
        setattr( Menu, name[:-4], value )

#===========================================================================

ManagedPermissions = (
    CMFCorePermissions.AccessContentsInformation,
    CMFCorePermissions.ListFolderContents,
    CMFCorePermissions.ModifyPortalContent,
    CMFCorePermissions.View,
    CMFCorePermissions.ManageProperties,
    CMFCorePermissions.ReplyToItem,
    ZopePermissions.delete_objects,
    ZopePermissions.take_ownership,
    Permissions.WebDAVLockItems,
    Permissions.WebDAVUnlockItems,
    Permissions.CreateObjectVersions,
    Permissions.MakeVersionPrincipal,
    Permissions.ViewAttributes,
    Permissions.ModifyAttributes,
)

PortalPermissions = (
    ( CMFCorePermissions.SetOwnPassword,        [ ManagerRole, MemberRole ],            1 ),
    ( CMFCorePermissions.SetOwnProperties,      [ ManagerRole, MemberRole ],            1 ),

    ( CMFCorePermissions.UndoChanges,           [ ManagerRole, MemberRole ],            1 ),
    ( CMFCorePermissions.ListUndoableChanges,   [ ManagerRole, MemberRole ],            1 ),
    ( CMFCorePermissions.ListPortalMembers,     [ ManagerRole, MemberRole ],            1 ),
    ( CMFCorePermissions.FTPAccess,             [ ManagerRole, OwnerRole ],             1 ),

    #( CMFCorePermissions.AccessContentsInformation, [],        1 ),
    #( CMFCorePermissions.AccessFuturePortalContent, [],        1 ),
    ( CMFCorePermissions.AddPortalContent,      [ ManagerRole, OwnerRole, EditorRole, WriterRole, AuthorRole ], 1 ),
    ( CMFCorePermissions.AddPortalFolders,      [ ManagerRole, OwnerRole, EditorRole ], 1 ),
    ( CMFCorePermissions.ModifyPortalContent,   [ ManagerRole, OwnerRole, EditorRole ], 1 ),
    ( CMFCorePermissions.ManageProperties,      [ ManagerRole, OwnerRole, EditorRole ], 1 ),
    ( CMFCorePermissions.View,                  [ ManagerRole, OwnerRole, EditorRole, MemberRole ], 0 ),
    ( CMFCorePermissions.ReplyToItem,           [ ManagerRole, OwnerRole, MemberRole ], 1 ),
    ( CMFCorePermissions.RequestReview,         [ ManagerRole, OwnerRole, EditorRole ], 1 ),

    ( CMFCorePermissions.ManagePortal,          [ ManagerRole ],                        1 ),
    ( CMFCorePermissions.ViewManagementScreens, [ ManagerRole ],                        1 ),
    ( CMFCorePermissions.ChangePermissions,     [ ManagerRole, OwnerRole, EditorRole ], 1 ),

    ( ZopePermissions.change_configuration,     [ ManagerRole, OwnerRole ],             1 ),
    ( ZopePermissions.delete_objects,           [ ManagerRole, OwnerRole, EditorRole ], 1 ),
    ( ZopePermissions.take_ownership,           [ ManagerRole, OwnerRole, EditorRole ], 1 ),

    ( Permissions.AddMailHostObjects,           [ ManagerRole ],                        1 ),
    ( Permissions.AddMailServerObjects,         [ ManagerRole ],                        1 ),
    ( Permissions.UseMailHostServices,          [ ManagerRole, EditorRole ],            1 ),
    ( Permissions.UseMailServerServices,        [ ManagerRole, EditorRole ],            1 ),

    ( Permissions.AddSubscriptionFolder,        [ ManagerRole, OwnerRole, EditorRole ], 1 ),
    ( Permissions.AddSubscriptionRoot,          [ ManagerRole ],                        1 ),

    ( Permissions.SubscribeUsers,               [ ManagerRole, OwnerRole, EditorRole, WriterRole ], 1 ),

    ( Permissions.UpdateRemoteObjects,          [ ManagerRole, OwnerRole, EditorRole ], 1 ),
    ( Permissions.EmployPortalContent,          [ ManagerRole, EditorRole ],            1 ),
    ( Permissions.PublishPortalContent,         [ ManagerRole, EditorRole ],            1 ),
    ( Permissions.ArchivePortalContent,         [ ManagerRole, OwnerRole, EditorRole ], 1 ),

    ( Permissions.UseExternalEditor,            [ ManagerRole, MemberRole ],            1 ),
    ( Permissions.WebDAVLockItems,              [ ManagerRole, OwnerRole, EditorRole ], 1 ),
    ( Permissions.WebDAVUnlockItems,            [ ManagerRole, OwnerRole, EditorRole ], 1 ),
#    ( Permissions.WebDAVAccess,                [ ManagerRole, OwnerRole, MemberRole ], 0 ),

    ( Permissions.AddDTMLDocuments,             [ ManagerRole ],                        1 ),

    ( Permissions.CreateObjectVersions,         [ ManagerRole, OwnerRole, EditorRole, WriterRole ], 1 ),
    ( Permissions.MakeVersionPrincipal,         [ ManagerRole, OwnerRole ],             1 ),

    ( Permissions.CopyOrMove,                   [ ManagerRole, OwnerRole, MemberRole ], 1 ),
    ( Permissions.UseErrorLogging,              [ ManagerRole, MemberRole ],            1 ),
    ( Permissions.ManageComments,               [ ManagerRole ],                        1 ),

    ( Restrictions.NoAccess,                    [],                                     1 ),
    ( Restrictions.NoModificationRights,        [],                                     1 ),

    ( Permissions.ViewAttributes,               [ ManagerRole, OwnerRole, EditorRole, VersionOwnerRole, ReaderRole ], 1 ),
    ( Permissions.ModifyAttributes,             [ ManagerRole, OwnerRole, EditorRole, VersionOwnerRole ], 1 ),
)
