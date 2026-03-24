"""
Membership tool class.

$Editor: vpastukhov $
$Id: MembershipTool.py,v 1.121 2008/12/05 09:43:59 oevsegneev Exp $
"""
__version__ = '$Revision: 1.121 $'[11:-2]
from Globals import DTMLFile

import re
from random import randrange
from string import lower, find
from types import StringType

from Acquisition import aq_inner, aq_base, aq_parent, aq_get
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from AccessControl.User import BasicUser, nobody
from BTrees.OOBTree import OOBTree
from DateTime import DateTime

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFCore.MembershipTool import MembershipTool as _MembershipTool
from Products.CMFCore.utils import getToolByName, _checkPermission

from interfaces.IDirectory import IDirectoryEntry

import Config
from Config import Roles
from ActionInformation import ActionInformation as AI
from DFRoleManager import DFRoleManager
from Exceptions import Unauthorized
from ResourceUid import ResourceUid
from SimpleObjects import ToolBase, SimpleRecord
from Utils import InitializeClass, getLanguageInfo, getNextTitle, translit_string, uniqueValues, isSequence

class MembershipTool( ToolBase, _MembershipTool ):
    """ Portal Membership Tool """
    _class_version = 1.50

    meta_type = 'NauSite Membership Tool'

    security = ClassSecurityInfo()

    manage_options = _MembershipTool.manage_options # + ToolBase.manage_options

    memberareaCreationFlag = 0

    _properties = [ { 'id': 'staff_list_directory', 'type': 'link', 'mode': 'w' },
                    { 'id': 'employee_list_directory', 'type': 'link', 'mode': 'w' },
                  ]

    _interface_properties = [ {'id':'viewing_document_number', 'default':10},
                              {'id':'cleanup', 'default':1},
                              {'id':'external_editor_buttons', 'default':0},
                              {'id':'contents_size', 'default':0},
                            ]

    _actions = (
            AI( id='logout'
              , title='Log out'
              , description='Click here to logout'
              , action=Expression( text='string: ${portal_url}/logout' )
              , permissions=(CMFCorePermissions.View,)
              , category='user'
              , condition=Expression(text='member')
              , visible=True
              ),
            AI( id='manageGroups'
              , title='Manage groups'
              , description='User groups management'
              , action=Expression( text='string: ${portal_url}/manage_groups_form' )
              , permissions=(CMFCorePermissions.ManagePortal,)
              , category='user'
              , condition=None
              , visible=True
              ),
            AI( id='manageUsers'
              , title='Manage users'
              , action=Expression( text='string: ${portal_url}/manage_users_form' )
              , permissions=(ZopePermissions.manage_users,)
              , category='user'
              , condition=None
              , visible=True
              ),
            AI( id='addUser'
              , title='Create user'
              , action=Expression( text='string: ${portal_url}/join_form' )
              , permissions=(ZopePermissions.manage_users,)
              , category='user'
              , condition=None
              , visible=True
              ),
            AI( id='preferences'
              , title='Preferences'
              , description='Change your user preferences'
              , action=Expression( text='string: ${portal_url}/personalize_form' )
              , permissions=(CMFCorePermissions.View,)
              , category='user'
              , condition=Expression(text='member')
              , visible=True
              ),
            AI( id='interfacePreferences'
              , title='Interface preferences'
              , description='Change your interface preferences'
              , action=Expression( text='string: ${portal_url}/interface_preferences_form' )
              , permissions=(CMFCorePermissions.View,)
              , category='user'
              , condition=Expression(text='member')
              , visible=True
              ),
            AI( id='changePassword'
              , title='Change password'
              , description='Change your password'
              , action=Expression( text='string: ${portal_url}/password_form' )
              , permissions=(CMFCorePermissions.View,)
              , category='user'
              , condition=Expression(text='python: member and not portal.portal_membership.isLDAPReadOnly()')
              , visible=True
              ),
            AI( id='favorites'
              , title='Add to Favorites'
              , description='Add to Favorites'
              , action=Expression( text='string: ${object_url}/addtoFavorites' )
              , permissions=(CMFCorePermissions.View,)
              , category='object'
              , condition=Expression(text='python: object.implements("Contentish") and'
                                          ' portal.portal_membership.getPersonalFolder() and folder is not object')
              , visible=True
              ),
        )

    _member_sources = {
        'user': {
            'title' : "User",
            'order' : 1,
            'values':
                lambda membership:
                    membership.listMembers(),
            'value_title':
                lambda value:
                    value.getMemberName(positions = True)
        },
        'group': {
            'title' : "Group",
            'order' : 2,
            'resolve':
                lambda membership, context, group:
                    membership.listGroupMembers(group),
            'values':
                lambda membership:
                    membership.listGroups(),
            'value_title':
                lambda value: value.Title()
        },
        'role': {
            'title' : "Role",
            'order' : 3,
            'resolve':
                lambda membership, context, role:
                    [member
                     for member in membership.listMembers()
                     if member.has_role(role, context)],
            'values':
                lambda membership:
                    ('VersionOwner', 'Owner', 'Reader', 'Writer', 'Editor'),
            'value_title':
                'localize' # this means that title is localized value
        }
    }

    def _initstate( self, mode ):
        """ Initialize attributes
        """
        if not ToolBase._initstate( self, mode ):
            return 0

        if getattr( self, 'role_map', None ) is None:
            self.role_map = OOBTree()

        return 1

    #
    # Users support
    #

    def addMember( self, id, password, roles, domains, properties=None, groups=Missing ):
        """
            Adds a new member to the user folder.
        """
        # XXX remove this when registration tool supports groups argument
        if groups is Missing and properties.has_key('storage'):
            groups = [ properties['storage'] ]

        self.__getPUS().userFolderAddUser( id, password, roles, domains, groups=groups )
        member = self.getMemberById( id, raise_exc=True )

        if properties is not None:
            member.setMemberProperties( properties )

        # this is required if stored password is encrypted
        # and must be mailed to the user after registration
        member.getUser().__ = password

    security.declareProtected( CMFCorePermissions.ManagePortal, 'deleteMembers' )
    def deleteMembers( self, userids ):
        """
            Delete one or more members
        """
        if not userids:
            return
        # XXX should we verify each ids in the list?

        userfolder = self.__getPUS()
        catalog    = getToolByName( self, 'portal_catalog' )
        memberdata = getToolByName( self, 'portal_memberdata' )

        # cleanup objects ownership
        results = catalog.unrestrictedSearch( Creator=userids )

        for item in results:
            object = item.getObject()
            if object is None:
                continue # should not happen
            object.changeOwnership( None ) # does reindex

        # cleanup local roles
        roles   = [ 'user:%s' % id for id in userids ]
        results = catalog.unrestrictedSearch( allowedRolesAndUsers=roles )

        for item in results:
            object = item.getObject()
            if object is None:
                continue # should not happen
            object.manage_delLocalRoles( userids )
            object.reindexObject( idxs=['allowedRolesAndUsers','Creator'] )

        # filter out orphaned users
        accounts = userfolder.getUserNames()
        accounts = [ id for id in userids if id in accounts ]

        # remove user accounts
        userfolder.userFolderDelUsers( accounts )

        # purge member data; this is the last since it looks in the userfolder
        memberdata.pruneMemberDataContents( userids )

    def wrapUser( self, u, wrap_anon=False ):
        """
            Sets up the correct acquisition wrappers for a user.

            Does not ignore errors as the original CMF method does.
        """
        b = getattr( u, 'aq_base', None )
        if b is None:
            b = u
            u = u.__of__( self.__getPUS() )
        if (b is nobody and not wrap_anon) or hasattr( b, 'getMemberId' ):
            return u

        if hasattr( self, 'role_map' ):
            for prole, role in self.role_map.items():
                if role in u.roles and prole not in u.roles:
                    u.roles.append( prole )

        md = getToolByName( self, 'portal_memberdata' )
        return md.wrapUser( u )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getMemberById' )
    def getMemberById( self, id, containment=False, raise_exc=False ):
        """
            Returns the given member object.
        """
        users = self.__getPUS()
        if containment:
            users = aq_inner( users )
        u = users.getUser( id )
        if u is None:
            mdata = getToolByName( self, 'portal_memberdata' )
            if mdata.getMemberData( id, None ) is not None:
                u = OrphanedUser( id, '', [Roles.Orphaned,Roles.Locked] )
        if u is not None:
            if containment:
                u = u.__of__( users )
            u = self.wrapUser(u)
        elif raise_exc:
            raise KeyError, id
        return u

    security.declarePublic('getMemberName')
    def getMemberName( self, u_id=None, brief=False, positions=False ):
        """
           Returns the formatted member name/surname
           or just login if no user data specified.
        """
        if u_id is None:
            member = self.getAuthenticatedMember()
        else:
            member = self.getMemberById( u_id )
        if not member:
            return u_id
        try:
            return member.getMemberName( brief=brief, positions=positions )
        except AttributeError:
            return u_id

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listMembers' )
    def listMembers( self, all=False ):
        """
            Lists all the registered members.
        """
        return map(self.getMemberById, self.listMemberIds(all))

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listMemberIds' )
    def listMemberIds( self, all=False ):
        """
            Lists Ids of all the registered members.
        """
        user_folder = self.__getPUS()
        results = user_folder.getUserNames()

        if all:
            # append orphaned users
            mdata = getToolByName( self, 'portal_memberdata' )
            for id in mdata.listStoredMemberIds():
                if id not in results:
                    results.append( id )
        else:
            # filter out locked users
            def isUserLocked( id ):
                u = userfolder.getUser( id )
                return u and u.has_role( Roles.Locked )

            userfolder = self.__getPUS()
            results = [ id for id in results if not  isUserLocked( id )]

        return results

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listMemberNames' )
    def listMemberNames( self, all=False ):
        """
            Returns (id, full name) tuple for each member
        """
        results = []
        for id in self.listMemberIds( all=all ):
            name = self.getMemberName( id )
            results.append( (name, {'user_id':id, 'user_name':name}) )

        results.sort()
        return [ r[1] for r in results ]

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'getMemberBriefName' )
    def getMemberBriefName( self, u_id=None ):
        """
           deprecated use getMemberName with brief arg
        """
        if u_id is None:
            member = self.getAuthenticatedMember()
        else:
            member = self.getMemberById( u_id )

        return member and member.getMemberBriefName() or u_id

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'getMemberEmail' )
    def getMemberEmail( self, u_id ):
        """
           Returns the user email address or None if
           no user data specified.
        """
        member = self.getMemberById( u_id )
        return member and member.getMemberEmail()

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'getUserInfo' )
    def getUserInfo( self, u_id ):
        """
          Get user personal data

          Returns: user info dictionary
        """
        info = {}
        member = self.getMemberById( u_id )
        if member:
            for key in member.getTool().propertyIds():
                info[key] = member.getProperty( key )
            info['is_orphaned'] = member.has_role( Roles.Orphaned )
            info['is_locked']   = member.has_role( Roles.Locked )
            info['positions']   = member.listPositions()
        return info

    #
    #   User groups interface methods
    #

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'getGroup' )
    def getGroup( self, id, default=Missing ):
        """
            Returns the group object.
        """
        return self.__getPUS().getGroupById( id, default )

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listGroups' )
    def listGroups( self ):
        """
            Return a user groups list
        """
        group_names = list( self.__getPUS().getGroupNames() )
        group_names.sort()
        return map( self.__getPUS().getGroupById, group_names )

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listGroups' )
    def listGroupIds( self ):
        """
            Return a user group ids list
        """
        return list( self.__getPUS().getGroupNames() )

    def expandUserList( self, user_groups=(), members=() ):
        """
          Returns a plain users list using groups and
        """
        users = list( members )
        for group in user_groups:
            users.extend( self.getGroup(group).getUsers() )

        return uniqueValues( users )

    def isGroupInheritsRole( self, object, groupid, role ):
        """
            Does this role is inherited from the parent?
        """
        return role not in object.get_local_roles_for_groupid( groupid ) \
           and self.isGroupInRole( object, groupid, role )

    def isGroupInRole( self, object, groupid, role ):
        """
            Check whether the group has
            the given permission over the object
        """
        while not object.implements('isPortalRoot'):
            if role in object.get_local_roles_for_groupid( groupid ):
                return 1
            object = object.aq_parent
        return 0

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_groups')
    def manage_groups( self, REQUEST, addGroup=None, delGroup=None ):
        """
          Create or delete the user group
          Called by the management screen.
        """
        msg  = getToolByName( self, 'msg' )
        if addGroup is None and delGroup is None:
            addGroup = REQUEST.get('addGroup', '')
            delGroup = REQUEST.get('delGroup', '')

        if addGroup:
            title = REQUEST.get('group')
            if title:
                id = translit_string( title, self.getLanguage() )
                if id in [group.getId() for group in self.listGroups()]:
                    message = msg("Group '%s' already exists.") % title
                    return self.redirect( action='manage_groups_form', REQUEST=REQUEST, message=message )
                return self._addGroup( id, title, REQUEST )

        if delGroup:
            ids = REQUEST.get('groups')
            return self._delGroups( ids, REQUEST )

        if REQUEST is not None:
            return self.redirect( action='manage_groups_form', REQUEST=REQUEST )

    def _addGroup( self, group, title=None, REQUEST=None ):
        if not group:
            return

        self.__getPUS().userFolderAddGroup( group, title or group )

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.portal_url() + '/group_edit_form?group_id=' + group)

    def _delGroups( self, groups, REQUEST=None ):
        if not groups: return

        self.__getPUS().userFolderDelGroups(groups)

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.portal_url() + '/manage_groups_form')


    security.declareProtected(CMFCorePermissions.ChangePermissions, 'manage_changeGroup')
    def manage_changeGroup(self, group=None, group_users=None, title=None, REQUEST=None):
        """
           Assign the users to the given group
           and change the group description
        """
        if group is None:
            group = REQUEST.get('group')
            group_users = REQUEST.get('group_users', [])
            title = REQUEST.get('title', '')

        elif group_users is None:
            group_users = []

        acl_users = self.__getPUS()
        acl_users.setUsersOfGroup( group_users, group )

        if title is not None:
            acl_users.getGroupById(group).setTitle(title)

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.portal_url() + '/manage_groups_form')

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'canListMembers' )
    def canListMembers( self, group ):
        """
            Checks whether the current user can list members of a group.

            Arguments:

                'group' -- group object or identifier of interest

            Result:

                Boolean value.
        """
        policy = Config.GroupAccessPolicy

        if policy == 'all':
            # any user can list members of any group
            return 1

        if _checkPermission( ZopePermissions.manage_users, self ):
            # portal manager can list members of any group
            return 1

        if policy == 'member':
            # only group member can list other members of the group
            return self.getAuthenticatedMember().isMemberOfGroup( group )

        # users cannot list group members
        return 0

    security.declareProtected( CMFCorePermissions.ListPortalMembers, 'listGroupMembers' )
    def listGroupMembers( self, group ):
        """
            Returns members of a given group.

            Arguments:

                'group' -- either group object or identifier string

            Result:

                List of user objects (MemberData).
        """
        if type(group) is StringType:
            group = self.getGroup( group )

        if not self.canListMembers( group ):
            raise Unauthorized( group )

        # XXX group may return invalid users in case users/groups source was switched
        return filter( None, map( self.getMemberById, group.getUsers() ) )

    security.declarePrivate( 'listSubordinateUsers' )
    def listSubordinateUsers( self, user=None, include_chief=None ):
        """
            Returns names of users subordinate to the specified user.

            Positional arguments:

                'user' -- optional user object or username of the user
                        whose subordinates are requested; if not given
                        subordinates of the current user are returned

            Keyword arguments:

                'include_chief' -- boolean flag indicating that the user
                        himself should be included in results list too;
                        default is not to include

            Result:

                List of usernames (user IDs).
        """
        if user is None:
            user = self.getAuthenticatedMember()
        if type(user) is StringType:
            user_id = user
        else:
            user_id = user.getId()

        user_ids = []
        if include_chief:
            user_ids.append( user_id )

        return user_ids

    #
    # Personal folders
    #

    security.declarePublic( 'getPersonalFolder' )
    def getPersonalFolder( self, *args, **kw ):
        """
            Returns the current user's personal folder object by type.
        """
        user = self.getAuthenticatedMember()
        if hasattr(user, 'getPersonalFolder'):
            return user.getPersonalFolder( *args, **kw )

    security.declarePublic( 'getPersonalFolderPath' )
    def getPersonalFolderPath( self, *args, **kw ):
        """
            Returns the path to the current user's personal folder by type.
        """
        user =self.getAuthenticatedMember()
        if hasattr(user, 'getPersonalFolderPath'):
            return user.getPersonalFolderPath( *args, **kw )

    security.declarePublic( 'getPersonalFolderUrl' )
    def getPersonalFolderUrl( self, *args, **kw ):
        """
            Returns the URL of the current user's personal folder by type.
        """
        user = self.getAuthenticatedMember()
        if hasattr(user, 'getPersonalFolderUrl'):
            return user.getPersonalFolderUrl( *args, **kw )

    def listAllowedUsers( self, object, roles=None, all=False ):
        """
          Returns a list of roles and users with View permission.
          Used by PortalCatalog to filter out items you're not allowed to see.
        """
        allowed = []
        roles = roles or Config.ManagedLocalRoles

        for id in self.listMemberIds( all=all ):
            member = self.getMemberById( id, raise_exc=True )
            if member.has_role(roles, object):
                allowed.append( id )

        return allowed

    security.declarePublic('listSortedUserNames')
    def listSortedUserNames( self, ids, do_sort=True, positions=False ):
        """
            TODO: rename to listUserNames
        """
        results = []
        for id in ids:
            results.append( {  'user_id': id,
                               'user_name': self.getMemberName( id, positions=positions ),
                               'user_position': self.listMemberPositions( id )
                               } )
        if do_sort:
            results.sort(lambda x, y: cmp(lower(x['user_name']), lower(y['user_name'])))
        return results

    # Task templates support functions
    # added to member attribute:
    # taskTemplates - dictionary with format:
    #    {taskTemplate_id :{'responsible_users':[userIds], 'supervisor': userId, 'name': name}, ...}

    security.declarePublic( 'saveTaskTemplate' )
    def saveTaskTemplate(self, template_id=None, template_name='', supervisor='', users=[]):
        """Save task Template for current user.
        """
        # if taskTemplate_id present - save template with this id,
        # else generate new unique id
        member=self.__getMember()
        if not template_id:
            template_id = str(randrange(1, 2000000000))
            while member.taskTemplates.has_key(template_id):
                template_id = str(randrange(1, 2000000000))

        member.taskTemplates[template_id] = {'name':template_name, \
                        'responsible_users':users, 'supervisor':supervisor}

        member._p_changed = 1
        return template_id

    security.declarePublic( 'deleteTaskTemplate' )
    def deleteTaskTemplate(self, template_id):
        """Remove task template with given template_id.
        """
        member = self.__getMember()
        if not member.taskTemplates.has_key(template_id): return

        del(member.taskTemplates[template_id])
        member._p_changed = 1

    security.declarePublic( 'getTaskTemplate' )
    def getTaskTemplate(self, template_id):
        """Return task template having template_id, if not exists - return empty template.
        """
        member=self.__getMember()
        res_template = {'name':'', 'responsible_users':[], 'supervisor':''}

        if member.taskTemplates=={}:
            return res_template

        if template_id and member.taskTemplates.has_key(template_id):
            res_template = member.taskTemplates[template_id]

        return res_template

    security.declarePublic( 'listTaskTemplates' )
    def listTaskTemplates(self):
        """Return all task templates for current user
        """
        member=self.__getMember()
        return member.taskTemplates

    security.declarePublic( 'processTemplateActions' )
    def processTemplateActions(self, REQUEST):
        """Function for processing all template form actions
        """
        come_from_doc_confirmation_form = REQUEST.get('from_document_confirmation') is not None
        t_action = str(REQUEST.get('template_action', ''))

        if t_action=='save_template':
            template_id = REQUEST.get('template_list', None)
            template_name = REQUEST.get('template_name', '')
            involved_users = REQUEST.get('involved_users', [])

            if come_from_doc_confirmation_form:
                template = self.getTaskTemplate(template_id)
                # leave old value of supervisor, because we dont change them
                supervisor = template['supervisor']
            else:
                supervisor = REQUEST.get('supervisor', None)

            if template_name and involved_users:
                self.saveTaskTemplate(template_id, template_name, supervisor, involved_users)

        elif t_action=='create_new_template':
            template_name = REQUEST.get('template_name', '')
            supervisor = REQUEST.get('supervisor', None)
            involved_users = REQUEST.get('involved_users', [])

            if template_name and involved_users:
                q = self.saveTaskTemplate(None, template_name, supervisor, involved_users)

        elif t_action=='delete_template':
            self.deleteTaskTemplate( REQUEST.get('template_list', None) )

        brains_type = REQUEST.has_key('brains_type') and REQUEST.get('brains_type') or ''

        if come_from_doc_confirmation_form:
            REQUEST.RESPONSE.redirect('%s/document_confirmation_form?brains_type=%s' % (REQUEST['URL2'], brains_type ))
        else:
            REQUEST.RESPONSE.redirect('%s/task_add_form?brains_type=%s' % (REQUEST['URL2'], brains_type ))

    # filter suport functions
    # We add to to member 2 attributes:
    # 1. filters - dictionary with format
    #     {filter_id_1:{'filter':filter_content, 'name':filter_name}, ...}
    # 2. main_filter_id - id of default filter
    def saveFilter(self, filter_id=None, filter_name='', folderFilter='', user_name=None):
        # if filter_id present - save filter with this id,
        # else generate new unique id
        member=self.__getMember(user_name)
        if not filter_id:
            while 1:
                filter_id = str(randrange(1, 2000000000))
                if not member.filters.has_key(filter_id):
                    break

        member.filters[filter_id] = {'filter':folderFilter, 'name':filter_name}
        # if this is first filter make it as main filter
        if len(member.filters.keys())==1:
            member.main_filter_id = filter_id

        member._p_changed = 1
        return filter_id

    def deleteFilter(self, filter_id):
        """
          delete fiter with filter_id
        """
        member = self.__getMember()
        if not member.filters.has_key(filter_id): return

        del(member.filters[filter_id])
        # if this is main filter make other filter as main
        if member.main_filter_id==filter_id:
            if len(member.filters)>0:
                member.main_filter_id = member.filters.keys()[0]
            else:
                member.main_filter_id = None

        member._p_changed = 1

    def setMainFilter(self, filter_id):
        """
          set filter with filter_id as main filter
        """
        member=self.__getMember()
        if member.filters.has_key(filter_id):
            member.main_filter_id = filter_id

    security.declarePublic( 'getFilter' )
    def getFilter( self, REQUEST ):
        # return current selected filter as dictionary with format
        # {'name':filter_name, 'filter':filter_content}
        # if hasn't current filter - return main filter and make it as current
        member = self.__getMember()
        res_filter = { 'name':'', 'filter':'' }

        if not ( member.filters and REQUEST.get('filter_is_on') ):
            return res_filter

        currFilterId = REQUEST.SESSION.get('current_filter_id', 0)
        if not ( currFilterId and member.filters.has_key( currFilterId ) ):
            currFilterId = REQUEST.SESSION['current_filter_id'] = member.main_filter_id

        return member.filters[ currFilterId ]

    security.declarePublic( 'listFilters' )
    def listFilters( self ):
        # return list of filtres in format:
        # [[filter_id, filter_name], ...]
        result_list=[]
        member=self.__getMember()
        for id, item in member.filters.items():
            result_list.append({ 'id':id, 'name':item['name'] })
        return result_list

    security.declarePublic( 'isMainFilterId' )
    def isMainFilterId( self, filter_id='' ):
        """
          returns truth if filter with filter_id is main filter
        """
        return self.__getMember().main_filter_id == filter_id

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setDefaultFilters' )
    def setDefaultFilters( self, user_name=None ):
        """
          set default filters to user 'user_name' and deletes other filters of user 'user_name'
        """
        for item in self.listFilters():
            self.deleteFilter( item['id'] )

        filter = {'filter_by_Type': ['HTMLDocument', 'Heading']}
        cfilter = self.encodeFolderFilter(filter)
        self.saveFilter(filter_name='Heading+Documents', folderFilter=cfilter, user_name=user_name)

        filter = {'filter_by_Type': ['HTMLDocument']}
        cfilter = self.encodeFolderFilter(filter)
        self.saveFilter(filter_name='Documents', folderFilter=cfilter, user_name=user_name)

    security.declarePublic( 'processFilterActions' )
    def processFilterActions( self, REQUEST ):
        """ this function for processing all filter form actions
        uses '*.x' REQUEST keys from input 'image' elements.
        """
        SESSION = REQUEST.SESSION
        filter_id = REQUEST.get('current_filter_id') \
                 or SESSION.get('current_filter_id')

        if REQUEST.get('save_filter.x'):
            filter_name = REQUEST.get('filter_name', '')
            folderFilter = self.encodeFolderFilter(REQUEST)
            self.saveFilter(filter_id, filter_name, folderFilter)
            if REQUEST.get('set_main_filter', 0):
                self.setMainFilter( SESSION.get('current_filter_id', '') )

        elif REQUEST.get('create_new_filter.x'):
            msg  = getToolByName( self, 'msg' )
            name = REQUEST.get( 'filter_name', '' )
            name = getNextTitle( name or msg('Filter'),
                               [ item['name'] for item in self.listFilters() ] )

            folderFilter = self.encodeFolderFilter( REQUEST )
            filter_id = self.saveFilter( None, name, folderFilter )

            SESSION.set( 'current_filter_id', filter_id )

        elif REQUEST.get('load_filter.x'):
            REQUEST.RESPONSE.setCookie('filter_is_on', '1', path='/',
                                        expires='Wed, 19 Feb 2020 14:28:00 GMT')
            filter_id = REQUEST.get('filterList')
            if filter_id:
                SESSION.set( 'current_filter_id', filter_id )

        elif REQUEST.get('delete_filter.x'):
            self.deleteFilter( SESSION.get('current_filter_id', '') )
            SESSION.set( 'current_filter_id', 0 )

        elif REQUEST.get('open_filter_form.x') or REQUEST.get('open_filter_form'):
            REQUEST.RESPONSE.setCookie('filter_is_on', '1', path='/',
                                        expires='Wed, 19 Feb 2020 14:28:00 GMT')
            REQUEST.RESPONSE.setCookie('show_filter_form', '1', path='/',
                                        expires='Wed, 19 Feb 2020 14:28:00 GMT')

        elif REQUEST.get('close_filter_form.x'):
            REQUEST.RESPONSE.expireCookie('show_filter_form', path='/')

        elif REQUEST.get('disable_filter.x'):
            REQUEST.RESPONSE.expireCookie('filter_is_on', path='/')
            REQUEST.RESPONSE.expireCookie('show_filter_form', path='/')

        if REQUEST['URL2'] == self.portal_url():
            REQUEST.RESPONSE.redirect(self.portal_url() + '/storage#filter')
        else:
            REQUEST.RESPONSE.redirect(REQUEST['URL2'] + '/#filter')

    # Interface Preferences functions

    security.declarePublic( 'getInterfacePreferences' )
    def getInterfacePreferences(self, name=None):
        """
          Returns the member's interface preferences

          If 'name' is None, the whole settings map is returned.
        """
        preferences = self.__getMember().interfacePreferences
        for p in self._interface_properties:
            if not preferences.has_key(p['id']):
                preferences[p['id']] = p['default']

        if name:
            return preferences.get(name)

        return preferences

    security.declarePublic( 'setInterfacePreferences' )
    def setInterfacePreferences( self, REQUEST=None ):
        member = self.__getMember()
        for p in self._interface_properties:
            member.interfacePreferences[p['id']] = REQUEST.get( p['id'] )

        member._p_changed = 1

    # folder views support functions
    # We add to to member 2 attributes:
    # 1. folder_views - dictionary with format
    #    {folder_view_1_name:{'param_1':param_1_value, ...}, ...}
    # 2. current_folder_view - id of current selected folder view
    security.declarePublic( 'listFolderViews' )
    def listFolderViews(self):
        return self.__getMember().folder_views.keys()

    security.declarePublic( 'getCurrentFolderView' )
    def getCurrentFolderView(self):
        return self.__getMember().current_folder_view

    security.declarePublic( 'getCurrentFolderView' )
    def setFolderView(self, view_name='', REQUEST=None):
        """function for setting current folder view"""
        member = self.__getMember()
        if member.folder_views.has_key(view_name):
            member.current_folder_view = view_name

        if REQUEST is not None:
            qs = REQUEST.get('qs', 0)
            if qs=='undefined': qs=0
            if REQUEST['URL2'] == self.portal_url():
                REQUEST.RESPONSE.redirect(self.portal_url() + '/storage/folder_contents?qs=' + str(qs))
            else:
                REQUEST.RESPONSE.redirect(REQUEST['URL2'] + '/folder_contents?qs=' + str(qs))

    security.declarePublic( 'setCurrFolderViewParam' )
    def setCurrFolderViewParam(self, param_name='', param_value='', REQUEST=None):
        """function for setting current folder view param value"""
        member = self.__getMember()
        if member.folder_views[member.current_folder_view].has_key(param_name):
            member.folder_views[member.current_folder_view][param_name] = param_value
            member._p_changed = 1

        if REQUEST: REQUEST.RESPONSE.redirect(REQUEST['URL2'] + '/')

    security.declarePublic( 'getCurrFolderViewParam' )
    def getCurrFolderViewParam(self, param_name):
        member = self.__getMember()
        if member.folder_views[member.current_folder_view].has_key(param_name):
            return member.folder_views[member.current_folder_view][param_name]
        return ''

    security.declarePublic( 'getLanguage' )
    def getLanguage( self, preferred=None, REQUEST=None ):
        """
            Returns selected language for the current user.
        """
        if not preferred:
            REQUEST = REQUEST or aq_get( self, 'REQUEST', None )
            lang = REQUEST and REQUEST.get( 'LOCALIZER_LANGUAGE' )
            if lang and getLanguageInfo( lang, None ):
                return lang

        return self.getAuthenticatedMember().getProperty( 'language', None ) \
            or getToolByName( self, 'msg' ).get_default_language()

    security.declareProtected( CMFCorePermissions.SetOwnProperties, 'setMemberLanguage' )
    def setMemberLanguage( self, lang ):
        """
            Changes language for the current user.
        """
        if lang:
            member = self.getAuthenticatedMember()
            member.setProperties( language=lang )

    security.declarePublic( 'getFontFamily' )
    def getFontFamily( self, style='general', REQUEST=None ):
        """
            Returns font names by style for the current language.
        """
        lang = self.getLanguage( REQUEST=REQUEST )
        return getLanguageInfo( lang ).get( style+'_font', '' )

    # different useful functions
    security.declarePublic('convertToList')
    def convertToList(self, obj):
        if not obj: return []
        elif type(obj)==type(''): return [obj]
        return obj

    def __getMember(self, user_name=None):
        # this function return current authorized member
        # and add to member, if it needed, some params
        if user_name is None:
            m = self.getAuthenticatedMember()
        else:
            m = self.getMemberById( str(user_name) )
        if aq_base( m ) is nobody:
            return m
        member = m.getUser()
        # check task templates support presense
        if not hasattr(member, 'taskTemplates'):
            member.taskTemplates = {}
            member._p_changed = 1
        # check filter support presence
        if not hasattr(member, 'main_filter_id'):
            member.main_filter_id = None
            member.filters = {}
            member._p_changed = 1
        # check folder views suport presence
        if not hasattr(member, 'current_folder_view'):
            member.current_folder_view = 'default'
            member.folder_views = {'default':{}, 'table':{'reverse':'1', 'sort_by':'Title'}, 'outgoing': {}}
            member._p_changed = 1
        if not hasattr(member, 'interfacePreferences'):
            member.interfacePreferences = {}
            for p in self._interface_properties:
                member.interfacePreferences[p['id']] = p['default']
            member._p_changed = 1

        if member.interfacePreferences.has_key('nausite_nav_frame'):
            del member.interfacePreferences['nausite_nav_frame']
            member._p_changed = 1

        return member

    def __checkDocumentForAction(self, doc):
        # this function return true, if current user is site admin or
        # has role 'Editor' for this document; else return false
        member = self.__getMember()
        username = member.getUserName()
        return (username in doc.requiredUsers) or \
                (doc.state=='awaiting' and \
                 ( ('Manager' in member.getRoles()) or ('Editor' in doc.getObject().user_roles() ) )\
                )

    security.declarePublic( 'filterDocumentsForAction')
    def filterDocumentsForAction(self, allDocuments):
        return filter(self.__checkDocumentForAction, allDocuments)

    #
    # LDAP support
    #

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getUsersSource' )
    def getUsersSource( self ):
        """
        """
        return self.__getPUS().getUsersType()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getGroupsSource' )
    def getGroupsSource( self ):
        """
        """
        return self.__getPUS().getGroupsType()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setUsersSource' )
    def setUsersSource( self, auth ):
        """
        """
        return self.__getPUS().setSourceFolder( auth, users=1 )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setGroupsSource' )
    def setGroupsSource( self, auth ):
        """
        """
        return self.__getPUS().setSourceFolder( auth, groups=1 )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'getAuthSettings' )
    def getAuthSettings( self, auth=None ):
        """
        """
        userfolder = self.__getPUS()

        if auth is None:
            auth = self.getUsersSource()

        if auth == 'ldap':
            info = userfolder.getLDAPSettings()
            if info is None:
                info = SimpleRecord( address=None
                                   , binduid=''
                                   , login_attr=''
                                   , read_only=1 )
        else:
            info = SimpleRecord()

        info.auth_frontend = userfolder.getProperty('auth_frontend')
        return info

    security.declareProtected( CMFCorePermissions.View, 'isLDAPReadOnly' )
    def isLDAPReadOnly( self ):
        return self.getAuthSettings().get('read_only')

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setAuthSettings' )
    def setAuthSettings( self, auth, data ):
        """
        """
        userfolder = self.__getPUS()
        userfolder._updateProperty( 'auth_frontend', data.auth_frontend )

        try:
            userfolder.getSourceFolder( auth )
        except ValueError:
            userfolder.createAuthFolder( auth )

        if auth == 'ldap':
            userfolder.setLDAPSettings( data )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'setPropertiesMapping' )
    def setPropertiesMapping( self, auth, mapping ):
        """
        """
        userfolder = self.__getPUS()
        if auth == 'ldap':
            userfolder.setLDAPSchemaMapping( mapping )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'changePropertyMapping' )
    def changePropertyMapping( self, auth, id, title='', property=None ):
        """
        """
        userfolder = self.__getPUS()
        if auth == 'ldap':
            userfolder.changeLDAPSchemaAttribute( id, title, property )

    security.declareProtected( CMFCorePermissions.ManagePortal, 'refreshUserRecords' )
    def refreshUserRecords( self ):
        """
        """
        self.__getPUS().invalidateCache()

    security.declarePrivate( 'updateLoginTime' )
    def updateLoginTime( self, user ):
        """
        """
        member = self.getMemberById( str(user), raise_exc=False )
        if member is not None:
            member.login_time = DateTime()

    security.declareProtected( CMFCorePermissions.ManagePortal, 'copyAccessRights' )
    def copyAccessRights( self, source_user, target_user ):
        """
        """
        portal_catalog= getToolByName( self, 'portal_catalog' )
        member_source_user = self.getMemberById( source_user, raise_exc=True )
        users_groups=member_source_user.getGroups()
        allowed_folders= portal_catalog.unrestrictedSearch(allowedRolesAndUsers='user:'+source_user,implements='isPrincipiaFolderish')
        home_phys_path = str(member_source_user.getPersonalFolderPath())

        # copying groups
        for group in users_groups:
            group_users = list(self.getGroup(group).getUsers() )
            group_users.append( target_user )
            self.manage_changeGroup( group, group_users )

        #  copying rights for folders
        for folder in allowed_folders:
            object = folder.getObject()
            obj_phys_path = object.physical_path()
            local_roles = list(object.get_local_roles_for_userid(source_user))
            if local_roles:
                local_source_user_roles=local_roles[:]
                if Config.Roles.Editor in local_source_user_roles:
                    if Config.Roles.Writer in local_source_user_roles:
                        local_source_user_roles.remove(Config.Roles.Editor)
                    else:
                        local_source_user_roles[local_source_user_roles.index(Config.Roles.Editor)]=Config.Roles.Writer
                object.setLocalRoles(target_user,local_source_user_roles)
                object.reindexObject( idxs=['allowedRolesAndUsers'], recursive=0 )

    def isUserLocked(self, user):
        """
        """
        return False

    def listSourceIds(self):
        """
        """
        items = [(v['order'], k)
                 for k, v in self._member_sources.items()]
        items.sort()

        return list( zip(*items)[1] )

    def getSourceProperty(self, id, name):
        """
        """
        return self._member_sources[id].get(name)

    def getSourceItems(self, id, uids = None):
        title = self.getSourceProperty(id, 'value_title')

        if title == 'localize': title = self.msg

        if uids is None:
            return [(ResourceUid(value, id), title(value))
                    for value in self.getSourceProperty(id, 'values')(self)]

        return [(uid, title( uid.deref(self) )) for uid in uids]

    def resolveSource(self, id, context, value):
        """
        """
        resolver = self.getSourceProperty(id, 'resolve')

        if not resolver:
            return [value]

        return resolver(self, context, value)

    def getSourceTemplate(self, id):
        """
        """
        return getattr(self, self.getSourceProperty(id, 'template'))

