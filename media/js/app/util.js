/* global MediaThread: true */
/* exported _propertyCount, getVisibleContentHeight */
/* exported switcher, toggleHelp, toggleHelpOverlay, storeData */
/* exported retrieveData, showMessage, urlWithCourse */
/* exported isElementInViewport */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

// eslint-disable-next-line no-unused-vars
function _propertyCount(obj) {
    var count = 0;
    for (var k in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, k)) {
            count++;
        }
    }
    return count;
}

// eslint-disable-next-line no-unused-vars
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

    var elt = document.getElementById('header');
    if (!elt) {
        elt = document.getElementById('three-section-tabs');
    }
    return viewportheight - (20 + elt.clientHeight);
}


/*
 * https://stackoverflow.com/questions/123999/how-can-i-tell-if-a-
 * dom-element-is-visible-in-the-current-viewport/7557433#7557433
 */
//eslint-disable-next-line no-unused-vars
function isElementInViewport(el) {
    var rect = el.getBoundingClientRect();
    var inView =
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (
            window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (
            window.innerWidth || document.documentElement.clientWidth);
    return inView;
}

// eslint-disable-next-line no-unused-vars
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

// eslint-disable-next-line no-unused-vars
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

// eslint-disable-next-line no-unused-vars
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

// eslint-disable-next-line no-unused-vars
function storeData(name, value, expires, path, domain, secure) {
    if (window.localStorage) {
        localStorage[name] = value;
    } else {
        setCookie(name, value, expires, path, domain, secure);
    }
}

// eslint-disable-next-line no-unused-vars
function retrieveData(name) {
    if (window.localStorage) {
        return localStorage.getItem(name);
    } else {
        return getCookie(name);
    }
}

// eslint-disable-next-line no-unused-vars
function showMessage(msg, onclose, customTitle, position) {
    const title = customTitle ? customTitle : 'Success';

    let buttons = {
        'OK': function(evt, ui) {
            evt.preventDefault();
            evt.stopPropagation();
            jQuery(this).dialog('close');
            if (onclose) {
                onclose(evt, ui);
            }
        }
    };

    // If this is an error dialog, we don't need both OK and Cancel
    // buttons.
    if (customTitle !== 'Error') {
        buttons['Cancel'] = function() {
            jQuery(this).dialog('close');
        };
    }

    const $dialogConfirm = jQuery('#dialog-confirm');

    $dialogConfirm.html(msg);
    $dialogConfirm.dialog({
        resizable: false,
        modal: true,
        title: title,
        buttons: buttons
    });
    // position newly opened dialog (using its parent container) below $div.
    if (position) {
        $dialogConfirm.dialog('widget').position(position);
    }
}

/**
 * Append course ID as a GET param to the url, if necessary.
 */
// eslint-disable-next-line no-unused-vars
function urlWithCourse(url, courseId) {
    if (!courseId) {
        courseId = MediaThread.current_course;
    }

    if (courseId && !url.match(/(\?|&)course=\d+/)) {
        if (url.match(/\?\w+=/)) {
            return url + '&course=' + courseId;
        } else {
            return url + '?course=' + courseId;
        }
    }

    return url;
}
