## Script (Python) "dateperiod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=period, short=0
##title=
##
#$Editor: ikuleshov $
#$Id: dateperiod.py,v 1.6 2004/11/03 10:07:52 vsafronovich Exp $
#$Revision: 1.6 $
period = long(period)
dhm = period / 86400, period % 86400 / 3600, period % 3600 / 60
translate = context.msg

def get_translation(num , word):
    if not num:
        return ''
    if num / 10 % 10 != 1 and num % 10 == 1:
        out = translate( word )
    elif num / 10 % 10 != 1 and num % 10 in [2,3,4]:
        out = translate( word + '.plural' )
    else:
        out = translate( word + 's' )
    return '%d %s' % ( num, out )

out = map(get_translation, dhm, ( 'day', 'hour', 'minute' ) )
del get_translation

return ' '.join( not short and out or filter( None, out )[:1] )
