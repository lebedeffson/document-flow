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
This module provides the MessageCatalog base class, which
provides message catalogs for the web.
"""
__version__ = "$Revision: 1.17 $"

# Python
import re, time
from types import StringType
from urllib import quote

# Zope
from Globals import  MessageDialog, PersistentMapping, InitializeClass, \
     get_request
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager

# Localizer
from LocalFiles import LocalDTMLFile
from zgettext import parse_po_file
from Utils import charsets, languages, lang_negotiator
from LanguageManager import LanguageManager
import Gettext


_ = Gettext.translation(globals())
N_ = Gettext.dummy



manage_addMessageCatalogForm = LocalDTMLFile('ui/MC_add', globals())
def manage_addMessageCatalog(self, id, title, languages, REQUEST=None):
    """ """
    self._setObject(id, MessageCatalog(id, title, languages))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


# Empty header information for PO files, the default
empty_po_header = {'last_translator_name': '',
                   'last_translator_email': '',
                   'language_team': '',
                   'charset': ''}



class MessageCatalog(LanguageManager, ObjectManager, SimpleItem):
    """
    Stores messages and their translations...
    """

    meta_type = 'MessageCatalog'

    security = ClassSecurityInfo()


    def manage_options(self):
        """ """
        options = (
            {'label': N_('Messages'), 'action': 'manage_messages',
             'help': ('Localizer', 'MC_messages.stx')},
            {'label': N_('Properties'), 'action': 'manage_propertiesForm'},
            {'label': N_('Import/Export'), 'action': 'manage_importExport',
             'help': ('Localizer', 'MC_importExport.stx')}) \
            + LanguageManager.manage_options \
            + SimpleItem.manage_options

        r = []
        for option in options:
            option = option.copy()
            option['label'] = _(option['label'])
            r.append(option)

        return r


    def __init__(self, id, title, languages):
        self.id = id

        self.title = title

        # Language Manager data
        self._languages = tuple(languages)
        self._default_language = languages[0]

        # Here the message translations are stored
        self._messages = PersistentMapping()

        # Data for the PO files headers
        self._po_headers = PersistentMapping()
        for lang in self._languages:
            self._po_headers[lang] = empty_po_header


    security.declareProtected('View management screens', 'manage_messages')
    manage_messages = LocalDTMLFile('ui/MC_messages', globals())

    security.declareProtected('View management screens', 'manage_message')
    manage_message = LocalDTMLFile('ui/MC_message', globals())


    security.declarePublic('get_language_name')
    def get_language_name(self, id):
        """ """
        return languages[id]

    security.declarePublic('get_url')
    def get_url(self, url, batch_start, batch_size, regex, lang, **kw):
        """ """
        params = []
        for key, value in kw.items():
            params.append('%s=%s' % (key, quote(value)))

        params.extend(['batch_start:int=%d' % batch_start,
                       'batch_size:int=%d' % batch_size,
                       'regex=%s' % quote(regex)])

        if lang:
            params.append('lang=%s' % lang)

        return url + '?' + '&amp;'.join(params)

    security.declarePublic('filter')
    def filter(self, regex='', batch_start=0, batch_size=20):
        """
        For the management interface, allows to filter the messages
        to show.
        """

        regex = regex.strip()

        try:
            regex = re.compile(regex)
        except:
            regex = re.compile('')

        r = [ x for x in self._messages.items() if regex.search(x[0]) ]
        r.sort()

        return {'entries': r[batch_start:batch_start+batch_size],
                'nentries': len(r)}

    security.declareProtected('Manage messages', 'get_translations')
    def get_translations(self, message):
        """ """
        return self._messages[message]


    security.declareProtected('Manage messages', 'manage_addLS')
    def manage_addLS(self, message, REQUEST=None, RESPONSE=None):
        """Adds a new message."""
        ## Add the string
        self._messages[message] = PersistentMapping()

        ## Warn if a Localizer in a parent directory already has the string
        localizer = self
        try:
            while 1:
                localizer = localizer.aq_parent.aq_parent.Localizer
                if localizer.hasLS(message):
                    return MessageDialog(
                        title="Warning",
                        message="Warning: text <em>%s</em> already defined in another Localizer" % message,
                        action="manage_messages?batch_start:int=%d&batch_size:int=%d" % (REQUEST.get('batch_start', 0), REQUEST.get('batch_size', 20)))
        except AttributeError:
            pass

        # All went fine
        if REQUEST is not None:
            RESPONSE.redirect(self.get_url(REQUEST.URL1 + '/manage_messages',
                                           REQUEST['batch_start'],
                                           REQUEST['batch_size'],
                                           REQUEST['regex'],
                                           REQUEST['lang']))


    security.declareProtected('Manage messages', 'manage_delMessages')
    def manage_delMessages(self, messages_del, REQUEST=None, RESPONSE=None):
        """Removes messages."""
        for message in messages_del:
            del self._messages[message]

        if REQUEST is not None:
            RESPONSE.redirect(self.get_url(REQUEST.URL1 + '/manage_messages',
                                           REQUEST['batch_start'],
                                           REQUEST['batch_size'],
                                           REQUEST['regex'],
                                           REQUEST['lang']))


    security.declareProtected('Manage messages', 'manage_changeMessages')
    def manage_changeMessages(self, messages, lang, REQUEST=None,
                              RESPONSE=None):
        """ """
        for i in range(0, len(messages), 2):
            message = messages[i]
            translation = messages[i+1]
            self._messages[message][lang] = translation

        if REQUEST is not None:
            RESPONSE.redirect(self.get_url(REQUEST.URL1 + '/manage_messages',
                                           REQUEST['batch_start'],
                                           REQUEST['batch_size'],
                                           REQUEST['regex'],
                                           lang))


    security.declareProtected('Manage messages', 'manage_editLS')
    def manage_editLS(self, ls, translations, REQUEST=None):
        """Modifies a message."""
        ls = self._messages[ls]
        for i in range(0, len(translations), 2):
            language = translations[i]
            translation = translations[i+1]
            ls[language] = translation

        if REQUEST is not None:
            return self.manage_message(self, REQUEST)


    # Looking for translations
    security.declarePublic('hasLS')
    def hasLS(self, message):
        """ """
        return self._messages.has_key(message)


    security.declarePublic('gettext')
    def gettext(self, message, lang=None, add=1):
        """Returns the message translation from the database if available."""
        # Add it if it's not in the dictionary
        if add and not self._messages.has_key(message):
            self._messages[message] = PersistentMapping()

        # Get the string
        if self._messages.has_key(message):
            m = self._messages[message]

            if lang is None:
                # Builds the list of available languages
                # should the empty translations be filtered?
                available_languages = list(self._languages)

                # Get the language!
                lang = lang_negotiator(available_languages)

                # Is it None? use the default
                if lang is None:
                    lang = self._default_language

            if lang is not None:
                return m.get(lang, None) or message

        return message

    __call__ = gettext


    # Properties management
    security.declareProtected('View management screens',
                              'manage_propertiesForm')
    manage_propertiesForm = LocalDTMLFile('ui/MC_properties', globals())

    security.declareProtected('View management screens', 'manage_properties')
    def manage_properties(self, title, REQUEST=None, RESPONSE=None):
        """Change the Message Catalog properties."""

        self.title = title

        if RESPONSE is not None:
            RESPONSE.redirect('manage_propertiesForm')


    # Properties management screen
    security.declareProtected('View management screens', 'get_po_header')
    def get_po_header(self, lang):
        """ """

        # For backwards compatibility
        if not hasattr(self.aq_base, '_po_headers'):
            self._po_headers = PersistentMapping()

        return self._po_headers.get(lang, empty_po_header)

    security.declareProtected('View management screens', 'update_po_header')
    def update_po_header(self, lang,
                         last_translator_name, last_translator_email,
                         language_team, charset,
                         REQUEST=None, RESPONSE=None):
        """ """

        self._po_headers[lang] = {'last_translator_name': last_translator_name,
                                  'last_translator_email': last_translator_email,
                                  'language_team': language_team,
                                  'charset': charset}

        if RESPONSE is not None:
            RESPONSE.redirect('manage_propertiesForm')


    # Import/export management screen
    security.declarePublic('get_charsets')
    def get_charsets(self):
        """ """
        return charsets[:]

    security.declareProtected('View management screens', 'manage_importExport')
    manage_importExport = LocalDTMLFile('ui/MC_importExport', globals())

    security.declarePublic('manage_export')
    def manage_export(self, x, REQUEST=None, RESPONSE=None):
        """
        Exports the content of the message catalog either to a template
        file (locale.pot) or to an language specific PO file (<x>.po).
        """

        # Get the PO header info
        header = self.get_po_header(x)
        last_translator_name = header['last_translator_name']
        last_translator_email = header['last_translator_email']
        language_team = header['language_team']
        charset = header['charset']

        # PO file header, empty message.
        po_revision_date = time.strftime('%Y-%m-%d %H:%m+%Z',
                                         time.gmtime(time.time()))
        pot_creation_date = po_revision_date
        last_translator = '%s <%s>' % (last_translator_name,
                                       last_translator_email)

        if x == 'locale.pot':
            language_team = 'LANGUAGE <LL@li.org>'
        else:
            language_team = '%s <%s>' % (x, language_team)

        r = ['msgid ""',
             'msgstr "Project-Id-Version: %s\\n"' % self.title,
             '"POT-Creation-Date: %s\\n"' % pot_creation_date,
             '"PO-Revision-Date: %s\\n"' % po_revision_date,
             '"Last-Translator: %s\\n"' % last_translator,
             '"Language-Team: %s\\n"' % language_team,
             '"MIME-Version: 1.0\\n"',
             '"Content-Type: text/plain; charset=%s\\n"' % charset,
             '"Content-Transfer-Encoding: 8bit\\n"',
             '', '']


        # Get the messages, and perhaps its translations.
        d = {}
        if x == 'locale.pot':
            filename = x
            for k in self._messages.keys():
                d[k] = ""
        else:
            filename = '%s.po' % x
            for k, v in self._messages.items():
                try:
                    d[k] = v[x]
                except KeyError:
                    d[k] = ""

        # Generate the file
        for k, v in d.items():
            r.append('msgid "%s"' % k)
            r.append('msgstr "%s"' % v)
            r.append('')


        if RESPONSE is not None:
            RESPONSE.setHeader('Content-type','application/data')
            RESPONSE.setHeader('Content-Disposition',
                               'inline;filename=%s' % filename)

        return '\n'.join(r)

    security.declareProtected('Manage messages', 'manage_import')
    def manage_import(self, lang, file, REQUEST=None):
        """ """
        messages = self._messages

        if type(file) is StringType:
            content = file.split('\n')
        else:
            content = file.readlines()

        k, k, k, d = parse_po_file(content)

        for k, v in d.items():
            k = k[0]
            if not messages.has_key(k):
                messages[k] = PersistentMapping()
            messages[k][lang] = v[1][0]

        if REQUEST is not None:
            return self.manage_messages(self, REQUEST)


    def objectItems(self, spec=None):
        """ """

        for lang in self._languages:
            if not hasattr(self.aq_base, lang):
                self._setObject(lang, POFile(lang))

        r = MessageCatalog.inheritedAttribute('objectItems')(self, spec)
        return r


    # Language stuff
    security.declarePublic('get_path_for_cookies')
    def get_path_for_cookies(self):
        """
        Returns the path that will be used to set the LOCALIZER_LANGUAGE
        cookie. Used from the LanguageManager.
        """

        return self.aq_parent.absolute_url()



class POFile(SimpleItem):
    """ """

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declareProtected('FTP access', 'manage_FTPget')
    def manage_FTPget(self):
        """ """

        return self.manage_export(self.id)

    security.declareProtected('Manage messages', 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ """

        body = REQUEST['BODY']
        self.manage_import(self.id, body)
        RESPONSE.setStatus(204)
        return RESPONSE


InitializeClass(MessageCatalog)
InitializeClass(POFile)
