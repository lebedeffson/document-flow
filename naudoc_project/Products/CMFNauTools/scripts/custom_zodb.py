"""
Set up customized database for use by the Zope server.

$Editor: vpastukhov $
$Id: custom_zodb.py,v 1.3 2004/02/08 14:01:37 vpastukhov Exp $
"""
__version__ = '$Revision: 1.3 $'[11:-2]

from os import getenv
from os.path import join as joinpath

import ZODB, Globals
from ZODB.FileStorage import FileStorage

try:
    from bsddb3Storage.Full import Full as bsddb3Full
except ImportError:
    bsddb3Full = None

try:
    from ZEO.ClientStorage import ClientStorage
except ImportError:
    ClientStorage = None

zeo = getenv('ZEO_SERVER')
dbname = getenv('ZODB_STORAGE')
dbtype = None

try: dbtype, dbname = dbname.split( ':', 1 )
except: pass

if zeo and ClientStorage:
    host, port = zeo.split( ':', 1 )
    Storage = ClientStorage( (host, int(port)) )

elif dbtype == 'bsddb3' and bsddb3Full:
    dbpath = dbname and joinpath( Globals.data_dir, dbname ) or Globals.data_dir
    DB = ZODB.DB( bsddb3Full( dbpath ) )

else:
    dbfile = dbname and joinpath( Globals.data_dir, dbname ) or Globals.BobobaseName
    DB = ZODB.DB( FileStorage( dbfile ) )
