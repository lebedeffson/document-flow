###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
a simple OpenOffice converter 

$Id: ooffice.py,v 1.1.1.1 2004/09/20 12:10:01 vpastukhov Exp $
"""

import xml.sax
import sys, zipfile, cStringIO
from xml.sax.handler import ContentHandler

from Products.TextIndexNG2.BaseConverter import BaseConverter


class ootextHandler(ContentHandler):

    def characters(self, ch):
        self._data.write(ch.encode("Latin-1") + ' ')

    def startDocument(self):
        self._data = cStringIO.StringIO()

    def getxmlcontent(self, doc):

        file = cStringIO.StringIO(doc)

        doctype = """<!DOCTYPE office:document-content PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">"""
        xmlstr = zipfile.ZipFile(file).read('content.xml')
        xmlstr = xmlstr.replace(doctype,'')       
        return xmlstr

    def getData(self):
        return self._data.getvalue()


class Converter(BaseConverter):

    content_type = ('application/vnd.sun.xml.writer',)
    content_description = "OpenOffice"

    def convert(self, doc):
        """ convert OpenOffice Document """

        handler = ootextHandler()
        xmlstr = handler.getxmlcontent(doc)
        xml.sax.parseString(xmlstr, handler)

        return handler.getData()

if __name__=="__main__":

    C = Converter()        
    print C.convert(open('test.sxw').read())


