""" Portal discussion access tool.

$Id: DiscussionTool.py,v 1.7 2005/09/23 07:26:34 vsafronovich Exp $
$Editor: vsafronovich $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

from zLOG import LOG, DEBUG, TRACE, INFO, ERROR

from AccessControl import ClassSecurityInfo

from Products.CMFDefault.DiscussionTool import DiscussionTool as _DiscussionTool, \
                                               DiscussionNotAllowed

from DiscussionItem import DiscussionItemContainer
from SimpleObjects import ToolBase
from Utils import InitializeClass

class DiscussionTool( ToolBase , _DiscussionTool):

    _class_version = 1.00

    meta_type = 'NauSite Discussion Tool'
    id = 'portal_discussion'

    security = ClassSecurityInfo()

    manage_options = _DiscussionTool.manage_options

    _actions = tuple(_DiscussionTool._actions)

    security.declarePrivate( '_createDiscussionFor' )
    def _createDiscussionFor( self, content ):
        """
            Create the object that holds discussion items inside
            the object being discussed, if allowed.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed

        content.talkback = DiscussionItemContainer()
        return content.talkback

InitializeClass( DiscussionTool )

def initialize( context ):
    # module initialization callback

    context.registerTool( DiscussionTool )
