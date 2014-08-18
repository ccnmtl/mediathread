jQuery(document).ready(function () {
    jQuery('.js-captcha-refresh').click(function(){
        var form = jQuery(this).parents('form');

        jQuery.getJSON("/captcha/refresh/", {}, function(json) {
            jQuery(form).find('input[name="captcha_0"]').val(json.key);
            jQuery(form).find('img.captcha').attr('src', json.image_url);
        });

        return false;
    });
});