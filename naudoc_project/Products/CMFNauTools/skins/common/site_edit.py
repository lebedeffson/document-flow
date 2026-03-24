## Script (Python) "site_edit"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=title, sync_addr='', sync_path='', level_max_count=[], level_title=[], new_level_title='New level', new_level_max_count=0
##title=Edit site properties
##
# $Editor: vpastukhov $
# $Id: site_edit.py,v 1.6 2004/02/08 14:01:38 vpastukhov Exp $
# $Revision: 1.6 $

request = context.REQUEST
r = request.has_key

if r('del_level'):
    context.deletePresentationLevel()
    request.RESPONSE.redirect( context.absolute_url(action='site_edit_form',message='Level deleted') )
elif r('add_level'):
    context.addPresentationLevel(max_count=new_level_max_count, title=new_level_title)
    request.RESPONSE.redirect( context.absolute_url(action='site_edit_form',message='Level added') )
elif r('save_levels'):
    levels = context.listPresentationLevels()

    for i in range(len(levels)-1):
        max_count = level_max_count[i]
        title = level_title[i]
        if levels[i+1] != {'max_count':max_count, 'title':title} and title:
            context.setPresentationLevelProperties(level=i+1, max_count=max_count, title=title)

    context.updateRemoteCopy( recursive=0 )

    request.RESPONSE.redirect( context.absolute_url(action='site_edit_form',message='Properties of levels saved') )
else:
    context.edit( title=title )
    context.setSyncProperties( sync_addr, sync_path )

    request.RESPONSE.redirect(
        context.absolute_url(
            action='folder_contents',
            message="Site configuration saved.",
            params={ 'update':'yes' }
            ),
        status=303
        )
