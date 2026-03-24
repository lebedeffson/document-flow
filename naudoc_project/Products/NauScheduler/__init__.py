"""
$Id: __init__.py,v 1.20 2005/10/27 04:36:23 vsafronovich Exp $
"""
__version__ = '$Revision: 1.20 $'[11:-2]

import ZODB

import threading

from zLOG import LOG, TRACE, DEBUG, INFO, ERROR

import Config
import Scheduler
import SchedulersList

product_globals = globals()

_started = 0
_threads = []

def startThreads( *args ):
    global _started, _threads
    while _threads:
        t = _threads.pop(0)
        try:
            if t.getName().find('NauScheduler') == 0 and not t.isAlive():
                t.start()
        except:
            pass
    _started = 1

def initialize(context):
    for module in [
                    Scheduler,
                    SchedulersList,
                    ScheduleElement
                  ]:
        module.initialize( context )

    product = context._ProductContext__prod
    Config.ProductName    = product.id
    Config.ProductVersion = product.version.split()[-1]

    if _started:
        return

    app = context._ProductContext__app
    schedulers_list = getattr( app, 'SchedulersList', None )
    if schedulers_list:
        for scheduler in schedulers_list.listSchedulers():
            _threads.append( scheduler.startDaemon( postpone=1 ) )

    if not _started and Config.AutoStartDaemonThreads:
        #its safe to start threads here because their run() method waits for Zope startup.
        startThreads()
