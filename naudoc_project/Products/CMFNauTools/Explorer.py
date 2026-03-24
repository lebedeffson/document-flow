

from random import randrange
from types import StringTypes
#from weakref import WeakValueDictionary

from Acquisition import Implicit, aq_get, aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo
from Globals import get_request
from Interface import Interface

from Products.CMFCore.utils import getToolByName

from SimpleObjects import Persistent
from JungleTag import ContentTree
from ResourceUid import ResourceUid
from Utils import getObjectImplements, InitializeClass, ClassTypes, getObjectByUid

#_explorers = WeakValueDictionary()

class ExplorerBase( Persistent, Implicit ):

    export_names = 'callback_form', 'callback_function', 'title_field', 'uid_field'
    sections = 'contents', 'search', 'clipboard', 'favorites'
    mode = NotImplemented

    _v_object = None
  
    def __init__(self, context=None, **kw):
        self._container = {}

        id = self.id = str( randrange(1000000000) )

        for key in self.export_names:
            self[key] = kw.get(key)

        for key, item in kw.items():
            if key.startswith(self.mode): # raise TypeError when mode=NotImplemented
                 self[ key[len(self.mode)+1:] ] = item

        # context
        self.assign( context )

        # XXX do not implicitly set to REQUEST
        REQUEST = context.REQUEST
        REQUEST[ 'explorer_id' ] = id
        REQUEST[ 'explorer_root_url' ] = context.relative_url()

        if self.has_key( 'data'):
            REQUEST['data'] = self['data']

        # register explorer in explorer factory
        self.register()

    # Dictionary

    def keys(self):
        return self._container.keys()

    def values(self):
        return self._container.values()

    def items(self):
        return self._container.items()

    def get(self, k, default=None):
        return self._container.get(k, default)

    def has_key(self, k):
        return self._container.has_key(k)

    def clear(self):
        self._p_changed = 1
        self._container.clear()

    def update(self, d):
        self._p_changed = 1
        for k in d.keys():
            self[k] = d[k]

    def __setitem__(self, k, v):
        self._p_changed = 1
        self._container[k] = v

    def __getitem__(self, k):
        return self._container[k]

    def __delitem__(self, k):
        self._p_changed = 1
        del self._container[k]

    def __str__(self):
        return str(self._container)


    def register(self):
        """
        """
        getExplorerFactory()[ ('explorer', self.id) ] = self

    def open(self, context):
        """
        """
        self._v_object = getObjectByUid( context, self['root'] )
        get_request()['root'] = self['root']

    def assign(self, new_root):
        """
        """
        self['root'] = ResourceUid( new_root )
        self.open( new_root )

    def reassign(self, context):
        """
           Reassign to the root in new REQUEST
        """
        self.open( context )

    def isAssigned(self):
        return self.has_key('root')

    def free(self):
        try:
            del self['root']
        except KeyError:
            pass
        else:
            if self._v_object is not None:
                del self._v_object

    def tree_index(self, item):
        raise NotImplementedError

    def content_index(self, item):
        raise NotImplementedError

    def contents( self, item ):
        raise NotImplementedError

    def listSections( self ):
        """
        """
        available_sections = []
        context = self._v_object
        for section in self.sections:
            if getattr( context, 'explorer_%s_%s' %( self.mode, section ), Missing) is not Missing:
                available_sections.append( section )
      
        return available_sections

    def listTabs(self):
        """
        """
        sections = self.listSections()
        context = self._v_object

        msg = context.msg
        REQUEST = context.REQUEST

        link = REQUEST.get('link', '')
        
        tabs = []
        for section in sections: 
            tab_url = "explorer_%s_%s" % (self.mode, section)
            tabs.append( { 'url': tab_url
                         , 'title': msg( section.capitalize() ) } )
            if link.find(tab_url)>=0:
                tabs[-1]['selected'] = True

        return tabs

