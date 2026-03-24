# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/TrayAgent/TrayAgentFeeder.py
# Compiled at: 2008-12-12 17:12:53
""" 
Tray Agent feeder object. 

$Id: TrayAgentFeeder.py,v 1.8 2008/12/12 14:12:53 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.8 $'[11:-2]
from random import randrange
from xmlrpclib import boolean
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Globals import PersistentMapping
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import Unauthorized
from Products.CMFNauTools.SearchProfile import SearchQuery
from Products.CMFNauTools.SimpleObjects import InstanceBase
from Products.CMFNauTools.Utils import InitializeClass, translate, getLanguageInfo
TasksQueryMode = 'query_pending_tasks'
MemberDataExtensions = ({'id': 'ta_check_interval', 'type': 'int', 'default': 2, 'title': '[Tray agent] check interval'}, {'id': 'ta_sound_alert', 'type': 'boolean', 'default': 1, 'title': '[Tray agent] sound notification'}, {'id': 'ta_open_browser', 'type': 'boolean', 'default': 1, 'title': '[Tray agent] show event details in browser'}, {'id': 'ta_balloon_tips', 'type': 'boolean', 'default': 1, 'title': '[Tray agent] display balloon tips'}, {'id': 'ta_check_on_startup', 'type': 'boolean', 'default': 1, 'title': '[Tray agent] check events on startup'})
FeederId = 'TrayAgentFeeder'

class TrayAgentFeeder(InstanceBase, ActionProviderBase):
    __module__ = __name__
    meta_type = 'Tray Agent Feeder'
    _actions = [ActionInformation(id='tray_agent_personalize', title='Tray agent settings', action=Expression(text='string: ${portal_url}/tray_agent_settings_form'), permissions=(CMFCorePermissions.View,), category='user', condition=Expression(text='member'), visible=1)]
    security = ClassSecurityInfo()

    def __init__(self, **kw):
        InstanceBase.__init__(self, id=FeederId, **kw)
        self.tray_last_accessed = PersistentMapping()
        return

    security.declarePrivate('listActions')

    def listActions(self, info=None):
        """
        Return available actions via tool.
        """
        return self._actions
        return

    security.declareProtected(CMFCorePermissions.View, 'getUserSettings')

    def getUserSettings(self):
        """
        """
        membership = getToolByName(self, 'portal_membership')
        member = membership.getAuthenticatedMember()
        if not member:
            raise SimpleError
        settings = {'locale': (membership.getLanguage()[:2] or 'en')}
        for p in MemberDataExtensions:
            id = p['id']
            value = member.getProperty(id)
            if p['type'] == 'boolean':
                value = boolean(value)
            settings[id[3:]] = value

        return settings
        return

    security.declareProtected(CMFCorePermissions.View, 'checkEvents')

    def checkEvents(self):
        """
           Tray agent feeder.
        """
        portal_sentinel = getToolByName(self, 'portal_sentinel')
        if not portal_sentinel.checkAction('TrayAgent'):
            msg = getToolByName(self, 'msg')
            return (5000, '', msg('sentinel.trial_expired') % msg('Tray agent support'), '')
        membership = getToolByName(self, 'portal_membership')
        member = membership.getAuthenticatedMember()
        name = member.getId()
        last_accessed = self.tray_last_accessed.get(name, DateTime())
        query = SearchQuery()
        if TasksQueryMode == 'query_pending_tasks':
            query.filter_query = {}
        else:
            self.tray_last_accessed[name] = DateTime()
            query.filter_query = {'created': last_accessed, 'created_usage': 'range:min'}
        followup = getToolByName(self, 'portal_followup')
        results = followup.executeQuery(query=query, mode_name='showNew')
        count = len(results)
        if not count:
            return (
             0, '', '', '')
        token = self.getAccessToken()
        url = self.absolute_url(action='tokenAccess', params={'token': token, 'target_url': (self.portal_url() + '/tray_agent_main'), 'last_accessed': (int(last_accessed))})
        if count == 1:
            message = translate(self, 'A new task has been assigned for you.')
            message += '\n'
            message += translate(self, 'Title') + ': '
            message += results[0]['Title']
        else:
            message = translate(self, 'There are %d new tasks waiting for you.') % count
        lang = membership.getLanguage()[:2]
        message = unicode(message, getLanguageInfo(lang)['python_charset'])
        event_code = 'generic'
        severity = 5000
        return (
         severity, event_code, message, url)
        return

    security.declarePrivate('getAccessToken')

    def getAccessToken(self):
        membership = getToolByName(self, 'portal_membership')
        if membership.isAnonymousUser():
            raise SimpleError, 'You must be logged in to get an instant access token'
        if not hasattr(self, '_v_authorized_agents'):
            self._v_authorized_agents = {}
        token = None
        while not token:
            token = '%d.%d' % (int(DateTime()), randrange(1000000000))
            if self._v_authorized_agents.get(token):
                token = None

        member = membership.getAuthenticatedMember()
        self._v_authorized_agents[token] = member.getId()
        return token
        return

    security.declarePublic('tokenAccess')

    def tokenAccess(self, token, target_url):
        """
            Note:

            User credentials are sent back to the client as plain text 
            therefore it is strongly recommended to enable SSL encryption 
            before using the NauDoc tray agent application.
        """
        if not hasattr(self, '_v_authorized_agents'):
            raise Unauthorized, token
        name = self._v_authorized_agents.get(token)
        if not name:
            raise Unauthorized, token
        membership = getToolByName(self, 'portal_membership')
        member = membership.getMemberById(name)
        if not member:
            raise Unauthorized, token
        cookie_crumbler = self.cookie_authentication
        self.REQUEST[cookie_crumbler.name_cookie] = name
        self.REQUEST[cookie_crumbler.pw_cookie] = member.getPassword()
        cookie_crumbler(self.parent(), self.REQUEST)
        self.dropAccessToken(token)
        if target_url.startswith(self.portal_url()):
            self.REQUEST['RESPONSE'].redirect(target_url)
        return

    security.declarePrivate('dropAccessToken')

    def dropAccessToken(self, token):
        if hasattr(self, '_v_authorized_agents') and self._v_authorized_agents.has_key(token):
            del self._v_authorized_agents[token]
        return


InitializeClass(TrayAgentFeeder)
