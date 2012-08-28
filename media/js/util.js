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

    return viewportheight - (10 + document.getElementById("primarynav").clientHeight + document.getElementById("header").clientHeight);
}

function switcher(a) {
    if (jQuery(a).hasClass("menuclosed")) {
        // we're going to open. make sure everyone else is CLOSED
        jQuery(".menuopen").toggleClass("menuopen menuclosed");
        jQuery("ul.switcher-options").hide();
    }
    jQuery(a).toggleClass('menuclosed menuopen');
    jQuery(a).parent().children('ul.switcher-options').toggle();
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