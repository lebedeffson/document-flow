## Script (Python) "listArchive"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST,
##title=Edit a document
##

#publisher = this.getToolByName(self.content, 'portal_publisher')

import string
path = context.internal + '/' + context.heading_absolute_url()

search_args = { 'state': 'published'
        , 'meta_type': ['HTMLDocument', 'DTMLDocument']
        , 'parent_path': path
        , 'sort_on' : 'Date'
        , 'sort_order' : 'reverse'
        }
catalog = context.portal_catalog
results = apply(catalog.searchResults, (), search_args )

archiveProperty = context.archiveProperty()

if archiveProperty=='None':
    res = []
    for r in results:
        if REQUEST.has_key('actionIds') and (r.id in REQUEST['actionIds']):
            continue
        res.append({'title':r.Title, 'id':r.id, 'date':r.Date})
    return res
elif archiveProperty=='byYear':
    res = []
    nums = {}
    ind = 0
    last_year = None
    for r in results:
        if REQUEST.has_key('actionIds') and (r.id in REQUEST['actionIds']):
            continue
        year = r.Date[0:4]
        if not nums.has_key(year):
            nums[year] = {'sum':0, 'ind':None}
        nums[year]['sum'] = nums[year]['sum'] + 1
        if REQUEST.has_key('year') and REQUEST['year']==year:
            if last_year!=year:
                if nums[year]['ind'] == None:
                    nums[year]['ind'] = ind
                res.append({'year':year, 'opened':1})
                ind += 1
            res.append({'year':year, 'title':r.Title, 'id':r.id, 'date':r.Date})
            ind += 1
        else:
            if last_year!=year:
                if nums[year]['ind'] == None:
                    nums[year]['ind'] = ind
                res.append({'year':year})
                ind += 1
        last_year = year


    #return nums
    for y in nums.keys():
        res[ nums[y]['ind'] ]['number_of_document'] = nums[y]['sum']
    return res

elif archiveProperty=='byMonth':
    res = []
    nums = {}
    ind = 0
    last_year = None
    last_month =  None
    for r in results:
        if REQUEST.has_key('actionIds') and (r.id in REQUEST['actionIds']):
            continue
        year = r.Date[0:4]
        month = r.Date[5:7]
        if not nums.has_key(year):
            nums[year] = {'sum':0, 'ind':None, 'months':{}}
        nums[year]['sum'] = nums[year]['sum'] + 1
        if REQUEST.has_key('year') and REQUEST['year']==year:
            if not nums[year]['months'].has_key(month):
                nums[year]['months'][month] = {'sum':0, 'ind':None}
            nums[year]['months'][month]['sum'] = nums[year]['months'][month]['sum'] + 1
            if last_year!=year:
                if nums[year]['ind'] == None:
                    nums[year]['ind'] = ind
                res.append({'year':year, 'opened':1})
                ind += 1
            if REQUEST.has_key('month') and REQUEST['month']==month:
                if last_year!=year or last_month!=month:
                    if nums[year]['months'][month]['ind'] == None:
                        nums[year]['months'][month]['ind'] = ind
                    res.append({'year':year, 'month':month, 'opened':1})
                    ind += 1
                res.append({'year':year, 'month':month, 'title':r.Title, 'id':r.id, 'date':r.Date})
                ind += 1
            else:
                if  last_year!=year or last_month!=month:
                    if nums[year]['months'][month]['ind'] == None:
                        nums[year]['months'][month]['ind'] = ind
                    res.append({'year':year, 'month':month})
                    ind += 1
            last_month = month
        else:
            if last_year!=year:
                if nums[year]['ind'] == None:
                    nums[year]['ind'] = ind
                res.append({'year':year})
                ind += 1
        last_year = year
    for y in nums.keys():
        res[ nums[y]['ind'] ]['number_of_document'] = nums[y]['sum']
        for m in nums[y]['months'].keys():
#                       print 'mo: ' + str(m) + ' ind: ' + str(nums[y]['months'][m]['ind']) + ' sum: ' + str(nums[y]['months'][m]['sum']) + '<br>\n'
            res[ nums[y]['months'][m]['ind'] ]['number_of_document'] = nums[y]['months'][m]['sum']

    #return printed
    return res

elif archiveProperty=='byDay':
    if REQUEST.has_key('year') and REQUEST.has_key('month') and REQUEST.has_key('day'):
        required_date = string.zfill(REQUEST['year'], 4) + '-' + string.zfill(REQUEST['month'], 2) + '-' + string.zfill(REQUEST['day'], 2)
        res = []
        for r in results:
            if REQUEST.has_key('actionIds') and (r.id in REQUEST['actionIds']):
                continue
            if r.Date[0:10] == required_date:
                res.append({'year':REQUEST['year'], 'month':REQUEST['month'], 'day':REQUEST['day'], 'title':r.Title, 'id':r.id, 'date':r.Date})
    elif REQUEST.has_key('year') and REQUEST.has_key('month') and not REQUEST.has_key('day'):
        res = {'days':{}, 'months':{}, 'years':{}, 'number_of_documents_by_month':0}
        required_date = string.zfill(REQUEST['year'], 4) + '-' + string.zfill(REQUEST['month'], 2)
        for r in results:
            if REQUEST.has_key('actionIds') and (r.id in REQUEST['actionIds']):
                continue
            if r.Date[0:7] == required_date:
                res['days'][str(int(r.Date[8:10]))] = 1
                res['number_of_documents_by_month'] = res['number_of_documents_by_month'] + 1
            if r.Date[0:4] == REQUEST['year']:
                res['months'][ str(int(r.Date[5:7])) ] = 1
            res['years'][ str(int(r.Date[0:4])) ] = 1
    return res
