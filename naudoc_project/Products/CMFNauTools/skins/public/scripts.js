//
// $Editor: ypetrov $
// $Id: scripts.js,v 1.157 2008/09/18 12:20:46 oevsegneev Exp $
// $Revision: 1.157 $
//

//
// MS IE 5.0 does not support Function.apply and .call methods,
// thus we have this hack.
//
if (Function.prototype.apply == null) {
    Function.prototype.apply = function (o, a) {
        o.__f = this;

        var params = [];
        for (var i = 0; i < a.length; i++)
            params[i] = 'a[' + i + ']';

        try {
            return eval( 'o.__f(' + params.join(',') + ')' );
        }
        finally {
            var error;
            try           { delete o.__f }
            catch (error) { o.__f = null }
        }
    };
}

if (Function.prototype.call == null) {
    Function.prototype.call = function( func )
    {
        return this.apply( func, toArray(arguments, 1) );
    };
}

Function.prototype.getName = function()
{
    return this.toString().split(' ')[1].split('(')[0];
};

//
// Patch MS IE 5.0 Number prototype.
//
if (Number.prototype.toFixed == null) {
    Number.prototype.toFixed = function( d )
    {
        var n = this;
        d = d || 0;
        with (Math)
        {
            var f = pow(10, d);
            n = round(n * f) / f;
            n += pow(10, - (d + 1));
        }
        n += '';
        return n.substring(0, n.indexOf('.') + (d && d+1) );
    };
}

//
// Patch MS IE 5.0 Array prototype.
// NB: do not use 'for (.. in ..)' with arrays
//
if (Array.prototype.push == null) {
    Array.prototype.push = function ()
    {
        for (var i = 0; i < arguments.length; i++)
            this[ this.length ] = arguments[i];

        return this.length;
    };
}

if (Array.prototype.pop == null) {
    Array.prototype.pop = function ()
    {
        var item = this[ this.length-1 ];
        delete this[ this.length-1 ];
        return item;
    };
}

String.prototype.endswith = function(part)
{
    var part_len = part.length;
    var this_len = this.length;

    return (this_len >= part_len) &&
           (this.substring(this_len-part_len, this_len) == part);
}

String.prototype.startswith = function(part)
{
    var part_len = part.length;
    var this_len = this.length;

    return (this_len >= part_len) &&
           (this.substring(0, part_len) == part);
}

// returns day of week number considering that monday is first
Date.prototype.getDayMF = function()
{

    return (this.getDay() + 6) % 7;
}

//
//    returns week number in month that includes current day of week
//    (e.g. 1 for the second wednesday, 3 for the fourth monday etc.)
//    Note that it isn't equal to the number of current week in month.
//
Date.prototype.getWeekWithDay = function()
{
    return Math.floor((this.getDate() - 1) / 7);
}


//
// Returns a copy of a given javascript object.
// XXX  cannot patch prototype in MS IE 5.0 because
//      it would break 'for (.. in ..)' loops
//
//Object.constructor.prototype.cloneObject =
function cloneObject( source, deep )
{
    //var source = this;
    var clone = new source.constructor();
    for (var property in source)
        if (typeof source[property] == 'object' && deep)
            clone[property] = cloneObject( source[property], deep);
        else
            clone[property] = source[property];

    return clone;
}

//
// Constructor for the UserAgent object.
// Detects user agent type, version and features.
//
function UserAgent()
{
    //var s = '';
    //for (k in navigator)
    //  s += k+'="'+navigator[k]+'"\n';
    //alert(s);

    var version = navigator.appVersion;
    var error;

    if (navigator.appName == 'Microsoft Internet Explorer') {
        this.type = 'IE';
        this.version = parseFloat( version.substr( version.indexOf('MSIE') + 4 ) );
        this.hasCoveredBug = true;
        this.brokenSetMultiple = true;

        var xmlhttp_classes = ['msxml2.XMLHTTP.4.0', 'Microsoft.XMLHTTP'];
        for (var i = 0; i < xmlhttp_classes.length; i++)
            try {
                new ActiveXObject(xmlhttp_classes[i]);
                this.hasXMLHTTP = true;
                // XXX: actually decoding bug was fixed between msxml 3.0 SP1 and SP3,
                //      but we cannot detect that some service pack was installed
                this.hasDecodingBug = (i != 0);
                break;
            } catch (error) {
                // pass
            }
    } else if (navigator.product == 'Gecko') {
        this.type = 'MZ';
        this[ 'NS6' ] = true;
        try {
            new XMLHttpRequest();
            this.hasXMLHTTP = true;
        } catch (error) {
            // pass
        }
    } else if (navigator.appName == 'Netscape') {
        this.type = 'NS';
        if (navigator.vendor == 'Netscape6')
            this.version = 6;
    }

    if (! this.version)
        this.version = parseFloat(version);

    this.major = parseInt( this.version );

    if (this.type) {
        this[ this.type ] = true;
        this[ this.type + this.major ] = true;
        this[ this.type + this.version ] = true;
    }

    this.hasComputedStyle = !! (window.document.defaultView &&
                                window.document.defaultView.getComputedStyle);
}

//
// Returns actual width of the given frame in pixels.
//
UserAgent.prototype.getFrameWidth = function ( frame )
{
    if (this.IE) {

        if (this.version < 5.5)
            return frame.document.body.offsetWidth;

        // TODO: use frame index
        else if (this.version < 6)
            return parseInt( frame.parent.document.body.cols ) &&
                   frame.document.body.offsetWidth;
        else
            return parseInt( frame.parent.document.body.cols );
    }

    return frame.innerWidth;
};

//
// Constructor for a dictionary-like object.
//
function Mapping( source )
{
    if (source)
        this.update( source );
}

Mapping.prototype.update = function ( source, keep )
{
    var proto = this.constructor.prototype;
    for (var n in source)
        if (proto[n] == null && (!keep || this[n] == null))
            this[n] = source[n];
};

//
// Creates custom exception object
//
function Exception(name, message, kw)
{
    var exception = {};

    exception.name = name;
    exception.message = message;
    exception.toString = function () { return message };

    if (kw != null)
        for (var k in kw) exception[k] = kw[k];

    return exception;
}

