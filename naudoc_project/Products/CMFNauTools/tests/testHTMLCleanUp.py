#! /bin/env python2.3
"""
Follow up Tests.

$Id: testHTMLCleanUp.py,v 1.1 2005/12/09 15:27:42 vsafronovich Exp $
$Editor: vsafronovich $
"""
__version__='$Revision: 1.1 $'[11:-2]

import os, sys
import Configurator

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import NauDocTestCase

ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFNauTools')
ZopeTestCase.installProduct('NauScheduler')
ZopeTestCase.installProduct('TextIndexNG2')

from unittest import TestCase

from Products.CMFNauTools import HTMLCleanup
from types import TupleType, DictType


dirt_html_for_complete_test = """
<html xmlns:o="urn:schemas-microsoft-com:office:office"
xmlns:w="urn:schemas-microsoft-com:office:word"
xmlns="http://www.w3.org/TR/REC-html40">

<head>
<meta http-equiv=Content-Type content="text/html; charset=windows-1251">
<meta name=ProgId content=Word.Document>
<meta name=Generator content="Microsoft Word 9">
<meta name=Originator content="Microsoft Word 9">
<title>Rename method</title>
<!--[if gte mso 9]><xml>
 <o:DocumentProperties>
  <o:Author>Firsov</o:Author>
  <o:LastAuthor>Firsov</o:LastAuthor>
  <o:Revision>2</o:Revision>
  <o:TotalTime>2</o:TotalTime>
  <o:Created>2004-06-07T09:38:00Z</o:Created>
  <o:LastSaved>2004-06-07T09:43:00Z</o:LastSaved>
  <o:Pages>1</o:Pages>
  <o:Words>19</o:Words>
  <o:Characters>112</o:Characters>
  <o:Company>naumen</o:Company>
  <o:Lines>1</o:Lines>
  <o:Paragraphs>1</o:Paragraphs>
  <o:CharactersWithSpaces>137</o:CharactersWithSpaces>
  <o:Version>9.3821</o:Version>
 </o:DocumentProperties>
</xml><![endif]-->
<style>
<!--
 /* Style Definitions */
p.MsoNormal, li.MsoNormal, div.MsoNormal
        {mso-style-parent:"";
        margin:0cm;
        margin-bottom:.0001pt;
        mso-pagination:widow-orphan;
        font-size:12.0pt;
        font-family:"Times New Roman";
        mso-fareast-font-family:"Times New Roman";}
h2
        {mso-style-next:Usual;
        margin-top:12.0pt;
        margin-right:0cm;
        margin-bottom:3.0pt;
        margin-left:0cm;
        mso-pagination:widow-orphan;
        page-break-after:avoid;
        mso-outline-level:2;
        font-size:14.0pt;
        font-family:Arial;
        font-style:italic;}
@page Section1
        {size:595.3pt 841.9pt;
        margin:2.0cm 42.5pt 2.0cm 3.0cm;
        mso-header-margin:35.4pt;
        mso-footer-margin:35.4pt;
        mso-paper-source:0;}
div.Section1
        {page:Section1;}
-->
</style>
</head>

<body lang=RU style='tab-interval:35.4pt'>

<div class=Section1>

<h2 style='line-height:150%'><span lang=EN-US style='mso-ansi-language:EN-US'>Rename
method<o:p></o:p></span></h2>

<p class=MsoNormal style='line-height:150%;mso-layout-grid-align:none;
text-autospace:none'><i><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";mso-ansi-language:EN-US'>#</span></i><i><span
lang=EN-US style='mso-ansi-language:EN-US'>The name of a method does not reveal
its purpose.</span></i><i><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";mso-ansi-language:EN-US'><o:p></o:p></span></i></p>

<p class=MsoNormal style='line-height:150%;mso-layout-grid-align:none;
text-autospace:none'><i><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";mso-ansi-language:EN-US'># before<o:p></o:p></span></i></p>

<p class=MsoNormal style='line-height:150%;mso-layout-grid-align:none;
text-autospace:none'><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";color:#00007F;mso-ansi-language:EN-US'>def</span><span
lang=EN-US style='mso-bidi-font-size:10.0pt;font-family:"Courier New";
mso-ansi-language:EN-US'> <span style='color:black'>getPrnt</span>():<o:p></o:p></span></p>

<p class=MsoNormal style='line-height:150%;mso-layout-grid-align:none;
text-autospace:none'><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";mso-ansi-language:EN-US'><span style="mso-spacerun:
yes"></span><span style='color:#00007F'>pass</span><o:p></o:p></span></p>

<p class=MsoNormal style='line-height:150%;mso-layout-grid-align:none;
text-autospace:none'><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";mso-ansi-language:EN-US'><![if !supportEmptyParas]>&nbsp;<![endif]><o:p></o:p></span></p>

<p class=MsoNormal style='line-height:150%;mso-layout-grid-align:none;
text-autospace:none'><i><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";mso-ansi-language:EN-US'># after<o:p></o:p></span></i></p>

<p class=MsoNormal style='line-height:150%;mso-layout-grid-align:none;
text-autospace:none'><b><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";color:#00007F;mso-ansi-language:EN-US'>def</span></b><b><span
lang=EN-US style='mso-bidi-font-size:10.0pt;font-family:"Courier New";
mso-ansi-language:EN-US'> <span style='color:black'>getParentUID</span>():<o:p></o:p></span></b></p>

<p class=MsoNormal><span lang=EN-US style='mso-bidi-font-size:10.0pt;
font-family:"Courier New";mso-ansi-language:EN-US'><span style="mso-spacerun:
yes"></span></span><span style='mso-bidi-font-size:10.0pt;font-family:"Courier New";
color:#00007F'>pass</span></p>

</div>

</body>

</html>"""
clear_html_for_complete_test = """<html>
<head>
<title>Rename method</title>
</head>
<body>
<div>
<h2><span>Rename
method</span></h2>
<p class=MsoNormal><i><span>#</span></i><i><span>The name of a method does not reveal
its purpose.</span></i><i><span></span></i></p>
<p class=MsoNormal><i><span># before</span></i></p>
<p class=MsoNormal><span>def</span><span> <span>getPrnt</span>():</span></p>
<p class=MsoNormal><span><span></span><span>pass</span></span></p>
<p class=MsoNormal><span>&nbsp;</span></p>
<p class=MsoNormal><i><span># after</span></i></p>
<p class=MsoNormal><b><span>def</span></b><b><span> <span>getParentUID</span>():</span></b></p>
<p class=MsoNormal><span><span></span></span><span>pass</span></p>
</div>
</body>
</html>"""


