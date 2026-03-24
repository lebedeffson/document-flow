## Script (Python) "tray_agent_settings"
##title=
##parameters=REQUEST=None
from Products.CMFNauTools.SecureImports import SimpleError

member = context.portal_membership.getAuthenticatedMember()
try:
    if not REQUEST.get('ta_check_interval') > 0:
        raise SimpleError, 'Check interval must be a positive integer number'

    sound_alert = REQUEST.get('ta_sound_alert')
    open_browser = REQUEST.get('ta_open_browser') 
    balloon_tips = REQUEST.get('ta_balloon_tips')
    if not( sound_alert or open_browser or balloon_tips ):
        raise SimpleError, 'Specify at least one notification action'

    member.setProperties( REQUEST.form )
except SimpleError, error:
    error.abort()
    return apply( context.tray_agent_settings_form, (context,),
                 script.values( portal_status_message=str(error) )  )

url = context.absolute_url( action='tray_agent_settings_form',
                            params={ 'portal_status_message': 'Changes saved' } 
                          )

context.REQUEST['RESPONSE'].redirect( url )
