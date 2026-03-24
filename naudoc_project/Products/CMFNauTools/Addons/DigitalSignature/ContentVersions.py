# uncompyle6 version 3.9.3
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.14.3 (main, Feb 13 2026, 15:31:44) [GCC 15.2.1 20260209]
# Embedded file name: /home/naudoc/DistributiveMonster/build/10.03.2009_19-24/Products/CMFNauTools/Addons/DigitalSignature/ContentVersions.py
# Compiled at: 2008-06-18 14:06:31
""" 
$Id: ContentVersions.py,v 1.3 2008/06/18 10:06:31 oevsegneev Exp $

$Editor: oevsegneev $

"""
__version__ = '$Revision: 1.3 $'[11:-2]
from ZODB.PersistentList import PersistentList
from Products.CMFNauTools.ContentVersions import ContentVersion
from utils import class_patch

class ContentVersion_patch(class_patch):
    """ 
        Patch of simple version class.
    """
    __module__ = __name__
    _signatures = []

    def __init_patch__(self, id, title='', description=''):
        """
            Class initialization patch
        """
        ContentVersion.old___init__(self, id=id, title=title, description=description)
        self._signatures = PersistentList()
        return


def initialize(context):
    ContentVersion_patch(ContentVersion, backup=True)
    return
