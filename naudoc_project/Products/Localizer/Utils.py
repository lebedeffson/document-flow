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
Localizer..
"""


from Globals import package_home, get_request


# Package home
ph = package_home(globals())

# Initializes a dictionary containing the iso 639 language codes/names
languages = {}
for line in open(ph + '/languages.txt').readlines():
    line = line.strip()
    if line and line[0] != '#':
        code, name = line.split(' ', 1)
        languages[code] = name

# Initializes a list with the charsets
charsets = [ x.strip() for x in open(ph + '/charsets.txt').readlines() ]



# Language negotiation
def lang_negotiator(available_languages):

    """
    Recives two ordered lists, the list of user prefered languages
    and the list of available languages. Returns the first user pref.
    language that is available, if none is available returns None.
    """

    request = get_request()

    lang = request.USER_PREF_LANGUAGES.select_language(available_languages)


    # Here we should set the Vary header, but, which value should it have??
##    response = request.RESPONSE
##    response.setHeader('Vary', 'accept-language')
##    response.setHeader('Vary', '*')

    return lang
