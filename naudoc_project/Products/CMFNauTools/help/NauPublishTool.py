"""Publisher entry point interface description.

$Id: NauPublishTool.py,v 1.2 2005/05/14 05:43:51 vsafronovich Exp $
"""

from Interface import Attribute, Base

class NauPublisher( Base ):
    """
      Publisher entry point is a basic part of the external site.
      It acts like a virtal folder that can fetch requested objects
      from the internal part of the site.

      There are not actual documents stored inside the Publiser EP.
    """
    def __before_publishing_traverse__(self, self2,  REQUEST=None):
        """
          This hook is called while retrieving the URL that contains
          reference to the Publisher EP instance.

          For example, if there is a publisher /site/go, than opening
          of the /site/go/fooDocument invokes this method. After that
          traversing stops and publisher fetchs object fooDocument
          from the real Site object somewhere inside a NauSite instance.
        """

    def __call__(self, REQUEST):
        """
          Gets site home page if no traverse subpath defined, fetchs
          requested document or returns 'site_error_message' site skin
          method if no page was found.

          Called thanks to '__before_publishing_traverse__' hook.
        """

    def publishedItems(self, subpath=None, exact = None):
        """
          Returns the list of the published items placed under the
          given subpath relative to the Site object root. Empty subpath
          is used to list all the documents of the site.

          If 'exact' is not None than documents are retrieved from
          subfolders also.
        """

    def getPublisher(self):
        """
          Returns the publisher itself.
        """

    def getSite(self):
        """
          Gets the reference to the Site object associated with
          current Publisher EP.
        """

    def getSiteUrl(self):
        """
          Gets the URL of the Site object associated with
          current Publisher EP.
        """

    def getParents(self, subpath=None):
        """
          Lists top parents starting from the given subpath

          Returned list contains not actual objects but dictionaries
          with fields:

          'absolute_url' - external URL of the object
          'meta_type'    - object meta type
          'title_or_id'  - object title or id
          'title'        - object title
          'id'           - parent id

          If 'subpath' is None, then current path is retrieved
          from the REQUEST['TraversalRequestNameStack'] variable.
        """

    def listSubFolders(self, subpath = None):
        """
          Lists subfolders under the given subpath. Those folders
          that does not contain any published items are not included
          into the list.

          Read getParents description for the results format details.

          If 'subpath' is None, then current path is retrieved
          from the REQUEST['TraversalRequestNameStack'] variable.
        """

    def fetchObject( self, path, REQUEST=None):
        """
          Fetchs requested document from the Site object and wraps it into
          the context of the site skin.
          The document is firstly looked up in the publisher's context and
          only after that is retrieved from the Site.

          In case folder object is found, then 'listPublishedForm' method
          is invoked from the site skin or the main folder document is fetched.

          Called by the publisher's __call__ hook.
        """
