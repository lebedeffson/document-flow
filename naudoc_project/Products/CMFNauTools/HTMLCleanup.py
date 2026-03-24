""" HTMLCleanup module

$Editor: kfirsov $

$Id: HTMLCleanup.py,v 1.28 2005/10/06 09:58:42 vsafronovich Exp $
"""
__version__='$Revision: 1.28 $'[11:-2]

from sys import version_info
if version_info[:2] < (2, 3):
    import pre as re
else:
    import re
import string


#cached compiled regexps:
tagsToCompletelyRemovePatterns = {}
tagsToRemovePatterns = {}
tagsAndAttributesPatterns = {}

#compiled regexps:
remove_comments_pattern = re.compile(r"<!--.*?-->(?ms)")

extract_tags_pattern = re.compile(r"<\/?(\??[\w\!\:]+).*?>(?si)")

arrtibutes_and_values_pattern = re.compile(r"([a-zA-Z\-]+)\s*=\s*(?:([\"\'])(.*?)\2|([\w\-\.\%\#]+))(?si)")

single_character_reference_pattern = re.compile(r"&#?\w+?;(?ms)")
group_character_reference_pattern = re.compile(r"(&#?\w+?;)\1+(?ms)")

empty_strings_pattern = re.compile( r"^\s*[\r\n]+(?msi)" )


default_update_str = """
    HTML HEAD TITLE
    BODY
    P class id width align height
    DIV align
    SPAN
    A class id href name target
    STRONG BR B U I EM PRE STRIKE SUB SUP
    H1 align class id
    H2 align class id
    H3 align class id
    H4 align class id
    H5 align class id
    H6 align class id
    UL class id
    OL class id start
    LI class id
    TABLE align class id bgcolor width height border cellspacing cellpadding bordercolor bordercolordark style
    TH class id bgcolor
    TBODY class id
    TR class id bgcolor valign align style
    TD class id nowrap rowspan width bgcolor colspan valign align style
    IMG style class id src width align height border hspace vspace alt
    FONT size color class id face
    BLOCKQUOTE style
    HR size color class style width align
"""


def convertTagsAndAttrsToDict( str_with_tags_and_attrs ):
    """
        Parses input string and return dictionary
        where keys are tags and values are attributes.

        Result: dictionary
    """
    result = {}
    attrslist = []
    for tag_or_attr in str_with_tags_and_attrs.split():
        if tag_or_attr.isupper():
            #tag name
            result[tag_or_attr] = attrslist = []
        else:
            #attribute name
            attrslist.append( tag_or_attr )

    return result


def excludeRepetitions( sequence ):
    """
        Removes from sequence repetitive elements.

        Note: elements in sequence must have __hash__() method.

        Result: tuple
    """
    result = {}
    for element in sequence:
        result[ element ] = 1
    return tuple( result.keys() )



def extractAllTagsFromHTML( html_text ):
    """
        Returns tuple of html tagnames found in given text.

        Result: Tuple with unique tagnames.
    """
    tags_list = extract_tags_pattern.findall( html_text )
    return tuple( map(string.upper, excludeRepetitions( tags_list )) )


def parseAttributesString( sting_with_attributes ):
    """
        Extracts from sting_with_attributes attributes
        and their values (if any) to dictionary.

        Result: dictionary
    """

    result = {}

    matched = arrtibutes_and_values_pattern.search( sting_with_attributes )
    # result is: (attr)=("/')(value)() or (attr)=()()(value)
    while matched:
        attribute_name = matched.group(1).lower()
        if matched.group(2):
            result[attribute_name] = ''.join( map(matched.group, [2,3,2]) )
        else:
            result[attribute_name] = matched.group(4)
        sting_with_attributes = sting_with_attributes[:matched.start()] + sting_with_attributes[matched.end():]
        matched = arrtibutes_and_values_pattern.search( sting_with_attributes, matched.start() )

    #all left in attr_str are boolean attrs
    boolean_attributes = sting_with_attributes.lower().split()
    for boolean_attribute in boolean_attributes:
        result[ boolean_attribute ] = ''

    return result

def removeHTMLComments( html ):
    """
        Removes html comments (<!-- ... -->) from given html.

        Result: string
    """
    return remove_comments_pattern.sub('', html)


def completelyRemoveTags( html, tagnames=[] ):
    """
        Removes from html tagnames with everything
        inside starting and closing tag.

        Note: does not work with tags like <br>, <hr> etc.

        Result: string
    """
    #remove all tags to be comletely remove
    global tagsToCompletelyRemovePatterns
    result = html
    for tagname in tagnames:
        if tagsToCompletelyRemovePatterns.has_key( tagname ):
            result = tagsToCompletelyRemovePatterns[ tagname ].sub( '', result )
        else:
            escaped_tagname = re.escape(tagname)
            pattern = re.compile(r"<%s[\s>]+.*?<\/%s(?:>|\s+.*?>)(?si)" % (escaped_tagname, escaped_tagname))
            tagsToCompletelyRemovePatterns[ tagname ] = pattern
            result = pattern.sub('', result)
    return result


