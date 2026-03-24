## Script (Python) "discussion_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, title,text,Creator, version=None, fullname=None, email=None, status=1, last_comment=1
##title=Reply to content
##
# $Editor: oevsegneev $
# $Id: discussion_reply.py,v 1.14 2007/10/04 08:34:05 ynovokreschenov Exp $
# $Revision: 1.14 $

from Products.CMFCore.utils import getToolByName

doc_ver = context.REQUEST['SESSION'].get('doc_ver')

replyID = context.createReply( title = title
                             , text = text
                             , Creator = Creator
                             , version = doc_ver
                             , email = email
                             )

reply = context.getReply( replyID )

try:
    reply.setContributors( fullname )
except:
    pass

context.REQUEST.RESPONSE.setCookie('fullname', fullname, path='/', expires='Wed, 19 Feb 2020 14:28:00 GMT')

#if version and not hasattr(reply.inReplyTo(), 'talkback'):

if email:
    context.REQUEST.RESPONSE.setCookie('email', email, path='/', expires='Wed, 19 Feb 2020 14:28:00 GMT')

#reply.manage_addProperty('status', status, 'int')

#if len(reply.parentsInThread())==1:
#   reply.manage_addProperty('number', last_comment, 'int')
#   for par in reply.parentsInThread():
#       par.manage_changeProperties( {'last_comment': last_comment+1} )
#       break
#   reply.manage_addProperty('mod_time', reply.bobobase_modification_time(), 'date')

#if len(reply.parentsInThread())>1:
#   c=1
#   for par in reply.parentsInThread():
#       if c==2:
#          par.manage_changeProperties( {'mod_time': par.bobobase_modification_time()} )
#          break
#       c=c+1

lang = REQUEST.get('LOCALIZER_LANGUAGE')
mailhost = context.MailHost
links = context.portal_links
membership = context.portal_membership

#comment_link = links.absolute_url( action='locate', params={'uid':reply.getUid()}, canonical=1 )
comment_link = links.absolute_url( action='locate', params={'uid':context.aq_parent.getUid(),'action':'document_comments'}, canonical=1 )

comment_title = context.Title()
comment_autor = membership.getMemberName(reply.Creator())
users=[]
for rep in reply.parentsInThread():
    if hasattr(rep, 'Creator') and users.count(rep.Creator())==0:
        users.append(rep.Creator())

try:
    mailhost.sendTemplate( template='discussion.notify_user'
                         , mto=users
                         , mfrom=reply.Creator()
                         , lang=lang
                         , comment_autor=comment_autor
                         , comment_text=text
                         , comment_link=comment_link
                         , comment_title=comment_title
                         , doc_title=context.aq_parent.Title()
                         )
except:
    pass

if hasattr(context, 'inReplyTo')==0:
    context.REQUEST.RESPONSE.redirect(context.aq_parent.absolute_url(action='document_comments', frame='inFrame'))

else:
    context.REQUEST.RESPONSE.redirect(context.aq_parent.absolute_url())
