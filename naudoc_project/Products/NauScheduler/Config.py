"""
Global settings.

$Id: Config.py,v 1.6 2004/06/11 12:21:10 vpastukhov Exp $
$Editor: ikuleshov $
"""
from mx.DateTime import RelativeDateTime

__version__ = '$Revision: 1.6 $'[11:-2]

ProductName             = 'NauScheduler'

QueueExpirationIterval  = RelativeDateTime( minutes=5 )
MaxThreadsCount         = 3
AutoStartDaemonThreads  = 1
DisableScheduler        = 0

DefaultLogFile = 'scheduler.log'
DefaultLogSeverity = -500

ActiveState = 'active'
RunnableState = 'runnable'
ZombieState = 'zombie'
SuspendedState = 'suspended'

#===========================================================================

class States: pass

for name, value in globals().items():
    if name[-5:] == 'State':
        States.__dict__[ name[:-5] ] = value

#===========================================================================
