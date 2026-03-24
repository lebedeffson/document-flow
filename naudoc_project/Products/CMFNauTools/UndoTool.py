"""
Undo transactions tool.

Config.EnableUndo - boolean  - visibility undo form


$Editor: spinagin $
$Id: UndoTool.py,v 1.9 2005/05/14 05:43:49 vsafronovich Exp $
"""
__version__ = '$Revision: 1.9 $'[11:-2]

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.UndoTool import UndoTool as _UndoTool

from ZODB.POSException import ConflictError

import Config, Exceptions
from ActionInformation import ActionInformation as AI
from SimpleObjects import ToolBase
from Utils import InitializeClass


class UndoTool(ToolBase, _UndoTool ):
    _class_version = 1.0
    meta_type = 'NauSite Undo Tool'
    security = ClassSecurityInfo()

    manage_options = _UndoTool.manage_options

    _actions = ( AI( id='undo'
                   , title='Undo'
                   , action=Expression(text='string: ${portal_url}/undo_form')
                   , condition=Expression(text='member')
                   , permissions=(CMFCorePermissions.ListUndoableChanges,)
                   , category='global'
                   , visible=Config.EnableUndo
                   ),
               )

    def undo(self, object, transaction_info):
        """
            Undo the list of transactions passed in 'transaction_info' for 'object'
        """
        if not Config.EnableUndo:
            raise Exceptions.SimpleError("Can't undo transaction(s)")

        try:
            _UndoTool.undo(self, object, transaction_info)
            get_transaction().commit()
        except ConflictError:
            # Don't swallow ConflictError
            raise
        except:
            raise Exceptions.SimpleError("Can't undo transaction(s)")


InitializeClass( UndoTool )

def initialize( context ):
    # module initialization callback

    context.registerTool( UndoTool )