//
// Downloads contents of page located by url.
//
// When ready_callback function specified download runs in async mode.
//
// Arguments:
//
//     'ready_callback' -- callback function that receives page contents in
//                         async mode.
//
//     'error_callback' -- callback function that receives exceptions in
//                         async mode.
//
// Exceptions:
//
//     'NotImplemented' -- XMLHTTP is not supported by user agent.
//
//     'DownloadError' -- response status differ from OK. Status code passed
//                        via 'status' attribute, page contents in 'text'.
//
UserAgent.prototype.downloadURL = function(url, ready_callback, error_callback)
{
    var async = (ready_callback != null),
        hasDecodingBug = this.hasDecodingBug,
        request;

    if (async && error_callback == null) error_callback = function() {};

    if (! this.hasXMLHTTP) {
        var error = Exception('NotImplemented', "XMLHTTP is not supported by your browser");

        if (async) {
            error_callback(error);
            return;
        } else
            throw error;
    }

    if (this.IE) // IE MSXML object
        request = new ActiveXObject('Microsoft.XMLHTTP');
    else // Mozilla object
        request = new XMLHttpRequest();

    function processResponse()
    {
        if (async && request.readyState != 4) return;

        var responseText = '';

        if (! hasDecodingBug)
            responseText = request.responseText;

        else {
            // workaround of msxml charset decoding bug (code was taken from
            // http://relib.com/forums/topic.asp?id=751103)

            var rs = new ActiveXObject('ADODB.Recordset');

            rs.Fields.Append('ru', 200, 100000);
            rs.Open();
            rs.AddNew();
            rs.Fields.Item(0).AppendChunk(request.ResponseBody);
            responseText += rs.Fields.Item(0);
            rs.Close();
        }

        if (request.status == 200) {
            if (async) ready_callback(responseText);
                  else return responseText;
        } else {
            var error = Exception( 'DownloadError'
                                 , request.status + ' ' + request.statusText
                                 , {'status': request.status, 'text': responseText}
                                 );

            if (async) error_callback(error);
                  else throw error;
        }
    }

    if (async) request.onreadystatechange = processResponse;

    if (this.IE) // XXX
        url = setParam(url, '_T', (new Date().getTime()));

    request.open('GET', url, async);
    request.send(null);

    if (! async) return processResponse();
};

//
// Fix scripts in downloaded content
//
function fixScripts( container ){
    var scripts = container.getElementsByTagName('script');
    for (var idx=0; idx<scripts.length; idx++ ) {
        var new_script = document.createElement('script');

        if (scripts[idx].src)
            new_script.src = scripts[idx].src;
        else
            new_script.text = scripts[idx].text;

        scripts[idx].parentNode.replaceChild(new_script, scripts[idx]);
    }
}

//
// Constructs CookieManager object which cache document cookies and
// implement their management methods: set, get and remove
//
function CookieManager()
{
    var cookies_cache = {};

    var crumbs = document.cookie.split('; ');
    for (var i=0; i < crumbs.length; i++) {
        var crumb = crumbs[i].split('=');
        cookies_cache[crumb[0]] = unescape(crumb[1]);
    }

    this.get = function(name)
    {
        return cookies_cache[name];
    };

    this.set = function(name, value, expires, domain, path)
    {
        var cookie_value = name + '=' + escape(value) + '; ';

        if (expires) {
            cookie_value += 'expires=';

            if (expires.constructor == Date) cookie_value += expires.toGMTString();
                                        else cookie_value += expires;

            cookie_value += '; ';
        }

        if (domain) cookie_value += 'domain=' + domain + '; ';

        if (path) cookie_value += 'path=' + path + '; ';

        document.cookie = cookie_value;
        cookies_cache[name] = value;
    };

    this.remove = function(name)
    {
        document.cookie = name + '=; expires=Thu, 1 Jan 1970 00:00:00 UTC';
        delete cookies_cache[name];
    };
}


//
// Registers callback for an event.
//
// Arguments:
//
//     'object' -- object on which to watch for events
//     'type' -- name of the event, with 'on' prefix
//     'callback' -- callback function object
//     'retval' -- required callback result (optional)
//
// Additional arguments are passed to the callback function as-is.
//
// Result:
//
//     Queue entry Id (actually, the callback's ordinal
//     number in the callbacks queue for this event).
//
function registerCallback( object, type )
{
    type = type.toLowerCase();
    object[ type ] = runCallbacks;

    var items = object[ type+'__callbacks__' ];
    if (items == null)
        items = object[ type+'__callbacks__' ] = new Array();

    var id = items.length;
    items[ id ] = toArray(arguments, 2);

    return id;
}

//
// Removes callback from then event queue.
//
// Arguments:
//
//     'object', 'type' -- as per 'registerCallback'
//     'id' -- queue entry Id received from 'registerCallback'
//
function unregisterCallback( object, type, id )
{
    type = type.toLowerCase();
    var items = object[ type+'__callbacks__' ];

    if (items && items.length > id)
        items[ id ] = null;
}

//
// Executes registered callbacks.
//
// The first argument of the function is the object that fired
// the event, the second is current Event object, and the rest
// are custom arguments passed to callback registration.
//
// The callback function is called with 'this' set to the object
// that fired the event (XXX does not work in MSIE 5.0).
//
// If 'retval' was specified and the return value of the function
// differs from it, the callbacks queue processing is interruptted
// and that value is returned as a result if the event handler.
//
function runCallbacks( event, object )
{
    if (object == null)
        object = this;

    var win = object.window || getDocument(object).parentWindow;
    var type, error;

    // determine event type
    if (typeof(event) == 'string') {
        type = event.toLowerCase();
        event = null;
    } else {
        event = event || win.event;
        type = 'on' + event.type.toLowerCase()
    }

    // get queue of the registered callbacks
    var items = object[ type+'__callbacks__' ];
    if (items == null) {
        // try to run ordinary js callback
        var callback = object[ type ];
        if (! callback)
            return true;
        return callback.apply( object, new Array(event) );
    }

    for (var i = 0; i < items.length; i++) {
        // item is [ callback, retval, args... ]
        var item = items[i];
        if (! item)
            continue; // was unregistered

        // build arguments list
        // NB: slice method in IE snaps on arrays
        //     from unloaded documents, so the loop is used
        var args = new Array( event );
        for (var j = 2; j < item.length; j++)
            args[ args.length ] = item[j];

        // now run the callback function
        var callback = item[0];
        var retval;
        try {
            retval = callback.apply( object, args );
        } catch (error) {
            if (error.number == -2146823277) {
                // the script was unloaded (MSIE)
                items[i] = null;
                continue;
            }
            throw error;
        }

        // check return value
        var wanted = item[1];
        if (wanted != null && retval != wanted)
            return retval;
    }

    return true;
}

//
// Registers onSubmit callback for a given form.
//
// Arguments:
//
//    'name' -- form's name
//    'callback' -- callback function object
//    'retval' -- required callback result or 'null'
//
// Additional arguments are passed to the callback as-is.
//
function registerFormCallback( name )
{
    var args = new Array( document.forms[ name ], 'onSubmit' );
    args = args.concat( toArray(arguments, 1) );
    registerCallback.apply( this, args );
}

