"""
$Id: SchedulerTool.py,v 1.5 2006/07/25 06:43:24 oevsegneev Exp $
$Editor: ikuleshov $
"""
__version__='$Revision: 1.5 $'[11:-2]

import new
from sys import modules

from Globals import DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.NauScheduler import product_globals as scheduler_globals
from Products.NauScheduler.Scheduler import Scheduler

from ActionInformation import ActionInformation as AI
from SimpleObjects import ToolBase
from Utils import InitializeClass

class SchedulerTool( ToolBase, Scheduler ):

    id = 'portal_scheduler'
    meta_type = 'NauSite Scheduler Tool'

    _actions = ( AI( id='manage'
                   , title='Manage scheduler'
                   , action=Expression(text='string: ${portal_url}/manage_scheduler_form')
                   , permissions=( CMFCorePermissions.ManagePortal, )
                   , category='global'
                   , visible=1
                   ),
               )

    security = ClassSecurityInfo()

    manage_options = ( Scheduler.manage_options +
                       ({ 'label' : 'Overview', 'action' : 'manage_overview' },
                       ) +
                       ToolBase.manage_options
                     )

    def __init__(self):
        ToolBase.__init__(self)
        Scheduler.__init__(self, id=self.getId() )

    #
    #   ZMI methods
    #
    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'dtml/explainSchedulerTool', scheduler_globals )

    def _containment_onAdd(self, item, container):
        Scheduler.manage_afterAdd(self, item, container)

    def _containment_onDelete( self, item, container ):
        Scheduler.manage_beforeDelete(self, item, container)

InitializeClass( SchedulerTool )

def initialize( context ):

    context.registerTool( SchedulerTool )

SchedulerTool_module = new.module('SchedulerTool')
SchedulerTool_module.SchedulerTool = SchedulerTool
modules['Products.NauScheduler.SchedulerTool'] = SchedulerTool_module
