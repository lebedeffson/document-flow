## Script (Python) "process_attributes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, object=None, category=None, pattern='%s'
##title=
##
# $Editor: ikuleshov $
# $Id: process_attributes.py,v 1.4 2005/09/29 09:39:21 oevsegneev Exp $
# $Revision: 1.4 $

from Products.CMFNauTools.SecureImports import SimpleError, Unauthorized

assert not ( object is category is None ), "neither object nor category is given"
assert pattern.count('%s') == 1, "pattern must contain exactly one string substitution"

attrs = {}
construction = object is None
pattern = construction and category.isTempletCreation() and '%s' or pattern

if category is None:
    category = object.getCategory()
    if category is None:
        return attrs

for attribute in category.listAttributeDefinitions():
    id   = attribute.getId()
    name = pattern % id

    # skip read-only attributes
    if attribute.isReadOnly():
        continue

    # if the field is not in the form, skip attribute
    if not REQUEST.has_key( name ):
        if construction and attribute.isMandatory():
            raise SimpleError( "Please fill in the mandatory attribute \"%(name)s\".", name=attribute.Title() )
        continue

    # check permission to modify the attribute
    if not ( construction or context.checkAttributePermissionModify( id ) ):
        raise Unauthorized( "You have no permission to modify this attribute." )
        #raise Unauthorized( "You have no permission to modify the attribute \"%(name)s\".", name=attribute.Title() )

    # get value from the form
    value = REQUEST[ name ]
    if attribute.isMandatory() and attribute.isEmpty( value ):
        raise SimpleError( "Please fill in the mandatory attribute \"%(name)s\".", name=attribute.Title() )

    attrs[ id ] = value

return attrs
