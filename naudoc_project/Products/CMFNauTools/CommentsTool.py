"""
Comments tool.

$Editor: vpastukhov $
$Id: CommentsTool.py,v 1.11 2005/05/14 05:43:47 vsafronovich Exp $
"""
__version__ = '$Revision: 1.11 $'[11:-2]

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from BTrees.OOBTree import OOBTree, OOSet

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser

import Config
from ActionInformation import ActionInformation as AI
from Config import Permissions
from SimpleObjects import InstanceBase, ToolBase, ContainerBase
from Utils import InitializeClass, cookId


class CommentTemplate( InstanceBase ):
    """ Comment template """
    _class_version = 1.0

    meta_type = 'Comment Template'

    security = ClassSecurityInfo()
    security.setDefaultAccess(1)

    _properties = InstanceBase._properties + (
            {'id':'text',             'type':'string',        'mode':'w'},
        )

    def __init__( self, id, text ):
        """ Initialize class instance
        """
        InstanceBase.__init__( self, id )
        self.text = text

    security.declareProtected( Permissions.ManageComments, 'setText' )
    def setText( self, text ):
        self.text = text

InitializeClass( CommentTemplate )


class CommentsTool( ToolBase, ContainerBase ):
    """ Portal comments """
    _class_version = 1.0

    meta_type = 'NauSite Comments Tool'
    id = 'portal_comments'

    security = ClassSecurityInfo()

    manage_options = ToolBase.manage_options + \
                     ContainerBase.manage_options[:-1] # exclude 'Properties'

    _actions = ( AI( id='manageComments'
                   , title='Manage resolutions'
                   , action=Expression( text='string: ${portal_url}/manage_comments_form')
                   , category='global'
                   , permissions=(Permissions.ManageComments,)
                   , visible=1
                   ),
               )

    def __init__( self ):
        """ Initialize class instance
        """
        ToolBase.__init__( self )
        self._contexts = OOBTree()

    security.declareProtected( Permissions.ManageComments, 'addComment' )
    def addComment( self, text, context ):
        id = cookId( self, prefix='comment' )
        self._setObject( id, CommentTemplate( id, text ), set_owner=0 )

        context  = context or 'global'
        comments = self._contexts.get( context )
        if comments is None:
            comments = self._contexts[ context ] = OOSet()
        comments.insert( id )

    security.declareProtected( Permissions.ManageComments, 'deleteComment' )
    def deleteComment( self, id ):
        for ids in self._contexts.values():
            try: ids.remove( id )
            except KeyError: pass

        self._delObject( id )

    security.declareProtected( CMFCorePermissions.View, 'listContexts' )
    def listContexts( self, id=None ):
        if id is None:
            return list( self._contexts.keys() )
        results = []
        for name, comments in self._contexts.items():
            if id in comments:
                results.append( name )
        return results

    security.declareProtected( CMFCorePermissions.View, 'listComments' )
    def listComments( self, context, exact=None ):
        contexts = self._contexts
        results  = []

        if exact:
            parts = [ context ]
        else:
            parts = context.split('.')
            parts = [ '.'.join( parts[:i] ) for i in range( 1, len(parts)+1 ) ]
            parts.insert( 0, 'global' )

        for part in parts:
            for id in contexts.get( part, [] ):
                results.append( self[ id ] )

        return results

InitializeClass( CommentsTool )

def initialize( context ):
    # module initialization callback

    context.registerTool( CommentsTool )
