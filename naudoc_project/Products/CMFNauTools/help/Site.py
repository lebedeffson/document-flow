"""Site class interface description.

$Id: Site.py,v 1.2 2003/03/04 16:33:08 vpastukhov Exp $
"""

from Interface import Attribute, Base

class Site( Base ):
    """
        Site class is a user-side presentation and control machinery
        of the external site.
        Class methods can be invoked only by those objects that
        are placed inside the Site instance.
    """
    def listInstalledPlugins( content ):
        """
            Get the list of external site plugins applied to the
            current Site object. Returned value is a list of ids.
        """

    def getSiteStorage( content ):
        """
            Returns the site storage object. For example if there
            is a site /docs/fooSite with storage id set up to
            'storage', then getSiteStorage returns a reference
            to /docs/fooSite/storage
        """

    def getSiteObject( content ):
        """
            Returns the site object itself.
            Invoked mostly by SimpleNauItem.getSite
        """

    def getExternalRootUrl(content, relative=None):
        """
            Gets an actual URL of the external site. Everyone is able
            to access your site by visiting this URL.

            If 'relative' option is not None then returned URL
            must be relative to the current NauSite object
        """

    def siteId(content):
        """
            Returns the site object id.
        """

    def setPresentationLevel(content, object, level=None):
        """
            Sets object 'ob' as a "presented" document of the current site.
            Depending on the site skin presented document may be displayed
            in a special way, unlike ordinary documents.
        """

    def getPresentationLevel(content, object):
        """
            Return presentation level of the document.
        """

    def getPresentedDocuments(content):
        """
            Returns list of the presented document objects.
        """
