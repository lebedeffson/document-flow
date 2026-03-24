## Script (Python) "tabs_head"
##parameters=tabs, auto_select=False
##title=Renders tabs head widget
##
# $Id: tabs_head.py,v 1.21 2005/07/12 09:09:33 vsafronovich Exp $
URL = context.REQUEST.get('URL')

ret = '<table class="TabsContainer" cellspacing="0" cellpadding="1">\n'\
      '  <tr valign="middle">\n'

for tab in tabs:
    tab_get = tab.get

    # get tab information
    tab_url = tab_get('url')

    tab_icon = tab_get('icon')    
    tab_icon_text = tab_get('icon_text')
    if tab_icon:
        tab_title = tab_get('title','')
    else:
        tab_title = tab_get('title','no title')
    
    sel_tab = tab_get('selected', False) or \
              auto_select and URL.endswith( tab_url.split('/')[-1] )

    # get colors. TODO : colors not implemented yet
    sel_tab_color = tab_get('selected_color', '#f2f2f2' )
    tab_color = tab_get('color', '#dddeee' )
    highlight_color = tab_get('highlight_color', '#E7E8F8')
    
    # construct tab text
    tab_text = ''
    if tab_icon:
         if tab_icon_text:
             tab_text += tab_icon.tag(align='absmiddle', alt=tab_icon_text)
         else:
             tab_text += tab_icon.tag(align='absmiddle')

    if tab_title:
         tab_text += tab_title

    ret += '<td class="%(container_class)s">\n'\
           '  <table class="Tab" cellspacing="0" cellpadding="1">\n'\
           '    <tr>\n'\
           '      <td class="Tab" nowrap>\n'\
           '        <a class="tabs" href="%(tab_url)s">%(tab_text)s</a>\n'\
           '      </td>\n'\
           '    </tr>\n'\
           '  </table>\n'\
           '</td>\n' % { 'container_class': sel_tab and 'SelectedTabContainer' or 'TabContainer'
                       , 'tab_url': tab_url
                       , 'tab_text': tab_text
                       }

# added empty td for bottom line and close table
ret += '    <td width="100%" class="TabContainer">&nbsp;</td>\n'\
       '  </tr>\n'\
       '</table>\n'

return ret
