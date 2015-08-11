/* global _: true, Backbone: true */
/* global annotationList: true, CitationView: true */

/**
 * Listens For:
 * Nothing
 *
 * Signals:
 * Nothing
 */

(function(jQuery) {
    var global = this;

    global.SelectionAssignmentView = Backbone.View.extend({
        events: {
            'click .submit-response': 'onSubmitResponse'
        },
        initialize: function(options) {
            _.bindAll(this, 'onSubmitResponse');

            jQuery('[data-toggle="tooltip"]').tooltip();

            // Setup the media display window.
            this.citationView = new CitationView();
            this.citationView.init({
                'default_target': 'asset-workspace-videoclipbox',
                'presentation': 'medium',
                'clipform': true,
                'autoplay': false
            });

            this.citationView.openCitationById(null, options.itemId, null);

            // @todo Setup the edit view -- anotationList.init
        },
        onSubmitResponse: function(evt) {
            evt.preventDefault();
            var frm = jQuery(this.el).find('.project-response-form')[0];
            jQuery.ajax({
                type: 'POST',
                url: frm.action,
                dataType: 'json',
                data: jQuery(frm).serializeArray(),
                success: function(json) {
                    window.location = json.context.project.url;
                },
                error: function() {
                    // do something useful here
                }
            });
        }
    });
}(jQuery));
