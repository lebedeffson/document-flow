######################################################################
#
# LDAPUser	The User object for the LDAP User Folder
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
######################################################################
__version__='$Revision: 1.5 $'[11:-2]

# General python imports
import time
from types import UnicodeType, StringType

# Zope imports
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from AccessControl.User import BasicUser
from AccessControl.Permissions import access_contents_information, manage_users
from DateTime import DateTime
from Globals import InitializeClass

# LDAPUserFolder package imports
from SimpleCache import deepCopyExtClass
from utils import _verifyUnicode, encoding, user_encoding


class LDAPUser(BasicUser):
    """ A user object for LDAP users """
    security = ClassSecurityInfo()
    security.declarePublic('getId')

    def __init__( self
                , name
                , password
                , roles
                , domains
                , user_dn
                , user_attrs
                , mapped_attrs
                , multivalued_attrs=()
                ):
        """ Instantiate a new LDAPUser object """
        self.name = _verifyUnicode(name)
        self.__ = password
        self._dn = _verifyUnicode(user_dn)
        self.roles = roles
        self.domains = []
        self.RID = ''
        self.groups = ''
        now = time.time()
        self._created = now
        self._lastactivetime = now
        self._properties = {}

        for key in user_attrs.keys():
            if key in multivalued_attrs:
                prop = user_attrs.get(key, [None])
            else:
                prop = user_attrs.get(key, [None])[0]

            if type(prop) is StringType:
                prop = _verifyUnicode(prop)

            self._properties[key] = prop

        for att_name, map_name in mapped_attrs:
            self._properties[map_name] = self._properties.get(att_name)

        self._properties['dn'] = user_dn

    __deepcopy__ = deepCopyExtClass


    ######################################################
    # User interface not implemented in class BasicUser
    #######################################################

    security.declarePrivate('_getPassword')
    def _getPassword(self):
        """ Retrieve the password """
        return self.__


    security.declarePublic('getUserName')
    def getUserName(self):
        """ Get the name associated with this user """
        if type(self.name) is UnicodeType:
            return self.name.encode(user_encoding)

        return self.name


    security.declarePublic('getRoles')
    def getRoles(self):
        """ Return the user's roles """
        if self.name == 'Anonymous User':
            return tuple(self.roles)
        else:
            return tuple(self.roles) + ('Authenticated',)


    security.declarePublic('getDomains')
    def getDomains(self):
        """ The user's domains """
        return self.domains


    def _delGroups( self, groupnames ):
        """ Remove groups from user """
        # if user object was expired by manage_editUserRoles
        # then the groups are already removed
        try:
            BasicUser._delGroups( self, groupnames )
        except ValueError:
            pass


    #######################################################
    # Overriding these to enable context-based role
    # computation with the LDAPUserSatellite
    #######################################################

    def getRolesInContext(self, object):
        """Return the list of roles assigned to the user,
           including local roles assigned in context of
           the passed in object."""
        roles = BasicUser.getRolesInContext(self, object)

        acl_satellite = self._getSatellite(object)
        if acl_satellite and hasattr(acl_satellite, 'getAdditionalRoles'):
            satellite_roles = acl_satellite.getAdditionalRoles(self)
            roles = list(roles) + satellite_roles

        return roles


    def allowed(self, object, object_roles=None):
        """ Must override, getRolesInContext is not always called """
        if BasicUser.allowed(self, object, object_roles):
            return 1

        acl_satellite = self._getSatellite(object)
        if acl_satellite and hasattr(acl_satellite, 'getAdditionalRoles'):
            satellite_roles = acl_satellite.getAdditionalRoles(self)

            for role in object_roles:
                if role in satellite_roles:
                    if self._check_context(object):
                        return 1

        return 0


    security.declarePrivate('_getSatellite')
    def _getSatellite(self, object):
        """ Get the acl_satellite (sometimes tricky!) """
        while 1:
            acl_satellite = getattr(object, 'acl_satellite', None)
            if acl_satellite is not None:
                return acl_satellite

            parent = aq_parent(aq_inner(object))
            if parent:
                object = parent
                continue

            if hasattr(object, 'im_self'):
                object = aq_inner(object.im_self)
                continue

            break

        return None


    #######################################################
    # Interface unique to the LDAPUser class of user objects
    #######################################################

    security.declareProtected(access_contents_information, '__getattr__')
    def __getattr__(self, name):
        """ Look into the _properties as well... """
        my_props = self._properties

        if my_props.has_key(name):
            prop = my_props.get(name)

            if type(prop) is UnicodeType:
                prop = prop.encode(user_encoding)

            return prop

        else:
            raise AttributeError, name


    security.declareProtected(access_contents_information, 'getProperty')
    def getProperty(self, prop_name, default=''):
        """
            Return the user property referred to by prop_name,
            if the attribute is indeed public.
        """
        prop = self._properties.get(prop_name, default)
        if type(prop) is UnicodeType:
            prop = prop.encode(user_encoding)

        return prop


    security.declareProtected(access_contents_information, 'getUserDN')
    def getUserDN(self):
        """ Return the user's full Distinguished Name """
        if type(self._dn) is UnicodeType:
            return self._dn.encode(user_encoding)

        return self._dn


    def _updateActiveTime(self):
        """ Update the active time """
        self._lastactivetime = time.time()


    def getLastActiveTime(self):
        """ When was this user last active? """
        return DateTime(self._lastactivetime)


    def getCreationTime(self):
        """ When was this user object created? """
        return DateTime(self._created)


InitializeClass(LDAPUser)
