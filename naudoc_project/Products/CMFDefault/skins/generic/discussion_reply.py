## Script (Python) "discussion_reply"
##parameters=title,text
##title=Reply to content
from Products.CMFCore.utils import getToolByName
pm = getToolByName(context, 'portal_membership')
Creator = pm.getAuthenticatedMember().getId()
replyID = context.createReply( title = title
                             , text = text
                             , Creator = Creator
                             )

target = '%s/%s' % (context.absolute_url(), replyID)

context.REQUEST.RESPONSE.redirect(target)
