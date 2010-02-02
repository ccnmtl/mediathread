/*
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

*/

var tinyMCEmode = true;
function toogleEditorMode(textarea_id) {

function toggleEditor(id) {
    if (!tinyMCE.get(id))
        tinyMCE.execCommand('mceAddControl', false, id);

    else
        tinyMCE.execCommand('mceRemoveControl', false, id);
    }
}


function toggleVisible(elem) {
    toggleElementClass("invisible", elem);
}

function makeVisible(elem) {
    removeElementClass(elem, "invisible");
}

function makeInvisible(elem) {
    addElementClass(elem, "invisible");
}



function connect_respond_clicked (e) {
    //logDebug (e.src().parentNode.id);
    div_id = e.src().parentNode.id 
    the_text_area =  $$('#' + div_id  + ' textarea')[0];
    the_div = $$('#' + div_id  + ' ul')[0]
    if (hasElementClass (the_div, 'invisible')) {
        makeVisible(the_div);
        tinyMCE.execCommand('mceAddControl', false, the_text_area);
    }
    else {
        tinyMCE.execCommand('mceRemoveControl', false, the_text_area);
        makeInvisible(the_div);
    }
}

function connect_respond_prompt(a) {
    connect (a, 'onclick', connect_respond_clicked);
}

function discussion_init() {
    forEach ($$('div.respond_to_comment_form_div ul'), makeInvisible);
    forEach ($$('input[name=url]'), makeInvisible);
    forEach ($$('input[name=honeypot]'), makeInvisible);
    forEach ($$('input[name=name]'), makeInvisible);
    forEach ($$('input[name=email]'), makeInvisible);
    forEach ($$('label[for=id_url]'), makeInvisible);
    forEach ($$('label[for=id_honeypot]'), makeInvisible);
    forEach ($$('label[for=id_name]'), makeInvisible);
    forEach ($$('label[for=id_email]'), makeInvisible);
    
    forEach($$('.respond_prompt'), connect_respond_prompt)
        //connect (
}
addLoadEvent(discussion_init);
