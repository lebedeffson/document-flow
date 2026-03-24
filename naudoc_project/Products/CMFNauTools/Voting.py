"""

$Editor: ypetrov $
$Id: Voting.py,v 1.12 2008/06/04 11:30:16 oevsegneev Exp $
"""
__version__ = '$Revision: 1.12 $'[11:-2]

from AccessControl import ClassSecurityInfo
from ZODB.PersistentMapping import PersistentMapping

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

import Features
from Exceptions import SimpleError
from SimpleNauItem import SimpleNauItem
from Utils import InitializeClass, addQueryString

VotingType = { 'id'             : 'Voting'
             , 'meta_type'      : 'Voting'
             , 'title'          : "Voting"
             , 'description'    : "Polls manager"
             , 'icon'           : 'voting_icon.gif'
             , 'product'        : 'CMFNauTools'
             , 'factory'        : 'addVoting'
             , 'immediate_view' : 'voting_edit_form'
             , 'condition'      : 'object/getSite'
             , 'actions'        :
               ( { 'id'            : 'view'
                 , 'name'          : "View"
                 , 'action'        : 'voting_view'
                 , 'permissions'   : (CMFCorePermissions.View, )
                 }
               , { 'id'            : 'vote'
                 , 'name'          : "Vote"
                 , 'action'        : 'voting_poll_form'
                 , 'permissions'   : (CMFCorePermissions.View, )
                 , 'condition'     : 'python: object.canVote(request)'
                 }
               , { 'id'            : 'edit'
                 , 'name'          : "Edit"
                 , 'action'        : 'voting_edit_form'
                 , 'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
                 }
               , { 'id'            : 'metadata'
                 , 'name'          : "Metadata"
                 , 'action'        : 'metadata_edit_form'
                 , 'permissions'   : (CMFCorePermissions.ModifyPortalContent, )
                 }
               )
             }

def addVoting( self, id, title='', **kwargs ):
    """
        Add a Voting Item
    """
    obj = Voting( id, title, **kwargs )
    self._setObject( id, obj )


class Voting( SimpleNauItem ):
    """
       Portal voting
    """
    meta_type = 'Voting'
    portal_type = 'Voting'

    effective_date = expiration_date = None

    __implements__ = ( Features.isCategorial
                     , Features.isPublishable
                     , SimpleNauItem.__implements__
                     )

    manage_options = SimpleNauItem.manage_options

    security = ClassSecurityInfo()

    def __init__( self, id, title=None, **kwargs ):
        # instance constructor
        SimpleNauItem.__init__( self, id, title, **kwargs )

        self.choices = []
        self.voted_ips = []
        self.voted_members = []
        self.finished = None

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'configure')
    def configure(self, choices=[], finished=None, main=None):
        """
            Edit voting choices, finished and main properties
        """
        for id in range(len(choices)):
            self.choices[id]['title'] = choices[id]

        self.finished = not not finished

        # main property is set as the voting uid to the site object
        site = self.getSite()

        if main:
            site.voting = self.getUid()

        elif site.voting == self.getUid():
            site.voting = None

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'addChoice')
    def addChoice(self, title):
        """
            Add voting choice
        """
        self.choices.append( PersistentMapping({ 'title': title, 'count': 0 }) )
        self._p_changed = 1

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'delChoices')
    def delChoices(self, ids=[]):
        """
            Delete voting choices
        """
        ids.sort()
        for shift in range(len(ids)):
            self.choices.pop(ids[shift] - shift)
        self._p_changed = 1

    security.declareProtected( CMFCorePermissions.View, 'processVote' )
    def processVote(self, REQUEST):
        """
           Process user vote
        """
        choice = REQUEST.form.get('responses')

        if choice is None:
            return self._redirectBack(REQUEST, message = "Select your voting choice")

        try:
            self._checkVoting(REQUEST)
        except SimpleError, reason:
            return self._redirectBack(REQUEST, message = reason)

        self.choices[choice]['count'] += 1

        # register user ip
        self.voted_ips.append( REQUEST['REMOTE_ADDR'] )

        # set cookie to the user
        REQUEST.RESPONSE.setCookie( '%s_voted' % self.getUid(), '1', path='/', expires='Wed, 19 Feb 2020 14:28:00 GMT' )

        # register portal user id
        mt = getToolByName( self, 'portal_membership' )
        member_id = not mt.isAnonymousUser() and mt.getAuthenticatedMember().getMemberId()
        if member_id:
            self.voted_members.append(member_id)

        self._p_changed = 1

        return self._redirectBack(REQUEST, message = "Thank you. Your vote have accounted.")

    security.declareProtected( CMFCorePermissions.View, 'listChoices' )
    def listChoices(self):
        """
            Returns list of voting choices
        """
        return tuple( self.choices )

    security.declareProtected( CMFCorePermissions.View, 'canVote' )
    def canVote(self, REQUEST):
        """
            Checks whether curent user can vote or not
        """
        try:
            self._checkVoting(REQUEST)

        except SimpleError:
            return False

        return True

    def _checkVoting(self, REQUEST):
        """
        """
        if self.finished:
            raise SimpleError, 'You cannot vote because this poll already finished'

        # check by ip or cookies
        if REQUEST['REMOTE_ADDR'] in self.voted_ips or REQUEST.cookies.get('%s_voted' % self.getUid()):
            raise SimpleError, 'You have voted already'

        # check portal member by its id
        membership = getToolByName(self, 'portal_membership')
        member_id = not membership.isAnonymousUser() and membership.getAuthenticatedMember().getMemberId()

        if member_id and member_id in self.voted_members:
            raise SimpleError, 'You have voted already'

    security.declareProtected( CMFCorePermissions.View, 'haveVotes' )
    def haveVotes(self):
        """
            Checks whether this poll have user votes
        """
        for choice_data in self.choices:
            if choice_data['count']: return True

        return False

    def _redirectBack(self, REQUEST, message):
        destination = REQUEST['HTTP_REFERER'] or self.external_url()
        REQUEST.RESPONSE.redirect(addQueryString(destination, portal_status_message = message))

InitializeClass(Voting)


def initialize( context ):
    # module initialization callback

    context.registerContent( Voting, addVoting, VotingType )
