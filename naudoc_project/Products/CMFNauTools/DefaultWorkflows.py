""" Default document workflows
$Id: DefaultWorkflows.py,v 1.75 2008/10/15 12:26:54 oevsegneev Exp $
"""
__version__ = '$Revision: 1.75 $'[11:-2]

from zLOG import LOG, DEBUG, TRACE, INFO

from AccessControl import Permissions as ZopePermissions
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Config
from Config import Permissions, Restrictions
from SimpleObjects import ExpressionWrapper


p_access        = CMFCorePermissions.AccessContentsInformation
p_list          = CMFCorePermissions.ListFolderContents
p_modify        = CMFCorePermissions.ModifyPortalContent
p_view          = CMFCorePermissions.View
p_manage        = CMFCorePermissions.ManagePortal
p_properties    = CMFCorePermissions.ManageProperties
p_addcontent    = CMFCorePermissions.AddPortalContent
p_addfolders    = CMFCorePermissions.AddPortalFolders
p_changeperms   = CMFCorePermissions.ChangePermissions
p_request       = CMFCorePermissions.RequestReview
p_reply         = CMFCorePermissions.ReplyToItem

p_modify_attr   = Permissions.ModifyAttributes
p_view_attr     = Permissions.ViewAttributes

p_delete        = ZopePermissions.delete_objects
p_ownership     = ZopePermissions.take_ownership

p_employ        = Permissions.EmployPortalContent
p_publish       = Permissions.PublishPortalContent
p_archive       = Permissions.ArchivePortalContent

p_mailhost      = Permissions.UseMailHostServices
p_mailserv      = Permissions.UseMailServerServices

p_lock          = Permissions.WebDAVLockItems
p_unlock        = Permissions.WebDAVUnlockItems

p_versions      = Permissions.CreateObjectVersions
p_makeprincipal = Permissions.MakeVersionPrincipal

p_noaccess      = Restrictions.NoAccess
p_nomodification= Restrictions.NoModificationRights

r_member        = Config.MemberRole
r_manager       = Config.ManagerRole
r_visitor       = Config.VisitorRole

r_owner         = Config.OwnerRole
r_editor        = Config.EditorRole
r_reader        = Config.ReaderRole
r_writer        = Config.WriterRole
r_author        = Config.AuthorRole
r_version_owner = Config.VersionOwnerRole


def actbox_url( transition_id ):
    return '%(content_url)s/change_state?transition=' + transition_id

msg=lambda s:s

def setupFolderWorkflow(wf, category, portal_metadata, msg=msg):
    """
      Setup the default NauSite folders workflow
    """
    wf.setProperties(title='NauSite folder workflow')

    for s in ('editable', 'frozen', 'fixed'):
        wf.states.addState(s)

    for t in ('edit', 'freeze', 'fix'):
        wf.transitions.addTransition(t)

    for p in (p_addcontent, p_addfolders, p_changeperms, p_delete, p_modify, \
              p_nomodification, p_view_attr, p_modify_attr):
        wf.addManagedPermission(p)

    #
    # Setup states
    wf.states.setInitialState('editable')

    sdef = wf.states['editable']
    sdef.setProperties(
        title=msg('Editable'),
        transitions=('fix', 'freeze'))
    sdef.setPermission(p_addcontent, 1, ())
    sdef.setPermission(p_addfolders, 1, ())
    sdef.setPermission(p_changeperms, 1, ())
    sdef.setPermission(p_delete, 1, ())
    sdef.setPermission(p_modify, 1, ())
    sdef.setPermission(p_view_attr, 0, (r_editor, r_manager, r_writer))
    sdef.setPermission(p_modify_attr, 0, (r_editor, r_manager, r_writer))

    sdef = wf.states['frozen']
    sdef.setProperties(
        title=msg('Frozen'),
        transitions=('edit', 'fix'))
    sdef.setPermission(p_addcontent, 0, ())
    sdef.setPermission(p_addfolders, 0, ())
    sdef.setPermission(p_changeperms, 1, ())
    sdef.setPermission(p_delete, 0, ())
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_nomodification, 1, (r_member, r_manager, r_owner, r_version_owner, r_editor, r_writer))
    sdef.setPermission(p_view_attr, 0, (r_editor, r_manager, r_writer))
    sdef.setPermission(p_modify_attr, 0, ())


    sdef = wf.states['fixed']
    sdef.setProperties(
        title=msg('Fixed'),
        transitions=('edit',))
    sdef.setPermission(p_addcontent, 0, ())
    sdef.setPermission(p_addfolders, 0, ())
    sdef.setPermission(p_changeperms, 0, (r_manager,))
    sdef.setPermission(p_delete, 0, ())
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_nomodification, 1, (r_member, r_manager, r_owner, r_version_owner, r_editor, r_writer))
    sdef.setPermission(p_view_attr, 0, (r_editor, r_manager, r_writer))
    sdef.setPermission(p_modify_attr, 0, ())

    #
    # Set transitions
    tdef = wf.transitions['edit']
    tdef.setProperties(
        title=msg('Edit folder'),
        new_state_id='editable',
        actbox_name=msg('Edit'),
        actbox_url=actbox_url( tdef.getId() ),
        props={ 'guard_permissions':p_changeperms }
       )

    tdef = wf.transitions['freeze']
    tdef.setProperties(
        title=msg('Freeze the folder'),
        new_state_id='frozen',
        actbox_name=msg('Freeze'),
        actbox_url=actbox_url( tdef.getId() ),
        props={ 'guard_permissions':p_changeperms }
       )

    tdef = wf.transitions['fix']
    tdef.setProperties(
        title=msg('Fix the folder'),
        new_state_id='fixed',
        actbox_name=msg('Fix'),
        actbox_url=actbox_url( tdef.getId() ),
        props={ 'guard_permissions':p_changeperms }
       )

    setupWorkflowVars(wf)

