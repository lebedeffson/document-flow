# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/StaffListDirectory/__init__.py
# Compiled at: 2008-06-04 16:46:22
"""
This addon does not fully implement functionality enabling staff list directory 
support which is a part of NauDoc core. Addon is only responsible for creating 
the directory object.

XXX: Add StaffListDirectory class derived from DirectoryObject. This class should 
implement some custom behaviour as well as positions/divisions cache.

$Editor: ikuleshov $
$Id: __init__.py,v 1.8 2008/06/04 12:46:22 oevsegneev Exp $
"""
__version__ = '$Revision: 1.8 $'[11:-2]
AddonId = 'StaffListDirectory'
AddonTitle = 'Staff list directory'
AddonVersion = '1.5'
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.Exceptions import AddonError, AddonDeactivateError
from Products.CMFNauTools.MembershipTool import MembershipTool
from Products.CMFNauTools.Utils import translate
Directories = (
 (
  'post_list_directory', ({'name': 'disable_for_properties', 'type': 'boolean'},)), ('department_list_directory', ({'name': 'disable_for_properties', 'type': 'boolean'},)), ('employee_list_directory', ({'name': 'employee_f', 'type': 'string'}, {'name': 'employee_i', 'type': 'string'}, {'name': 'employee_o', 'type': 'string'}, {'name': 'associate_user', 'type': 'userlist'}, {'name': 'disable_for_properties', 'type': 'boolean'})), ('staff_list_directory', ({'name': 'division', 'usage': (0, 1), 'type': 'link', 'link_directory': 'department_list_directory'}, {'name': 'position', 'type': 'link', 'link_directory': 'post_list_directory'}, {'name': 'employee', 'type': 'link', 'link_directory': 'employee_list_directory'}, {'name': 'deputy', 'type': 'link', 'link_directory': 'employee_list_directory'}, {'name': 'disable_for_properties', 'type': 'boolean'}, {'name': 'disable_for_permissions', 'type': 'boolean'}, {'name': 'disable_for_task', 'type': 'boolean'})))
order = 80

def initialize(context, app):
    context.registerAddon(AddonId, title=AddonTitle, version=AddonVersion, activate=True, order=order)
    return


def activate(portal):
    portal.addLocalizerMessages(globals())
    addons_tool = getToolByName(portal, 'portal_addons')
    if not addons_tool.hasActiveAddon('DirectoryObject'):
        addons_tool.activateAddons('DirectoryObject')
    if not addons_tool.hasActiveAddon('DirectoryObject'):
        raise AddonError, 'Unable to start StaffList addon. Please install DirectoryObject addon first.'
    directories = portal.getProperty('directories_folder')
    for (id, columns) in Directories:
        directory = directories._getOb(id, None)
        if not directory:
            directories.invokeFactory(type_name='Directory', id=id, title=translate(portal, 'StaffList.%s' % id))
            directory = directories._getOb(id)
            for entry in columns:
                column = directory.addColumn(entry['name'], entry['type'])
                title = translate(portal, 'StaffList.%s' % entry['name'])
                column.setTitle(title)
                if entry.has_key('usage'):
                    column.setUsage(*entry['usage'])
                if entry.has_key('link_directory'):
                    scope = directories._getOb(entry['link_directory']).getUid()
                    column.setProperties({'allowed_categories': (), 'allowed_types': ('Directory',), 'scope': scope})

        if id in ['staff_list_directory', 'employee_list_directory']:
            membership = getToolByName(portal, 'portal_membership')
            membership._updateProperty(id, directory)

    return


def deactivate(portal):
    for (id, columns) in Directories:
        if id in ['staff_list_directory', 'employee_list_directory']:
            membership = getToolByName(portal, 'portal_membership')
            membership._updateProperty(id, None)

    return