//
// Removes all onSubmit callbacks from the event queue for a given form.
//
// Arguments:
//
//    'name' -- form name
//
function clearFormCallbacks( name )
{
    type = 'onsubmit';
    form = document.forms[ name ];
    form[ type ] = '';
    form[ type+'__callbacks__' ] = null;
}


//
// Returns windows object containing the element.
//
function getWindow( element )
{
    var doc = getDocument( element );
    return (doc.defaultView || doc.parentWindow || doc.window);
}

//
// Returns document object the element belongs to.
//
function getDocument( element )
{
    return (element.body ? element : element.ownerDocument || element.document);
}

//
// Returns parent IFRAME element of the given window object.
//
function getParentFrame( win )
{
    if (win.frameElement)
        return win.frameElement;

    var iframes = win.parent.document.getElementsByTagName( 'iframe' );
    var windows = win.parent.document.frames;
    if (windows && iframes.length != windows.length)
        return null;

    for (var i = 0; i < iframes.length; i++) {
        var iframe = iframes[i];
        if (iframe.contentWindow && iframe.contentWindow == win)
            return iframe;
        if (windows && windows[i] == win)
            return iframe;
    }

    return null;
}

//
// Resizes parent IFRAME to accommodate the element identified by 'id'.
//
function resizeParentFrame( id, win )
{
    win = win || window;
    var frame = getParentFrame( win );
    var element = win.document.getElementById( id );
    if (! (frame && element))
        return;
    if (element.rows != null)
        frame.style.display = element.rows.length ? 'inline' : 'none';

    frame.width  = element.offsetWidth  + 15;
    frame.height = element.offsetHeight + 15;
}

//
// Set query parameter in the url string
//
function setParam( url, name, value )
{
    var url_hash = url.split('#'),
        url  = url_hash[0],
        hash = (url_hash[1] ? '#' + url_hash[1] : '');

    name  = escapeURL(name);
    value = name + '=' + escapeURL(value);

    if (url.indexOf('?') == -1)
        return url + '?' + value + hash;

    var param_re = new RegExp( '([?&])' + name + '=[^&]*' );
    if (url.match( param_re ))
        // replace existing value
        return url.replace( param_re, '\$1' + value ) + hash;

    return url + '&' + value + hash;
}

//
// Escape special characters in the HTML string
//
function escapeHTML( str, nlbr )
{
    for (var c in escapeHTMLMap)
        str = str.replace( new RegExp(c, 'g'), escapeHTMLMap[c] );
    if (nlbr)
        str = str.replace( new RegExp('\\r*\\n', 'g'), '<br />\n' );
    return str;
}

//
// Escape special characters in the URL string
//
function escapeURL( str )
{
    var plusRegexp = new RegExp('\\+', 'g');

    if (! userAgent.IE)
        return escape(str).replace(plusRegexp, '%2B');

    else {
        // convert cyrillic characters from unicode into cp1251 and escape it
        // (native IE method escapes unicode in proprietary format %u1234)
        var r = '';
        str = str.toString(); // convert str to string

        for (var i = 0; i < str.length; i++) {
            var n = str.charCodeAt(i);

            if (n >= 0x410 && n <= 0x44F) // À-ÿ
                n -= 0x350;
            else if (n == 0x451) // ¸
                n = 0xB8;
            else if (n == 0x401) // ¨
                n = 0xA8;

            if ((n != 42 && n < 45) || (57 < n && n < 65) || (90 < n && n != 95 && n < 97) || (122 < n && n < 256))
                r += '%' + (n < 16 ? '0' : '') + n.toString(16);
            else
                r += str.charAt(i);
        }

        return r;
    }
}

//
// Converts url to format suitable for workfield frame
//
function formatForWorkfield(url)
{
    var base = objectBaseURL + '/inFrame',
        url_hash = url.split('#');

    if (url_hash[1])
        return setParam(setParam(base, 'link', url_hash[0]), 'hash', url_hash[1]);

    return setParam(base, 'link', url);
}

//
// Check for top level frameset and create it if necessary
//
function checkFrameSet()
{
    if (! window.openInFrame)
        return true;

    var url  = window.redirectURL || window.location.href;

    if (window.parent.frames.length > 0) {

        if (window.openInFrame == 'workspace' && window.name == 'workfield') {
            // workspace was incorrectly opened in the workfield
            window.parent.location.replace( url );
            return false;
        }

        if (window.openInFrame == 'workfield' && window.name == 'workspace') {
            // workfield was incorrectly opened as the workspace
            window.location.replace( formatForWorkfield(url) );
            return false;
        }

        // frames seem to be ok
        return true;
    }

    url = setParam( url, '_R', Math.random() );
    if (userAgent.IE) {
        // XXX: IE assigns value of link target to name of opened window when
        //      it opened with Shift-Click
        window.name = '';
    }

    if (window.openInFrame == 'workfield')
        url = formatForWorkfield(url);

    // no frameset exist yet; create frames
    document.open();
    document.write(
        '<frameset cols="295,*" framespacing="5">\n' +
        '<frame name="menu" src="' + portalRootURL + '/menu" scrolling="no" marginwidth="0" marginheight="0" frameborder="0">\n' +
        '<frame name="workspace" src="' + url + '" scrolling="no" marginwidth="0" marginheight="0" frameborder="0">\n' +
        '</frameset>\n'
    );
    document.close();
    
    return false;
}

//
// Open user info popup
//
function OpenUserInfoWnd( user )
{
    var url = setParam( window.objectBaseURL + '/user_info_form', 'userid', user );
    window.open( url, '_blank', 'toolbar=no,scrollbars=no,status=yes,width=450,height=550,resizable=yes' );
}

//
// Open position info popup
//
function OpenPositionInfoWnd( entry_url )
{
    var url = setParam( entry_url + '/directory_entry_form', 'OpenInFrame', '' );
    url = setParam( url, 'inline', '1' );
    window.open( url, '_blank', 'toolbar=no,scrollbars=no,status=yes,width=450,height=350,resizable=yes' );
}

