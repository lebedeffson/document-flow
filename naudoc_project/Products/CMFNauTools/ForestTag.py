"""
Rendering object hierarchies as Trees multiple tags per page possible.
Tags on serveral pages may share status.

Adapted from the ForestTag 1.1 product by Andreas Leitner.
See http://www.zope.org/Members/anlei/dtml-forest

$Editor: ikuleshov $
$Id: ForestTag.py,v 1.13 2005/12/07 13:20:18 ikuleshov Exp $
"""
__version__ = '$Revision: 1.13 $'[11:-2]

import re
from binascii import b2a_base64
from string import translate
from zlib import compress
from cPickle import dumps

from DocumentTemplate.DT_Util import ParseError, InstanceDict, \
        Eval, add_with_prefix, name_param, parse_params, render_blocks

from TreeDisplay.TreeTag import encode_seq, decode_seq, \
        encode_str, apply_diff, oid, tplus, tpValuesIds, tpStateLevel

try:
    from TreeDisplay.TreeTag import MiniUnpickler
    del MiniUnpickler
    _use_mini_unpickler = True
except ImportError:
    _use_mini_unpickler = False

pyid = id # copy builtin


class Forest:
    name = 'forest'
    blockContinuations = ()
    expand = None

    def __init__(self, blocks):
        tname, args, section = blocks[0]
        args=parse_params(args, name=None, expr=None, nowrap=1,
                          expand=None, leaves=None, code=None,
                          header=None, footer=None,
                          branches=None, branches_expr=None,
                          sort=None, reverse=1, skip_unauthorized=1,
                          id=None, single=1, url=None,
                          secured_tree=None,
                          content_filter=None,
                          # opened_decoration=None,
                          # closed_decoration=None,
                          # childless_decoration=None,
                          assume_children=1,
                          urlparam=None, urlparam_expr=None, prefix=None,
                          state_id=None,
                          state_url=None,
                          security=None, security_expr=None,
                          pl_icon=None,
                          mi_icon=None)
        has_key=args.has_key

        if has_key('') or has_key('name') or has_key('expr'):
            name,expr=name_param(args,'tree',1)

            if expr is not None: args['expr']=expr
            elif has_key(''): args['name']=name
        else: name='a tree tag'



        if has_key('branches_expr'):
            if has_key('branches'):
                raise ParseError, _tm(
                    'branches and branches_expr given', 'tree')
            args['branches_expr']=Eval(args['branches_expr']).eval
        elif not has_key('branches'):
            args['branches']='tpValues'

        if has_key('urlparam_expr'):
            if has_key('urlparam'):
                raise ParseError, _tm(
                    'urlparam and urlparam given', 'tree')
            args['urlparam_expr']=Eval(args['urlparam_expr']).eval

        if has_key('security_expr'):
            if has_key('security'):
                raise ParseError, _tm(
                    'security and security_expr given', 'tree')
            args['security_expr']=Eval(args['security_expr']).eval

        if not has_key('id'): args['id']='tpId'
        if not has_key('url'): args['url']='tpURL'
        if not has_key('childless_decoration'):
            args['childless_decoration']=''

        prefix = args.get('prefix')
        if prefix and not simple_name(prefix):
            raise ParseError, _tm(
                'prefix is not a simple name', 'tree')

        if not has_key ('state_id'): args['state_id']='forest'
        if not has_key ('state_url'): args['state_url']='/'


        self.__name__ = name
        self.section=section.blocks
        self.args=args

    def render(self,md):
        args=self.args
        have=args.has_key

        if have('name'): v=md[args['name']]
        elif have('expr'): v=args['expr'].eval(md)
        else: v=md.this
        return tpRender(v,md,self.section, self.args)

    __call__=render

    def tpSecureValues(self):
        # Return a list of subobjects, used by tree tag.
        r=[]
        if hasattr(aq_base(self), 'tree_ids'):
            tree_ids=self.tree_ids
            try:   tree_ids=list(tree_ids)
            except TypeError:
                pass
            if hasattr(tree_ids, 'sort'):
                tree_ids.sort()
            for id in tree_ids:
                if hasattr(self, id):
                    r.append(self._getOb(id))
        else:
            obj_ids=self.objectIds()
            obj_ids.sort()
            for id in obj_ids:
                o=self._getOb(id)
                if hasattr(o, 'isPrincipiaFolderish') and \
                   o.isPrincipiaFolderish:
                    r.append(o)
        return r

