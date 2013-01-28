var hs_controls = [];

function cookie_name(el) {
    var name = "hsstate_";
    //across pages
    if (/^global-/.test(el.id)) {
        name += "#" + el.id;
    } else {
        name +=  document.location + "#" + el.id;
    }
    return name.replace(/\W/g, "_");
}

function futureDate() {
    var d = new Date();
    d.setTime(Date.parse('October, 4 2030 07:04:11'));
    return d;
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

function saveStateCookie(el, value, d) {
    setCookie(cookie_name(el), value, d);
}

function hs_DataStore(name, value, expires, path, domain, secure) {
    if (window.localStorage) {
        localStorage[name] = value;
    } else {
        setCookie(name, value, expires, path, domain, secure);
    }
}

function hs_DataRetrieve(name) {
    if (window.localStorage) {
        return localStorage.getItem(name);
    } else {
        return getCookie(name);
    }
}

function hs_getTarget(a) {
    var elt = jQuery(a.href.substr(a.href.indexOf('#')));
    if (elt.length) {
        return elt.get(0);
    } else {
        throw new Error('hs.js: target id: ' + a.href + ' not found');
    }
}

function hs_hide(e) {
    e = (typeof e === 'number' ? this : e);

    jQuery(e)
    .removeClass("hs-show")
    .addClass("hs-hide");

    jQuery(hs_controls[e.id])
    .removeClass("hs-control-show")
    .addClass("hs-control-hide");

    if (typeof window['hs_onhide_' + e.id] === 'function') {
        window['hs_onhide_' + e.id](e);
    }
}

function hs_show(e) {
    jQuery(e)
    .removeClass("hs-hide")
    .addClass("hs-show");

    jQuery(hs_controls[e.id])
    .removeClass("hs-control-hide")
    .addClass("hs-control-show");

    if (typeof window['hs_onshow_' + e.id] === 'function') {
        window['hs_onshow_' + e.id](e);
    }
}


function hs_toggle() {
    var target = hs_getTarget(this);
    if (jQuery(target).hasClass("hs-hide")) {
        hs_show(target);
        hs_DataStore(cookie_name(target), "show", futureDate());
    } else {
        hs_hide(target);
        hs_DataStore(cookie_name(target), "hidden", futureDate());
    }
    return false;
}

function hs_addControlCallback() {
    //log("adding callback to " + a);
    jQuery(this)
    .click(hs_toggle)
    .addClass('hs-control-show');
    hs_controls[hs_getTarget(this).id] = this;
}


function hs_lookForCookie() {
    var e = hs_getTarget(this);
    var s = hs_DataRetrieve(cookie_name(e));
    if (s === "hidden") {
        hs_hide(e);
    }
    if (s === "show") {
        hs_show(e);
    }
}

function hs_init(parent) {
    parent = ((parent && parent.tagName) ? parent : document);
    jQuery('a.hs-control', parent).each(hs_addControlCallback);
    jQuery('.hs-init-hide', parent).each(hs_hide);
    jQuery('a.hs-control', parent).each(hs_lookForCookie);
}

jQuery(hs_init);
