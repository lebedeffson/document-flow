# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/SiteObject/CategoryAttribute.py
# Compiled at: 2008-06-07 13:21:49
"""
CategoryAttribute patch class.

$Editor: oevsegneev $
$Id: CategoryAttribute.py,v 1.1 2008/06/07 09:21:49 oevsegneev Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
import Products.CMFNauTools.Exceptions
from Products.CMFNauTools.CategoryAttribute import CategoryAttribute, _field_template_infos, _field_template_methods
from utils import class_patch

class CategoryAttribute_patch(class_patch):
    __module__ = __name__

    def getViewFor(self, object, template_type='view', is_empty=False):
        try:
            info = _field_template_infos[template_type]
            method = _field_template_methods[template_type]
        except KeyError:
            raise ValueError("'%s' -- unknown template type" % template_type)

        if is_empty:
            value = ''
        else:
            value = self.getValueFor(object, moniker=True)
        return getattr(self, method)(object, None, value=value, **self.getFieldDescriptor(**info))
        return


def initialize(context):
    CategoryAttribute_patch(CategoryAttribute)
    context.registerFieldTemplate('external_edit', 'entry_field_external_edit')
    return