def setupSimpleDocumentWorkflow(wf, category, portal_metadata, msg=msg):
    """
      Setup the NauSite documents workflow
    """
    wf.setProperties(title='NauSite document workflow')

    for s in ('private', 'evolutive', 'group', 'fixed', 'archive'):
        wf.states.addState(s)

    for t in ('retract', 'evolve', 'open_for_group', 'fix', 'archive', 'modify'):
        wf.transitions.addTransition(t)

    for p in Config.ManagedPermissions:
        wf.addManagedPermission(p)

    ### setup variables ###

    setupWorkflowVars(wf)

    #
    # Setup states
    wf.states.setInitialState('evolutive')

    sdef = wf.states['private']
    sdef.setProperties(
        title=msg('Private'),
        transitions=('evolve', 'fix', 'open_for_group', 'archive'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_list, 1, ())
    sdef.setPermission(p_modify, 0, (r_manager, r_owner))
    sdef.setPermission(p_view, 0, (r_manager, r_owner))


    sdef = wf.states['evolutive']
    sdef.setProperties(
        title=msg('Evolutive'),
        transitions=('evolve', 'retract', 'fix', 'open_for_group', 'archive'))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_makeprincipal, 1, (r_manager, r_owner, r_editor) )
    sdef.setPermission(p_modify, 0, (r_manager, r_owner))

    sdef = wf.states['group']
    sdef.setProperties(
        title=msg('Open for group'),
        transitions=('retract', 'evolve', 'fix', 'archive', 'modify'))
    sdef.setPermission(p_modify, 0, (r_manager, r_owner))
    sdef.setPermission(p_lock, 1, (r_writer,))
    sdef.setPermission(p_unlock, 1, (r_writer,))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))

    sdef = wf.states['fixed']
    sdef.setProperties(
        title=msg('Fixed'),
        transitions=())
    sdef.setPermission(p_delete, 0, (r_manager,))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))

    sdef = wf.states['archive']
    sdef.setProperties(
        title=msg('Archive'),
        transitions=('retract', 'evolve', 'fix', 'open_for_group'))
    sdef.setPermission(p_delete, 0, (r_manager, r_editor))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_reply, 0, ())
    sdef.setPermission(p_ownership, 0, ())
    sdef.setPermission(p_properties, 0, ())
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))

    #
    # Set transitions

    tdef = wf.transitions['retract']
    tdef.setProperties(
        title=msg('Hide document'),
        new_state_id='private',
        actbox_name=msg('Retract'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
               'guard_roles': r_owner,
              }
       )

    tdef = wf.transitions['evolve']
    tdef.setProperties(
        title=msg('Evolve document'),
        new_state_id='evolutive',
        actbox_name=msg('Evolve'),
#        after_script_name='allow_version_edit',
        actbox_url=actbox_url( tdef.getId() ),
        props={
               'guard_roles' : r_owner,
              }
       )


    tdef = wf.transitions['open_for_group']
    tdef.setProperties(
        title=msg('Open the document for group editing'),
        new_state_id='group',
        actbox_name=msg('Open for group'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
               'guard_roles': r_owner,
              }
       )

    tdef = wf.transitions['fix']
    tdef.setProperties(
        title=msg('Fix the document'),
        new_state_id='fixed',
        actbox_name=msg('Fix'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
               'guard_roles': r_owner,
              }
       )

    tdef = wf.transitions['archive']
    tdef.setProperties(
        title=msg('Archive document'),
        new_state_id='archive',
        actbox_name=msg('Archive'),
#        script_name='fix',
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_archive,
              }
       )

    tdef = wf.transitions['modify']
    tdef.setProperties(
        title=msg('Modify document'),
        new_state_id=None,
        actbox_name=msg('Modify')
       )

def setupDocumentWorkflow(wf, category, portal_metadata, msg=msg):
    """
      Setup the NauSite documents workflow
    """
    wf.setProperties(title='NauSite document workflow')

    for s in ('private', 'evolutive', 'group', 'fixed', 'archive'):
        wf.states.addState(s)

    for t in ('retract', 'evolve', 'open_for_group', 'fix', 'archive', 'activate', 'modify'):
        wf.transitions.addTransition(t)
#    for s in ('fix', 'activate', 'allow_version_edit'):
#       wf.scripts._setOb( s, ExpressionWrapper( s, factory='dc_workflow', use_dict=1 ) )

    ### setup variables ###

    setupWorkflowVars(wf)

    #
    # Setup states
    wf.states.setInitialState('evolutive')

    sdef = wf.states['private']
    sdef.setProperties(
        title=msg('Private'),
        transitions=('evolve', 'fix', 'open_for_group', 'archive'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_list, 1, ())
    sdef.setPermission(p_modify, 0, (r_manager, r_version_owner))
    sdef.setPermission(p_view, 0, (r_manager, r_owner))
    sdef.setPermission(p_versions, 0, (r_manager, r_owner))
    sdef.setPermission(p_makeprincipal, 1, () )


    sdef = wf.states['evolutive']
    sdef.setProperties(
        title=msg('Evolutive'),
        transitions=('evolve', 'retract', 'fix', 'open_for_group', 'archive', 'activate'))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_versions, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_makeprincipal, 1, (r_manager, r_owner, r_editor) )
    sdef.setPermission(p_modify, 0, (r_manager, r_version_owner))

    sdef = wf.states['group']
    sdef.setProperties(
        title=msg('Open for group'),
        transitions=('retract', 'evolve', 'fix', 'archive', 'modify'))
