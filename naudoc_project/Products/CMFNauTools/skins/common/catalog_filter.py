## Script (Python) "catalog_filter"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=mode_name=None
##title=Save table filter settings
# $Editor: ikuleshov$
# $Id: catalog_filter.py,v 1.28 2007/06/29 12:25:30 oevsegneev Exp $
# $Revision: 1.28 $
from Products.CMFNauTools.SecureImports import parseDate

REQUEST = context.REQUEST
r = REQUEST.get

filter_id = r('filter_id')

default_filter = { 'conditions': [],
                   'query': {},
                   'columns': []
                 }

filter_map = REQUEST['SESSION'].get('%s_filter' % filter_id, default_filter)
columns = filter_map.get('columns')

if r('reset'):
    filter_map = default_filter
    filter_map['columns'] = columns

query = filter_map.get( 'query', {} )

conditions=[x.get('id') for x in columns if x.get('id') in query.keys()]

if r('add_condition'):
    c = r('condition')
    if c and c not in conditions: # 'c' is id of the column, but sometimes not. see #1278
        conditions.append(c)

elif r('remove_condition'):
    selected_conditions = r('selected_conditions', [])
    for id in selected_conditions:
        if id not in conditions: # session cleared
            continue
        conditions.remove(id)
        del query[id]
        del query['%s_usage' % id]

if query.has_key('CategoryAttributes'):
    del query['CategoryAttributes']

# Construct query
for id in conditions:
    column = [ col for col in columns if col.get('id') == id ][0]
    column_type = column.get('type')

    if column_type == 'date':
        min_date = parseDate( 'filter_min_%s' % id, REQUEST, DateTime() )
        max_date = parseDate( 'filter_max_%s' % id, REQUEST, DateTime() + 1 ) + 0.99999
        value = (min_date, max_date)
    else:
        value = r('filter_%s'%id, '')

    usage_key = '%s_usage' % id

    #XXX fix me. need to try not use mutable values in query mapping
    if column.has_key('attributes_index') and value:
        if not query.has_key('CategoryAttributes'):
            query['CategoryAttributes'] = {'query': [], 'operator': 'and'}
        query['CategoryAttributes']['query'].append( {'query': value, 'attributes': id, 'range': r(usage_key, '') } )

    query[usage_key] = r(usage_key, '')
    query[id] = value

filter_map['query'] = query
REQUEST['SESSION'].set('%s_filter' % filter_id, filter_map)

if r('save_filter'):
    query_new = context.create_query( filter_map,
                                      mode_name=mode_name
                                    )
    if filter_map.get( 'profile_id' ):
        filter = context.portal_catalog.getObjectByUid( filter_map['profile_id'], feature='containsQuery' )
        if filter:
            filter.setQuery( query_new )
            return filter.redirect( message="Filter has been saved" )

    folder = context.portal_membership.getPersonalFolder( 'searches', create=1 )
    params = { 'type_name' : 'Filter',
               'type_args' : { 'query_id' : query_new.getId(),
                               'source' : context.implements('isPortalRoot') and 'portal' or context.getUid() },
             }
    return folder.redirect( action='invoke_factory_form', params=params )


url = r('HTTP_REFERER')
REQUEST['RESPONSE'].redirect( url )
#REQUEST['RESPONSE'].redirect(context.absolute_url())
