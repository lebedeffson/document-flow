######################################################################
#
# utils     A collection of utility functions
#
# This software is governed by a license. See 
# LICENSE.txt for the terms of this license.
#
######################################################################
__version__='$Revision: 1.4 $'[11:-2]

from types import UnicodeType, StringType
import urllib, sha, SSHA, random, base64, codecs, string


#################################################
# "Safe" imports for use in the other modules
#################################################

try:
    import crypt
    HAVE_CRYPT = 1
except ImportError:
    crypt = None
    HAVE_CRYPT = 0

import ldap

#################################################
# Constants used in other modules
#################################################

HTTP_METHODS = ('GET', 'PUT', 'POST')

ldap_scopes = (ldap.SCOPE_BASE, ldap.SCOPE_ONELEVEL, ldap.SCOPE_SUBTREE)

GROUP_MEMBER_MAP = { 'groupOfUniqueNames' : 'uniqueMember'
                   , 'groupOfNames' : 'member'
                   , 'accessGroup' : 'member'
                   , 'group' : 'member'
                   }

encoding = 'utf8'
user_encoding = 'cp1251'


#################################################
# Helper methods for other modules
#################################################

def _verifyUnicode(st):
    """ Verify that the string is unicode """
    if type(st) is UnicodeType:
        return st
    else:
        try:
            return unicode(st)
        except UnicodeError:
            return unicode(st, user_encoding)


def _createLDAPPassword(password, encoding='SHA'):
    """ Create a password string suitable for userPassword """
    if encoding == 'SSHA':
        pwd_str = '{SSHA}' + SSHA.encrypt(password)
    elif encoding == 'crypt':
        saltseeds = list('%s%s' % ( string.lowercase[:26]
                                  , string.uppercase[:26]
                                  ) )
        salt = ''
        for n in range(2):
            salt += random.choice(saltseeds)
        pwd_str = '{crypt}%s' % crypt.crypt(password, salt)
    elif encoding == 'clear':
        pwd_str = password
    else:
        sha_obj = sha.new(password)
        sha_dig = sha_obj.digest()
        pwd_str = '{SHA}' + base64.encodestring(sha_dig)

    return pwd_str.strip()


try:
    encodeLocal, decodeLocal, reader = codecs.lookup(user_encoding)[:3]
    encodeUTF8, decodeUTF8 = codecs.lookup('UTF-8')[:2]

    if getattr(reader, '__module__', '')  == 'encodings.utf_8':
        # Everything stays UTF-8, so we can make this cheaper
        to_utf8 = from_utf8 = str

    else:

        def from_utf8(s):
            return encodeLocal(decodeUTF8(s)[0])[0]

        def to_utf8(s):
            return encodeUTF8(decodeLocal(s)[0])[0]


except LookupError:
    raise LookupError, 'Unknown encoding "%s"' % user_encoding


