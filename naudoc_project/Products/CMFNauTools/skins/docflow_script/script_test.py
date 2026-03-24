## Script (Python) "script_test"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Executes the script for testing purposes
##
# $Id: script_test.py,v 1.8 2005/05/14 05:43:53 vsafronovich Exp $
# $Editor: mbernatski $
# $Revision: 1.8 $
from Products.CMFNauTools.SecureImports import parseDate, updateLink

REQUEST = context.REQUEST
r = REQUEST.get
parameters = {}

if REQUEST.has_key('evaluateScript'):
    #Evaluates the script
    for param in context.listParameters():
        cid = param['id']
        title = r('title_%s' % cid)
        typ = param['data_type']
        if typ == 'date':
            value = parseDate('value_%s' % cid, REQUEST, default=None )
            if value:
                value = str(value)
        elif typ == 'lines':
            value = list(r('value_%s' % cid))
            if len(value) == 1 and not len(value[0]):
                # empty textarea gets parsed by Zope into
                # a single-element list containing an empty string
                value.pop(0)
        elif typ == 'link':
            val = r('value_%s' % cid, '')
            if val['uid']:
                link_id = updateLink( context, 'attribute', 'default', value=val )
                link = context.portal_links[ link_id ]
                value = link.getTargetObject()
            else:
                value = None
        else:
            value = r('value_%s' % cid)

        parameters[cid] = value

    namespace_class = context.getNamespaceFactory()
    namespace = namespace_class(context.parent(), context.portal_membership.getAuthenticatedMember().getUserName(), context.getPortalObject())
    return context.test(namespace=namespace, parameters=parameters)