#    sdef.setPermission(p_modify, 1, (r_writer,))
    sdef.setPermission(p_modify, 0, (r_version_owner,))
    sdef.setPermission(p_lock, 1, (r_writer,))
    sdef.setPermission(p_unlock, 1, (r_writer,))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_versions, 0, (r_manager, r_owner, r_editor, r_writer))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_makeprincipal, 1, (r_writer, r_editor))

    sdef = wf.states['fixed']
    sdef.setProperties(
        title=msg('Fixed'),
        transitions=())
    sdef.setPermission(p_delete, 0, (r_manager,))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    # fix only one version, but it is possible to create new ones:
    sdef.setPermission(p_versions, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_makeprincipal, 0, () )

    sdef = wf.states['archive']
    sdef.setProperties(
        title=msg('Archive'),
        transitions=('retract', 'evolve', 'fix', 'open_for_group'))
    sdef.setPermission(p_delete, 0, (r_manager, r_editor))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_reply, 0, ())
    sdef.setPermission(p_ownership, 0, ())
    sdef.setPermission(p_properties, 0, ())
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_versions, 0, (r_manager, r_owner))
    sdef.setPermission(p_makeprincipal, 0, () )

    #
    # Set transitions

    tdef = wf.transitions['retract']
    tdef.setProperties(
        title=msg('Hide document'),
        new_state_id='private',
        actbox_name=msg('Retract'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
               'guard_roles': r_owner + ';' + r_manager,
              }
       )

    tdef = wf.transitions['evolve']
    tdef.setProperties(
        title=msg('Evolve document'),
        new_state_id='evolutive',
        actbox_name=msg('Evolve'),
#        after_script_name='allow_version_edit',
        actbox_url=actbox_url( tdef.getId() ),
        props={
               'guard_roles' : r_owner + ';' + r_manager + ';' + r_editor,
              }
       )


    tdef = wf.transitions['open_for_group']
    tdef.setProperties(
        title=msg('Open the document for group editing'),
        new_state_id='group',
        actbox_name=msg('Open for group'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
               'guard_roles': r_owner + ';' + r_manager + ';' + r_editor,
              }
       )

    tdef = wf.transitions['fix']
    tdef.setProperties(
        title=msg('Fix the document'),
        new_state_id='fixed',
        actbox_name=msg('Fix'),
#        script_name='fix',
        actbox_url=actbox_url( tdef.getId() ),
        props={
               'guard_roles': r_owner + ';' + r_manager,
              }
       )

    tdef = wf.transitions['archive']
    tdef.setProperties(
        title=msg('Archive document'),
        new_state_id='archive',
        actbox_name=msg('Archive'),
#        script_name='fix',
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_archive,
              }
       )

    tdef = wf.transitions['activate']
    tdef.setProperties(
        title=msg('Make current version principal'),
        new_state_id='',
        actbox_name=msg('Make the version principal'),
        actbox_url=actbox_url( tdef.getId() ),
#       script_name='activate',
        props={'guard_permissions': p_makeprincipal,
               'guard_expr':"python: (here.implements('isVersionable') or here.implements('isVersion')) and not here.isCurrentVersionPrincipal()"
              }
        )

    tdef.addVariable( 'principal_version', "python: (here.implements('isVersionable') or here.implements('isVersion')) and here.getPrincipalVersionId()" )

    # TRIGGER_WORKFLOW_METHOD (on 'edit')
    tdef = wf.transitions['modify']
    tdef.setProperties(
        title=msg('Modify'),
        new_state_id='',
        actbox_name=msg('Modify'),
        actbox_url=actbox_url( tdef.getId() ),
        trigger_type=2 # TRIGGER_WORKFLOW_METHOD
        )



    # action template make version principal
    assignActionTemplateToTransition(
        portal_metadata=portal_metadata,
        category_id=category,
        action_template_id=createActionTemplate_MakeVersionPrincipal( portal_metadata, category ),
        transition='activate'
    )

    # to state 'group', set that only one version can exists in this state
    # and exclude old version by 'evolve' transition
    portal_metadata.getCategoryById( category ).manageAllowSingleStateForVersionArray( action='add', state='group', transition_for_exclude='evolve' )

#    sdef = wf.scripts['fix']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.denyVersionEdit()" )

#    sdef = wf.scripts['activate']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.activateCurrentVersion()" )

#    sdef = wf.scripts['allow_version_edit']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.allowVersionEdit()" )

def setupSimplePublicationWorkflow(wf, category, portal_metadata, msg=msg):
    """
      Setup the NauSite publications workflow
    """
    wf.setProperties(title='NauSite publication workflow')

    for s in ( 'evolutive', 'awaiting', 'published' ):
        wf.states.addState(s)

    for t in ( 'evolve', 'request', 'reject', 'publish', 'unpublish' ):
        wf.transitions.addTransition(t)

    for s in ('publication_request',  'publish', 'unpublish' ): # , 'activate' , 'allow_version_edit', 'deny_version_edit' ):
        wf.scripts._setOb( s, ExpressionWrapper( s, factory='dc_workflow', use_dict=1 ) )

    for p in (p_access, p_list, p_modify, p_reply, p_view):
        wf.addManagedPermission(p)

    ### setup variables ###

    setupWorkflowVars( wf )

    wf.variables.addVariable( 'published' )
    vdef = wf.variables['published']
    vdef.setProperties( description='Published on the external site', for_status=1 )

    ### setup states ###

    wf.states.setInitialState( 'evolutive' )

    sdef = wf.states['evolutive']
    sdef.setProperties(
        title=msg('Evolutive'),
        transitions=( 'request', 'publish', 'unpublish' ))
    sdef.setPermission(p_access, 1, ())
    sdef.setPermission(p_list, 1, ())
    sdef.setPermission(p_modify, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))

    sdef = wf.states['awaiting']
    sdef.setProperties(
        title=msg('Awaiting publication'),
        transitions=( 'evolve', 'reject', 'publish' ))
    sdef.setPermission(p_access, 1, ())
    sdef.setPermission(p_list, 1, ())
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))

    sdef = wf.states['published']
    sdef.setProperties(
        title=msg('Published'),
        transitions=( 'evolve', 'unpublish' ))
    sdef.setPermission(p_access, 1, (r_visitor,))
    sdef.setPermission(p_list, 1, (r_visitor,))
    sdef.setPermission(p_modify, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_reply, 1, (r_visitor,))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer, r_visitor))


    ### setup transitions ###

    tdef = wf.transitions['evolve']
    tdef.setProperties(
        title=msg('Evolve document'),
        new_state_id='evolutive',
        actbox_name=msg('Evolve'),
#       after_script_name='allow_version_edit',
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_changeperms,
               'guard_expr':"python: not (state_change.old_state and state_change.old_state.getId() == 'awaiting' and user.has_permission('%s', here))" % p_publish
              }
        )

    tdef = wf.transitions['request']
    tdef.setProperties(
        title=msg('Request the document publication on the external site'),
        new_state_id='awaiting',
#       script_name='deny_version_edit',
        actbox_name=msg('Request publication'),
        actbox_url=actbox_url( tdef.getId() ),
        after_script_name='publication_request',
        props={'guard_permissions':p_request,
               'guard_expr':"python: not user.has_permission('%s', here)" % p_publish
              }
        )

    tdef = wf.transitions['reject']
    tdef.setProperties(
        title=msg('Reject the document publication on the external site'),
        new_state_id='evolutive',
#       after_script_name='allow_version_edit',
        actbox_name=msg('Reject publication'),
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_publish,
              }
        )

    tdef = wf.transitions['publish']
    tdef.setProperties(
        title=msg('Publish the document on the external site'),
        new_state_id='published',
        actbox_name=msg('Publish'),
        actbox_url=actbox_url( tdef.getId() ),
        after_script_name='publish',
        props={'guard_permissions':p_publish,
              }
        )
    tdef.addVariable( 'published', 'string: 1' )

    tdef = wf.transitions['unpublish']
    tdef.setProperties(
        title=msg('Recall the document from the external site'),
        new_state_id='evolutive',
        actbox_name=msg('Unpublish'),
        actbox_url=actbox_url( tdef.getId() ),
        script_name='unpublish',
#       after_script_name='allow_version_edit',
        props={'guard_permissions':p_publish + ';' + p_request,
               'guard_expr':"python: status.get('published')"
              }
        )
    tdef.addVariable( 'published', 'nothing' )
    tdef.addVariable( 'principal_version', "python: (here.implements('isVersionable') or here.implements('isVersion')) and here.getPrincipalVersionId()" )

    ### setup scripts ###

    # synchronize the document with external site document
    sdef = wf.scripts['publish']
    sdef.setExpression( "python: object.implements('isSyncableContent') and kwargs.get('sync', 1) and object.updateRemoteCopy() or object.announce_publication(object)" )

    sdef = wf.scripts['publication_request']
    sdef.setExpression( "python: object.followup.createTask( title=\"%s '%s'\" % ( object.msg('Publication request for the document') \
                                                             , object.title_or_id() \
                                                             ) \
                                          , description=kwargs.get('comment', '') \
                                          , involved_users=object.editor() \
                                          , expiration_date=DateTime()+7.0 \
                                          , brains_type='publication_request' \
                                          )" )

    # delete remote copy of this document
    sdef = wf.scripts['unpublish']
    sdef.setExpression( "python: object.implements('isSyncableContent') and kwargs.get('sync', 1) and status.get('published') and object.deleteRemoteCopy()" )


    # action template make version principal
    assignActionTemplateToTransition(
        category_id=category,
        action_template_id=createActionTemplate_MakeVersionPrincipal( portal_metadata, category ),
        transition='activate',
        portal_metadata=portal_metadata
    )

