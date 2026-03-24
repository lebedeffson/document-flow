"""
Transient data storage tool.

$Editor: vpastukhov $
$Id: TransienceTool.py,v 1.3 2004/03/17 17:30:14 vpastukhov Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

from Queue import Queue
from ThreadLock import allocate_lock

from AccessControl import ClassSecurityInfo

from Products.Transience.Transience import TransientObjectContainer

from SimpleObjects import ToolBase
from Utils import InitializeClass


class TransienceTool( ToolBase, TransientObjectContainer ):
    """
        Portal transient data storage tool.
    """
    _class_version = 1.0

    meta_type = 'NauSite Transience Tool'
    id = 'portal_transience'

    security = ClassSecurityInfo()

    __implements__ = ToolBase.__implements__, \
                     TransientObjectContainer.__implements__

    manage_options = TransientObjectContainer.manage_options + \
                     ToolBase.manage_options

    # It is horrible to use such global objects, but we have to because
    # of the skewed TOC implementation.
    # The problem is addressed by chrism-sessiongeddon branch in Zope CVS.

    lock = allocate_lock()
    notify_queue = Queue()
    replentish_queue = Queue(1)

    def __init__( self ):
        ToolBase.__init__( self )
        TransientObjectContainer.__init__( self, self.getId() )

InitializeClass( TransienceTool )


def initialize( context ):
    # module initialization callback

    context.registerTool( TransienceTool )
