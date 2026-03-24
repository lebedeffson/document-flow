"""
Migration script -- setup the portal categories phase 1.

$Editor: oevsegneev $
$Id: setup_categories_phase1.py,v 1.16 2006/09/27 10:03:45 oevsegneev Exp $
"""
__version__ = '$Revision: 1.16 $'[11:-2]

title = 'Setup the portal categories phase 1'
version = '3.2.0.115'

order = 57
before_script = 1

default_cats = ( 'Folder', 'SimpleDocument', 'Document', 'SimplePublication', \
                 'Publication', 'Directive', 'IncomingMail', 'OutgoingMail', \
                 'MailingItem', 'SimpleDocs', 'NormativeDocument', 'NormativeDocumentEdit', \
                 'ExternalNormativeDocument', 'ExternalNormativeDocumentEdit', 'CorrespondDocument', 'FBDocument', \
                 'UPDocument', 'InDocument', 'ISDocument', 'OPDocument', 'RDocument', 'PrikazBasic', \
               )

from Globals import DTMLFile
from Products.CMFCore.utils import getToolByName
from Products.CMFNauTools.NauSite import PortalGenerator

configuration_form = DTMLFile( 'dtml/setup_categories_form', globals() )

def check( context, object ):
    mdtool = getToolByName( object, 'portal_metadata' )
    categories = map( lambda c: c.getId(), mdtool.listCategories() )
    categories_to_update = [c for c in categories if c in default_cats]
    if categories_to_update:
        context.script_init[ __name__ ] =  { 'categories_to_update' : categories_to_update }
    else:
        try:
            del globals()['configuration_form']
        except:
            pass
    return True

def migrate( context, object ):
    mdtool = getToolByName( object, 'portal_metadata' )
    wftool = getToolByName( object, 'portal_workflow' )
    lnktool = getToolByName( object, 'portal_links' )

    for c in mdtool.listCategories():
        if not c.getWorkflow():
            wftool.createWorkflow( 'category_%s' % c.getId() )
            c.setWorkflow( 'category_%s' % c.getId() )

    categories_to_update = {}
    if context.script_options.has_key( __name__ ):
        script_options = context.script_options[ __name__ ]
        categories = context.script_init[ __name__ ][ 'categories_to_update' ]
        categories_to_update['replace'] = [c for c in categories if script_options.get( c, None ) == 'replace']
        categories_to_update['old'] = [c for c in categories if script_options.get( c, None ) == 'old']


        for c in categories_to_update['replace']:
            cat = mdtool.getCategoryById( c )
            ids = [l.id for l in lnktool.searchLinks( target=cat )]
            if ids:
                lnktool.removeLinks( ids=ids, restricted=Trust )
            mdtool.deleteObjects( c )
            wftool.deleteObjects( 'category_%s' % c )

        for c in categories_to_update['old']:
            cat = mdtool.getCategoryById( c )
            version = hasattr( context.portal, 'product_version' ) and context.portal.product_version or 'copy'
            cat.title = '( %s ) %s' % ( version, cat.Title() )
            new_cat_id = 'old_%s' % c
            idx = 1
            while mdtool.getCategoryById( new_cat_id ):
                new_cat_id = 'old%d_%s' % ( idx, c )
                idx += 1;
            new_wf_id = 'category_%s' % new_cat_id
            mdtool.manage_renameObject( c, new_cat_id )
            wftool.manage_renameObject( ('category_%s' % c), new_wf_id )
            wftool.bindWorkflow( new_wf_id )
            cat = mdtool.getCategory( new_cat_id )
            cat.setWorkflow( new_wf_id )

    PortalGenerator().setupCategories( object, 1 )
