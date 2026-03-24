## Script (Python) "create_query"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=filter_map=None, mode_name=None
##title=return SearchQuery instance
# $Editor: vsafronovich$
# $Id: create_query.py,v 1.8 2005/12/10 15:57:16 vsafronovich Exp $
# $Revision: 1.8 $
REQUEST = context.REQUEST

query_id = filter_map.get('query_id')
profile_id = REQUEST.get('profile_id') or filter_map.get('profile_id')

if REQUEST['SESSION'].has_key('load_filter') and profile_id:
    # remove flag
    del REQUEST['SESSION']['load_filter']
    # get profile query
    query = context.portal_catalog.getQuery( profile=profile_id)

    filter_map['query'] = query.filter_query.copy()
    filter_map['conditions'] = query.filter_conditions[:]
    #filter_map['profile_id'] = profile_id
    query_new = query
else:
    # try get query from session
    query_new = context.portal_catalog.getQuery( id=query_id )
    if query_new.getId() != query_id:
        # really new query, so fill attributes
        query_new.viewer_mode = mode_name

    # update query from filter_map
    query_new.filter_query = filter_map.get( 'query', {}).copy()
    query_new.filter_conditions = filter_map.get( 'conditions', [])[:]

# save query_id
query_id = filter_map['query_id'] = query_new.getId()
# save query in session
session = REQUEST['SESSION']
key = ( 'search', query_id)
if session.get(key) != query_new:
    session.set(key, query_new)
return query_new
