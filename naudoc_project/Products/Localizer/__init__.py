# Copyright (C) 2000 - 2002  Juan David Ibáñez Palomar <jdavid@nuxeo.com>

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


"""Localizer"""
__version__ = "$Revision: 1.35 $"


from zLOG import LOG, ERROR, INFO, PROBLEM




#################################################################
#   Patches start here!!!
################################################################


# PATCH 1
#
# Makes REQUEST available from the Globals module.
#
# It's needed because context is not available in the __of__ method,
# so we can't get REQUEST with acquisition. And we need REQUEST for
# local properties (see LocalPropertyManager.pu).
#
# This patch is at the beginning to be sure code that requires it
# doesn't breaks.
#
# This pach is inspired in a similar patch by Tim McLaughlin, see
# "http://dev.zope.org/Wikis/DevSite/Proposals/GlobalGetRequest".
# Thanks Tim!!
#

from thread import get_ident
from ZPublisher import Publish, mapply

def get_request():
    """Get a request object"""
    return Publish._requests.get(get_ident(), None)

def new_publish(request, module_name, after_list, debug=0,
                # Optimize:
                call_object=Publish.call_object,
                missing_name=Publish.missing_name,
                dont_publish_class=Publish.dont_publish_class,
                mapply=mapply.mapply):
    ident = get_ident()
    Publish._requests[ident] = request
    x = Publish.old_publish(request, module_name, after_list, debug,
                            call_object, missing_name, dont_publish_class,
                            mapply)

    try: del Publish._requests[ident]
    except: pass

    return x
 
patch = 0
if not hasattr(Publish, '_requests'):
    # Apply patch
    Publish._requests = {}
    Publish.old_publish = Publish.publish
    Publish.publish = new_publish

    import Globals
    Globals.get_request = get_request

    # First import (it's not a refresh operation).
    # We need to apply the patches.
    patch = 1


# PATCH 2
#
# Adds a new variable to REQUEST: USER_PREF_LANGUAGES, which holds the
# list of user prefered languages.
#

# Apply the patch
from AcceptLanguage import AcceptLanguage
from ZPublisher.HTTPRequest import HTTPRequest
def new_processInputs(self):
    HTTPRequest.old_processInputs(self)

    # Set the USER_PREF_LANGUAGES variable
    request = self

    # Initialize witht the browser configuration
    accept_language = request['HTTP_ACCEPT_LANGUAGE']
    # Patches for user agents that don't support correctly the protocol
    user_agent = request['HTTP_USER_AGENT']
    if user_agent.startswith('Mozilla/4'):
        # Netscape 4.x
        q = 1.0
        langs = []
        for lang in [ x.strip() for x in accept_language.split(',') ]:
            langs.append('%s;q=%f' % (lang, q))
            q = q/2
        accept_language = ','.join(langs)

    accept_language = AcceptLanguage(accept_language)

    # Add the language from the form
    lang = request.form.get('LOCALIZER_LANGUAGE', None)
    if lang is not None:
        accept_language[lang] = 3.0

    # Add the language from the cookies
    lang = request.cookies.get('LOCALIZER_LANGUAGE', None)
    if lang is not None:
        accept_language[lang] = 2.0

    self.other['USER_PREF_LANGUAGES'] = accept_language

if patch:
    HTTPRequest.old_processInputs = HTTPRequest.processInputs
    HTTPRequest.processInputs = new_processInputs




# PATCH 3
#
# Changes the tag method of Images to use the real path.
#
# This is needed to prevent browsers to cache different images with
# the same logical url.
#

from OFS import Image
def tag(self, height=None, width=None, alt=None,
        scale=0, xscale=0, yscale=0, css_class=None, **args):
    s = apply(Image.old_tag,
              (self, height, width, alt, scale, xscale, yscale),
              args)

    # Process the string
    l = s.split()       

    for i in range(len(l)):
        x = l[i]
        if x[:4] == 'src=':
            break

    l[i] = 'src="%s"' % '/'.join(self.getPhysicalPath())

    return ' '.join(l)

if patch:
    Image.old_tag = Image.Image.tag
    Image.Image.tag = tag



# Standard intialization code
from ImageFile import ImageFile
from DocumentTemplate.DT_String import String
import ZClasses

import Localizer, LocalContent, MessageCatalog, LocalFolder
from LocalFiles import LocalDTMLFile, LocalPageTemplateFile
from LocalPropertyManager import LocalPropertyManager, LocalProperty
from GettextTag import GettextTag


misc_ = {'arrow_left': ImageFile('img/arrow_left.gif', globals()),
         'arrow_right': ImageFile('img/arrow_right.gif', globals()),
         'eye_opened': ImageFile('img/eye_opened.gif', globals()),
         'eye_closed': ImageFile('img/eye_closed.gif', globals())}



def initialize(context):
    # Register the Localizer
    context.registerClass(Localizer.Localizer,
                          constructors = (Localizer.manage_addLocalizerForm,
                                          Localizer.manage_addLocalizer),
                          icon = 'img/localizer.gif')

    # Register LocalContent
    context.registerClass(
        LocalContent.LocalContent,
        constructors = (LocalContent.manage_addLocalContentForm,
                        LocalContent.manage_addLocalContent),   
        icon='img/local_content.gif')

    # Register MessageCatalog
    context.registerClass(
        MessageCatalog.MessageCatalog,
        constructors = (MessageCatalog.manage_addMessageCatalogForm,
                        MessageCatalog.manage_addMessageCatalog),
        icon='img/message_catalog.gif')

    # Register LocalFolder
    context.registerClass(
        LocalFolder.LocalFolder,
        constructors = (LocalFolder.manage_addLocalFolderForm,
                        LocalFolder.manage_addLocalFolder),
        icon='img/localizer.gif')

    # Register LocalPropertyManager as base class for ZClasses
    ZClasses.createZClassForBase(LocalPropertyManager, globals(),
                                 'LocalPropertyManager',
                                 'LocalPropertyManager')


    context.registerHelp()

    # Register the dtml-gettext tag
    String.commands['gettext'] = GettextTag


    ## Register the translator profile
    try:
        import Translator
        context.registerPlugInClass(
            Translator.Translator,
            'Translator',
            constructors = (Translator.manage_addTranslatorForm,
                            Translator.manage_addTranslator))
    except:
        pass
