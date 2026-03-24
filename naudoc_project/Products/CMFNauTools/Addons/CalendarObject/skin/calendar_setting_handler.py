## Script (Python) "calendar_setting_handler"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,view_month_select=0,view_month_list=0,week_mode,len_of_text=60,popup_full_text=0,week_table_mode_only_title=0,show_holidays_together=0,show_tasks_month_view=0,public_default_check=0,calendar_skin_version='1.0'
##title=Create content
##

context.setSetting(view_month_select=view_month_select,
                   view_month_list=view_month_list,
                   week_mode=week_mode,
                   len_of_text=int(len_of_text),
                   popup_full_text=popup_full_text,
                   week_table_mode_only_title=week_table_mode_only_title,
                   show_holidays_together=show_holidays_together,
                   show_tasks_month_view=show_tasks_month_view,
                   public_default_check=public_default_check,
                   calendar_skin_version=calendar_skin_version
 )

context.redirect(action='calendar_setting', message='Setting save')
