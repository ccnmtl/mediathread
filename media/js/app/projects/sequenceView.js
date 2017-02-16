/* global _: true, AssignmentView: true, updateUserSetting: true */
/* global MediaThread: true, tinymceSettings:true, tinymce: true */
/* global showMessage: true, confirmAction: true */
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

    global.SequenceView = AssignmentView.extend({
        events: {
            'click .toggle-feedback': 'onToggleFeedback',
            'click .save-feedback': 'onSaveFeedback',
            'keyup input[name="title"]': 'onChange',
            'click .btn-save': 'onSaveProject'
        },
        initialize: function(options) {
            _.bindAll(this, 'render', 'onToggleFeedback',
                      'onSaveFeedback', 'onSaveFeedbackSuccess',
                      'onChange', 'onSaveProject', 'serializeData',
                      'isDirty', 'setDirty', 'beforeUnload',
                      'validTitle');

            AssignmentView.prototype.initialize.apply(this, arguments);

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

            this.mapSignals();
        },
        mapSignals: function() {
            var self = this;

            jQuery(window).on(
                'sequence.set_dirty',
                function(e, data) {
                    self.setDirty(data.dirty);
                });

            var $saveButton = this.$el.find('.btn-save');
            jQuery(window).on(
                'sequence.on_save_success',
                function(e, data) {
                    self.setDirty(false);
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
                $elt.removeAttr('disabled');
                $elt.removeClass('disabled');
            } else {
                if (tinymce && tinymce.activeEditor) {
                    tinymce.activeEditor.isNotDirty = true;
                }
                $elt.text('Saved');
                $elt.attr('disabled', 'disabled');
                $elt.addClass('disabled');
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

            var data = this.serializeData();

            var self = this;
            jQuery.ajax({
                type: 'POST',
                url: '/project/save/' + this.responseId + '/',
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
        }
    });
}(jQuery));
