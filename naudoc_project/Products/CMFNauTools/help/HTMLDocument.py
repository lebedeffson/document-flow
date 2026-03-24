"""HTMLDocument class interface description.

$Id: HTMLDocument.py,v 1.3 2005/05/14 05:43:51 vsafronovich Exp $
"""

from Interface import Attribute, Base

class HTMLDocument(Base):
    """
       HTMLDocumement is derived from the CMFDefault.Document class.
    """
    def __call__(self):
        """\
           Invokes the default document view.
        """

    def cleanup(self):
        """
           Applies HTMLCleaner to the document's text and removes all
           unwanted HTML tags. Also tries to remove absolute links to
           attached files and make them relative.

           Returns: document HTML source
        """

    def addFile(self, file):
        """
           Attaches a 'file' to the HTML document.
           No changes are made to the document source.

           Returns: id of the resulting object that was created inside
           the document with the 'file' contents
        """

    def pasteFile(self, basename, size=None):
        """
           Insert the file reference into the document's HTML code.
           Do not touch the file itself.

           'size' is used only for adding thumbnail previews and
           defines image scale. It can take one of the following
           values:

               'thumbnail': 128x128 px;
               'xsmall'   : 200x200 px;
               'small'    : 320x320 px;
               'medium'   : 480x480 px;
               'large'    : 768x768 px;
               'xlarge'   : 1024x1024 px;

           Returns: document HTML source
        """

    def removeFile(self, basename):
        """
           Removes all links pointing to the file with given basename
           from the document's HTML code then deletes file.

           Returns: document HTML source
        """

    def rated(self, REQUEST=None):
        """
           Checks whether the authenticated user has rated
           this document

           Returns: 1 or None
        """

    def get_rating(self):
        """
           Get the document rating

           Returns: an integer from 1 to 5 or None if the document
           was not rated yet,
        """

    def getTasksFor(self, content):
        """
            Return the tasks container for the content,
            creating it if need be.
        """

class ConfirmableContent:
    """
       A suite of methods enabling document review feature.
       Document review allows coordinate the document content with
       any other portal members.

       After each requested member has approved confirmation, the
       document is transited to the 'fixed reviewed' state. In case
       there is at least one member who refused confirmation then object
       state changes to 'refused'

       Document review request can be cancelled at any time.
    """

    def requestConfirmation(self, requested_users, confirm_by_turn=None, comment='', REQUEST=None):
        """
           Requests the user's review of the current
           document.

           requested_users: requested usernames list
           confirm_by_turn: request confirmation step by step
           comment: user comment
        """

    def cancelConfirmationRequest(self, comment='', REQUEST=None):
        """
           Cancels the user's confirmation request

           comment: user comment
        """

    def confirm(self, comment='', REQUEST=None):
        """
           User confirms the document

           comment: user comment
        """

    def refuse(self, comment='', REQUEST=None):
        """
           User refuses confirmation

           comment: user comment
        """