//
// Open NauDoc object selection box
// callback_function will be called with 5 params: uid, title, ver_id, uid_field_value, title_field_value (in future may be more params.)
// Arguments:
//     'callback_form' - required.
//     'callback_function' - required.
//     'search_path' - optional. beginning path.
//     'search_features' - optional. features of searching types.
//     'uid_field' - optional. need for callback.
//     'title_field' - optional. need for callback.
//     'categories' - categories of the search objects.
function OpenDocumentSelectionWnd( callback_form, callback_function, search_scope, search_features, uid_field, title_field, categories, search_types, getPath, target_window )
{
    var url = window.portalRootURL + '/storage/explorer_frame';

    url = setParam( url, 'open_explorer:int' , 1);
    url = setParam( url, 'callback_function', callback_function);
    url = setParam( url, 'callback_form', callback_form);

    if ( uid_field )
        url = setParam( url, 'uid_field', uid_field);
    if ( title_field )
        url = setParam( url, 'title_field', title_field);

    if ( search_scope )
        url = setParam( url, 'root:uid', search_scope);
    if ( categories )
        url = setParam( url, 'folder_categories:sentences', categories);
    if ( search_types )
        url = setParam( url, 'folder_search_types:sentences', search_types);
    if ( getPath )
        url = setParam( url, 'folder_getPath', 1);

    url = setParam( url, 'folder_search_features:sentences'
                  , search_features ? search_features : 'isPortalContent');

    registerWindow( callback_form + '|' + callback_function + '|' + uid_field
                  , url
                  , 'dependent=yes,toolbar=no,scrollbars=yes,status=yes,width=550,height=550,resizable=yes'
                  , target_window
                  );

}

//
// this function returns to callback_function: title, path_to_object
// DEPRECATED soon, use OpenDocumentSelectionWnd
function OpenDocumentSelectionWndPath( callback_function )
{
    OpenDocumentSelectionWnd( '', callback_function, '', '', '', '', '', '', 1 ); // XXX. backward compatibility
}

//
// register window in windowManager object
function registerWindow( id, url, params, target_window )
{
    target_window = target_window || window;

    var win = windowManager[id];

    if (win && ! win.closed)// this also check, that win is closed
        win.focus();
    else
    {
        win = windowManager[id] = target_window.open( url, '_blank', params);

        registerCallback( target_window, 'onUnload', _closeWindowCallback, null, win );
    }

    return win;
}

//
// Callback for automatic close of dependent windows.
//
function _closeWindowCallback( ev, win )
{
    if (win && ! win.closed)
        win.close();
}

//
// Refresh navigation frame
//
function updateNavFrame( section )
{
    if (! window.parent)
        return;

    var frame = top.frames['menu'];
    if (! frame)
        return;

    var width = userAgent.getFrameWidth( frame );

    if (section == null && frame.needsUpdate != null) {
        section = frame.needsUpdate;
        frame.needsUpdate = null;
    }

    if (frame.savedWidth && width <= 1) {
        // navigation frame is hidden
        frame.needsUpdate = section;
        return;
    }

    // do actual refresh
    frame.reload( section, 1 );
}

//
// Toggle expanded workspace view
//
function toggleExpand()
{
    if (! window.parent)
        return;

    var frame = top.frames['menu'];
    var width = userAgent.getFrameWidth( frame );

    if (frame.savedWidth && width <= 1) {
        top.document.body.cols = frame.savedWidth + ',*';
        frame.savedWidth = null;

        if (frame.needsUpdate != null)
            // navigation tree was changed
            updateNavFrame();

    } else {
        top.document.body.cols = '0,*';
        frame.savedWidth = width;
    }
}

//
// Preload rollover images
//
function preloadImages()
{
    if (arguments.length == 0)
        return;

    var images;
    if (typeof( arguments[0] ) == 'object') {
        images = arguments[0];

    } else {
        images = new Array();
        for (var i = 0; i < arguments.length; i++)
            images[i] = arguments[i];
    }

    registerCallback( window, 'onLoad', runPreloadImages, null, images );
}

function setStatus( status_message )
{
    this.status = status_message.toString();
    return true;
}

function resetStatus()
{
    this.status = '';
}

function runPreloadImages( event, images )
{
    var preload = this.preloadArray;
    var url = this.portalImagesURL;

    for (var i = 0; i < images.length; i++) {
        var image = preload[ preload.length ] = new Image();
        image.src = url + '/' + images[i];
    }
}

//
// Roll the image on event
//
function change( image, what )
{
    var name;

    switch (what) {
        case 1: name= image.name + '_over.gif'; break;
        case 2: name= image.name + '.gif'; break;
        case 3: name= image.name + '_click.gif'; break;
    }

    if (name)
        image.src = portalImagesURL + '/' + name;
}

//
// Hide/show overlapped elements on the page.
// Adapted from JSCalendar by Mihai Bazon, <mishoo@infoiasi.ro>
//
function hideCoveredElements( element, hide )
{
    if (hide == null)
        hide = true;

    var doc  = getDocument( element );
    var tags = [ 'applet', 'iframe', 'select' ];

    var p = getAbsolutePos(element);
    var x1 = p.x1;
    var x2 = p.x2;
    var y1 = p.y1;
    var y2 = p.y2;

    for (var i = tags.length; i-- > 0; ) {
        var objs = doc.getElementsByTagName(tags[i]);

        for (j = objs.length; j-- > 0; ) {
            var obj = objs[j];
            var v;

            if (hide) {
                v = getStyleProp(obj, 'visibility');
                if (v == 'hidden')
                    continue;

                p = getAbsolutePos(obj);
                if (p.x1 > x2 || p.x2 < x1 || p.y1 > y2 || p.y2 < y1)
                    continue;

                obj._nau_saved_visibility = v;
                obj.style.visibility = 'hidden';

            } else if (obj._nau_saved_visibility) {
                obj.style.visibility = obj._nau_saved_visibility;
                obj._nau_saved_visibility = null;
            }
        }
    }
}

//
// Returns record of element's dimensions and position in a window.
//
function getAbsolutePos( element )
{
    var pos = { x1: element.offsetLeft, y1: element.offsetTop };
    if (element.offsetParent) {
        var par = getAbsolutePos(element.offsetParent);
        pos.x1 += par.x1;
        pos.y1 += par.y1;
    }
    pos.x2 = pos.x1 + ( pos.w = element.offsetWidth  ) - 1;
    pos.y2 = pos.y1 + ( pos.h = element.offsetHeight ) - 1;
    return pos;
}

//
// Returns current value of the elements's style property.
//
function getStyleProp( element, style )
{
    var value = element.style[ style ];
    if (value)
        return value;

    if (userAgent.hasComputedStyle) {
        var doc = getDocument( element );
        value = doc.defaultView.getComputedStyle(element, '').getPropertyValue(style);
    } else if (element.currentStyle) {
        value = element.currentStyle[ style ];
    }

    return value;
}

//
// Returns event's target element.
//
function getEventTarget( ev )
{
    ev = ev || window.event;
    var ob = ev.target || ev.srcElement;
    if (ob.tagName.toLowerCase() == 'option' || ob.tagName.toLowerCase() == 'span')
        ob = ob.parentNode;
    return ob;
}

//
// Determines whether the element is the original event target.
//
function isElementEventTarget( ev, element )
{
    ev = ev || window.event;

    var target = ev.explicitOriginalTarget;
    if (target != null) {
        if (target.tagName.toLowerCase() == 'span')
            target = target.parentNode;
        return (target == element);
    }

    var x = ev.clientX;
    var y = ev.clientY;
    var p = getAbsolutePos(element);

    return (x >= p.x1 && x <= p.x2 && y >= p.y1 && y <= p.y2);
}

