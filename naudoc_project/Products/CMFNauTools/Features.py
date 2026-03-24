"""
Features are simplified interfaces used to describe class instances.

$Editor: vpastukhov $
$Id: Features.py,v 1.30 2007/07/19 07:59:14 oevsegneev Exp $
"""
__version__ = '$Revision: 1.30 $'[11:-2]

try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

from new import classobj as _classobj

class Feature( Interface ): pass

# portal

class isPortalRoot(Feature): pass
class isTool(Feature): pass
class isCatalog(Feature): pass

# content

class isPortalContent(Feature): pass
class isExternallyEditable(Feature): pass
class hasLanguage(Feature): pass
class reindexAfterRefresh(Feature): pass
class containsQuery(Feature): pass

# interfaces

class isCategorial(Feature): pass
class isLockable(Feature): pass
class isVersionable(Feature): pass
class isVersion(Feature): pass
class isItemsRealm(Feature): pass
class isAttributesProvider(Feature): pass
class hasTabs(Feature):
    def listTabs():
        """
           TODO
        """
class hasHeadingInfo(Feature):
    def getHeadingInfo():
        """
           TODO
        """
# documents

class isDocument(Feature): pass
class isCompositeDocument(Feature): pass
class isAttachment(Feature): pass
class isPrintable(Feature): pass
class isTemplate(Feature): pass

# folders

class isPrincipiaFolderish(Feature): pass
class isStatic(Feature): pass
class isContentStorage(Feature): pass
class canHaveSubfolders(Feature): pass
class hasContentFilter(Feature): pass

# site

class isSiteRoot(Feature): pass
class isPublishable(Feature): pass
class isSyncableContent(Feature): pass

# subscription

class hasSubscription(Feature): pass
class isSubscription(Feature): pass
class isSubscriptionRoot(Feature): pass

# tasks

class isTaskItem(Feature): pass
class canCreateTasks(Feature): pass

# others

class isImage(Feature): pass
class isFSFolder(Feature): pass
class isFSFile(Feature): pass
class isMessagingService(Feature): pass
class isDirectory(Feature): pass
class isNavigable(Feature): pass


def createFeature( name ):
    """
        Creates a new feature with a given name.
    """
    try:
        feature = _classobj( name, (Feature,), {} )
    except SystemError: # python2.1
        exec 'class %s ( Feature ): pass' % name
        feature = locals()[ name ]
    globals()[ name ] = feature
    return feature
