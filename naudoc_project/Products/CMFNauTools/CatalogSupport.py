"""
Object cataloguing helpers.

$Editor: vpastukhov $
$Id: CatalogSupport.py,v 1.13 2005/12/19 11:11:03 vsafronovich Exp $
"""
__version__ = '$Revision: 1.13 $'[11:-2]

from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import Explicit, aq_base, aq_parent

from DocumentTemplate.DT_Util import safe_callable

from Products.CMFCore.CatalogTool import IndexableObjectWrapper as _IndexableObjectWrapper

def absattr( attr ):
    if safe_callable( attr ):
        return attr()
    return attr

def mergedLocalRoles(object, withgroups=0):
    """
        Returns a merging of object and its ancestors'
        __ac_local_roles__.
        When called with withgroups=1, the keys are
        of the form user:foo and group:bar.
    """
    # Modified from AccessControl.User.getRolesInContext().
    merged = {}
    object = getattr(object, 'aq_inner', object)
    while 1:
        if hasattr(object, '__ac_local_roles__'):
            dict = object.__ac_local_roles__ or {}
            if callable(dict): dict = dict()
            for k, v in dict.items():
                if withgroups and k[:4] not in [ 'pos:', 'div:' ]: 
                    k = 'user:'+k
                if merged.has_key(k):
                    merged[k] = merged[k] + v
                else:
                    merged[k] = v
        # deal with groups
        if withgroups:
            if hasattr(object, '__ac_local_group_roles__'):
                dict = object.__ac_local_group_roles__ or {}
                if callable(dict): dict = dict()
                for k, v in dict.items():
                    k = 'group:'+k
                    if merged.has_key(k):
                        merged[k] = merged[k] + v
                    else:
                        merged[k] = v
        # end groups
        if hasattr(object, 'aq_parent'):
            object=object.aq_parent
            object=getattr(object, 'aq_inner', object)
            continue
        if hasattr(object, 'im_self'):
            object=object.im_self
            object=getattr(object, 'aq_inner', object)
            continue
        break
    return merged

class IndexableObjectWrapper( _IndexableObjectWrapper ):

    # mapping index_name => (features_list, default_value)
    __ignored_indexes = {
            'nd_uid' : (['isVersion'], lambda ob: str(ob.getResourceUid()) ),
        }

    # mapping index_name => (features_list, default_value)
    __allowed_indexes = {
            'category' : (['isCategorial'], None),
            'hasBase' : (['isCategorial'], ()),
            'CategoryAttributes' : (['isCategorial'], None),
            'state' : (['isCategorial', 'isSearchProfile'], None),
            'in_reply_to' : (['isHTMLDocument'], None),
            'registry_ids' : (['isHTMLDocument'], () ),
            'getPrincipalVersionId' : (['isHTMLDocument'], None),
        }

    def __init__( self, vars, ob ):
        names = {}
        if hasattr( aq_base(ob), 'implements' ):

            for attr, (impls, default) in self.__ignored_indexes.items():
                for impl in impls:
                    if ob.implements( impl ):
                        if callable(default):
                             default = default( ob ) 
                        names[ attr ] = default
                        break

            for attr, (impls, default) in self.__allowed_indexes.items():
                for impl in impls:
                    if ob.implements( impl ):
                        break
                else:
                    if callable(default):
                        default = default( ob ) 

                    names[ attr ] = default
        else:
            for attr, (impls, default) in self.__allowed_indexes.items():
                names[ attr ] = default

        self.__ignored_names = names
        _IndexableObjectWrapper.__init__( self, vars, ob )

    def __getattr__( self, name ):
        try:
            return self.__ignored_names[ name ]
        except KeyError:
            pass
        return _IndexableObjectWrapper.__getattr__( self, name )

    def allowedRolesAndUsers(self):
        """
        Return a list of roles, users and groups with View permission.
        Used by PortalCatalog to filter out items you're not allowed to see.
        """
        ob = self._IndexableObjectWrapper__ob # Eeek, manual name mangling
        allowed = {}
        for r in rolesForPermissionOn('View', ob):
            allowed[r] = 1

        localroles = mergedLocalRoles(ob, withgroups=1) # groups

        for user_or_group, roles in localroles.items():
            for role in roles:
                if allowed.has_key(role):
                    allowed[user_or_group] = 1
        if allowed.has_key('Owner'):
            del allowed['Owner']


        return list(allowed.keys())

class IndexableMethod( Explicit ):
    """
        Method wrapper class -- watches for instance attributes
        modified by the wrapped method and performs catalog reindex
        accordingly.
    """

    isIndexableMethod = 1 # need __implements__ here. TODO

    def __init__( self, func, **idxs ):
        """
            Creates an indexable method.

            Positional arguments:

                'func' -- real method to wrap around

            Keyword arguments:

                Use attribute names as argument names and lists
                of corresponding index identifiers as values.
        """
        if getattr(func, 'isIndexableMethod', 0):
            func = func._func
            # TODO rebuild indexes too
        self._func = func
        self._idxs = []
        append = self._idxs.append

        # mapping attribute => indexes
        for n,ii in idxs.items():
            for i in ii:
                append( (n, i) )

    def __call__( self, *args, **kwargs ):
        # obtain the method target
        context = aq_parent( self )
        if context is None:
            # 2 ways 
            # the first this method called by unwrapper object, should be an error
            # the second this method called by unbound method
            if len(args) >= 1:
                context, args = args[0], args[1:]
            else:
                raise RuntimeError( "couldn't get `context`")

        base = aq_base( context )

        # collect old attribute values
        saved = [ (n, i, absattr( getattr(base, n, None) )) for n,i in self._idxs ]

        # call the original method
        result = self._func( context, *args, **kwargs )

        # filter out unchanged attributes
        idxs = [ i for n,i,v in saved if absattr( getattr(base, n, None) ) != v ]

        # update indexes if necessary
        if idxs:
            self.getReindexMethod(context)(idxs)

        return result

    def getReindexMethod(self, context):
        return context.reindexObject

class DerefferedIndexableMethod( IndexableMethod ):
    def doReindex( self, idxs ):
        im = getIndexationManager()
        im.push( aq_parent( self ), idxs )

class ZCatalogIter:
    def __init__(self, iter, hook=None):
        self.iter = iter
        if hook is not None:
            assert callable(hook)
            self.hook = hook
 
    def hook(self, item):
        pass

    def __getitem__(self, i):
        item = self.iter[i]
        return self.hook(item)

    def __iter__(self):
        for i in iter(self.iter):
            yield self.hook(i)

class SimpleQuery:
    def __init__(self, query):
        #assert isinstance( query, Query )
        self.query = query
                  
    def getQuery(self):
        return self.query
   
    def setQuery(self, query):
        self.query = query

    def setOption(self, option, value ):
        setattr(self, option, value)

#TODO deprecate this
QueryContext = SimpleQuery

class ComplexQuery:
    """
        many SimpleQueries into one
        TODO write this class
    """
    pass