## <TODO: move to StaffListDirectory addon>

    def getStaffList( self ):
        return self.getProperty( 'staff_list_directory' )

    def getEmployeeList( self ):
        return self.getProperty( 'employee_list_directory' )

    def listMemberPositions( self, member ):
        if isinstance( member, StringType ):
            member = self.getMemberById( member )

        if member is None:
            return
        return member.listPositions()

    def listMemberDivisions( self, member ):
        if isinstance( member, StringType ):
            member = self.getMemberById( member )

        if member is None:
            return

        return member.listDivisions()

    def resolvePosition( self, position, plain_users=False ):
        staff_list = self.getStaffList()
        if not staff_list:
            return

        if position.startswith( 'div:' ):
            return self.resolveDivision( position[4:], plain_users=False )
        if position.startswith( 'pos:' ):
            position = position[4:]

        entry = staff_list.getEntry( position )
        if plain_users:
            return self.listPlainUsers( entry )
        else:
            return entry

    def resolveDivision( self, division, plain_users=False ):
        if division.startswith( 'div:' ):
            division = division[4:]

        entry = self.resolvePosition( division )
        entries = [ entry ]
        entries.extend( entry.listEntries().listItems() )
        
        if plain_users:
            return self.listPlainUsers( entries )
        else:
            return entries


    def listPlainUsers( self, values, filter_locked=True, context=Missing ):
        if not isSequence( values ):
            values = [ values ]

        r = []
        for value in values:
            # we just trust that this is a staff list directory entry
            if isDirectoryEntry( value ):
                employee = self.getStaffListAttribute( value, 'employee' )
                deputy = self.getStaffListAttribute( value, 'deputy' )
                r.extend( [ employee, deputy ] )
            elif value.startswith('pos:'):
                try:
                    r.extend( self.resolvePosition( value[4:], plain_users=True ) )
                except LookupError:
                    pass
            elif value.startswith('div:'):
                try:
                    r.extend( self.resolveDivision( value[4:], plain_users=True ) )
                except LookupError:
                    pass
            elif value.startswith('group:'):
                r.extend( self.getGroup( value[6:] ).getUsers() )
            elif value.startswith('role:'):
                role_manager = DFRoleManager( context is Missing and self or context, context )
                r.extend( role_manager.getUsersByRole( value[5:] ) )
            else:
                r.append( value )

        r = filter( None, r )
        r = uniqueValues( r )
        if filter_locked:
            return [ u for u in r if not self.isUserLocked( u )  ]
        return r

    def getStaffListAttribute( self, entry, attribute, forced=0 ):
        if not isDirectoryEntry( entry ):
            staff_list = self.getStaffList()
            if not staff_list:
                return
            try:
                v = staff_list.getEntry( entry )
            except LookupError:
                return
                v = None
