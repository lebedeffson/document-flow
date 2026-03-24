###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
a stupid null converter

$Id: null.py,v 1.1.1.1 2004/09/20 12:10:01 vpastukhov Exp $
"""

from Products.TextIndexNG2.BaseConverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('text/plain',)
    content_description = "Null converter"

    def convert(self, doc):
        return doc
