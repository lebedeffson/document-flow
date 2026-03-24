"""
$Id: update_indexes.py,v 1.5 2008/04/08 13:11:18 oevsegneev Exp $
$Editor: oevsegneev $
"""
__version__ = '$Revision: 1.5 $'[11:-2]

title = "Update catalog indexes"
version = '3.4.0.0'
before_script = 1
order = 100

indexes = ['implements', 'nd_uid', 'CategoryAttributes']

from Products.CMFCore.utils import getToolByName

def migrate( context, object ):
    context.markForReindex( catalog='portal_catalog', idxs=indexes )
