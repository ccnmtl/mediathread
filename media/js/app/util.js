/* global escape: true, MediaThread: true, unescape: true */
/* exported _propertyCount, getVisibleContentHeight */
/* exported switcher, toggleHelp, toggleHelpOverlay, storeData */
/* exported retrieveData, showMessage, confirmAction */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

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
    var viewportheight;

    // the more standards compliant browsers (mozilla/netscape/opera/IE7
    // use window.innerWidth and window.innerHeight
    if (typeof window.innerWidth !== 'undefined') {
        viewportheight = window.innerHeight;
    } else if (typeof document.documentElement !== 'undefined' &&
        typeof document.documentElement.clientWidth !== 'undefined' &&
            document.documentElement.clientWidth !== 0) {
        // IE6 in standards compliant mode (i.e. with a valid doctype
        // as the first line in the document)
        viewportheight = document.documentElement.clientHeight;
    } else {
        // older versions of IE
        viewportheight = document.getElementsByTagName('body')[0].clientHeight;
    }

    return viewportheight -
        (20 + document.getElementById('header').clientHeight);
}

function switcher(event, a) {
    event.preventDefault();
    event.stopPropagation();
    var $a = jQuery(a);
    if ($a.parent().hasClass('disabled')) {
        return false;
    }
    if ($a.hasClass('menuclosed')) {
        // we're going to open. make sure everyone else is CLOSED
        jQuery('.menuopen').toggleClass('menuopen menuclosed');
        jQuery('.switcher-options').hide();
    }
    $a.toggleClass('menuclosed menuopen');
    $a.parent().children('.switcher-options').toggle();
    return false;
}

function updateUserSetting(user, setting, value) {
    jQuery.post('/setting/' + user + '/', {name: setting, value: value});
}

function toggleHelp(a, user, parent, helpContentId, callback) {
    jQuery(parent).toggleClass('on off');
    jQuery('#' + helpContentId).toggleClass('on off');
    jQuery(a).toggleClass('open');

    var userSetting = jQuery(parent).hasClass('on') ? 'True' : 'False';

    jQuery.post('/setting/' + user + '/',
        {name: helpContentId, value: userSetting});

    if (callback) {
        callback();
    }
}

function toggleHelpOverlay(btn, user, helpContentId) {
    var overlayId = '#' + helpContentId + '-overlay';
    var tabId = '#' + helpContentId + '-tab';
    var contentId = '#' + helpContentId + '-content';
    if (jQuery(overlayId).is(':visible')) {
        jQuery(overlayId).hide();
        jQuery(tabId).hide();
        jQuery(contentId).hide();
    } else {
        jQuery(overlayId).show();
        jQuery(tabId).show();
        jQuery(contentId).show();
    }
    var checkedId = '#' + helpContentId + '_checkbox';
    var elts = jQuery(checkedId);
    if (elts.length) {
        var checked = jQuery(elts[0]).is(':checked');
        updateUserSetting(MediaThread.current_username,
                          helpContentId, !checked);
    }
    return false;
}

function getCookie(name) {
    var dc = document.cookie;
    var prefix = name + '=';
    var begin = dc.indexOf('; ' + prefix);
    if (begin === -1) {
        begin = dc.indexOf(prefix);
        if (begin !== 0) {
            return null;
        }
    } else {
        begin += 2;
    }
    var end = document.cookie.indexOf(';', begin);
    if (end === -1) {
        end = dc.length;
    }
    return unescape(dc.substring(begin + prefix.length, end));
}

function setCookie(name, value, expires, path, domain, secure) {
    document.cookie = name + '=' + escape(value) +
        ((expires) ? '; expires=' + expires.toGMTString() : '') +
        ((path) ? '; path=' + path : '') +
        ((domain) ? '; domain=' + domain : '') +
        ((secure) ? '; secure' : '');
}

/* eslint-disable  scanjs-rules/property_localStorage */
/* eslint-disable scanjs-rules/identifier_localStorage */

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

/* eslint-enable scanjs-rules/property_localStorage */
/* eslint-enable scanjs-rules/identifier_localStorage */

function showMessage(msg, onclose, customTitle, position) {
    var title = customTitle ? customTitle : 'Success';
    var $dialogConfirm = jQuery('#dialog-confirm');
    $dialogConfirm.html(msg);
    $dialogConfirm.dialog({
        resizable: false,
        modal: true,
        title: title,
        close: function(evt, ui) {
            if (onclose) {
                onclose(evt, ui);
                $dialogConfirm.html('');
            }
        },
        buttons: {
            'OK': function(e) {
                e.preventDefault();
                e.stopPropagation();
                jQuery(this).dialog('close');
            }
        }
    });
    // position newly opened dialog (using its parent container) below $div.
    if (position) {
        $dialogConfirm.dialog('widget').position(position);
    }
}

function confirmAction(msg, onOK, customTitle, position) {
    var title = customTitle ? customTitle : 'Confirm Action';
    var $dialogConfirm = jQuery('#dialog-confirm');
    $dialogConfirm.html(msg);
    $dialogConfirm.dialog({
        resizable: false,
        modal: true,
        title: title,
        close: function(evt, ui) {
            $dialogConfirm.html('');
        },
        buttons: {
            'Cancel': function() {
                jQuery(this).dialog('close');
            },
            'OK': function() {
                onOK();
                jQuery(this).dialog('close');
            }
        }
    });
    // position newly opened dialog (using its parent container) below $div.
    if (position) {
        $dialogConfirm.dialog('widget').position(position);
    }
}