class FolderExplorer( ExplorerBase ):
    """
    """
    mode = 'folder'

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess( 1 )

    _args = {'implements':'isPrincipiaFolderish'}

    def tree_index(self, item):
        """
        """
        context = self._v_object
        REQUEST = context.REQUEST
        explorer_id = self.id

        # item is a uid of the folder
        # then item is empty --> getting uid of the context
        # XXX this is not good, item must exist
        item = item or context.getUid()
        # XXX do not implicitly set to REQUEST
        REQUEST.set('item',item)

        catalog = getToolByName(context, 'portal_catalog')

        folder = catalog.getObjectByUid( item, feature='isPrincipiaFolderish')

        return ContentTree(folder, self._args.copy() )

    def content_index(self, item):
        """
        """
        context = self._v_object
        REQUEST = context.REQUEST
        explorer_id = self.id

        # item is a uid of the folder
        # then item is empty --> getting uid of the context
        # XXX this is not good, item must exist
        item = item or self['root']

        catalog = context.portal_catalog

        folder = catalog.getObjectByUid(item, feature='isPrincipiaFolderish')

        # This only need here to calculate the sort_limit
        batch_size = int(context.portal_membership.getInterfacePreferences('viewing_document_number'))
        qs_old = self.get('qs', 1)
        qs_new = int( REQUEST.get('qs', qs_old) )
        qs = qs_new / batch_size * batch_size + 1
        if qs > 1 or (qs == 1 and qs_old > 1):
             self[ 'qs' ] = qs

        limit = qs + batch_size - 1

        path = folder.parent().implements('isPortalRoot') and 'path' or 'parent_path'

        query = { 'sort_on': 'Title'
                , 'sort_limit': limit
                , path: folder.physical_path()
                }

        if path == 'path':
            query['nd_uid'] = {'query':folder.getUid(), 'operator':'not'}
            query['parent_path'] = {'query':context.portal_properties.getProperty('templates_folder').physical_path(), 'operator':'not'}

        if self.has_key('categories'):
            query['category'] = self['categories']

        if self.has_key('search_types'):
            query['portal_type'] = self['search_types']

        implements = self.get('search_features')
        implements_operator = implements==['isHTMLDocument','isPortalContent'] and 'and' or 'or' # XXX

        query['implements'] = {'query':implements, 'operator':implements_operator}
        results = catalog.searchResults( **query )
        results_count = results and results.actual_result_count or 0

        # transform into ( (item1, callback_result1), info1) ...)
        results = [ ( ( brains['nd_uid']
                      , self.has_key('getPath') and brains.getPath() or brains['nd_uid'])
                      , brains)
                    for brains in results ]

        return { 'results': results
               , 'results_count': results_count
               , 'batch_size': batch_size
               , 'qs': qs
               , 'object': folder
               , 'item': item
               }
 
InitializeClass( FolderExplorer )

#class DirectoryExplorer( ExplorerBase ):
#    mode = 'directory'

#InitializeClass( DirectoryExplorer )

_registered_explorer_types = {}
_feature2ids = {}

def registerExplorer( feature, ExplorerType ):
    assert isinstance( feature, StringTypes ), `feature`
    assert isinstance( ExplorerType, ClassTypes ), `ExplorerType`
    assert hasattr( ExplorerType, 'mode') and isinstance( ExplorerType.mode, StringTypes ), `ExplorerType`

    global _registered_explorer_types, _feature2ids
    id = ExplorerType.mode
    _registered_explorer_types[ id ] = ExplorerType
    _feature2ids[ feature ] = id

def getExplorerTypeByMode( mode ):
    return _registered_explorer_types[ mode ]

def getExplorerType( context ):
    for feature, id in _feature2ids.items():
        if getObjectImplements( context, feature ):
            return _registered_explorer_types[id]

    raise TypeError(context)

def getExplorerById( id ):
    return getExplorerFactory()[ ('explorer', id ) ]

def getExplorerFactory():
    return get_request().SESSION

def initialize( context ):
    context.register( registerExplorer ) 
    context.registerExplorer( 'isPrincipiaFolderish', FolderExplorer )
