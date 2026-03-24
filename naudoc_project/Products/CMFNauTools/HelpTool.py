""" HelpTool class
$Id: HelpTool.py,v 1.7 2005/04/19 13:59:04 vsafronovich Exp $
"""
__version__='$Revision: 1.7 $'[11:-2]

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression

from ActionInformation import ActionInformation as AI
from SimpleObjects import ToolBase
from Utils import InitializeClass

class HelpTool( ToolBase ):

    _class_version = 1.00

    meta_type = 'NauSite Help Tool'
    id = 'portal_help'

    _actions = ( AI( id='about'
                   , title='About NauDoc'
                   , action=Expression(text='string: ${portal_url}/about')
                   , permissions=(CMFCorePermissions.View,)
                   , category='help'
                   , condition=None
                   , visible=True
                   )
               , AI( id='about'
                   , title='User manual'
                   , action=Expression(text='string: ${portal_url}/manual')
                   , permissions=(CMFCorePermissions.View,)
                   , category='help'
                   , condition=None
                   , visible=True
                   )
               )

InitializeClass( HelpTool )

def initialize( context ):
    # module initialization callback

    context.registerTool( HelpTool )
