"""
Migration script -- Update FS Folders and FS Files from version prior 2.0.

$Editor: kfirsov $
$Id: update_fsobjects.py,v 1.1 2004/04/28 12:27:24 kfirsov Exp $
"""
__version__ = '$Revision: 1.1 $'[11:-2]

title = 'Update FS Folders and FS Files'

classes = ['Products.CMFNauTools.FSFolder.FSFolder']

version = '3.1.2.61'

def migrate(context, object):
    object._completelyUpdate()
