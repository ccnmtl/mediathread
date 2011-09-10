/* requires jQueryUI */

    function ajaxDelete(link, container, opts) {
        var postUrl = null;
        if (link && link.href)
            postUrl = link.href;
        else if (opts && opts.href)
            postUrl = opts.href;
        else
            alert("An error occurred. Unable to delete this item.");
        
        var dom = document.getElementById(container);
        jQuery(dom).addClass('about-to-delete');
        if( confirm("Are you sure you want to delete this?") ) {
            jQuery.ajax({
                type: 'POST',
                url: postUrl,
                success:function (responseText, textStatus, xhr) {
                    if( xhr.status == 200 ) {
                        jQuery(dom).hide("fade");
                    } else alert("Error: "+textStatus);
                },
                error:function(xhr) {
                    window.sky = xhr;
                    alert("Error!");
                }
            });
        } else {
            jQuery(dom).removeClass('about-to-delete');
        }
        return false;
    }
