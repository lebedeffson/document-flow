#!/usr/bin/env python

# Localizer, Zope product that provides internationalization services
# Copyright (C) 2001 Andres Marzal Varo
#                    J. David Ibáñez <palomar@sg.uji.es>

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
zgettext.py is a script that parses DTML files and generates .pot and .po
files, and then generates .mo files from the .po files.
"""

__version__ = "$Revision: 1.15 $"


import os, re, sys, time



def create_mo_files():
    for filename in [ x for x in os.listdir('locale') if x.endswith('.po') ]:
        language = filename[:-3]
        os.system('msgfmt locale/%s.po -o locale/%s.mo' % (language, language))


def parse_po_file(content):
    # The regular expressions
    com = re.compile('^#.*')
    msgid = re.compile(r'^ *msgid *"(.*?[^\\]*)"')
    msgstr = re.compile(r'^ *msgstr *"(.*?[^\\]*)"') 
    re_str = re.compile(r'^ *"(.*?[^\\])"') 
    blank = re.compile(r'^\s*$')

    trans = {}
    pointer = 0
    state = 0
    COM, MSGID, MSGSTR = [], [], []
    while pointer < len(content):
        line = content[pointer]
        # print 'STATE:', state, 'LANGUAGE', language
        # print 'LINE:', content[pointer].strip()
        if state == 0:
            COM, MSGID, MSGSTR = [], [], []
            if com.match(line):
                COM.append(line.strip())
                state = 1
                pointer = pointer + 1
            elif msgid.match(line):
                MSGID.append(msgid.match(line).group(1))
                state = 2
                pointer = pointer + 1
            elif blank.match(line):
                pointer = pointer + 1
            else:
                raise 'ParseError', 'state 0, line %d\n' % (pointer + 1)
        elif state == 1:
            if com.match(line):
                COM.append(line.strip())
                state = 1
                pointer = pointer + 1
            elif msgid.match(line):
                MSGID.append(msgid.match(line).group(1))
                state = 2
                pointer = pointer + 1
            elif blank.match(line):
                pointer = pointer + 1
            else:
                raise 'ParseError', 'state 1, line %d\n' % (pointer + 1)
        elif state == 2:
            if com.match(line):
                COM.append(line.strip())
                state = 2
                pointer = pointer + 1
            elif re_str.match(line):
                MSGID.append(re_str.match(line).group(1))
                state = 2
                pointer = pointer + 1
            elif msgstr.match(line):
                MSGSTR.append(msgstr.match(line).group(1))
                state = 3
                pointer = pointer + 1
            elif blank.match(line):
                pointer = pointer + 1
            else:
                raise 'ParseError', 'state 2, line %d\n' % (pointer + 1)
        elif state == 3:
            if com.match(line) or msgid.match(line):
                # print "\nEn", language, "detected", MSGID
                trans[tuple(MSGID)] = (COM, MSGSTR)
                state = 0
            elif re_str.match(line):
                MSGSTR.append(re_str.match(line).group(1))
                state = 3
                pointer = pointer + 1
            elif blank.match(line):
                pointer = pointer + 1
            else:
                raise 'ParseError', 'state 3, line %d\n' % (pointer + 1)

    # the last also goes in
    if tuple(MSGID):
        trans[tuple(MSGID)] = (COM, MSGSTR)

    return COM, MSGID, MSGSTR, trans


def parse_generic(text, commands=('gettext', 'ugettext')):
    """
    Search for patterns like: gettext('message')
    """

    # XXX Probably pygettext or xpot should be used.
    r = []
    for command in commands:
        pattern = command + '\s*\(\s*(\'.*?[^\\\\]\'|\".*?[^\\\\]\")\s*\)'
        regex = re.compile(pattern, re.DOTALL)
        r.extend([ x[1:-1] for x in re.findall(regex, text) ])

    return r


def parse_dtml(text):
    """Extract the messages from a DTML template."""

    messages = parse_generic(text)

    # Search the "<dtml-gettext>message</dtml-gettext>" pattern
    regex = re.compile('<dtml-gettext(.*?)>(.*?)</dtml-gettext>', re.DOTALL)
    for parameters, message in re.findall(regex, text):
        if parameters.find('verbatim') == -1:
            message = ' '.join([ x.strip() for x in message.split() ])
        messages.append(message)

    return messages

def parse_zpt(text):
    """Extract the messages from a ZPT template."""

    return parse_generic(text)


def do_all(filenames, languages):
    # Create the locale directory
    if not os.path.isdir('./locale'):
        try:
            os.mkdir('./locale')
        except OSError, msg:
            sys.stderr.write('Error: Cannot create directory "locale".\n%s\n'
                             % msg)
            sys.exit(1)

    # Get the messages
    messages = []
    for filename in filenames:
        filetype = filename.split('.')[-1]

        text = open(filename).read()

        aux = []
        if filetype == 'dtml':
            aux = parse_dtml(text)
        elif filetype == 'zpt':
            auz = parse_generic(text)
        elif filetype == 'py':
            aux = parse_generic(text, ('gettext', 'ugettext', '_', 'N_'))

        for message in aux:
            if message not in messages:
                messages.append(message)

    messages.sort()


    trans = {}
    for s in messages:
        x = []
        lines = s.split('\n')
        for i in range(len(lines)):
            line = lines[i]
            if i < len(lines) - 1:
                line = line + ' '
            x.append(line)
        trans[tuple(x)] = ([],[])

    # Create the .pot file
    if os.path.exists('./locale/locale.pot'):
        # read and preserve the file content
        content = open('./locale/locale.pot').readlines()
        os.rename('locale/locale.pot', 'locale/locale.pot.bak')
        # Parse the locale.pot file
        COM, MSGID, MSGSTR, new_trans = parse_po_file(content)
        trans.update(new_trans)
    else:
        trans[('',)] = ([], [])

    # Generation of the .pot file
    f = open('locale/locale.pot', 'w')
    # First, the msgid ""
    ##if os.path.exists('./version.txt'):
    ##    version = open('version.txt').read().strip()
    ##else:
    ##    version = 'PRODUCT VERSION'

    trans[('',)] = (
        trans[('',)][0],
        ["Project-Id-Version: PACKAGE VERSION\\n",
         "POT-Creation-Date: %s\\n"
         % time.strftime('%Y-%m-%d %H:%m+%Z', time.gmtime(time.time())),
         "PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n",
         "Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n",
         "Language-Team: LANGUAGE <LL@li.org>\\n",
         "MIME-Version: 1.0\\n",
         "Content-Type: text/plain; charset=CHARSET\\n",
         "Content-Transfer-Encoding: ENCODING\\n"])


    # Now, the rest
    msgids = trans.keys()
    msgids.sort()

    for k in msgids:
        v = trans[k]
        f.write('\n'.join(v[0]) + '\n')
        f.write('msgid "%s"' % k[0] +'\n')
        for kk in k[1:]:
            f.write('"%s"' % kk +'\n')
        if len(v[1])>0:
            f.write('msgstr "%s"' % v[1][0] +'\n')
            for vv in v[1][1:]:
                f.write('"%s"' % vv + '\n')
        else:
            f.write('msgstr ""\n')
        f.write('\n')
    f.close()



    # generate the .po and .mo files
    for language in languages:
        if os.path.exists('./locale/%s.po' % language):
            # a .po file already exist, merge it with locale.pot
            os.system('msgmerge -o locale/%s.po locale/%s.po locale/locale.pot'
                      % (language, language))
        else:
            # po doesn't exist, just copy locale.pot
            text = open('./locale/locale.pot').read()
            open('./locale/%s.po' % language, 'w').write(text)



if __name__ == '__main__':
    # Parse the command line
    status = 0
    files = []
    langs = []
    for arg in sys.argv[1:]:
        if status == 0:
            if arg == '-h':
                status = 1
            elif arg == '-m':
                status = 2
            elif arg == '-l':
                status = 3
            else:
                files.append(arg)
                status = 4
        elif status == 1:
            status = 'Error'
            break
        elif status == 2:
            status = 'Error'
            break
        elif status == 3:
            langs.append(arg)
            status = 5
        elif status == 4:
            if arg == '-l':
                status = 3
            else:
                files.append(arg)
        elif status == 5:
            langs.append(arg)
        else:
            raise 'UknownStatus', str(status)

    # Action
    if status in (0, 1, 3, 'Error'):
        # Provide help if the line format is wrong or if the -h modifier
        # is provided
        print 'Usage:'
        print '  zgettext.py -h'
        print '    Shows this help message.'
        print '  zgettext.py [file file ... file] [-l languages]'
        print '    Parses all the specified files, creates the locale'
        print '    directory, creates the locale.pot file and the .po'
        print '    files of the languages specified.'
        print '  zgettxt.py -m'
        print '    Compiles all the .po files in the locale directory'
        print '    and creates the .mo files.'
        print
        print 'Examples:'
        print '  zgettext.py *.dtml -l ca es en'
        print '  zgettext.py -m'
    elif status == 2:
        create_mo_files()
    elif status in (4, 5):
        do_all(files, langs)
    else:
        raise 'UknownStatus', str(status)
