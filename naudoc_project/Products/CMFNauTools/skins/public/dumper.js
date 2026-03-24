
// <!-- script type="text/javascript" -->


//
// $Editor: ypetrov $
// $Id: dumper.js,v 1.3 2004/07/28 14:50:04 vpastukhov Exp $
// $Revision: 1.3 $
//


//
// Recursively dumps JavaScript objects into separate window.
//
// An arbitrary number of arguments is accepted, each being
// an object to dump.  Optional switches can be specified after
// a separate '--' argument:
//
//   'clear' -- clear output window before dumping objects
//
//   'named' -- use first argument as a mapping from names to objects
//
function dumper()
{
    var wsh, obj, str, i, j;
    var flags = new Object();

    try {
        wsh = WScript; // under Windows Scripting Host
    } catch (wsh) {
        wsh = null; // under Web browser
    }

    for (j = 0; j < arguments.length; j++) {
        if (typeof arguments[j] == 'string' && arguments[j] == '--') {
            for (i = j + 1; i < arguments.length; i++)
                flags[ arguments[i].toLowerCase() ] = true;
            break;
        }
    }

    if (! wsh) {
        if (window == null)
            return false;
        if (__dumperWindow == null || __dumperWindow.closed) {
            __dumperWindow = window.open( '', 'dumper_window',
                        'menubar,scrollbars,resizable,width=500,height=500' );
            flags.clear = true;
        }
        __dumperWindow.focus();
        //__dumperWindow.onerror = null;
        if (flags.clear) with (__dumperWindow.document) {
            open();
            write('<pre>');
        }
    }

    if (j == 0)
        return false;

    if (flags.named && typeof(arguments[0]) == 'object'
                    && arguments[0]+'' == '[object Object]') {
        obj = arguments[0];
    } else {
        obj = new Object();
        for (i = 0; i < j; i++)
            obj[ 'VAR' + (i + 1) ] = arguments[i];
    }

    str = __dumpObject( obj );
    if (! wsh)
        __dumperWindow.document.write( escapeHTML(str) + '\n<hr/>' );
    else
        wsh.StdErr.Write( str + '\n----------------------------------------\n' );

    return true;
}

// remembers opened dumper window
var __dumperWindow = null;
var __dumperSkip = {
    'innerHTML' : true,
    'innerText' : true,
    'parentElement' : true,
    'parentNode' : true,
    'offsetParent' : true,
    'previousSibling' : true,
    'nextSibling' : true,
    'firstChild' : true,
    'lastChild' : true
};

// helper function for dumper
function __dumpObject( obj, lev, hier )
{
    if (obj == null)
        return 'null';

    if (lev == null)
        lev = 0;
    else if (lev > 2)
        return '[...]';

    if (hier == null) {
        hier = new Array();
    } else {
        for (var i = 0; i < lev; i++)
            if (hier[i] == obj)
                return '[recurse: ' + (i - lev) + ']';
    }
    hier[lev] = obj;

    var error;
    var res = '';
    var pfx = '';
    for (var i = 0; i < lev; i++)
        pfx += '    ';

    for (var n in obj) {

        var p = obj[n];

        res += '\n' + pfx + n + ' (' + typeof(p) + ') = ';
        //alert(n + ' ' + typeof(p) + ' ' + p);

        if (__dumperSkip[n]) {
            res += '[...]';

        } else switch (typeof(p)) {
            case 'object':
                if (p == null) {
                    res += 'null';
                    break;
                }
                res += "'" + p + "' ";
                try {
                    res += __dumpObject( p, lev+1, hier );
                } catch (error) {
                    res += '[error: ' + error.description + ']';
                }
                break;

            case 'string':
                res += "'" + p + "'";
                break;

            case 'function':
                res += '[code]';
                break;

            default:
                res += p;
        }

        if (! lev)
            res += '\n';
    }

    delete hier[lev];
    return res;
}

// <!-- /script -->
