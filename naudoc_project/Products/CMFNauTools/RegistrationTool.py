"""
Portal registration tool.

$Id: RegistrationTool.py,v 1.4 2005/04/19 13:59:32 vsafronovich Exp $
$Editor: vpastukhov $
"""
__version__ = '$Revision: 1.4 $'[11:-2]

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.RegistrationTool import \
        RegistrationTool as _RegistrationTool

from SimpleObjects import ToolBase
from Utils import InitializeClass


class RegistrationTool( ToolBase, _RegistrationTool ):
    """
        Create and modify users by making calls to portal_membership.
    """
    _class_version = 1.0

    meta_type = 'NauSite Registration Tool'
    id = 'portal_registration'

    security = ClassSecurityInfo()

    _actions = tuple(_RegistrationTool._actions)

    _properties = ToolBase._properties + (
            {'id':'require_email', 'type':'boolean', 'mode':'w'},
        )

    # default property values
    require_email = True

    security.declareProtected( CMFCorePermissions.AddPortalMember, 'isMemberIdAvailable' )
    def isMemberIdAvailable( self, id ):
        """
            Verifies that the given login name not used yet.

            Arguments:

                'id' -- the login name to verify

            Result:

                Boolean.
        """
        return not getToolByName( self, 'portal_membership' ).getMemberById( id )

    def testPropertiesValidity( self, props, member=None ):
        """
            Verifies that the properties supplied satisfy portal's requirements.

            Result:

                If the properties are valid, return None.
                If not, return a string explaining why.
        """
        require_email = self.getProperty( 'require_email', True )

        if member is None: # New member.

            username = props.get( 'username', '' )
            if not username:
                return "You must enter a valid name."

            if not self.isMemberIdAllowed( username ):
                return "The login name you selected is already in use or is not valid. Please choose another."

            if require_email and not props.get('email'):
                return "You must enter a valid email address."

        else: # Existing member.
            # Not allowed to clear an existing non-empty email.
            if require_email and ( member.getProperty('email') and \
                                   not props.get( 'email', 'NoPropIsOk' )):
                return "You must enter a valid email address."

        return None

InitializeClass( RegistrationTool )


def initialize( context ):
    # module initialization callback

    context.registerTool( RegistrationTool )
