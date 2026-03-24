"""
ReferenceTable class.
$Id: ReferenceTable.py,v 1.23 2008/03/27 13:07:55 oevsegneev Exp $
$Editor: ishabalin $
"""

__version__ = '$Revision: 1.23 $'[11:-2]

from DocumentTemplate.DT_Util import html_quote
from AccessControl import ClassSecurityInfo, Permissions as ZopePermissions
from Products.CMFCore import CMFCorePermissions

import Features
from Utils import InitializeClass, getToolByName, cookId, ClassTypes
from Config import Roles, Permissions
from SimpleObjects import ContentBase, InstanceBase
from Monikers import UserMoniker

class ReferenceColumn( InstanceBase ):
    """
        TODO: Add comments.
    """

    security = ClassSecurityInfo()
    security.setDefaultAccess(1)

    column_type = 'expression'

    def __init__( self, id, title='', argument=None, sort_query={} ):
        InstanceBase.__init__( self, id, title )
        self.expression = argument
        self.sort_index = 0
        self.sort_query = sort_query

    def __cmp__( self, other ):
        assert isinstance( other, ReferenceColumn )
        return cmp( self.sort_index, other.sort_index )

    def render( self, context, object, default=Missing ):
        """
            TODO: Add comments.
        """
        try:
            return html_quote( eval( self.expression, {'context':context,'object':object} ) )
        except:
            if default is not Missing:
                return html_quote( default )
            raise

    def getSortQuery( self ):
        """
            TODO: Add comments.
        """
        return self.sort_query

InitializeClass( ReferenceColumn )

class AttributeReferenceColumn( ReferenceColumn ):
    """
        TODO: Add comments.
    """
    column_type = 'attribute'

    def __init__( self, id, title='', argument=None, sort_query={} ):
        expression = 'object.getCategoryAttribute(%s)' % ( argument )
        ReferenceColumn.__init__( self, id, title, expression, sort_query=sort_query )

        # XXX attribute must be a link to attribute
        self.attribute = argument

    def render( self, context, object, default=Missing ):
        """
            TODO: Add comments.
        """
        try:
            attr = object.getCategory().getAttributeDefinition( self.attribute )
            return self.entry_field_view(   None, context,
                                            name=self.Title(),
                                            type=attr.Type(),
                                            multiple=attr.isMultiple(),
                                            value=object.getCategoryAttribute(attr, moniker=1),
                                            properties=attr.getProperties(),
                                            descriptor={'view':True, 'external':True},
                                            )
        except:
            return ReferenceColumn.render( self, context, object, default )

InitializeClass( AttributeReferenceColumn )

class StateReferenceColumn( ReferenceColumn ):
    """
        TODO: Add comments.
    """
    column_type = 'state'

    def __init__( self, id, title='', argument=None, sort_query={} ):
        ReferenceColumn.__init__( self, id, title, sort_query={'sort_on': 'state'} )

    def render( self, context, object, default=Missing ):
        """
            TODO: Add comments.
        """
        try:
            workflow = getToolByName( self, 'portal_workflow' )
            msg = getToolByName( self, 'msg' )
            workflow_id = object.getCategory().getWorkflow().getId()
            status = workflow.getStatusOf( workflow_id, object )
            return html_quote( msg( workflow.getStateTitle( workflow_id, status.get('state', default) ) ) )
        except:
            if default is not Missing:
                return html_quote( default )
            raise

InitializeClass( StateReferenceColumn )

class StateFlagReferenceColumn( ReferenceColumn ):
    """
        TODO: Add comments.
    """
    column_type = 'stateflag'

    def __init__( self, id, title='', argument=None, sort_query={} ):
        ReferenceColumn.__init__( self, id, title, sort_query={'sort_on': 'state'} )
        self.state = argument

    def render( self, context, object, default=Missing ):
        """
            TODO: Add comments.
        """
        try:
            workflow = getToolByName( self, 'portal_workflow' )
            msg = getToolByName( self, 'msg' )
            workflow_id = object.getCategory().getWorkflow().getId()
            status = workflow.getStatusOf( workflow_id, object )
            if status.get('state', default) == self.state:
                return '<img src="vdocument_step_passed_enabled.gif">'
            else:
                return ''
        except:
            if default is not Missing:
                return html_quote( default )
            raise

