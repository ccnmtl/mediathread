/* requires jQueryUI */

    function ajaxDelete(link, container) {
        if( confirm("Are you sure?") ) {
            jQuery.ajax({
                type: 'POST',
                url: link.href,
                success:function (responseText, textStatus, xhr) {
                    if( xhr.status == 200 ) {
                        jQuery('#'+container).hide("fade");
                    } else alert("Error: "+textStatus);
                },
                error:function(xhr) {
                    window.sky = xhr;
                    alert("Error!");
                }
            });
        }
        return false;
    }
