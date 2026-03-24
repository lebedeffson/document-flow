"""
$Id: TaskDefinitionNotification.py,v 1.9 2007/04/26 06:11:38 oevsegneev Exp $

Action template for notification about changing transition of document via email.
"""

__version__ = '$Revision: 1.9 $'[11:-2]

from Products.CMFCore import CMFCorePermissions

from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import InitializeClass, getToolByName

#--------------------------------------------------------------
class TaskDefinitionNotification( TaskDefinition ):
    """
      Notification to users about performing transition on the document.
    """

    _class_version = 1.00

    type = 'notification'

    def activate( self, object, context, transition ):
        """
            Activate taskDefinition (action template)

            Send email notifications.

            Arguments:

                'object' -- object in context of which happened activation

                'ret_from_up' -- dictionary

            Result:

                Also returns dictionary, which is passed to next (inner)
                taskDefinition's activate (if presented)

        """
        membership_tool = getToolByName( self, 'portal_membership' )
        mailhost = getToolByName( self, 'MailHost' )
        workflow_tool = getToolByName( self, 'portal_workflow' )
        emails = []

        if not ( hasattr(object, 'listSubscribedUsers') and
                 hasattr(object, 'getUserSubscription') ):
            return

        # building emails list for subscribed users that have permission to view this document
        for user in object.listSubscribedUsers():
            transitions_ids = object.getUserSubscription( user )
            if transition in transitions_ids:
                member = membership_tool.getMemberById( user, containment = True )
                email = member and member.has_permission(CMFCorePermissions.View, object) and member.getMemberEmail()
                if email:
                    emails.append(email)

        ti=workflow_tool.getTransitionInfo( object.getCategory().Workflow(), transition )
        tr_name = ti['actbox_name'] or ti['title'] or ti['id']

        if emails:
            mail_text = self.document_subscription_announce(self,
                                        transition = tr_name,
                                        doc_title = object.title_or_id(),
                                        doc_descr = object.Description(),
                                        user = membership_tool.getMemberName(),
                                        url = object.absolute_url(),
                                        subscription_url = \
                                        object.absolute_url( action='manage_document_subscription' ),
                                                        )

            mailhost.send( mailhost.createMessage( source=mail_text ), emails, raise_exc=0 )

InitializeClass( TaskDefinitionNotification )

class TaskDefinitionFormNotification( TaskDefinitionForm ):
    """
      Class view (form)

    """
    _template = 'task_definition_notification'

class TaskDefinitionControllerNotification( TaskDefinitionController ):
    """
      Class controller

    """
    def getTaskDefinitionByRequest( self, request ):
        """
            Gets destination folder uid from request and srotes it in
            TaskDefinitionNotification() instance.

        """
        taskDefinition = TaskDefinitionNotification( )
        TaskDefinitionController.getTaskDefinitionByRequest( self, request, taskDefinition )

        return taskDefinition


class TaskDefinitionRegistryNotification( TaskDefinitionRegistry ):
    """
        Class that provides information for factory about class
    """

    type_list = ( { "id": "notification"
                  , "title": "Send notification about transition perform" 
                  },
                )

    Controller = TaskDefinitionControllerNotification()
    Form = TaskDefinitionFormNotification()

    dtml_token = 'notification'


def initialize( context ):
    context.registerAction( TaskDefinitionRegistryNotification() )
