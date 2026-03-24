## Script (Python) "doFormSearch"
##parameters=REQUEST
##title=Pre-process form variables, then return catalog query results.
##
form_vars = {}
select_vars = ( 'state'
              , 'Subject'
              , 'created'
              , 'Type'
              )


for k, v in REQUEST.form.items():

    if k in select_vars:

        if same_type( v, [] ):
            v = filter( None, v )
        if not v:
            continue

    form_vars[ k ] = v

if not form_vars.get('SearchableText'):
    return []

form_vars['path'] = context.getSiteUrl()
form_vars['implements'] = 'isPortalContent'

return context.portal_catalog( form_vars )