#            if not v:
#                raise KeyError, entry
        else:
            v = entry

        v = v.getEntryAttribute( attribute )
        if v and isDirectoryEntry( v ):
            if attribute in [ 'employee', 'deputy' ] and not forced:
                v = v.getEntryAttribute( 'associate_user' )
            else:
                v = v.Title()
        return v
  
## </TODO>

InitializeClass( MembershipTool )


class OrphanedUser( BasicUser ):
    """
        A user object for users deleted from the underlying
        user folder.
    """

    security = ClassSecurityInfo()

    def __init__( self, name, password=None, roles=(), domains=() ):
        self.name = name
        self.roles = tuple(roles)

    def getUserName( self ):
        return self.name

    def _getPassword( self ):
        return ''

    def getRoles( self ):
        return self.roles

    def getDomains( self ):
        return ()

    def authenticate( self, password, request ):
        return False

InitializeClass( OrphanedUser )

class GroupResource:

    def identify( portal, object ):
        return { 'uid' : object.getId() }

    def lookup( portal, uid=None, **kwargs ):
        members = getToolByName( portal, 'portal_membership' )
        object = members.getGroup( uid )
        if object is None:
            raise Exceptions.LocatorError( 'group', uid )
        return object

# TODO: develop role object
# currently role resource is identified from uid string like 'role:VersionOwner::'
class RoleResource:

