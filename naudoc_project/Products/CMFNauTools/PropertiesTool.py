"""
Portal properties tool.

$Editor: vpastukhov $
$Id: PropertiesTool.py,v 1.38 2008/08/21 11:37:37 oevsegneev Exp $
"""
__version__ = '$Revision: 1.38 $'[11:-2]

from copy import deepcopy

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.PropertiesTool import PropertiesTool as _PropertiesTool

import Config
from ActionInformation import ActionInformation as AI
from SimpleObjects import ToolBase
from Utils import InitializeClass, getLanguageInfo


class PropertiesTool( ToolBase, _PropertiesTool ):
    """
        Portal properties tool
    """
    _class_version = 1.10

    meta_type = 'NauSite Properties Tool'

    security = ClassSecurityInfo()

    manage_options = _PropertiesTool.manage_options # + ToolBase.manage_options

    _actions = tuple(_PropertiesTool._actions) + \
          (
            AI( id=Config.NavTreeMenu
              , title='Accessible documents'
              , icon='tree'
              , permissions=(CMFCorePermissions.View,)
              , category='menu'
              , visible=True
              , priority=10
              ),
            AI( id=Config.FollowupMenu
              , title='Follow-up tasks'
              , icon='kid'
              , permissions=(CMFCorePermissions.View,)
              , category='menu'
              , visible=True
              , priority=20
              ),
            AI( id=Config.UserMenu
              , title='User'
              , icon='user'
              , permissions=(CMFCorePermissions.View,)
              , category='menu'
              , visible=True
              , priority=30
              ),
            AI( id=Config.GlobalMenu
              , title='Tools'
              , icon='service'
              , permissions=(CMFCorePermissions.ManagePortal,)
              , category='menu'
              , visible=True
              , priority=40
              ),
            AI( id=Config.SearchMenu
              , title='Search'
              , icon='search'
              , permissions=(CMFCorePermissions.View,)
              , category='menu'
              , visible=True
              , priority=50
              ),
            AI( id=Config.ArchTreeMenu
              , title='Archival documents'
              , icon='arch'
              , permissions=(CMFCorePermissions.View,)
              , category='menu'
              , visible=True
              , priority=60
              ),
            AI( id=Config.HelpMenu
              , title='Help'
              , icon='help'
              , permissions=(CMFCorePermissions.View,)
              , category='menu'
              , visible=True
              , priority=70
              ),
            AI( id=Config.FavoritesMenu
              , title='Favorites'
              , icon='favourites'
              , permissions=(CMFCorePermissions.View,)
              , category='menu'
              , visible=True
              , priority=80
              ),
             
            # reports
            AI( id='followup_tasks_form'
              , title='Root tasks tree'
              , permissions=(CMFCorePermissions.View,)
              , action=Expression( text="string: ${portal_url}/followup_tasks_form" )
              , category='report'
              , visible=True
              ),
            AI( id='followup_stat'
              , title='Tasks progress report'
              , permissions=(CMFCorePermissions.View,)
              , action=Expression( text="string: ${portal_url}/followup_stat" )
              , category='report'
              , visible=True
              ),
            AI( id='documents_stat'
              , title='Documents report'
              , permissions=(CMFCorePermissions.View,)
              , action=Expression( text="string: ${portal_url}/documents_stat" )
              , category='report'
              , visible=True
              ),
            AI( id='followup_ndreport'
              , title='Documents registry report'
              , permissions=(CMFCorePermissions.View,)
              , action=Expression( text="string: ${portal_url}/followup_ndreport" )
              , category='report'
              , condition=Expression( 'python: portal.portal_metadata.getCategoryById("NormativeDocument")' )
              ),
          )

    # restore method overridden by PropertyManager in ItemBase
    title = _PropertiesTool.title

    ### Override 'portal_properties' interface methods ###

    security.declareProtected( CMFCorePermissions.ManagePortal, 'editProperties' )
    def editProperties( self, props ):
        """ Change portal settings
        """
        portal = self.parent()
        portal.manage_changeProperties( props )

        lang = props.get('language')
        if lang:
            langinfo = getLanguageInfo( lang )
            portal.msg.manage_changeDefaultLang( lang )

            default_encoding = langinfo['python_charset']
            catalog_tool = getToolByName( self, 'portal_catalog' )

            for idx in catalog_tool.getIndexObjects():
                if idx.meta_type == 'TextIndexNG2':
                    idx.default_encoding = default_encoding

        mail = getToolByName( self, 'MailHost', None )
        if mail and props.has_key('smtp_server'):
            mail.address( props['smtp_server'] )

        if mail and props.has_key('smtp_login'):
            login = props['smtp_login'] or None
            mail.setCredentials( login=login )

            password = login and props.get('smtp_password', '')
            if not password or len(password.replace('*', '')):
                mail.setCredentials( password=password )

        mail = getToolByName( self, 'MailPOP', None )
        if mail and props.has_key('mail_pop'):
            mail.address( props['mail_pop'] )

        mail = getToolByName( self, 'MailIMAP', None )
        if mail and props.has_key('mail_imap'):
            mail.address( props['mail_imap'] )

    def smtp_server( self ):
        """ Get smtp server address
        """
        return self.MailHost.address()

    def smtp_login( self ):
        """Get smtp server login
        """
        return self.MailHost.login()

    def smtp_password( self ):
        """Get smtp password
        """
        return self.MailHost.password()


    ### New interface methods ###

    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'getProperty' )
    def getProperty( self, id, default=None, moniker=False ):
        """
            Get the portal property 'id', returning the optional second
            argument or None if no such property is found.
        """
        portal = self.parent()
        if portal.meta_type == 'CMF Site':
            return portal.getProperty( id, default )
        return portal.getProperty( id, default, moniker=moniker )

    security.declareProtected( CMFCorePermissions.AccessContentsInformation, 'getConfig' )
    def getConfig( self, name, default=None ):
        """
            Returns value of the requested configuration variable.

            Arguments:

                'name' -- variable's name of interest

                'default' -- value to return unless the named variable
                             exists; 'None' if not given

            Result:

                A copy of variable's value, or default one.
        """
        try:
            value = getattr( Config, name )
        except AttributeError:
            return default
        return deepcopy( value )

    def mail_pop( self ):
        """ Get POP3 mail server address
        """
        mail = getToolByName( self, 'MailPOP', None )
        return mail and mail.address() or ''

    def mail_imap( self ):
        """ Get IMAP4 mail server address
        """
        mail = getToolByName( self, 'MailIMAP', None )
        return mail and mail.address() or ''

InitializeClass( PropertiesTool )

def initialize( context ):
    # module initialization callback

    context.registerTool( PropertiesTool )
