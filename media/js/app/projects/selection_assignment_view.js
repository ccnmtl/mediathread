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
            'click .submit-response': 'onSubmitResponse',
            'click .btn-show-submit': 'onShowSubmitDialog'
        },
        initialize: function(options) {
            _.bindAll(this, 'onSubmitResponse', 'onShowSubmitDialog');
            var self = this;

            self.viewer = options.viewer;

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

            // annotationlist is readonly by faculty and submitted students
            var readOnly = options.responseId.length < 1 || options.submitted;

            if (jQuery('#asset-view-details').length > 0) {
                window.annotationList.init({
                    'asset_id': options.itemId,
                    'annotation_id': undefined,
                    'update_history': false,
                    'vocabulary': options.vocabulary,
                    'parentId': options.assignmentId,
                    'projectId': options.responseId,
                    'readOnly': readOnly
                });
            }
        },
        onShowSubmitDialog: function(evt) {
            evt.preventDefault();
            var opts = {'show': true, 'backdrop': 'static'};

            if (window.annotationList.hasAnnotations(this.viewer)) {
                jQuery('#submit-project').modal(opts);
            } else {
                jQuery('#cannot-submit-project').modal(opts);
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
