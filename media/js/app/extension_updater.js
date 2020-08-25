/* global chrome: true */

jQuery(document).ready(function() {
    jQuery('.update-chrome-extension-hosturl').click(function() {
        if (chrome && chrome.runtime) {
            var extensionId = 'gambcgmmppeklfmbahomokogelnaffbi';
            chrome.runtime.sendMessage(
                extensionId, {
                    command: 'updatesettings'
                }, function(response) {
                    var $el = jQuery('.update-chrome-extension-feedback');
                    var defaultResponse = 'Error Updating Settings.';
                    var msg = response ? response : defaultResponse;
                    var oldmsg = 'Mediathread URL updated to:';

                    $el.hide();
                    if(msg === defaultResponse) {
                        $el.addClass('alert alert-danger');
                        $el.text(msg);
                    } else if (msg.includes(oldmsg)) {
                        $el.addClass('alert alert-info');
                        msg = 'The extension will now collect to ' +
                                window.location.origin;
                        $el.text(msg);
                    } else {
                        $el.text(msg);
                        $el.addClass('alert alert-info');
                    }
                    $el.fadeIn();
                });
        }
    });
});
