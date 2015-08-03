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
            'click .gallery-item-overlay': 'onGalleryItemSelect'
        },
        initialize: function(options) {
            _.bindAll(this, 'onNext', 'onPrev', 'onSave',
                    'onGalleryItemMouseOver', 'onGalleryMouseOut',
                    'onGalleryItemSelect');
            var self = this;
            this.currentPage = 1;
            this.totalPages = 3;
            this.hoverItem = null;
            this.selectedItem = jQuery('.selected-item .gallery-item')[0];
            
            // hook up behaviors
            jQuery(window).on('tinymce_init_instance',
                function (event, instance, param2) {
                    if (instance) {
                        var width = jQuery(self.el).find('textarea').width();
                        instance.theme.resizeTo(width, 400);
                    }
                }
            );
        },
        validate: function(pageNo) {
            if (pageNo === 1) {
                return jQuery(this.el).find("input[name='title']").val().length > 0;
            } else if (pageNo === 2) {
                return tinyMCE.activeEditor.getContent().length > 0;
            } else if (pageNo === 3) {
                return this.selectedItem !== undefined;
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
                var form = jQuery(evt.currentTarget).parents('form').first();

                // set the item id
                var pk = jQuery(this.selectedItem).attr('data-id');
                jQuery("input[name='item']").val(pk);
                
                form.submit();
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
            this.hoverItem = null;
            var $overlay = jQuery('.gallery-item-overlay');
            $overlay.addClass('hidden');
        },
        onGalleryItemSelect: function(evt) {
            this.selectedItem = this.hoverItem;
            var clone = jQuery.clone(this.selectedItem);
            jQuery(clone).attr('style', 'float: none');
            jQuery('.selected-item div').replaceWith(clone);
        }
    });
}(jQuery));