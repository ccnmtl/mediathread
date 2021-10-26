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

                    if (!response) {
                        $el.addClass('alert alert-danger')
                            .text('Error updating settings.')
                            .fadeIn();
                        return;
                    }

                    var msg = response;
                    var oldmsg = 'Mediathread URL updated to:';

                    if (msg.includes(oldmsg)) {
                        msg = 'The extension will now collect to ' +
                                window.location.origin;
                        $el.text(msg);
                    }

                    $el.hide();
                    $el.addClass('alert alert-info')
                        .text(msg)
                        .fadeIn();
                });
        }
    });
});
