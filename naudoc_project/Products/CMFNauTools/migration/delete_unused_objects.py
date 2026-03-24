"""
Migration script -- delete unused objects.

$Editor: spinagin $
$Id: delete_unused_objects.py,v 1.6 2005/05/14 05:43:46 vsafronovich Exp $
"""
__version__ = '$Revision: 1.6 $'[11:-2]

title = 'Delete unused objects'
version = '3.2.0.66'

names = [ 'plugins', 'tracker' ]

def check( context, object ):
    for name in names:
        if object.hasObject( name ):
            return True
    return False

def migrate( context, object ):
    objects2del = [ name for name in names if object.hasObject( name ) ]
    object.deleteObjects( objects2del )
