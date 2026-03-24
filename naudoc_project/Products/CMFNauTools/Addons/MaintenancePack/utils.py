# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/MaintenancePack/utils.py
# Compiled at: 2009-02-17 18:04:21
"""
Addon utils.

$Editor: oevsegneev $
$Id: utils.py,v 1.1 2009/02/17 15:04:21 oevsegneev Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFNauTools.ActionInformation import ActionInformation as AI

def safe_apply(object, name, *args):
    """
        Tries to get method of object by given *name* and call it.
    """
    func = getattr(object, name, None)
    if not callable(func):
        return
    return func(*args)
    return


class class_patch:
    __module__ = __name__

    def __init__(self, klass, backup=True):
        """
            Patches given *class* with attributes of its own.
        """
        patch = self.__class__.__dict__
        for (name, attr) in patch.items():
            if name in ('__doc__', '__module__'):
                continue
            if name is '__init_patch__':
                name = '__init__'
            if backup and hasattr(klass, name):
                setattr(klass, 'old_%s' % name, getattr(klass, name))
            setattr(klass, name, attr)

        return


def registerAction(container, **kw):
    _action = AI(id=kw['id'], title=kw['title'], description=kw['description'], action=kw.get('action') or Expression(text='string: ${portal_url}/' + kw['form']), permissions=kw.get('permissions', (CMFCorePermissions.ManagePortal,)), category=kw['category'], visible=kw.get('visible', True))
    actions = list(container._actions)
    actions.append(_action)
    container._actions = tuple(actions)
    return


def unregisterAction(container, id):
    container._actions = tuple([_[1] for action in container._actions if action.id != id])
    return