#    sdef = wf.scripts['activate']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.activateCurrentVersion()" )

#    sdef = wf.scripts['deny_version_edit']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.denyVersionEdit()" )

#    sdef = wf.scripts['allow_version_edit']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.allowVersionEdit()" )

def setupPublicationWorkflow(wf, category, portal_metadata, msg=msg):
    """
      Setup the NauSite publications workflow
    """
    wf.setProperties(title='NauSite publication workflow')

    for s in ( 'evolutive', 'awaiting', 'published' ):
        wf.states.addState(s)

    for t in ( 'evolve', 'request', 'reject', 'publish', 'unpublish', 'activate' ):
        wf.transitions.addTransition(t)

    ### setup variables ###

    setupWorkflowVars( wf )

    wf.variables.addVariable( 'published' )
    vdef = wf.variables['published']
    vdef.setProperties( description='Published on the external site', for_status=1 )

    ### setup states ###

    wf.states.setInitialState( 'evolutive' )

    sdef = wf.states['evolutive']
    sdef.setProperties(
        title=msg('Evolutive'),
        transitions=( 'request', 'publish', 'unpublish', 'activate' ))
    sdef.setPermission(p_access, 1, ())
    sdef.setPermission(p_list, 1, ())
    sdef.setPermission(p_modify, 0, (r_manager, r_version_owner))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))

    sdef = wf.states['awaiting']
    sdef.setProperties(
        title=msg('Awaiting publication'),
        transitions=( 'evolve', 'reject', 'publish' ))
    sdef.setPermission(p_access, 1, ())
    sdef.setPermission(p_list, 1, ())
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))

    sdef = wf.states['published']
    sdef.setProperties(
        title=msg('Published'),
        transitions=( 'evolve', 'unpublish' ))
    sdef.setPermission(p_access, 1, (r_visitor,))
    sdef.setPermission(p_list, 1, (r_visitor,))
    sdef.setPermission(p_modify, 0, (r_manager, r_owner, r_editor, r_version_owner))
    sdef.setPermission(p_reply, 1, (r_visitor,))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer, r_visitor))


    ### setup transitions ###

    tdef = wf.transitions['evolve']
    tdef.setProperties(
        title=msg('Evolve document'),
        new_state_id='evolutive',
        actbox_name=msg('Evolve'),
#       after_script_name='allow_version_edit',
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_changeperms,
               'guard_expr':"python: not (state_change.old_state and state_change.old_state.getId() == 'awaiting' and user.has_permission('%s', here))" % p_publish
              }
        )

    tdef = wf.transitions['request']
    tdef.setProperties(
        title=msg('Request the document publication on the external site'),
        new_state_id='awaiting',
#       script_name='deny_version_edit',
        actbox_name=msg('Request publication'),
        actbox_url=actbox_url( tdef.getId() ),
        after_script_name='publication_request',
        props={'guard_permissions':p_request,
               'guard_expr':"python: not user.has_permission('%s', here)" % p_publish
              }
        )

    tdef = wf.transitions['reject']
    tdef.setProperties(
        title=msg('Reject the document publication on the external site'),
        new_state_id='evolutive',
#       after_script_name='allow_version_edit',
        actbox_name=msg('Reject publication'),
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_publish,
              }
        )

    tdef = wf.transitions['publish']
    tdef.setProperties(
        title=msg('Publish the document on the external site'),
        new_state_id='published',
        actbox_name=msg('Publish'),
        actbox_url=actbox_url( tdef.getId() ),
        after_script_name='publish',
        props={'guard_permissions':p_publish,
              }
        )
    tdef.addVariable( 'published', 'string: 1' )

    tdef = wf.transitions['unpublish']
    tdef.setProperties(
        title=msg('Recall the document from the external site'),
        new_state_id='evolutive',
        actbox_name=msg('Unpublish'),
        actbox_url=actbox_url( tdef.getId() ),
        script_name='unpublish',
#       after_script_name='allow_version_edit',
        props={'guard_permissions':p_publish + ';' + p_request,
               'guard_expr':"python: status.get('published')"
              }
        )
    tdef.addVariable( 'published', 'nothing' )

    tdef = wf.transitions['activate']
    tdef.setProperties(
        title=msg('Make current version principal'),
        new_state_id='',
        actbox_name=msg('Make the version principal'),
        actbox_url=actbox_url( tdef.getId() ),
#       script_name='activate',
        props={'guard_permissions': p_makeprincipal,
               'guard_expr':"python: (here.implements('isVersionable') or here.implements('isVersion')) and not here.isCurrentVersionPrincipal()"
              }
        )
    tdef.addVariable( 'principal_version', "python: (here.implements('isVersionable') or here.implements('isVersion')) and here.getPrincipalVersionId()" )

    # Inherit scripts from SimplePublication workflow.


    #avoid duplicate creation of the same template
    principal_template_id = createActionTemplate_MakeVersionPrincipal( portal_metadata, category )

    # action template make version principal
    assignActionTemplateToTransition(
        category_id=category,
        action_template_id=principal_template_id,
        transition='activate',
        portal_metadata=portal_metadata
    )

    #when publishing any version, make it principal (to avoid bugs on external site)
    assignActionTemplateToTransition(
        category_id=category,
        action_template_id=principal_template_id,
        transition='publish',
        portal_metadata=portal_metadata
    )

    # to state 'published', set that only one version can exists in this state
    # and exclude old version by 'unpublish' transition
    portal_metadata.getCategoryById( category ).manageAllowSingleStateForVersionArray( action='add', state='published', transition_for_exclude='unpublish' )

