## Script (Python) "task_delete.py"
##parameters=ids=[],showTaskMode='showCurrent'
##title=Delete tasks

from Products.CMFNauTools.SecureImports import SimpleError, refreshClientFrame
from Products.CMFCore.utils import getToolByName

catalog = getToolByName( context, 'portal_catalog' )

params = {'showTaskMode':showTaskMode}
if ids:
    for id in ids:
        task = catalog.getObjectByUid( id )
        if task is not None:
            task.deleteObject()
        else:
            raise SimpleError('Task not found')

    refreshClientFrame( 'followup_menu' )
    context.redirect( params=params )
else:
    context.redirect( params=params, message='Specify task')

