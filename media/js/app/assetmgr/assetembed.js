/* exported initializeAssetEmbed */

// eslint-disable-next-line no-unused-vars
function initializeAssetEmbed(options) {
    jQuery(window).one('collection.ready', {'self': this},
        function(event, params) {
            jQuery(window).trigger('collection.open', [{
                'allowAssets': true,
                'disable': []
            }]);
        }
    );

    document.addEventListener('asset.select', function(e) {
        e.preventDefault();
        var $form = jQuery('#asset-embed-form');
        var $elt = jQuery('#selection-to-embed');

        if (e.detail.annotationId) {
            $elt.attr('name', 'selection-' + e.detail.annotationId);
            $elt.attr('value', 'Embed Selection');
        } else {
            $elt.attr('name', 'item-' + e.detail.assetId);
            $elt.attr('value', 'Embed Item');
        }

        $form.submit();
        return false;
    });
}

