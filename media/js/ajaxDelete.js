/* requires jQueryUI */

    function ajaxDelete(link, container) {
        var dom = document.getElementById(container);
        jQuery(dom).addClass('about-to-delete');
        if( confirm("Are you sure you want to delete this?") ) {
            jQuery.ajax({
                type: 'POST',
                url: link.href,
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
