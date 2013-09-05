function _propertyCount(obj) {
    var count = 0;
    for (var k in obj) {
        if (obj.hasOwnProperty(k)) {
            count++;
        }
    }
    return count;
}


function getVisibleContentHeight() {
    var viewportwidth;
    var viewportheight;

    // the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight
    if (typeof window.innerWidth !== 'undefined') {
        viewportwidth = window.innerWidth;
        viewportheight = window.innerHeight;
    } else if (typeof document.documentElement !== 'undefined' &&
        typeof document.documentElement.clientWidth !== 'undefined' &&
            document.documentElement.clientWidth !== 0) {
        // IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)
        viewportwidth = document.documentElement.clientWidth;
        viewportheight = document.documentElement.clientHeight;
    } else {
        // older versions of IE
        viewportwidth = document.getElementsByTagName('body')[0].clientWidth;
        viewportheight = document.getElementsByTagName('body')[0].clientHeight;
    }

    return viewportheight - (20 + document.getElementById("header").clientHeight);
}

function switcher(event, a) {
    event.preventDefault();
    event.stopPropagation();
    if (jQuery(a).hasClass("menuclosed")) {
        // we're going to open. make sure everyone else is CLOSED
        jQuery(".menuopen").toggleClass("menuopen menuclosed");
        jQuery(".switcher-options").hide();
    }
    jQuery(a).toggleClass('menuclosed menuopen');
    jQuery(a).parent().children('.switcher-options').toggle();
    return false;
}

function updateHelpSetting(user, help_content_id, value) {
    jQuery.post('/yourspace/' + user + '/setting/', { name: help_content_id, value: value });
}

function toggleHelp(a, user, parent, help_content_id, callback) {
    jQuery(parent).toggleClass('on off');
    jQuery("#" + help_content_id).toggleClass('on off');
    jQuery(a).toggleClass('open');

    var user_setting = jQuery(parent).hasClass('on') ? 'True' : 'False';

    jQuery.post('/yourspace/' + user + '/setting/', { name: help_content_id, value: user_setting });

    if (callback) {
        callback();
    }
}

function toggleHelpOverlay(btn, user, help_content_id) {
    
    var overlay_id = "#" + help_content_id + "-overlay";
    var tab_id = "#" + help_content_id + "-tab";
    var content_id = "#" + help_content_id + "-content";
    
    if (jQuery(overlay_id).is(":visible")) {
        jQuery(overlay_id).hide();
        jQuery(tab_id).hide();
        jQuery(content_id).hide();
    } else {
        jQuery(overlay_id).show();
        jQuery(tab_id).show();
        jQuery(content_id).show();
    }
    
    var checked_id = "#" + help_content_id + "_checkbox";
    var elts = jQuery(checked_id);
    if (elts.length) {
        var checked = jQuery(elts[0]).is(":checked");
        updateHelpSetting(MediaThread.current_username, help_content_id, !checked);
    }
    
    return false;
}

function getCookie(name) {
    var dc = document.cookie;
    var prefix = name + "=";
    var begin = dc.indexOf("; " + prefix);
    if (begin === -1) {
        begin = dc.indexOf(prefix);
        if (begin !== 0) {
            return null;
        }
    } else {
        begin += 2;
    }
    var end = document.cookie.indexOf(";", begin);
    if (end === -1) {
        end = dc.length;
    }
    return unescape(dc.substring(begin + prefix.length, end));
}

function setCookie(name, value, expires, path, domain, secure) {
    document.cookie = name + "=" + escape(value) +
        ((expires) ? "; expires=" + expires.toGMTString() : "") +
        ((path) ? "; path=" + path : "") +
        ((domain) ? "; domain=" + domain : "") +
        ((secure) ? "; secure" : "");
}

function storeData(name, value, expires, path, domain, secure) {
    if (window.localStorage) {
        localStorage[name] = value;
    } else {
        setCookie(name, value, expires, path, domain, secure);
    }
}

function retrieveData(name) {
    if (window.localStorage) {
        return localStorage.getItem(name);
    } else {
        return getCookie(name);
    }
}

function showMessage(msg, onclose, customTitle, position) {
    var title = customTitle ? customTitle : "Success";
    jQuery("#dialog-confirm").html(msg);
    jQuery("#dialog-confirm").dialog({
        resizable: false,
        modal: true,
        title: title,
        close: function() {
            if (onclose) {
                onclose();
                jQuery("#dialog-confirm").html("");
            }            
        },
        buttons: {
            "OK": function() {
                jQuery(this).dialog("close");
            }
        } 
    });
    
    // position newly opened dialog (using its parent container) below $div.
    if (position) {
        jQuery("#dialog-confirm").dialog('widget').position(position);
    }
}