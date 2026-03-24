"""NauSite Membership class interface description.

$Id: MembershipTool.py,v 1.2 2005/05/14 05:43:51 vsafronovich Exp $
"""

from Interface import Attribute, Base

class MembershipTool(Base):
    """
       NauSite membership tool is an extension of the core CMF tool
       and appends methods for interaction with 'User Folder with Groups',
       provides public interfaces for retrieving and formatting personal
       user data.
    """

    def list_groups(self, object=None):
        """
          Returns a groups list

          'object' option is obsolete
        """
    def group_users(self, group):
        """
          Returns a list of the group user names
        """

    def local_users(self):
        """
          Returns the list of all user names
        """

    def inheritedRole(self, object, group, role):
        """
          Checks whether this role was inherited from the parent.
        """

    def hasRole(self, object, group, role):
        """
          Check whether the group has
          the given permission over the object
        """

    def setRoles(self, userid, roles):
        """
          Assign roles to ther given user
        """

    def Title(self, group):
        """
          Returns the group title
        """

    def changeGroup(self, group=None, group_users=None, title=None, REQUEST=None):
        """
           Assign the users to the given group
           and change the group description
        """

    def getUserInfo(self, u_id):
        """
          Get user properties
        """

    def allowedUsers(self, object, roles):
        """
          Return a list of roles and users with View permission.
          Used by PortalCatalog to filter out items you're not allowed to see.
        """
