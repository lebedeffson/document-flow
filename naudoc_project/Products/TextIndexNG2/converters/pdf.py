###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
pdf converter

$Id: pdf.py,v 1.1.1.1 2004/09/20 12:10:01 vpastukhov Exp $
"""


from Products.TextIndexNG2.BaseConverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('application/pdf',)
    content_description = "Adobe Acrobat PDF"
    depends_on = 'pdftotext'

    def convert(self,doc):
        """Convert pdf data to raw text"""

        tmp_name = self.saveFile(doc)
        return self.execute('pdftotext %s -' % tmp_name)
