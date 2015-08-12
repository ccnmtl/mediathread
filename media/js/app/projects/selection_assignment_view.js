/* global _: true, Backbone: true, djangosherd: true */
/* global annotationList: true, CitationView: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

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
            var self = this;

            jQuery('[data-toggle="tooltip"]').tooltip();

            // load the selection item into storage
            djangosherd.storage.json_update(options.itemJson);

            // Setup the media display window.
            this.citationView = new CitationView();
            this.citationView.init({
                'default_target': 'asset-workspace-videoclipbox',
                'presentation': 'medium',
                'clipform': true,
                'autoplay': false
            });

            this.citationView.openCitationById(null, options.itemId, null);

            if (jQuery('#asset-view-details').length > 0) {
                window.annotationList.init({
                    'asset_id': options.itemId,
                    'annotation_id': undefined,
                    'update_history': false,
                    'vocabulary': options.vocabulary,
                    'parentId': options.assignmentId,
                    'projectId': options.responseId
                });
            }
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