//
// Returns corresponding label element for the form input field.
//
function getLabelFor( form, elem )
{
    var name;
    if (typeof(elem) == 'object')
        name = elem.name.toLowerCase();
    else
        name = elem.toString().toLowerCase();

    var labels = form.getElementsByTagName('label');

    for (var i = 0; i < labels.length; i++) {
        var htmlfor = labels[i].htmlFor;
        if (htmlfor && htmlfor.toLowerCase() == name)
            return labels[i];
    }

    return null;
}

//
// Navigates the browser to the URL of the child link element,
// either enumerated by index or the first one.
//
function followInnerLink( element, index )
{
    var links = element.getElementsByTagName('a');

    if (links) {
        // TODO handle target frame
        window.location.href = links[ index || 0 ].href;
        return false;
    }

    return true;
}

//
// Disables form's submit action.
//
function disableForm( form )
{
    if (form == null || form.tagName != 'FORM')
        // must be an event handler
        form = this

    if (form.isFormDisabled) return true

    if (form.onsubmit) {
        form._old_onsubmit = form.onsubmit
        form.onsubmit = function () { return false }
    }

    form.isFormDisabled = true
    addClass(form, 'disabled')

    return true
}

//
// Enables form's submit action.
//
function enableForm( form )
{
    if (form == null || form.tagName != 'FORM')
        // must be an event handler
        form = this

    if (! form.isFormDisabled) return true

    if (form._old_onsubmit) {
        form.onsubmit = form._old_onsubmit
        form._old_onsubmit = null
    }

    form.isFormDisabled = false
    removeClass(form, 'disabled')

    return true
}

//
// Annuls all required fields in the form.
// (to shup ZPublisher up in case some "Cancel" button is hit)
// + replace onsubmit handler that returns always true
//
function cancelForm( form )
{
    for (var i = 0; i < form.elements.length; i++) {
        with (form.elements[i])
            if (name)
                name = name.replace( fieldRequiredRegexp, '' );
    }

    form.onsubmit = function () { return true };
    form.isCancelled = true;
    return true;
}

//
// Validate user form (used in heading/manage_access_form, membership/change_ownership_form)
//
function validateUserForm(form) {
    if ( form['userid'] && !testField( form.userid, null, messageCatalog.select_user ) )
        return false;

    if ( form['userids:list'] && selectAll( form['userids:list'] ) && !testField( form['userids:list'], null, messageCatalog.select_user ) )
        return false;

    if ( form['roles:list'] && !testField( form['roles:list'], null, messageCatalog.select_role ) )
        return false;

    return true;
}

//
// Validate range
//
function validateRange( type, min, max )
{
    var rx_min = validationRegexp[type].exec(min),
        rx_max = validationRegexp[type].exec(max),
        from, till;

    // Mozilla support
    for( i=5; i<7; i++ ){
      if( !rx_min[i] ) rx_min[i] = 0;
      if( !rx_max[i] ) rx_max[i] = 0;
    }

    switch (type) {
        case 'datetime':
            from = new Date(rx_min[3], rx_min[2] - 1, rx_min[1], rx_min[5], rx_min[6]); 
            till = new Date(rx_max[3], rx_max[2] - 1, rx_max[1], rx_max[5], rx_max[6]);
            break;

        default:
            from = rx_min[0]; 
            till = rx_max[0];
    }      

    return (from <= till);
}

//
// Validate date
//
function validateDate( year, month, day )
{
    month = month - 1;

    var tempDate = new Date(year, month, day);

    return ( (tempDate.getFullYear() == year) &&
             (tempDate.getMonth() == month) &&
             (tempDate.getDate() == day) );
}

//
// Validate time
//
function validateTime( hour, minute )
{
    return ( Number(hour) < 24 && Number(minute) < 60 )
}

//
// Validate e-mail address
//
function validateEmail( field, message, allow_empty )
{
    return testField( field, 'email', message, allow_empty );
}

//
// Validate object identifier
//
function validateIdentifier( field, message, allow_empty )
{
    return testField( field, 'id', message, allow_empty );
}

//
// Validate object identifier (strong version)
//
function validateIdentifierStrong( field, message )
{
    return testField( field, 'idstrong', message, false );
}

//
// Validate field value by type, using associated regular expression.
//
function testField( field, type, message, allow_empty )
{
    var value = field.value;
    var regexp;

    if (typeof(type) == 'string') {
        if (type.substr(type.length-1) == '_')
            type = type.substr(0, type.length-1);
        regexp = validationRegexp[ type ];
    } else if (type != null) {
        regexp = type;
        type = null;
    }

    if (! message)
        message = field.getAttribute('validation_message');

    if (type == 'required')
        allow_empty = false;

    else if (allow_empty == null)
        allow_empty = ! message;

    if (! message) {
        message = validationMessages[ type ];
        if (! message)
            return true;
    }

    do {
        if (emptyValueRegexp.test( value )) {
            if (value.length)
                // prevent whitespace from being submitted
                field.value = '';
            if (! allow_empty) break;
            // value is not required
            return true;
        }

        if (regexp && ! regexp.test(value)) break;

        if (type == 'id' || type == 'idstrong') {
            if (value.substr(0,1) == '_') break;
            if (value.substr(0,3) == 'aq_') break;
            if (value.substr(-2,2) == '__') break;
        }
        else if (type == 'date') {
            if (! validateDate(RegExp.$3, RegExp.$2, RegExp.$1)) break;
        }
        else if (type == 'datetime') {
            if (! validateDate(RegExp.$3, RegExp.$2, RegExp.$1)) break;
            if (RegExp.$4 && ! validateTime(RegExp.$5, RegExp.$6)) break;
        }
        else if (type == 'search' ) {
            if (value.split('(').length != value.split(')').length) break; // may be this check in RegExp???
        }

        // value is ok
        return true;
    } while (false);

    field.focus();
    if (field.select != null)
        field.select();

    alert( messageCatalog[ message ] || message );
    return false;
}

//
// Validate form by detecting special fields
//
function validateForm( form, allow_empty, validate_mandatory )
{
    var elements = form.elements;

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];

        with (element)
            if (! ( (type == 'text' || type == 'textarea' || type == 'select-one') &&
                    name ) )
                continue;

        var name = element.name;
        while ( index = name.search( fieldFormatRegexp ) + 1 )
        {
            if (! testField(element, RegExp.$1, null, allow_empty))
                return false;
            name = name.substr( index );
        }
    }

    if (validate_mandatory)
         return validateMandatory( form ); 


    return true;
}