InitializeClass( StateFlagReferenceColumn )

class HyperlinkReferenceColumn( ReferenceColumn ):
    """
        TODO: Add comments.
    """
    column_type = 'hyperlink'

    def __init__( self, id, title='', argument=None, sort_query={} ):
        ReferenceColumn.__init__( self, id, title, argument, sort_query=sort_query )

    def render( self, context, object, default=Missing ):
        """
            TODO: Add comments.
        """
        try:
            value = ReferenceColumn.render( self, context, object, default )
            return '<a href="%s" class="navigate" target="_blank">%s</a>' % \
                                ( object.absolute_url(), value )
        except:
            if default is not Missing:
                return html_quote( default )
            raise

InitializeClass( HyperlinkReferenceColumn )

class MemberReferenceColumn( ReferenceColumn ):
    """
        TODO: Add comments.
    """
    column_type = 'user'

    def render( self, context, object, default=Missing, plain=False ):
        """
            TODO: Add comments.
        """
        try:
            membership = getToolByName( self, 'portal_membership' )
            value = ReferenceColumn.render( self, context, object, default )
            member = membership.getMemberById( value )
            if not member:
                return value
            elif plain:
                return member.getMemberBriefName()
            else:
                return UserMoniker( member, brief=1 ).render( context )
        except:
            if default is not Missing:
                return html_quote( default )
            raise

InitializeClass( MemberReferenceColumn )

class DtmlReferenceColumn( ReferenceColumn ):
    """
        TODO: Add comments.
    """
    column_type = 'dtml'

    def render( self, context, object, default=Missing ):
        """
            TODO: Add comments.
        """
        try:
            template = context.get( self.expression, None, False )
            return template( object )

        except:
            if default is not Missing:
                return html_quote( default )
            raise

InitializeClass( DtmlReferenceColumn )


class ReferenceTable( ContentBase ):
    """
        TODO: Add comments.
    """
    _class_version = 1.0
    security = ClassSecurityInfo()

    __implements__ = (  ContentBase.__implements__,
                        Features.isPortalContent,
                        )

    _meta_columns = ()

    def __init__( self, id, **kwargs ):
        ContentBase.__init__( self, id, **kwargs )
        self.columns = ()

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'addColumn' )
    def addColumn( self, id, title, type, argument, sort_query={} ):
        """
            TODO: Add comments.
        """
        counter = 0
        new_id = cookId( self.columns, id)
        klass = _reference_columns.get(type)
        if klass:
            column = klass( new_id, title, argument, sort_query )
            column.sort_index = len( self.columns )
            self.columns = self.columns + (column,)

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'delColumn' )
    def delColumn(self, id):
        """
            TODO: Add comments.
        """
        self.columns = tuple( filter( lambda x, id=id: x.getId() != id, self.columns ) )

    security.declareProtected( CMFCorePermissions.View, 'getColumnById' )
    def getColumnById(self, id, wrapped=True):
        """
            TODO: Add comments.
        """
        for column in self.columns:
            if column.getId() == id:
                return wrapped and column.__of__(self) or column

    security.declareProtected( CMFCorePermissions.View, 'listColumns' )
    def listColumns(self, wrapped=True):
        """
            TODO: Add comments.
        """
        columns = list(self.columns)
        columns.sort()
        return wrapped and [column.__of__(self) for column in columns] or columns

    security.declarePublic('moveColumn')
    def moveColumn(self, id=None, direction=1, REQUEST=None):
        """
            TODO: Add comments.
        """
        direction = int( direction )
        columns = self.listColumns()
        for ckey in range(0, len(columns)):
            if columns[ckey].getId() == id:
                if direction < 0 and ckey < len(columns) - 1:
                    columns[ckey].sort_index = ckey + 1
                    columns[ckey + 1].sort_index = ckey
                    break
                elif direction > 0 and ckey > 0:
                    columns[ckey].sort_index = ckey - 1
                    columns[ckey - 1].sort_index = ckey
                    break
            else:
                columns[ckey].sort_index = ckey

        if REQUEST is not None:
            type_info = self.getTypeInfo()
            action_path = type_info.getActionById( 'edit' )
            self.redirect( action=action_path )

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'listMetaColumns' )
    def listMetaColumns(self):
        """
            TODO
        """
        return self._meta_columns

    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'getMetaColumnParams' )
    def getMetaColumnParams(self, meta_id):
        """
            TODO: static method
        """
        return _meta_columns_params.get(meta_id, {})

    security.declareProtected( CMFCorePermissions.View, 'getAggregates')
    def getAggregates(self, results):
        """
            For each category attribute with numeric type counts min, avg and max values across all results.

            Arguments:
                'results' -- list of results found by searchEntries or its subset

            Result:
                Dictionary of 3-element tuples: {category_attribute_id:(min, avg, max), ...}

        """
        metadata = getToolByName( self, 'portal_metadata' )
        category = metadata.getCategoryById( self.getSearchableCategory() )
        if not category:
            return {}

        numeric_attributes = filter(lambda a: a.Type() in ('currency', 'float', 'int')
                                   , category.listAttributeDefinitions())
        if not numeric_attributes:
            return {}
        attributes_ids = [a.getId() for a in numeric_attributes]

        data = {}
        for r in results:
            r_values = r.CategoryAttributes
            for attr_id in attributes_ids:
                if r_values.has_key( attr_id ):
                    # attribute is indexed
                    v = r_values[attr_id]
                else:
                    # attribute is not indexed yet, try to obtain default value
                    v = category.getAttributeDefinition( attr_id ).getDefaultValue()

                # ignore unset attributes with no default values
                if v is not None:
                    data.setdefault( attr_id, [] ).append( v )

        for attr, set in data.items():
            data[attr] = ( min(set)
                         , float(sum(set))/len(set)
                         , max(set)
                         )

        return data

