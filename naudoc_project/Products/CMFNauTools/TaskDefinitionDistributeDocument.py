"""
Action template for distribute document.

$Editor: inemihin $
$Id: TaskDefinitionDistributeDocument.py,v 1.8 2005/12/13 12:20:37 ikuleshov Exp $
"""

__version__ = '$Revision: 1.8 $'[11:-2]

import Exceptions
from TaskDefinitionAbstract import TaskDefinition
from TaskDefinitionAbstract import TaskDefinitionForm
from TaskDefinitionAbstract import TaskDefinitionController
from TaskDefinitionAbstract import TaskDefinitionRegistry
from Utils import cookId, InitializeClass, getObjectByUid, getToolByName, parseDate


class TaskDefinitionDistributeDocument(TaskDefinition):
    """
        .
    """

    _class_version = 1.01

    def __init__(self):
        """
            Creates new instance.
        """
        TaskDefinition.__init__( self )
        self.type = 'distribute_document'
        self._allow_edit = []

        self.requested_users = []
        self.other_user_emails = ''
        self.subject = ''
        self.letter_parts = []
        self.comment = ''
        self.letter_type = 'partial'

    def _initstate( self, mode ):
        """
            Initialize attributes
        """
        if not TaskDefinition._initstate( self, mode ):
            return 0

        if getattr( self, 'letter_type', None ) is None:
            self.letter_type = 'partial'

    def changeTo( self, taskDefinition ):
        """
            Changes self data.

            Arguments:
                'taskDefinition' -- instance of TaskDefinition
        """
        TaskDefinition.changeTo( self, taskDefinition )
        self._allow_edit = taskDefinition._allow_edit

        # specific fields
        self.requested_users = taskDefinition.requested_users
        self.other_user_emails = taskDefinition.other_user_emails
        self.subject  = taskDefinition.subject
        self.letter_parts = taskDefinition.letter_parts
        self.letter_type = taskDefinition.letter_type
        self.comment = taskDefinition.comment

    def toArray( self ):
        """
            Converts object's fields to dictionary

            Result:
                Dictionary as { 'field_name': 'field_value', ... }
        """
        arr = TaskDefinition.toArray( self )
        arr['_allow_edit'] = self._allow_edit

        arr["requested_users"] = self.requested_users
        arr["other_user_emails"] = self.other_user_emails
        arr["subject"] = self.subject
        arr["letter_parts"] = self.letter_parts
        arr["comment"] = self.comment
        arr["letter_type"] = self.letter_type
        return arr

    def activate(self, object, context, transition):
        """
            Activate taskDefinition (action template)

            Arguments:
                'object' -- object in context of which happened activation
                'context' -- Action context

            Result:
                 None
        """
        self.loadParams( context )

        lang = self.REQUEST.get('LOCALIZER_LANGUAGE')

        requested_users = self._getField('requested_users')[:]
        comment = self._getField('comment')
        subject = self._getField('subject')
        letter_parts = self._getField('letter_parts')[:]
        letter_type = self._getField('letter_type')
        other_user_emails = self._getField('other_user_emails')

        from re import split as re_split

        if other_user_emails:
            requested_users.extend( re_split( '[;\s]\s*', other_user_emails ) )

        self.saveParams( context )
        sent = object.distributeDocument( template='distribute_document_template'
                                  , mto=requested_users
                                  , from_member=1
                                  , lang=lang
                                  , comment=comment
                                  , subject=subject
                                  , letter_parts=letter_parts
                                  , letter_type=letter_type
                                  )

    def allowEdit( self, name ):
        # fields is groupped
        if name in ['requested_users', 'other_user_emails']:
            return 'users' in self._allow_edit
        if name in ['subject', 'letter_parts', 'comment']:
            return 'content' in self._allow_edit
        return 0

InitializeClass(TaskDefinitionDistributeDocument)

class TaskDefinitionFormDistributeDocument(TaskDefinitionForm):
    """
      Class view (form)
    """
    _template = 'task_definition_distribute_document'

    def onSubmit( self ):
        """
          Returns java-script fragment, to check form's fields on submit

        """
        script = TaskDefinitionForm.onSubmit( self )
        script +="""
    if ( !validSelectionRequestedUsers( form ) ){
      alert('You have not selected user(s)');
      return false;
    }

    if ( !validSelectionLetterContent( form ) ){
      alert("'You didn\'t specify what to include in the letter.");
      return false;
    }

    if ( selectedTransportableContent( form ) && !userAgreeWithSendOverNonSecureConnection() ){
      return false;
    }

    requested_users = form['requested_users:list'];
    selectAll(requested_users);
    return true;
        """
        return script

    getTaskDefinitionFormScriptOnSubmit = onSubmit

class TaskDefinitionControllerDistributeDocument(TaskDefinitionController):
    """
      Class controller
    """
    def getEmptyArray(self):
        """
            Returns dictionary with empty values.

            Arguments:
                'array' -- dictionary to fill
        """
        array = TaskDefinitionController.getEmptyArray(self)
        array['_allow_edit'] = []

        array['requested_users'] = []
        array['other_user_emails'] = ''
        array['subject'] = ''
        array['letter_parts'] = ['link_to_doc']
        array['letter_type'] = 'partial'
        array['comment'] = ''
        return array

    def getTaskDefinitionByRequest( self, request ):
        """
        """
        taskDefinition = TaskDefinitionDistributeDocument()
        TaskDefinitionController.getTaskDefinitionByRequest(self, request, taskDefinition)

        if request.has_key('_allow_edit'):
            taskDefinition._allow_edit = request['_allow_edit']
        else:
            taskDefinition._allow_edit = []

        if request.has_key('requested_users'):
            taskDefinition.requested_users = request['requested_users']

        if request.has_key('other_user_emails'):
            taskDefinition.other_user_emails = request['other_user_emails']

        if request.has_key('subject'):
            taskDefinition.subject = request['subject']

        if request.has_key('letter_parts'):
            taskDefinition.letter_parts = request['letter_parts']

        if request.has_key('letter_type'):
            taskDefinition.letter_type = request['letter_type']

        if request.has_key('comment'):
            taskDefinition.comment = request['comment']

        return taskDefinition


class TaskDefinitionRegistryDistributeDocument(TaskDefinitionRegistry):
    """
        Class that provides information for factory about class
    """
    type_list = ( { "id": "distribute_document"
                  , "title": "Distribute document" 
                  },
                )

    Controller = TaskDefinitionControllerDistributeDocument()
    Form = TaskDefinitionFormDistributeDocument()

    dtml_token = 'distribute_document'


def initialize( context ):
    # module initialization callback
    context.registerAction( TaskDefinitionRegistryDistributeDocument() )
