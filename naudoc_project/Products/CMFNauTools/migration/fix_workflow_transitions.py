"""
$Id: fix_workflow_transitions.py,v 1.7 2005/05/14 05:43:46 vsafronovich Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.7 $'[11:-2]

title = 'Fix workflow transitions'
version = '3.1.5.53'
classes = ['Products.DCWorkflow.Transitions.TransitionDefinition']

import re
from Products.CMFNauTools.SimpleObjects import ExpressionWrapper

_expr = re.compile('(?:here.isInCategory\(.*?\)|here.Category\(\) == .*?)(?: and |$)')

deprecated_exprs = [ "python: object.implements('isVersionable') and object.denyVersionEdit()",
                     "python: object.implements('isVersionable') and object.activateCurrentVersion()",
                     "python: object.implements('isVersionable') and object.allowVersionEdit()",
                   ]

def update_scripts( context, object, check=False ):
    wf = object.getWorkflow()
    if object.script_name:
        script = getattr( wf.scripts, object.script_name, None )
        if not script or isinstance( script, ExpressionWrapper ) and script.expr.text in deprecated_exprs:
            if check:
                return True
            object.script_name = None


def check(context, object):
    if not object.getWorkflow():
        return False
    if update_scripts( context, object, True ):
        return True

    guard = object.guard
    return guard and guard.expr and _expr.search(guard.expr.text)

def migrate(context, object):
    update_scripts( context, object )

    expr_text = object.guard.expr.text
    fixed_expr = _expr.sub('', expr_text)

    if fixed_expr.strip() == 'python:':
        del object.guard.expr
    else:
        object.guard.expr.text = fixed_expr
