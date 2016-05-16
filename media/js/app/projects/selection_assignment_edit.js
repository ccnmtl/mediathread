/* global _: true, Backbone: true, CitationView: true */
/* global showMessage: true, tinymce: true, tinymceSettings: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function(jQuery) {
    var global = this;

    global.SelectionAssignmentEditView = Backbone.View.extend({
        events: {
            'click .next': 'onNext',
            'click .prev': 'onPrev',
            'click .save': 'onSave',
            'mouseover .asset-table .gallery-item': 'onGalleryItemMouseOver',
            'mouseleave .asset-table': 'onGalleryMouseOut',
            'click .gallery-item-overlay': 'onGalleryItemSelect',
            'keypress form[name="selection-assignment-edit"]': 'onFormKeyPress'
        },
        initialize: function(options) {
            _.bindAll(this, 'onNext', 'onPrev', 'onSave', 'onFormKeyPress',
                      'onGalleryItemMouseOver', 'onGalleryMouseOut',
                      'onGalleryItemSelect', 'beforeUnload');
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

            // Setup the media display window.
            this.citationView = new CitationView();
            this.citationView.init({
                'default_target': 'asset-workspace-videoclipbox',
                'presentation': 'medium',
                'clipform': false,
                'autoplay': false
            });

            jQuery(window).bind('beforeunload', self.beforeUnload);
        },
        beforeUnload: function() {
            return 'Changes to your assignment have not been saved.';
        },
        validate: function(pageNo) {
            var q;
            if (pageNo === 2) {
                return jQuery('input[name="item"]').val() !== '';
            } else if (pageNo === 3) {
                var title = jQuery(this.el).find('input[name="title"]').val();
                var body = this.tinymce.getContent();
                return title.length > 0 && body.length > 0;
            } else if (pageNo === 4) {
                var q1 = 'input[name="due_date"]';
                var q2 = 'input[name="response_view_policy"]:checked';
                return jQuery(q1).val() !== undefined &&
                    jQuery(q2).val() !== undefined;
            } else if (pageNo === 5) {
                q = 'input[name="publish"]:checked';
                return jQuery(q).val() !== undefined;
            }
            return true;
        },
        onNext: function(evt) {
            var $current = jQuery('div[data-page="' + this.currentPage + '"]');
            if (!this.validate(this.currentPage)) {
                $current.addClass('has-error');
            } else {
                $current.removeClass('has-error').addClass('hidden');

                this.currentPage = Math.min(this.currentPage + 1,
                                            this.totalPages);
                var q = 'div[data-page="' + this.currentPage + '"]';
                jQuery(q).removeClass('hidden');

                if (this.currentPage === 2) {
                    jQuery('#sliding-content-container').removeClass('hidden');
                    jQuery('.asset-view-publish-container').addClass('hidden');
                    jQuery(window).trigger('resize');
                } else if (this.currentPage === 3) {
                    jQuery('#sliding-content-container').addClass('hidden');
                    jQuery('.asset-view-publish-container').removeClass(
                        'hidden');
                    var itemId = jQuery('input[name="item"]').val();
                    this.citationView.openCitationById(null, itemId, null);

                    if (!this.tinymce) {
                        tinymce.settings = this.tinymceSettings;
                        tinymce.execCommand('mceAddEditor', true,
                                            'assignment-instructions');
                    }
                } else if (this.currentPage === 4) {
                    // if there is only one radio button, select it
                    var elts = jQuery('input[name="response_view_policy"]');
                    if (elts.length === 1) {
                        jQuery(elts).attr('checked', 'checked');
                    }
                }
            }
        },
        onPrev: function() {
            jQuery('#sliding-content-container').addClass('hidden');
            jQuery('.page').addClass('hidden');

            this.currentPage = Math.max(this.currentPage - 1, 1);
            var q = 'div[data-page="' + this.currentPage + '"]';
            jQuery(q).removeClass('hidden');

            if (this.currentPage === 2) {
                jQuery('#sliding-content-container').removeClass('hidden');
                jQuery('.asset-view-publish-container').addClass('hidden');
                jQuery(window).trigger('resize');
            }
        },
        onSave: function(evt) {
            var $current = jQuery('div[data-page="' + this.currentPage + '"]');
            if (!this.validate(this.currentPage)) {
                $current.addClass('has-error');
            } else {
                jQuery(window).unbind('beforeunload');
                tinymce.activeEditor.save();
                var frm = jQuery(evt.currentTarget).parents('form')[0];
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
        },
        onFormKeyPress: function(evt) {
            if (evt.keyCode === 13) {
                evt.preventDefault();
            }
        },
        onGalleryItemMouseOver: function(evt) {
            this.hoverItem = evt.currentTarget;
            var $elt = jQuery(evt.currentTarget);
            var $overlay = jQuery('.gallery-item-overlay').first();
            $overlay.css('top', $elt.position().top);
            $overlay.css('left', $elt.position().left);
            $overlay.css('width', $elt.outerWidth());
            $overlay.css('height', $elt.outerHeight());
            $overlay.removeClass('hidden');
        },
        onGalleryMouseOut: function(evt) {
            delete this.hoverItem;
            var $overlay = jQuery('.gallery-item-overlay');
            $overlay.addClass('hidden');
        },
        onGalleryItemSelect: function(evt) {
            if (!this.hoverItem) {
                return;
            }
            jQuery('.has-error').removeClass('has-error');

            var pk = jQuery(this.hoverItem).attr('data-id');
            jQuery('input[name="item"]').val(pk);

            var clone = jQuery.clone(this.hoverItem);
            jQuery(clone).attr('style', 'float: none');
            jQuery('.selected-item div').replaceWith(clone);

            delete this.hoverItem;

            // scroll to top of page
            jQuery('body').scrollTop(0);
        }
    });
}(jQuery));
