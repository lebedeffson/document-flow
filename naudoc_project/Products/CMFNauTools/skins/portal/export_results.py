## Script (Python) "export_results"
##title=Export data to Excel
##
# $Editor: ishabalin $
# $Id: export_results.py,v 1.4 2004/03/09 15:02:21 vpastukhov Exp $
# $Revision: 1.4 $

REQUEST = context.REQUEST
setHeader = REQUEST.RESPONSE.setHeader
query_id = REQUEST.get('nd_query_id', None)
query = context.portal_catalog.getQuery(query_id, REQUEST=REQUEST)

filename = (context.msg('Search results')).replace(' ', '_')

setHeader = REQUEST.RESPONSE.setHeader
setHeader("Content-Type", "application/vnd.ms-excel; name='excel'");
setHeader("Content-type", "application/octet-stream");
setHeader("Content-Disposition", "attachment; filename=%s.xls" % filename);
setHeader("Cache-Control", "must-revalidate, post-check=0, pre-check=0");
setHeader("Pragma", "no-cache");
setHeader("Expires", "0");

result_content = context.search_results_ndocument_excel (   context,
                                                            query=query,
                                                            REQUEST=REQUEST)
return result_content
