/* global _: true, Backbone: true, showMessage: true, tinymce: true */

/**
 * Listens For:
 * Nothing
 *
 * Signals:
 * Nothing
 */

(function(jQuery) {
    var global = this;

    global.AssignmentView = Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            self.viewer = options.viewer;
            self.isFaculty = options.isFaculty;
            self.feedback = options.feedback;
            self.feedbackCount = options.feedbackCount;
            self.responseId = options.responseId;
            self.projectId = options.projectId;
            self.assignmentId = options.assignmentId;
            self.myResponse = parseInt(options.responseId, 10);

            // bind beforeunload so user won't forget to submit response
            if (options.responseId && options.responseId.length > 0 &&
                !options.submitted
               ) {
                jQuery(window).bind('beforeunload', this.beforeUnload);
            }

            this.listenTo(this, 'render', this.render);
        },
        beforeUnload: function() {
            return 'Your work has been saved, ' +
                'but you have not submitted your response.';
        },
        busy: function(elt) {
            var parent = jQuery(elt).parents('.group-header')[0];
            elt = jQuery(parent).find('a.toggle-feedback .glyphicon');
            jQuery(elt).removeClass('glyphicon-pencil glyphicon-plus');
            jQuery(elt).addClass('glyphicon-repeat spin');
        },
        idle: function(elt) {
            var parent = jQuery(elt).parents('.group-header')[0];
            elt = jQuery(parent).find('a.toggle-feedback .glyphicon');
            jQuery(elt).removeClass('glyphicon-repeat spin');
            jQuery(elt).addClass('glyphicon-pencil');
        },
        onSaveFeedback: function(evt) {
            var self = this;
            if (typeof(tinymce) !== 'undefined') {
                tinymce.activeEditor.save();
            }

            evt.preventDefault();
            self.busy(evt.currentTarget);

            // change the feedback icon to a progress indicator
            var frm = jQuery(evt.currentTarget).parents('form')[0];

            jQuery.ajax({
                type: 'POST',
                url: frm.action,
                dataType: 'json',
                data: jQuery(frm).serializeArray(),
                success: function(json) {
                    self.onSaveFeedbackSuccess(frm, json);
                },
                error: function() {
                    var msg = 'An error occurred while saving the feedback. ' +
                        'Please try again';
                    var pos = {
                        my: 'center', at: 'center',
                        of: jQuery('.container')
                    };
                    showMessage(msg, undefined, 'Error', pos);
                    self.idle(evt.currentTarget);
                }
            });
        },
        onShowSubmitDialog: function(evt) {
            evt.preventDefault();

            var opts = {'show': true, 'backdrop': 'static'};

            if (this.readyToSubmit()) {
                jQuery('#submit-project').modal(opts);
            } else {
                jQuery('#cannot-submit-project').modal(opts);
            }
        },
        onToggleFeedback: function(evt) {
            evt.preventDefault();
            var q = jQuery(evt.currentTarget).attr('data-target');
            jQuery('#' + q).toggle();
        }
    });
}(jQuery));
