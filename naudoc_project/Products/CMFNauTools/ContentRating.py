""" ContentRating class
$Id: ContentRating.py,v 1.5 2005/12/09 15:42:56 vsafronovich Exp $
"""
__version__='$Revision: 1.5 $'[11:-2]

import re, string, os.path
import Globals

from AccessControl import ClassSecurityInfo, Permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions

from Utils import InitializeClass

class ContentRating:
    """ Content category type """

    security = ClassSecurityInfo()

    #
    # Document rating support
    security.declareProtected(CMFCorePermissions.View, 'rate')
    def rate(self, grade, REQUEST=None):
        """
          Rate the document (from 1 to 5 points)
        """
        if grade and int(grade) <= 5:
            membership = getToolByName(self, 'portal_membership')
            member = membership.getAuthenticatedMember()
            uname = member.getUserName()
            try:
                self.manage_addProperty('rate_sum', 0, 'int')
                self.manage_addProperty('rate_users', '', 'tokens')
            except:
                pass

            rate_sum = self.getProperty('rate_sum', 0)
            rate_users = self.getProperty('rate_users', '')

            if uname not in rate_users:
                self.manage_changeProperties( rate_sum=rate_sum + int(grade) )
                rate_users = list(rate_users)
                rate_users.append(uname)
                self.manage_changeProperties( rate_users=rate_users )

            if REQUEST is not None:
                REQUEST[ 'RESPONSE' ].redirect( self.absolute_url() )

    security.declareProtected(CMFCorePermissions.View, 'rated')
    def rated(self, REQUEST=None):
        """
          Checks whether the user rated this document
        """
        membership = getToolByName(self, 'portal_membership')
        uname = membership.getAuthenticatedMember().getUserName()

        rate_sum = self.getProperty('rate_sum', 0)
        rate_users = self.getProperty('rate_users', '')

        if rate_users and uname in rate_users:
            return 1

        return None

    security.declareProtected(CMFCorePermissions.View, 'get_rating')
    def get_rating(self):
        """
          Get the document rating
        """
        rate_sum = self.getProperty('rate_sum', 0)
        rate_users = self.getProperty('rate_users', '')

        if len(rate_users) > 0:
            return rate_sum / len(rate_users)

        return 0

InitializeClass( ContentRating, __version__ )
