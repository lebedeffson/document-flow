## Script (Python) "search_query"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None, implements=None, text=None, query_id=None, profile_id=None, objects=None, filters=None, transitivity=None, doc_in_plan=None, fields=None, otype=None, owners=None, scope_value=None, scope_trigger=None, location=None, action=None, special_trigger=None, normative_trigger=None, category=None, state=None, mode=None, standard_trigger, ctrl_attributes_trigger
##title=Handles search query and redirects to the results page.
##
# $Editor: vpastukhov $
# $Id: search_query.py,v 1.45 2006/07/18 11:59:27 ypetrov Exp $
# $Revision: 1.45 $

from Products.CMFNauTools.SecureImports import parseDate

if profile_id:
    query = context.portal_catalog.getQuery( profile=profile_id, copy=1, REQUEST=REQUEST )
elif mode == 'simple':
    query = context.portal_catalog.getQuery( REQUEST=REQUEST )
    query.implements = {'query':['isAttachment', 'isHTMLDocument', 'isVersion'], 'operator':'or'}
else:
    query = context.portal_catalog.getQuery( query_id, REQUEST=REQUEST )

query_id = query.getId()

if text is not None:
    query.text = text

if ctrl_attributes_trigger and standard_trigger:
    for item in 'oid', 'title', 'description':
        if REQUEST.has_key( item ):
            setattr( query, item, str( REQUEST[item] ) )

if ctrl_attributes_trigger and standard_trigger or mode == 'doc_stat':
    created_from = parseDate( 'created_from', REQUEST, None )
    created_till = parseDate( 'created_till', REQUEST, None )

    query.creation = (created_from, created_till and created_till + 0.99999)

if owners:
    query.owners = owners

if objects is not None:
    query.objects = filter( None, objects )

if implements is not None:
    query.implements = filter( None, implements )
elif mode != 'simple':
    query.implements = []

otype_cat_kw = {'Heading': 'Folder'}

if otype is not None:
    if otype == 'Attachments':
        query.implements = {'query':['isAttachment'], 'operator':'or'}
    elif otype == 'HTMLDocument':
        if REQUEST.has_key('is_versions'):
            query.implements = {'query':['isVersion', 'isHTMLDocument'], 'operator':'and'}
        else:
            query.implements = {'query':['isVersionable', 'isHTMLDocument'], 'operator':'and'}
    elif otype == 'any':
        pass
    else:
        # XXX                  
        category = otype_cat_kw.has_key(otype) and otype_cat_kw[otype]
        query.types = [otype]

if category and category != 'any':
    attributes=[]
    extract_Factory = { 'int' :int
                      , 'float' : float
                      , 'currency' : float
                      , 'date' : parseDate
                      }

    cat = context.portal_metadata.getCategoryById(category)
    for attr in cat.listAttributeDefinitions():
        attr_id = attr.getId()
        attr_value = REQUEST.get(category + '_' + attr_id)
        in_child = REQUEST.get(category + '_' + attr_id + '_inchild')
        attribute = {}

        condition_value = '%s_%s' % ( category, attr_id )
        if not REQUEST.has_key('conditions_' + category ) \
           or condition_value not in REQUEST.get( 'conditions_' + category ):
            continue
        attr_type = attr.Type()
        if attr_type == 'boolean':
            attribute['query'] = attr_value[0] != 'false' and [1] or '' # XXX

        elif attr_type in ['text', 'string']:
            attribute['query'] = attr_value[0]

        elif attr_type in ['lines', 'userlist']:
            attribute['query'] = attr_value

        elif attr_type in ['int', 'float', 'currency', 'date']:
            min_max = {}
            for idx in (0,1):
                if attr_value[idx]:
                    min_max[ ['min','max'][idx] ] = extract_Factory[attr_type]( attr_value[idx] )

            attribute['query'] = min_max.values()
            attribute['range'] = ':'.join( min_max.keys() )

        attribute['attributes'] = [ category + '/' + attr_id ]
        if in_child:
            for dep_cat in cat.listDependentCategories():
                attribute['attributes'].append( '%s/%s' % (dep_cat.getId(), attr_id) )

        attributes.append( attribute )

    if attributes:
        query.attributes = {'query': attributes, 'operator': 'and'}

    if otype in ('HTMLDocument', 'Heading'):
        query.category = category
        if state is not None and state.has_key(category) and state[category] != 'any':
            query.state = state[category]

if filters is not None:
    query.filters = filter( None, filters )
    # show another dtml for search over documents for revision
    if 'normative_filter' in query.filters:
        action = 'search_results_ndocument'

if special_trigger:
    if normative_trigger:
        if transitivity is not None:
            query.transitivity = transitivity
        if doc_in_plan is not None:
            query.doc_in_plan = doc_in_plan

if scope_trigger:
    if scope_value == 'preserved':
        pass

    elif location and scope_value != 'global':
        # find the nearest enclosing folder unless the location is folder
        object = context.restrictedTraverse( location )
        if not object.implements('isPrincipiaFolderish'):
            object = object.parent( feature='isPrincipiaFolderish' )
            location = object.physical_path()

        query.scope = scope_value or 'recursive'
        query.location = location

    elif query.location:
        query.scope = scope_value or 'global'

    else:
        query.scope = 'global'
else:
    query.scope = 'global'

params = {}
frame='inFrame'

if not REQUEST.get('save'):
    params['query_id'] = query_id
    params['batch_length'] = REQUEST.get('batch_length')
    if REQUEST.has_key('adv_search'):
        params['adv_search'] = 1
    if REQUEST.has_key('from_explorer'):
        frame = None
        params['link'] = 'search'

    query_location = context.restrictedTraverse( query.location )
    return query_location.redirect( action=(action or 'search_results'), frame=frame, params=params )

elif profile_id:
    profile = context.portal_catalog.getObjectByUid( profile_id )
    profile.setQuery( query )
    params['portal_status_message'] = "Search query has been saved."
    return profile.redirect( action='view', frame=frame, params=params )

else:
    params['type_name'] = 'Search Profile'
    params['type_args'] = { 'query_id':query_id }
    folder = context.portal_membership.getPersonalFolder( 'favorites', create=1 )
    return folder.redirect( action='invoke_factory_form', frame=frame, params=params )
