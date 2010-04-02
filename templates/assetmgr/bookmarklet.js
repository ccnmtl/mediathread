javascript:/*BOOKMARKLET:{{request.get_host}}*/(function(host,bookmarklet_url){ 

var b=document.body;
window.SherdBookmarkletOptions={mondrian_url:'http://'+host+'/save/?',
                                action:'jump'
                                {%for k,v in bookmarklet_vars.items%}
                                ,'{{k}}':'{{v}}'
                                {%endfor%}
                               };
var t='text/javascript';
if(b){
    z=document.createElement('script');
    z.type=t;
    z.src='http://'+host+bookmarklet_url;
    b.appendChild(z);
    if (typeof jQuery=='undefined') {
        y=document.createElement('script');
        y.type=t;
        y.src='http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js';
        var onload = (/Trident/.test(navigator.userAgent))?'onreadystatechange':'onload';
        y[onload]=function(){
            window.SherdBookmarkletOptions.jQuery = jQuery.noConflict(true);
            if (MondrianBookmarklet && MondrianBookmarklet.onJQuery) {
                MondrianBookmarklet.onJQuery(window.SherdBookmarkletOptions.jQuery);
            }
        };
        b.appendChild(y);
    }
}

 })('{{request.get_host}}','{%url analyze-bookmarklet "analyze.js" %}')