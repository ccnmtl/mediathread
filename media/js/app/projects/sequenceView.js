/* global _: true, AssignmentView: true */
/* global tinymceSettings:true, tinymce: true, showMessage: true */
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
            'keyup input[name="title"]': 'onChange',
            'click .btn-save': 'showSaveOptions',
            'click .save-publish-status .btn-primary': 'saveProject'
        },
        initialize: function(options) {
            _.bindAll(this, 'render',
                'onChange', 'showSaveOptions', 'saveProject',
                'serializeData', 'isDirty', 'setDirty',
                'beforeUnload', 'validTitle');

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
            this.readOnly = options.readOnly;

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
        serializeData: function() {
            var q = '[name="title"], [name="body"], [name="publish"]';
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
            } else {
                if (tinymce && tinymce.activeEditor) {
                    tinymce.activeEditor.isNotDirty = true;
                }
                $elt.text('Saved');
            }
        },
        validTitle: function() {
            var $title = this.$el.find('input.project-title').first();
            var value = $title.val();
            if (!value || value.length < 1) {
                showMessage(
                    'Please specify a title for your composition',
                    null, 'Error');
                $title.focus();
                return false;
            }
            return true;
        },
        saveProject: function(e) {
            e.preventDefault();

            var $elt = this.$el.find('.save-publish-status');
            $elt.modal('hide');

            tinymce.activeEditor.save();

            if (!this.validTitle()) {
                return false;
            }

            var $saveButton = this.$el.find('.btn-save');
            $saveButton.attr('disabled', 'disabled')
                .text('Saving...')
                .addClass('saving');

            jQuery.ajax({
                type: 'POST',
                url: '/project/save/' + this.projectId + '/',
                data: this.serializeData(),
                dataType: 'json',
                error: function() {
                    $saveButton.removeAttr('disabled')
                        .text('Save').removeClass('saving');
                    showMessage('There was an error saving your project.',
                        null, 'Error');
                },
                success: function(json, textStatus, xhr) {
                    jQuery('.sequence-proj-status').text(
                        json.revision.visibility);

                    if (json.revision.public_url) {
                        jQuery('.sequence-proj-status').append(
                            ' (<a href="' + json.revision.public_url + '">' +
                                'public url</a>)');
                    }

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
        showSaveOptions: function(evt) {
            var $elt = this.$el.find('.save-publish-status');
            $elt.modal('show');
        }
    });
}(jQuery));
