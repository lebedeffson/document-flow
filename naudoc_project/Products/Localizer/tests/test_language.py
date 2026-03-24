# Localizer, Zope product that provides internationalization services
# Copyright (C) 2001, 2002 J. David Ibáñez <jdavid@nuxeo.com>

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
Test suite for the language negotiation stuff.
"""

__version__ = "$Revision: 1.3 $"



# Python unit test
import unittest
from unittest import TestCase


# Add the Localizer product directory to the path
import os, sys
sys.path.append(os.path.join(sys.path[0], '../'))

# Localizer modules
from AcceptLanguage import AcceptLanguage



class QualityAcceptLanguageTestCase(TestCase):
    def setUp(self):
        self.al = AcceptLanguage("da, en-gb;q=0.8")

    def test_special1(self):
        assert self.al.get_quality() == 0.0

    def test_special2(self):
        al = AcceptLanguage("da, en-gb;q=0.8, *;q=0.2")
        assert al.get_quality() == 0.2

    def test_da(self):
        assert self.al['da'].get_quality() == 1.0

    def test_en_gb(self):
        assert self.al['en-gb'].get_quality() == 0.8

    def test_en(self):
        assert self.al['en'].get_quality() == 0.8


class SelectLanguageAcceptLanguageTestCase(TestCase):
    def setUp(self):
        self.al = AcceptLanguage("da, en-gb;q=0.8")

    def testNone(self):
        """When none of the languages is acceptable."""

        assert self.al.select_language(['en-us', 'es']) == None

    def testImplicit(self):
        """When the prefered language is not explictly set."""

        assert self.al.select_language(['en-us', 'en']) == 'en'

    def testSeveral(self):
        """When there're several accepted languages."""

        assert self.al.select_language(['en-us', 'en', 'da']) == 'da'


class ChangeAcceptLanguageTestCase(TestCase):
    def setUp(self):
        self.al = AcceptLanguage("da, en-gb;q=0.8")

    def testChange(self):
        al = AcceptLanguage("da, en-gb;q=0.8")
        al['es'] = 5.0

        assert al['es'].get_quality() == 5.0
        



if __name__ == '__main__':

    unittest.main()
