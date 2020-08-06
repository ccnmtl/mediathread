/* global AssignmentView: true, updateUserSetting: true */
/* global MediaThread: true, tinymceSettings:true, tinymce: true */
/* global showMessage: true, showMessage: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

/**
 * Listens For:
 * sequence.set_dirty
 * sequence.on_save_success
 * sequence.on_save_error
 *
 * Signals:
 * sequence.save
 */

(function(jQuery) {
    var global = this;

    global.SequenceAssignmentView = AssignmentView.extend({
        events: {
            'click .submit-response': 'onSubmitResponse',
            'click .btn-show-submit': 'onShowSubmitDialog',
            'click .toggle-feedback': 'onToggleFeedback',
            'click .save-feedback': 'onSaveFeedback',
            'keyup input[name="title"]': 'onChange',
            'click .btn-save': 'onSaveProject',
            'click .btn-unsubmit': 'onConfirmUnsubmitResponse',
        },
        initialize: function(options) {
            _.bindAll(this, 'render', 'onToggleFeedback',
                'onShowSubmitDialog', 'onSubmitResponse',
                'onSaveFeedback', 'onSaveFeedbackSuccess',
                'onChange', 'onSaveProject', 'serializeData',
                'isDirty', 'setDirty', 'beforeUnload',
                'validTitle',
                'onConfirmUnsubmitResponse', 'onUnsubmitResponse');

            AssignmentView.prototype.initialize.apply(this, arguments);

            var key = 'assignment_instructions_' + options.assignmentId;
            jQuery('#accordion').on('hidden.bs.collapse', function() {
                updateUserSetting(MediaThread.current_username, key, false);
            });

            jQuery('#accordion').on('shown.bs.collapse', function() {
                updateUserSetting(MediaThread.current_username, key, true);
            });

            var self = this;
            var settings = jQuery.extend(tinymceSettings, {
                height: '300',
                setup: function(ed) {
                    ed.on('change', function(e) {
                        self.setDirty(true);
                    });
                }
            });
            tinymce.init(settings);

            this.dirty = false;
            this.readOnly = options.readOnly;
            this.primaryInstructions = options.primaryInstructions;
            this.secondaryInstructions = options.secondaryInstructions;

            // bind beforeunload for faculty to ensure feedback is saved
            if (options.isFaculty) {
                jQuery(window).bind('beforeunload', this.beforeUnload);
            }

            this.mapSignals();
        },
        mapSignals: function() {
            var self = this;

            jQuery(window).on(
                'sequence.set_dirty',
                function(e, data) {
                    self.setDirty(data.dirty);
                });

            jQuery(window).on(
                'sequence.set_submittable',
                function(e, data) {
                    self.setSubmittable(data.submittable);
                });

            var $saveButton = this.$el.find('.btn-save');
            jQuery(window).on(
                'sequence.on_save_success',
                function(e, data) {
                    self.setDirty(false);
                    self.setSubmittable(data.submittable);
                    $saveButton.removeAttr('disabled')
                        .removeClass('saving', 1200, function() {
                            jQuery(self).text('Saved');
                        });
                });

            jQuery(window).on(
                'sequence.on_save_error',
                function(e, data) {
                    $saveButton.removeAttr('disabled')
                        .text('Save').removeClass('saving');
                    showMessage('There was an error saving your project.',
                        null, 'Error');
                });
        },
        beforeUnload: function() {
            // Check tinymce dirty state.
            // For some reason, the instance is not always current
            if (this.isDirty()) {
                return 'Changes to your project have not been saved.';
            }
        },
        onChange: function() {
            this.setDirty(true);
            this.$el.find('.alert-success').fadeOut();
        },
        onSaveFeedbackSuccess: function(frm, json) {
            this.setDirty(false);
            this.$el.find('.alert-success').show();
            var today = Date().toLocaleString();
            var dataId = 'feedback-date-' + this.responseId;
            this.$el.find('span[data-id=' + dataId + ']').html(today);
        },
        serializeData: function() {
            var q = '[name="title"], [name="body"]';
            return this.$el.find(q).serializeArray();
        },
        isDirty: function() {
            return this.dirty;
        },
        setDirty: function(isDirty) {
            this.dirty = isDirty;
            var $elt = this.$el.find('.btn-save');
            if (isDirty) {
                $elt.text('Save');
                $elt.removeClass('disabled');
                jQuery('.btn-show-submit').addClass('disabled');
            } else {
                if (tinymce && tinymce.activeEditor) {
                    tinymce.activeEditor.isNotDirty = true;
                }
                $elt.text('Saved');
                $elt.addClass('disabled');
            }
        },
        setSubmittable: function(isSubmittable) {
            if (isSubmittable) {
                jQuery('.btn-show-submit').removeClass('disabled');
            } else {
                jQuery('.btn-show-submit').addClass('disabled');
            }
        },
        validTitle: function() {
            var $title = this.$el.find('input.project-title').first();
            var value = $title.val();
            if (!value || value.length < 1) {
                showMessage(
                    'Please specify a title for your response',
                    null, 'Error');
                $title.focus();
                return false;
            }
            return true;
        },
        onSaveProject: function(e) {
            e.preventDefault();
            tinymce.activeEditor.save();

            if (!this.validTitle()) {
                return false;
            }

            var $saveButton = this.$el.find('.btn-save');
            $saveButton.attr('disabled', 'disabled')
                .text('Saving...')
                .addClass('saving');

            let saveUrl = '/course/' + MediaThread.current_course +
                '/project/save/' + this.responseId + '/';

            jQuery.ajax({
                type: 'POST',
                url: saveUrl,
                data: this.serializeData(),
                dataType: 'json',
                error: function() {
                    $saveButton.removeAttr('disabled')
                        .text('Save').removeClass('saving');
                    showMessage('There was an error saving your project.',
                        null, 'Error');
                },
                success: function(json, textStatus, xhr) {
                    if (json.status === 'error') {
                        showMessage(json.msg, null, 'Error');
                    } else {
                        document.dispatchEvent(
                            new CustomEvent('sequence.save'));
                    }
                }
            });

            return true;
        },
        onConfirmUnsubmitResponse: function() {
            showMessage(
                'Are you sure? Once you unsubmit, you will no ' +
                'longer have access to this student\'s response. And, you ' +
                'will be taken to the main assignment page to choose ' +
                'another response.',
                this.onUnsubmitResponse, 'Unsubmit Response');
        },
        onUnsubmitResponse: function(evt) {
            var frm = jQuery(this.el).find('.unsubmit-response-form')[0];
            jQuery(frm.submit());
        },
        readyToSubmit: function() {
            return true;
        },
        onSubmitResponse: function(evt) {
            evt.preventDefault();

            var data = this.serializeData();
            data.push({
                'name': 'publish',
                'value': this.$el.find(
                    '#submit-project input[name="publish"]').val()
            });

            var saveUrl = '/course/' + MediaThread.current_course +
                '/project/save/' + this.responseId + '/';

            jQuery.ajax({
                type: 'POST',
                url: saveUrl,
                data: data,
                dataType: 'json',
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

            return true;
        }
    });
}(jQuery));