InitializeClass( ReferenceTable )

_reference_columns = {}
_meta_columns_params = {}

def registerReferenceColumn( columnklass ):
    assert isinstance(columnklass, ClassTypes)

    global _reference_columns
    id = columnklass.column_type

    if _reference_columns.has_key(id):
        raise ValueError, 'Column(%s) already registered' % id

    _reference_columns[id] = columnklass

def registerMetaColumnParams( id, params ):
    assert isinstance( id, str ), repr(id)
    assert isinstance( params, dict ), repr( params )
    _meta_columns_params[ id ] = params

def initialize( context ):
    # module initialization callback

    context.register( registerReferenceColumn )
    context.register( registerMetaColumnParams )

    for item in globals().values():
        if isinstance( item, ClassTypes ) and issubclass( item, ReferenceColumn ):
            context.registerReferenceColumn( item )

    context.registerMetaColumnParams( 'Id', { 'type': 'hyperlink'
                                            , 'argument': 'object.getId()'
                                            , 'sort_query': { 'sort_on': 'id' }
                                            } )

    context.registerMetaColumnParams( 'Title', { 'type': 'hyperlink'
                                               , 'argument': 'object.Title()'
                                               , 'sort_query': { 'sort_on': 'Title' }
                                               } )

    context.registerMetaColumnParams( 'Description', { 'type': 'hyperlink'
                                                     , 'argument': 'object.Description()'
                                                     , 'sort_query': { 'sort_on': 'Description' }
                                                     } )


    context.registerMetaColumnParams( 'State', { 'type': 'state'
                                               , 'argument': 'object.State()'
                                               , 'sort_query': { 'sort_on': 'state' }
                                               } )

    # XXX in docflow_logic sort_on Creator, but in registration book no sort_on
    context.registerMetaColumnParams( 'Owner', { 'type': 'user'
                                               , 'argument': 'object.Creator()'
                                               } )

    context.registerMetaColumnParams( 'Followup', { 'type': 'dtml'
                                                  , 'argument': 'reference_column_dtml_followup'
                                                  } )

    context.registerMetaColumnParams( 'Attachments', { 'type': 'dtml'
                                                     , 'argument': 'reference_column_dtml_attachments'
                                                     } )