//
// Validate mandatory data of the givin form
// TODO remove this, always validate mandatory data in testField function
//
function validateMandatory( form )
{
    for ( var i = 0; i < form.elements.length; i++ )
    {
        with ( form.elements[i] )
            if (name && getAttribute('mandatory') && type!='checkbox' && !value)
            {
                 alert( messageCatalog.mandatory_attribute + ' "' + title + '".');
                 if ( type != 'hidden') 
                     focus();
                 return false;
            }
    }

    return true; //disableForm( form );
}


//
//  Sets focus to the first visible element of form
//
function focusForm(form) {
    var element;
    for (var i=0; i<form.elements.length; i++) {
        element = form.elements[i];
        if (element.type != 'hidden') {
            try {
              element.focus();
            } catch (error) {
                // pass
            }
            finally {
              break;
            }
        }
    }
}


//
//  Selects users in textarea - quick search
// Arguments:
//
//  'str', ----    TODO
//  'select', -----    TODO
//  'sortFunction', if Given select sorted by this function
//  'matchRegExp', if Given full text of the option filtered by this regexp
//
function SearchStrInSelect(str, select, sortFunction, matchRegExp )
{
    if (!select.length)
        return;

    var strn=0, strl=0;

    var inpStr = str.toUpperCase();

    if (sortFunction)
        sortList( select, sortFunction );

    for (var i = 0; i < select.length; i++)
    {
        select.options[i].selected = false;
        var curl = 0;

        var selStr = select.options[i].text.toUpperCase();
        if ( matchRegExp )
            selStr = matchRegExp.match( selStr );

        if ( !selStr )
            continue;

        for ( var l = 0; l < str.length+1; l++ )
        {
            curl=l;
            if (inpStr.charAt(l)!=selStr.charAt(l))
                break;
        }

        if ( curl>strl )
        {
            strl=curl;
            strn=i;
        }
    }

    if (!select.multiple || str.length)
        select.options[strn].selected=true;
}

//
// Adds a new option to the list
//
function addOptionTo( list, text, value, ignore_existent )
{
    var len = list.length;
    var opt;


    //Check if this value already exist in the dest_list or not
    //if not then add it otherwise do not add it.
    var found = false;

    if (!ignore_existent)
        for( var count = 0; count < len; count++ )
            if ( list.options[count] != null )
                if ( value == list.options[count].value)
                    return;

    if (userAgent.IE)
        opt = list.document.createElement("OPTION");
    else
        opt = new Option();

    opt = list.options[len] = opt;
    opt.text  = text;
    opt.value = value;

    len++;

    return opt;
}

//
// default sort function, sorted options of the select by compare text values.
//
function sortByText( object1, object2 )
{
   var value1 = object1.text.toLowerCase();
   var value2 = object2.text.toLowerCase();
   
   return value1 > value2 ? 1 : (value1 < value2 ? -1 : 0);
}

//
// Sortes select by given sort function.
// Caches select name with function name, and not sort select with cached name by cached function.
//
function sortList( list, sortFunction )
{
    sortFuncName = sortFunction ? sortFunction.getName() : typeof(sortFunction);

    name = list.form.name + list.name;
    isSorted = window[ name ] == sortFuncName;

    //alert( [ sortFuncName, name, isSorted.toString() ].join('/') );

    if ( !isSorted )
    {

        var len = list.length;
        var array = toArray( list );
        array.sort( sortFunction || null );

        clearList( list );
        for ( var i = 0; i < len; i++ )
            with( array[i] )
                addOptionTo( list, text, value );

        window[ name ] = sortFuncName;
    }
}


//
// Add the selected items from the source to destination list
//
function addSelectionToList(src_list, dest_list)
{
    var len = dest_list.length;
    for(var i = 0; i < src_list.length; i++) 
       if ((src_list.options[i] != null) && (src_list.options[i].selected))
           addOptionTo( dest_list, src_list.options[i].text, src_list.options[i].value );
}

//
// Deletes from the destination list
//
function deleteSelectionFromList(select)
{
    select = getElement(select)

    while (select.selectedIndex != -1)
        if (userAgent.IE)
            select.options.remove(select.selectedIndex)
        else
            select.options[select.selectedIndex] = null;
}

//
// Clear list contents
//
function clearList(select)
{
    while (select.options.length)
        select.options.remove(0)
}

//
// Adds options to select by given range.
// Arguments:
//   'list', select object
//
// Additional arguments pass as the python range function.
//
function addOptionsRange( list )
{
    var l = arguments.length,
        start, end, step;

    start = l > 2 ? arguments[1]: 0;
    end = arguments[2] || arguments[1];
    step = arguments[3] || 1;

    for( var i = start; i<end; i = i+step )
        addOptionTo( list, i, i, 1 );
}

function upSelectionInList( list )
{
    list = getElement( list );
    var len = list.options.length;

    if ( len && list.options[0].selected != true ) {
        for( var i = 1; i < len; i++ ) {
            if ( (list.options[i] != null) && (list.options[i].selected == true) ) {
                text = list.options[i - 1].text;
                value = list.options[i - 1].value;

                list.options[i - 1].text = list.options[i].text;
                list.options[i - 1].value = list.options[i].value;

                list.options[i].text = text;
                list.options[i].value = value;

                list.options[i - 1].selected = true;
                list.options[i].selected = false;
            }
        }
    }
}

function downSelectionInList( list )
{
    list = getElement( list );
    var len = list.options.length;

    if ( len && list.options[len - 1].selected != true ) {
        for(var i = len; i >= 0; i--) {
            if ((list.options[i] != null) && (list.options[i].selected == true)) {
                text = list.options[i + 1].text;
                value = list.options[i + 1].value;

                list.options[i + 1].text = list.options[i].text;
                list.options[i + 1].value = list.options[i].value;

                list.options[i].text = text;
                list.options[i].value = value;

                list.options[i].selected = false;
                list.options[i + 1].selected = true;
            }
        }
    }
}


//
// Returns the checked option of the radio buttons set
//
function getCheckedRadioButton(radio)
{
    if ( !radio )
        return;

    if ( !radio.length )
        radio = [radio];

    for ( var i = 0; i < radio.length; i++ )
        if ( radio[i].checked )
            return radio[i];
}

//
// reset radio buttons set
//
function resetRadioButton(radio)
{
   if ( !radio )
       return;

   if ( !radio.length )
       radio = [radio];

   for (var i = 0; i < radio.length; i++)
       radio[i].checked = false;
}
//
// Check whether any checkbox is checked
//
function checkEmptiesCheckboxes( form, elementName, message )
{
    var elements = form.elements;
    for ( var i = 0; i < elements.length; i++ )
        with( elements[i] )
            if ( type=='checkbox' && name.indexOf( elementName )==0 && checked )
                 return true;

    if ( message )
        alert( messageCatalog[ message ] || message );

    return false;
}

