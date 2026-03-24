## Script (Python) "reconfig_mail_subjects"
##title=Configure mail subjects
##parameters=rebuild_ids=[],refresh_ids=[],target_folder=None,before_date=None
##
# $Id: manage_sanation.py,v 1.1 2009/02/17 15:04:22 oevsegneev Exp $

from Products.CMFNauTools.SecureImports import SimpleError

REQUEST = context.REQUEST
message = ""
params = {}

if REQUEST.has_key('rebuild'):
    context.portal_sanation.rebuildCatalogs( rebuild_ids )
    message = "maintenance_pack.rebuild_completed"

elif REQUEST.has_key('refresh'):
    context.portal_sanation.refreshCatalogs( refresh_ids )
    message = "maintenance_pack.refresh_completed"

elif REQUEST.has_key('clean_tree'):
    removed, bad = context.portal_sanation.cleanFolder( target_folder, before_date )
    message = "maintenance_pack.clean_tree_completed"
    params = {'removed':removed, 'bad':bad}

context.redirect( action='manage_sanation_form', message=message, params=params )