def setupDirectiveWorkflow( wf, category, portal_metadata, msg=msg ):
    """ Setup directive document workflow
    """
    wf.setProperties( title='Directive document workflow' )

    for s in ( 'evolutive', 'effective', 'archive' ):
        wf.states.addState(s)

    for t in ( 'evolve', 'apply', 'revoke', 'archive', 'activate' ):
        wf.transitions.addTransition(t)

#    for s in ('activate', 'deny_version_edit', 'allow_version_edit'):
#       wf.scripts._setOb( s, ExpressionWrapper( s, factory='dc_workflow', use_dict=1 ) )

    for p in ( p_view, p_delete, p_modify, p_properties, p_reply, p_ownership, p_versions, p_makeprincipal ):
        wf.addManagedPermission(p)

    ### setup variables ###

    setupWorkflowVars(wf)

    ### setup states ###

    wf.states.setInitialState('evolutive')

    sdef = wf.states['evolutive']
    sdef.setProperties(
        title=msg('Evolutive'),
        transitions=( 'evolve', 'apply', 'archive', 'activate' ))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_versions, 0, (r_manager, r_owner, r_editor, r_writer))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_makeprincipal, 1, (r_manager, r_owner))
    sdef.setPermission(p_modify, 0, (r_manager, r_version_owner))


    sdef = wf.states['effective']
    sdef.setProperties(
        title=msg('Effective'),
        transitions=( 'evolve', 'revoke', 'archive' ))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_delete, 0, ())
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_versions, 0, (r_manager, r_owner, r_editor, r_writer))
    sdef.setPermission(p_makeprincipal, 1, (r_manager, r_owner))

    sdef = wf.states['archive']
    sdef.setProperties(
        title=msg('Archive'),
        transitions=( 'evolve', ))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_delete, 0, (r_manager, r_editor))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_properties, 0, ())
    sdef.setPermission(p_reply, 0, ())
    sdef.setPermission(p_ownership, 0, ())
    sdef.setPermission(p_versions, 0, (r_manager, r_owner))
    sdef.setPermission(p_makeprincipal, 0, ())

    ### setup transitions ###

    tdef = wf.transitions['evolve']
    tdef.setProperties(
        title=msg('Evolve document'),
        new_state_id='evolutive',
        actbox_name=msg('Evolve'),
#       after_script_name='allow_version_edit',
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_modify + ';' + p_archive + ';' + p_employ,
              }
        )

    tdef = wf.transitions['apply']
    tdef.setProperties(
        title=msg('Give effect to the document'),
        new_state_id='effective',
        actbox_name=msg('Apply'),
#       script_name='deny_version_edit',
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_employ,
              }
        )

    tdef = wf.transitions['revoke']
    tdef.setProperties(
        title=msg('Revoke the document'),
        new_state_id='evolutive',
        actbox_name=msg('Revoke'),
#       after_script_name='allow_version_edit',
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_employ,
              }
        )

    tdef = wf.transitions['archive']
    tdef.setProperties(
        title=msg('Archive document'),
        new_state_id='archive',
        actbox_name=msg('Archive'),
#       script_name='deny_version_edit',
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions':p_archive,
              }
        )

    tdef = wf.transitions['activate']
    tdef.setProperties(
        title=msg('Make current version principal'),
        new_state_id='',
        actbox_name=msg('Make the version principal'),
        actbox_url=actbox_url( tdef.getId() ),
#       script_name='activate',
        props={'guard_permissions': p_makeprincipal,
               'guard_expr':"python: (here.implements('isVersionable') or here.implements('isVersion')) and not here.isCurrentVersionPrincipal()"
              }
        )
    tdef.addVariable( 'principal_version', "python: (here.implements('isVersionable') or here.implements('isVersion')) and here.getPrincipalVersionId()" )

    # action template make version principal
    assignActionTemplateToTransition(
        category_id=category,
        action_template_id=createActionTemplate_MakeVersionPrincipal( portal_metadata, category ),
        transition='activate',
        portal_metadata=portal_metadata
    )

#    sdef = wf.scripts['activate']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.activateCurrentVersion()" )

#    sdef = wf.scripts['deny_version_edit']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.denyVersionEdit()" )

#    sdef = wf.scripts['allow_version_edit']
#    sdef.setExpression( "python: object.implements('isVersionable') and object.allowVersionEdit()" )


def setupIncomingMailWorkflow( wf, category, portal_metadata, msg=msg ):
    """ Setup workflow for mail messages
    """
    wf.setProperties( title='Incoming mail workflow' )

    for s in ( 'evolutive', 'received' ):
        wf.states.addState(s)

    for t in ( 'receive', ):
        wf.transitions.addTransition(t)

    for p in ( p_view, p_versions, p_modify, p_view_attr, p_modify_attr ):
        wf.addManagedPermission(p)

    ### setup variables ###

    setupWorkflowVars( wf )

    ### setup states ###

    wf.states.setInitialState('evolutive')

    sdef = wf.states['evolutive']
    sdef.setProperties(
            title=msg('Evolutive'),
            transitions=('receive',),
        )
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_versions, 0, (r_manager, r_owner, r_editor, r_writer))
    sdef.setPermission(p_modify, 0, (r_manager, r_version_owner))
    sdef.setPermission(p_view_attr, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_modify_attr, 0, (r_manager, r_version_owner))

    sdef = wf.states['received']
    sdef.setProperties(
            title=msg('Message is received'),
            transitions=(),
        )
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_versions, 0, ())
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_view_attr, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_modify_attr, 0, ())

    ### setup transitions ###

    tdef = wf.transitions['receive']
    tdef.setProperties(
            title=msg("Receive message"),
            new_state_id='received',
            props={'guard_permissions':p_mailserv}
        )


