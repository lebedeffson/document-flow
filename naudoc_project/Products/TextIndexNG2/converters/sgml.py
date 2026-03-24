###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
A stupid HTML to Ascii converter

$Id: sgml.py,v 1.1.1.1 2004/09/20 12:10:01 vpastukhov Exp $
"""

from types import StringType
from Products.TextIndexNG2.BaseConverter import BaseConverter
from StripTagParser import StripTagParser

class Converter(BaseConverter):

    content_type = ('text/sgml',)
    content_description = "Converter SGML to ASCII"

    def convert(self, doc):
        """Convert html data to raw text"""

        p = StripTagParser()
        p.feed(doc)
        p.close()

        return str(p)
