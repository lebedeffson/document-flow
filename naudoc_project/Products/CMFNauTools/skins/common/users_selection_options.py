## Script (Python) "users_selection_options"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=options
##title=Returns lists of options
##

members = context.portal_membership

if options is None:
    roles  = [('role:%s' % role, role)
              for role in ['VersionOwner', 'Owner', 'Reader', 'Writer',
                           'Editor']]
    groups = [('group:%s' % group.getId(), group.Title())
              for group in members.listGroups()]
    users = members.listMemberIds()

else:
    roles  = []
    groups = []
    users  = []

    for option in options:
        if option.startswith('role:'):
            roles.append( (option, option[5:]) )
        elif option.startswith('group:'):
            groups.append( (option, members.getGroup(option[6:]).Title()) )
        else:
            users.append(option)

return (roles, groups, users)