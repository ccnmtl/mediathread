
var hs_controls = new Array();

function cookie_name(el) {
    name =  "hsstate_" + document.location + "#" + el.id;
    return name.replace(/\W/g,"_");
}

function saveStateCookie(el,value,d) {
	setCookie(cookie_name(el), value, d);
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
    	if (begin == -1) {
        	begin = dc.indexOf(prefix);
        	if (begin != 0) return null;
    	} else {
        	begin += 2;
    	}
    	var end = document.cookie.indexOf(";", begin);
    	if (end == -1) {
        	end = dc.length;
    	}
    	return unescape(dc.substring(begin + prefix.length, end));
}

function setCookie(name, value, expires, path, domain, secure) {   
    	document.cookie= name + "=" + escape(value) +
        	((expires) ? "; expires=" + expires.toGMTString() : "") +
        	((path) ? "; path=" + path : "") +
        	((domain) ? "; domain=" + domain : "") +
        	((secure) ? "; secure" : "");
}


function hs_addControlCallback(a) {
	log("adding callback to " + a);
	a.onclick = hs_toggle;
	hs_controls[hs_getTarget(a).id] = a;
	addElementClass(a,"hs-control-show");
}

function hs_lookForCookie(a) {
   var e = hs_getTarget(a);
   var s = getCookie(cookie_name(e));
   if (s == "hidden") {
      hs_hide(e);
   } 
   if (s == "show") {
      hs_show(e);
   }
}

function hs_getTarget(a) {
	return $(a.href.split("#")[1]);
}

function hs_toggle() {
	var target = hs_getTarget(this);
	if (hasElementClass(target,"hs-hide")) {
	   hs_show(target);
	   setCookie(cookie_name(target),"show",futureDate());
        } else {
	   hs_hide(target);
	   setCookie(cookie_name(target),"hidden",futureDate());
	}
	return false;
}

function hs_hide(e) {
	log("hiding " + e);
	removeElementClass(e,"hs-show");
	addElementClass(e,"hs-hide");

	var control = hs_controls[e.id];
	removeElementClass(control,"hs-control-show");
	addElementClass(control,"hs-control-hide");
}

function hs_show(e) {
	log("showing " + e);
	removeElementClass(e,"hs-hide");
	addElementClass(e,"hs-show");
	
	var control = hs_controls[e.id];
	removeElementClass(control,"hs-control-hide");
	addElementClass(control,"hs-control-show");
}

function hs_init() {
        log("initializing");
	log("adding callbacks to controls");
	forEach(getElementsByTagAndClassName("a","hs-control"),hs_addControlCallback);
	log("hiding any divs that need to be initially hidden");
	forEach(getElementsByTagAndClassName("*","hs-init-hide"),hs_hide);
   log("check for cookies setting the state for any...");
   forEach(getElementsByTagAndClassName("a","hs-control"),hs_lookForCookie);
}

addLoadEvent(hs_init);
