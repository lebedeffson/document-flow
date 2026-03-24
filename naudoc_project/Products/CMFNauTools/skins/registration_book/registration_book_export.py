## Script (Python) "registration_book_export"
##title=Export data to Excel
##
# $Editor: ishabalin $
# $Id: registration_book_export.py,v 1.2 2004/04/12 08:51:53 ishabalin Exp $
# $Revision: 1.2 $

REQUEST = context.REQUEST
setHeader = REQUEST.RESPONSE.setHeader

filename = context.title_or_id().replace( ' ', '_' )
setHeader = REQUEST.RESPONSE.setHeader
setHeader("Content-Type", "application/vnd.ms-excel; name='excel'");
setHeader("Content-type", "application/octet-stream");
setHeader("Content-Disposition", "attachment; filename=%s.xls" % filename);
setHeader("Cache-Control", "must-revalidate, post-check=0, pre-check=0");
setHeader("Pragma", "no-cache");
setHeader("Expires", "0");

result_content = context.registration_book_excel (  context,
                                                    REQUEST=REQUEST)
return result_content