def setupOutgoingMailWorkflow( wf, category, portal_metadata, msg=msg ):
    """ Setup workflow for mail messages
    """
    wf.setProperties( title='Outgoing mail workflow' )

    for s in ( 'evolutive', 'pending', 'queued', 'sending', 'failed', 'sent' ):
        wf.states.addState(s)

    for t in ( 'evolve', 'enqueue', 'dequeue', 'refuse', 'dispatch', 'deliver', 'fail', 'fix', 'activate' ):
        wf.transitions.addTransition(t)

    for l in ( 'mailman_queue', ):
        wf.worklists.addWorklist(l)

    for p in ( p_delete, p_modify, p_versions, p_view_attr, p_modify_attr ):
        wf.addManagedPermission(p)

    ### setup variables ###

    setupWorkflowVars( wf )

    ### setup states ###

    wf.states.setInitialState('evolutive')

    sdef = wf.states['evolutive']
    sdef.setProperties(
        title=msg('Evolutive'),
        transitions=('evolve', 'enqueue', 'dispatch', 'activate'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, (r_manager, r_version_owner))
    sdef.setPermission(p_versions, 0, (r_manager, r_owner, r_editor, r_writer))
    sdef.setPermission(p_view_attr, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_modify_attr, 0, (r_manager, r_version_owner))

    sdef = wf.states['pending']
    sdef.setProperties(
        title=msg('Message is waiting for delivery permit'),
        transitions=('evolve', 'dequeue', 'refuse', 'dispatch', 'deliver'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_versions, 0, ())
    sdef.setPermission(p_view_attr, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_modify_attr, 0, ())

    sdef = wf.states['queued']
    sdef.setProperties(
        title=msg('Message is in the send queue'),
        transitions=('dequeue', 'deliver'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_versions, 0, ())
    sdef.setPermission(p_view_attr, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_modify_attr, 0, ())

    sdef = wf.states['sending']
    sdef.setProperties(
        title=msg('Message is currently being sent'),
        transitions=('fail', 'fix'))
    sdef.setPermission(p_delete, 0, ())
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_versions, 0, ())
    sdef.setPermission(p_view_attr, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_modify_attr, 0, ())

    sdef = wf.states['failed']
    sdef.setProperties(
        title=msg('Error happened during message send'),
        transitions=('evolve', 'enqueue', 'dispatch', 'deliver'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, (r_version_owner, r_editor, r_manager))
    sdef.setPermission(p_versions, 0, (r_owner, r_editor, r_manager))
    sdef.setPermission(p_view_attr, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_modify_attr, 0, (r_version_owner, r_editor, r_manager))

    sdef = wf.states['sent']
    sdef.setProperties(
        title=msg('Message is sent'),
        transitions=())
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_versions, 0, ())
    sdef.setPermission(p_view_attr, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_modify_attr, 0, ())

    ### setup transitions ###

    tdef = wf.transitions['evolve']
    tdef.setProperties(
        title=msg('Evolve message'),
        new_state_id='evolutive',
        actbox_name=msg('Evolve'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_permissions':p_changeperms,
              }
        )

    tdef = wf.transitions['enqueue']
    tdef.setProperties(
        title=msg('Enqueue message'),
        new_state_id='pending',
        actbox_name=msg('Enqueue'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_roles':r_owner,
                'guard_permissions':p_changeperms,
              }
        )

    tdef = wf.transitions['dequeue']
    tdef.setProperties(
        title=msg('Dequeue message'),
        new_state_id='evolutive',
        actbox_name=msg('Dequeue'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_permissions':p_changeperms,
              }
        )

    tdef = wf.transitions['refuse']
    tdef.setProperties(
        title=msg('Refuse message delivery'),
        new_state_id='evolutive',
        actbox_name=msg('Refuse'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_permissions':p_mailhost,
              }
        )

    tdef = wf.transitions['dispatch']
    tdef.setProperties(
        title=msg('Dispatch message'),
        new_state_id='queued',
        actbox_name=msg('Dispatch'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_permissions':p_mailhost,
              }
        )

    tdef = wf.transitions['deliver']
    tdef.setProperties(
        title=msg('Start message delivery'),
        new_state_id='sending',
        props={
                'guard_permissions':p_mailhost,
              }
        )

    tdef = wf.transitions['fail']
    tdef.setProperties(
        title=msg('Error during delivery'),
        new_state_id='failed',
        props={
                'guard_permissions':p_mailhost,
              }
        )

    tdef = wf.transitions['fix']
    tdef.setProperties(
        title=msg('Fix message'),
        new_state_id='sent',
        props={
                'guard_permissions':p_mailhost,
              }
        )

    tdef = wf.transitions['activate']
    tdef.setProperties(
        title=msg('Make current version principal'),
        new_state_id='',
        actbox_name=msg('Make the version principal'),
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions': p_makeprincipal,
               'guard_expr':"python: (here.implements('isVersionable') or here.implements('isVersion')) and not here.isCurrentVersionPrincipal()"
              }
        )
    tdef.addVariable( 'principal_version', "python: (here.implements('isVersionable') or here.implements('isVersion')) and here.getPrincipalVersionId()" )

def setupOutgoingMailWorkflowPhase2( wf, category, portal_metadata, portal ):

    # action template -- make version principal
    assignActionTemplateToTransition(
        category_id=category,
        action_template_id=createActionTemplate_MakeVersionPrincipal( portal_metadata, category ),
        transition='activate',
        portal_metadata=portal_metadata
    )

    # action template -- deliver mail message
    deliver_outgoing_mail = createActionTemplate_ExecuteScript(
        portal_metadata=portal_metadata,
        category_id=category,
        script_id='deliver_outgoing_mail',
    )

    assignActionTemplateToTransition(
        category_id=category,
        action_template_id=deliver_outgoing_mail,
        transition='dispatch',
        portal_metadata=portal_metadata
    )


def setupMailingItemWorkflow( wf, category, portal_metadata, msg=msg ):
    """ Setup workflow for mailing items
    """
    wf.setProperties( title='Mailing item workflow' )

    for s in ( 'evolutive', 'pending', 'queued', 'sending', 'failed', 'published' ):
        wf.states.addState(s)

    for t in ( 'activate', 'evolve', 'enqueue', 'dequeue', 'distribute', 'distribute_immediately', 'to_sending', 'fail', 'publish' ):
        wf.transitions.addTransition(t)

    for s in ( 'deliver', 'publish' ):
        wf.scripts._setOb( s, ExpressionWrapper( s, factory='dc_workflow', use_dict=1 ) )

    for p in ( p_delete, p_modify, p_list, p_view, p_access, p_versions ):
        wf.addManagedPermission(p)

    ### setup variables ###

    setupWorkflowVars( wf )

    wf.variables.addVariable( 'published' )
    vdef = wf.variables['published']
    vdef.setProperties( description='Published on the external site', for_status=1 )

    ### setup states ###

    wf.states.setInitialState('evolutive')

    sdef = wf.states['evolutive']
    sdef.setProperties(
        title=msg('Evolutive'),
        transitions=('enqueue', 'distribute', 'distribute_immediately', 'activate'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, (r_manager, r_version_owner))
    sdef.setPermission(p_access, 1, ())
    sdef.setPermission(p_list, 1, ())
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer))
    sdef.setPermission(p_versions, 0, (r_manager, r_owner, r_editor, r_writer))

    sdef = wf.states['pending']
    sdef.setProperties(
        title=msg('Message is waiting for delivery permit'),
        transitions=('dequeue', 'distribute', 'distribute_immediately'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, (r_manager, r_version_owner, r_editor))
    sdef.setPermission(p_versions, 0, ())

    sdef = wf.states['queued']
    sdef.setProperties(
        title=msg('Message is in the send queue'),
        transitions=('dequeue', 'distribute_immediately', 'to_sending'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_versions, 0, ())

    sdef = wf.states['sending']
    sdef.setProperties(
        title=msg('Message is currently being sent'),
        transitions=('fail', 'publish'))
    sdef.setPermission(p_delete, 0, ())
    sdef.setPermission(p_modify, 0, ())
    sdef.setPermission(p_versions, 0, ())

    sdef = wf.states['failed']
    sdef.setProperties(
        title=msg('Error happened during message send'),
        transitions=('evolve', 'enqueue', 'distribute', 'distribute_immediately'))
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 0, (r_version_owner, r_editor, r_manager))
    sdef.setPermission(p_versions, 0, (r_owner, r_editor, r_manager))

    sdef = wf.states['published']
    sdef.setProperties(
        title=msg('Message is sent and published in archive'),
        transitions=())
    sdef.setPermission(p_delete, 0, (r_manager, r_owner, r_editor))
    sdef.setPermission(p_modify, 1, ())
    sdef.setPermission(p_access, 1, (r_visitor,))
    sdef.setPermission(p_list, 1, (r_visitor,))
    sdef.setPermission(p_view, 0, (r_manager, r_owner, r_editor, r_reader, r_writer, r_visitor))
    sdef.setPermission(p_versions, 0, ())

    ### setup transitions ###

    tdef = wf.transitions['evolve']
    tdef.setProperties(
        title=msg('Evolve document'),
        new_state_id='evolutive',
        actbox_name=msg('Evolve'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_permissions':p_changeperms,
              }
        )

    tdef = wf.transitions['enqueue']
    tdef.setProperties(
        title=msg('Enqueue message'),
        new_state_id='pending',
        actbox_name=msg('Enqueue'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_roles':r_owner,
                'guard_permissions':p_changeperms,
              }
        )

    tdef = wf.transitions['dequeue']
    tdef.setProperties(
        title=msg('Dequeue message'),
        new_state_id='evolutive',
        actbox_name=msg('Dequeue'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_permissions':p_mailhost,
              }
        )

    tdef = wf.transitions['distribute_immediately']
    tdef.setProperties(
        title=msg('Distribute immediately'),
        new_state_id='sending',
        actbox_name=msg('Distribute immediately'),
        actbox_url=actbox_url( tdef.getId() ),
        after_script_name='deliver',
        props={
                'guard_permissions':p_mailhost,
                'guard_expr':"python: hasattr( here, 'dispatchNow')"
              }
        )

    tdef = wf.transitions['to_sending']
    tdef.setProperties(
        title=msg('Send'),
        new_state_id='sending',
        actbox_name=msg('Send'),
        actbox_url=actbox_url( tdef.getId() ),
        trigger_type=2 # TRIGGER_WORKFLOW_METHOD
        )

    tdef = wf.transitions['distribute']
    tdef.setProperties(
        title=msg('Distribute message'),
        new_state_id='queued',
        actbox_name=msg('Distribute'),
        actbox_url=actbox_url( tdef.getId() ),
        props={
                'guard_permissions':p_mailhost,
              }
        )

    tdef = wf.transitions['fail']
    tdef.setProperties(
        title=msg('Error during delivery'),
        new_state_id='failed',
        props={
                'guard_permissions':p_mailhost,
              }
        )

    tdef = wf.transitions['publish']
    tdef.setProperties(
        title=msg('Publish message on the external site'),
        new_state_id='published',
        after_script_name='publish',
        props={
                'guard_permissions':p_mailhost,
              }
        )
    tdef.addVariable( 'published', 'string: 1' )

    tdef = wf.transitions['activate']
    tdef.setProperties(
        title=msg('Make current version principal'),
        new_state_id='',
        actbox_name=msg('Make the version principal'),
        actbox_url=actbox_url( tdef.getId() ),
        props={'guard_permissions': p_makeprincipal,
               'guard_expr':"python: (here.implements('isVersionable') or here.implements('isVersion')) and not here.isCurrentVersionPrincipal()"
              }
        )
    tdef.addVariable( 'principal_version', "python: (here.implements('isVersionable') or here.implements('isVersion')) and here.getPrincipalVersionId()" )

    ### setup scripts ###

    sdef = wf.scripts['deliver']
    sdef.setExpression( "python: object.dispatchNow( object )" )

    # action template make version principal
    assignActionTemplateToTransition(
        category_id=category,
        action_template_id=createActionTemplate_MakeVersionPrincipal( portal_metadata, category ),
        transition='activate',
        portal_metadata=portal_metadata
    )

    # synchronize the document with external site document
    sdef = wf.scripts['publish']
    sdef.setExpression( "python: object.implements('isSyncableContent') and kwargs.get('sync', 1) and object.updateRemoteCopy()" )

# start generated from xml

def setupSimpleDocsWorkflowPhase1(wf, category, portal_metadata, msg=msg):

    for p in Config.ManagedPermissions:
        try:
            wf.addManagedPermission(p)
        except:
            pass

    setupWorkflowVars(wf)


def setupSimpleDocsWorkflowPhase2(wf, category, portal_metadata, portal):

    pass


def setupSimpleDocsWorkflowAttributes( wf ):

    pass

# end generated from xml


def setupWorkflowVars(wf):
    """
       Setup default workflow variables
    """
    for v in ('action', 'actor', 'comments', 'review_history', 'time', 'principal_version'):
        wf.variables.addVariable(v)

    wf.variables.setStateVar('state')

    vdef = wf.variables['action']
    vdef.setProperties(description='The last transition',
                       default_expr='transition/getId|nothing',
                       for_status=1, update_always=1)

    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed '
                       'the last transition',
                       default_expr='user/getUserName',
                       for_status=1, update_always=1)

    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_status=1, update_always=1)

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_expr="state_change/getHistory",
                       props={'guard_permissions':p_view})

    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_expr="state_change/getDateTime",
                       for_status=1, update_always=1)

    vdef = wf.variables['principal_version']
    vdef.setProperties( description='Id of the principal version', for_status=1, \
            for_catalog=1, update_always=0, default_value='version_0.1' )


