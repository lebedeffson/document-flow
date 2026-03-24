"""Heading class interface description.

$Id: Heading.py,v 1.4 2005/05/14 05:43:51 vsafronovich Exp $
"""

from Interface import Attribute, Base

class Heading(Base):
    """
       Heading is a folder metaphor for the NauSite portal.
    """

    def __call__(self):
        """
           Invokes the default view.
        """

    def setMainPage(self, object):
        """
           Affects heading view in context of the external
           site.

           'object' values:
              None - documents list. This is a normal view of the heading.
              document object - main page. Heading view will have a main document
                     automatically displayed instead of the documents list.
        """

    def hasMainPage(self):
        """
           Check whether this folder is in the main page
           mode or not.

           Returns: 1 or None
        """

    def getMainPage(self):
        """
           Returns the reference to the object that was previously
           set up as a main heading document. If there was no object
           assigned, then the most recent heading document returned.
        """

    def reindexSubObjects(self):
        """
           Reindex objects inside the given folder
           (have to update 'allowedRolesAndUsers')
        """

    def setLocalRoles(self, userid, roles, REQUEST=None):
        """
           Wrapper for the built-in manage_setLocalRoles
           Prevents accidental double role assignements.
        """

    def delLocalRoles(self, userids, REQUEST=None):
        """
           Wrapper for the built-in manage_delLocalRoles
        """

    def getLocalRoles(self, userid=None):
        """
           Return all local roles assigned over this object
        """

    def user_roles(self):
        """
           Get the users' role list within current context
        """

    def subscribe(self, email, REQUEST=None):
        """
           Starts subscribing sequence.
           Requests user confirmation to recieve information
           about latest updates within current heading.

           'email': subscribed user's email.
        """

    def confirm_subscription(self, email, secret_code, REQUEST):
        """
           Enables news mailing for the given email address after
           the user confirmed subscription by visiting the URL included
           into the confirmation request mail.

           'email': subscribed user's email.
           'secret_code': special value that identifies subscribed user.
        """

    def unsubscribe(self, email, REQUEST=None):
        """
           Cancels news mailing for the given email.

           'email': subscribed user's email.
        """

    def announce_publication( self, ob, REQUEST=None ):
        """
           Passes document properties to site's announce demon.

           That demon, when starts, generates email message for each
           subscribed user with announces of all documents that were
           published since last start.

           Arguments:

               'ob' -- document which was published

               'REQUEST' -- REQUEST object
        """
