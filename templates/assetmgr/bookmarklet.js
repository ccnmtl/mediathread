javascript:/*BOOKMARKLET:{{request.get_host}}*/(function(host,bookmarklet_url,user_url){ 

var b=document.body;
window.SherdBookmarkletOptions={mondrian_url:'http://'+host+'/save/?',
                                action:'jump'
                                {%for k,v in bookmarklet_vars.items%}
                                ,'{{k}}':'{{v}}'
                                {%endfor%}
                               };
var t='text/javascript';
if(b){
    var z=document.createElement('script'); z.type=t; z.src='http://'+host+bookmarklet_url;
    b.appendChild(z);
    var x=document.createElement('script'); x.type=t; x.src='http://'+host+user_url;
    b.appendChild(x);
    if (typeof jQuery=='undefined') {
        var y=document.createElement('script');
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

})('{{request.get_host}}',
   '{%url analyze-bookmarklet "analyze.js" %}',
   '{%url is_logged_in.js %}')