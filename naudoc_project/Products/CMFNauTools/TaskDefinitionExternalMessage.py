"""
On-transition action -- send a message to a user of the external system.

$Editor: vpastukhov $
$Id: TaskDefinitionExternalMessage.py,v 1.12 2006/02/09 11:20:54 vsafronovich Exp $
"""
__version__ = '$Revision: 1.12 $'[11:-2]

from Globals import HTMLFile

from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

import Exceptions
from TaskDefinitionAbstract import TaskDefinition, \
        TaskDefinitionForm, TaskDefinitionController, TaskDefinitionRegistry
from SimpleObjects import SimpleRecord
from Utils import InitializeClass


_recipient_types = [
        {'id':'username', 'title':'action.external_message.external_username'},
        {'id':'owner',    'title':'action.external_message.object_owner'},
        {'id':'editor',   'title':'action.external_message.folder_editor'},
        {'id':'assigned', 'title':'action.external_message.assigned_user'},
    ]


class ExternalMessage( TaskDefinition ):
    """
        Sends a message to a user of the external system.
    """
    _class_version = 1.1

    _properties = TaskDefinition._properties + (
            {'id':'message_service', 'type':'link', 'features':'isService', 'mode':'w'},
            {'id':'message_type', 'type':'string', 'mode':'wn'},
            {'id':'message_title', 'type':'string', 'mode':'wn'},
            {'id':'message_template', 'type':'link', 'features':'isTemplate', 'mode':'w'},
            {'id':'recipient_type', 'type':'string', 'mode':'w'},
            {'id':'recipient_id', 'type':'string', 'mode':'wn'},
        )

    message_service = None
    message_type = None
    message_title = None
    message_template = None
    recipient_type = None
    recipient_id = None

    type = 'external_message'

    def __init__( self ):
        TaskDefinition.__init__( self )

    def changeTo( self, taskDefinition ):
        TaskDefinition.changeTo( self, taskDefinition )
        self.message_type = taskDefinition.message_type
        self.message_title = taskDefinition.message_title
        self.recipient_type = taskDefinition.recipient_type
        self.recipient_id = taskDefinition.recipient_id
        self._updateProperty( 'message_service', taskDefinition.message_service )
        self._updateProperty( 'message_template', taskDefinition.message_template )

    def toArray( self ):
        arr = TaskDefinition.toArray( self )
        arr.update( self.getProperties( monikers=True ) )
        arr['message_types'] = self.listMessageTypes()
        arr['recipient_types'] = self.listRecipientTypes()
        return arr

    def activate( self, object, context, transition ):
        """
        """
        sdef = self.getProperty('message_service')
        template = self.getProperty('message_template')

        if sdef is None or template is None:
            return {}

        connector = getToolByName( self, 'portal_connector' )
        service   = connector.getService( sdef )
        msg_type  = self.message_type
        msg_title = self.message_title
        rcpt_type = self.recipient_type

        if rcpt_type == 'owner':
            username = object.Creator()

        elif rcpt_type == 'editor':
            if object.implements('isPrincipiaFolderish'):
                folder = object
            else:
                folder = object.parent()
            username = folder.getEditor().getUserName()

        elif rcpt_type == 'username':
            username = self.recipient_id

        else:
            username = None

        recipient = service.mapRecipient( username, object )
        if recipient is None:
            raise Exceptions.SimpleError( 'action.external_message.unknown_recipient',
                                          name=(username or '?') )

        lang = service.getLanguage( recipient )
        text = template( object, lang=lang ).strip()

        if msg_title is None:
            msg_title = text.split('\n',1)[0].strip()

        service.sendMessage( recipient, text, msg_type,
                             title=msg_title, object=object )

    def listMessageTypes( self ):
        sdef = self.getProperty('message_service')
        if sdef is None:
            return []
        return sdef.getInfo( 'message_types', [] )

    def listRecipientTypes( self ):
        return _recipient_types

InitializeClass( ExternalMessage )


class ExternalMessageForm( TaskDefinitionForm ):
    _template = 'task_definition_external_message'

class ExternalMessageController( TaskDefinitionController ):

    def getEmptyArray( self ):
        emptyArray = TaskDefinitionController.getEmptyArray( self )
        emptyArray['message_service'] = None
        emptyArray['message_type'] = None
        emptyArray['message_types'] = []
        emptyArray['message_title'] = None
        emptyArray['message_template'] = None
        emptyArray['recipient_type'] = None
        emptyArray['recipient_id'] = None
        emptyArray['recipient_types'] = _recipient_types
        return emptyArray

    def createTaskDefinition( self ):
        return ExternalMessage()

    def getTaskDefinitionByRequest( self, request ):
        # XXX
        record = SimpleRecord({'vars':{}})

        TaskDefinitionController.getTaskDefinitionByRequest( self, request, record )

        for item in ExternalMessage._properties:
            id = item['id']
            if request.has_key( id ):
                record[ id ] = request[ id ]

        return record


class ExternalMessageRegistry( TaskDefinitionRegistry ):

    type_list = ( {'id':'external_message'
                  , 'title':"action.external_message.title"
                  },
                )

    Controller = ExternalMessageController()
    Form = ExternalMessageForm()

    dtml_token = type_list[0]['id']

    condition = Expression( "python: bool(portal.portal_connector.listServices( feature='isMessagingService' ))")


def initialize( context ):
    context.registerAction( ExternalMessageRegistry() )
