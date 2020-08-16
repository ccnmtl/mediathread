/* global djangosherd: true */
/* global AssignmentView: true, CitationView: true */
/* global Mustache: true, MediaThread: true, showMessage: true */
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

    global.SelectionAssignmentView = AssignmentView.extend({
        events: {
            'click .submit-response': 'onSubmitResponse',
            'click .btn-show-submit': 'onShowSubmitDialog',
            'click .toggle-feedback': 'onToggleFeedback',
            'click .save-feedback': 'onSaveFeedback'
        },
        initialize: function(options) {
            _.bindAll(this, 'render', 'onToggleFeedback',
                'onShowSubmitDialog', 'onSubmitResponse',
                'decrementSelectionCount', 'incrementSelectionCount',
                'onSaveFeedbackSuccess');

            AssignmentView.prototype.initialize.apply(this, arguments);

            var self = this;

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
            var readOnly = options.responseId.length < 1 ||
                           options.submitted ||
                           options.isFaculty;

            if (jQuery('#asset-view-details').length > 0) {
                window.annotationList.init({
                    'parent': this.$el,
                    'asset_id': options.itemId,
                    'annotation_id': undefined,
                    'update_history': false,
                    'vocabulary': options.vocabulary,
                    'parentId': options.assignmentId,
                    'projectId': options.responseId,
                    'readOnly': readOnly,
                    'view_callback': this.render
                });
                MediaThread.loadTemplate('asset_feedback')
                    .then(function() {
                        self.initializeAfterTemplateLoad(options);
                    });
            } else {
                this.initializeAfterTemplateLoad(options);
            }
        },
        initializeAfterTemplateLoad: function(options) {
            var self = this;

            jQuery(window).on('annotation.on_delete', {'self': self},
                self.decrementSelectionCount);
            jQuery(window).on('annotation.on_create', {'self': self},
                self.incrementSelectionCount);
            jQuery(window).one('annotation-list.init', {'self': self},
                self.render);
        },
        render: function() {
            var self = this;
            jQuery('.feedback-count').html(self.feedbackCount);
            jQuery('#annotations-organized .group-header').each(function() {
                // annotations exist?
                var ctx = {
                    'isFaculty': self.isFaculty,
                    'color': jQuery(this).find('.color-box')
                        .css('background-color'),
                    'title': jQuery(this).find('.group-title').html()
                };
                var elt = jQuery(this).parent()
                    .find('.annotation-header')
                    .first();
                if (elt.length) {
                    var username = jQuery(elt).data('username');
                    ctx.username = username;
                    ctx.responseId = self.feedback[username].responseId;
                    ctx.comment = self.feedback[username].comment;
                    ctx.showFeedback = ctx.responseId === self.myResponse &&
                        ctx.comment !== undefined;

                    // render the template
                    var rendered = Mustache.render(
                        MediaThread.templates.asset_feedback, ctx);
                    jQuery(this).html(rendered);
                }
            });
        },
        readyToSubmit: function() {
            var $elt = jQuery('.project-note-count');
            var $label = jQuery('.project-note-count-label');
            jQuery('.project-submit-count').html($elt.html());
            jQuery('.project-submit-count-label').html($label.html());
            return window.annotationList.hasAnnotations(this.viewer);
        },
        adjustSelectionCount: function(evt, increment) {
            var $elt = jQuery('.project-note-count');

            var html = $elt.html();
            var noteCount = html.length ? parseInt(html, 10) : 0;
            noteCount += increment;

            if (noteCount > 0) {
                // Enabled button will display "Submit n Selections"
                $elt.html(noteCount);
                var label = noteCount === 1 ? 'Selection' : 'Selections';
                jQuery('.project-note-count-label').html(label);
                $elt.parent('button').removeAttr('disabled');
            } else {
                // Disabled button will display "Submit Selections"
                $elt.html('');
                jQuery('.project-note-count-label').html('Selections');
                $elt.parent('button').attr('disabled', 'disabled');
            }
        },
        incrementSelectionCount: function(evt) {
            this.adjustSelectionCount(evt, 1);
        },
        decrementSelectionCount: function(evt) {
            this.adjustSelectionCount(evt, -1);
        },
        onSaveFeedbackSuccess: function(frm, json) {
            // rerender the form based on the return context
            var username = jQuery(frm).attr('data-username');
            if (this.feedback[username].comment === undefined) {
                this.feedbackCount++;
            }
            this.feedback[username].comment = {
                'id': json.context.discussion.thread[0].id,
                'content': json.context.discussion.thread[0].content
            };
            var self = this;
            jQuery(frm).fadeOut('slow', function() {
                self.trigger('render');
            });
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
                    jQuery(window).unbind('beforeunload');
                    // eslint-disable-next-line scanjs-rules/assign_to_location
                    window.location = json.context.project.url;
                },
                error: function() {
                    var msg = 'An error occurred while submitting your ' +
                        'response. Please try again';
                    var pos = {
                        my: 'center', at: 'center',
                        of: jQuery('.container')
                    };
                    showMessage(msg, undefined, 'Error', pos);
                }
            });
        }
    });
}(jQuery));
