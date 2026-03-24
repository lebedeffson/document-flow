## Script (Python) "followup_ndreport_results"
##parameters=folder_uid, view_category, view_state,
##title=Search normative documents results
##
# $Id: followup_ndreport_results.py,v 1.7 2005/05/14 05:43:50 vsafronovich Exp $
# $Editor: vsafronovich$
# $Revision: 1.7 $
from DateTime import DateTime

from Products.CMFNauTools.SecureImports import parseDate

REQUEST = context.REQUEST

effective_date = parseDate('effective_date', REQUEST, '')
expiration_date = parseDate('expiration_date', REQUEST, '')
REQUEST.set('effective_date', effective_date)   #  need
REQUEST.set('expiration_date', expiration_date) #  correct date

if not folder_uid:
    message = 'Please choose beginning folder'
    REQUEST['RESPONSE'].redirect(context.absolute_url(action='followup_ndreport', message=message))
    return

catalog_tool = context.portal_catalog
folder = catalog_tool.searchResults( nd_uid=folder_uid )
if folder:
    folder_path = folder[0].getPath()
else:
    message = "This folder was deleted or you don't have access to it"
    REQUEST['RESPONSE'].redirect(context.absolute_url(action='followup_ndreport', message=message))
    return

query = {'meta_type': 'HTMLDocument',
         'path': folder_path,
         'sort_on': 'parent_path'
        }

if view_category:
    query['category'] = view_category

    min_max = {}
    for date_name in 'effective_date', 'expiration_date':
        value = parseDate( date_name, REQUEST, '' )
        if value:
            REQUEST.set( date_name, value)# need correct date
            min_max[ ['min','max'][date_name != 'effective_date'] ] = value

    query['CategoryAttributes'] = [ { 'attributes': [ view_category + '/dv' ]
                                    , 'query': min_max.values()
                                    , 'range': ':'.join( min_max.keys() )
                                    } ]

if view_state:
    query['state'] = view_state

results = catalog_tool.searchResults( **query )

items=[]
old_folder_path=''
for item in results:

    dv = item['CategoryAttributes']['dv']
    doc = item.getObject()

    copies = doc.listCopiesHolders()

    subordinate_docs_uids = doc.listSubordinateDocuments( version_dependent=1,
                                                          category_id='NormativeDocumentEdit',
                                                          state_id='effective')
    subordinate_docs_titles = []
    if subordinate_docs_uids:
        subordinate_docs_brains = catalog_tool.searchResults( nd_uid=subordinate_docs_uids)
        subordinate_docs_titles = [ brain['Title'] for brain in subordinate_docs_brains ]

    dv = same_type(dv, DateTime) and "%s.%s.%s"%(dv.dd(), dv.mm() , dv.year()) or dv# to avoid DateTime.strftime bug with too future and too past dates

    items.append({'Title': item['Title'],
                  'Description': item['Description'],
                  'dv': dv,
                  'copies': copies,
                  'copies_nums': ', '.join( [ str( copy['number']) for copy in copies]),
                  'subordinate_docs_titles': subordinate_docs_titles,
                })

    new_folder_path = doc.parent_path()
    if new_folder_path != old_folder_path:
        old_folder_path = new_folder_path
        items[-1]['Folder'] = doc.aq_parent.Title()

return items
