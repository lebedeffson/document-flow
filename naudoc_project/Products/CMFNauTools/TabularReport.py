"""Tabular Report content class.

$Editor: ikuleshov $
$Id: TabularReport.py,v 1.48 2005/05/14 05:43:48 vsafronovich Exp $
"""
__version__ = '$Revision: 1.48 $'[11:-2]

import Globals

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.CMFCore import CMFCorePermissions

from GuardedTable import GuardedTable
from ContentCategory import ContentCategory
from Utils import InitializeClass
import Features

TabularReportType = { 'id'             : 'Tabular Report'
                    , 'meta_type'      : 'Tabular Report'
                    , 'title'          : "Report"
                    , 'description'    : "Tabular report"
                    , 'icon'           : 'reportitem_icon.gif'
                    , 'product'        : 'CMFNauTools'
                    , 'factory'        : 'addReport'
                    , 'immediate_view' : 'report_options_form'
                    , 'permissions'    : ( CMFCorePermissions.ManagePortal, )
                    , 'actions'        :
                      ( { 'id'            : 'view'
                        , 'name'          : 'View'
                        , 'action'        : 'report_view'
                        , 'permissions'   : (CMFCorePermissions.View,)
                        },
                        { 'id'            : 'edit'
                        , 'name'          : "Report options"
                        , 'action'        : 'report_options_form'
                        , 'permissions'   : (CMFCorePermissions.ModifyPortalContent,)
                        },
                        { 'id'            : 'metadata'
                        , 'name'          : "Metadata"
                        , 'action'        : 'metadata_edit_form'
                        , 'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
                        },
                      )
                    }

def addReport( self, id, title='', **kwargs ):
    """ Adds tabular report """
    obj = TabularReport( id, title, **kwargs )
    self._setObject( id, obj )


class TabularReport(GuardedTable, ContentCategory):
    """ Tabular Report type """

    _class_version = 1.0

    meta_type = 'Tabular Report'
    portal_type = 'Tabular Report'

    __implements__ = ( Features.isPortalContent,
                       Features.isPublishable,
                       GuardedTable.__implements__,
                       ContentCategory.__implements__
                       #Features.isReport,
                     )

    security = ClassSecurityInfo()

    def __init__( self, id, title=None, category=None, category_template=None,
                        category_primary=None, category_attributes=None, **kwargs ):
        # instance contructor
        GuardedTable.__init__( self, id, title, **kwargs )
        ContentCategory.__init__( self, category, category_template,
                                        category_primary, category_attributes )
        # reports do not implement column-specific security policy
        self.allowed_groups = ()
        self.allowed_members = ()

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'setAllowedUsers' )
    def setAllowedUsers( self, members=(), groups=() ):
        """
          Sets up the list of the users allowed to add new report entries.

          Arguments:

            'members' -- Allowed members ids.

            'groups' -- Allowed groups ids.

          Note:

            Arguments format will be changed soon.
        """
        self.allowed_members = members
        self.allowed_groups = groups

    def isUserAllowed( self, username=None ):
        """
           Checks whether the particular user is allowed to add new report entries.

           Arguments:

             'username' -- User id string.

           Result:

             Boolean.
        """
        return username in self.allowed_memebers

    security.declareProtected( CMFCorePermissions.View, 'isGroupAllowed' )
    def isGroupAllowed( self, groupname=None ):
        """
           Checks whether the particular group is allowed to add new report entries.

           Arguments:

             'groupname' -- Group id string.

           Note:

             This method should be deprecated in future releases.

           Result:

             Boolean.
        """
        return groupname in self.allowed_groups

    security.declareProtected( CMFCorePermissions.View, 'listAllowedMembers' )
    def listAllowedMembers( self, status=None ):
        """
           Returns the list of the members allowed to add new report entries.

           All users from the allowed groups are also included into the resulting list.

           Note:

             This method should be deprecated in future releases.

           Result:

              List of user id strings.
        """
        members_list = []

        if self.allowed_members:
            members_list += self.allowed_members

        membership = getToolByName(self, 'portal_membership')
        if self.allowed_groups:
            for group in self.allowed_groups:
                group_users = membership.getGroup(group).getUsers()
                for user in group_users:
                    if user not in members_list: members_list.append(user)

        return members_list

InitializeClass( TabularReport )


def initialize( context ):
    # module initialization callback

    context.registerContent( TabularReport, addReport, TabularReportType )