##    def identify( portal, object ):
##        return { 'uid' : object.getId() }

    def lookup(portal, uid, **kwargs):
        return uid

class PositionResource:

    def identify( portal, object ):
        return { 'uid' : object.getId() }

    def lookup( portal, uid=None, **kwargs ):
        members = getToolByName( portal, 'portal_membership' )
        staff_list = members.getStaffList()
        if staff_list is None:
            raise Exceptions.LocatorError( 'position', uid )
        
        pos_object = staff_list.getEntry( uid )
        if pos_object is None:
            raise Exceptions.LocatorError( 'position', uid )
        return pos_object

class DivisionResource( PositionResource ):
    pass

class MembershipInstaller:
    after = True
    name = 'setupMembership'

    def install(self, portal, check=False):
        msgcat = getToolByName( portal, 'msg' )
        lang = msgcat.get_default_language()

        count = 0
        membership = getToolByName( portal, 'portal_membership' )
        for item in Config.DefaultGroups:
            if membership.getGroup( item['id'], None ) is None:
                count += 1
                if check:
                    continue
                membership._addGroup( item['id'], msgcat.gettext( item['title'], lang=lang ) )
        return count
  
    __call__ = install

def isDirectoryEntry( value ):
    return hasattr( value, 'implements' ) and value.implements( IDirectoryEntry )

def initialize( context ):
    # module initialization callback

    context.registerResource( 'group', GroupResource, moniker='group' )
    context.registerResource( 'role', RoleResource )
    context.registerResource( 'position', PositionResource, moniker='position' )
    context.registerResource( 'division', DivisionResource, moniker='division' )

    context.registerTool( MembershipTool )

    context.registerInstaller( MembershipInstaller )
