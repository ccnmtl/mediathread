/* global _: true, AssignmentView: true, updateUserSetting: true */
/* global MediaThread: true */
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

    global.SequenceAssignmentView = AssignmentView.extend({
        events: {
            'click .submit-response': 'onSubmitResponse',
            'click .btn-show-submit': 'onShowSubmitDialog',
            'click .toggle-feedback': 'onToggleFeedback',
            'click .save-feedback': 'onSaveFeedback',
            'change textarea[name="comment"]': 'onChangeFeedback',
            'keyup textarea[name="comment"]': 'onChangeFeedback',
            'paste textarea[name="comment"]': 'onChangeFeedback'
        },
        initialize: function(options) {
            _.bindAll(this, 'render', 'onToggleFeedback',
                      'onShowSubmitDialog', 'onSubmitResponse',
                      'onSaveFeedback', 'onSaveFeedbackSuccess',
                      'onChangeFeedback');

            AssignmentView.prototype.initialize.apply(this, arguments);

            var key = 'assignment_instructions_' + options.assignmentId;
            jQuery('#accordion').on('hidden.bs.collapse', function() {
                updateUserSetting(MediaThread.current_username, key, false);
            });

            jQuery('#accordion').on('shown.bs.collapse', function() {
                updateUserSetting(MediaThread.current_username, key, true);
            });
        },
        readyToSubmit: function() {
            return true;
        },
        onChangeFeedback: function() {
            this.$el.find('.alert-success').fadeOut();
        },
        onSaveFeedbackSuccess: function(frm, json) {
            this.$el.find('.alert-success').show();
            var today = Date().toLocaleString();
            var dataId = 'feedback-date-' + this.responseId;
            this.$el.find('span[data-id=' + dataId + ']').html(today);
        }
    });
}(jQuery));
