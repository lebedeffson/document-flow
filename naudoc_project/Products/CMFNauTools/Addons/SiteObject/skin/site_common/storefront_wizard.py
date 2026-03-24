## Script (Python) "storefront_wizard"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=step, products=None,
##title=Storefront steps
##
# Proccess storefront steps
# $Editor: vsafronovich $
# $Id: storefront_wizard.py,v 1.1 2008/10/15 12:48:08 oevsegneev Exp $
# $Revision: 1.1 $

REQUEST=context.REQUEST

REQUEST['SESSION'].set('items_url',context.absolute_url())
url = REQUEST['SESSION']['items_url']
if not REQUEST['SESSION'].has_key('%s_items'%url):
    REQUEST['SESSION'].set('%s_items'%url,[])
items = REQUEST['SESSION']['%s_items'%url]

if step=='1':
    items_ids = [x.get('id') for x in items]
    for product in products:
        if product['id'] in items_ids:
            product['count'] = items[items_ids.index(product['id'])]['count']
        else:
            product['count'] = '0'

elif step=='2':
    if REQUEST.has_key('del_items'):
        selected_items = REQUEST.get('selected_items',[])
        REQUEST['SESSION']['%s_items'%url] = filter(lambda x: x['id'] not in selected_items, items)

    if REQUEST.has_key('go_to_cart'):
        item_counts = REQUEST.get('item_counts',[])
        items_ids = [x.get('id') for x in items]

        def check(item_count,product):
            if item_count=='0':
                if product['id'] in items_ids:
                    return items[items_ids.index(product['id'])]
                return None
            product['count']=item_count
            return product

        cart = map(check, item_counts, context.publishedItems())
        REQUEST['SESSION']['%s_items'%url] = filter(None, cart)

elif step=='3':
    if REQUEST.has_key('send_order'):
        new_counts=REQUEST.get('counts')
        for idx in range(len(items)):
            items[idx]['count'] = new_counts[idx]

elif step=='4':
    context.SendOrder(REQUEST)
    REQUEST['SESSION'].set('%s_items'%url,[])
