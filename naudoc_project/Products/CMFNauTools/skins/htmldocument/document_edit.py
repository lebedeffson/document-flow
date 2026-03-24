## Script (Python) "document_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=text_format=None, text=None, SafetyBelt='', poll='', file='', doc_type=None, delete=None, pastefile=None, attachfile=None, associatefile=None, rm_associate=None, id=None, upload=None, log_message='', try_to_associate=None, lockfile=None
##title=Handler for the document editing form.
##
# $Editor: vpastukhov $
# $Id: document_edit.py,v 1.51 2006/04/12 06:11:18 oevsegneev Exp $
# $Revision: 1.51 $

from Products.CMFNauTools.SecureImports import SimpleError, ResourceLockedError, BadRequestException

REQUEST = context.REQUEST
message = ''

member = context.portal_membership.getAuthenticatedMember()
username = member.getUserName()

try:
    if text is not None:
        try:
            context.edit(text_format, text, file, safety_belt=SafetyBelt)
            context.setCategoryAttributes(
                context.process_attributes(object = context,
                                           pattern = 'attribute/%s',
                                           REQUEST = REQUEST)
                )
            message = "Document saved."
        except SimpleError, error_text:
            message = "Please specify mandatory attribute: " + str(error_text)

    if attachfile and upload:
        try:
            context.addFile( upload, id=id, paste=1, try_to_associate=try_to_associate )
        except (SimpleError, BadRequestException), text:
            return apply( context.document_attaches, (context, REQUEST),
                          script.values( portal_status_message=str(text) ) )
        message = "The file has been attached."

    if pastefile:
        id = REQUEST['pastefile']
        # 'size' is used while generating an image preview thumbnail
        size = REQUEST.get('%s_size' % id, None)
        context.pasteFile(pastefile, size)
        message = "Link to the attachment has been inserted."

    if delete:
        for id in REQUEST['ids']:
            context.removeFile(id)

        message = "The attachment has been removed."

    if rm_associate:
        context.removeAssociation(rm_associate)
        message = "The association with attachment has been removed."

    if associatefile:
        context.associateWithAttach(associatefile)
        message = "The association with attachment has been added."

    if lockfile:
        if context.lockAttachment(lockfile):
            message = "The file has been locked."
        else:
            message = "The file has not been locked."

    # Update the document 'modification' date
    # todo: document.setEffectiveDate(DateTime())

    if log_message:
        ts = str(int(DateTime()))
        context.changes_log.append( { 'date'   : ts
                                    , 'member' : username
                                    , 'comment': log_message
                                    } )

    if text  or associatefile or (attachfile and try_to_associate):
        no_clean_html = not context.portal_membership.getInterfacePreferences('cleanup')
        context.cleanup(no_clean_html)

except 'EditingConflict', text:
    return context.document_conflict_form( context, REQUEST=REQUEST )

except ResourceLockedError:
    message = "Since document is locked, it was not saved."

except SimpleError, msg:
    message = msg

action = (lockfile or attachfile or delete or associatefile or rm_associate) and 'document_attaches' or 'document_edit_form'
return context.redirect( action=action, message=message, frame='inFrame' )
