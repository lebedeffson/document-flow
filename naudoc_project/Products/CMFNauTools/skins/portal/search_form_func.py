## Script (Python) "search_form_func"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, query = None, cat_id = None, attr_id = None, attr_type = None, mode = None
##title=
##
# $Editor: oevsegneev $
# $Id: search_form_func.py,v 1.3 2005/05/14 05:43:53 vsafronovich Exp $
# $Revision: 1.3 $

if hasattr( query, 'attributes' ) and None not in (query, cat_id, attr_id, attr_type, mode):
    for qattr in query.attributes['query']:
        if qattr['attributes'][0] == cat_id+'/'+attr_id:
            if mode == 1:
                if attr_type in ('string', 'text'):
                    return '%s\n' % qattr['query']
                elif attr_type in ('date', 'int', 'float', 'currency'):
                    if qattr['range'] == 'min:max':
                        return '%s\n%s' % ( qattr['query'][0], qattr['query'][1] )
                    elif qattr['range'] == 'min':
                        return '%s\n\n' % qattr['query'][0]
                    elif qattr['range'] == 'max':
                        return '\n%s' % qattr['query'][0]
                elif attr_type in ('lines', 'userlist'):
                    return '%s' % ('\n'.join(qattr['query']))
            elif mode == 2:
                return len(qattr['attributes']) > 1

return ''