def createActionTemplate_MakeVersionPrincipal( portal_metadata, category_id ):
    portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
      category_id=category_id,
      action='add_root_task_definition',
      request={ "task_definition_type": "activate_version", "template_id": "_make_version_principal", "name": "Make the version principal" }
    )
    return '_make_version_principal'

def createActionTemplate_SetCategoryAttribute( portal_metadata, category_id, task_template_id, task_template_name, attribute_name, attribute_value ):
    portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
      category_id=category_id,
      action='add_root_task_definition',
      request={
          'task_definition_type': 'set_category_attribute',
          'template_id': task_template_id,
          'name': task_template_name,
          'attribute_name': attribute_name,
          'attribute_value': attribute_value
      }
    )
    return task_template_id

def createActionTemplate_CreateVersion( portal_metadata, category_id, task_template_id, task_template_name, version_state ):
    portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
      category_id=category_id,
      action='add_root_task_definition',
      request={
        'task_definition_type': 'create_version',
        'template_id': task_template_id,
        'name': task_template_name,
        'version_state': version_state
      }
    )
    return task_template_id

def createActionTemplate_CreateSubordinate( portal_metadata, category_id, task_template_id, task_template_name, dest_category, dest_folder_template=None ):
    request={
        'task_definition_type': 'create_subordinate',
        'template_id': task_template_id,
        'name': task_template_name,
        'dest_category': dest_category,
        'dest_folder_template': dest_folder_template,
        'dest_folder_type': dest_folder_template and 'template' or 'path'
    }
    portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
      category_id=category_id,
      action='add_root_task_definition',
      request=request
    )
    return task_template_id

