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
                    var defaultResponse = 'Settings updated.';
                    var msg = response ? response : defaultResponse;

                    $el.hide();
                    $el.text(msg);
                    $el.fadeIn();
                });
        }
    });
});
