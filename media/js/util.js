function getVisibleContentHeight() {
    var viewportwidth;
    var viewportheight;
    
    // the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight
    if (typeof window.innerWidth != 'undefined') {
         viewportwidth = window.innerWidth,
         viewportheight = window.innerHeight
    } else if (typeof document.documentElement != 'undefined'
        && typeof document.documentElement.clientWidth !=
        'undefined' && document.documentElement.clientWidth != 0) {
        // IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)
        viewportwidth = document.documentElement.clientWidth,
        viewportheight = document.documentElement.clientHeight
    } else {
        // older versions of IE
        viewportwidth = document.getElementsByTagName('body')[0].clientWidth,
        viewportheight = document.getElementsByTagName('body')[0].clientHeight
    }
    
    return viewportheight - (10 + document.getElementById("primarynav").clientHeight + document.getElementById("header").clientHeight); 
}

function switcher(a) {
    if (jQuery(a).hasClass("closed")) {
        // we're going to open. make sure everyone else is CLOSED
        jQuery(".open").toggleClass("open closed");
        jQuery("ul.switcher-options").hide();
    }
    jQuery(a).toggleClass('closed open');
    jQuery(a).parent().children('ul.switcher-options').toggle();
}

function toggleHelp(a, user, parent, help_content_id) {
    console.log(a);
    console.log(user);
    console.log(parent);
    console.log(help_content_id);
    
    jQuery(parent).toggleClass('on off');
    jQuery("#" + help_content_id).toggleClass('on off');
    
    var user_setting = jQuery(parent).hasClass('on') ? 'True' : 'False';
        
    jQuery.post('/yourspace/' + user + '/setting/', { name: help_content_id, value: user_setting });
}