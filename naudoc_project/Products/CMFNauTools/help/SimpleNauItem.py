"""SimpleNauItem class interface description.

$Id: SimpleNauItem.py,v 1.3 2005/05/14 05:43:51 vsafronovich Exp $
"""

from Interface import Attribute, Base

class SimpleNauItem( Base ):
    """
       Methods of this class are shared by all NauSite
       content objects
    """
    def parent_url(self):
        """
           Returns the object container URL.
           Invoked by the portal_catalog 'parent_url' field
           index for cataloguing purposes.
        """

    def full_size(self):
        """
           Returns size(in bytes) of the object including subobjects
        """

    def editor(self):
        """
           Gets the list of all editors within current context
        """

    def delete_me(self, REQUEST=None):
        """
           Removes self including subobjects
        """

    def getSite(self):
        """
           Returns current Site object or None if not in context of
           the external site.
        """

    def external_url(self):
        """
           Rewrites absolute url of the object in a way it accessible
           through the external site.

           For example, URL like /docs/storage/companysite.com/doc
           will be converted to /docs/external/companysite.com/doc
        """

    def isPublished(self):
        """
           Checks whether the document is published on the external site

           Returns: 1 or None
        """

    def setNewsMode(self, mode=''):
        """
           Sets external site presentation mode of the document

           mode: 'primary', 'secondary' or None for ordinary objects
        """

    def getNewsMode(self):
        """
          Get the way document is displayed on the external site
        """
