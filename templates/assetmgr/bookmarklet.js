javascript:/*BOOKMARKLET:{{request.get_host}}*/(function(host,bookmarklet_url,user_url){ 

var b=document.body;
var sb=window.SherdBookmarkletOptions;
if (!sb) {
    sb = window.SherdBookmarkletOptions = {};
    sb['action']='jump';
}
sb['host_url']='http://'+host+'/save/?';
{%for k,v in bookmarklet_vars.items%}
  sb['{{k}}']='{{v}}';
{%endfor%}
var r=function(){return 'abcdefghijklmnopqrstuvwxyz0123456789'.charAt(parseInt(Math.random()*36));};
var r3=function(){return '/nocache/'+r()+r()+r();};
var t='text/javascript';
if(b){
    var x=document.createElement('script'); x.type=t; x.src='http://'+host+r3()+user_url;
    b.appendChild(x);
    var z=document.createElement('script'); z.type=t; z.src='http://'+host+r3()+bookmarklet_url;
    b.appendChild(z);
    if (typeof jQuery=='undefined') {
        var y=document.createElement('script');
        y.type=t;
        y.src='http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js';
        var onload = (/MSIE/.test(navigator.userAgent))?'onreadystatechange':'onload';        
        y[onload]=function(){
            var jQ = sb.jQuery = jQuery.noConflict(true);
            if (sb && sb.onJQuery) {
                sb.onJQuery(jQ);
            }
        };
        b.appendChild(y);
    }
}

})('{{request.get_host}}',
   '{%url analyze-bookmarklet "analyze.js" %}',
   '{%url is_logged_in.js %}')