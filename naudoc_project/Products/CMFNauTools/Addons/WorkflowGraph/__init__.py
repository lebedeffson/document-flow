# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/WorkflowGraph/__init__.py
# Compiled at: 2008-10-15 16:34:28
"""
$Editor: ikuleshov $
$Id: __init__.py,v 1.4 2008/10/15 12:34:28 oevsegneev Exp $
"""
__version__ = '$Revision: 1.4 $'[11:-2]
AddonId = 'WorkflowGraph'
AddonTitle = 'Workflow Graph'
AddonVersion = '1.1'
IsPaid = True
from pydot import Node, Edge, Dot
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import AddonError, AddonDeactivateError
from Products.CMFNauTools.CategoryDefinition import CategoryDefinition
from Products.CMFNauTools.Utils import InitializeClass, getObjectByUid, getLanguageInfo, recode_string, translate, uniqueValues, isBroken

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True, is_paid=IsPaid)
    registerDirectory('skin', globals())
    CategoryDefinition.listDFActions = listDFActions
    CategoryDefinition.getGraph = getGraph
    return


def activate(portal):
    portal_sentinel = getToolByName(portal, 'portal_sentinel')
    if not portal_sentinel.checkActivation(AddonId):
        return False
    skins = getToolByName(portal, 'portal_skins')
    skins.addSkinLayer('graph', 'skin', globals(), before='categories')
    portal.addLocalizerMessages(globals())
    return True
    return


def deactivate(portal):
    skins = getToolByName(portal, 'portal_skins')
    skins.deleteSkinLayer('graph')
    return


def listDFActions(self):
    """
        Returns the list of docflow actions created within the category definition.
    """
    return self.taskTemplateContainer.getTaskTemplates()
    return


def getGraph(self, fmt='png', transition=None, state=None):
    """
    """
    portal_sentinel = getToolByName(self, 'portal_sentinel')
    if not portal_sentinel.checkAction(AddonId):
        msg = getToolByName(self, 'msg')
        return msg('sentinel.trial_expired') % msg(AddonTitle)
    wf = self.getWorkflow()
    if wf is None:
        return
    graph = Dot(type='digraph', label=cook_label(self, self.Title(), fmt), labelloc='top')
    states = []
    if wf.initial_state:
        states.append(wf.states.get(wf.initial_state))
    states.extend([sdef for sdef in wf.states.objectValues() if sdef.getId() != wf.initial_state])
    for sdef in states:
        shape = 'box'
        if sdef.getId() == wf.initial_state:
            fillcolor = 'hotpink'
            shape = 'diamond'
        elif not sdef.transitions:
            fillcolor = 'lightgray'
        else:
            fillcolor = 'lightblue'
        if state and state == sdef.getId():
            peripheries = 2
        else:
            peripheries = 1
        url = self.absolute_url(action='state_properties', params={'state': (sdef.getId())})
        label = cook_label(self, sdef.title, fmt)
        node = Node(name=sdef.getId(), label=label, URL=url, shape=shape, style='filled', fontname='Arial', fontsize='9', fillcolor=fillcolor, target='workspace', peripheries=peripheries)
        graph.add_node(node)
        for tid in sdef.transitions:
            tdef = wf.transitions.get(tid)
            if tdef is None:
                continue
            transition_src = sdef.getId()
            transition_dst = tdef.new_state_id
            if not transition_dst:
                transition_dst = transition_src
            if transition and transition == tdef.getId():
                style = 'bold'
            else:
                style = 'solid'
            label = cook_label(self, tdef.actbox_name or tdef.title, fmt)
            edge = Edge(src=transition_src, dst=transition_dst, name=tdef.getId(), label=label, href=self.absolute_url(action='transition_properties', params={'transition': (tdef.getId())}), fontname='Arial', fontsize='8', target='workspace', style=style)
            graph.add_edge(edge)

    result = graph.create(format=fmt, prog='dot')
    if fmt == 'cmap':
        membership = getToolByName(self, 'portal_membership')
        lang = getLanguageInfo(self)
        python_charset = lang['python_charset']
        return recode_string(result, enc_from='utf-8', enc_to=python_charset)
    return result
    return


def cook_label(context, text, fmt):
    text = translate(context, text)
    membership = getToolByName(context, 'portal_membership')
    lang = getLanguageInfo(context)
    python_charset = lang['python_charset']
    return recode_string(text, enc_from=python_charset, enc_to='utf-8')
    return
