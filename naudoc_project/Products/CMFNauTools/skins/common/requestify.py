## Script (Python) "requestify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=pairs, ignore=()
##title=Wrapper for formatForRequest function
##
#$Editor: ypetrov $
#$Id $
#$Revision $

from Products.CMFNauTools.SecureImports import formatForRequest

return formatForRequest(pairs, ignore)
