/* global _: true, Backbone: true */
/* global showMessage: true, tinyMCE: true */

(function(jQuery) {
    var global = this;

    global.SelectionAssignmentView = Backbone.View.extend({
        events : {
            'click .next': 'onNext',
            'click .prev': 'onPrev',
            'click .save': 'onSave',
            'mouseover .asset-table .gallery-item': 'onGalleryItemMouseOver',
            'mouseleave .asset-table': 'onGalleryMouseOut',
            'click .gallery-item-overlay': 'onGalleryItemSelect',
            'keypress form[name="selection-assignment-edit"]': 'onFormKeyPress'
        },
        initialize: function(options) {
            _.bindAll(this, 'onNext', 'onPrev', 'onSave',
                    'onFormKeyPress',
                    'onGalleryItemMouseOver', 'onGalleryMouseOut',
                    'onGalleryItemSelect');
            var self = this;
            this.currentPage = 1;
            this.totalPages = 4;
            
            // hook up behaviors
            jQuery(window).on('tinymce_init_instance',
                function (event, instance, param2) {
                    if (instance) {
                        var width = jQuery(self.el).find('textarea').width();
                        instance.theme.resizeTo(width, 400);
                    }
                }
            );
            jQuery('input[name="due_date"]').datepicker({
                minDate: 0,
                dateFormat: 'mm/dd/yy'
            });
        },
        validate: function(pageNo) {
            if (pageNo === 1) {
                return jQuery(this.el).find("input[name='title']").val().length > 0;
            } else if (pageNo === 2) {
                return tinyMCE.activeEditor.getContent().length > 0;
            } else if (pageNo === 3) {
                return jQuery("input[name='item']").val() !== '';
            } else if (pageNo === 4) {
                return true;
            }
        },
        onNext: function(evt) {
            var $current = jQuery("div[data-page='" + this.currentPage + "']"); 
            if (!this.validate(this.currentPage)) {
                $current.addClass('has-error');
            } else {
                $current.removeClass('has-error').addClass('hidden');

                this.currentPage = Math.min(this.currentPage + 1, this.totalPages);
                jQuery("div[data-page='" + this.currentPage + "']").removeClass('hidden');
    
                if (this.currentPage == 3) {
                    jQuery('#sliding-content-container').removeClass('hidden');
                    jQuery(window).trigger('resize');
                } else {
                    jQuery('#sliding-content-container').addClass('hidden');
                }
            }
        },
        onPrev: function() {
            jQuery('#sliding-content-container').addClass('hidden');

            jQuery("div[data-page='" + this.currentPage + "']").addClass('hidden');
            
            this.currentPage = Math.max(this.currentPage - 1, 1);
            jQuery("div[data-page='" + this.currentPage + "']").removeClass('hidden');
        },
        onSave: function(evt) {
            var $current = jQuery("div[data-page='" + this.currentPage + "']"); 
            if (!this.validate(this.currentPage)) {
                $current.addClass('has-error');
            } else {
                tinyMCE.activeEditor.save();
                var frm = jQuery(evt.currentTarget).parents('form')[0];

                var data = jQuery(frm).serializeArray();

                jQuery.ajax({
                    type: 'POST',
                    url: frm.action,
                    dataType: 'json',
                    data: data,
                    success: function (json) {
                        window.location = json.project.url;
                    },
                    error: function() {
                        // do something useful here
                    }
                });

            }
        },
        onFormKeyPress: function(evt) {
            if (evt.keyCode == 13) {
                evt.preventDefault();
            }
        },
        onGalleryItemMouseOver: function(evt) {
            this.hoverItem = evt.currentTarget;
            var $elt = jQuery(evt.currentTarget);
            var $overlay = jQuery('.gallery-item-overlay');
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
            var pk = jQuery(this.hoverItem).attr('data-id');
            jQuery("input[name='item']").val(pk);

            var clone = jQuery.clone(this.hoverItem);
            jQuery(clone).attr('style', 'float: none');
            jQuery('.selected-item div').replaceWith(clone);
            
            delete this.hoverItem;
        }
    });
}(jQuery));