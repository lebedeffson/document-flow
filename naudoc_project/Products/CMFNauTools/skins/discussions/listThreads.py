## Script (Python) "listThreads"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=show=None,filter=None,filter_ver=None,parent_reply=None
##
# $Editor: oevsegneev $
# $Id: listThreads.py,v 1.3 2004/03/22 16:42:56 ikuleshov Exp $
# $Revision: 1.3 $

def getAllReplies(parent_rep):
    replies = context.branches(show=show, filter=filter, filter_ver=filter_ver, parent_reply=parent_rep)
    for rep in replies[:]:
        replies.extend(getAllReplies(rep.talkback))
    return replies

return getAllReplies(context.implements('isVersion') and context.getVersionable().talkback or context.talkback)
