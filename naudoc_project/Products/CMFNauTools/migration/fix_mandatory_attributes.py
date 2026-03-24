"""
$Id: fix_mandatory_attributes.py,v 1.1 2006/03/29 13:21:43 ypetrov Exp $
$Editor: $
"""
__version__ = '$Revision: 1.1 $'[11:-2]

title = 'Fix state mandatory attributes'
classes = ['Products.CMFNauTools.WorkflowTool.StateDefinition']
version = '3.3.1.2'

from Products.CMFCore.utils import getToolByName

def _invalid_links(context, state):
    links  = getToolByName(context.portal, 'portal_links')
    states = context.parents[-3][1]
    state  = state.__of__(states)

    return links.searchLinks(source = state, relation = 'property')

def check(context, object):
    return bool(_invalid_links(context, object))

def migrate(context, object):
    links = getToolByName(context.portal, 'portal_links')

    for brain in _invalid_links(context, object):
        link = brain.getObject()
        source = link.getSourceObject()
        target = link.getTargetObject()

        links.removeLink(link, source, restricted = Trust)
        links.createLink(source, target, 'reference', restricted = Trust)
