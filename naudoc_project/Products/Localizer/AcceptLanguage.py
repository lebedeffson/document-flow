# Localizer, Zope product that provides internationalization services
# Copyright (C) 2001 Andres Marzal Varo
#                    J. David Ibáñez <palomar@sg.uji.es>

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
Zope independent language negotiation stuff.
"""

#from UserDict import UserDict
from types import StringType


class AcceptLanguageNode:
    """
    This class is a recursive representation of a tree.

    To implement the tree behaviour the 'children' attribute is used,
    it's a mapping object, the value is another AcceptLanguageNode.

    This class also stores the quality of the node, if its value is None,
    it means that the quality is the maximum of the qualities of their
    children.

    This class provides a simplified mapping interface.
    """

    def __init__(self):
        self.quality = None
        self.children = {}

    def __setitem__(self, lang, quality):
        """
        Inserts a new language in the tree. Receives two parameters, the
        language to insert as a sequence of strings, and the quality.
        """

        if type(lang) == StringType:
            lang = lang.split('-')

        if len(lang) == 0:
            self.quality = quality
        else:
            al = self.children.setdefault(lang[0], AcceptLanguageNode())
            lang = lang[1:]
            al[lang] = quality


    def __getitem__(self, key):
        """Traverses the tree to get the object."""

        key = key.split('-', 1)
        x = key[0]

        try:
            y = key[1]
        except IndexError:
            return self.children[x]
        else:
            return self.children[x][y]


    def get_quality(self):
        """ """

        if self.quality is None:
            return max([ x.get_quality() for x in self.children.values() ])

        return self.quality




class AcceptLanguage(AcceptLanguageNode):
    def __init__(self, accept_language):
        """
        Initialize from a string with the format of the Accept-Language
        header of the HTTP protocol version 1.1, as documented in the
        RFC 2068.
        """

        AcceptLanguageNode.__init__(self)

        self.quality = 0.0

        for lang in accept_language.split(','):
            lang = lang.strip()
            lang = lang.split(';')

            # Get the quality
            if len(lang) == 2:
                quality = lang[1]         # Get the quality
                quality = quality[2:]     # Get the number (remove "q=")
                quality = float(quality)  # Change it to float
            else:
                quality = 1.0

            # Get the lang
            lang = lang[0]
            if lang == '*':
                lang = []
            else:
                lang = lang.split('-')

            self[lang] = quality



    def select_language(self, languages):
        """
        This is the selection language algorithm, it returns the user
        prefered language for the given list of available languages,
        if the intersection is void returns None.
        """

        language, quality = None, 0.0

        for lang in languages:
            try:
                x = self[lang]
            except KeyError:
                continue

            q = x.get_quality()
            if q > quality:
                language, quality = lang, q

        return language
