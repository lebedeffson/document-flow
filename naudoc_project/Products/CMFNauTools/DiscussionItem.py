"""

$Id: DiscussionItem.py,v 1.17 2006/03/31 13:31:27 ypetrov Exp $
$Editor: vsafronovich $
"""
__version__ = '$Revision: 1.17 $'[11:-2]

from copy import copy

from zLOG import LOG, DEBUG, TRACE, INFO, ERROR

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFDefault.DiscussionItem import DiscussionItem as _DiscussionItem, \
          DiscussionItemContainer as _DiscussionItemContainer,\
          factory_type_information as _DiscussionItem_fti

import Features
from SimpleObjects import ContentBase, ContainerBase
from Utils import InitializeClass, cookId, _checkId


DiscussionItemType = _DiscussionItem_fti[0].copy()
DiscussionItemType['disallow_manual'] = 1


def addDiscussionItem( self, id, title='', description='', text_format='',
                       text='', reply_to=None, RESPONSE=None, **kwargs ):
    """
    Add a discussion item

    'title' is also used as the subject header
    if 'description' is blank, it is filled with the contents of 'title'
    'reply_to' is the object (or path to the object) which this is a reply to

    Otherwise, same as addDocument
    """
    item = DiscussionItem( id, title=title, description=(description or title),
                           text_format=text_format, text=text, **kwargs )
    item._parse()

    self._setObject( id, item )
    item = self._getOb( id )

    if reply_to:
        item.setReplyTo( reply_to )

    if RESPONSE is not None:
        RESPONSE.redirect( self.absolute_url() )


class DiscussionItem( ContentBase, _DiscussionItem ):
    """
        Class for content which is a response to other content.
    """
    _class_version = 1.00

    meta_type           = 'Discussion Item'
    portal_type         = 'Discussion Item'

    __implements__ = Features.createFeature('isDiscussionItem'), \
                     ContentBase.__implements__, \
                     _DiscussionItem.__implements__

    security = ClassSecurityInfo()

    def __init__( self, id, text_format='', text='', **kwargs ):
        ContentBase.__init__( self, id, **kwargs )
        _DiscussionItem.__init__( self, id, self.title, self.description, text_format, text )

    SearchableText = _DiscussionItem.SearchableText
    Creator = _DiscussionItem.Creator
    getPrincipalVersionId = ''

InitializeClass( DiscussionItem )


class DiscussionItemContainer( ContainerBase, _DiscussionItemContainer ):
    """
        Store DiscussionItem objects. Discussable content that
        has DiscussionItems associated with it will have an
        instance of DiscussionItemContainer injected into it to
        hold the discussion threads.
    """
    _class_version = 1.00

    security = ClassSecurityInfo()

    def __init__( self, id=None, title=None ):
        ContainerBase.__init__( self, id, title )
        _DiscussionItemContainer.__init__( self )

    security.declareProtected( CMFCorePermissions.ReplyToItem, 'createReply' )
    def createReply( self, title, text, Creator, version=None, email=None ):
        """
            Create a reply in the proper place
        """
        id = cookId( self, prefix='discussion')
        discussion = DiscussionItem( id, title=title, description=title,
                                     text_format='structured-text', text=text )

        self._setObject( id, discussion )
        discussion = self._getOb(id)

        if Creator:
            discussion.creator = Creator

        discussion.setReplyTo( self._getDiscussable() )

        if len(discussion.parentsInThread()) == 1:
            discussion.doc_ver = version
            discussion.email = email

        return id

    def _setOb(self, id, object):
        self._container[id] = object

    def _delOb(self, id):
        del self._container[id]

    def _getOb(self, id, default=Missing):
        try:
            return self._container[id].__of__(self)
        except KeyError:
            if default is not Missing:
                return default

        raise AttributeError(id)

    def _checkId(self, id, allow_dup = False):
        if allow_dup:
            _checkId(id)
        else:
            _checkId(id, self._container)

InitializeClass( DiscussionItemContainer )


def initialize( context ):
    # module initialization callback

    context.registerContent( DiscussionItem, addDiscussionItem, DiscussionItemType )