//
// Select all items of the list
//
function selectAll(list)
{
    if ( !list )
        return;

    for(var i = 0; i < list.options.length; i++)
        list.options[i].selected = true;

    return true;
}

//
// Select additional arguments in the given list.
//
function selectValues(list)
{
    if ( !list )
        return;

    for (var i = 1; i < arguments.length; i++)
       for(var j = 0; j < list.options.length; j++)
           with ( list.options[j] )
               if ( value == arguments[i] )
                   selected = true;
}

//
// Select/Deselect(change checked property) all check buttons set,
// toggle is a button which value need change depending on checked property of the list
//
function toggleSelect(list, toggle)
{
    if ( !list )
        return;

    if ( !list.length )
        list = [list];

    var name = list[0].form.name + 'isSelected';
    var isSelected = window[ name ] = !window[ name ];

    for ( var i = 0; i < list.length; i++ )
        list[i].checked = isSelected;

    if (toggle)
        toggle.value = isSelected ? messageCatalog.deselect_all
                                  : messageCatalog.select_all;

    return isSelected;
}

function toggleDiv( div, state ) {
  div.style.display = state ? '' : 'none';
}

//
// Copies input fields from source to target form.
//
// Arguments:
//
//     'source' -- source form object
//     'target' -- target form object
//     'from'   -- optional field index in the source form
//     'to'     -- optional field index in the target form
//
// If 'from' index is given, fields preceding it are skipped.
// If 'to' index is given, only field values are copied, otherwise
// new elements are created and appended to the target form.
// Newly created elements have 'none' display style.
//
function copyFormItems( source, target, from, to )
{
    var cname  = '__copy__' + source.name;
    var tdoc   = getDocument( target );
    var create = false;

    from = from || 0;
    if (to == null) {
        create = target[cname] == null;
        to = create ? target.length : target[cname];
    }

    for (var i = 0; i < source.elements.length - from; i++) {
        var se = source.elements[ from+i ];
        var te = target.elements[ to+i ];

        if (te == null) {
            if (! create)
                continue;

            var tag = se.tagName;
            if (userAgent.brokenSetMultiple && se.type == 'select-multiple')
                tag = '<select multiple>';

            te = tdoc.createElement( tag );
            te.name = se.name;

            if (te.multiple != se.multiple)
                te.multiple  = se.multiple;
            if (te.type != se.type)
                te.type  = se.type;

            te.style.display = 'none';
            target.appendChild( te );
        }

        copyFieldValue( se, te );
    }

    if (create)
        target[cname] = to;
}

//
// Copies value of one input field to another.
//
function copyFieldValue( source, target )
{
    if (source.type != target.type)
        return;

    switch (source.type) {
        case 'checkbox':
        case 'radio':
            target.value = source.value;
            target.checked = source.checked;
            break;

        case 'select-one':
        case 'select-multiple':
            copySelectOptions( source, target, true );
            break;

        default:
            target.value = source.value;
    }
}

//
// Copies all options from one select control to another.
//
function copySelectOptions( source, target, state )
{
    var tdoc  = getDocument( target );
    var topts = target.options;

    while (topts.length)
        topts[0] = null;

    for (var i = 0; i < source.options.length; i++) {
        var so = source.options[i];
        var to = tdoc.createElement('option');

        to.text  = so.text;
        to.value = so.value;

        topts[ topts.length ] = to;
        if (state)
            to.selected = so.selected;
    }
}

//
// Copies shylesheet element to another document.
//
// Result:
//
//     New STYLE element.
//
function copyStyleSheet( style, target )
{
    var copy = target.createElement('style');
    target.body.appendChild( copy );

    if (userAgent.IE) { // Microsoft
        var rules = style.styleSheet.rules;
        var sheet = copy.styleSheet;
        for (var i = 0; i < rules.length; i++)
            sheet.addRule( rules[i].selectorText, rules[i].style.cssText );

    } else { // W3C DOM
        var rules = style.sheet.cssRules;
        var sheet = copy.sheet;
        for (var i = 0; i < rules.length; i++)
            sheet.insertRule( rules[i].cssText, sheet.cssRules.length );
    }

    return copy;
}

//
// Appends rows and cells from one HTML table to another.
//
// Result:
//
//     Number of rows copied.
//
function appendTableRows( source, target, from, to )
{
    var i;
    from = from || 0;
    to = to || target.rows.length;

    for (i = 0; i < source.rows.length - from; i++) {
        var srow = source.rows[ from+i ];
        var drow = target.insertRow( to+i );
        for (var j = 0; j < srow.cells.length; j++)
            drow.insertCell(-1).innerHTML = srow.cells[j].innerHTML;
    }

    return i;
}

//
// Deletes rows from an HTML table.
//
// Result:
//
//     Number of rows copied.
//
function deleteTableRows( target, index, count )
{
    if (! count)
        return;
    for (var i = 0; i < count; i++)
        target.deleteRow( index );
}

//
// Enable/disable control
//
function setControlState(form, element_id, state)
{
    form[element_id].disabled = !state;
}

//
// Returns an element given it's id.
//
function getElement( element )
{
    if( typeof( element ) == 'string' )
        return document.getElementById( element );
    return element
}

//
// Handle mass show/hide operations.
//
function displayElements( show, hide )
{
    if( hide )
        for( i = 0; i < hide.length; i++ )
            getElement( hide[ i ] ).style.display = 'none';

    if( show )
        for( i = 0; i < show.length; i++ ) {
            var element = getElement( show[ i ] );
            element.style.display = '';
            if (userAgent.MZ) {
                // workaround of Mozilla bug
                var selects = element.getElementsByTagName('SELECT');
                for (var j = selects.length; j-- > 0;)
                    selects[j].style.visibility = 'visible';
            }
        }
}

//
// Opens an URL in a workspace window
//
function openUrl( url, target )
{
    if (! url)
        return;
    parent[target].location.href = url;
}

//
// Shows hint window for pattern input
//
function showHint(fmt)
{
    registerWindow( 'pattern_help_form'
                  , 'pattern_help_form?fmt='+fmt
                  , 'toolbar=no, scrollbars=yes, width = 400, height = 250, resizable=yes'
                  );
}

//
// Tests whether the given character is alphanumeric.
//
function isAlnum( ch )
{
    return wordCharRegexp.test(ch) || ch.charCodeAt(0) > 127;
}

//
// Converts array-like object to array.
//
function toArray(array_like, start, length)
{
    start = start || 0;

    var array = [], end;

    if (length == null || (end = start + length) > array_like.length)
        end = array_like.length;

    for (var i = start; i < end; i++)
        array[array.length] = array_like[i];

    return array;
}

