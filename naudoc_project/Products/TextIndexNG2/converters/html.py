###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
a stupid HTML to Ascii converter

$Id: html.py,v 1.1.1.1 2004/09/20 12:10:01 vpastukhov Exp $
"""

from types import StringType
from Products.TextIndexNG2.BaseConverter import BaseConverter
from stripogram import html2text

class Converter(BaseConverter):

    content_type = ('text/html',)
    content_description = "Converter HTML to ASCII"

    def convert(self, html):
        """Convert html data to raw text"""
        
        return html2text(html,
                         ignore_tags=('img',),
                         indent_width=4,
                         page_width=80)

        
