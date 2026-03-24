## Script (Python) "folder_edit"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=display_mode=None, mail_login=None, mail_password=None, mail_keep=None, mail_interval=None, mail_from_name=None, mail_from_address=None, mail_recipients=None
##title=Handler for the folder settings form.
##
# $Editor: vpastukhov $
# $Id: folder_edit.py,v 1.31 2005/08/12 10:28:43 vsafronovich Exp $
# $Revision: 1.31 $

from Products.CMFNauTools.SecureImports import SimpleError, refreshClientFrame

REQUEST = context.REQUEST

if mail_password is not None:
    if len(mail_password) and not len(mail_password.replace('*', '')):
        mail_password = None

    elif mail_password != REQUEST['mail_password2']:
        return apply( context.folder_edit_form, (context, REQUEST),
                      script.values( portal_status_message="Mail account password and confirmation do not match." ) )

if display_mode is not None and not display_mode:
    context.setMainPage( None )

if REQUEST.has_key('maxNumberOfPages'):
    context.setMaxNumberOfPages( int(REQUEST['maxNumberOfPages']) )

if REQUEST.has_key('varchive_settings'):
    context.setArchiveProperty( REQUEST['varchive_settings'] )

if REQUEST.has_key('allowed_categories'):
    context.setAllowedCategories( REQUEST['allowed_categories'] )
elif not REQUEST.has_key('category_inheritance'):
    return apply( context.folder_edit_form, (context, REQUEST), # TODO
            script.values( portal_status_message = "Select one or more allowed categories first." ) )
else:
    context.setAllowedCategories( [] )

context.setCategoryInheritance( REQUEST.has_key('category_inheritance') )

props = {}
test_mail = 0

if context.implements('isIncomingMailFolder'):
    if mail_login and mail_login != context.mail_login:
        test_mail = 1

    if mail_password is not None:
        props['mail_password'] = mail_password
        test_mail = 1

elif context.implements('isOutgoingMailFolder'):
    if mail_recipients is not None:
        props['mail_recipients'] = mail_recipients.replace(',', ' ').split()

try:
    context.manage_changeProperties( REQUEST, **props )
    if test_mail:
        context.testServer()

except SimpleError, error:
    if not test_mail:
        error.abort()
    return apply( context.folder_edit_form, (context, REQUEST),
                  script.values( portal_status_message=error ) )

refreshClientFrame('navTree')
refreshClientFrame('workspace')

return context.redirect( frame='inFrame', message="Folder changed" )
