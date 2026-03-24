## Script (Python) "unpublish_all"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# $Id: unpublish_all.py,v 1.4 2005/05/14 05:43:50 vsafronovich Exp $

request  = container.REQUEST
RESPONSE = request.RESPONSE

results = context.portal_catalog.searchResults(meta_type='HTMLDocument'
                                              ,path=context.physical_path()
                                              )

print 'Starting unpublishing inside ' + context.physical_path() + '\n'

for item in results:
    obj = item.getObject()
    if context.portal_workflow.getInfoFor(obj, 'state', '')=='published':
        context.portal_workflow.doActionFor( obj, 'retract', comment='Automatically unpublished' )
        print obj.physical_path() + '\n'

print 'finished\n'

return printed