#==========================================

class HTMLCleanupTests( TestCase ):

#    def setUp( self ):
#        pass

    def testConvertTagsAndAttrsToDict( self ):

        self.assertEqual( HTMLCleanup.convertTagsAndAttrsToDict(''), {}, 'Error parsing empty parameter string' )

        param_string = """ HTML P
            align
                style A    href       """
        param_dict = {'HTML':[], 'P':['align', 'style'], 'A':['href']}

        converted_params = HTMLCleanup.convertTagsAndAttrsToDict( param_string )
        self.assertEqual( len(converted_params.keys()), len(param_dict), 'Invalid number of key tags')
        for key, value in converted_params.items():
            if not param_dict.has_key( key ):
                self.fail( "The tagname %s is invalid" % key )
            value.sort()
            param_v = param_dict[key]
            param_v.sort()

            self.assertEqual( value, param_v, "Invalid properties for %s" % key )

    def testExcludeRepetitions( self ):
        self.assertEqual( HTMLCleanup.excludeRepetitions( () ), (), "Error while compressing empty sequence" )
        self.assertEqual( HTMLCleanup.excludeRepetitions( ('1', ) ), ('1', ), "Error while compressing 1 element sequence" )
        sequence_with_repetitions = ('a', 'b', 'c', 'b', 'a')
        sequence_without_repetitions = ['a', 'b', 'c']

        result = HTMLCleanup.excludeRepetitions( sequence_with_repetitions )
        self.assertEqual( type( result ), TupleType, "Result is not a tuple" )

        result = list( result )
        result.sort()

        self.assertEqual( result, sequence_without_repetitions, "Compressed sequence is invalid" )


    def testExtractAllTagsFromHTML( self ):
        test_html = """
        <HTML><BODY><table width="100%">
            <tr>
              <td><img src=""></td>
            </tr>
            </BODY>
        </HTML>
        """
        test_tags = ['BODY', 'HTML', 'IMG', 'TABLE', 'TD', 'TR']
        self.assertEqual( HTMLCleanup.extractAllTagsFromHTML( '' ), (), "Error processing empty string")
        self.assertEqual( HTMLCleanup.extractAllTagsFromHTML( '<HTML>' ), ('HTML',), "Error processing 1 element string")

        result = HTMLCleanup.extractAllTagsFromHTML( test_html )
        self.assertEqual( type( result ), TupleType, "Result is not a tuple")

        result = list( result )
        result.sort()

        self.assertEqual( result, test_tags, "Found tags are invalid")


    def testParseAttributesString( self ):
        #empty string
        self.assertEqual( HTMLCleanup.parseAttributesString( '' ), {}, "Error parsing empty string" )

        str1 = """ WIDTH="100%" height=10px align=left checked selected name='test' id=test style="text-color:#FFFFFF; background-color:#000000;" """
        dict1 = {   'width'     : '"100%"',
                    'height'    : '10px',
                    'align'     : 'left',
                    'checked'   : '',
                    'selected'  : '',
                    'name'      : "'test'",
                    'id'        : 'test',
                    'style'     : '"text-color:#FFFFFF; background-color:#000000;"'
                }
        #result type
        result = HTMLCleanup.parseAttributesString( str1 )
        self.assertEqual( type( result ), DictType, "Result is not a dictionary" )

        #lowercase of attribute
        self.assertEqual( HTMLCleanup.parseAttributesString( "CHECKED" ), {'checked':''}, "Attribue was not lowercased" )

        self.assertEqual( len( result.keys() ), len( dict1.keys() ), "Number of attributes does not match" )
        for key, value in result.items():
            if not dict1.has_key( key ):
                self.fail( "Found invalid attribute: %s" % key )
            self.assertEqual( value, dict1[ key ], "Value of attribute %s is invalid" % key)

    def testRemoveHTMLComments( self ):
        self.assertEqual( HTMLCleanup.removeHTMLComments( '' ), '', "Error parsing empty string" )
        self.assertEqual( HTMLCleanup.removeHTMLComments( '<!---->' ), '', "Error parsing only comment" )


        test1 = """<html><body><!-- <table><tr>
        <td> --><span>123</span><!-- 123 123
        --></body></html>"""

        result1 = "<html><body><span>123</span></body></html>"

        self.assertEqual( HTMLCleanup.removeHTMLComments(test1), result1, "Error removing comments" )

    def testCompletelyRemoveTags( self ):
        self.assertEqual( HTMLCleanup.completelyRemoveTags( '' ), '', "Error parsing empty string" )

        #3 variants to test case insensitivity
        str1 = """<p></p><h1><p class="h1"></p></h1><a />"""
        self.assertEqual( HTMLCleanup.completelyRemoveTags( str1, ['H1'] ), "<p></p><a />" )

        str1 = """<P></P><H1><P class="h1"></P></H1><A />"""
        self.assertEqual( HTMLCleanup.completelyRemoveTags( str1, ['H1'] ), "<P></P><A />" )

        str1 = """<P></P><H1><P class="h1"></P></H1><A />"""
        self.assertEqual( HTMLCleanup.completelyRemoveTags( str1, ['h1'] ), "<P></P><A />" )

    def testRemoveTags( self ):
        self.assertEqual( HTMLCleanup.removeTags( '' ), '', "Error parsing empty string" )

        str1 = """<P></P><DIV><P class="h1">123</P></DIV><A />"""
        self.assertEqual( HTMLCleanup.removeTags( str1, ['DIV'] ), "<P></P><P class=\"h1\">123</P><A />" )

        #swap case
        str1 = """<p></p><div><p class="h1">123</p></div><a />"""
        self.assertEqual( HTMLCleanup.removeTags( str1, ['DIV'] ), "<p></p><p class=\"h1\">123</p><a />" )

        #test nested tags
        str1 = """<P></P><DIV><P class="h1"><DIV>123</DIV></P></DIV><A />"""
        self.assertEqual( HTMLCleanup.removeTags( str1, ['div'] ), "<P></P><P class=\"h1\">123</P><A />" )

    def testProcessCharacterReferences( self ):
        self.assertEqual( HTMLCleanup.processCharacterReferences('', 0), '', "Error parsing empty string" )
        str1 = "&nbsp;&nbsp;&nbsp;&amp;&amp; &lt; &lt;"
        self.assertEqual( HTMLCleanup.processCharacterReferences(str1, 0), str1, "Error when no processing must be done" )

        #remove all
        self.assertEqual( HTMLCleanup.processCharacterReferences(str1, 1), "  ", "Error removing char refs" )

        #shrink if >=1
        self.assertEqual( HTMLCleanup.processCharacterReferences(str1, 2), "&nbsp;&amp; &lt; &lt;", "Error shrinking char refs" )


    def testHTMLCleaner( self ):
        self.assertEqual( HTMLCleanup.HTMLCleaner(''), '', "Error parsing empty string" )

        #The main test in module goes here:
        self.assertEqual( HTMLCleanup.HTMLCleaner( dirt_html_for_complete_test ), clear_html_for_complete_test )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(HTMLCleanupTests))
    return suite

if __name__ == '__main__':
    framework()
