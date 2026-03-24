## Script (Python) "explorer_open"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=item=''
##title=
##
# $Id: explorer_init.py,v 1.6 2006/04/05 14:14:38 ikuleshov Exp $
# $Editor: vsafronovich$
# $Revision: 1.6 $

from Products.CMFNauTools.SecureImports import getExplorerType, getExplorerById
REQUEST = context.REQUEST
h = REQUEST.has_key

# create or get explorer
if h( 'open_explorer' ):                                                 
    root = context.portal_catalog.getObjectByUid( REQUEST.form.get('root') ) or context
    ExplorerType = getExplorerType( root )
    explorer = ExplorerType( root, **REQUEST.form )
elif h( 'explorer_id' ):
    explorer = getExplorerById( REQUEST['explorer_id'] )
    explorer.reassign(context)
else:
    raise RuntimeError('no explorer found')
return explorer