def tpRender(self, md, section, args,
             simple_type={type(''):0, type(1):0, type(1.0):0}.has_key):
    """Render data organized as a tree.

    We keep track of open nodes using a cookie.  The cookie stored the
    tree state. State should be a tree represented like:

      []  # all closed
      ['eagle'], # eagle is open
      ['eagle'], ['jeep', [1983, 1985]]  # eagle, jeep, 1983 jeep and 1985 jeep

    where the items are object ids. The state will be converted to a
    compressed and base64ed string that gets unencoded, uncompressed,
    and evaluated on the other side.

    Note that ids used in state need not be connected to urls, since
    state manipulation is internal to rendering logic.

    Note that to make eval safe, we do not allow the character '*' in
    the state.

    Multiple tags per page are possible.
    Multiple tags on different pages may share same state.
    """
    data=[]
    idattr=args['id']
    if hasattr(self, idattr):
        id=getattr(self, idattr)
        if not simple_type(type(id)): id=id()
    elif hasattr(self, '_p_oid'): id=oid(self)
    else: id=pyid(self)

    try:
        # see if we are being run as a sub-document
        root=md['tree-root-url']
        url=md['tree-item-url']
        state=md['tree-state']
        diff=md['tree-diff']
        substate=md['-tree-substate-']
        colspan=md['tree-colspan']
        level=md['tree-level']

    except KeyError:
        # OK, we are a top-level invocation
        level=-1

        if md.has_key('collapse_all'):
            state=[id,[]],
        elif md.has_key('expand_all'):
            have_arg=args.has_key
            if have_arg('branches'):
                def get_items(node, branches=args['branches'], md=md):
                    get = md.guarded_getattr
                    if get is None:
                        get = getattr
                    items = get(node, branches)
                    return items()
            elif have_arg('branches_expr'):
                def get_items(node, branches_expr=args['branches_expr'], md=md):
                    md._push(InstanceDict(node, md))
                    items=branches_expr(md)
                    md._pop()
                    return items
            state=[id, tpValuesIds(self, get_items, args)],
        else:
            if md.has_key('tree-s' + args['state_id']):
                state=md['tree-s' + args['state_id']]
                state=decode_seq(state)

                try:
                    if state[0][0] != id: state=[id,[]],
                except IndexError: state=[id,[]],
            else: state=[id,[]],

            if md.get('tree-e'):
                diff=decode_seq(md['tree-e'])
                apply_diff(state, diff, 1)

            if md.get('tree-c'):
                diff=decode_seq(md['tree-c'])
                apply_diff(state, diff, 0)


        colspan=tpStateLevel(state)
        substate=state
        diff=[]

        url=''
        root=md['URL']
        l=root.rfind('/')
        if l >= 0: root=root[l+1:]

    treeData={'tree-root-url': root,
              'tree-colspan': colspan,
              'tree-state': state }

    prefix = args.get('prefix')
    if prefix:
        for k, v in treeData.items():
            treeData[prefix + k[4:].replace('-', '_')] = v

    md._push(InstanceDict(self, md))
    md._push(treeData)

    try: tpRenderTABLE(self,id,root,url,state,substate,diff,data,colspan,
                       section,md,treeData, level, args)
    finally: md._pop(2)

    if state is substate and not (args.has_key('single') and args['single']):
        state=state or ([id],)
        state=encode_seq(state)
        md['RESPONSE'].setCookie('tree-s' + args['state_id'], state, path=args['state_url'])
    return ''.join(data)