//
// Returns array index of given value or null if it doesn't exist.
//
function arrayIndex(array, value)
{
    for (var i = 0; i < array.length; i++)
        if (array[i] == value) return i
}

//
// Inserts class_name into element css classes value if it doesn't included there.
//
function addClass(element, class_name)
{
    var classes = element.className.split(/\s+/g)

    if ( arrayIndex(classes, class_name) != null ) return

    classes = [class_name].concat(classes)
    element.className = classes.join(' ')
}

//
// Removes class_name from element css classes value if it included there.
//
function removeClass(element, class_name)
{
    var classes = element.className.split(/\s+/g),
        i = arrayIndex(classes, class_name)

    if (i == null) return

    classes = [].concat(classes.slice(0, i), classes.slice(i + 1))
    element.className = classes.join(' ')
}

//
// Finds all matches of search string in pointed window content.
//
function findOnPage( parent_window, str, search_scope, search_flags ) {

  if (str == "") 
    return false;

  if (parent_window.document.all) {
    var txt = parent_window.document.body.createTextRange();
    if (search_numtimes>0 && search_range) 
      txt = search_range;
    var found = txt.findText(str, search_scope, search_flags);
    var text_len = txt.text.length;

    if (found) {
      txt.select();
      if (search_scope > 0) {
        txt.moveStart("character", text_len);
        txt.moveEnd("textedit");
      } else {
        txt.moveStart("textedit", -1);
        txt.moveEnd("character", -1*text_len);
      }
      search_range = txt;
      search_numtimes++;
    } else {
      if (search_numtimes>0) {
        search_numtimes = 0;
        findOnPage( parent_window, str, search_scope, search_flags );
      } else
        alert( messageCatalog[ 'not_found' ] || 'Searched word was not found on this page' );
    }
  }
}

//
// Opens modal dialog.
//
function openModal( url, title, width, height ) {
  var oDialogInfo = new Object();
  oDialogInfo.Title = title;
  oDialogInfo.Page = url;
  oDialogInfo.Editor = window;
	
  window.showModalDialog( url, oDialogInfo, "dialogWidth:" + width + "px;dialogHeight:" + height + "px;help:no;scroll:no;status:no");
}

//
// Adds hidden field to *container*
//
function addHidden(container, name, value)
{
    var input = getDocument(container).createElement(
            // IE doesn't understand dynamic name setting
            userAgent.IE ? '<input name="' + name + '">' : 'INPUT'
        )

    input.type = 'hidden'
    input.name = name
    input.value = value

    container.appendChild(input)
}

//
// Removes hidden field from *form*
//
function deleteHidden(form, name, value)
{
    var inputs = form.elements[name]

    if (! inputs.length)
        inputs = [inputs]

    for (var i = 0; i < inputs.length; i++) {
        var input = inputs[i]
        if (input.value == value) {
            input.parentNode.removeChild(input)
            break
        }
    }
}

//
// Filters select values using *input* value.
//
// Container of *input* should contain only one select which would be filtered.
//
function filterSelect(input)
{
    var value = input.value.toLowerCase(),
        select = input.parentNode.getElementsByTagName('select')[0],
        options = select.getAttribute('_all_options')

    if (! options) {
        options = toArray(select.options)
        select.setAttribute('_all_options', options)
    }

    // removing all options
    clearList(select)

    // showing only options which text contains filter *value*
    for (var i = 0; i < options.length; i++) {
        var option = options[i]
        if (option.text.toLowerCase().indexOf(value) != -1) {
            option.selected = false
            select.options.add(option)
        }
    }
}


///////////////////////////////////////////////////////////////////////////

var escapeHTMLMap = { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' };

var wordCharRegexp = new RegExp( '\\w' );
var emptyValueRegexp = new RegExp( '^\\s*$' );
var fieldFormatRegexp = new RegExp( ':(string|int|long|float|currency|required|search|date|datetime|id|idstrong)_?\\b' );
var fieldRequiredRegexp = new RegExp( ':required_?\\b' );
var userPositionRegexp = new RegExp( '\\[(.*)\\]' );


var validationRegexp = {
'int'      : new RegExp( '^-?\\d+$' ),
'long'     : new RegExp( '^-?\\d+[Ll]?$' ),
'float'    : new RegExp( '^-?\\d+[.,]?\\d*$' ),
'currency' : new RegExp( '^-?\\d+[.,]?\\d{0,2}$' ),
'datetime' : new RegExp( '^(\\d{1,2})[-./](\\d{1,2})[-./](\\d{4})(\\s+(\\d{1,2}):(\\d{1,2}))?\\s*$' ),
'email'    : new RegExp( '^[a-z0-9_.-]+@[a-z0-9_.-]+\\.[a-z0-9_]+$', 'i' ),
'id'       : new RegExp( '^[a-z0-9_.$()~, -]+$', 'i' ),
'idstrong' : new RegExp( '^[a-z][a-z0-9_]*$', 'i' ),
'required' : new RegExp( '\\S' ), // this not needed now
'search'   : new RegExp( '^[\\s()]*((%[^%*?()\\s"]+|\\*?[^%*?()\\s"]+\\*?)($|[\\s()]+))+$' ) // TextIndexNG search pattern
};
validationRegexp['date'] = validationRegexp['datetime'];

var validationMessages = {
'string'   : 'enter_string',
'int'      : 'enter_integer',
'long'     : 'enter_long',
'float'    : 'enter_float',
'currency' : 'enter_currency',
'date'     : 'invalid_date',
'datetime' : 'invalid_date',
'email'    : 'invalid_email',
'id'       : 'invalid_id',
'idstrong' : 'invalid_id',
'required' : 'required_input',
'search'   : 'invalid_pattern'
};

var userAgent = new UserAgent();
var cookies = new CookieManager();
var windowManager = new Mapping();
var preloadArray = new Array();
var messageCatalog = new Mapping();
var fieldEditHandler = new Mapping();
var portalImagesURL = portalRootURL;

var search_numtimes = 0;
var search_range = null;

// create frameset unless it already exists
if (checkFrameSet()) {

    // change to another location if redirect was requested
    if (window.redirectURL)
        window.location.replace( window.redirectURL );

    // set top level window title to current page title
    if (window.name == 'workspace' && window != top) {
        var error;
        try {
            top.document.title = document.title;
        } catch (error) {
            // ignore
        }
    }

    // preload page common images
    if (window.commonImages)
        preloadImages( window.commonImages );

} else if (! window.redirectURL) {
    window.updateSections = null;
}

// refresh navigation frame sections
if (window.updateSections) {
    var sections = window.updateSections.split(' ');
    for (var i in sections)
        updateNavFrame( sections[i] );
}
