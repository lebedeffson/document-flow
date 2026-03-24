"""
Secure symbols available for import from Python Scripts.

$Editor: vpastukhov $
$Id: SecureImports.py,v 1.35 2008/10/15 12:26:55 oevsegneev Exp $
"""
__version__ = '$Revision: 1.35 $'[11:-2]

from re import split as re_split

from ZODB.PersistentList import PersistentList
from ZODB.PersistentMapping import PersistentMapping

from Products.NauScheduler.TemporalExpressions import DailyTE, WeeklyTE, MonthlyByDayTE, \
                                                      MonthlyByDateTE, YearlyTE, DateTimeTE, \
                                                      UnionTE

from Explorer import getExplorerType, getExplorerById
from Exceptions import formatErrorValue, SimpleError, ResourceLockedError, SentinelError, \
        InvalidIdError, ReservedIdError, DuplicateIdError, CopyError, Unauthorized, BadRequestException
from Mail import MailMessage
from SimpleObjects import SimpleRecord
from Utils import refreshClientFrame, parseDate, parseTime, parseDateTime, cookId, joinpath, listClipboardObjects, updateLink
from PatternProcessor import listExplanations

# end of imported symbols

from AccessControl import ModuleSecurityInfo, allow_class
from types import ClassType

# make everything in this module public
ModuleSecurityInfo(__name__).setDefaultAccess(1)

name = item = value = None

for name, item in globals().items():
    # skip hidden (protected attributes)
    if name.startswith('_'):
        continue

    # __basicnew__ is used to check for extension classes
    if type(item) is ClassType or hasattr( item, '__basicnew__' ):
        # skip classes with existing permissions
        if item.__dict__.has_key( '__ac_permissions__' ):
            continue

        # skip classes with existing ClassSecurityInfo
        for value in item.__dict__.values():
            if hasattr( value, '__security_info__' ):
                break
        else:
            # the class has no security info on it, make it public
            allow_class( item )
            # allow setitem and getitem calls too
            # XXX what about setattr and delattr???
            if hasattr( item, '__setitem__' ) and not hasattr( item, '__guarded_setitem__' ):
                item.__guarded_setitem__ = item.__setitem__
            if hasattr( item, '__delitem__' ) and not hasattr( item, '__guarded_delitem__' ):
                item.__guarded_delitem__ = item.__delitem__

del name, item, value
del ModuleSecurityInfo, allow_class, ClassType
