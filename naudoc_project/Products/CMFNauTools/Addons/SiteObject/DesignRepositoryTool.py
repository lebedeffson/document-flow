# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/SiteObject/DesignRepositoryTool.py
# Compiled at: 2008-10-15 16:48:07
"""
DesignRepositoryTool and SiteSkinContainer classes.

$Editor: vpastukhov $
$Id: DesignRepositoryTool.py,v 1.1 2008/10/15 12:48:07 oevsegneev Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]
import re
from os.path import join as pathjoin, exists as pathexists
from App.Common import package_home
from Globals import DTMLFile
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from Products.CMFCore import DirectoryView
from Products.CMFCore.utils import minimalpath, expandpath
from SiteImage import SiteImage
from Products.CMFNauTools.SimpleObjects import ToolBase
from Products.CMFNauTools.Utils import InitializeClass, pathdelim

class DesignRepositoryTool(ToolBase, ObjectManager, SimpleItem):
    """
      This tool accesses external site design collection
    """
    __module__ = __name__
    id = 'portal_site_skins'
    meta_type = 'NauSite Design Repository Tool'
    manage_options = ObjectManager.manage_options + ({'label': 'Manage', 'action': 'manageForm'},)
    manageForm = DTMLFile('dtml/manageRepository', globals())

    def __init__(self):
        ToolBase.__init__(self)
        path = minimalpath(package_home(globals()))
        path = path.replace('\\', pathdelim)
        self._site_skins_path = path + '/skin/site_skins'
        self.manage_reloadSkins()
        return

    def addSkin(self, id):
        """
          adds skin view to repository
        """
        skins_info = DirectoryView._dirreg.getDirectoryInfo(self._site_skins_path)
        if id not in skins_info.getSubdirs():
            return 'no such skin'
        skin_path = pathjoin(self._site_skins_path, str(id))
        if not pathexists(pathjoin(expandpath(skin_path), 'description.txt')):
            return 'no description'
        ssc = SiteSkinContainer(id, skin_path)
        info = DirectoryView._dirreg.getDirectoryInfo(skin_path)
        for folderId in info.getSubdirs():
            DirectoryView.manage_addDirectoryView(ssc, pathjoin(skin_path, folderId))

        self._setObject(ssc.id, ssc)
        return

    def getCategories(self):
        """
          returns list of all design categories
        """
        categories = {}
        for skin in self.objectValues():
            categories[skin.getCategory()] = 1

        return categories.keys()
        return

    def getSkinsInCategory(self, category):
        """
          returns list of all skins in category 'category'
        """
        return [_[1] for skin in self.objectValues() if skin.getCategory() == category]
        return

    def manage_addSkinContainer(self, REQUEST=None):
        """
          adds skin container to repository
        """
        ssc = SiteSkinContainer()
        self._setObject(ssc.id, ssc)
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)
        return

    def manage_reloadSkins(self, REQUEST=None):
        """
          reloads skin views to repository

          works after product refresh only
        """
        for itemId in self.objectIds():
            self._delObject(itemId)

        DirectoryView._dirreg.reloadDirectory(self._site_skins_path)
        for skinId in DirectoryView._dirreg.getDirectoryInfo(self._site_skins_path).getSubdirs():
            DirectoryView._dirreg.reloadDirectory(self._site_skins_path + pathdelim + str(skinId))

        for skinId in DirectoryView._dirreg.getDirectoryInfo(self._site_skins_path).getSubdirs():
            self.addSkin(skinId)

        if REQUEST is not None:
            return self.manageForm(self, REQUEST)
        return


InitializeClass(DesignRepositoryTool)

class SiteSkinContainer(ObjectManager, SimpleItem):
    """
      site skin container class
    """
    __module__ = __name__
    manage_options = ObjectManager.manage_options + ({'label': 'Property', 'action': 'propertyForm'},)
    propertyForm = DTMLFile('dtml/propertyDesign', globals())
    _title = None
    _cat = None

    def __init__(self, id, path):
        self.id = id
        self._path = path
        self.loadDescription()
        return

    def loadDescription(self):
        """
          loads skin description: title, design category, description
        """
        path = expandpath(self._path)
        description_file = open(pathjoin(path, 'description.txt'))
        lines = description_file.readlines()
        for i in range(len(lines)):
            line = lines[i]
            if line.strip() == 'description':
                self._description = ('\n').join(lines[i + 1:]).strip()
                break
            else:
                try:
                    (name, value) = line.split('=')
                except ValueError:
                    pass
                else:
                    if name.strip() == 'title':
                        self._title = value.split("'")[1].strip()
                    elif name.strip() == 'category':
                        self._cat = value.split("'")[1].strip()

        description_file.close()
        screenshot = open(pathjoin(path, 'screenshot.jpg'), 'rb')
        self.screenshot = SiteImage(id='screenshot', file=screenshot)
        screenshot.close()
        return

    def getDescription(self):
        """
          returns design description
        """
        return self._description
        return

    def title_or_id(self):
        """
          returns design title or id
        """
        return self._title or self.id
        return

    def getCategory(self):
        """
          returns design category
        """
        return self._cat
        return


InitializeClass(SiteSkinContainer)

def initialize(context):
    context.registerTool(DesignRepositoryTool)
    return
