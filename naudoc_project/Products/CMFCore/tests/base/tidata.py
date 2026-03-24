ManageProperties = 'Manage properties'
ModifyPortalContent = 'Modify portal content'
View = 'View'

FTIDATA_ACTIONS = (
      { 'id' : 'Action Tests'
      , 'meta_type' : 'Dummy'
      , 'actions' : (
            { 'id':'view',
              'name':'View',
              'action':'string:',
              'permissions':('View',),
              'category':'object',
              'visible':1 }
          , { 'name':'Edit',                    # Note: No ID passed
              'action':'string:${object_url}/foo_edit',
              'permissions':('Modify',),
              'category':'object',
              'visible':1 }
          , { 'name':'Object Properties',       # Note: No ID passed
              'action':'string:foo_properties',
              'permissions':('Modify',),
              'category':'object',
              'visible':1 }
          , { 'id':'slot',
              'action':'string:foo_slot',
              'category':'object',
              'visible':0 }
          )
      }
    ,
    )

FTIDATA_DUMMY = (
      { 'id' : 'Dummy Content'
      , 'title' : 'Dummy Content Title'
      , 'meta_type' : 'Dummy'
      , 'product' : 'FooProduct'
      , 'factory' : 'addFoo'
      , 'actions' : (
            { 'name':'View',
              'action':'string:view',
              'permissions':('View',) }
          , { 'name':'View2',
              'action':'string:view2',
              'permissions':('View',) }
          , { 'name':'Edit',
              'action':'string:edit',
              'permissions':('forbidden permission',) }
          )
      }
    ,
    )

FTIDATA_CMF13 = (
      { 'id' : 'Dummy Content 13'
      , 'meta_type' : 'Dummy'
      , 'description' : (
           'Dummy Content.')
      , 'icon' : 'dummy_icon.gif'
      , 'product' : 'FooProduct'
      , 'factory' : 'addFoo'
      , 'immediate_view' : 'metadata_edit_form'
      , 'actions' : (
            { 'id':'view',
              'name':'View',
              'action':'dummy_view',
              'permissions':(View,) }
          , { 'id':'edit',
              'name':'Edit',
              'action':'dummy_edit_form',
              'permissions':(ModifyPortalContent,) }
          , { 'id':'metadata',
              'name':'Metadata',
              'action':'metadata_edit_form',
              'permissions':(ModifyPortalContent,) }
          )
      }
    ,
    )

FTIDATA_CMF13_FOLDER = (
      { 'id' : 'Dummy Folder 13'
      , 'meta_type' : 'Dummy Folder'
      , 'description' : (
           'Dummy Folder.')
      , 'icon' : 'dummy_icon.gif'
      , 'product' : 'FooProduct'
      , 'factory' : 'addFoo'
      , 'filter_content_types' : 0
      , 'immediate_view' : 'dummy_edit_form'
      , 'actions' : (
            { 'id':'view',
              'name':'View',
              'action':'',
              'permissions':(View,),
              'category':'folder' }
          , { 'id':'edit',
              'name':'Edit',
              'action':'dummy_edit_form',
              'permissions':(ManageProperties,),
              'category':'folder' }
          , { 'id':'localroles',
              'name':'Local Roles',
              'action':'folder_localrole_form',
              'permissions':(ManageProperties,),
              'category':'folder' }
          )
      }
    ,
    )


STI_SCRIPT = """\
## Script (Python) "addBaz"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=folder, id
##title=
##
product = folder.manage_addProduct['FooProduct']
product.addFoo(id)
item = getattr(folder, id)
return item
"""
