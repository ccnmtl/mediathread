/* global _: true, Backbone: true, tinymce: true, tinymceSettings: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function(jQuery) {
    var global = this;

    global.AssignmentEditView = Backbone.View.extend({
        events: {
            'click .next': 'onNext',
            'click .prev': 'onPrev',
            'click .save': 'onSave'
        },
        initialize: function(options) {
            _.bindAll(this, 'onNext', 'onPrev', 'onSave', 'beforeUnload');
            var self = this;

            this.currentPage = 1;
            this.totalPages = jQuery('.page').length;

            this.tinymceSettings = jQuery.extend(tinymceSettings, {
                init_instance_callback: function(instance) {
                    if (instance && !self.tinymce) {
                        self.tinymce = instance;
                    }
                }
            });

            // hook up behaviors
            jQuery('input[name="due_date"]').datepicker({
                minDate: 0,
                dateFormat: 'mm/dd/yy'
            });

            jQuery(window).bind('beforeunload', self.beforeUnload);
        },
        beforeUnload: function() {
            return 'Changes to your assignment have not been saved.';
        },
        validate: function(pageContent) {
            if (pageContent === 'title') {
                var title = jQuery(this.el).find('input[name="title"]').val();
                var body = this.tinymce.getContent();
                return title.length > 0 && body.length > 0;
            } else if (pageContent === 'due-date') {
                var q1 = 'input[name="due_date"]';
                var q2 = 'input[name="response_view_policy"]:checked';
                return jQuery(q1).val() !== undefined &&
                    jQuery(q1).val() !== '' && jQuery(q2).val() !== undefined;
            } else if (pageContent === 'publish') {
                var q = 'input[name="publish"]:checked';
                return jQuery(q).val() !== undefined;
            }
            return true;
        },
        showPage: function(pageContent) {
            if (pageContent === 'title') {
                if (!this.tinymce) {
                    tinymce.settings = this.tinymceSettings;
                    tinymce.execCommand('mceAddEditor', true,
                                        'assignment-instructions');
                    tinymce.execCommand('mceAddEditor', true, 'summary');
                }
            } else if (pageContent === 'due-date') {
                // if there is only one radio button, select it
                var elts = jQuery('input[name="response_view_policy"]');
                if (elts.length === 1) {
                    jQuery(elts).attr('checked', 'checked');
                }
            }
        },
        onNext: function(evt) {
            var $current = jQuery('div[data-page="' + this.currentPage + '"]');
            var content = $current.data('page-content');
            if (!this.validate(content)) {
                $current.addClass('has-error');
                return false;
            }

            $current.removeClass('has-error').addClass('hidden');

            this.currentPage = Math.min(this.currentPage + 1, this.totalPages);
            $current = jQuery('div[data-page="' + this.currentPage + '"]');
            $current.removeClass('hidden');
            this.showPage($current.data('page-content'));
        },
        onPrev: function() {
            jQuery('.page').addClass('hidden');

            this.currentPage = Math.max(this.currentPage - 1, 1);
            var $current = jQuery('div[data-page="' + this.currentPage + '"]');
            $current.removeClass('hidden');
            this.showPage($current.data('page-content'));
        },
        onSave: function(evt) {
            var $current = jQuery('div[data-page="' + this.currentPage + '"]');
            var content = $current.data('page-content');
            if (!this.validate(content)) {
                $current.addClass('has-error');
                return false;
            }

            jQuery(window).unbind('beforeunload');
            tinymce.activeEditor.save();
            var frm = jQuery(evt.currentTarget).parents('form')[0];
            jQuery.ajax({
                type: 'POST',
                url: frm.action,
                dataType: 'json',
                data: jQuery(frm).serializeArray(),
                success: function(json) {
                    // eslint-disable-next-line scanjs-rules/assign_to_location
                    window.location = json.context.project.url;
                },
                error: function() {
                    // do something useful here
                }
            });
        },
        onFormKeyPress: function(evt) {
            if (evt.keyCode === 13) {
                evt.preventDefault();
            }
        }
    });
}(jQuery));