def tpRenderTABLE(self, id, root_url, url, state, substate, diff, data,
                  colspan, section, md, treeData, level=0, args=None,
                  simple_type={type(''):0, type(1):0, type(1.0):0}.has_key,
                  ):
    "Render a tree as a table"

    have_arg=args.has_key
    exp=0

    if level >= 0:
        urlattr=args['url']
        if urlattr and hasattr(self, urlattr):
            tpUrl=getattr(self, urlattr)
            if not simple_type(type(tpUrl)): tpUrl=tpUrl()
            url = (url and ('%s/%s' % (url, tpUrl))) or tpUrl
            root_url = root_url or tpUrl

    ptreeData = add_with_prefix(treeData, 'tree', args.get('prefix'))
    ptreeData['tree-item-url']=url
    ptreeData['tree-level']=level
    ptreeData['tree-item-expanded']=0
    ptreeData['tree-item-code']=0
    idattr=args['id']

    output=data.append

    items=None
    if (have_arg('assume_children') and args['assume_children']
        and substate is not state):
        # We should not compute children unless we have to.
        # See if we've been asked to expand our children.
        for i in range(len(substate)):
            sub=substate[i]
            if sub[0]==id:
                exp=i+1
                break
        if not exp: items=1

    get=md.guarded_getattr
    if get is None:
        get = getattr

    if items is None:
        if have_arg('branches') and hasattr(self, args['branches']):
            items = get(self, args['branches'])
            items = items()
        elif have_arg('branches_expr'):
            items=args['branches_expr'](md)

        ids=[]
        for item in items: ids.append( item.id )

        if have_arg('content_filter'):
            items=map( lambda item: item[1],
                      self._filteredItems( ids, eval(args['content_filter']) ) )

        if not items and have_arg('leaves'): items=1

    if items and items != 1:
        getitem = getattr(md, 'guarded_getitem', None)
        if getitem is not None:
            unauth=[]
            secured=None
            security=None

            while secured is None:
                secured = 1
                for index in range(len(items)):
                    md._push(InstanceDict(items[index], md))

                    if have_arg('security') and hasattr(items[index], args['security']):
                        security = get(items[index], args['security'])
                        security = security()
                    elif have_arg('security_expr'):
                        security=args['security_expr'](md)
                    else:
                        security = 1

                    try:

                        if not security:
                            if have_arg('branches') and hasattr(self, args['branches']):
                                subitems = get(items[index], args['branches'])
                                subitems = subitems()
                            elif have_arg('branches_expr'):
                                subitems=args['branches_expr'](md)

                            del items[index]

                            items+=subitems
                            secured = None
                            md._pop()

                            break
                    except ValidationError:
                        unauth.append(index)

                    md._pop()

                    if unauth:
                        if have_arg('skip_unauthorized') and args['skip_unauthorized']:
                            items=list(items)
                            unauth.reverse()
                            for index in unauth: del items[index]
                        else:
                            raise ValidationError, unauth

        if have_arg('sort'):
            # Faster/less mem in-place sort
            if type(items)==type(()):
                items=list(items)
            sort=args['sort']
            size=range(len(items))
            for i in size:
                v=items[i]
                k=getattr(v,sort)
                try:    k=k()
                except: pass
                items[i]=(k,v)
            items.sort()
            for i in size:
                items[i]=items[i][1]

        if have_arg('reverse'):
            items=list(items)           # Copy the list
            items.reverse()
    diff.append(id)


    _td_colspan='<TD COLSPAN="%s" NOWRAP></TD>'
    _td_single ='<TD WIDTH="16" NOWRAP></TD>'

    sub=None
    if substate is state:
        output('<TABLE CELLSPACING="0">\n')
        sub=substate[0]
        exp=items
    else:
        # Add prefix
        output('<TR>\n')

        # Add +/- icon
        if items:
            if level:
                if level > 3:   output(_td_colspan % (level-1))
                elif level > 1: output(_td_single * (level-1))
                output(_td_single)
                output('\n')
            output('<TD WIDTH="16" VALIGN="TOP" NOWRAP>')
            for i in range(len(substate)):
                sub=substate[i]
                if sub[0]==id:
                    exp=i+1
                    break

            ####################################
            # Mostly inline encode_seq for speed
            if _use_mini_unpickler:
                s=compress(dumps(diff,1))
            else:
                s=compress(str(diff))
            if len(s) > 57: s=encode_str(s)
            else:
                s=b2a_base64(s)[:-1]
                l=s.find('=')
                if l >= 0: s=s[:l]
            s=translate(s, tplus)
            ####################################

            script=md['SCRIPT_NAME']

            # Propagate extra args through tree.
            if args.has_key( 'urlparam' ):
                param = args['urlparam']
                param = "%s&" % param
            elif args.has_key( 'urlparam_expr' ):
                param = args['urlparam_expr']( md )
                param = "%s&" % param
            else:
                param = ""

            if have_arg('mi_icon'):
                mi_icon=args['mi_icon']
            else:
                mi_icon=script + '/p_/mi'

            if have_arg('pl_icon'):
                pl_icon=args['pl_icon']
            else:
                pl_icon=script + '/p_/pl'

            if exp:
                ptreeData['tree-item-expanded']=1
                output('<A HREF="%s?%stree-c=%s#%s">'
                       '<IMG SRC="%s" ALT="-" BORDER=0></A>' %
                       (root_url, param, s, id, mi_icon))
            else:
                output('<A HREF="%s?%stree-e=%s#%s">'
                       '<IMG SRC="%s" ALT="+" BORDER=0></A>' %
                       (root_url, param, s, id, pl_icon))

            ptreeData['tree-item-code']=s

            output('</TD>\n')

        else:
            if level > 2:   output(_td_colspan % level)
            elif level > 0: output(_td_single  * level)
            output(_td_single)
            output('\n')


        # add item text
        dataspan=colspan-level
        output('<TD%s%s VALIGN="TOP" ALIGN="LEFT">' %
               ((dataspan > 1 and (' COLSPAN="%s"' % dataspan) or ''),
               (have_arg('nowrap') and args['nowrap'] and ' NOWRAP' or ''))
               )
        output(render_blocks(section, md))
        output('</TD>\n</TR>\n')


    if exp:

        level=level+1
        dataspan=colspan-level
        if level > 2:   h=_td_colspan % level
        elif level > 0: h=_td_single  * level
        else: h=''

        if have_arg('header'):
            doc=args['header']
            if md.has_key(doc): doc=md.getitem(doc,0)
            else: doc=None
            if doc is not None:
                output(doc(
                    None, md,
                    standard_html_header=(
                        '<TR>%s<TD WIDTH="16" NOWRAP></TD>'
                        '<TD%s VALIGN="TOP">'
                        % (h,
                           (dataspan > 1 and (' COLSPAN="%s"' % dataspan)
                            or ''))),
                    standard_html_footer='</TD></TR>',
                    ))

        if items==1:
            # leaves
            if have_arg('leaves'):
                doc=args['leaves']
                if md.has_key(doc): doc=md.getitem(doc,0)
                else: doc=None
                if doc is not None:
                    treeData['-tree-substate-']=sub
                    ptreeData['tree-level']=level
                    md._push(treeData)
                    try: output(doc(
                        None,md,
                        standard_html_header=(
                            '<TR>%s<TD WIDTH="16" NOWRAP></TD>'
                            '<TD%s VALIGN="TOP">'
                            % (h,
                               (dataspan > 1 and
                                (' COLSPAN="%s"' % dataspan) or ''))),
                        standard_html_footer='</TD></TR>',
                        ))
                    finally: md._pop(1)
        elif have_arg('expand'):
            doc=args['expand']
            if md.has_key(doc): doc=md.getitem(doc,0)
            else: doc=None
            if doc is not None:
                treeData['-tree-substate-']=sub
                ptreeData['tree-level']=level
                md._push(treeData)
                try: output(doc(
                    None,md,
                    standard_html_header=(
                        '<TR>%s<TD WIDTH="16" NOWRAP></TD>'
                        '<TD%s VALIGN="TOP">'
                        % (h,
                           (dataspan > 1 and
                            (' COLSPAN="%s"' % dataspan) or ''))),
                    standard_html_footer='</TD></TR>',
                    ))
                finally: md._pop(1)
        else:
            __traceback_info__=sub, args, state, substate
            ids={}
            for item in items:
                if hasattr(item, idattr):
                    id=getattr(item, idattr)
                    if not simple_type(type(id)): id=id()
                elif hasattr(item, '_p_oid'): id=oid(item)
                else: id=pyid(item)
                if len(sub)==1: sub.append([])
                substate=sub[1]
                ids[id]=1
                md._push(InstanceDict(item,md))
                try: data=tpRenderTABLE(
                    item,id,root_url,url,state,substate,diff,data,
                    colspan, section, md, treeData, level, args)
                finally: md._pop()
                if not sub[1]: del sub[1]

            ids=ids.has_key
            for i in range(len(substate)-1,-1):
                if not ids(substate[i][0]): del substate[i]

        if have_arg('footer'):
            doc=args['footer']
            if md.has_key(doc): doc=md.getitem(doc,0)
            else: doc=None
            if doc is not None:
                output(doc(
                    None, md,
                    standard_html_header=(
                        '<TR>%s<TD WIDTH="16" NOWRAP></TD>'
                        '<TD%s VALIGN="TOP">'
                        % (h,
                           (dataspan > 1 and (' COLSPAN="%s"' % dataspan)
                            or ''))),
                    standard_html_footer='</TD></TR>',
                    ))

    del diff[-1]
    if not diff: output('</TABLE>\n')

    return data

def initialize( context ):
    context.registerDTCommand( Forest.name, Forest )
