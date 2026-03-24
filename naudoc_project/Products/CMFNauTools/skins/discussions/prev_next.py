## Script (Python) "prev_next"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=comm, id
##
# $Editor: oevsegneev $
# $Id: prev_next.py,v 1.3 2005/05/14 05:43:49 vsafronovich Exp $
# $Revision: 1.3 $

c = 0
for i in comm:
    if id == i.id:
        break
    c += 1

ret = c and '<a href="'+comm[c-1].absolute_url()+'">Предыдущий комментарий</a>' or ''

if c == len(comm) - 1:
    ret += ''
else:
    ret += ' <a href="'+comm[c+1].absolute_url()+'">Следующий комментарий</a>'

return ret
