"""
MailFilter -- filter class which can be matched against messages

$Editor: vpastukhov $
$Id: MailFilter.py,v 1.2 2004/08/10 09:42:07 ikuleshov Exp $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

import re
from types import StringType

from email.Utils import getaddresses

from AccessControl import ClassSecurityInfo
from ZODB.PersistentList import PersistentList

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from ActionInformation import ActionDefinition
from Features import createFeature
from SimpleObjects import InstanceBase, SimpleRecord
from Utils import InitializeClass, cookId


_test_operations = ['+','-']

_test_sender = ['from','reply-to','sender','return-path','x-envelope-from']
_test_recipient = ['to','cc','bcc','resent-to','resent-cc','x-envelope-to']
_test_subject = ['subject']


class MailFilter( InstanceBase ):
    """
        Filter that can be applied to incoming mail messages
    """
    _class_version = 1.39

    __implements__ = ( createFeature('isMailFilter'),
                       InstanceBase.__implements__ )

    security = ClassSecurityInfo()

    _subitems = [ 'action' ]

    _properties = InstanceBase._properties + (
            {'id':'enabled', 'type':'boolean', 'mode':'w'},
        )

    # default property value
    enabled = True

    # default filter action Id
    _default_action = 'mail_filter_default'

    # available tests against mail message
    _test_types = [
            {'id':'sender'},
            {'id':'recipient'},
            {'id':'subject'},
            {'id':'text'},
            {'id':'message'},
            {'id':'header',
                'properties':[
                    {'id':'header','type':'string'}
                ]
            },
        ]

    def __init__( self, id=None, title=None ):
        # instance constructor
        InstanceBase.__init__( self, id, title )
        self.action = ActionDefinition( 'action' )
        self.tests = PersistentList()

    def _instance_onCreate( self ):
        # initialize action definition
        self.setAction( self._default_action )

    security.declareProtected( CMFCorePermissions.View, 'getAction' )
    def getAction( self ):
        """
        """
        return self.action

    security.declareProtected( CMFCorePermissions.ManageProperties, 'setAction' )
    def setAction( self, id, **kwargs ):
        """
        """
        obj = self.parent().parent() # mail folder
        action = self.action
        id = id or self._default_action

        if action.getActionId() != id:
            action.setActionId( id )

        action.setProperties( **kwargs )

    security.declareProtected( CMFCorePermissions.View, 'isEnabled' )
    def isEnabled( self ):
        """
        """
        return self.enabled

    security.declareProtected( CMFCorePermissions.ManageProperties, 'enableFilter' )
    def enableFilter( self, enable=True ):
        """
        """
        self.enabled = not not enable

    security.declareProtected( CMFCorePermissions.ManageProperties, 'append' )
    def append( self, ttype, id=None, op=None, patterns=None, **kwargs ):
        """
        """
        # check for valid test type
        ttype = ttype.lower()
        for test in self._test_types:
            if ttype == test['id']:
                break
        else:
            raise ValueError, ttype

        # check for duplicate test id
        if id is None:
            id = cookId( self.tests, prefix='test' )
        else:
            for atest in self.tests:
                if atest.id == id:
                    raise KeyError, id

        # check for valid test operation
        if op is None:
            op = '+'
        elif op not in _test_operations:
            raise ValueError, op

        # TODO should check all props for given test type
        if ttype == 'header' and not kwargs.get('header'):
            raise ValueError, 'header'

        test = SimpleRecord( id=id, type=ttype, op=op, **kwargs )
        self.tests.append( test )
        index = len( self.tests ) - 1

        self[ index ] = patterns
        return index

    security.declareProtected( CMFCorePermissions.ManageProperties, 'edit' )
    def edit( self, id=None, patterns=None, index=None ):
        if index is None:
            index = self._getIndex( id )
        self[ index ] = patterns

    security.declareProtected( CMFCorePermissions.ManageProperties, 'get' )
    def get( self, id=None, default=Missing, index=None ):
        if index is None:
            try:
                index = self._getIndex( id )
            except KeyError:
                if default is Missing:
                    raise
                return default
        return self[ index ]

    security.declareProtected( CMFCorePermissions.ManageProperties, 'remove' )
    def remove( self, id=None, index=None ):
        if index is None:
            index = self._getIndex( id )
        del self[ index ]

    security.declareProtected( CMFCorePermissions.ManageProperties, 'clear' )
    def clear( self ):
        del self.tests[:]

    def __len__( self ):
        return len( self.tests )

    def __nonzero__( self ):
        return True

    def __getitem__( self, index ):
        return self.tests[ index ].copy()

    def __setitem__( self, index, patterns ):
        test = self.tests[ index ]

        if patterns is None:
            patterns = []
        elif type(patterns) is StringType:
            if test.type in ['sender','recipient']:
                patterns = patterns.split()
            else:
                patterns = [ v.strip() for v in patterns.split('\n') ]

        # remove empty pattern strings
        test.patterns = filter( None, list(patterns) )
        # notify persistence
        self.tests[ index ] = test

    def __delitem__( self, index ):
        del self.tests[ index ]

    security.declarePrivate( 'match' )
    def match( self, msg ):
        if not self.enabled:
            return False
        res = True

        for test in self.tests:
            typ = test.type
            if not test.patterns:
                continue

            if typ == 'header':
                res = _header_match( msg, test.patterns, [test.header] )

            elif typ == 'sender':
                res = _email_match( msg, test.patterns, _test_sender )

            elif typ == 'recipient':
                res = _email_match( msg, test.patterns, _test_recipient )

            elif typ == 'subject':
                res = _header_match( msg, test.patterns, _test_subject )

            elif typ == 'text':
                res = _text_match( msg, test.patterns )

            elif typ == 'message':
                for part in msg.walk():
                    res = _header_match( part, test.patterns ) or \
                          _text_match( part, test.patterns )
                    if res:
                        break

            if test.op == '-':
                res = not res
            if not res:
                break

        return res

    def _getIndex( self, id ):
        if id is None:
            raise KeyError, id
        index = 0
        for test in self.tests:
            if test.id == id:
                return index
            index += 1
        else:
            raise KeyError, id

    security.declareProtected( CMFCorePermissions.View, 'listAvailableTests' )
    def listAvailableTests( self ):
        """
        """
        return list( self._test_types )

    def _initstate( self, mode ):
        # update instance version
        if not InstanceBase._initstate( self, mode ):
            return False

        if mode and not hasattr( self, 'tests' ):
            self.tests = PersistentList()

        if hasattr( self, 'cond' ): # < 1.36
            for cond in self.cond:
                # cond is (id, type, op, name, patterns)
                self.append( cond[1], cond[0], op='+', patterns=cond[4] )
            del self.cond

        if hasattr( self, '_action' ): # < 1.37
            self.action = ActionDefinition( 'action' )
            self.action.action_id = self._default_action
            del self._action

        if hasattr( self, '_tests' ): # < 1.38
            self.tests = self._tests
            del self._tests

        return True

InitializeClass( MailFilter )


def _text_match( msg, patterns,
                 _re_escape=re.escape, _re_flags=(re.I + re.L) ):
    # text substring match for MailFilter
    if not msg.is_text():
        return False

    parts = []
    for p in patterns:
        parts.append( r'\s+'.join( map( _re_escape, p.split() ) ) )
    regex = re.compile( '(?:' + '|'.join(parts) + ')', _re_flags )

    return not not regex.search( msg.get_payload( decode=True ) )

def _header_match( msg, patterns, headers=None,
                   _re_escape=re.escape, _re_flags=(re.I + re.L) ):
    # header substring match for MailFilter
    parts = []
    for p in patterns:
        parts.append( r'\s+'.join( map( _re_escape, p.split() ) ) )
    regex = re.compile( '(?:' + '|'.join(parts) + ')', _re_flags )

    if headers is None:
        # scan all headers
        for name, value in msg.items( decode=True ):
            if regex.search( value ):
                return True
    else:
        # scan only named headers
        for header in headers:
            for value in msg.get_all( header, decode=True ):
                if regex.search( value ):
                    return True

    return False

def _email_match( msg, patterns, headers,
                  _re_escape=re.escape, _re_flags=(re.I + re.L) ):
    # email header match for MailFilter
    parts = []
    for p in patterns:
        p = map( _re_escape, p.strip().split('@',1) )
        if len(p) == 1:
            # p is [ pattern ]
            p = p[0].replace( r'\*', r'.*' )
        else:
            # p is [ username, domain ]
            p[0] = p[0].replace( r'\*', r'[^@]*' )
            p[1] = p[1].replace( r'\*\.', r'[^@.]*\.' ) \
                       .replace( r'\*', r'(?:[^@]*(?:\.|\.*$))?' )
            p = '@'.join( p )
        parts.append( p )

    regex = re.compile( '^(?:' + '|'.join(parts) + ')$', _re_flags )

    for header in headers:
        values = msg.get_all( header, decode=True )
        if not values:
            continue
        for name, email in getaddresses( values ):
            #if regex.match( email.strip().rstrip('.') ): # needs python 2.2
            if regex.match( email.strip() ):
                return True

    return False
