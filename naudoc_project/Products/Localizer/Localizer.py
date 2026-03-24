# Localizer, Zope product that provides internationalization services
# Copyright (C) 2000-2002  Juan David Ibáñez Palomar <jdavid@nuxeo.com>

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
Localizer
"""
__version__ = "$Revision: 1.53 $"


# Zope
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile, InitializeClass, MessageDialog
from OFS.Folder import Folder
from ZPublisher.BeforeTraverse import registerBeforeTraverse, \
     unregisterBeforeTraverse, queryBeforeTraverse, NameCaller
##from zLOG import LOG, ERROR, INFO, PROBLEM

# Localizer
from LocalFiles import LocalDTMLFile
from MessageCatalog import MessageCatalog
from Utils import languages, lang_negotiator
from LanguageManager import LanguageManager
import Gettext


_ = Gettext.translation(globals())
N_ = Gettext.dummy



# Constructors
manage_addLocalizerForm = LocalDTMLFile('ui/Localizer_add', globals())
def manage_addLocalizer(self, title, languages, locale_folders=0,
                        REQUEST=None):
    """
    Add a new Localizer instance.
    """

    id = 'Localizer'
    localizer = Localizer(title, languages)
    localizer._v_hook = locale_folders
    self._setObject(id, localizer)

    localizer = getattr(self, 'Localizer')

    # Add the locale folders
    for lang in languages:
        getattr(self, id).manage_addLocaleFolder(lang)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class Localizer(LanguageManager, Folder):
    meta_type = 'Localizer'

    id = 'Localizer'

    meta_types = ({'name':'Locale Folder',
                   'action':'manage_addLocaleFolderForm'},)

    security = ClassSecurityInfo()

    def manage_options(self):
        """The manage options are defined here so they can be translated"""

        if self.need_upgrade():
            options = ({'label': 'Upgrade', 'action': 'manage_upgradeForm',
                        'help': ('Localizer', 'Localizer_upgrade.stx')},)
        else:
            options = ()

        options = options \
                  + (Folder.manage_options[0],
                     {'label': N_('Locale folders'),
                      'action':'manage_hookForm'}) \
                  + LanguageManager.manage_options \
                  + Folder.manage_options[1:]
##                  + ({'label': 'Localized Content',
##                      'action': 'manage_ContentUI'}) \

        r = []
        for option in options:
            option = option.copy()
            option['label'] = _(option['label'])
            r.append(option)

        return r

    def __init__(self, title, languages):
        self.title = title

        self._languages = languages
        self._default_language = languages[0]


    # Hook/unhook the traversal machinery
    # Support for copy, cut and paste operations
    def manage_beforeDelete(self, item, container):
        if item is self:
            self._v_hook = queryBeforeTraverse(container, self.meta_type)
            unregisterBeforeTraverse(container, self.meta_type)

    def manage_afterAdd(self, item, container):
        if item is self:
            if self._v_hook:
                id = self.id

                container = container.this()
                hook = NameCaller(id)
                registerBeforeTraverse(container, hook, self.meta_type)

    def _getCopy(self, container):
        ob = Localizer.inheritedAttribute('_getCopy')(self, container)
        ob._v_hook = queryBeforeTraverse(container, self.meta_type)
        return ob

    # Fix this! a new permission needed?
    security.declareProtected('Add Folders',
                              'manage_addLocaleFolderForm',
                              'manage_addLocaleFolder')
    manage_addLocaleFolderForm = LocalDTMLFile('ui/LF_add', globals())
    def manage_addLocaleFolder(self, id, title='', REQUEST=None):
        """ """
        self.manage_addFolder(id, title)
        f = getattr(self, id)
        f.manage_addSiteRoot('', '', '')

        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

    # Get some data
    security.declarePublic('get_supported_languages')
    def get_supported_languages(self):
        """
        Get the supported languages, that is the languages that the
        are being working so the site is or will provide to the public.
        """
        return self._languages

    security.declarePublic('get_selected_language')
    def get_selected_language(self):
        """ """
        return lang_negotiator(self._languages) \
               or self._default_language


    # Hooking the traversal machinery
    # Fix this! a new permission needed?
    security.declareProtected('View management screens', 'manage_hookForm')
    manage_hookForm = LocalDTMLFile('ui/Localizer_hook', globals())
    security.declareProtected('Manage properties', 'manage_hook')
    def manage_hook(self, hook=0, REQUEST=None, RESPONSE=None):
        """ """
        if hook != self.hooked():
            if hook:
                hook = NameCaller(self.id)
                registerBeforeTraverse(self.aq_parent, hook, self.meta_type)
            else:
                unregisterBeforeTraverse(self.aq_parent, self.meta_type)

        if REQUEST is not None:
            RESPONSE.redirect('manage_hookForm')

    security.declarePublic('hooked')
    def hooked(self):
        """ """
        if queryBeforeTraverse(self.aq_parent, self.meta_type):
            return 1
        return 0

    def __call__(self, container, REQUEST):
        """Hooks the traversal path."""

        stack = REQUEST['TraversalRequestNameStack']

        # Get the language
        lang = self.get_selected_language()
        if stack and (stack[-1] in self._languages):
            lang = stack.pop()
            # Add to the list of prefered languages
            REQUEST['USER_PREF_LANGUAGES'][lang] = 4.0

        # The condition is for backawards compatibility with versions < 0.6
        # Backwards compatibility code, it will be removed in 0.9
        if self.getProperty('hook_traversal', 1):
            path = '/'.join(container.getPhysicalPath()) + '/'

            # Back door to the management interfaces
            if stack and stack[-1]=='Z':
                stack.pop()
                REQUEST.setVirtualRoot(path[1:] + 'Z')
                return

            # Set a REQUEST variable
            REQUEST.set('SELECTED_LANGUAGE', lang)

            # The magic is here
            REQUEST.set('SiteRootPATH', path)
            stack.append(lang)
            stack.append(self.id)


##    # Changing the language, useful snippets
##    security.declarePublic('changeLanguage')
##    changeLanguageForm = LocalDTMLFile('ui/changeLanguageForm', globals())
##    def changeLanguage(self, REQUEST, RESPONSE):
##        """ """
##        lang = REQUEST['lang']

##        path = self.absolute_url()[len(REQUEST['SERVER_URL']):] or '/'
##        RESPONSE.setCookie('LOCALIZER_LANGUAGE', lang, path=path)

##        RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    # Upgrading..
    security.declarePublic('need_upgrade')
    def need_upgrade(self):
        """ """

        return hasattr(self.aq_base, 'localized_strings')

    security.declareProtected('Manage Access Rules', 'manage_upgradeForm',
                              'manage_upgrade')
    manage_upgradeForm = LocalDTMLFile('ui/Localizer_upgrade', globals())
    def manage_upgrade(self, REQUEST=None, RESPONSE=None):
        """ """

        # Upgrade to 0.7
        if hasattr(self.aq_base, 'localized_strings'):
            id = 'Messages'
            self._setObject(id,
                            MessageCatalog(id, '', self.supported_languages))

            message_catalog = self.Messages
            message_catalog._messages = self.localized_strings
            message_catalog._default_language = self.default_language

            del self.localized_strings

            #
            self._languages = tuple(self.supported_languages)
            self._default_language = self.default_language

            delattr(self, 'default_language')
            delattr(self, 'available_languages')
            delattr(self, 'supported_languages')

            if hasattr(self.aq_base, 'hook_traversal'):
                if self.hook_traversal:
                    hook = 1
                else:
                    hook = 0
                self.manage_hook(hook)
                delattr(self, 'hook_traversal')


        if REQUEST is not None:
            RESPONSE.redirect('manage_main')


##    def __setstate__(self, state):
##        """Used for upgrading."""
##        Localizer.inheritedAttribute('__setstate__')(self, state)

##        # It's not possible to upgrade automatically because self
##        # is not wrapped.
##        if self.hasProperty('hook_traversal'):
##            LOG(self.meta_type, PROBLEM, 'object needs to be upgraded.')


    # UI to manage Content objects from the Content product.
    # Perhaps the Content and Localizer products should be merged
##    manage_ContentUI = LocalDTMLFile('ui/manageContentUI', globals())

##    def get_content(self, batch_start=0, batch_size=100, lang='', status=0):
##        """Returns a lot of Content objects."""

##        d = {'meta_type': 'Content',
##             'size': 1, 'size_usage': 'range:min'}
##        if lang:
##            d['revision'] = '%s0' % lang
##        if status:
##            d['status'] = status

##        r = apply(self.Catalog, (), d)

##        return {'content' : r[batch_start:batch_start + batch_size],
##                'nentries': len(r)}

InitializeClass(Localizer)