def createActionTemplate_Notification( portal_metadata, category_id, task_template_id, task_template_name ):
    request={
        'task_definition_type': 'notification',
        'template_id': task_template_id,
        'name': task_template_name,
    }
    portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
      category_id=category_id,
      action='add_root_task_definition',
      request=request
    )
    return task_template_id

def createActionTemplate_ExecuteScript( portal_metadata, category_id, script_id ):

    portal = portal_metadata.getPortalObject()
    catalog = getToolByName( portal, 'portal_catalog' )

    folder_path = portal.getProperty('scripts_folder').physical_path()

    # XXX may be simply: scripts_folder._getOb( script_id )
    result = catalog.searchResults( id=script_id, path=folder_path )
    script = result and result[0].getObject() or None

    request={
        'task_definition_type': 'script',
        'template_id': script_id,
        'name': script.Title(),
        'script': script,
        'portal': portal,
    }
    portal_metadata.taskTemplateContainerAdapter.makeTaskDefinitionActionByRequest(
      category_id=category_id,
      action='add_root_task_definition',
      request=request
    )
    return script_id

def assignActionTemplateToTransition( portal_metadata, category_id, action_template_id, transition ):
    category = portal_metadata.getCategoryById( category_id )
    category.transition2TaskTemplate.setdefault(transition, []).append( action_template_id )
    category._p_changed = 1

class CategoriesPhaseOneInstaller:
    after = True
    name = 'setupCategories'
 
    def __call__(self, p, phase):
        if phase==1:
            self.install(p)
        elif phase==2:
            CategoriesPhaseTwoInstaller().install(p)
        else:
            raise TypeError( "wrong phase <%s>" % phase )

    def install(self,p):
        mdtool = getToolByName( p, 'portal_metadata' )
        msg = getToolByName( p, 'msg')

        category_id = 'Folder'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Folder'), default_workflow=0, allowed_types=['Heading', 'Incoming Mail Folder', 'Outgoing Mail Folder', 'Storefront'] )

            category.addAttributeDefinition( 'nomenclative_number', 'string', msg('Nomenclative number') )
            category.addAttributeDefinition( 'postfix', 'string', msg('Postfix') )
            setupFolderWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        category_id = 'SimpleDocument'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Simple Document'), default_workflow=0, allowed_types=['DTMLDocument', 'Site Image'] )
            setupSimpleDocumentWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        category_id = 'Document'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Document'), default_workflow=0, allowed_types=['HTMLDocument'] )
            category.setBases(['SimpleDocument'])
            setupDocumentWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        category_id = 'SimplePublication'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Simple Publication'), default_workflow=0, allowed_types=['DTMLDocument', 'Site Image', 'Tabular Report', 'Voting']  )
            setupSimplePublicationWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        category_id = 'Publication'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Publication'), default_workflow=0, allowed_types=['HTMLDocument']  )
            category.setBases(['SimplePublication'])
            setupPublicationWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        category_id = 'Directive'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Directive'), default_workflow=0, allowed_types=['HTMLDocument'] )
            setupDirectiveWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        category_id = 'IncomingMail'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Incoming Mail'), default_workflow=0, allowed_types=['HTMLDocument'], disallow_manual=1 )

            category.addAttributeDefinition( 'senderName', 'string', msg('Sender name') )
            category.addAttributeDefinition( 'senderAddress', 'string', msg('Sender address') )
            category.addAttributeDefinition( 'messageDate', 'date', msg('Message date') )

            setupIncomingMailWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        category_id = 'OutgoingMail'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Outgoing Mail'), default_workflow=0, allowed_types=['HTMLDocument'] )

            category.addAttributeDefinition( 'recipientName', 'string', msg('Recipient name') )
            category.addAttributeDefinition( 'recipientAddress', 'string', msg('Recipient address') )

            setupOutgoingMailWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        category_id = 'MailingItem'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('Mailing Item'), default_workflow=0, allowed_types=['HTMLDocument'] )
            setupMailingItemWorkflow( category.getWorkflow(), category_id, mdtool, msg )

        # start generated from xml

        category_id = 'SimpleDocs'
        if not mdtool.getCategoryById( category_id ):
            category = mdtool.addCategory( category_id, msg('category.SimpleDocs.title'), default_workflow=0, allowed_types=[] )
            category.addAttributeDefinition( 'DocDate', 'date', msg('category.SimpleDocs.metadata.DocDate'), None )
            category.addAttributeDefinition( 'RegNo', 'string', msg('category.SimpleDocs.metadata.RegNo'), '' )

            setupSimpleDocsWorkflowPhase1( category.getWorkflow(), category_id, mdtool, msg )

            setupSimpleDocsWorkflowAttributes( category.getWorkflow() )

        # end generated from xml


class CategoriesPhaseTwoInstaller:
    after = True

    priority = 80 #CatPhaseOne and Workflow and Script installers

    _def_categories = ( 'OutgoingMail', 'SimpleDocs', )

    def install(self, p):
        mdtool = getToolByName( p, 'portal_metadata' )

        for category_id in self._def_categories:
            category = mdtool.getCategoryById( category_id )
            setup = globals()[ 'setup%sWorkflowPhase2' % category_id ]
            setup( category.getWorkflow(), category_id, mdtool, p )

def initialize( context ):
    # module initialization callback

    context.registerInstaller( CategoriesPhaseOneInstaller )
    context.registerInstaller( CategoriesPhaseTwoInstaller )
