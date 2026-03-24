"""
$Id: update_task_definitions.py,v 1.2 2008/06/07 08:27:25 oevsegneev Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = "Update task definitions"
version = '3.4.0.1'

order = 75
before_script = 1

from Products.CMFCore.utils import getToolByName

def check( context, object ):
    metadata = getToolByName( object, 'portal_metadata' )
    cats = metadata.listCategories()
    for cat in cats:
        for template in cat.taskTemplateContainer.getTaskTemplates():
            for task_def in template.taskDefinitions:
                if task_def.type == 'set_category_attribute' and task_def.attribute_value == '{date_now}':
                    return True
    else:
        return False

def migrate( context, object ):
    metadata = getToolByName( object, 'portal_metadata' )
    cats = metadata.listCategories()
    for cat in cats:
        for template in cat.taskTemplateContainer.getTaskTemplates():
            for task_def in template.taskDefinitions:
                if task_def.type == 'set_category_attribute' and task_def.attribute_value == '{date_now}':
                    task_def.attribute_value = None

