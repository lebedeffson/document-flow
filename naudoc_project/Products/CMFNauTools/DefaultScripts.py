"""
Script objects created by default in the new portals.

$Editor: oevsegneev $
$Id: DefaultScripts.py,v 1.13 2008/06/04 12:33:44 oevsegneev Exp $
"""
__version__ = '$Revision: 1.13 $'[11:-2]


Scripts = {
    'archive_detachable_document' :
    { 'id'    : 'archive_detachable_document'
    , 'title' : "Archive detachable document"
    , 'data'  :
"""
# This script is a part of the normative document replacement functionality
# implementation. It is intended to be executed on the "effective"
# transition of the "Normative Document" category workflow.

old = object.getCategoryAttribute( attr = "DetachItDoc" )
if old is not None:
    old.setCategoryAttribute( attr = "ItDetachDoc", value = object )
    portal.portal_workflow.doActionFor( old, "archive" )
"""
    , 'namespace_factory' : 'action_script_namespace'
    , '_allowed_types'    : ['HTMLDocument']
    },
    'get_object_creator' :
    { 'id'    : 'get_object_creator'
    , 'title' : "Get Object Creator"
    , 'data'  :
"""
# for NormativeDocument ResponsAuthor ( obsolete now )
return object.Creator()
"""
    , 'namespace_factory' : 'category_attribute'
    , 'result_type' : 'userlist'
    , '_allowed_types'    : []# ['HTMLDocument'],
    },
    'deliver_outgoing_mail' :
    { 'id'    : 'deliver_outgoing_mail'
    , 'title' : "Dispatch mail message"
    , 'data'  :
"""
# This script delivers mail documents from the outgoing mail folders.
# Executed on the "Dispatch message" transition of the "Outgoing Mail" category.

folder = object.parent( 'isOutgoingMailFolder' )
if folder is not None:
    folder.sendMail( uids=[ object.getUid() ] )
"""
    , 'namespace_factory' : 'action_script_namespace'
    , '_allowed_types'    : ['HTMLDocument']
    },
}