def removeTags( html, tagnames=[]):
    """
        Removes from html only start tag or/and end tag with all properties,
        but leaves text inside.

        Result: string
    """
    #
    global tagsToRemovePatterns
    result = html
    for tagname in tagnames:
        if tagsToRemovePatterns.has_key( tagname ):
            result = tagsToRemovePatterns[ tagname ].sub( '', result )
        else:
            pattern = re.compile( r"<\/?%s(?:>|[\W]+?.*?>)(?msi)" % re.escape(tagname) )
            tagsToRemovePatterns[ tagname ] = pattern
            result = pattern.sub('', result)
    return result

def processCharacterReferences( html, char_references_mode ):
    """
        Arguments:
            'char_references_mode' -- processing character references mode
            1 - cut all character references;
            2 - reduce sequence of same character references to one;
            other values: do nothing.
    """
    result = html
    #process character references
    if char_references_mode == 1:
        #remove all
        result = single_character_reference_pattern.sub( '', html )
    elif char_references_mode == 2:
        #replace sequence with one char ref
        result = group_character_reference_pattern.sub( r"\1", html )

    return result



#main function
def HTMLCleaner(dirt_html, update_str=None, char_references_mode = 0, leave_str = '', remove_str = ''):
    """ Clean 'dirty' html text - remove some tags, some attributes.

        dirt_html - string with HTML text we want to cleanup;
        update_str - string in format: TAG1 [attr1 [attr2 [...]]] TAG2 [attr1 [...]]
             leave only these tags and their attributes
        char_references_mode - processing character references mode
            0 - leave all character references,
            1 - cut all character references
            2 - reduce character references (for example '&nbsp;&nbsp;&nbsp;' becomes '&nbsp;')
        leave_str - tagnames (in uppercase) separated by spaces those will not be cleaned
            (all their attributes will be leaved)
        remove_str - tagnames (in uppercase) separated by spaces those will be completely
            removed (with any data in it)
    """
    if update_str is None:
        update_str = default_update_str

    #parse update_str
    update_tags = convertTagsAndAttrsToDict( update_str )

    update_tags_list = update_tags.keys()

    #keep_unchanged - tags we do not want to change
    keep_unchanged = leave_str.split()

    dirt_html = removeHTMLComments( dirt_html )

    dirt_html = completelyRemoveTags( dirt_html, remove_str.split() )

    dirt_html = processCharacterReferences( dirt_html, char_references_mode )

    #remove tags not specified in update_str and leave_str
    all_tags = extractAllTagsFromHTML( dirt_html )
    tags_not_to_remove = (update_tags_list + keep_unchanged)
    tags_to_remove = [ tag for tag in  all_tags if tag not in tags_not_to_remove ]

    dirt_html = removeTags( dirt_html, tags_to_remove)


    #process attributes
    global tagsAndAttributesPatterns
    for tagname in update_tags_list:
        #cache regexps
        if tagsAndAttributesPatterns.has_key( tagname ):
            tag_tuples = tagsAndAttributesPatterns[ tagname ].findall( dirt_html )
        else:
            pattern = re.compile( r"<(\/?)(%s)(\s+.*?)>(?si)" % re.escape(tagname) )
            tagsAndAttributesPatterns[ tagname ] = pattern
            tag_tuples = pattern.findall( dirt_html )

        #some tags are very repetitive
        tag_tuples = excludeRepetitions( tag_tuples )

        #process attributes
        for tag_tuple in tag_tuples:
            tag_str = "<%s>" % ''.join( tag_tuple )

            filtered_attrs_data = [ "<%s%s" % tag_tuple[:-1] ]

            if tag_tuple[-1].strip():
                attributes_data = parseAttributesString( tag_tuple[-1] + " " )

                for attr_name in update_tags[ tagname ]:
                    if attributes_data.has_key(attr_name):
                        if attributes_data[attr_name]:
                            filtered_attrs_data.append( "%s=%s" % (attr_name, attributes_data[attr_name]))
                        else:
                            filtered_attrs_data.append( attr_name )

            replace_str = "%s>" % ' '.join( filtered_attrs_data )

            dirt_html = dirt_html.replace(tag_str, replace_str)

    #remove empty strings
    dirt_html = empty_strings_pattern.sub('', dirt_html)

    return dirt_html
