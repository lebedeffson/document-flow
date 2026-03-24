## Script (Python) "register"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=password='password', confirm='confirm', domains=None, storage=None, groups=None
##title=Register a user
##
# $Editor: vpastukhov $
# $Id: register.py,v 1.24 2006/01/16 11:20:22 vsafronovich Exp $
# $Revision: 1.24 $
from Products.CMFNauTools.SecureImports import cookId

REQUEST = context.REQUEST
username = REQUEST['username']

portal = context.portal_url.getPortalObject()
members = portal.getProperty( 'members_folder', None )

if not REQUEST.get('noHome'):
    if members is None:
        return context.join_form( context, REQUEST, error="Members folder does not exist." )
    if username in members.objectIds():
        return context.join_form( context, REQUEST, error="The new user's home folder already exists." )
    if username != cookId(members, id=username):
        return context.join_form( context, REQUEST, error="This identifier is reserved." )

portal_registration = context.portal_registration
portal_properties   = context.portal_properties

if not portal_properties.validate_email:
    failMessage = portal_registration.testPasswordValidity( password, confirm )
    if failMessage:
        REQUEST.set( 'error', failMessage )
        return context.join_form( context, REQUEST, error=failMessage )

failMessage = portal_registration.testPropertiesValidity( REQUEST )
if failMessage:
    REQUEST.set( 'error', failMessage )
    return context.join_form( context, REQUEST, error=failMessage )

password = REQUEST.get('password') or portal_registration.generatePassword()

roles = [ 'Member' ]
if REQUEST.get('asManager'):
    roles.append( 'Manager' )

domains = domains or None

groups = groups or []
if storage:
    groups.append( storage )

portal_membership   = context.portal_membership

# member = portal_registration.addMember( username, password, roles, domains, groups=groups, properties=REQUEST )
# XXX remove this when registration tool supports groups argument
member = portal_registration.addMember( username, password, roles, domains, properties=REQUEST )
for group in groups:
    group_users = list( portal_membership.getGroup(group).getUsers() )
    group_users.append( username )
    portal_membership.manage_changeGroup( group, group_users )

send_password = REQUEST.get('mail_me')
if member.getProperty('email') and (portal_properties.validate_email or send_password):
    try:
        portal_registration.registeredNotify( username )
    except:
        REQUEST.set('not_sended','1')

portal_membership.setDefaultFilters( username )

if not REQUEST.get('noHome'):
    username = member.getUserName()
    home     = member.getHomeFolder( create=1 )
    if REQUEST['home']:
        home.setTitle(REQUEST['home'])
    defaults = portal.getProperty( 'defaults_folder', None )

    if not (REQUEST.get('noDefaults') or defaults is None):
        ids = defaults.objectIds()
        if ids:
            data = defaults.manage_copyObjects( ids )
            home.manage_pasteObjects( data )
            home.changeOwnership( username, recursive=1 )

if REQUEST.get('active'):
   context.portal_licensing.addActiveUsers( username )

if REQUEST.get('source_user'):
    portal_membership.copyAccessRights(REQUEST['source_user'], username)

return context.registered( context, REQUEST )
