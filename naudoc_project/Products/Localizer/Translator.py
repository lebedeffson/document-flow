# Localizer, Zope product that provides internationalization services
# Copyright (C) 2000, 2001  Juan David Ibáñez Palomar <palomar@sg.uji.es>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
Translator
"""
__version__ = "$Revision: 1.6 $"


from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem

from Products.UserBag.BasicProfile import Profile

from LocalFiles import LocalDTMLFile


manage_addTranslatorForm = LocalDTMLFile('ui/TranslatorAdd', globals())
def manage_addTranslator(self, REQUEST=None):
    """ """
    id = 'translator'
    self._setObject(id, Translator(id))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class Translator(Profile, PropertyManager, SimpleItem):
    """Profile for human translators"""

    meta_type = 'Translator'

    def __init__(self, id):
        self.id = id

    def manage_afterAdd(self, item, container):
        localizer = container.Localizer
        localizer.manage_setLocalRoles(container.id, ['Translator'])
        Profile.manage_afterAdd.im_func(self, item, container)

    def manage_beforeDelete(self, item, container):
        localizer = container.Localizer
        localizer.manage_delLocalRoles([container.id])
        Profile.manage_beforeDelete.im_func(self, item, container)


    manage_profile__roles__ = ('Manager', 'Owner')
    manage_profile = LocalDTMLFile('ui/manageContentUI', globals())


    ## Naviagator interface
    def anchor(self, what='menu'):
        if what == 'main':
            return 'manage_profile'

        return []
