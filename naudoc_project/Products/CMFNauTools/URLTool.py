""" Portal url tool.

$Id: URLTool.py,v 1.5 2005/05/14 05:43:49 vsafronovich Exp $
$Editor: vpastukhov $
"""
__version__ = '$Revision: 1.5 $'[11:-2]

from AccessControl import ClassSecurityInfo

from Products.CMFDefault.URLTool import URLTool as _URLTool

from SimpleObjects import ToolBase
from Utils import InitializeClass

class URLTool( ToolBase, _URLTool ):

    _class_version = 1.00

    meta_type = 'NauSite URL Tool'
    id = 'portal_url'

    security = ClassSecurityInfo()

    manage_options = _URLTool.manage_options

    _actions = tuple(_URLTool._actions)

    def __call__( self, *args, **kwargs ):
        """
            Returns the absolute URL of the portal.
        """
        return self.parent().absolute_url( *args, **kwargs )

InitializeClass( URLTool )

def initialize( context ):
    # module initialization callback

    context.registerTool( URLTool )
