"""
Mail Folder classes.

$Editor: vpastukhov $
$Id: MailActions.py,v 1.6 2005/10/10 07:12:13 vsafronovich Exp $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

import re
from email.Utils import getaddresses

from AccessControl import ClassSecurityInfo
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName

import Config
from HTMLCleanup import HTMLCleaner
from Utils import InitializeClass, cookId, formatPlainText

class ActionBase:

    def __init__( self, definition ):
        self.definition = definition

    def perform( self, **kwargs ):
        pass


class DefaultAction( ActionBase ):

    allowed_content_types = [ 'text/html', 'text/plain' ]

    def perform( self, folder=None, message=None, document=None, category=None, creator=None ):
        """
        """
        assert not ( folder is None or message is None )
        #In case when filter moves mail message, destination folder is not mail folder.
        #assert folder.implements('isIncomingMailFolder')

        if category is None:
            category = folder.getProperty('mail_category')

        doc = self.documentFromMail( message=message, folder=folder, category=category )
        if creator:
            doc.changeOwnership( creator.getUser() )

        workflow = getToolByName( folder, 'portal_workflow' )
        workflow.doActionFor( doc, 'receive' )
        return doc

    def documentFromMail( self, folder=None, message=None, category=None, type_name='HTMLDocument' ):
        """
            Converts a MailMessage instance into a new document object.
        """
        content = None
        subtype = 'html' # 'plain' is unsupported
        text = ''
        attachments = []
        attributes = {}

        msgcat = getToolByName( folder, 'msg' )
        lang = msgcat.get_default_language()

        subject = message.get( 'subject', '', decode=True )
        if not subject.strip():
            subject = '(%s)' % msgcat.gettext( 'no subject', lang=lang )

        date = message.get( 'date', '', decode=True )
        try:
            date = DateTime( date )
            date = date.toZone( date.localZone() )
        except:
            date = DateTime()
        attributes['messageDate'] = date

        name = email = ''
        for header in ['from','reply-to','sender']:
            parsed = getaddresses( message.get_all( header, decode=True ) )
            if parsed:
                attributes['senderName']    = parsed[0][0]
                attributes['senderAddress'] = parsed[0][1]
                break

        #doc.setCategoryAttribute( 'messageHeaders', message.items( decode=True ) )

        for part in message.walk():
            if part.is_multipart():
                continue

            try:
                data  = part.get_payload( decode=True )
                ctype = part.get_content_type()
            except: # XXX which exceptions???
                data  = part.get_payload()
                ctype = Config.DefaultAttachmentType

            if not content and ctype in self.allowed_content_types:
                # TODO: support for multipart/alternative, multipart/related
                content = part
                text = data
                #LOG( 'MailFolder.documentFromMail', TRACE, 'text = %s' % text )

            else:
                fname = part.get_filename( decode=True )
                params = { 'title':fname, 'content_type':ctype }
                attachments.append( (data, params) )
                #LOG( 'MailFolder.documentFromMail', TRACE, 'attached %s = %s' % (ctype, fname) )

        if content:
            subtype = content.get_content_subtype()

            if subtype == 'html':
                # TODO: need better cleaner
                text = HTMLCleaner( text, None, 0, '', 'HEAD SCRIPT STYLE' )

            elif subtype == 'plain':
                text = formatPlainText( text, target='_blank' )
                subtype = 'html'

            langs = content.get( 'content-language', '', decode=True )
            langs = langs.replace( ',', ' ' ).split()
            if langs:
                lang = langs[0].lower()

        id = cookId( folder, prefix='mail' )

        folder.invokeFactory( type_name, id,
                              title=subject,
                              language=lang,
                              text_format=subtype,
                              text=text,
                              attachments=attachments,
                              category=category,
                              category_attributes=attributes,
                              restricted=Trust )

        return folder._getOb( id )


class MoveAction( DefaultAction ):

    def perform( self, folder=None, category=None, **kwargs ):
        """
        """
        if category is None:
            category = folder.mail_category

        folder = self.definition.getProperty('destination')

        return DefaultAction.perform( self, folder=folder, category=category, **kwargs )


class CopyAction( DefaultAction ):

    def perform( self, **kwargs ):
        """
        """
        doc = DefaultAction.perform( self, **kwargs )

        target = self.definition.getProperty('destination')

        copied = doc.copyObject( target )

        workflow = getToolByName( target, 'portal_workflow' )
        workflow.doActionFor( copied, 'receive' )

        return copied


class DeleteAction( ActionBase ):
    pass



def initialize( context ):
    # module initialization callback

    context.registerAction( 'mail_filter_default',
                            title="mail.filter_action.default",
                            category='mail_filter',
                            handler=DefaultAction )

    context.registerAction( 'mail_filter_move',
                            title="mail.filter_action.move",
                            category='mail_filter',
                            parameters=[
                                {'id':'destination','type':'link','allowed_types':['Heading']}
                            ],
                            handler=MoveAction )

    context.registerAction( 'mail_filter_copy',
                            title="mail.filter_action.copy",
                            category='mail_filter',
                            parameters=[
                                {'id':'destination','type':'link','allowed_types':['Heading']}
                            ],
                            handler=CopyAction )

    context.registerAction( 'mail_filter_delete',
                            title="mail.filter_action.delete",
                            category='mail_filter',
                            handler=DeleteAction )
