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
Test suite for the zgettext.py script.
"""

__version__ = "$Revision: 1.4 $"


# Add the Localizer product directory to the path
import os, sys
sys.path.append(os.path.join(sys.path[0], '../'))

import zgettext



from unittest import TestCase, TestSuite, TextTestRunner


class SimpleGettextTagTestCase(TestCase):
    def runTest(self):
        """Test the 'dtml-gettext' tag without any option."""

        text = "<dtml-gettext>\n" \
               "  message\n" \
               "</dtml-gettext>"

        assert zgettext.parse_dtml(text) == ['message']


class VerbatimGettextTagTestCase(TestCase):
    def runTest(self):
        """Test the 'dtml-gettext' tag when using the 'verbatim' option."""

        text = "<dtml-gettext verbatim>\n" \
               "  message\n" \
               "</dtml-gettext>"

        assert zgettext.parse_dtml(text) == ['\n  message\n']



if __name__ == '__main__':

    # Build the test suite
    suite = TestSuite()
    suite.addTest(SimpleGettextTagTestCase())
    suite.addTest(VerbatimGettextTagTestCase())

    # Run the tests
    runner = TextTestRunner()
    runner.run(suite)

