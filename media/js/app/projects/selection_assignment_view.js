/* global _: true, Backbone: true, djangosherd: true */
/* global annotationList: true, CitationView: true */
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

    global.SelectionAssignmentView = Backbone.View.extend({
        events: {
            'click .submit-response': 'onSubmitResponse',
            'click .btn-show-submit': 'onShowSubmitDialog',
            'click .toggle-feedback': 'onToggleFeedback',
            'click .save-feedback': 'onSaveFeedback'
        },
        initialize: function(options) {
            _.bindAll(this, 'render', 'onToggleFeedback',
                      'onShowSubmitDialog', 'onSubmitResponse',
                      'decrementSelectionCount',
                      'incrementSelectionCount');
            var self = this;
            self.viewer = options.viewer;
            self.isFaculty = options.isFaculty;
            self.feedback = options.feedback;
            self.feedbackCount = options.feedbackCount;
            self.myResponse = parseInt(options.responseId, 10);

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
                    'asset_id': options.itemId,
                    'annotation_id': undefined,
                    'update_history': false,
                    'vocabulary': options.vocabulary,
                    'parentId': options.assignmentId,
                    'projectId': options.responseId,
                    'readOnly': readOnly,
                    'view_callback': self.render
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

            // bind beforeunload so user won't forget to submit response
            if (options.responseId.length > 0 && !options.submitted) {
                jQuery(window).bind('beforeunload', function() {
                    return 'Your work has been saved, ' +
                        'but you have not submitted your response.';
                });
            }

            this.listenTo(this, 'render', this.render);
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
                    // rerender the form based on the return context
                    var username = jQuery(frm).attr('data-username');
                    if (self.feedback[username].comment === undefined) {
                        self.feedbackCount++;
                    }
                    self.feedback[username].comment = {
                        'id': json.context.discussion.thread[0].id,
                        'content': json.context.discussion.thread[0].content
                    };
                    jQuery(frm).fadeOut('slow', function() {
                        self.trigger('render');
                    });
                },
                error: function() {
                    var msg = 'An error occurred while saving the feedback. ' +
                        'Please try again';
                    var pos = {
                        my: 'center', at: 'center',
                        of: jQuery('div.asset-view-tabs')
                    };
                    showMessage(msg, undefined, 'Error', pos);
                    self.idle(evt.currentTarget);
                }
            });
        },
        onShowSubmitDialog: function(evt) {
            evt.preventDefault();

            var $elt = jQuery('.project-note-count');
            var $label = jQuery('.project-note-count-label');
            jQuery('.project-submit-count').html($elt.html());
            jQuery('.project-submit-count-label').html($label.html());

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
                    jQuery(window).unbind('beforeunload');
                    window.location = json.context.project.url;
                },
                error: function() {
                    var msg = 'An error occurred while submitting your ' +
                        'response. Please try again';
                    var pos = {
                        my: 'center', at: 'center',
                        of: jQuery('div.asset-view-tabs')
                    };
                    showMessage(msg, undefined, 'Error', pos);
                }
            });
        },
        onToggleFeedback: function(evt) {
            evt.preventDefault();
            var q = jQuery(evt.currentTarget).attr('data-target');
            jQuery('#' + q).toggle();
        },
        incrementSelectionCount: function(evt) {
            var $elt = jQuery('.project-note-count');
            var value = parseInt($elt.html(), 10) + 1;
            $elt.html(value);

            var label = value === 1 ? 'Selection' : 'Selections';
            jQuery('.project-note-count-label').html(label);
        },
        decrementSelectionCount: function(evt) {
            var $elt = jQuery('.project-note-count');
            var value = parseInt($elt.html(), 10) - 1;
            $elt.html(value);

            var label = value === 1 ? 'Selection' : 'Selections';
            jQuery('.project-note-count-label').html(label);
        }
    });
}(jQuery));
