## Script (Python) "branches"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=show=None,filter=None,filter_ver=None,parent_reply=None
##
# $Editor: oevsegneev $
# $Id: branches.py,v 1.6 2005/05/14 05:43:49 vsafronovich Exp $
# $Revision: 1.6 $

if not parent_reply:
    parent_reply = context.implements('isVersion') and context.getVersionable().talkback or context.talkback

reps = parent_reply.getReplies()

if filter:
    #filter by date
    if show=='all':
        return [ reply for reply in reps if DateTime(reply.CreationDate()) > DateTime(filter) ]
    elif show=='hide':
        return [ reply for reply in reps if DateTime(reply.CreationDate()) > DateTime(filter) and reply.status in (1,2) ]
elif filter_ver and not hasattr(context,'parentsInThread'):
    #filter by version
    if filter_ver!='all':
        if show=='all':
            return [ reply for reply in reps if reply.doc_ver == filter_ver ]
        elif show=='hide':
            return [ reply for reply in reps if reply.doc_ver == filter_ver and reply.status in (1,2)]
    else:
        if show=='all':
            return reps
        elif show=='hide':
            return [ reply for reply in reps if reply.status in (1,2)]

elif show=='hide':
    #Hide closed and dismissed comments
    return [ reply for reply in reps if reply.status in (1,2) ]

else:
    #Show all comments or not a bug track mode
    return reps
