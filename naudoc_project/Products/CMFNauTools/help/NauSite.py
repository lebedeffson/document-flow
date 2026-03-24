"""NauSite class interface description.

$Id: NauSite.py,v 1.2 2005/05/14 05:43:51 vsafronovich Exp $
"""

from Interface import Attribute, Base

class NauSite( Base ):
    """
        The *only* function this class should have is to help in the setup
        of a new NauSite.  It should not assist in the functionality at all.
    """

class PortalGenerator( Base ):
    """
        This class is based on Products.CMFDefault.Portal.PortalGenerator class

        PortalGenerator is used to deploy a new NauSite instance.
        Invoked by the manage_addNauSite constructor.
    """

    def create(self, parent, id, create_userfolder, home_title):
        """
            Deploy NauSite.

            'parent' - object container;
            'create_userfolder' - whether we need to create a userfolder or not;
            'home_title' - title of the members home folder
        """
