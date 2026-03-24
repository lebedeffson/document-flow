"""
$Id: change_login_time.py,v 1.5 2007/11/16 13:37:10 oevsegneev Exp $
$Editor: spinagin $
"""
__version__ = '$Revision: 1.5 $'[11:-2]

title='Change default login time'
version = '3.4.0.0'

from Products.CMFCore.utils import getToolByName

def check( context, object ):
    p_md = getToolByName( object,'portal_memberdata')
    if p_md.getProperty('login_time')<>'' or p_md.hasProperty('last_login_time') :
        return True
    return False


def migrate( context, object ):
    p_md = getToolByName( object,'portal_memberdata')
    p_md.login_time=''
    if p_md.hasProperty('last_login_time'):
        p_md.manage_delProperties(['last_login_time'])
