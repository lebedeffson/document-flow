"""
$Id: remove_vote_objects.py,v 1.2 2005/05/14 05:43:46 vsafronovich Exp $
$Editor: ikuleshov $
"""
__version__ = '$Revision: 1.2 $'[11:-2]

title = 'Remove Vote objects'
version = '3.2.0.0'
classes = ['Products.CMFNauTools.Vote.Vote']

def migrate( context, object ):
    container = context.container
    if hasattr( container, '_delObject' ):
        container._delObject( context.name )
