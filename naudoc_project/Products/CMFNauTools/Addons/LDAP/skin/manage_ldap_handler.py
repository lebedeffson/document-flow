## Script (Python) "manage_ldap_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=Handler of the LDAP configuration form.
##
# $Editor: vpastukhov $
# $Id: manage_ldap_handler.py,v 1.1 2008/12/05 11:26:19 oevsegneev Exp $
# $Revision: 1.1 $

from Products.CMFNauTools.SecureImports import SimpleRecord

tool = context.portal_membership
record = SimpleRecord( REQUEST.form )

if REQUEST.has_key('save_settings'):
    tool.setAuthSettings( 'ldap', record )

    if REQUEST.has_key('ldap_users'):
        tool.setUsersSource( REQUEST.get('ldap_users') and 'ldap' or None )

    if REQUEST.has_key('ldap_groups'):
        tool.setGroupsSource( REQUEST.get('ldap_groups') and 'ldap' or None )

    msg = "LDAP settings have been saved."

elif REQUEST.has_key('save_schema'):
    tool.setPropertiesMapping( 'ldap', record.schema_map )
    msg = "LDAP schema has been saved."

elif REQUEST.has_key('add_attribute'):
    attr_def = record.attribute.copy() # ** below needs a dict
    attr_id  = attr_def['id'].strip()
    del attr_def['id']

    tool.changePropertyMapping( 'ldap', attr_id, **attr_def )
    msg = "LDAP attribute has been added."

elif REQUEST.has_key('refresh'):
    tool.refreshUserRecords()
    msg = "User records have been refreshed."

return tool.redirect( action='manageLDAP', message=msg, REQUEST=REQUEST )
