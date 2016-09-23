/* global _: true, AssignmentView: true */

/**
 * Listens For:
 * Nothing
 *
 * Signals:
 * Nothing
 */

(function(jQuery) {
    var global = this;

    global.JuxtapositionAssignmentView = AssignmentView.extend({
        events: {
            'click .submit-response': 'onSubmitResponse',
            'click .btn-show-submit': 'onShowSubmitDialog',
            'click .toggle-feedback': 'onToggleFeedback',
            'click .save-feedback': 'onSaveFeedback'
        },
        initialize: function(options) {
            _.bindAll(this, 'render', 'onToggleFeedback',
                    'onShowSubmitDialog', 'onSubmitResponse');

            AssignmentView.prototype.initialize.apply(this, arguments);
        },
        readyToSubmit: function() {
            return true;
        }
    });
}(jQuery));
