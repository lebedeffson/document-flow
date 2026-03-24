## Script (Python) "aboveInThread"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=top_action='view'
##title=Discussion parent breadcrumbs
##
# $Editor: oevsegneev $
# $Id: aboveInThread.py,v 1.15 2005/10/10 10:31:23 vsafronovich Exp $
# $Revision: 1.15 $

breadcrumbs = ''

if hasattr(context, 'parentsInThread'):
    parents = context.parentsInThread()
else:
    parents = None

if parents:
    for parent in parents:
        if parent.implements('isTaskItem') and not parent.validate():
            continue
        if not context.portal_membership.checkPermission('View', parent):
            continue
        p_str = '<a target="workfield" href="%s">%s</a> - ' \
                   % ( parent.absolute_url(action=breadcrumbs and 'view' or top_action) 
                     , parent.title_or_id()
                     )
        breadcrumbs = breadcrumbs + p_str

breadcrumbs = breadcrumbs + context.title_or_id()
        
return breadcrumbs
