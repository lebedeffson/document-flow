"""
  Docflow role manager
  
  This class provide logic for mapping specified role id (on scope of DocFlow) 
  to real user id

$Editor: inemihin $
$Id: DFRoleManager.py,v 1.12 2007/06/04 10:27:43 oevsegneev Exp $

"""
from types import StringType

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName

from Config import Roles

class DFRoleManager:

    _role_handlers = {}

    def __init__(self, obj, context=Missing):
        self._init( obj, context=context)

    def _init(self, obj, context=Missing):
        """
            Arguments:

                'object' -- object according which roles will be analized

                'context' -- object for calling 'getToolByName'

        """
        self.object = obj
        if context is Missing:
            context = obj
        self.context = context        
  
    def replaceVersionOwner( self ):
        return [ self.object.getVersion().getOwner() ]

    def replaceOwner( self ):
        if self.object.implements( 'isVersion' ):
            return [ self.object.getVersionable().getOwner() ]
        else:
            return [ self.object.getOwner() ]

    def replaceReader( self ):
        portal_membership = getToolByName( self.context, 'portal_membership' )
        # for document is assigned local roles 'Reader'
        # when task is created
        # i.e. we havent to analise this role
        # we get document's container
        obj = aq_parent( aq_inner( self.object ) )
        return portal_membership.listAllowedUsers( obj, Roles.Reader )

    def replaceWriter( self ):
        portal_membership = getToolByName( self.context, 'portal_membership' )
        return portal_membership.listAllowedUsers( self.object, Roles.Writer )
 
    def replaceEditor( self ):
        portal_membership = getToolByName( self.context, 'portal_membership' )
        return portal_membership.listAllowedUsers( self.object, Roles.Editor )

    def getUsersByRole( self, role ):
        """
            Returns user id by role

                'role' -- id of role

            Result:

                Returns array of user's id matching to specified role.

        """
        users = self._role_handlers.get( role, lambda RM:[] )(self)
        return [ str(u) for u in users ]

    # XXXXXX: remove this
    def getUserIdByRole( self, parent, object, role ):
        """
           see getUsersByRole.__doc__
        """
        self._init( obj, context=parent )
        return self.getUsersByRole( role )

    def registerDFRoleHandler(self, role, handler):
        """
            
        """
        assert isinstance( role, StringType )
        assert callable( handler )
        if self._role_handlers.has_key(role):
             raise ValueError( 'dublicate role: %s' % role )
        self._role_handlers[role] = handler
    registerDFRoleHandler = classmethod( registerDFRoleHandler )

def initialize( context ):
    # module initialization callback

    context.register( DFRoleManager.registerDFRoleHandler )

    # register default roles
    for name, method in DFRoleManager.__dict__.items():
        if name.startswith( 'replace' ):
             context.registerDFRoleHandler( getattr( Roles, name[7:]), method )
