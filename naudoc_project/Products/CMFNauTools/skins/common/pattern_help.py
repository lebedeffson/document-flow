## Script (Python) "pattern_help"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=fmt
##title=
##
# $Editor: oevsegneev $
# $Id: pattern_help.py,v 1.4 2005/09/16 08:47:31 vsafronovich Exp $
# $Revision: 1.4 $

from Products.CMFNauTools.SecureImports import listExplanations

return listExplanations(fmt)
