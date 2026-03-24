## Script (Python) "parse_link"
##bind context=context
##bind namespace=
##bind script=script
##title=Parse link
##parameters=link=''
# $Editor: ishabalin $
# $Id: parse_link.py,v 1.1 2004/03/31 06:22:58 ishabalin Exp $
# $Revision: 1.1 $

try:
    params = link.split('?', 1)[1].split('&')
except:
    params = []

for item in params:
    parts = item.split('=', 1)
    if len(parts) > 1:
        context.REQUEST.set(parts[0], parts[1])
