"""
Skinnable views tool.

$Editor: vpastukhov $
$Id: SkinsTool.py,v 1.9 2005/10/19 05:01:43 vsafronovich Exp $
"""
__version__ = '$Revision: 1.9 $'[11:-2]

from os import path as os_path
from string import strip

from AccessControl import ClassSecurityInfo
from App.Common import package_home

from Products.CMFCore.SkinsTool import SkinsTool as _SkinsTool
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFCore.utils import getToolByName

import Config
from Exceptions import SimpleError
from SimpleObjects import ToolBase, ContainerBase
from Utils import InitializeClass, joinpath, minimalpath, makepath, pathdelim


class SkinsTool( ToolBase, ContainerBase, _SkinsTool ):
    """
        Portal skinnable views tool.
    """
    _class_version = 1.0

    meta_type = 'NauSite Skins Tool'
    id = 'portal_skins'
    isPrincipiaFolderish = 1   # for ZMI

    security = ClassSecurityInfo()

    __implements__ = ToolBase.__implements__, \
                     _SkinsTool.__implements__

    manage_options = _SkinsTool.manage_options
    manage_propertiesForm = _SkinsTool.manage_propertiesForm

    def __init__( self ):
        ToolBase.__init__( self )
        _SkinsTool.__init__( self )

    security.declarePrivate( 'addSkinLayer' )
    def addSkinLayer( self, id, path, namespace=None, skin=None, before=None, after=None ):
        """
            Adds a new skin layer into the skins container.

            Positional arguments:

                'id' -- view Id, string

                'path' -- filesystem path to the directory containing
                          skin files

                'namespace' -- optional globals dictionary, required if the
                               path is relative to another package

            Keyword arguments:

                'skin' -- skin name; if omitted, default skin is used

                'before' -- view Id, place the new view before this existing view

                'after' -- view Id, place the new view after this existing view

        """
        # ensure the path is absolute
        if not os_path.isabs( path ):
            if namespace is None:
                namespace = globals()
            package_path = minimalpath( package_home( namespace ) )
            path = joinpath( package_path, path )

        # TODO: handle paths better
        path = path.replace( '\\', pathdelim )
        # may raise DuplicateIdError
        self.manage_addProduct['CMFCore'].manage_addDirectoryView( path, id )

        if not skin:
            skin = self.getDefaultSkin()

        skin_path = self.getSkinPath( skin )
        if skin_path is None:
            raise KeyError, skin

        # append view Id to the skin selections
        paths = map( strip, skin_path.split(',') )
        if id not in paths:

            if before is after is None:
                place = len(paths)
            elif after is None:
                # before is not None
                place = paths.index(before) # may raise IndexError
            elif before is None:
                # after is not None
                place = paths.index(after) + 1 # may raise IndexError
            else:
                raise SimpleError("'before' and 'after' parameters giving, this is not supported.") # TODO

            paths.insert( place, id )

            self.addSkinSelection( skin, ','.join(paths) )

    security.declarePrivate( 'deleteSkinLayer' )
    def deleteSkinLayer( self, id, skin=None ):
        """
            Removes a skin layer from the skins container.

            Positional arguments:

                'id' -- view Id, string

            Keyword arguments:

                'skin' -- skin name; if omitted, default skin is used
        """
        if not skin:
            skin = self.getDefaultSkin()

        skin_path = self.getSkinPath( skin )
        if skin_path is None:
            raise KeyError, skin

        # remove view Id from the skin selections
        paths = map( strip, skin_path.split(',') )
        if id in paths:
            paths.remove( id )
            self.addSkinSelection( skin, ','.join(paths) )

        try:
            self._delObject( id )
        except AttributeError:
            pass

InitializeClass( SkinsTool )

# depends on Config.SkinViews and Config.PublicViews constants
class SkinsInstaller:
    def install(self, p):
        ps = getToolByName(p, 'portal_skins')

        ps.manage_addProduct['OFSP'].manage_addFolder(id='custom')

        ps.addSkinSelection( 'Site', 'custom', make_default=1 )

        for view in Config.SkinViews:
            ps.addSkinLayer( view, 'skins/%s' % view, globals() )

        # these skin elements are available for anonymous visitors
#        for name in Config.PublicViews:
#            ps[ name ].manage_permission( CMFCorePermissions.View, [Roles.Anonymous], 1 )

        ps.addSkinSelection( 'Mail', 'mail_templates' )

        p.setupCurrentSkin()

class DirectoryViewsInstaller:
    def install(self, target):
        for path in 'manual', 'fckeditor':
            createDirectoryView(target, makepath(path))


def initialize( context ):
    # module initialization callback

    context.registerTool( SkinsTool )

    context.registerInstaller( SkinsInstaller )
    context.registerInstaller( DirectoryViewsInstaller )
